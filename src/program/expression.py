"""
This module defines Expression, a class representing an expression in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from typing import Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class Concatenate:
    def __init__(self, obj: dict) -> None:
        self.left = None
        self.right = None
        if obj is not None:
            self.parse(obj)

    def parse(self, obj: dict) -> None:
        self.left = Expression(obj["left"])
        self.right = Expression(obj["right"])

    def eval(self, store: Dict[str, str]) -> str:
        left_value = self.left.eval(store)
        right_value = self.right.eval(store)
        return left_value + right_value

    def __repr__(self) -> str:
        return f"Concatenate(left={self.left!r}, right={self.right!r})"

    def __str__(self) -> str:
        return f"{self.left} ++ {self.right}"


class Slice:
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

    def eval(self, store: Dict[str, str]) -> Tuple[Dict[str, str], str]:
        value = self.reference.eval(store)
        return value[self.lsb : self.msb]

    def __repr__(self) -> str:
        return (
            f"Slice(reference={self.reference!r}, msb={self.msb!r}, lsb={self.lsb!r})"
        )

    def __str__(self) -> str:
        return f"{self.reference}[{self.msb}:{self.lsb}]"


class Expression:
    def __init__(self, component: dict) -> None:
        self.value = None
        if component is not None:
            self.parse(component)

    def parse(self, component: dict) -> None:
        logger.debug(f"Parsing expression: {component}")
        match component["Node_Type"]:
            case "Constant":
                self.value = Constant(component)
            case "Slice":
                self.value = Slice(component)
            case "Concat":
                self.value = Concatenate(component)
            case "Member" | "PathExpression":
                self.value = Reference(component)
            case _:
                logger.warning(
                    f"Ignoring Expression of type '{component['Node_Type']}'"
                )

    def eval(self, store: Dict[str, str]) -> str:
        return self.value.eval(store)

    def __repr__(self) -> str:
        return f"Expression(value={self.value!r})"

    def __str__(self) -> str:
        return str(self.value)


class Constant:
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


class Reference:
    def __init__(self, component: dict) -> None:
        self.reference = None
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
            return store[self.reference]
        else:
            logger.warning(f"Reference '{self.reference}' not found in store.")
            return ""

    def __repr__(self) -> str:
        return f"Reference(reference={self.reference!r})"

    def __str__(self) -> str:
        return str(self.reference)


# class LValue:
#     def __init__(self, component: dict) -> None:
#         if component is not None:
#             self.parse(component)
#
#     def parse(self, component: dict) -> None | Slice | Reference:
#         match component["Node_Type"]:
#             case "Slice":
#                 return Slice(component)
#             case "Member":
#                 return Reference(component)
#             case _:
#                 logger.warning(f"Ignoring LValue of type '{component['Node_Type']}'")
#         return None
