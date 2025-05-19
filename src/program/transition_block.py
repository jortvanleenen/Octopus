"""
This module defines TransitionBlock, a class representing the transition block of a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging

from src.program.expression import Expression, DontCare

logger = logging.getLogger(__name__)


class TransitionBlock:
    """A class representing the transition block of a P4 parser state."""

    def __init__(self, select_expr: dict = None) -> None:
        self.values = []
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
                to_state_name = select_expr["path"]["name"]
                for_values = [DontCare()]
                self.cases[tuple(for_values)] = to_state_name
            case _:
                logger.warning(f"Ignoring selectExpression of type '{select_type}'")

    def _parse_select_expression(self, select_expr: dict) -> None:
        """Parse a selectExpression JSON into a SelectExpression object."""

        for expression in select_expr["select"]["components"]["vec"]:
            self.values.append(Expression(expression))

        for case in select_expr["selectCases"]["vec"]:
            for_values = []
            keyset = case["keyset"]
            if "value" in keyset:
                for_values.append(Expression(case["keyset"]))
            else:
                for expression in keyset["components"]["vec"]:
                    for_values.append(Expression(expression))
            to_state_name = case["state"]["path"]["name"]
            self.cases[tuple(for_values)] = to_state_name

    def eval(self, store: dict) -> str:
        if len(self.values) == 0:
            return self.cases[tuple([DontCare()])]
        evaluated_values = [expression.eval(store) for expression in self.values]
        for key, state in self.cases.items():
            if len(key) != len(evaluated_values):
                logger.warning(
                    f"Key length {len(key)} does not match evaluated values length {len(evaluated_values)}"
                )
                continue

            evaluated_for_values = [expression.eval(store) for expression in key]
            if evaluated_for_values == evaluated_values:
                return state
        return "reject"

    def __repr__(self) -> str:
        return f"TransitionBlock(values={self.values!r}, cases={self.cases!r})"

    def __str__(self) -> str:
        n_spaces = 2
        output = []
        if self.values:
            output.append(f"Values: ({', '.join(str(v) for v in self.values)})")

        output.append("Cases:")
        for key, state in self.cases.items():
            key_str = ", ".join(str(k) for k in key)
            output.append(" " * n_spaces + f"({key_str}) -> {state}")
        return "\n".join(output)
