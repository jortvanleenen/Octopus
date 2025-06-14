"""
This module defines Expression, a class hierarchy representing an expression in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, Any

from pysmt.shortcuts import TRUE, FreshSymbol, BV, BVExtract
from pysmt.typing import BVType

from octopus.utils import AutoRepr

if TYPE_CHECKING:
    from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class Expression(ABC):
    """An abstract base class representing an expression in a P4 parser state."""

    @abstractmethod
    def eval(self, store: dict[str, str]) -> str:
        """
        Evaluate the expression using the provided store.

        :param store: the current store
        :return: the evaluated value of the expression
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class Concatenate(AutoRepr, Expression):
    def __init__(self, program: "ParserProgram", obj: dict) -> None:
        self._program = program
        self.left: Expression | None = None
        self.right: Expression | None = None
        if obj is not None:
            self.parse(obj)

    def parse(self, obj: dict) -> None:
        """
        Parse a concatenation expression JSON into a Concatenate object.

        :param obj: the concatenation expression JSON object
        """
        self.left = parse_expression(self._program, obj["left"])
        self.right = parse_expression(self._program, obj["right"])

    def eval(self, store: dict[str, str]) -> str:
        left_value: str = self.left.eval(store)
        right_value: str = self.right.eval(store)
        return left_value + right_value

    def __len__(self) -> int:
        return len(self.left) + len(self.right)

    def __str__(self) -> str:
        return f"{self.left} ++ {self.right}"


class Slice(AutoRepr, Expression):
    def __init__(self, program: "ParserProgram", obj: dict = None) -> None:
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
        length = len(self.reference)

        msb = obj["e1"]["value"]
        lsb = obj["e2"]["value"]
        self.lsb = length - msb - 1
        self.msb = length - lsb

    def eval(self, store: dict[str, str]) -> str:
        value = self.reference.eval(store)
        return value[self.lsb : self.msb]

    def to_smt(self) -> Any:
        reference_symbolic = self.reference.to_smt()
        return BVExtract(reference_symbolic, self.lsb, self.msb - 1)  # BVExtract has inclusive msb

    def __len__(self) -> int:
        return self.msb - self.lsb

    def __str__(self) -> str:
        return f"{self.reference}[{self.msb}:{self.lsb}]"


class Constant(AutoRepr, Expression):
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

    def eval(self, store: dict[str, str]) -> str:
        return self.value

    def to_smt(self) -> Any:
        return BV(self.numeric_value, len(self))

    def __len__(self) -> int:
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


class DontCare(AutoRepr, Expression):
    def __init__(self) -> None:
        pass

    def eval(self, store: dict[str, str]) -> "DontCare":
        return self

    def to_smt(self) -> Any:
        return TRUE()

    def __len__(self) -> int:
        return 0

    def __hash__(self) -> int:
        return 0  # fixed value: all DontCares are "equal" and hash identically

    def __eq__(self, other) -> bool:
        return True

    def __str__(self) -> str:
        return "*"


class Reference(AutoRepr, Expression):
    def __init__(self, program: "ParserProgram", obj: dict) -> None:
        self._program = program
        self._reference: str | None = None
        self._size: int = 0
        if obj is not None:
            self.parse(obj)

    @property
    def reference(self) -> str:
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

    def eval(self, store: dict[str, str]) -> str:
        if self._reference in store:
            return store[self._reference]
        else:
            logger.warning(f"Reference '{self._reference}' not found in store.")
            return ""

    def to_smt(self) -> Any:
        return FreshSymbol(BVType(self._size))

    def __len__(self) -> int:
        return self._size

    def __str__(self) -> str:
        return str(self._reference)


_EXPRESSION_DISPATCH: dict[
    str, Callable[["ParserProgram", dict, int | None], Expression]
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
    "PathExpression": lambda program, component, size_context: Reference(
        program=program, obj=component
    ),
    "DefaultExpression": lambda program, component, size_context: DontCare(),
}


def parse_expression(
    program: "ParserProgram", component: dict, size_context: int = None
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
