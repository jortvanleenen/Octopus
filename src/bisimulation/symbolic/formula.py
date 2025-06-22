"""
This module defines classes for symbolic execution.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from __future__ import annotations

import copy
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

import pysmt.shortcuts as pysmt

from octopus.utils import AutoRepr

if TYPE_CHECKING:
    from program.expression import Expression

logger = logging.getLogger(__name__)


class FormulaNode(ABC):
    """An abstract base class for formula nodes in symbolic execution."""

    @abstractmethod
    def to_smt(self, pf: PureFormula) -> Any:
        """
        Get the SMT representation of the formula.

        :param pf: the PureFormula in which the expression occurs
        :return: the SMT representation of the expression
        """
        pass

    @abstractmethod
    def used_vars(self, pf: PureFormula) -> set[Variable]:
        """
        Get the set of variables used in this formula node.

        :param pf: the PureFormula in which the expression occurs
        :return: a set of Variable instances used in this formula node
        """
        pass

    @abstractmethod
    def substitute(
        self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        """
        Substitute variables in the formula with the given mapping.

        :param pf: the PureFormula in which the expression occurs
        :param mapping: a dictionary mapping Variable to FormulaNode
        :return: a formula node obtained after substitution
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

    def to_smt(self, pf: PureFormula) -> Any:
        return pysmt.Symbol(self.name, pysmt.BVType(self._size))

    def used_vars(self, pf: PureFormula) -> set[Variable]:
        return {self}

    def substitute(
        self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
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

    def to_smt(self, pf: PureFormula) -> Any:
        return pysmt.Not(self.subformula.to_smt(pf))

    def used_vars(self, pf: PureFormula) -> set[Variable]:
        return self.subformula.used_vars(pf)

    def substitute(
        self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return Not(self.subformula.substitute(pf, mapping))

    def __str__(self):
        return f"¬{self.subformula}"


class And(AutoRepr, FormulaNode):
    def __init__(self, left: FormulaNode, right: FormulaNode):
        self.left = left
        self.right = right

    def to_smt(self, pf) -> Any:
        return pysmt.And(self.left.to_smt(pf), self.right.to_smt(pf))

    def used_vars(self, pf: PureFormula) -> set[Variable]:
        return self.left.used_vars(pf) | self.right.used_vars(pf)

    def substitute(
        self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return And(
            self.left.substitute(pf, mapping),
            self.right.substitute(pf, mapping),
        )

    def __str__(self):
        return f"{self.left} & {self.right}"


class TRUE(AutoRepr, FormulaNode):
    def to_smt(self, pf) -> Any:
        return pysmt.TRUE()

    def used_vars(self, pf) -> set[Variable]:
        return set()

    def substitute(
        self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return TRUE()

    def __str__(self):
        return "TRUE"


class Concatenate(AutoRepr, FormulaNode):
    def __init__(self, left: Expression | FormulaNode, right: Expression | FormulaNode):
        self.left = left
        self.right = right

    def to_smt(self, pf: PureFormula) -> Any:
        # TODO: check order
        return pysmt.BVConcat(self.left.to_smt(pf), self.right.to_smt(pf))

    def used_vars(self, pf: PureFormula) -> set["Variable"]:
        return self.left.used_vars(pf) | self.right.used_vars(pf)

    def substitute(
        self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return Concatenate(
            self.left.substitute(pf, mapping),
            self.right.substitute(pf, mapping),
        )

    def __len__(self):
        return len(self.left) + len(self.right)

    def __str__(self):
        return f"{self.left} ++ {self.right}"


class Equals(AutoRepr, FormulaNode):
    def __init__(self, left: Expression | FormulaNode, right: Expression | FormulaNode):
        self.left = left
        self.right = right

    def __str__(self):
        return f"{self.left} == {self.right}"

    def to_smt(self, pf: PureFormula) -> Any:
        return pysmt.Equals(self.left.to_smt(pf), self.right.to_smt(pf))

    def used_vars(self, pf: PureFormula) -> set[Variable]:
        return self.left.used_vars(pf) | self.right.used_vars(pf)

    def substitute(
        self, pf: PureFormula, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        return Equals(
            self.left.substitute(pf, mapping),
            self.right.substitute(pf, mapping),
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
    def __init__(
        self,
        root: FormulaNode = TRUE(),
        header_field_vars: dict[tuple[str, bool], Variable] = None,
        buf_vars: dict[bool, Variable] = None,
        used_vars: set[Variable] = None,
    ):
        self.root = root
        self._header_field_vars = (
            header_field_vars if header_field_vars is not None else {}
        )

        self._buf_vars = buf_vars if buf_vars is not None else {}
        self._used_vars = (
            used_vars if used_vars is not None else self.root.used_vars(self)
        )

    @classmethod
    def clone(
        cls,
        root: FormulaNode,
        header_field_vars: dict[tuple[str, bool], Variable],
        buf_vars: dict[bool, Variable],
    ):
        return cls(
            copy.deepcopy(root),
            copy.deepcopy(header_field_vars),
            copy.deepcopy(buf_vars),
        )

    @property
    def header_field_vars(self) -> dict[tuple[str, bool], Variable]:
        return self._header_field_vars

    @property
    def buf_vars(self) -> dict[bool, Variable]:
        return self._buf_vars

    @property
    def used_vars(self) -> set[Variable]:
        return self._used_vars

    def get_header_field_var(self, name: str, left: bool) -> Variable | None:
        """
        Get the Variable object for the given header field name.

        :param name: name of the header field
        :param left: whether to get the header field for the left or right parser
        :return: the Variable object if found, else None
        """
        return self.header_field_vars.get((name, left))

    def set_header_field_var(self, name: str, left: bool, variable: Variable) -> None:
        """
        Set the Variable object for the given header field name.

        :param name: name of the header field
        :param left: whether to set the header field for the left or right parser
        :param variable: the Variable object to set for the header field
        """
        self.header_field_vars[(name, left)] = variable
        if variable is None:
            print("gattie wel lekke?")
        self.used_vars.add(variable)

    def get_buffer_var(self, left: bool) -> Variable | None:
        """
        Get the Variable object for the given buffer field name.

        :param left: whether to get the buffer field for the left or right parser
        :return: the Variable object if found, else None
        """
        return self._buf_vars.get(left)

    def set_buffer_var(self, left: bool, var: Variable | None) -> None:
        """
        Set the Variable object for the given buffer field name.

        :param left: whether to set the buffer field for the left or right parser
        :param var: the Variable object to set for the buffer field
        """
        # if var is None:
        #     old_var = self.get_buffer_var(left)
        #     if old_var is not None and old_var in self.used_vars:
        #         self.used_vars.remove(old_var)

        self._buf_vars[left] = var
        if var is not None:
            self.used_vars.add(var)

    def substitute(self, mapping: dict[Variable, FormulaNode]) -> None:
        """
        Substitute variables in the formula with the given mapping.

        :param mapping: a dictionary mapping Variable to FormulaNode
        """
        self.root = self.root.substitute(self, mapping)
        self._used_vars = {v for v in self.used_vars if v not in mapping}

    def to_smt(self):
        print("TOSMT", self.used_vars)
        return pysmt.Exists(
            variables=[v.to_smt(self) for v in self.used_vars],
            formula=self.root.to_smt(self),
        )

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
        prev_guarded_formula: GuardedFormula = None,
    ) -> None:
        self.state_l = state_left
        self.state_r = state_right
        self.buf_len_l = buffer_length_left
        self.buf_len_r = buffer_length_right
        self.pf = pure_formula
        self.prev_guarded_formula = prev_guarded_formula

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
