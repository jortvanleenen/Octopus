"""
This module defines ParserProgram, a class that represents the parser block of
a P4 program and types used in the parser.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from typing import Dict

from src.program.parser_state import ParserState

logger = logging.getLogger(__name__)


class ParserProgram:
    """A class representing a P4 parser program with its input and output types."""

    def __init__(self, json: Dict | None = None) -> None:
        """
        Initialise a ParserProgram object.

        :param json: the IR JSON data to parse
        """
        self.types: Dict[str, dict | int] = {}

        self.input_name: str | None = None
        self.output_name: str | None = None
        self.output_type: str | None = None

        self.states: Dict[str, ParserState] = {}

        if json is not None:
            self.parse(json)

    def parse(self, data: Dict) -> None:
        """
        Parse IR JSON data into a ParserProgram object.

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
                            "Multiple parser blocks found, only the first one is used."
                        )
                        continue
                    logger.info("Parsing parser block...")
                    logger.debug(f"For: '{obj}'")
                    self._parse_parser_block(obj)
                case _:
                    logger.debug(
                        f"Ignoring type '{obj['Node_Type']}' of object '{obj}'"
                    )

    def _parse_data_type(self, obj: Dict) -> None:
        """
        Parse a data type object of a P4 program.

        At the moment, only the Type_Header and Type_Struct types are supported.
        Additionally, fields must be either:
          - Type_Bits (fixed-width, unsigned integers only)
          - Type_Name (to a supported container type, i.e. header or struct)

        :param obj: the data type object to parse
        """
        type_name = obj["name"]
        fields = {}
        for field in obj["fields"]["vec"]:
            name = field["name"]
            match field["type"]["Node_Type"]:
                case "Type_Bits":
                    fields[name] = field["type"]["size"]
                case "Type_Name":
                    fields[name] = field["type"]["path"]["name"]
                case _:
                    logger.warning(
                        f"Unknown node type '{field['type']['Node_Type']}' for '{name}'"
                    )

        logger.info(f"Parsed type '{type_name}' with fields: {fields}")
        self.types[type_name] = fields

    def _parse_parser_block(self, obj: Dict) -> None:
        """
        Parse a parser block object of a P4 program.

        At the moment, a parser is expected to have exactly two parameters:
          - a packet_in parameter (the 'input to parse')
          - a parameter with as direction 'out' (the parsed packet/'store')

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

        if self.input_name is None or self.output_name is None:
            raise ValueError("Could not determine both input and output parameters")
        logger.info(
            f"Parsed parameters. Input '{self.input_name}', output '{self.output_name}'"
        )

        states = obj["states"]["vec"]
        for state in states:
            name = state["name"]
            logger.info(f"Parsing state '{name}'...")
            if name in ["reject", "accept"]:
                continue
            self.states[name] = ParserState(
                self, state["components"], state["selectExpression"]
            )

        logger.info(f"Parsed states (excluding terminals): {list(self.states.keys())}")

    def get_header_fields(self, reference: str) -> dict:
        """
        Get the names and sizes (in bits) of the fields in a header type.

        For example, get_header_fields(hdr.mpls) = {label: 32}.

        As a P4 program is statically typed and compiled, the type of a field
        must be known at compile time and valid. This eliminates the need
        for type checking at runtime.

        :param reference: a reference to the header
        :return: a dictionary with the names and sizes of its fields
        """
        type_content = self.types.get(self.output_type)
        if type_content is None:
            raise KeyError(f"Output type '{self.output_type}' not found in types")

        if reference.startswith(self.output_name + "."):
            reference_parts = reference.removeprefix(self.output_name + ".").split(".")
        else:
            reference_parts = reference.split(".")
        for part in reference_parts:
            if part not in type_content:
                raise KeyError(f"Reference part '{part}' not found in type content")
            type_content = self.types.get(type_content[part])
            if type_content is None:
                raise KeyError(f"Type '{part}' not found in types")

        logger.info(f"Obtained header fields for '{reference}': {type_content}")
        return type_content

    def __repr__(self) -> str:
        return (
            f"Parser(input={self.input_name!r}, "
            f"output=({self.output_type!r} {self.output_name!r}), "
            f"types={list(self.types.keys())!r}, "
            f"states={list(self.states.keys())!r})"
        )

    def __str__(self) -> str:
        n_spaces = 2
        output = [
            "Parser",
            n_spaces * " " + f"Input name: {self.input_name}",
            n_spaces * " " + f"Output: {self.output_name} ({self.output_type})",
            n_spaces * " " + "Types:",
        ]
        for name, fields in self.types.items():
            output.append(2 * n_spaces * " " + f"{name}: {fields}")

        output.append(n_spaces * " " + "States:")
        for name, content in self.states.items():
            output.append(2 * n_spaces * " " + f"{name}:")
            output.append("\n".join(3 * n_spaces * " " + line for line in str(content).splitlines()))

        return "\n".join(output)
