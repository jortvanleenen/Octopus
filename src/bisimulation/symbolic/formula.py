"""
This module defines classes for symbolic execution.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pysmt.shortcuts as pysmt

from octopus.utils import AutoRepr

if TYPE_CHECKING:
    from program.expression import Expression

logger = logging.getLogger(__name__)


class FormulaNode(ABC):
    """An abstract base class for formula nodes in symbolic execution."""

    @abstractmethod
    def to_smt(self):
        """Get the SMT representation of the formula."""
        pass

    @abstractmethod
    def used_vars(self) -> set[Variable]:
        """
        Get the set of variables used in this formula node.

        :return: a set of Variable instances used in this formula node
        """
        pass

    @abstractmethod
    def substitute(self, mapping: dict[Variable, FormulaNode]) -> FormulaNode:
        """
        Substitute variables in the formula with the given mapping.

        :param mapping: a dictionary mapping Variable to FormulaNode
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class Variable(AutoRepr, FormulaNode):
    def __init__(self, name: str, size: int):
        if size <= 0:
            raise ValueError("Size of variable must be greater than 0")
        self.name = name
        self._size = size

    def to_smt(self):
        return pysmt.Symbol(self.name, pysmt.BVType(self._size))

    def used_vars(self) -> set[Variable]:
        return {self}

    def substitute(self, mapping: dict[Variable, FormulaNode]) -> FormulaNode:
        return mapping.get(self, self)

    def __len__(self):
        return self._size

    def __hash__(self):
        return hash((self.name, self._size))

    def __eq__(self, other: FormulaNode) -> bool:
        if isinstance(other, Variable):
            return self.name == other.name and self._size == other._size
        return False

    def __str__(self):
        return f"{self.name}({self._size})"


class Not(AutoRepr, FormulaNode):
    def __init__(self, subformula: FormulaNode):
        self.subformula = subformula

    def to_smt(self):
        return pysmt.Not(self.subformula.to_smt())

    def used_vars(self) -> set[Variable]:
        return self.subformula.used_vars()

    def substitute(self, mapping: dict[Variable, FormulaNode]) -> FormulaNode:
        return Not(self.subformula.substitute(mapping))

    def __str__(self):
        return f"¬{self.subformula}"


class And(AutoRepr, FormulaNode):
    def __init__(self, left: FormulaNode, right: FormulaNode):
        self.left = left
        self.right = right

    def to_smt(self):
        return pysmt.And(self.left.to_smt(), self.right.to_smt())

    def used_vars(self) -> set[Variable]:
        return self.left.used_vars() | self.right.used_vars()

    def substitute(self, mapping: dict[Variable, FormulaNode]) -> FormulaNode:
        return And(
            self.left.substitute(mapping),
            self.right.substitute(mapping),
        )

    def __str__(self):
        return f"{self.left} & {self.right}"


class TRUE(AutoRepr, FormulaNode):
    def to_smt(self):
        return pysmt.TRUE()

    def used_vars(self) -> set[Variable]:
        return set()

    def substitute(self, mapping: dict[Variable, FormulaNode]) -> FormulaNode:
        return TRUE()

    def __str__(self):
        return "TRUE"


class Concatenate(AutoRepr, FormulaNode):
    def __init__(self, left: Expression | FormulaNode, right: Expression | FormulaNode):
        self.left = left
        self.right = right

    def to_smt(self):
        # TODO: check order
        return pysmt.BVConcat(self.left.to_smt(), self.right.to_smt())

    def used_vars(self) -> set["Variable"]:
        return self.left.used_vars() | self.right.used_vars()

    def substitute(self, mapping: dict[Variable, FormulaNode]) -> FormulaNode:
        return Concatenate(
            self.left.substitute(mapping),
            self.right.substitute(mapping),
        )

    def __str__(self):
        return f"{self.left} ++ {self.right}"


class Equals(AutoRepr, FormulaNode):
    def __init__(self, left: Expression | FormulaNode, right: Expression | FormulaNode):
        self.left = left
        self.right = right

    def __str__(self):
        return f"{self.left} == {self.right}"

    def to_smt(self):
        return pysmt.Equals(self.left.to_smt(), self.right.to_smt())

    def used_vars(self) -> set[Variable]:
        return self.left.used_vars() | self.right.used_vars()

    def substitute(self, mapping: dict[Variable, FormulaNode]) -> FormulaNode:
        return Equals(
            self.left.substitute(mapping),
            self.right.substitute(mapping),
        )


class FormulaManager(AutoRepr):
    def __init__(self):
        self._next_free_var_name: int = 0

    def fresh_name(self) -> str:
        """
        Generate a fresh variable name.

        :return: a unique variable name as a string
        """
        name = str(self._next_free_var_name)
        self._next_free_var_name += 1
        return name

    def fresh_variable(self, size: int) -> Variable:
        """
        Create a fresh variable with a unique name and specified size.

        :param size: the size of the variable
        :return: a Variable instance with a unique name and specified size
        """
        return Variable(self.fresh_name(), size)


class PureFormula(AutoRepr):
    def __init__(self, root: FormulaNode = TRUE()):
        self.root = root
        self.used_vars: set[Variable] = self.root.used_vars()
        self.header_field_vars: dict[tuple[str, bool], Variable] = {}
        self.buf_vars: dict[bool, Variable] = {}

    @classmethod
    def clone_with_new_root(
        cls, original: PureFormula, new_root: FormulaNode
    ) -> "PureFormula":
        new_pf = cls(root=new_root)
        new_pf.header_field_vars = dict(original.header_field_vars)
        new_pf.buf_vars = dict(original.buf_vars)
        return new_pf

    def get_header_field_var(self, name: str, left: bool) -> Variable | None:
        return self.header_field_vars.get((name, left))

    def set_header_field_var(self, name: str, left: bool, variable: Variable):
        self.header_field_vars[(name, left)] = variable
        self.used_vars.add(variable)

    def get_buffer_var(self, left: bool) -> Variable | None:
        return self.buf_vars.get(left)

    def set_buffer_var(self, left: bool, var: Variable | None) -> None:
        self.buf_vars[left] = var
        self.used_vars.add(var)

    def substitute(self, mapping: dict[Variable, FormulaNode]) -> None:
        """
        Substitute variables in the formula with the given mapping.

        :param mapping: a dictionary mapping Variable to FormulaNode
        """
        self.root = self.root.substitute(mapping)
        self.used_vars = {v for v in self.used_vars if v not in mapping}

    def to_smt(self):
        return pysmt.Exists(
            variables=[v.to_smt() for v in self.used_vars],
            formula=self.root.to_smt(),
        )

    def used_vars(self) -> set[Variable]:
        return self.used_vars

    def __str__(self):
        return "E " + ", ".join(str(v) for v in self.used_vars) + f". {self.root}"


class GuardedFormula(AutoRepr):
    """A template-guarded formula for symbolic execution."""

    def __init__(
        self,
        state_left: str = None,
        state_right: str = None,
        buffer_length_left: int = None,
        buffer_length_right: int = None,
        pure_formula: PureFormula = PureFormula(),
    ) -> None:
        self.state_l = state_left
        self.state_r = state_right
        self.buf_len_l = buffer_length_left
        self.buf_len_r = buffer_length_right
        self.pf = pure_formula

    def has_equal_guard(self, other: GuardedFormula) -> bool:
        """
        Check if the guard of this formula is equal to another.

        :param other: the GuardedFormula to compare with
        :return: True if the guards are equal, False otherwise
        """
        return (
            self.state_l == other.state_l
            and self.state_r == other.state_r
            and self.buf_len_l == other.buf_len_l
            and self.buf_len_r == other.buf_len_r
        )
