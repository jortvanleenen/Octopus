"""
This module defines Slice, a class representing a slice operation in a P4 parser state.

Author: Jort van Leenen
License: MIT
"""


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

    def __repr__(self) -> str:
        return f"Slice(base={self.base!r}, hi={self.hi}, lo={self.lo})"

    def __str__(self) -> str:
        return f"Slice from {self.base}[{self.hi}:{self.lo}]"
