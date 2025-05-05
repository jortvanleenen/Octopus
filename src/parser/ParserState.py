"""
This module defines ParserState, a class representing a state in a P4 parser.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging

from src.parser.SelectExpression import SelectExpression
from src.parser.Component import Component

logger = logging.getLogger(__name__)


class ParserState:
    """A class representing a state in a P4 parser."""

    def __init__(self, components: dict = None, select_expr: dict = None) -> None:
        self.operations = None
        self.transitions = None
        if components is not None and select_expr is not None:
            self.parse(components, select_expr)

    def parse(self, components: dict, select_expr: dict) -> None:
        """Parse components and selectExpression JSONs into a ParserState object."""
        self.operations = [Component(comp) for comp in components["vec"]]
        self.transitions = SelectExpression(select_expr)

    def __repr__(self) -> str:
        return (
            f"ParserState(operations={self.operations!r}, "
            f"transitions={self.transitions!r})"
        )

    def __str__(self) -> str:
        lines = ["ParserState"]
        if self.operations:
            lines.append("  Operations:")
            for op in self.operations:
                lines.append(f"    {op}")
        else:
            lines.append("  Operations: None")

        lines.append(f"  Transitions: {self.transitions or 'None'}")
        return "\n".join(lines)
