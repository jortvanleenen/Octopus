class PureFormula:
    class Expression:
        def __str__(self) -> str:
            raise NotImplementedError

        @property
        def width(self) -> int:
            raise NotImplementedError

    class Variable(Expression):
        def __init__(self, name: str, bits: str):
            self.name = name
            self.bits = bits

        def __str__(self):
            return f"{self.name}({self.bits})"

        @property
        def width(self) -> int:
            return len(self.bits)

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
        def __init__(self, base: "PureFormula.Expression", msb: int, lsb: int):
            assert msb >= 0 and lsb >= 0, "Slice indices must be non-negative"
            assert msb >= lsb, "Invalid slice range: msb must be ≥ lsb"
            assert msb < base.width and lsb < base.width, "Slice indices out of bounds"

            self.base = base
            self.hi = msb
            self.lo = lsb
            self.bits = base.bits[msb:lsb]

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

    def __init__(self):
        self.equalities: list[PureFormula.Equality] = []
        self.used_variable_names: set[str] = set()
        self.next_free_variable_index: int = 0

    def new_variable(self, bits: str) -> "PureFormula.Variable":
        """Generate a fresh variable with a unique name and the given bitstring."""
        while True:
            name = str(self.next_free_variable_index)
            self.next_free_variable_index += 1
            if name not in self.used_variable_names:
                self.used_variable_names.add(name)
                return PureFormula.Variable(name, bits)

    def substitute(self, mapping: dict[str, "PureFormula.Expression"]) -> None:
        """Substitute variable names using a name → expression mapping."""
        new_equalities = []
        for eq in self.equalities:
            left = self._substitute_expr(eq.left, mapping)
            right = self._substitute_expr(eq.right, mapping)
            new_equalities.append(PureFormula.Equality(left, right))
        self.equalities = new_equalities

    def _substitute_expr(
        self,
        expr: "PureFormula.Expression",
        mapping: dict[str, "PureFormula.Expression"],
    ) -> "PureFormula.Expression":
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
            return expr  # Other expressions are considered constant

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
