"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT
"""


class Component:
    def __init__(self, component: dict = None) -> None:
        self.operation = None
        self.parse(component)
