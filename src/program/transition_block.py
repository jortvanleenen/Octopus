"""
This module defines TransitionBlock, a class representing the transition block of a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from __future__ import annotations

import copy
import logging
from typing import TYPE_CHECKING

from bisimulation.symbolic.formula import (
    TRUE,
    And,
    Equals,
    FormulaNode,
    Not,
)
from program.expression import DontCare, Expression, parse_expression

if TYPE_CHECKING:
    from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class TransitionBlock:
    """A class representing the transition block of a P4 parser state."""

    def __init__(self, program: ParserProgram, select_expr: dict | None = None):
        """
        Initialise a TransitionBlock object.

        :param program: the ParserProgram this transition block belongs to
        :param select_expr: the selectExpression JSON object
        """
        self._program = program
        self._selectors: list[Expression] = []
        self._cases: dict[tuple[Expression, ...], str] = {}
        if select_expr is not None:
            self.parse(select_expr)

    @property
    def program(self) -> ParserProgram:
        """
        Get the ParserProgram this transition block belongs to.

        :return: the ParserProgram object
        """
        return self._program

    @property
    def selectors(self) -> list[Expression]:
        """
        Get the selectors of the transition block.

        An example of selectors: 'transition select(selector1, ...) { ... }'

        :return: a list of Expression objects representing the selectors
        """
        return self._selectors

    @property
    def cases(self) -> dict[tuple[Expression, ...], str]:
        """
        Get the cases of the transition block.

        An example of cases: 'transition select(...){ (for_expr1, ...): state_name; ... }'

        :return: a dictionary mapping tuples of Expression objects to state names
        """
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
        """
        Parse a selectExpression JSON into a SelectExpression object.

        :param select_expr: the selectExpression JSON object
        """
        for expression in select_expr["select"]["components"]["vec"]:
            self._selectors.append(parse_expression(self._program, expression))
            logger.info(f"Parsed selector: {self._selectors[-1]}")

        for case in select_expr["selectCases"]["vec"]:
            for_exprs = []
            keyset = case["keyset"]
            if "components" in keyset and "vec" in keyset["components"]:
                for i, expression in enumerate(keyset["components"]["vec"]):
                    for_exprs.append(
                        parse_expression(
                            self._program, expression, len(self._selectors[i])
                        )
                    )
            else:
                for_exprs.append(
                    parse_expression(self._program, keyset, len(self._selectors[0]))
                )
            to_state_name = case["state"]["path"]["name"]
            self._cases[tuple(for_exprs)] = to_state_name

            logger.info(f"Parsed transition to '{to_state_name}' for '{for_exprs}'")

    def symbolic_transition(self, pf) -> set[tuple[FormulaNode, str]]:
        """
        Generate symbolic transitions based on the transition block.

        :param pf: the PureFormula representing the current state of symbolic execution
        :return: a set of tuples containing the symbolic condition and the state to transition to
        """
        if len(self._selectors) == 0:
            return {(TRUE(), self._cases[tuple([DontCare()])])}

        symbolic_transitions: set[tuple[FormulaNode, str]] = set()
        seen: set[FormulaNode] = set()
        for for_exprs, to_state in self._cases.items():
            formula = TRUE()
            for i, expr in enumerate(for_exprs):
                if not isinstance(expr, DontCare):
                    expr_copy = copy.deepcopy(expr)
                    expr_copy.to_formula(pf)
                    selector_copy = copy.deepcopy(self._selectors[i])
                    selector_copy.to_formula(pf)
                    formula = And(formula, Equals(expr_copy, selector_copy))
            appended_formula = formula
            for seen_formula in seen:
                appended_formula = And(appended_formula, Not(seen_formula))

            seen.add(formula)
            symbolic_transitions.add((appended_formula, to_state))

        logger.debug(f"Symbolic transitions (left: {self._program.is_left}):")
        for condition, state in symbolic_transitions:
            logger.debug(f"  {condition} -> {state}")
        return symbolic_transitions

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
