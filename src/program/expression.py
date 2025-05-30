"""
This module defines Expression, a class hierarchy representing an expression in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

import pysmt.shortcuts

if TYPE_CHECKING:
    from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class Expression(ABC):
    @abstractmethod
    def eval(self, store: dict[str, str]) -> str:
        """
        Evaluate the expression using the provided store.

        :param store: the current store
        :return: the evaluated value of the expression
        """
        pass

    @abstractmethod
    def to_symbolic(self):
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class Concatenate(Expression):
    def __init__(self, program: "ParserProgram", obj: dict) -> None:
        self._program = program
        self.left = None
        self.right = None
        if obj is not None:
            self.parse(obj)

    def parse(self, obj: dict) -> None:
        self.left = parse_expression(self._program, obj["left"])
        self.right = parse_expression(self._program, obj["right"])

    def eval(self, store: dict[str, str]) -> str:
        left_value: str = self.left.eval(store)
        right_value: str = self.right.eval(store)
        return left_value + right_value

    def to_symbolic(self):
        left_symbolic = self.left.to_symbolic()
        right_symbolic = self.right.to_symbolic()

        return pysmt.shortcuts.BVConcat(left_symbolic, right_symbolic)

    def __len__(self) -> int:
        return self.left.size + self.right.size

    def __repr__(self) -> str:
        return f"Concatenate(left={self.left!r}, right={self.right!r})"

    def __str__(self) -> str:
        return f"{self.left} ++ {self.right}"


class Slice(Expression):
    def __init__(self, program: "ParserProgram", obj: dict = None) -> None:
        self._program = program
        self.reference = None
        self.msb = None
        self.lsb = None
        if obj is not None:
            self.parse(obj)

    def parse(self, slice: dict) -> None:
        self.reference = Reference(self._program, slice["e0"])
        length = len(self.reference)

        msb = slice["e1"]["value"]
        lsb = slice["e2"]["value"]
        self.lsb = length - msb - 1
        self.msb = length - lsb

    def eval(self, store: dict[str, str]) -> str:
        value = self.reference.eval(store)
        return value[self.lsb : self.msb]

    def to_symbolic(self):
        reference_symbolic = self.reference.to_symbolic()
        return pysmt.shortcuts.BVExtract(reference_symbolic, self.lsb, self.msb)

    def __len__(self) -> int:
        return self.msb - self.lsb + 1

    def __repr__(self) -> str:
        return (
            f"Slice(reference={self.reference!r}, msb={self.msb!r}, lsb={self.lsb!r})"
        )

    def __str__(self) -> str:
        return f"{self.reference}[{self.msb}:{self.lsb}]"


class Constant(Expression):
    def __init__(self, obj: dict, size_context: int) -> None:
        self.numeric_value: int | float | None = None
        self.value: str | None = None
        self._size: int | None = size_context
        if obj is not None:
            self.parse(obj)

    def parse(self, component: dict) -> None:
        self.numeric_value = component["value"]
        self.value = bin(self.numeric_value)[2:]  # Convert to binary string
        if self._size is not None:
            self.value = self.value.zfill(self._size)

    def eval(self, store: dict[str, str]) -> str:
        return self

    def to_symbolic(self):
        return pysmt.shortcuts.BV(self.numeric_value, len(self))

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

    def __repr__(self) -> str:
        return f"Constant(value={self.value!r})"

    def __str__(self) -> str:
        return str(self.value)


class DontCare(Expression):
    def __init__(self) -> None:
        pass

    def eval(self, store: dict[str, str]) -> "DontCare":
        return self

    def to_symbolic(self):
        return pysmt.shortcuts.TRUE()

    def __hash__(self) -> int:
        return 0  # fixed value: all DontCares are "equal" and hash identically

    def __eq__(self, other) -> bool:
        return True

    def __repr__(self) -> str:
        return "DontCare()"

    def __str__(self) -> str:
        return "*"


class Reference(Expression):
    def __init__(self, program: "ParserProgram", obj: dict) -> None:
        self._program = program
        self.reference: str | None = None
        self._size: int = 0
        if obj is not None:
            self.parse(obj)

    def parse(self, component: dict) -> None:
        reference = ""
        while True:
            if "member" in component:
                reference = component["member"] + ("." if reference else "") + reference

            if "expr" in component:
                component = component["expr"]
                continue

            if "path" in component:
                reference = (
                    component["path"]["name"] + ("." if reference else "") + reference
                )
            break

        self.reference = reference

        header_content: dict = self._program.get_header_fields(self.reference)
        self._size = sum(header_content.values())

    def eval(self, store: dict[str, str]) -> str:
        if self.reference in store:
            return store[self.reference]
        else:
            logger.warning(f"Reference '{self.reference}' not found in store.")
            return ""

    def to_symbolic(self):
        return pysmt.shortcuts.FreshSymbol("BVType")

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"Reference(reference={self.reference!r})"

    def __str__(self) -> str:
        return str(self.reference)


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
