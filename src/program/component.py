"""
This module defines Component, a class structure representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

from bisimulation.formula import (
    And,
    Equals,
    FormulaManager,
    FormulaNode,
    PureFormula,
    Variable,
)
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
            self, manager: FormulaManager, pf: PureFormula, buf_size: int
    ) -> tuple[PureFormula, int]:
        """
        Generate the strongest postcondition for this component.

        :param manager: the FormulaManager to use for generating the postcondition
        :param pf: the PureFormula representing what we currently know
        :param buf_size: the size of the parser's buffer
        :return: a PureFormula representing the SP, and remaining buffer size
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
        left = parse_expression(self._program, component["left"])
        if not isinstance(left, (Slice, Reference)):
            raise ValueError(
                "Assignment left-hand side must be a Slice or Reference, "
                f"but got {type(left).__name__}"
            )
        self.left = left
        self.right = parse_expression(self._program, component["right"], len(left))

    def strongest_postcondition(
            self, manager: FormulaManager, pf: PureFormula, buf_size: int
    ) -> tuple[PureFormula, int]:
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

        fresh_var = manager.fresh_variable(len(reference))
        right_subst = self.right.substitute({reference.reference: fresh_var})

        return PureFormula(
            And(
                pf.root.substitute({reference.reference: fresh_var}),
                Equals(reference.reference, right_subst)
            ),
            pf.used_vars | right_subst.used_vars() | {fresh_var},
            pf.stream_var,
        ), buf_size

    def __repr__(self):
        return f"Assignment(left={self.left!r}, right={self.right!r})"

    def __str__(self):
        return f"{self.left} = {self.right}"


class Extract(Component):
    """A class representing an extract method call in a P4 parser state."""

    def __init__(self, program: ParserProgram, call: dict = None):
        self._program: ParserProgram = program
        self.header_reference: str | None = None
        self.header_content: dict[str, int] | None = None
        self.size: int | None = None
        if call is not None:
            self.parse(call)

    def parse(self, call: dict) -> None:
        header_name = call["arguments"]["vec"][0]["expression"]["member"]
        self.header_reference = self._program.output_name + "." + header_name
        self.header_content: dict = self._program.get_header(self.header_reference)

        sizes = []
        for val in self.header_content.values():
            if isinstance(val, int):
                sizes.append(val)
            else:
                try:
                    sizes.append(self._program.typedefs[val])
                except KeyError:
                    raise KeyError(f"Missing typedef: '{val}'") from None

        self.size = sum(sizes)

    def strongest_postcondition(
            self, manager: FormulaManager, pf: PureFormula, buf_size: int
    ) -> tuple[PureFormula, int]:
        buf_var = self._program.get_buffer_var(buf_size)

        len_after = len(buf_var) - self.size
        if len_after < 0:
            raise ValueError("Invalid buffer length")

        new_buf_expr = None
        substitution: dict[Variable, FormulaNode] = {}
        new_vars: set = set()
        for field, field_size in self.header_content.items():
            field_var = self._program.get_header_var(self.header_reference + '.' + field)
            if isinstance(field_size, str):
                field_size = self._program.typedefs[field_size]
            fresh_var = manager.fresh_variable(field_size)
            substitution[field_var] = fresh_var
            new_vars |= {fresh_var}
            if new_buf_expr is None:
                new_buf_expr = field_var
            else:
                new_buf_expr = Concatenate(left=field_var, right=new_buf_expr)

        if len_after > 0:
            new_buf_var = self._program.get_buffer_var(len_after)
            new_buf_expr = Concatenate(left=new_buf_expr, right=new_buf_var)
        substitution[buf_var] = new_buf_expr

        return PureFormula(
            pf.root.substitute(substitution),
            pf.used_vars | new_vars,
            pf.stream_var
        ), len_after

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
