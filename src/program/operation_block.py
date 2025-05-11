"""
This module defines OperationBlock, a class representing the operation block of a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from typing import TYPE_CHECKING, Dict

from src.program.component import Component, Extract

if TYPE_CHECKING:
    from src.program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class OperationBlock:
    """A class representing the operation block of a P4 parser state."""

    def __init__(self, program: "ParserProgram", components: dict = None) -> None:
        self.program: ParserProgram = program
        self.components = []
        self.size: int = 0

        if components is not None:
            self.parse(components)

    def parse(self, components: dict) -> None:
        """Parse the components JSON object into an OperationBlock object."""
        for component in components["vec"]:
            match component["Node_Type"]:
                case "AssignmentStatement":
                    parsed_component = Assignment(self.program, component)
                case "MethodCallStatement":
                    parsed_component = Extract(self.program, component)
                    self.size += parsed_component.size
                case _:
                    logger.warning(f"Ignoring unknown component type '{component["Node_Type"]}'")
            self.components.append(parsed_component)

    def eval(self, store: Dict[str, str], buffer: str):
        """Evaluate the operation block."""
        for component in self.components:
            store, buffer = component.eval(store, buffer)

    def __repr__(self) -> str:
        return f"OperationBlock(components={self.components!r})"

    def __str__(self) -> str:
        return f"OperationBlock: {self.components}"