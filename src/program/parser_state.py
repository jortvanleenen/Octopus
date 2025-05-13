"""
This module defines ParserState, a class representing a state in a P4 parser.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging

from src.program.operation_block import OperationBlock
from src.program.transition_block import TransitionBlock

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.program.parser_program import ParserProgram


logger = logging.getLogger(__name__)


class ParserState:
    """A class representing a state in a P4 parser."""

    def __init__(
        self,
        program: "ParserProgram",
        components: dict = None,
        select_expr: dict = None,
    ) -> None:
        self.program: ParserProgram = program
        self.operationBlock: OperationBlock | None = None
        self.transitionBlock: TransitionBlock | None = None
        if components is not None and select_expr is not None:
            self.parse(components, select_expr)

    def parse(self, components: dict, select_expr: dict) -> None:
        """Parse components and selectExpression JSONs into a ParserState object."""
        self.operationBlock = OperationBlock(self.program, components)
        self.transitionBlock = TransitionBlock(select_expr)

    def __repr__(self) -> str:
        return (
            f"ParserState(operations={self.operationBlock!r}, "
            f"transitions={self.transitionBlock!r})"
        )

    def __str__(self) -> str:
        n_spaces = 2
        output = [
            "Operations:",
            "\n".join(
                n_spaces * " " + line for line in str(self.operationBlock).splitlines()
            ),
            "Transitions:",
            "\n".join(
                n_spaces * " " + line for line in str(self.transitionBlock).splitlines()
            ),
        ]
        return "\n".join(output)
