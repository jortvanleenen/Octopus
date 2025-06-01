"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from bisimulation import symbolic
from bisimulation.symbolic.formula import PureFormula, FormulaManager, And, Equals
from program.expression import (
    Expression,
    Reference,
    Slice,
    parse_expression,
)

if TYPE_CHECKING:
    from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class Component(ABC):
    """A class representing an executable component of a P4 parser state's operation block."""

    @abstractmethod
    def parse(self, component: dict) -> None:
        """
        Parse a component JSON into a Component object.

        :param component: the component JSON object
        """
        pass

    @abstractmethod
    def eval(self, store: dict[str, str], buffer: str) -> tuple[dict[str, str], str]:
        """
        Evaluate the component using the provided store and buffer.

        :param store: the current store
        :param buffer: the current buffer
        :return: a tuple containing the updated store and buffer
        """
        pass

    @abstractmethod
    def strongest_postcondition(
        self, manager: FormulaManager, pf: PureFormula, left: bool
    ) -> PureFormula:
        """
        Generate the strongest postcondition for this component.

        :param manager: the FormulaManager to use for generating the postcondition
        :param pf: the PureFormula representing what we currently know
        :param left: whether the postcondition is for the left parser
        """
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

    def strongest_postcondition(
        self, manager: FormulaManager, pf: PureFormula, left: bool
    ) -> PureFormula:
        reference_var = pf.get_header_field_var(self.left.reference, left)
        new_var = manager.fresh_variable(len(reference_var))

        substitution = {reference_var: new_var}
        pf.substitute(substitution)

        return PureFormula.clone_with_new_root(
            pf, And(pf.root, Equals(reference_var, self.right))
        )

    def __repr__(self) -> str:
        return f"Component(left={self.left!r}, right={self.right!r})"

    def __str__(self) -> str:
        return f"{self.left} = {self.right}"


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
        self.header_content: dict = self.program.get_header(self.header_reference)
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

    def strongest_postcondition(
        self, manager: FormulaManager, pf: PureFormula, left: bool
    ) -> PureFormula:
        substitution = {}
        buffer_var = pf.get_buffer_var(left)
        if buffer_var is None:
            logger.warning("No buffer variable found in the postcondition")
            raise ValueError("No buffer variable found in the postcondition")
        else:
            length = len(buffer_var) - self.size
            if length <= 0:
                pf.set_buffer_var(left, None)
                new_buffer = None
            else:
                new_buffer = manager.fresh_variable(len(buffer_var) - self.size)

        for field, field_size in self.header_content.items():
            variable = manager.fresh_variable(field_size)

            store_name = self.header_reference + "." + field
            old_variable = pf.get_header_field_var(store_name, left)
            if old_variable is not None:
                substitution[old_variable] = variable
            pf.set_header_field_var(store_name, left, variable)

            if new_buffer is None:
                new_buffer = variable
            else:
                new_buffer = symbolic.formula.Concatenate(variable, new_buffer)

        substitution[buffer_var] = new_buffer
        pf.substitute(substitution)

        return pf

    def __repr__(self) -> str:
        return f"Extract(header_reference={self.header_reference!r}, header_content={self.header_content!r}, size={self.size!r})"

    def __str__(self) -> str:
        return self.header_reference


_METHOD_DISPATCH: dict[str, Callable[["ParserProgram", dict], Component]] = {
    "extract": lambda program, call: Extract(program, call),
}


def parse_method_call(program: "ParserProgram", component: dict) -> Component | None:
    """
    Parse a method call component into a specific MethodCall subclass.

    :param program: the ParserProgram this component belongs to
    :param component: the full component JSON object
    :return: a Component instance representing the method call
    """
    if component.get("Node_Type") != "MethodCallStatement":
        logger.warning(
            f"Ignoring non-method-call node type '{component.get('Node_Type')}'"
        )
        return None

    call = component.get("methodCall")
    if call is None:
        logger.warning("Missing 'methodCall' field in MethodCallStatement")
        return None

    method_name = call.get("method", {}).get("member")
    factory = _METHOD_DISPATCH.get(method_name)

    if factory is None:
        logger.warning(f"Unsupported method call: '{method_name}()'")
        return None

    return factory(program, call)
