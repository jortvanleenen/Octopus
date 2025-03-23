"""
This module defines ParserState, a class representing a state in a P4 parser.

Author: Jort van Leenen
License: MIT
"""

import logging

from src.parser.SelectExpression import SelectExpression
from src.parser.Component import Component

logger = logging.getLogger(__name__)


class ParserState:
    """A class representing a state in a P4 parser."""

    def __init__(self, components: dict = None, select_expr: dict = None) -> None:
        self.operation = None
        self.transition = None
        if components is not None and select_expr is not None:
            self.parse(components, select_expr)

    def parse(self, components: dict, select_expr: dict) -> None:
        """Parse components and selectExpression JSONs into a ParserState object."""
        self.operation = Component(components)
        self.transition = SelectExpression(select_expr)
