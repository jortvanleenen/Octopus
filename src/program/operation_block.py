"""
This module defines OperationBlock, a class representing the operation block of a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from bisimulation.symbolic.formula import FormulaManager, PureFormula
from program.component import Assignment, Component, Extract, parse_method_call

if TYPE_CHECKING:
    from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


class OperationBlock(Component):
    """A class representing the operation block of a P4 parser state."""

    def __init__(self, program: ParserProgram, components: dict = None):
        """
        Initialise an OperationBlock object.

        :param program: the ParserProgram this operation block belongs to
        :param components: the components JSON object, which contains a list of components
        """
        self._program: ParserProgram = program
        self._components = []
        self._size: int = 0

        if components is not None:
            self.parse(components)

    @property
    def program(self) -> ParserProgram:
        """
        Get the ParserProgram this operation block belongs to.

        :return: the ParserProgram object
        """
        return self._program

    @property
    def components(self) -> list[Component]:
        """
        Get the components of the operation block.

        :return: a list of Component objects
        """
        return self._components

    @property
    def size(self) -> int:
        """
        Get the size of the operation block.

        :return: the size of the operation block, which is the sum of the sizes of its components
        """
        return self._size

    def parse(self, components: dict) -> None:
        """
        Parse the components JSON object into an OperationBlock object.

        At the moment, this only supports AssignmentStatement and MethodCallStatement components.

        :param components: the components JSON object, which contains a list of components
        """
        for component in components["vec"]:
            match component["Node_Type"]:
                case "AssignmentStatement":
                    parsed_component = Assignment(self._program, component)
                case "MethodCallStatement":
                    parsed_component = parse_method_call(self._program, component)
                    if isinstance(parsed_component, Extract):
                        self._size += parsed_component.size
                case _:
                    logger.warning(
                        f"Ignoring unknown component type '{component['Node_Type']}'"
                    )
                    continue
            self._components.append(parsed_component)

    def eval(self, store: dict[str, str], buffer: str):
        for component in self._components:
            store, buffer = component.eval(store, buffer)
        return store, buffer

    def strongest_postcondition(
        self, manager: FormulaManager, pf: PureFormula
    ) -> PureFormula:
        for component in self._components:
            pf = component.strongest_postcondition(manager, pf)
        return pf

    def __len__(self):
        return self._size

    def __repr__(self) -> str:
        return f"OperationBlock(size={self._size!r}, components={self._components!r})"

    def __str__(self) -> str:
        return "\n".join(f"{component}" for component in self._components)
