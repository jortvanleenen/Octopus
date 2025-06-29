"""
This module defines ParserProgram, a class that represents the parser block in
a P4 program, including the types and parameters that it uses.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging

from octopus.utils import ReprMixin
from program.parser_state import ParserState

logger = logging.getLogger(__name__)


class ParserProgram(ReprMixin):
    """A class representing a P4 parser program with its input and output types."""

    def __init__(self, json: dict | None = None, is_left: bool = False):
        """
        Initialise a ParserProgram object.

        :param json: the IR JSON data to parse
        :param is_left: whether this is the left parser program (True) or the right one (False)
        """
        self._types: dict[str, dict | int] = {}

        self._input_name: str | None = None
        self._output_name: str | None = None
        self._output_type: str | None = None

        self._states: dict[str, ParserState] = {}

        self._is_left = is_left

        if json is not None:
            self.parse(json)

    @property
    def types(self) -> dict[str, dict | int] | None:
        """
        Get the types of the parser program.

        :return: a dictionary of type names to their fields or sizes, or None if no types are defined
        """
        return self._types

    @property
    def input_name(self) -> str | None:
        """
        Get the name of the input parameter.

        :return: the name of the input parameter, or None if not set
        """
        return self._input_name

    @property
    def output_name(self) -> str | None:
        """
        Get the name of the output parameter.

        :return: the name of the output parameter, or None if not set
        """
        return self._output_name

    @property
    def output_type(self) -> str | None:
        """
        Get the type of the output parameter.

        :return: the type of the output parameter, or None if not set
        """
        return self._output_type

    @property
    def states(self) -> dict[str, ParserState]:
        """
        Get the states of the parser program.

        :return: a dictionary of state names to ParserState objects
        """
        return self._states

    @property
    def is_left(self) -> bool:
        """
        Get whether the parser program is the left one or not.

        :return: True if this is the left parser program, False otherwise
        """
        return self._is_left

    def parse(self, data: dict) -> None:
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
                    if len(self._states) > 0:
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

    def _parse_data_type(self, obj: dict) -> None:
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
        self._types[type_name] = fields

    def _parse_parser_block(self, obj: dict) -> None:
        """
        Parse a parser block object of a P4 program.

        At the moment, a parser is expected to have exactly two parameters:
          - a packet_in parameter (the packet stream to parse)
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
                self._output_name = name
                self._output_type = parameter["type"]["path"]["name"]
            else:
                self._input_name = name

        if self._input_name is None or self._output_name is None:
            raise ValueError("Could not determine both input and output parameters")
        logger.info(
            f"Parsed parameters. Input '{self._input_name}', output '{self._output_name}'"
        )

        states = obj["states"]["vec"]
        for state in states:
            name = state["name"]
            logger.info(f"Parsing state '{name}'...")
            if name in ["reject", "accept"]:
                continue
            self._states[name] = ParserState(
                self, state["components"], state["selectExpression"]
            )

        logger.info(f"Parsed states (excluding terminals): {list(self._states.keys())}")

    def get_header(self, reference: str) -> dict[str, int] | int:
        """
        Given a reference, get either the size of the field, or the fields
        contained in the header.

        For example:
        - get_header(hdr.mpls) = {label: 32}
        - get_header(hdr.mpls.label) = 32

        As a P4 program is statically typed and compiled, the type of a field
        must be known at compile time and valid. This eliminates the need
        for strict type checking here.

        :param reference: a reference to a header or a field in a header
        :return: a dictionary of fields and their sizes, or a size
        """
        type_content = self._types.get(self._output_type)
        if type_content is None:
            raise KeyError(f"Output type '{self._output_type}' not found in types")

        if reference.startswith(self._output_name + "."):
            reference_parts = reference.removeprefix(self._output_name + ".").split(".")
        else:
            reference_parts = reference.split(".")
        for part in reference_parts:
            if part not in type_content:
                raise KeyError(f"Reference part '{part}' not found in type content")
            type_content = type_content[part]
            if type_content in self._types:
                # If found, then it is a reference to a type and not a field
                type_content = self._types[type_content]

        logger.info(f"Obtained header fields for '{reference}': {type_content}")
        return type_content

    def __str__(self):
        n_spaces = 2
        output = [
            "Parser",
            n_spaces * " " + f"Input name: {self._input_name}",
            n_spaces * " " + f"Output: {self._output_name} ({self._output_type})",
            n_spaces * " " + "Types:",
        ]
        for name, fields in self._types.items():
            output.append(2 * n_spaces * " " + f"{name}: {fields}")

        output.append(n_spaces * " " + "States:")
        for name, content in self._states.items():
            output.append(2 * n_spaces * " " + f"{name}:")
            output.append(
                "\n".join(
                    3 * n_spaces * " " + line for line in str(content).splitlines()
                )
            )

        return "\n".join(output)
