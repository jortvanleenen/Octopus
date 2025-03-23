"""
This module defines ParserState, a class representing a state in a P4 parser.

Author: Jort van Leenen
License: MIT
"""

import logging

logger = logging.getLogger(__name__)

class ParserState:
    """A class representing a state in a P4 parser."""

    def __init__(self, components: dict = None, select_expr: dict = None) -> None:

        if components is not None and select_expr is not None:
            self.parse(components, select_expr)

    def parse(self, components: dict, select_expr: dict) -> None:
        pass
