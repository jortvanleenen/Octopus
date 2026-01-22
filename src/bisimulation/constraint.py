import ast
from typing import Any

import pysmt.shortcuts as pysmt

from bisimulation.formula import PureFormula


def constraint_to_smt(constraint: Any, pf: PureFormula) -> Any:
    """
    Take a constraint string and convert it to an SMT formula.

    For example, "('hdr.f0' + 'hdr.f1') == 'hdr.f'" is interpreted as requiring
    the concatenation of two fields in the left parser (left side of equality)
    to be equal to a field in the right parser (right side of equality).
    """

    class UnsafeExpression(ValueError):
        """
        Exception raised for unsafe expressions in the constraint.
        """

        pass

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, ast.Attribute) or isinstance(node, ast.Name):
            def _parse_hdr_field(node):
                def _get_hdr_str(node):
                    if isinstance(node, ast.Name):
                        return node.id
                    if isinstance(node, ast.Attribute):
                        return node.attr + '.' + _get_hdr_str(node.value)

                header = _get_hdr_str(node)
                return header[::-1], header[4] == "l"

            header, left = _parse_hdr_field(node)

            var = pf.get_header_field_var(header, left=left)
            if var is None:
                return None
            return var.to_smt(pf)

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left_smt = _eval(node.left)
            right_smt = _eval(node.right)

            if (left_smt is None) != (right_smt is None):
                return pysmt.FALSE()

            if left_smt is None:
                return None

            return pysmt.BVConcat(left_smt, right_smt)

        if isinstance(node, ast.Constant):
            # format: <value>_bitwidth, e.g. 0x4503_16
            if isinstance(node.value, str):
                if '_' not in node.value:
                    raise UnsafeExpression(
                        "Constants must specify bitwidth using '_'"
                    )
                value_str, bitwidth_str = node.value.split('_', 1)
                try:
                    bitwidth = int(bitwidth_str)
                except ValueError:
                    raise UnsafeExpression(
                        f"Invalid bitwidth in constant: {bitwidth_str}"
                    )
                try:
                    if value_str.startswith('0x') or value_str.startswith('0X'):
                        value = int(value_str, 16)
                    elif value_str.startswith('0b') or value_str.startswith('0B'):
                        value = int(value_str, 2)
                    else:
                        value = int(value_str)
                except ValueError:
                    raise UnsafeExpression(
                        f"Invalid value in constant: {value_str}"
                    )
                return pysmt.BV(value, bitwidth)
            else:
                raise UnsafeExpression(f"Disallowed constant type: {type(node.value)}")

        if isinstance(node, ast.BoolOp):
            if len(node.values) != 2:
                raise UnsafeExpression("Only binary boolean operations are allowed.")

            left_smt = _eval(node.values[0])
            right_smt = _eval(node.values[1])

            if (left_smt is None) != (right_smt is None):
                return pysmt.FALSE()

            if left_smt is None:
                return None

            operator = node.op
            match operator:
                case ast.Or():
                    return pysmt.Or(left_smt, right_smt)
                case ast.And():
                    return pysmt.And(left_smt, right_smt)
                case _:
                    raise UnsafeExpression(
                        f"Disallowed boolean operator: {operator.__class__.__name__}"
                    )

        if isinstance(node, ast.Compare):
            if (
                    len(node.ops) != 1
                    or len(node.comparators) != 1
            ):
                raise UnsafeExpression("Only simple (two element) comparisons are allowed.")

            left_smt = _eval(node.left)
            right_smt = _eval(node.comparators[0])

            if (left_smt is None) != (right_smt is None):
                return pysmt.FALSE()

            if left_smt is None:
                return pysmt.TRUE()

            operator = node.ops[0]
            match operator:
                case ast.Eq():
                    return pysmt.Equals(left_smt, right_smt)
                case ast.NotEq():
                    return pysmt.Not(pysmt.Equals(left_smt, right_smt))
                case _:
                    raise UnsafeExpression(
                        f"Disallowed comparison operator: {operator.__class__.__name__}"
                    )

        if isinstance(node, ast.Subscript):
            base = _eval(node.value)
            if base is None:
                return None

            if not isinstance(node.slice, ast.Slice):
                raise UnsafeExpression("Only slicing is allowed")

            lower = node.slice.lower
            upper = node.slice.upper

            if lower is None or upper is None:
                raise UnsafeExpression("Slice must specify both bounds")

            if not (isinstance(lower, ast.Constant) and isinstance(upper, ast.Constant)):
                raise UnsafeExpression("Slice bounds must be constants")

            high = lower.value
            low = upper.value

            if not (isinstance(high, int) and isinstance(low, int)):
                raise UnsafeExpression("Slice bounds must be integers")

            if low > high:
                raise UnsafeExpression("Invalid slice: low > high")

            return pysmt.BVExtract(base, low, high)

        raise UnsafeExpression(f"Disallowed syntax: {node.__class__.__name__}")

    return pysmt.And(
        _eval(ast.parse(constraint, mode="eval").body),
        pf.to_smt()
    )
