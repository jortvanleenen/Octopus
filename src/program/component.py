"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging

from typing import TYPE_CHECKING, Dict, Tuple

if TYPE_CHECKING:
    from src.program.parser_program import ParserProgram

logger = logging.getLogger(__name__)

class Component:
    def parse(self, component: dict) -> None:
        raise NotImplementedError()

    def eval(self, store: Dict[str, str], buffer: str) -> Tuple[Dict[str, str], str]:
        raise NotImplementedError()

class Assignment(Component):
    pass

class Extract(Component):
    """A class representing a state in a P4 parser."""

    def __init__(self, program: "ParserProgram", component: dict = None) -> None:
        self.program = program
        self.operation = None
        self.size = None
        if component is not None:
            self.parse(component)

    def parse(self, component: dict):
        """Parse a component JSON into a Component object."""
        operation_type = component["Node_Type"]
        match operation_type:
            case "MethodCallStatement":
                self.operation = self._parse_method_call(component)
                if self.operation[0] == "extract":
                    self.size = self.program.get_type_reference_size(
                        f"hdr.{self.operation[1]}"
                    )
            case _:
                logger.warning(f"Ignoring component of type '{operation_type}'")

    def _parse_method_call(self, component: dict):
        """Parse a method call JSON into a Component object."""
        call = component["methodCall"]
        function_name = call["method"]["member"]
        arguments = call["arguments"]["vec"]
        if len(arguments) != 1:
            logger.warning(f"Method call '{function_name}' has more than one argument")
        store = arguments[0]["expression"]["member"]
        return function_name, store

    def eval(self, store: Dict[str, str], buffer: str):
        store[self.operation[1]] = buffer[: self.size]
        buffer = buffer[self.size :]
        return store, buffer

    def __repr__(self) -> str:
        return f"Component(operation={self.operation!r})"

    def __str__(self) -> str:
        return f"Component: {self.operation}"