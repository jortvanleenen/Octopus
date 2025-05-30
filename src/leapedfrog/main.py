"""
This module contains the main entry point of the program.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import argparse
import json
import logging
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import Any, Callable, Generator

from pysmt.logics import get_logic_by_name
from pysmt.shortcuts import Portfolio, get_env

from automata.dfa import DFA
from bisimulation.bisimulation import naive_bisimulation, symbolic_bisimulation
from leapedfrog import constants
from leapedfrog.__about__ import __version__
from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    :return: an argparse namespace containing the parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="LeapedFrog is an equivalence checker for P4 packet parsers.",
        epilog="Developed by Jort van Leenen.",
    )
    parser.add_argument(
        "--version", action="version", version=f"LeapedFrog v{__version__}"
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
        "-n",
        "--naive",
        action="store_true",
        help="use naive bisimulation instead of symbolic bisimulation",
    )
    parser.add_argument(
        "--disable_leaps",
        action="store_true",
        help="disable leaps in symbolic bisimulation (ignored if --naive is set)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="write the bisimulation certificate or counterexample to this file",
    )
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="exit with code 1 if the parsers are not equivalent",
    )
    parser.add_argument(
        "-t",
        "--time",
        action="store_true",
        help="measure and print bisimulation execution time",
    )
    parser.add_argument(
        "-s",
        "--solvers",
        type=str,
        nargs="+",
        default=["z3", "cvc5"],
        help="list of solvers (supported by PySMT) to use for symbolic bisimulation",
    )
    return parser.parse_args()


def setup_logging(verbosity: int) -> None:
    """
    Set up the logging configuration based on the verbosity level.

    :param verbosity: the verbosity level
    """
    if verbosity >= 3:
        level = logging.DEBUG
    elif verbosity == 2:
        level = logging.INFO
    elif verbosity == 1:
        level = logging.WARNING
    else:
        level = logging.ERROR

    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(
            format="[%(levelname)s - %(filename)s, line %(lineno)d]: %(message)s",
            level=level,
        )
    else:
        root_logger.setLevel(level)


def create_portfolio(solvers: list[str], **options: Any) -> Portfolio:
    """
    Given a list of wanted solvers, return a portfolio of available solvers.

    :param solvers: a list of solver names to check for availability
    :return: a Portfolio object containing the available solvers
    """
    available_solvers: list[str] = list(
        get_env().factory.all_solvers(logic=get_logic_by_name(constants.logic_name)).keys()
    )
    logger.info(f"Available solvers: {available_solvers}")

    selected_solvers = [s for s in solvers if s in available_solvers]
    if not selected_solvers:
        raise ValueError(
            "None of the specified solvers are available. "
            "Available solvers: " + ", ".join(available_solvers)
        )
    logger.info(f"Selected solvers: {selected_solvers}")

    portfolio = Portfolio(selected_solvers, get_logic_by_name(constants.logic_name), **options)

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
            "Please ensure it is installed and available in your system PATH."
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
                    f"- stdout: {e.stdout}\n"
                    f"- stderr: {e.stderr}"
                )
                raise RuntimeError(
                    f"p4c-graphs failed with exit code {e.returncode}"
                ) from e
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON output from p4c-graphs at line {e.lineno}, column {e.colno}: {e.msg}"
                ) from e

    return jsons


def select_bisimulation_method(
    args: argparse.Namespace,
) -> tuple[
    Callable[
        [ParserProgram, ParserProgram],
        tuple[bool, set[tuple[DFA.Configuration, DFA.Configuration]]],
    ],
    str,
]:
    """
    Select the bisimulation method based on the command-line arguments.

    :param args: the parsed command-line arguments
    :return: a tuple containing the selected bisimulation method and its name
    """
    if args.naive:
        logger.info("Using naive bisimulation")
        return naive_bisimulation, "Naive"
    else:
        logger.info("Using symbolic bisimulation")
        portfolio = create_portfolio(args.solvers)
        return partial(
            symbolic_bisimulation,
            enable_leaps=not args.disable_leaps,
            solver_portfolio=portfolio,
        ), "Symbolic"


@contextmanager
def timed_block(label: str) -> Generator[None, Any, None]:
    """
    Context manager to measure the execution time of a code block.

    :param label: a label for the block of code being timed

    """
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    yield
    end_wall = time.perf_counter()
    end_cpu = time.process_time()
    duration_msg = (
        f"{label} completed. Timing results:\n"
        f"  Wall time: {end_wall - start_wall:.4f} s\n"
        f"  CPU time:  {end_cpu - start_cpu:.4f} s"
    )
    logger.info(duration_msg)
    print(duration_msg)


def main() -> None:
    """Entry point of the program."""
    args = parse_arguments()
    setup_logging(args.verbosity)

    logger.info("Starting...")
    logger.debug(f"Parsed CLI argument values: {args}")

    logger.info("Reading P4 files...")
    ir_jsons = read_p4_files([args.file1, args.file2], args.json)

    logger.info("Converted both P4 files to IR JSON format")
    logger.debug(f"IR JSON of file 1: '{ir_jsons[0]}'")
    logger.debug(f"IR JSON of file 2: '{ir_jsons[1]}'")

    logger.info("Creating Parser objects...")
    parsers = [ParserProgram(j) for j in ir_jsons]
    logger.info("Created Parser objects")
    logger.debug(f"Parser object 1 (repr): '{parsers[0]!r}'")
    logger.debug(f"Parser object 1 (str):\n {parsers[0]}")
    logger.debug(f"Parser object 2 (repr): '{parsers[1]!r}'")
    logger.debug(f"Parser object 2 (str)\n {parsers[1]}")

    method, method_name = select_bisimulation_method(args)
    if args.time:
        with timed_block(f"{method_name} bisimulation"):
            are_equal, certificate = method(parsers[0], parsers[1])
    else:
        are_equal, certificate = method(parsers[0], parsers[1])

    if are_equal:
        message = "The two parsers are equivalent."
        header = "--- Bisimulation Certificate ---"
    else:
        message = "The two parsers are NOT equivalent."
        header = "--- Counterexample ---"

    logger.info(f"{message}\n{header}\n{certificate}")
    print(message + "\n" + header + "\n" + str(certificate))

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(f"{message}\n{header}\n{certificate}\n")
        except OSError as e:
            logger.error(
                f"Could not write to output file '{args.output}': {e.strerror}"
            )
            sys.exit(1)

    if args.fail_on_mismatch and not are_equal:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("An unexpected error occurred.")
        sys.exit(1)
