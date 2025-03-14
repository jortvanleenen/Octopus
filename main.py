"""
This module contains the main entry point of the program.

Author: Jort van Leenen
License: MIT
"""

import argparse
import json
import os
import shutil
import subprocess
import tempfile

from src.parse import parse_json


def parse_arguments() -> argparse.Namespace:
    """
    Parse CLI arguments.

    :return: a namespace containing the parsed arguments
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
    parser.add_argument("file1", help="a path to the first P4 program")
    parser.add_argument("file2", help="a path to the second P4 program")

    return parser.parse_args()


def read_p4_files(args: argparse.Namespace) -> [dict]:
    """
    Read the provided P4 files and return their JSON representations.

    It expects an argparse.Name as defined by :func:`parse_arguments`.

    :param args: parsed arguments from :func:`parse_arguments`
    :return: a tuple containing the JSON representations of the two P4 files
    """
    if shutil.which("p4c-graphs") is None:
        raise FileNotFoundError("p4c-graphs could not be found on PATH")

    jsons = []
    for file in [args.file1, args.file2]:
        if args.json:
            try:
                with open(file, encoding="utf-8") as f:
                    jsons.append(json.load(f))
            except OSError:
                raise FileNotFoundError(f"Could not open file {file}")
            except json.JSONDecodeError:
                raise ValueError(f"Error decoding JSON input from {file}")

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

                    with open(temp_json_file, "r", encoding="utf-8") as f:
                        jsons.append(json.load(f))

            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"p4c-graphs failed with exit code {e.returncode}")
            except json.JSONDecodeError:
                raise ValueError("Error decoding JSON output from p4c-graphs")

            finally:
                if os.path.exists(temp_json_file):
                    try:
                        os.remove(temp_json_file)
                    except OSError:
                        print(f"Could not remove temporary file {temp_json_file}")

        return jsons


def main():
    """Entry point of the program."""
    args = parse_arguments()
    parsers = [parse_json(obj) for obj in read_p4_files(args)]
    print(parsers)


if __name__ == "__main__":
    main()
