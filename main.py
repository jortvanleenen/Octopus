"""
This module contains the main entry point of the program.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import tempfile
from typing import Dict

from src.parser.Parser import Parser

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse the CLI arguments.

    :return: an argparse namespace containing the parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Kangaroo is an equivalence checker for P4 packet parsers.",
        epilog="Written by Jort van Leenen.",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="specify that both inputs are in IR (p4c) JSON format",
    )
    parser.add_argument(
        "file1", metavar="file 1", help="a path to the first P4 program"
    )
    parser.add_argument(
        "file2", metavar="file 2", help="a path to the second P4 program"
    )
    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="increase output verbosity (-v, -vv, -vvv)",
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

    logging.basicConfig(format="[%(levelname)s]: %(message)s", level=level)


def read_p4_files(files: list[str], in_json: bool) -> list[Dict]:
    """
    Read the provided (IR) P4 files and return their JSON representations.

    :param files: the files to read
    :param in_json: whether the files are already in IR JSON format
    :return: a list containing the JSON representations of the files
    """
    if shutil.which("p4c-graphs") is None:
        raise FileNotFoundError("P4c-graphs could not be found")

    jsons = []
    for file in files:
        if in_json:
            try:
                with open(file, encoding="utf-8") as f:
                    jsons.append(json.load(f))
            except OSError as e:
                raise FileNotFoundError(f"Could not open file '{file}'") from e
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON input from '{file}'") from e
        else:
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_json_file = os.path.join(temp_dir, "IR.json")

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
                raise RuntimeError("P4c-graphs Failed with a non-zero exit code") from e
            except json.JSONDecodeError as e:
                raise ValueError("Error decoding JSON output from p4c-graphs") from e

    return jsons


def main() -> None:
    """Entry point of the program."""
    args = parse_arguments()
    setup_logging(args.verbosity)

    logger.info("Starting Kangaroo...")
    logger.debug(f"Parsed CLI argument values: {args}")

    logger.info("Reading P4 files...")
    ir_jsons = read_p4_files([args.file1, args.file2], args.json)

    logger.info("Parsed all P4 files into IR JSON format")
    logger.debug(f"IR JSON of file 1: '{ir_jsons[0]}'")
    logger.debug(f"IR JSON of file 2: '{ir_jsons[1]}'")

    logger.info("Creating Parser objects...")
    parsers = [Parser(j) for j in ir_jsons]
    # TODO: continue on code here...
    print(parsers)
    print(str(parsers[0]))


if __name__ == "__main__":
    main()
