"""
This module defines ParserProgram, a class that represents that parser block of
a P4 program. Additionally, it contains the types that are used in the block.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from typing import Dict

from src.parser_program.ParserState import ParserState

logger = logging.getLogger(__name__)


class ParserProgram:
    """A class representing a P4 parser program with its input and output types."""

    def __init__(self, json: Dict = None) -> None:
        """
        Initialise a Parser object.

        :param json: the IR JSON data to parse
        """
        self.types = {}

        self.input_name = None
        self.output_name = None
        self.output_type = None

        self.states = {}

        if json is not None:
            self.parse(json)

    def parse(self, data: Dict) -> None:
        """
        Parse IR JSON data into a Parser object.

        At the moment, only the first parser block that is found is parsed.

        :param data: the IR JSON data to parse
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
                    self._parse_parser_block(obj)
                case _:
                    logger.debug(f"Ignoring type '{obj['Node_Type']} of '{obj}'")

        self.get_type_reference_size("hdr.mpls")
        self.get_type_reference_size("hdr.mpls.label")

    def _parse_data_type(self, obj: Dict) -> None:
        """
        Parse a data type object of a P4 program.

        At the moment, only the Type_Header and Type_Struct types are supported.
        Additionally, fields must be either:
          - Type_Bits (fixed-width, unsigned integers only)
          - Type_Name (a supported container type, i.e. header or struct)

        :param obj: the data type object to parse
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

    def _parse_parser_block(self, obj: Dict) -> None:
        """
        Parse a Parser block object of a P4 program.

        At the moment, a parser is expected to have two parameters:
          - a packet_in parameter (the 'input to parse')
          - a parameter with direction 'out' (the parsed packet/store)

        :param obj: the parser object to parse
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

    def get_type_reference_size(self, reference: str) -> int:
        """
        Get the size of a referenced type in bits.

        For example, get_type_reference_size(hdr.mpls.label) = 32.

        As a P4 program is statically typed and compiled, the type of a field
        must be known at compile time and valid. This eliminates the need
        for type checking at runtime.

        :param reference: the reference to the type
        :return: the size of the type in bits
        """
        type_content = self.types[self.output_type]
        reference_components = reference.split(".")[1:]
        for component in reference_components:
            type_content = self.types[type_content[component]]
            if len(type_content) == 1:
                value = next(iter(type_content.values()))
                if isinstance(value, int):
                    logger.info(
                        f"Type reference '{reference}' is a fixed-width type of size {value} bits."
                    )
                    return value
        logger.error(f"Type reference '{reference}' not found.")
        return 0

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
        for name, content in self.states.items():
            lines.append(f"    {name}: {content}")

        return "\n".join(lines)
