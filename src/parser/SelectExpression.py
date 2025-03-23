"""
This module defines SelectExpression, a class representing the transition block of a P4 parser state.

Author: Jort van Leenen
License: MIT
"""


class SelectExpression:
    """A class representing the transition block of a P4 parser state."""

    def __init__(self, select_expr: dict = None) -> None:
        self.transition = None

    def parse(self, select_expr: dict) -> None:
        if select_expr["Node_Type"] == "PathExpression":
            self.transition = select_expr["path"]["name"]
        else:
            pass