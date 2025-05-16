"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""


class PureFormula:
    class PureFormula:
        class Expression:
            def __str__(self) -> str:
                raise NotImplementedError

            @property
            def width(self) -> int:
                raise NotImplementedError

        class BufferLeft(Expression):
            def __init__(self, bits: str):
                self.bits = bits

            def __str__(self):
                return f"buf<({self.bits})"

            @property
            def width(self) -> int:
                return len(self.bits)

        class BufferRight(Expression):
            def __init__(self, bits: str):
                self.bits = bits

            def __str__(self):
                return f"buf>({self.bits})"

            @property
            def width(self) -> int:
                return len(self.bits)

        class FieldLeft(Expression):
            def __init__(self, field: str, bits: str):
                self.field = field
                self.bits = bits

            def __str__(self):
                return f"st<.{self.field}({self.bits})"

            @property
            def width(self) -> int:
                return len(self.bits)

        class FieldRight(Expression):
            def __init__(self, field: str, bits: str):
                self.field = field
                self.bits = bits

            def __str__(self):
                return f"st>.{self.field}({self.bits})"

            @property
            def width(self) -> int:
                return len(self.bits)

        class BitString(Expression):
            def __init__(self, bits: str):
                self.bits = bits

            def __str__(self):
                return f"bs({self.bits})"

            @property
            def width(self) -> int:
                return len(self.bits)

        class Slice(Expression):
            def __init__(self, base: "PureFormula.Expression", hi: int, lo: int):
                assert hi >= lo, "Invalid slice range"
                self.base = base
                self.hi = hi
                self.lo = lo
                self.bits = base.bits[base.width - 1 - hi : base.width - lo]

            def __str__(self):
                return f"{self.base}[{self.hi}:{self.lo}]"

            @property
            def width(self):
                return len(self.bits)

        class Concat(Expression):
            def __init__(
                self, left: "PureFormula.Expression", right: "PureFormula.Expression"
            ):
                self.left = left
                self.right = right
                self.bits = left.bits + right.bits

            def __str__(self):
                return f"({self.left} ++ {self.right})"

            @property
            def width(self):
                return len(self.bits)

        class Equality:
            def __init__(
                self, left: "PureFormula.Expression", right: "PureFormula.Expression"
            ):
                assert left.bits == right.bits, "Bitvector mismatch in equality"
                self.left = left
                self.right = right

            def __str__(self):
                return f"{self.left} == {self.right}"

    class Equality:
        def __init__(
            self, left: "PureFormula.Expression", right: "PureFormula.Expression"
        ) -> None:
            self.left: PureFormula.Expression = left
            self.right: PureFormula.Expression = right

    def __init__(self):
        self.equalities: [PureFormula.Equality] = []

    def substitute(self, formula: "PureFormula") -> None:
        pass

    def __str__(self):
        return " ∧ ".join(str(eq) for eq in self.equalities)


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

def transition_r():
    pass