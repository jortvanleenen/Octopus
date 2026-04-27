"""
This module defines Expression, a class hierarchy representing a subset of expressions in P4.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import pysmt.shortcuts as pysmt
from pysmt.shortcuts import BV, TRUE, BVConcat, BVExtract

from bisimulation.formula import (
    FormulaNode,
    Variable,
)

if TYPE_CHECKING:
    from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class Expression(FormulaNode):
    """An abstract base class representing an expression in a P4 parser state."""

    def used_vars(self) -> set[Variable]:
        return set()

    @abstractmethod
    def __len__(self) -> int:
        pass

    @staticmethod
    @abstractmethod
    def parse(program: ParserProgram, obj: dict, size_context: int) -> Expression:
        """
        Parse a JSON AST node into an Expression.

        :param program: parser context
        :param obj: JSON node
        :param size_context: bit-width context
        :return: Expression instance
        """
        pass


class BinaryExpression(Expression, ABC):
    """A mixin for binary expressions that have a left and right operand."""

    left: Expression
    right: Expression

    def used_vars(self) -> set[Variable]:
        return self.left.used_vars() | self.right.used_vars()


class Concatenate(BinaryExpression):
    def __init__(
            self,
            left: Expression,
            right: Expression,
    ) -> None:
        if left is None:
            raise ValueError(f"Left operand is required.")
        if right is None:
            raise ValueError(f"Right operand is required.")
        self.left = left
        self.right = right

    @staticmethod
    def parse(program: ParserProgram, obj: dict, size_context: int) -> Concatenate:
        return Concatenate(
            parse_expression(program, obj["left"]),
            parse_expression(program, obj["right"]),
        )

    def to_smt(self):
        return BVConcat(self.left.to_smt(), self.right.to_smt())

    def substitute(
            self, mapping: dict[Variable, FormulaNode]
    ) -> Concatenate:
        return Concatenate(
            self.left.substitute(mapping),
            self.right.substitute(mapping)
        )

    def __len__(self) -> int:
        return len(self.left) + len(self.right)

    def __str__(self) -> str:
        return f"({self.left}) ++ ({self.right})"


class Slice(Expression):
    def __init__(self, reference, msb, lsb) -> None:
        self.reference = reference
        self.msb = msb
        self.lsb = lsb

    @staticmethod
    def parse(program, obj: dict, size_context: int) -> Slice:
        return Slice(
            Reference.parse(program, obj["e0"], None),
            obj["e1"]["value"],
            obj["e2"]["value"]
        )

    def to_smt(self) -> Any:
        return BVExtract(
            self.reference.to_smt(), self.lsb, self.msb
        )  # BVExtract has both ends inclusive; start=msb, end=lsb

    def used_vars(self) -> set[Variable]:
        return self.reference.used_vars()

    def substitute(
            self, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return Slice(
            self.reference.substitute(mapping),
            self.msb,
            self.lsb
        )

    def __len__(self) -> int:
        return self.msb - self.lsb + 1

    def __str__(self) -> str:
        return f"{self.reference}[{self.msb}:{self.lsb}]"


class Constant(Expression):
    def __init__(self, numeric_value: int, size: int | None = None) -> None:
        self.numeric_value = numeric_value
        self.value = bin(self.numeric_value)[2:]  # Convert to binary string
        self._size = size
        if self._size is not None:
            self.value = self.value.zfill(self._size)

    @staticmethod
    def parse(program: ParserProgram, obj: dict, size_context: int) -> Constant:
        return Constant(obj["value"], size_context)

    def to_smt(self) -> Any:
        if self._size is None:
            logger.warning("No size for constant of value %s", self.numeric_value)
        return BV(self.numeric_value, len(self))

    def substitute(
            self, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return self

    def __len__(self) -> int:
        if self._size is None:
            logger.warning("No size for constant of value %s", self.numeric_value)
            return 0
        return self._size

    def __hash__(self) -> int:
        return hash((self.numeric_value, self._size))

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

    @staticmethod
    def parse(program: ParserProgram, obj: dict, size_context: int) -> DontCare:
        return DontCare()

    def to_smt(self) -> Any:
        return TRUE()

    def substitute(
            self, mapping: dict[Variable, FormulaNode]
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
    def __init__(self, reference: Variable, size: int):
        self._reference = reference
        self._size = size

    @property
    def reference(self) -> str | Variable | None:
        """Get the reference of the expression."""
        return self._reference

    @staticmethod
    def parse(program: ParserProgram, obj: dict, size_context: int) -> Reference:
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

        return Reference(
            program.get_header_var(reference),
            program.get_header(reference),
        )

    def to_smt(self) -> Any:
        return self._reference.to_smt()

    def used_vars(self) -> set[Variable]:
        return self._reference.used_vars()

    def substitute(
            self, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return self._reference.substitute(mapping)

    def __len__(self) -> int:
        return self._size

    def __str__(self) -> str:
        return str(self._reference)


class MethodCall(Expression):
    pass


class BVAnd(BinaryExpression):
    def __init__(
            self,
            left: Expression,
            right: Expression,
    ) -> None:
        self.left = left
        self.right = right

    @staticmethod
    def parse(program: ParserProgram, obj: dict, size_context: int) -> BVAnd:
        return BVAnd(
            parse_expression(program, obj["left"], size_context),
            parse_expression(program, obj["right"], size_context)
        )

    def to_smt(self) -> Any:
        return pysmt.BVAnd(self.left.to_smt(), self.right.to_smt())

    def substitute(
            self, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return BVAnd(
            self.left.substitute(mapping),
            self.right.substitute(mapping),
        )

    def __len__(self) -> int:
        return max(len(self.left), len(self.right))

    def __str__(self) -> str:
        return f"({self.left} & {self.right})"


class BVLShr(BinaryExpression):
    def __init__(
            self,
            left: Expression,
            right: Expression,
    ) -> None:
        self.left = left
        self.right = right

    @staticmethod
    def parse(program: ParserProgram, obj: dict, size_context: int) -> BVLShr:
        return BVLShr(
            parse_expression(program, obj["left"], size_context),
            parse_expression(program, obj["right"], size_context),
        )

    def to_smt(self) -> Any:
        return pysmt.BVLShr(self.left.to_smt(), self.right.to_smt())

    def substitute(
            self, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return BVLShr(
            self.left.substitute(mapping),
            self.right.substitute(mapping),
        )

    def __len__(self) -> int:
        return len(self.left)

    def __str__(self) -> str:
        return f"({self.left} >> {self.right})"


_EXPRESSION_DISPATCH: dict[
    str,
    type[Concatenate | Slice | Constant | Reference | MethodCall | DontCare | BVAnd | BVLShr]
] = {
    "Concat": Concatenate,
    "Slice": Slice,
    "Constant": Constant,
    "Member": Reference,
    "MethodCallExpression": MethodCall,
    "PathExpression": Reference,
    "DefaultExpression": DontCare,
    "BAnd": BVAnd,
    "Shr": BVLShr,
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
    cls = _EXPRESSION_DISPATCH.get(node_type)
    if cls is None:
        logger.warning(f"Unknown expression node type: {node_type}")
        return DontCare()

    return cls.parse(program, component, size_context)
