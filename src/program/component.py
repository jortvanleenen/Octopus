"""
This module defines Component, a class structure representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from __future__ import annotations

import copy
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from bisimulation.formula import And, Equals, FormulaManager, PureFormula
from program.expression import (
    Concatenate,
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
    def strongest_postcondition(
        self, manager: FormulaManager, pf: PureFormula
    ) -> PureFormula:
        """
        Generate the strongest postcondition for this component.

        :param manager: the FormulaManager to use for generating the postcondition
        :param pf: the PureFormula representing what we currently know
        :return: a PureFormula representing the strongest postcondition
        """
        pass


class Assignment(Component):
    def __init__(self, program: ParserProgram, component: dict = None):
        self._program: ParserProgram = program
        self.left: Slice | Reference | None = None
        self.right: Expression | None = None
        if component is not None:
            self.parse(component)

    def parse(self, component: dict) -> None:
        self.left = parse_expression(self._program, component["left"])
        self.right = parse_expression(self._program, component["right"], len(self.left))

    def strongest_postcondition(
        self, manager: FormulaManager, pf: PureFormula
    ) -> PureFormula:
        left = self._program.is_left
        logger.debug(
            f"Header variables at start of assignment SP (left: {left}): {pf.header_field_vars}"
        )

        if isinstance(self.left, Slice):
            raise NotImplementedError(
                "Assignment with left-hand slice is not yet supported"
            )
            # reference = self.left.reference.reference
        elif isinstance(self.left, Reference):
            reference = self.left
        else:
            raise ValueError(
                "Assignment left-hand side must be a Slice or Reference, "
                f"but got {type(self.left).__name__}"
            )

        new_var = manager.fresh_variable(len(reference))
        new_pf = pf.deepcopy()
        new_pf.set_header_field_var(reference.reference, self._program.is_left, new_var)

        right_copy = copy.deepcopy(self.right)
        right_copy.to_formula(pf)

        logger.debug(
            f"Header variables at end of assignment SP (left: {left}): {new_pf.header_field_vars}"
        )

        return PureFormula(
            And(new_pf.root, Equals(new_var, right_copy)),
            new_pf.header_field_vars,
            new_pf.buf_vars,
        )

    def __repr__(self):
        return f"Assignment(left={self.left!r}, right={self.right!r})"

    def __str__(self):
        return f"{self.left} = {self.right}"


class Extract(Component):
    """A class representing an extract method call in a P4 parser state."""

    def __init__(self, program: ParserProgram, call: dict = None):
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

    def strongest_postcondition(
        self, manager: FormulaManager, pf: PureFormula
    ) -> PureFormula:
        left = self.program.is_left
        buffer_var = pf.get_buffer_var(left)
        logger.debug(
            f"Buffer variables at start of extract SP (left: {left}): {pf.buf_vars}"
        )
        if buffer_var is None:
            raise ValueError("No buffer variable found for the pure formula")

        length = len(buffer_var) - self.size
        if length < 0:
            raise ValueError("Invalid buffer length")
        elif length == 0:
            pf.set_buffer_var(left, None)
            new_buffer = None
        else:
            new_buffer = manager.fresh_variable(len(buffer_var) - self.size)
            pf.set_buffer_var(left, new_buffer)

        for field, field_size in self.header_content.items():
            variable = manager.fresh_variable(field_size)

            store_name = self.header_reference + "." + field
            pf.set_header_field_var(store_name, left, variable)

            if new_buffer is None:
                new_buffer = variable
            else:
                new_buffer = Concatenate(self.program, left=variable, right=new_buffer)

        new_pf = PureFormula(
            And(pf.root, Equals(buffer_var, new_buffer)),
            pf.header_field_vars,
            pf.buf_vars,
        )

        logger.debug(
            f"Buffer variables at end of extract SP (left: {left}): {new_pf.buf_vars}"
        )

        return new_pf

    def __repr__(self):
        return f"Extract(header_reference={self.header_reference!r}, header_content={self.header_content!r}, size={self.size!r})"

    def __str__(self):
        return f"extract({self.header_reference})"


_METHOD_DISPATCH: dict[str, Callable[[ParserProgram, dict], Component]] = {
    "extract": lambda program, call: Extract(program, call),
}


def parse_method_call(program: ParserProgram, component: dict) -> Component | None:
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
