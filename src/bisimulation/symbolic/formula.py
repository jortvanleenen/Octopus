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
    Equals,
    And,
    TRUE,
    Exists,
    Not,
)
from pysmt.typing import BVType

from kangaroo.bit_vector import BitVector
from kangaroo.utils import AutoRepr
from program.component import Assignment, MethodCall, Extract
from program.operation_block import OperationBlock
from program.parser_program import ParserProgram
from program.transition_block import TransitionBlock


class PureFormula:
    """A formula that should be template-guarded for symbolic execution."""

    class Subformula(ABC):
        """A class representing a subformula in a PureFormula."""

        @property
        @abstractmethod
        def size(self) -> int:
            """Get the size of the bit vector underlying the subformula."""
            pass

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
            self.n_bits = size

        @property
        def size(self) -> int:
            return self.n_bits

        def to_smt(self):
            return Symbol(self.name, BVType(self.size))

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

    class Slice(Subformula, AutoRepr):
        def __init__(self, base: "PureFormula.Subformula", msb: int, lsb: int):
            assert msb >= 0 and lsb >= 0, "Slice indices must be non-negative"
            assert msb >= lsb, "Invalid slice range: msb must be ≥ lsb"
            assert msb < base.size and lsb < base.size, "Slice indices out of bounds"

            sliced_bits = base.bits[msb:lsb]
            super().__init__(sliced_bits)

            self.base = base
            self.hi = msb
            self.lo = lsb

        def __str__(self):
            return f"{self.base}[{self.hi}:{self.lo}]"

        @property
        def width(self):
            return len(self.bits)

        def to_smt(self):
            return BVExtract(self.base.to_smt(), start=self.hi, end=self.lo)

    class Concat(Subformula, AutoRepr):
        def __init__(
            self, left: "PureFormula.Subformula", right: "PureFormula.Subformula"
        ):
            self.left = left
            self.right = right
            self.bits = left.bits + right.bits

        def __str__(self):
            return f"({self.left} ++ {self.right})"

        @property
        def width(self):
            return len(self.bits)

        def to_smt(self):
            return BVConcat(self.left.to_smt(), self.right.to_smt())

    class Equality(AutoRepr):
        def __init__(
            self, left: "PureFormula.Subformula", right: "PureFormula.Subformula"
        ):
            assert left.bits == right.bits, "Bitvector mismatch in equality"
            self.left = left
            self.right = right

        def __str__(self):
            return f"{self.left} == {self.right}"

        def to_smt(self):
            # Exists <all variables in left and right>, Equals(left smt, right smt)
            return Exists()  # TODO

    def __init__(self):
        self.equalities: list[PureFormula.Equality] = []
        self.used_variable_names: set[str] = set()
        self.next_free_variable_index: int = 0

    def fresh_variable(self, size: int) -> "PureFormula.Variable":
        while True:
            name = str(self.next_free_variable_index)
            self.next_free_variable_index += 1
            if name not in self.used_variable_names:
                self.used_variable_names.add(name)
                return PureFormula.Variable(name, size)

    def substitute(self, mapping: dict[str, "PureFormula.Subformula"]) -> None:
        new_equalities = []
        for eq in self.equalities:
            left = self._substitute_expr(eq.left, mapping)
            right = self._substitute_expr(eq.right, mapping)
            new_equalities.append(PureFormula.Equality(left, right))
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
        return And(*[eq.to_smt() for eq in self.equalities])

    def __str__(self):
        return " ∧ ".join(str(eq) for eq in self.equalities)


class TemplateGuardedFormula(AutoRepr):
    """A template-guarded formula for symbolic execution."""

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


def strongest_postcondition(
    formula: TemplateGuardedFormula, operationBlock: OperationBlock, left: bool
):
    pf = formula.formula

    for component in operationBlock.components:
        if isinstance(component, Assignment):
            pass  # TODO
        elif isinstance(component, Extract):
            field_name = component.header_reference
            field_width = component.size

            y = pf.fresh_variable(field_width)

            if left:
                field = PureFormula.FieldLeft(field_name, )
                buffer = PureFormula.Equality(PureFormula.BufferLeft())
            else:
                field = PureFormula.FieldRight(field_name, )



        else:
            raise NotImplementedError(f"Unknown component type: {type(component)}")


def symbolic_transition(transition_block: TransitionBlock) -> list[tuple[object, str]]:
    symbolic_values = [v.to_symbolic() for v in transition_block.values]

    for

    return transitions

