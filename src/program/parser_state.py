"""
This module defines ParserState, a class representing a state in a P4 parser block.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from typing import TYPE_CHECKING

from program.operation_block import OperationBlock
from program.transition_block import TransitionBlock

if TYPE_CHECKING:
    from program.parser_program import ParserProgram


logger = logging.getLogger(__name__)


class ParserState:
    """A class representing a state in a P4 parser block."""

    def __init__(
        self,
        program: "ParserProgram",
        components: dict | None = None,
        select_expr: dict | None = None,
    ) -> None:
        """ "
        Initialise a ParserState object.

        :param program: the ParserProgram object this state belongs to
        :param components: the components JSON object of the state
        :param select_expr: the selectExpression JSON object of the state
        """
        self._program: ParserProgram = program
        self._operationBlock: OperationBlock | None = None
        self._transitionBlock: TransitionBlock | None = None
        if components is not None and select_expr is not None:
            self.parse(components, select_expr)

    @property
    def operation_block(self) -> OperationBlock | None:
        """Get the operation block of this parser state."""
        return self._operationBlock

    @property
    def transition_block(self) -> TransitionBlock | None:
        """Get the transition block of this parser state."""
        return self._transitionBlock

    @property
    def program(self) -> "ParserProgram":
        """Get the ParserProgram this state belongs to."""
        return self._program

    def parse(self, components: dict, select_expr: dict) -> None:
        """
        Parse components and selectExpression JSONs into a ParserState object.

        :param components: the components JSON object of the state
        :param select_expr: the selectExpression JSON object of the state
        """
        self._operationBlock = OperationBlock(self._program, components)
        self._transitionBlock = TransitionBlock(self._program, select_expr)

    def __repr__(self) -> str:
        return (
            f"ParserState(operations={self._operationBlock!r}, "
            f"transitions={self._transitionBlock!r})"
        )

    def __str__(self) -> str:
        n_spaces = 2
        output = [
            "Operations:",
            "\n".join(
                n_spaces * " " + line for line in str(self._operationBlock).splitlines()
            ),
            "Transitions:",
            "\n".join(
                n_spaces * " " + line
                for line in str(self._transitionBlock).splitlines()
            ),
        ]
        return "\n".join(output)
