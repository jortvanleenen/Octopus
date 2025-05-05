"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging

logger = logging.getLogger(__name__)


class Component:
    """A class representing a state in a P4 parser."""

    def __init__(self, component: dict = None) -> None:
        self.operation = None
        if component is not None:
            self.parse(component)

    def parse(self, component: dict):
        """Parse a component JSON into a Component object."""
        operation_type = component["Node_Type"]
        match operation_type:
            case "MethodCallStatement":
                self.operation = self._parse_method_call(component)
            case _:
                logger.warning(f"Ignoring component of type '{operation_type}'")


    def _parse_method_call(self, component: dict):
        """Parse a method call JSON into a Component object."""
        call = component["methodCall"]
        function_name = call["method"]["member"]
        arguments = call["arguments"]["vec"]
        if len(arguments) != 1:
            logger.warning(f"Method call '{function_name}' has more than one argument")
        store = arguments[0]["expression"]["member"]
        return function_name, store

    def __repr__(self) -> str:
        return f"Component(operation={self.operation!r})"

    def __str__(self) -> str:
        return f"Component: {self.operation}"