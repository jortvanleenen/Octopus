"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging

from typing import TYPE_CHECKING, Dict, Tuple

from src.program.expression import Expression, Slice

if TYPE_CHECKING:
    from src.program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class Component:
    """A class representing an executable component of a P4 parser state's operation block."""

    def parse(self, component: dict) -> None:
        raise NotImplementedError()

    def eval(self, store: Dict[str, str], buffer: str) -> Tuple[Dict[str, str], str]:
        raise NotImplementedError()


class Assignment(Component):
    def __init__(self, program: "ParserProgram", component: dict = None) -> None:
        self.program: ParserProgram = program
        self.left: Slice | str | None = None
        self.right: Expression | None = None
        if component is not None:
            self.parse(component)

    def parse(self, component: dict) -> None:
        # self.left = LValue(component["left"])
        self.left = Expression(component["left"])
        self.right = Expression(component["right"])

    def eval(self, store: Dict[str, str], buffer: str) -> Tuple[Dict[str, str], str]:
        right_value = self.right.eval(store)
        if isinstance(self.left, Slice):
            store[self.left.reference][self.left.lsb : self.left.msb] = right_value
        else:
            store[self.left] = right_value

        return store, buffer

    def __repr__(self) -> str:
        return f"Component(left={self.left!r}, right={self.right!r})"

    def __str__(self) -> str:
        return f"{self.left} = {self.right}"


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
        # if "fields" in arguments[0]["expression"]["type"]:
        #     store += "." + arguments[0]["expression"]["type"]["fields"]["vec"][0]["name"]
        return function_name, store

    def eval(self, store: Dict[str, str], buffer: str):
        store[self.operation[1]] = buffer[: self.size]
        buffer = buffer[self.size :]
        return store, buffer

    def __repr__(self) -> str:
        return f"Component(operation={self.operation!r}, size={self.size!r})"

    def __str__(self) -> str:
        args = ", ".join(str(arg) for arg in self.operation[1:])
        return f"{self.operation[0]}({args}, {self.size})"
