"""
This module defines Parser, a class representing a P4 program's parser.

Author: Jort van Leenen
License: MIT
"""

import logging
from typing import Dict

from src.parser.ParserState import ParserState

logger = logging.getLogger(__name__)


class Parser:
    """A class representing a P4 parser with its input and output types."""

    def __init__(self, json: Dict = None):
        self.types = {}

        self.input_name = None
        self.output_name = None
        self.output_type = None

        self.states = {}

        if json is not None:
            self.parse(json)

    def parse(self, data: Dict) -> None:
        """Parse IR JSON data into a Parser object.

        At the moment, only the first parser that is found is parsed.
        """
        if "objects" not in data or "vec" not in data["objects"]:
            raise ValueError("Invalid JSON data")

        for obj in data["objects"]["vec"]:
            match obj["Node_Type"]:
                case "Type_Header" | "Type_Struct":
                    logger.info(f"Parsing type '{obj['Node_Type']}'...")
                    logger.debug(f"For: '{obj}'")
                    self._parse_data_type(obj)
                case "P4Parser":
                    if len(self.states) > 0:
                        logger.warning(
                            "Multiple parsers found, only the first one is parsed"
                        )
                        continue
                    logger.info("Parsing parser...")
                    logger.debug(f"For: '{obj}'")
                    self._parse_parser(obj)
                case _:
                    logger.debug(f"Ignoring type '{obj['Node_Type']} of '{obj}'")

    def _parse_parser(self, obj: Dict):
        """Parse a Parser object in a P4 program.

        At the moment, a parser is expected to have two parameters:
          - a packet_in parameter (the 'input to parse')
          - a parameter with direction 'out' (the parsed packet/store)
        """
        parameters = obj["type"]["applyParams"]["parameters"]["vec"]
        if len(parameters) != 2:
            logger.warning(
                f"Expected 2 parameters for the parser, found {len(parameters)}"
            )

        for parameter in parameters:
            name = parameter["name"]
            logger.info(f"Parsing parameter '{name}'...")
            if parameter["direction"] == "out":
                self.output_name = name
                self.output_type = parameter["type"]["path"]["name"]
            else:
                self.input_name = name

        states = obj["states"]["vec"]
        for state in states:
            name = state["name"]
            logger.info(f"Parsing state '{name}'...")
            if name in ["reject", "accept"]:
                continue
            self.states[name] = ParserState(
                state["components"], state["selectExpression"]
            )

    def _parse_data_type(self, obj: Dict) -> None:
        """Parse a data type in a P4 program.

        At the moment, only the Type_Header and Type_Struct types are supported.
        Additionally, fields must be either:
          - Type_Bits (unsigned integers only)
          - Type_Name (another, supported type, i.e. header or struct)
        """
        type_name = obj["name"]
        fields = {}
        for field in obj["fields"]["vec"]:
            name = field["name"]
            if field["type"]["Node_Type"] == "Type_Bits":
                fields[name] = field["type"]["size"]
            elif field["type"]["Node_Type"] == "Type_Name":
                fields[name] = field["type"]["path"]["name"]
            else:
                logger.warning(
                    f"Unknown node type '{field['type']['Node_Type']}' for '{name}'"
                )

        self.types[type_name] = fields

    def __repr__(self) -> str:
        return (
            f"Parser(input={self.input_name!r}, "
            f"output=({self.output_type} {self.output_name}), "
            f"types={list(self.types.keys())!r}, "
            f"states={list(self.states.keys())!r})"
        )

    def __str__(self) -> str:
        lines = [
            "Parser",
            f"  Input: {self.input_name}",
            f"  Output: {self.output_name} ({self.output_type})",
            "  Types:",
        ]
        for name, fields in self.types.items():
            lines.append(f"    {name}: {fields}")

        lines.append("  States:")
        for state_name in self.states:
            lines.append(f"    {state_name}")

        return "\n".join(lines)
