"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from bisimulation.symbolic.formula import PureFormula
from program.expression import (
    Concatenate,
    Expression,
    Reference,
    Slice,
    parse_expression,
)

if TYPE_CHECKING:
    from program.operation_block import OperationBlock
    from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class Component(ABC):
    """A class representing an executable component of a P4 parser state's operation block."""

    @abstractmethod
    def parse(self, component: dict) -> None:
        pass

    @abstractmethod
    def eval(self, store: dict[str, str], buffer: str) -> tuple[dict[str, str], str]:
        pass

    @abstractmethod
    def strongest_postcondition(self, pf: PureFormula, left: bool):
        pass


class Assignment(Component):
    def __init__(self, program: "ParserProgram", component: dict = None) -> None:
        self._program: ParserProgram = program
        self.left: Slice | Reference | None = None
        self.right: Expression | None = None
        if component is not None:
            self.parse(component)

    def parse(self, component: dict) -> None:
        self.left = parse_expression(self._program, component["left"])
        self.right = parse_expression(self._program, component["right"])

    def eval(self, store: dict[str, str], buffer: str) -> tuple[dict[str, str], str]:
        right_value = self.right.eval(store)
        if isinstance(self.left, Slice):
            store[self.left.reference][self.left.lsb : self.left.msb] = right_value
        else:
            store[self.left.reference] = right_value

        return store, buffer

    def strongest_postcondition(self, pf: PureFormula, left: bool):
        reference_var = pf.get_header_field_var(self.left.reference, left)
        new_var = pf.fresh_variable(len(reference_var))
        substitution = {reference_var: new_var}
        pf.substitute(substitution)
        return PureFormula.And(
            reference_var, PureFormula.Equals(reference_var, self.right)
        )

    def __repr__(self) -> str:
        return f"Component(left={self.left!r}, right={self.right!r})"

    def __str__(self) -> str:
        return f"{self.left} = {self.right}"


class MethodCall(Component):
    """A class representing a method call in a P4 parser state."""

    def __init__(self, program: "ParserProgram", component: dict = None) -> None:
        self.program: ParserProgram = program
        self.instance: Extract | None = None
        self.function_name: str | None = None
        if component is not None:
            self.parse(component)

    def parse(self, component: dict) -> None:
        """Parse a component JSON into a MethodCall object."""
        operation_type = component["Node_Type"]
        match operation_type:
            case "MethodCallStatement":
                call = component["methodCall"]
                self.function_name = call["method"]["member"]
                match self.function_name:
                    case "extract":
                        self.instance = Extract(self.program, call)
                    case _:
                        logger.warning(f"Ignoring method call '{self.function_name}()'")
            case _:
                logger.warning(f"Ignoring component of type '{operation_type}'")

    def eval(self, store: dict[str, str], buffer: str):
        """Evaluate the method call."""
        if self.instance is None or self.function_name is None:
            logger.warning("Method call has not yet been parsed")
            return store, buffer

        return self.instance.eval(store, buffer)

    def __repr__(self) -> str:
        return f"MethodCall(function_name={self.function_name!r}, instance={self.instance!r})"

    def __str__(self) -> str:
        return f"{self.function_name}({self.instance})"


class Extract(Component):
    """A class representing an extract method call in a P4 parser state."""

    def __init__(self, program: "ParserProgram", call: dict = None) -> None:
        self.program: ParserProgram = program
        self.header_reference: str | None = None
        self.header_content: dict[str, int] | None = None
        self.size: int | None = None
        if call is not None:
            self.parse(call)

    def parse(self, call: dict) -> None:
        header_name = call["arguments"]["vec"][0]["expression"]["member"]
        self.header_reference = self.program.output_name + "." + header_name
        self.header_content: dict = self.program.get_header_fields(
            self.header_reference
        )
        self.size = sum(self.header_content.values())

    def eval(self, store: dict[str, str], buffer: str):
        """Evaluate the extract method call."""
        if self.header_content is None or self.size is None:
            logger.warning("Extract method call has not yet been parsed")
            return store, buffer

        for field in self.header_content:
            field_size = self.header_content[field]
            store[self.header_reference + "." + field] = buffer[:field_size]
            buffer = buffer[field_size:]

        return store, buffer

    def strongest_postcondition(self, pf: PureFormula, left: bool):
        substitution = {}
        buffer_var = pf.get_buffer_var()
        new_buffer = pf.fresh_variable(len(buffer_var) - self.size)

        for field, field_size in self.header_content.items():
            variable = pf.fresh_variable(field_size)

            store_name = self.header_reference + "." + field
            old_variable = pf.get_header_field_var(store_name)
            if old_variable is not None:
                substitution[old_variable] = variable
            pf.set_header_field_var(store_name, variable)

            new_buffer = Concatenate(variable, new_buffer)

        substitution[buffer_var] = new_buffer
        pf.substitute(substitution)

    def __repr__(self) -> str:
        return f"Extract(header_reference={self.header_reference!r}, header_content={self.header_content!r}, size={self.size!r})"

    def __str__(self) -> str:
        return self.header_reference
