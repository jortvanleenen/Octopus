"""
This module defines classes for symbolic execution.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from abc import ABC, abstractmethod

from pysmt.shortcuts import (
    Symbol,
    BV,
    BVConcat,
    BVExtract,
    And,
    TRUE,
    Exists,
    Not,
    Equals,
    Or,
)
from pysmt.typing import BVType

from kangaroo.bit_vector import BitVector
from kangaroo.utils import AutoRepr
from program.expression import Expression


class PureFormula:
    """A formula that should be template-guarded for symbolic execution."""

    class Subformula(ABC):
        """A class representing a subformula in a PureFormula."""

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

    class Variable(Subformula, AutoRepr):
        def __init__(self, name: str, size: int):
            self.name = name
            self._size = size

        def __len__(self):
            return self.size

        def to_smt(self):
            return Symbol(self.name, BVType(self.size))

        def __eq__(self, other: "PureFormula"):
            if isinstance(other, PureFormula.Variable):
                return self.name == other.name and self.size == other.size
            return False

        def __str__(self):
            return f"{self.name}({self.size})"

    class BufferLeft(Subformula, AutoRepr):
        def __init__(self, bv: BitVector):
            self.bv = bv

        @property
        def size(self) -> int:
            return len(self.bv)

        def to_smt(self):
            return BV(self.bv.bits, self.size)

        def __str__(self):
            return f"buf<({self.bv})"

        def __repr__(self):
            return f"{self.__class__.__name__}(bv={self.bv!r})"

    class BufferRight(Subformula, AutoRepr):
        def __init__(self, bv: BitVector):
            self.bv = bv

        def __str__(self):
            return f"buf>({self.bits})"

        @property
        def size(self) -> int:
            return len(self.bv)

        def to_smt(self):
            return BV(self.bits, self.width)

    class FieldLeft(Subformula, AutoRepr):
        def __init__(self, field: str, bv: BitVector):
            self.field = field
            self.bv = bv

        def __str__(self):
            return f"st<.{self.field}({self.bits})"

        @property
        def size(self) -> int:
            return len(self.bv)

        def to_smt(self):
            return BV(self.bv.bits, self.size)

    class FieldRight(Subformula, AutoRepr):
        def __init__(self, field: str, bv: BitVector):
            self.field = field
            self.bv: BitVector = bv

        @property
        def width(self) -> int:
            return len(self.bits)

        def to_smt(self):
            return BV(self.bits, self.width)

        def __str__(self):
            return f"st>.{self.field}({self.bits})"

    class BitString(Subformula, AutoRepr):
        def __init__(self, bits: str):
            super().__init__(bits)

        def __str__(self):
            return f"bs({self.bits})"

        @property
        def width(self) -> int:
            return len(self.bits)

        def to_smt(self):
            return BV(self.bits, self.width)

    class Not(Subformula, AutoRepr):
        def __init__(self, subformula: "PureFormula.Subformula"):
            self.subformula = subformula

        def to_smt(self):
            return Not(self.subformula.to_smt())

        def __str__(self):
            return f"¬{self.subformula}"

    class And(Subformula, AutoRepr):
        def __init__(
            self, left: "PureFormula.Subformula", right: "PureFormula.Subformula"
        ):
            pass

    # class Exists(Subformula, AutoRepr):
    #     def __init__(self, variable: "PureFormula.Variable", subformula: "PureFormula.Subformula"):
    #         self.variable = variable
    #         self.subformula = subformula

    class TRUE(Subformula, AutoRepr):
        def to_smt(self):
            return TRUE()

        def __str__(self):
            return "TRUE"

    class Equals(Subformula, AutoRepr):
        def __init__(
            self, left: Expression, right: Expression
        ):
            assert left.bits == right.bits, "Bitvector mismatch in equality"
            self.left = left
            self.right = right

        def __str__(self):
            return f"{self.left} == {self.right}"

        def to_smt(self):
            return Equals(self.left.to_symbolic(), self.right.to_symbolic())

    def __init__(self):
        self.equalities: list[PureFormula.Equals] = []
        self.used_vars: set[PureFormula.Variable] = set()
        self.next_free_var_name: int = 0
        self.header_field_vars: dict[tuple[str, bool], PureFormula.Variable] = {}
        self.buf_vars: dict[bool, PureFormula.Variable] | None = None


    def get_header_field_var(self, name: str, left: bool):
        return self.header_field_vars.get((name, left), None)

    def set_header_field_var(self, name: str, left: bool, variable: "PureFormula.Variable"):
        """Set a header variable by name, ensuring it is unique."""
        self.header_field_vars[(name, left)] = variable
        self.used_vars.add(variable)

    def get_buffer_var(self, left: bool) -> "PureFormula.Variable":
        """Get the buffer variable."""
        var = self.buf_vars.get(left, None)
        if var is None:
            self.buf_vars[left] = self.fresh_variable(0)
        return self.buf_vars[left]

    def set_buffer_var(self, left: bool, var: "PureFormula.Variable") -> None:
        self.buf_vars[left] = var
        self.used_vars.add(var)

    def fresh_variable(self, size: int) -> "PureFormula.Variable":
        while True:
            name = str(self.next_free_var_name)
            self.next_free_var_name += 1
            if name not in self.used_vars:
                self.used_vars.add(name)
                return PureFormula.Variable(name, size)

    def substitute(self, mapping: dict["PureFormula.Variable", "PureFormula.Subformula"]) -> None:
        new_equalities = []
        for eq in self.equalities:
            left = self._substitute_expr(eq.left, mapping)
            right = self._substitute_expr(eq.right, mapping)
            new_equalities.append(PureFormula.Equals(left, right))
        self.equalities = new_equalities

    def _substitute_expr(
        self,
        expr: "PureFormula.Subformula",
        mapping: dict[str, "PureFormula.Subformula"],
    ) -> "PureFormula.Subformula":
        if isinstance(expr, PureFormula.Variable):
            return mapping.get(expr.name, expr)
        elif isinstance(expr, PureFormula.Slice):
            base = self._substitute_expr(expr.base, mapping)
            return PureFormula.Slice(base, expr.hi, expr.lo)
        elif isinstance(expr, PureFormula.Concat):
            left = self._substitute_expr(expr.left, mapping)
            right = self._substitute_expr(expr.right, mapping)
            return PureFormula.Concat(left, right)
        else:
            return expr

    def to_smt(self):
        if not self.equalities:
            return TRUE()
        return Exists(*[v for v in self.used_vars], Or(*[eq.to_smt() for eq in self.equalities]))

    def __str__(self):
        return " ∧ ".join(str(eq) for eq in self.equalities)


class GuardedFormula(AutoRepr):
    """A template-guarded formula for symbolic execution."""

    def __init__(
        self,
        state_left: str = None,
        state_right: str = None,
        buffer_length_left: int = None,
        buffer_length_right: int = None,
        pure_formula: PureFormula = None,
    ) -> None:
        self.state_l = state_left
        self.state_r = state_right
        self.buf_len_l = buffer_length_left
        self.buf_len_r = buffer_length_right
        self.pf = pure_formula

    def equal_template(self, other: "GuardedFormula") -> bool:
        """Check if two template-guarded formulas are equal."""
        return (
                self.state_l == other.state_l
                and self.state_r == other.state_r
                and self.buf_len_l == other.buf_len_l
                and self.buf_len_r == other.buf_len_r
        )