"""
This module contains the main entry point of the program.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import argparse
import ast
import json
import logging
import shutil
import subprocess
import sys
import tempfile
from contextlib import nullcontext
from pathlib import Path
from typing import Any

from pysmt.logics import get_logic_by_name
from pysmt.shortcuts import Portfolio, get_env

from bisimulation.bisimulation import symbolic_bisimulation
from octopus import constants
from octopus.__about__ import __version__
from octopus.utils import setup_logging, stat_block
from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    :return: an argparse namespace containing the parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Octopus is an equivalence checker for P4 packet parsers.",
        epilog="Developed by Jort van Leenen.",
    )
    parser.add_argument(
        "--version", action="version", version=f"Octopus v{__version__}"
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="specify that both inputs are in IR (p4c) JSON format",
    )
    parser.add_argument("file1", metavar="file 1", help="path to the first P4 program")
    parser.add_argument("file2", metavar="file 2", help="path to the second P4 program")
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity (-v, -vv, -vvv)",
    )
    parser.add_argument(
        "-L",
        "--disable-leaps",
        action="store_true",
        help="disable leaps; only use single-step bisimulation",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="write the bisimulation certificate or counterexample to this file",
    )
    parser.add_argument(
        "-f",
        "--fail-on-mismatch",
        action="store_true",
        help="exit with code 1 if the parsers are not equivalent",
    )
    parser.add_argument(
        "-S",
        "--stat",
        action="store_true",
        help="measure and print bisimulation execution time and memory usage",
    )
    parser.add_argument(
        "-s",
        "--solvers",
        type=str,
        default="['cvc5']",
        help="list of solvers, possibly with options, to use for bisimulation",
    )
    parser.add_argument(
        "--solvers-global-options",
        type=str,
        metavar="GLOBAL_OPTIONS",
        help="global options for the provided solvers",
    )
    parser.add_argument(
        "--filter-accepting-string",
        type=str,
        help="define a filter for accepting pairs via a string",
    )
    parser.add_argument(
        "--filter-accepting-file",
        type=str,
        help="define a filter for accepting pairs via a file",
    )
    parser.add_argument(
        "--filter-disagreeing-string",
        type=str,
        help="define a filter for disagreeing pairs via a string",
    )
    parser.add_argument(
        "--filter-disagreeing-file",
        type=str,
        help="define a filter for disagreeing pairs via a file",
    )
    return parser.parse_args()


def parse_filters(args: argparse.Namespace) -> tuple[str | None, str | None]:
    """
    Parse accepting and disagreeing filters from command-line arguments.

    :param args: parsed command-line arguments
    :return: (filter_accepting, filter_disagreeing)
    """

    def _load_filter(filter_string: str | None, filter_file: str | None, kind: str) -> str | None:
        if filter_string is not None and filter_file is not None:
            raise ValueError(
                f"Specify either --{kind}-string or --{kind}-file, not both."
            )

        if filter_string is not None:
            logger.info(f"Using {kind} filter from string: {filter_string}")
            return filter_string

        if filter_file is not None:
            try:
                with open(filter_file, "r", encoding="utf-8") as f:
                    filter_str = f.read()
                logger.info(f"Using {kind} filter from file '{filter_file}': {filter_str}")
                return filter_str
            except OSError as e:
                raise OSError(
                    f"Error opening {kind} filter file '{filter_file}': {e.strerror}"
                ) from e

        logger.info(f"No {kind} filter provided.")
        return None

    filter_accepting = _load_filter(
        args.filter_accepting_string,
        args.filter_accepting_file,
        "filter-accepting",
    )

    filter_disagreeing = _load_filter(
        args.filter_disagreeing_string,
        args.filter_disagreeing_file,
        "filter-disagreeing",
    )

    return filter_accepting, filter_disagreeing


def create_portfolio(args: argparse.Namespace):
    """
    Given a list of wanted solvers, return a portfolio of available solvers.

    :param args: the parsed command-line arguments
    :return: a Portfolio object containing the available solvers
    """
    try:
        solvers = ast.literal_eval(args.solvers)
    except (SyntaxError, ValueError) as e:
        raise ValueError(
            f"Invalid solvers format: {args.solvers}. "
            "Expected a list of solvers, e.g., ['z3', ('cvc5', {'option': 'value'})]."
        ) from e

    options = {}
    if args.solvers_global_options:
        try:
            options = ast.literal_eval(args.solvers_global_options)
        except (SyntaxError, ValueError) as e:
            raise ValueError(
                f"Invalid solvers global options format: {args.solvers_global_options}. "
                "Expected a dictionary, e.g., {'option': 'value'}"
            ) from e

    available_solvers: list[str] = list(
        get_env()
        .factory.all_solvers(logic=get_logic_by_name(constants.logic_name))
        .keys()
    )
    logger.info(f"Available solvers: {available_solvers}")

    selected_solvers = []
    for solver in solvers:
        if isinstance(solver, str):
            if solver in available_solvers:
                selected_solvers.append(solver)
            else:
                logger.warning(f"Solver '{solver}' is not available.")
        elif isinstance(solver, tuple) and len(solver) == 2:
            name, opts = solver
            if name in available_solvers:
                selected_solvers.append((name, opts))
            else:
                logger.warning(f"Solver '{name}' is not available.")
        else:
            logger.error(
                f"Invalid solver format: {solver}. "
                "Expected a string or a tuple (name, options)."
            )
    if not selected_solvers:
        raise ValueError(
            "None of the specified solvers are available. "
            "Available solvers: " + ", ".join(available_solvers)
        )
    logger.info(f"Selected solvers: {selected_solvers}")

    portfolio = Portfolio(
        selected_solvers, get_logic_by_name(constants.logic_name), **options
    )

    return portfolio


def read_p4_files(files: list[str], in_json: bool) -> list[dict]:
    """
    Read the provided (IR) P4 files and return their parsed JSON representations.

    :param files: a list of file paths to the P4 files to read
    :param in_json: whether the files are already in IR JSON format
    :return: a list containing the parsed JSON representations of the files
    """
    if shutil.which("p4c-graphs") is None:
        raise FileNotFoundError(
            "Required tool 'p4c-graphs' not found in PATH. "
            "Please ensure it is installed and available in your system PATH"
        )

    jsons = []
    for file in files:
        if in_json:
            try:
                with open(file, encoding="utf-8") as f:
                    jsons.append(json.load(f))
            except OSError as e:
                raise OSError(f"Error opening file '{file}': {e.strerror}") from e
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON in '{file}' at line {e.lineno} column {e.colno}: {e.msg}"
                ) from e
        else:
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_json_file = Path(temp_dir) / "IR.json"

                    subprocess.run(
                        [
                            "p4c-graphs",
                            "--toJSON",
                            temp_json_file,
                            "--graphs-dir",
                            temp_dir,
                            file,
                        ],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    logger.info(f"Converted '{file}' to IR JSON format")

                    with open(temp_json_file, "r", encoding="utf-8") as f:
                        jsons.append(json.load(f))

            except subprocess.CalledProcessError as e:
                logger.error(
                    f"p4c-graphs failed, it reported:\n"
                    f"  stdout: {e.stdout}\n"
                    f"  stderr: {e.stderr}"
                )
                raise RuntimeError(
                    f"p4c-graphs failed with exit code {e.returncode}"
                ) from e
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON output from p4c-graphs at line {e.lineno}, column {e.colno}: {e.msg}"
                ) from e

    return jsons


def main(args: Any = None) -> None:
    """Entry point of the program."""
    logger.info("Starting...")

    if args is None:
        args = parse_arguments()
        setup_logging(args.verbosity)
        logger.debug(f"Parsed CLI argument values: {args}")
    else:
        logger.debug(f"Received the following arguments: {args}")

    sys.setrecursionlimit(10000)  # Required for larger parsers

    portfolio = create_portfolio(args)
    filter_accepting, filter_disagreeing = parse_filters(args)
    logger.info(f"Leaps are {'disabled' if args.disable_leaps else 'enabled'}")

    logger.info("Reading P4 files...")
    ir_jsons = read_p4_files([args.file1, args.file2], args.json)
    if not args.json:
        logger.info("Converted both P4 files to IR JSON format")
        logger.debug(f"IR JSON of file 1:\n{ir_jsons[0]}")
        logger.debug(f"IR JSON of file 2:\n{ir_jsons[1]}")

    logger.info("Creating Parser objects...")
    parsers = [ParserProgram(j, i == 0) for i, j in enumerate(ir_jsons)]
    logger.info("Created Parser objects")
    logger.debug(f"Parser object 1 (repr):\n{parsers[0]!r}")
    logger.debug(f"Parser object 1 (str):\n{parsers[0]}")
    logger.debug(f"Parser object 2 (repr):\n{parsers[1]!r}")
    logger.debug(f"Parser object 2 (str)\n{parsers[1]}")

    ctx = stat_block("Symbolic bisimulation") if args.stat else nullcontext()
    with ctx:
        are_equal, certificate = symbolic_bisimulation(
            parsers[0],
            parsers[1],
            filter_accepting=filter_accepting,
            filter_disagreeing=filter_disagreeing,
            enable_leaps=not args.disable_leaps,
            solver_portfolio=portfolio,
        )

    if are_equal:
        message = "The two parsers are equivalent."
        header = "--- Bisimulation Certificate ---"
    else:
        message = "The two parsers are NOT equivalent."
        header = "--- Counterexample ---"

    print(f"{message}")
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(f"{message}\n{header}\n{certificate}")
        except OSError as e:
            logger.error(
                f"Could not write to output file '{args.output}': {e.strerror}"
            )
            sys.exit(1)
    else:
        print(f"{header}\n{certificate}")

    if args.fail_on_mismatch and not are_equal:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"An unexpected error occurred:\n{e}")
        sys.exit(1)
