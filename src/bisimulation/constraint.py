"""
This module defines constraint_to_smt(), a function that converts a Python AST
representation of relational constraints into SMT formulas, handling uninitialised
variables according to specified semantics.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import ast
from typing import Any

import pysmt.shortcuts as pysmt

from bisimulation.formula import PureFormula


def constraint_to_smt(constraint: Any, pf: PureFormula) -> Any:
    """
    Convert a relational constraint into an SMT formula.

    :param constraint: a string representing a Python expression for the constraint
    :param pf: a PureFormula object representing the current state of variables
    :return: an SMT formula representing the constraint combined with the PureFormula

    Semantics:
    - If both sides of a relation are uninitialised, the constraint is dropped.
    - If exactly one side is uninitialised, the constraint is violated.
    - If both sides are initialised, the constraint is enforced.
    """

    class UnsafeExpression(ValueError):
        """Raised when an unsafe expression is encountered."""
        pass

    UNINIT = object()

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, (ast.Attribute, ast.Name)):
            def _get_hdr_str(n):
                if isinstance(n, ast.Name):
                    return n.id
                if isinstance(n, ast.Attribute):
                    return _get_hdr_str(n.value) + '.' + n.attr
                return None

            header = _get_hdr_str(node)
            left = header[4] == "l"
            header = "hdr" + header[5:]

            var = pf.get_header_field_var(header, left=left)
            if var is None:
                return UNINIT
            return var.to_smt(pf)

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            l = _eval(node.left)
            r = _eval(node.right)

            if l is UNINIT and r is UNINIT:
                return UNINIT
            if l is UNINIT or r is UNINIT:
                return pysmt.FALSE()

            return pysmt.BVConcat(l, r)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return pysmt.TRUE() if node.value else pysmt.FALSE()

            if not isinstance(node.value, str) or '_' not in node.value:
                raise UnsafeExpression("Constants must be of the form <value>_<bitwidth>")

            val, bw = node.value.split('_', 1)
            bitwidth = int(bw)

            if val.startswith(('0x', '0X')):
                value = int(val, 16)
            elif val.startswith(('0b', '0B')):
                value = int(val, 2)
            else:
                value = int(val)

            return pysmt.BV(value, bitwidth)

        if isinstance(node, ast.BoolOp):
            smts = [_eval(v) for v in node.values]
            smts = [s for s in smts if s is not UNINIT]
            if not smts:
                return UNINIT

            if isinstance(node.op, ast.And):
                return pysmt.And(smts)

            if isinstance(node.op, ast.Or):
                return pysmt.Or(smts)

            raise UnsafeExpression("Unsupported boolean operator")

        if isinstance(node, ast.Compare):
            l = _eval(node.left)
            r = _eval(node.comparators[0])

            if l is UNINIT and r is UNINIT:
                return UNINIT
            if l is UNINIT or r is UNINIT:
                return pysmt.FALSE()

            if isinstance(node.ops[0], ast.Eq):
                return pysmt.Equals(l, r)
            if isinstance(node.ops[0], ast.NotEq):
                return pysmt.Not(pysmt.Equals(l, r))

            raise UnsafeExpression("Unsupported comparison")

        if isinstance(node, ast.Subscript):
            base = _eval(node.value)
            if base is UNINIT:
                return UNINIT

            if not isinstance(node.slice, ast.Slice):
                raise UnsafeExpression("Only slicing is allowed")

            # In Python AST, lower and upper are reversed for slicing
            lo = node.slice.upper
            hi = node.slice.lower
            if not (isinstance(lo, ast.Constant) and isinstance(hi, ast.Constant)):
                raise UnsafeExpression("Slice bounds must be constants")

            low = lo.value
            high = hi.value
            return pysmt.BVExtract(base, low, high)

        raise UnsafeExpression(f"Unsupported syntax: {type(node).__name__}")

    if constraint:
        expr = _eval(ast.parse(constraint, mode="eval").body)
    else:
        expr = UNINIT

    if expr is UNINIT:
        return pf.to_smt()
    return pysmt.And(expr, pf.to_smt())
