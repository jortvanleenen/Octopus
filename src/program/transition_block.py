"""
This module defines TransitionBlock, a class representing the transition block of a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from typing import TYPE_CHECKING

from bisimulation.symbolic.formula import (
    PureFormula,
    FormulaManager,
    Equals,
    And,
    Not,
    FormulaNode,
    TRUE,
)
from program.expression import DontCare, Expression, parse_expression

if TYPE_CHECKING:
    from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class TransitionBlock:
    """A class representing the transition block of a P4 parser state."""

    def __init__(
        self, program: "ParserProgram", select_expr: dict | None = None
    ) -> None:
        """
        Initialise a TransitionBlock object.

        :param select_expr: the selectExpression JSON object
        """
        self._program = program
        self._selectors: list[Expression] = []
        self._cases: dict[tuple[Expression, ...], str] = {}
        if select_expr is not None:
            self.parse(select_expr)

    @property
    def selectors(self) -> list[Expression]:
        """Get the selectors of the transition block."""
        return self._selectors

    @property
    def cases(self) -> dict[tuple[Expression, ...], str]:
        """Get the cases of the transition block."""
        return self._cases

    def parse(self, select_expr: dict) -> None:
        """
        Parse a selectExpression JSON into a SelectExpression object.

        :param select_expr: the selectExpression JSON object
        """
        select_type: str = select_expr["Node_Type"]
        match select_type:
            case "SelectExpression":
                self._parse_select_expression(select_expr)
            case "PathExpression":
                selector: tuple[Expression] = (DontCare(),)
                to_state_name: str = select_expr["path"]["name"]
                self._cases[selector] = to_state_name
                logger.info(f"Parsed 'dont_care' transition to '{to_state_name}'")
            case _:
                logger.warning(f"Ignoring selectExpression of type '{select_type}'")

    def _parse_select_expression(self, select_expr: dict) -> None:
        """Parse a selectExpression JSON into a SelectExpression object."""

        for expression in select_expr["select"]["components"]["vec"]:
            self._selectors.append(parse_expression(self._program, expression))

        for case in select_expr["selectCases"]["vec"]:
            for_values = []
            keyset = case["keyset"]
            if "value" in keyset:
                for_values.append(
                    parse_expression(self._program, keyset, len(self._selectors[0]))
                )
            else:
                for i, expression in enumerate(keyset["components"]["vec"]):
                    for_values.append(
                        parse_expression(
                            self._program, expression, len(self._selectors[i])
                        )
                    )
            to_state_name = case["state"]["path"]["name"]
            self._cases[tuple(for_values)] = to_state_name

            logger.info(f"Parsed transition to '{to_state_name}' for '{for_values}'")

    def eval(self, store: dict) -> str:
        """
        Evaluate the transition block with the given store.

        :param store: the store containing the values for the selectors
        :return: the name of the state to transition to, or "reject" if no match is found
        """
        if len(self._selectors) == 0:
            return self._cases[tuple([DontCare()])]

        evaluated_selectors = [expression.eval(store) for expression in self._selectors]
        for key, state in self._cases.items():
            if len(key) != len(evaluated_selectors):
                logger.warning(
                    f"Key length {len(key)} does not match evaluated values length {len(evaluated_selectors)}"
                )
                continue

            evaluated_for_values = [expression.eval(store) for expression in key]
            if evaluated_for_values == evaluated_selectors:
                return state

        return "reject"

    def __repr__(self) -> str:
        return f"TransitionBlock(values={self._selectors!r}, cases={self._cases!r})"

    def __str__(self) -> str:
        n_spaces = 2
        output = []
        if self._selectors:
            output.append(f"Values: ({', '.join(str(v) for v in self._selectors)})")

        output.append("Cases:")
        for key, state in self._cases.items():
            key_str = ", ".join(str(k) for k in key)
            output.append(" " * n_spaces + f"({key_str}) -> {state}")
        return "\n".join(output)

    def symbolic_transition(
        self, manager: FormulaManager, pf: PureFormula
    ) -> set[tuple[FormulaNode, str]]:
        """
        Generate symbolic transitions based on the transition block and a given pure formula.

        :param manager: the formula manager to create fresh variables
        :param pf: the pure formula, representing the current state
        :return: a set of tuples containing the symbolic formula and the state to transition to
        """
        if len(self._selectors) == 0:
            return {
                (TRUE(), self._cases[tuple([DontCare()])])
            }

        symbolic_cases: set[tuple[FormulaNode, str]] = set()
        seen: set[FormulaNode] = set()
        fresh_variables = [manager.fresh_variable(len(v)) for v in self._selectors]
        for for_values, to_state in self._cases.items():
            formula = None
            for i, v in enumerate(for_values):
                if formula is None:
                    formula = Equals(fresh_variables[i], v)
                formula = And(formula, Equals(v, fresh_variables[i]))
            seen.add(formula)
            for f in seen:
                formula = And(formula, Not(f))
            symbolic_cases.add((formula, to_state))

        return symbolic_cases
