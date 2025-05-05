"""
This module defines SelectExpression, a class representing the transition block of a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging

from src.parser_program.Slice import Slice

logger = logging.getLogger(__name__)


class SelectExpression:
    """A class representing the transition block of a P4 parser state."""

    def __init__(self, select_expr: dict = None) -> None:
        self.value = None
        self.cases = {}
        if select_expr is not None:
            self.parse(select_expr)

    def parse(self, select_expr: dict) -> None:
        """Parse a selectExpression JSON into a SelectExpression object."""
        select_type = select_expr["Node_Type"]
        match select_type:
            case "SelectExpression":
                self._parse_select_expression(select_expr)
            case "PathExpression":
                self.cases["*"] = select_expr["path"]["name"]
            case _:
                logger.warning(f"Ignoring selectExpression of type: {select_type}")

    def _parse_select_expression(self, select_expr: dict) -> None:
        """Parse a selectExpression JSON into a SelectExpression object."""
        selectValue = select_expr["select"]["components"]["vec"]
        if len(selectValue) != 1:
            logger.warning("Select value has more than one component")

        for component in selectValue:
            select_type = component["Node_Type"]
            match select_type:
                case "Slice":
                    self.value = Slice(component)
                case _:
                    logger.warning(f"Ignoring select value of type '{select_type}'")

        for case in select_expr["selectCases"]["vec"]:
            case_value = case["keyset"]["value"]
            case_state = case["state"]["path"]["name"]
            self.cases[case_value] = case_state

    def __repr__(self) -> str:
        return f"SelectExpression(value={repr(self.value)}, cases={self.cases!r})"

    def __str__(self) -> str:
        lines = ["SelectExpression", f"  Value: {self.value}", "  Cases:"]
        for key, state in self.cases.items():
            lines.append(f"    {key} → {state}")
        return "\n".join(lines)
