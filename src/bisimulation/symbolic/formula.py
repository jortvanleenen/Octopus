"""
This module defines classes for symbolic execution.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from abc import ABC, abstractmethod

import pysmt.shortcuts as pysmt

from octopus.utils import AutoRepr
from program.expression import Expression, Constant

logger = logging.getLogger(__name__)


class FormulaNode(ABC):
    """An abstract base class for formula nodes in symbolic execution."""

    @abstractmethod
    def to_smt(self):
        """Get the SMT representation of the formula."""
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

    def __str__(self):
        return f"¬{self.subformula}"


class And(AutoRepr, FormulaNode):
    def __init__(self, left: FormulaNode, right: FormulaNode):
        self.left = left
        self.right = right

    def to_smt(self):
        return pysmt.And(self.left.to_smt(), self.right.to_smt())

    def __str__(self):
        return f"{self.left} & {self.right}"


class TRUE(AutoRepr, FormulaNode):
    def to_smt(self):
        return pysmt.TRUE()

    def __str__(self):
        return "TRUE"


class Concatenate(AutoRepr, FormulaNode):
    def __init__(self, left: Expression | FormulaNode, right: Expression | FormulaNode):
        self.left = left
        self.right = right

    def to_smt(self):
        return pysmt.BVConcat(self.left.to_smt(), self.right.to_smt())

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


class PureFormula(AutoRepr, FormulaNode):
    def __init__(self, root: FormulaNode = TRUE()):
        self.root = root
        self.used_vars: set[Variable] = self._used_vars(self.root)
        self.header_field_vars: dict[tuple[str, bool], Variable] = {}
        self.buf_vars: dict[bool, Variable] = {}

    @classmethod
    def clone_with_new_root(
        cls, original: "PureFormula", new_root: FormulaNode
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
        self.root = self._substitute(self.root, mapping)
        self.used_vars = {v for v in self.used_vars if v not in mapping}

    def _substitute(
        self, node: FormulaNode, mapping: dict[Variable, FormulaNode]
    ) -> FormulaNode:
        """
        Recursively substitute variables in the formula nodes.

        :param node: the current formula node to substitute
        :param mapping: a dictionary mapping Variable to FormulaNode
        :return: the substituted formula node
        """
        if isinstance(node, Variable):
            return mapping.get(node, node)
        elif isinstance(node, Not):
            return Not(self._substitute(node.subformula, mapping))
        elif isinstance(node, And):
            return And(
                self._substitute(node.left, mapping),
                self._substitute(node.right, mapping),
            )
        elif isinstance(node, Equals):
            return Equals(
                self._substitute(node.left, mapping),
                self._substitute(node.right, mapping),
            )
        elif isinstance(node, TRUE):
            return TRUE()
        elif isinstance(node, Concatenate):
            return Concatenate(
                self._substitute(node.left, mapping),
                self._substitute(node.right, mapping),
            )
        else:
            raise TypeError(f"Unsupported formula node type: {type(node)}")

    def _used_vars(self, node: FormulaNode) -> set[Variable]:
        """
        Recursively collect all used variables in the formula.

        :param node: the current formula node to check
        :return: a set of used Variable instances
        """
        if isinstance(node, Variable):
            return {node}
        elif isinstance(node, Not):
            return self._used_vars(node.subformula)
        elif isinstance(node, And):
            return self._used_vars(node.left) | self._used_vars(node.right)
        elif isinstance(node, Equals):
            return self._used_vars(node.left) | self._used_vars(node.right)
        elif isinstance(node, TRUE):
            return set()
        elif isinstance(node, Concatenate):
            return self._used_vars(node.left) | self._used_vars(node.right)
        elif isinstance(node, Constant):
            return set()
        else:
            logger.warning(f"Unsupported formula node type for used_vars: {type(node)}")
            return set()

    def to_smt(self):
        return pysmt.Exists(
            variables=[v.to_smt() for v in self.used_vars],
            formula=self.root.to_smt(),
        )

    def __str__(self):
        return " E " + ", ".join(str(v) for v in self.used_vars) + f". {self.root}"


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

    def equal_guard(self, other: "GuardedFormula") -> bool:
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
