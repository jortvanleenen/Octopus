"""
This module defines Expression, a class hierarchy representing a subset of expressions in P4.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable

import pysmt.shortcuts as pysmt
from pysmt.shortcuts import BV, TRUE, BVConcat, BVExtract

from bisimulation.formula import (
    FormulaNode,
    PureFormula,
    Variable, FormulaManager,
)

if TYPE_CHECKING:
    from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class Expression(FormulaNode):
    """An abstract base class representing an expression in a P4 parser state."""

    def used_vars(self, pf: PureFormula) -> set[Variable]:
        return set()

    @abstractmethod
    def __len__(self) -> int:
        pass


class BinaryExpression(Expression, ABC):
    """A mixin for binary expressions that have a left and right operand."""

    left: Expression
    right: Expression

    def used_vars(self, pf: PureFormula) -> set[Variable]:
        return self.left.used_vars(pf) | self.right.used_vars(pf)


class Concatenate(BinaryExpression):
    def __init__(
            self,
            program: ParserProgram,
            obj: dict | None = None,
            *,
            left: Expression | FormulaNode | None = None,
            right: Expression | FormulaNode | None = None,
    ) -> None:
        self._program = program
        if obj is not None:
            self.parse(obj)
        else:
            if left is None:
                raise ValueError(f"Left operand is required.")
            if right is None:
                raise ValueError(f"Right operand is required.")
            self.left = left
            self.right = right

    def parse(self, obj: dict) -> None:
        """
        Parse a concatenation expression JSON into a Concatenate object.

        :param obj: the concatenation expression JSON object
        """
        self.left = parse_expression(self._program, obj["left"])
        self.right = parse_expression(self._program, obj["right"])

    def to_smt(self):
        return BVConcat(self.left.to_smt(), self.right.to_smt())

    def substitute(
            self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> Concatenate:
        self.left = self.left.substitute(pf, mapping)
        self.right = self.right.substitute(pf, mapping)
        return self

    def __len__(self) -> int:
        return len(self.left) + len(self.right)

    def __str__(self) -> str:
        return f"({self.left}) ++ ({self.right})"


class Slice(Expression):
    def __init__(self, program: ParserProgram, obj: dict = None) -> None:
        self._program = program
        self.reference = None
        self.msb = None
        self.lsb = None
        if obj is not None:
            self.parse(obj)

    def parse(self, obj: dict) -> None:
        """
        Parse a slice expression JSON into a Slice object.

        :param obj: the slice expression JSON object
        """
        self.reference = Reference(self._program, obj["e0"])
        self.msb = obj["e1"]["value"]
        self.lsb = obj["e2"]["value"]

    def to_smt(self) -> Any:
        return BVExtract(
            self.reference.to_smt(), self.lsb, self.msb
        )  # BVExtract has both ends inclusive; start=msb, end=lsb

    def used_vars(self, pf: PureFormula) -> set[Variable]:
        return self.reference.used_vars(pf)

    def substitute(
            self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        self.reference = self.reference.substitute(pf, mapping)
        return self

    def __len__(self) -> int:
        return self.msb - self.lsb + 1

    def __str__(self) -> str:
        return f"{self.reference}[{self.msb}:{self.lsb}]"


class Constant(Expression):
    def __init__(self, obj: dict, size_context: int) -> None:
        self.numeric_value: int | float | None = None
        self.value: str | None = None
        self._size: int | None = size_context
        if obj is not None:
            self.parse(obj)

    def parse(self, obj: dict) -> None:
        """
        Parse a constant expression JSON into a Constant object.

        :param obj: the constant expression JSON object
        """
        self.numeric_value: int = obj["value"]
        self.value = bin(self.numeric_value)[2:]  # Convert to binary string
        if self._size is not None:
            self.value = self.value.zfill(self._size)

    def to_smt(self) -> Any:
        if self._size is None:
            logger.warning("No size for constant of value %s", self.numeric_value)
        return BV(self.numeric_value, len(self))

    def substitute(
            self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return self

    def __len__(self) -> int:
        if self._size is None:
            logger.warning("No size for constant of value %s", self.numeric_value)
            return 0
        return self._size

    def __hash__(self) -> int:
        return hash(self.numeric_value)

    def __eq__(self, other) -> bool:
        if isinstance(other, Constant):
            return self.numeric_value == other.numeric_value
        elif isinstance(other, str):
            return self.numeric_value == int(other, 2)
        else:
            return NotImplemented

    def __str__(self) -> str:
        return str(self.value)


class DontCare(Expression):
    def __init__(self) -> None:
        pass

    def to_smt(self) -> Any:
        return TRUE()

    def substitute(
            self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return self

    def __len__(self) -> int:
        return 0

    def __hash__(self) -> int:
        return hash("DontCare")  # all DontCares are "equal" and hash identically

    def __eq__(self, other) -> bool:
        return True

    def __str__(self) -> str:
        return "*"


class Reference(Expression):
    def __init__(self, program: ParserProgram, obj: dict) -> None:
        self._program = program
        self._reference: str | None = None
        self._size: int = 0
        if obj is not None:
            self.parse(obj)

    @property
    def reference(self) -> str | None:
        """Get the reference of the expression."""
        return self._reference

    def parse(self, obj: dict) -> None:
        """
        Parse a reference expression JSON into a Reference object.

        :param obj: the reference expression JSON object
        """
        reference = ""
        while True:
            if "member" in obj:
                reference = obj["member"] + ("." if reference else "") + reference

            if "expr" in obj:
                obj = obj["expr"]
                continue

            if "path" in obj:
                reference = obj["path"]["name"] + ("." if reference else "") + reference
            break

        self._reference = reference

        self._size = self._program.get_header(self._reference)

    def to_smt(self) -> Any:
        if isinstance(self._reference, str):
            return self._program.get_header_var(self._reference).to_smt()
        else:
            return self._reference.to_smt()

    def used_vars(self, pf: PureFormula) -> set[Variable]:
        return {self.variable}

    def substitute(
            self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return self.variable.substitute(pf, mapping)

    def __len__(self) -> int:
        return self._size

    def __str__(self) -> str:
        return str(self._reference)


class MethodCall(Expression):
    pass


class BVAnd(BinaryExpression):
    def __init__(
            self,
            program: ParserProgram,
            obj: dict | None = None,
            *,
            left: Expression | None = None,
            right: Expression | None = None,
    ) -> None:
        self._program = program
        self.left: Expression | None = None
        self.right: Expression | None = None

        if obj is not None:
            self.parse(obj)
        elif left is not None and right is not None:
            self.left = left
            self.right = right
        else:
            raise ValueError("Must provide either 'obj' or both 'left' and 'right'")

    def parse(self, obj: dict) -> None:
        """
        Parse a bitwise AND expression JSON into a BitwiseAnd object.

        :param obj: the bitwise AND expression JSON object
        """
        self.left = parse_expression(self._program, obj["left"])
        self.right = parse_expression(self._program, obj["right"], len(self.left))

    def to_smt(self) -> Any:
        return pysmt.BVAnd(self.left.to_smt(), self.right.to_smt())

    def substitute(
            self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        self.left = self.left.substitute(pf, mapping)
        self.right = self.right.substitute(pf, mapping)
        return self

    def __len__(self) -> int:
        return max(len(self.left), len(self.right))

    def __str__(self) -> str:
        return f"({self.left} & {self.right})"


class BVLShr(BinaryExpression):
    def __init__(
            self,
            program: ParserProgram,
            obj: dict | None = None,
            *,
            left: Expression | None = None,
            right: Expression | None = None,
    ) -> None:
        self._program = program
        self.left: Expression | None = None
        self.right: Expression | None = None

        if obj is not None:
            self.parse(obj)
        elif left is not None and right is not None:
            self.left = left
            self.right = right
        else:
            raise ValueError("Must provide either 'obj' or both 'left' and 'right'")

    def parse(self, obj: dict) -> None:
        """
        Parse a bitwise shift right expression JSON into a BitwiseShiftRight object.

        :param obj: the bitwise shift right expression JSON object
        """
        self.left = parse_expression(self._program, obj["left"])
        self.right = parse_expression(self._program, obj["right"], len(self.left))

    def to_smt(self) -> Any:
        return pysmt.BVLShr(self.left.to_smt(), self.right.to_smt())

    def substitute(
            self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        self.left = self.left.substitute(pf, mapping)
        self.right = self.right.substitute(pf, mapping)
        return self

    def __len__(self) -> int:
        return len(self.left)

    def __str__(self) -> str:
        return f"({self.left} >> {self.right})"


_EXPRESSION_DISPATCH: dict[
    str, Callable[[ParserProgram, dict, int | None], Expression]
] = {
    "Concat": lambda program, component, size_context: Concatenate(
        program=program, obj=component
    ),
    "Slice": lambda program, component, size_context: Slice(
        program=program, obj=component
    ),
    "Constant": lambda program, component, size_context: Constant(
        obj=component, size_context=size_context
    ),
    "Member": lambda program, component, size_context: Reference(
        program=program, obj=component
    ),
    "MethodCallExpression": lambda program, component, size_context: MethodCall(
        program=program, obj=component
    ),
    "PathExpression": lambda program, component, size_context: Reference(
        program=program, obj=component
    ),
    "DefaultExpression": lambda program, component, size_context: DontCare(),
    "BAnd": lambda program, component, size_context: BVAnd(
        program=program, obj=component
    ),
    "Shr": lambda program, component, size_context: BVLShr(
        program=program, obj=component
    ),
}


def parse_expression(
        program: ParserProgram, component: dict, size_context: int = None
) -> Expression:
    """
    Parse a P4 expression component into an Expression object.

    :param program: the ParserProgram this expression belongs to
    :param component: the JSON object representing the expression
    :param size_context: an optional size context for disambiguating bit-width
    :return: an Expression object representing the parsed component
    """
    node_type = component.get("Node_Type")
    factory = _EXPRESSION_DISPATCH.get(node_type)

    if factory is None:
        logger.warning(f"Unknown expression node type: {node_type}")
        return DontCare()

    return factory(program, component, size_context)
