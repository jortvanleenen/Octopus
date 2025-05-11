"""
This module defines Expression, a class representing an expression in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

class Expression:
    class Concatenate:
        pass

    class Slice:
        def __init__(self, slice: dict = None) -> None:
            self.base = None
            self.hi = None
            self.lo = None
            if slice is not None:
                self.parse(slice)

        def parse(self, slice: dict) -> None:
            store = ""
            expr_obj = slice["e0"]
            while True:
                if "member" in expr_obj:
                    store = expr_obj["member"] + ("." if store else "") + store

                if "expr" in expr_obj:
                    expr_obj = expr_obj["expr"]
                else:
                    break
            self.base = store
            self.hi = slice["e1"]["value"]
            self.lo = slice["e2"]["value"]

        def eval(self, parser):
            value = parser.getValue(self.base)
            return value[self.lo : self.hi]

        def __repr__(self) -> str:
            return f"Slice(base={self.base!r}, hi={self.hi}, lo={self.lo})"

        def __str__(self) -> str:
            return f"Slice from {self.base}[{self.hi}:{self.lo}]"

