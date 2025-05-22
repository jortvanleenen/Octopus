"""
This module defines Expression, a class hierarchy representing an expression in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class Expression(ABC):
    @abstractmethod
    def eval(self, store: Dict[str, str]) -> str:
        pass

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class Concatenate(Expression):
    def __init__(self, obj: dict) -> None:
        self.left = None
        self.right = None
        if obj is not None:
            self.parse(obj)

    def parse(self, obj: dict) -> None:
        self.left = parse_expression(obj["left"])
        self.right = parse_expression(obj["right"])

    def eval(self, store: Dict[str, str]) -> str:
        left_value: str = self.left.eval(store)
        right_value: str = self.right.eval(store)
        return left_value + right_value

    def __repr__(self) -> str:
        return f"Concatenate(left={self.left!r}, right={self.right!r})"

    def __str__(self) -> str:
        return f"{self.left} ++ {self.right}"


class Slice(Expression):
    def __init__(self, slice: dict = None) -> None:
        self.reference = None
        self.msb = None
        self.lsb = None
        if slice is not None:
            self.parse(slice)

    def parse(self, slice: dict) -> None:
        self.reference = Reference(slice["e0"])
        self.msb = slice["e1"]["value"]
        self.lsb = slice["e2"]["value"]

    def eval(self, store: Dict[str, str]) -> str:
        value = self.reference.eval(store)
        new_lsb = len(value) - self.msb - 1
        new_msb = len(value) - self.lsb
        if new_lsb < 0 or new_msb < 0 or new_lsb >= len(value) or new_msb > len(value):
            logger.warning(
                f"Slice indices out of range: lsb={self.lsb}, msb={self.msb}, value length={len(value)}"
            )
            return ""
        return value[new_lsb:new_msb]

    def __repr__(self) -> str:
        return (
            f"Slice(reference={self.reference!r}, msb={self.msb!r}, lsb={self.lsb!r})"
        )

    def __str__(self) -> str:
        return f"{self.reference}[{self.msb}:{self.lsb}]"


class Constant(Expression):
    def __init__(self, component: dict) -> None:
        self.numeric_value: int | float | None = None
        self.value: str | None = None
        if component is not None:
            self.parse(component)

    def parse(self, component: dict) -> None:
        self.numeric_value = component["value"]
        self.value = bin(self.numeric_value)[2:]  # Convert to binary string

    def eval(self, store: Dict[str, str]) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Constant(value={self.value!r})"

    def __str__(self) -> str:
        return str(self.value)


class DontCare(Expression):
    def eval(self, store: Dict[str, str]):  # Type hint?
        return self
        # pass

    def __hash__(self) -> int:
        return 0  # fixed value: all DontCares are "equal" and hash identically

    def __eq__(self, other) -> bool:
        return True

    def __repr__(self) -> str:
        return "DontCare()"

    def __str__(self) -> str:
        return "*"


class Reference(Expression):
    def __init__(self, component: dict) -> None:
        self.reference: str | None = None
        if component is not None:
            self.parse(component)

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

    def eval(self, store: Dict[str, str]) -> str:
        if self.reference in store:
            if self.reference == "hdr.udp.label":
                print("test")
            return store[self.reference]
        else:
            logger.warning(f"Reference '{self.reference}' not found in store.")
            return ""

    def __repr__(self) -> str:
        return f"Reference(reference={self.reference!r})"

    def __str__(self) -> str:
        return str(self.reference)


_expression_dispatch = {
    "Constant": Constant,
    "Slice": Slice,
    "Concat": Concatenate,
    "Member": Reference,
    "PathExpression": Reference,
    "DefaultExpression": DontCare,
}


def parse_expression(component: dict) -> Expression:
    logger.debug(f"Parsing expression: {component}")
    cls = _expression_dispatch.get(component["Node_Type"], DontCare)
    return cls(component) if cls is not DontCare else cls()
