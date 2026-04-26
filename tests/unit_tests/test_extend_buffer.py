import pytest
import pysmt.shortcuts as pysmt

from bisimulation.formula import (
    TRUE,
    And,
    Equals,
    FormulaManager,
    PureFormula,
)
from bisimulation.bisimulation import extend_buffer
from program.expression import Concatenate
from program.parser_program import ParserProgram


class DummyParser(ParserProgram):
    def __init__(self, is_left=True):
        super().__init__(json=None, is_left=is_left)


@pytest.fixture
def manager():
    return FormulaManager()


@pytest.fixture
def parser():
    return DummyParser(is_left=True)


@pytest.fixture
def solver():
    s = pysmt.Solver(name="z3")
    yield s
    s.exit()


def collect_equals(node):
    """Collect all Equals nodes from an And-tree."""
    result = []
    if isinstance(node, Equals):
        result.append(node)
    elif isinstance(node, And):
        result.extend(collect_equals(node.left))
        result.extend(collect_equals(node.right))
    return result


def test_extend_buffer_empty_buffer(manager, parser):
    pf = PureFormula(TRUE(), set(), None)

    new_bits = manager.fresh_variable(8)
    pf.add_used_vars({new_bits})

    extend_buffer(parser, 0, pf, manager, new_bits)

    eqs = collect_equals(pf.root)
    assert len(eqs) == 1

    eq = eqs[0]
    assert eq.right == new_bits
    assert len(eq.left) == 8


def test_extend_buffer_non_empty_buffer(manager, parser):
    pf = PureFormula(TRUE(), set(), None)

    old_buf = parser.get_buffer_var(4)
    pf.add_used_vars({old_buf})

    new_bits = manager.fresh_variable(4)
    pf.add_used_vars({new_bits})

    extend_buffer(parser, 4, pf, manager, new_bits)

    eqs = collect_equals(pf.root)
    assert len(eqs) == 1

    eq = eqs[0]
    assert isinstance(eq.right, Concatenate)

    concat = eq.right
    assert concat.right == new_bits
    assert len(eq.left) == 8


def test_extend_buffer_substitution_occurs(manager, parser):
    pf = PureFormula(TRUE(), set(), None)

    old_buf = parser.get_buffer_var(4)
    pf.add_used_vars({old_buf})

    new_bits = manager.fresh_variable(4)
    pf.add_used_vars({new_bits})

    extend_buffer(parser, 4, pf, manager, new_bits)

    assert old_buf not in pf.used_vars


def test_extend_buffer_fresh_variable_introduced(manager, parser):
    pf = PureFormula(TRUE(), set(), None)

    old_buf = parser.get_buffer_var(4)
    pf.add_used_vars({old_buf})

    new_bits = manager.fresh_variable(4)
    pf.add_used_vars({new_bits})

    extend_buffer(parser, 4, pf, manager, new_bits)

    eqs = collect_equals(pf.root)
    assert len(eqs) == 1

    concat = eqs[0].right
    assert isinstance(concat, Concatenate)

    assert concat.left != old_buf


def test_extend_buffer_smt_satisfiable(manager, parser, solver):
    pf = PureFormula(TRUE(), set(), None)

    new_bits = manager.fresh_variable(4)
    pf.add_used_vars({new_bits})

    extend_buffer(parser, 0, pf, manager, new_bits)

    solver.add_assertion(pf.to_smt())
    assert solver.solve()


def test_extend_buffer_multiple_extensions(manager, parser):
    pf = PureFormula(TRUE(), set(), None)

    new_bits1 = manager.fresh_variable(4)
    pf.add_used_vars({new_bits1})
    extend_buffer(parser, 0, pf, manager, new_bits1)

    new_bits2 = manager.fresh_variable(4)
    pf.add_used_vars({new_bits2})
    extend_buffer(parser, 4, pf, manager, new_bits2)

    eqs = collect_equals(pf.root)

    assert len(eqs) >= 1

    assert any(len(eq.left) == 8 for eq in eqs)
