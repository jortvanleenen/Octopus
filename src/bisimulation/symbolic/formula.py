"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

class PureFormula:
    class Expression:
        def __init__(self):
            pass

    class Equality:
        def __init__(self, left: "PureFormula.Expression", right: "PureFormula.Expression") -> None:
            self.left: PureFormula.Expression = left
            self.right: PureFormula.Expression = right

    def __init__(self):
        self.equalities: [PureFormula.Equality] = []

    def substitute(self, formula: "PureFormula") -> None:
        pass


class TemplateGuardedFormula:
    def __init__(
        self,
        state_left: str = None,
        state_right: str = None,
        buffer_length_left: int = None,
        buffer_length_right: int = None,
        formula: PureFormula = None,
    ) -> None:
        self.state_left = state_left
        self.state_right = state_right
        self.buffer_length_left = buffer_length_left
        self.buffer_length_right = buffer_length_right
        self.formula = formula


def strongest_postcondition():
    pass

def transition