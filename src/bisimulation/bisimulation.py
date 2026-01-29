"""
This module defines two functions for checking the bisimilarity of two P4 packet parsers.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from typing import Any

import pysmt.shortcuts as pysmt

from bisimulation.constraint import constraint_to_smt
from bisimulation.formula import (
    TRUE,
    And,
    Equals,
    FormulaManager,
    GuardedFormula,
    PureFormula,
)
from program.expression import Concatenate
from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


def _get_relevant_formulas(
        knowledge: set[GuardedFormula], guarded_form: GuardedFormula
) -> set[PureFormula]:
    """
    Get relevant pure formulas from knowledge for the given guarded formula.

    :param knowledge: a set of previously seen guarded formulas
    :param guarded_form: the guarded formula to check against
    :return: a set of relevant pure formulas
    """
    relevant_pfs = set()
    for seen_guarded_form in knowledge:
        if guarded_form.has_equal_guard(seen_guarded_form):
            relevant_pfs.add(seen_guarded_form.pf)
    return relevant_pfs


def _get_trace(
        solver: Any, relevant_pfs: set[PureFormula], guarded_form: GuardedFormula
) -> str:
    """
    Generate a trace of the guarded formula.

    :param solver: a solver (portfolio) instance to obtain a model from
    :param relevant_pfs: a set of relevant, previously seen pure formulas
    :param guarded_form: the guarded formula to generate a trace for
    :return: a string representation of the trace
    """
    trace = []
    current = guarded_form
    while current is not None:
        trace.append(current)
        current = current.prev_guarded_formula
    trace.reverse()

    lines = []
    buffer_vars = []
    for step, g_form in enumerate(trace):
        if g_form.pf.stream_var is not None:
            buffer_vars.append(g_form.pf.stream_var)

        lines.append(f"Step {step} (left, right):")
        lines.append("  At start:")
        lines.append(f"  - State:   {g_form.state_l}, {g_form.state_r}")
        lines.append(f"  - Buffer:  {g_form.buf_len_l}, {g_form.buf_len_r}")
        lines.append("  After operation(s):")
        buf_l = len(g_form.pf.buf_vars[True] or "")
        buf_r = len(g_form.pf.buf_vars[False] or "")
        lines.append(f"  - Buffer:  {buf_l}, {buf_r}")
        lines.append("")

    solver.is_sat(
        pysmt.Or(
            guarded_form.pf.to_smt(), pysmt.Or(*[pf.to_smt() for pf in relevant_pfs])
        )
    )
    model = solver.get_model()
    if model is not None:
        buffer_vars_smt = [var.to_smt(guarded_form.pf) for var in buffer_vars]

        if len(buffer_vars_smt) == 0:
            counterexample = "N/A (no buffered input)"
        elif len(buffer_vars_smt) == 1:
            val = model.get_value(buffer_vars_smt[0]).constant_value()
            length = len(buffer_vars[0]) if buffer_vars else 0
            counterexample = bin(val) + '\n' + f"Length: {length} bits"
        else:
            val = model.get_value(pysmt.BVConcat(*buffer_vars_smt)).constant_value()
            length = sum(len(var) for var in buffer_vars)
            counterexample = bin(val) + '\n' + f"Length: {length} bits"

        lines.insert(
            0, f"A stream for which both parsers differ is:\n{counterexample}\n"
        )

    return "\n".join(lines)


def _is_terminal(state_name: str) -> bool:
    """
    Check if a state is terminal.

    :param state_name: the state to check
    :return: True if the state is terminal, False otherwise
    """
    return state_name in ["accept", "reject"]


def _has_new_information(
        solver: Any, relevant_pfs: set[PureFormula], guarded_form: GuardedFormula
) -> bool:
    """
    Check if the guarded formula contains new information.

    :param solver: a solver instance to check satisfiability
    :param relevant_pfs: a set of relevant, previously seen pure formulas
    :param guarded_form: the guarded formula to check
    :return: True if the guarded formula contains new information, False otherwise
    """
    return not solver.is_valid(
        pysmt.Implies(
            guarded_form.pf.to_smt(), pysmt.Or(*[pf.to_smt() for pf in relevant_pfs])
        )
    )


def symbolic_bisimulation(
        parser1: ParserProgram,
        parser2: ParserProgram,
        solver_portfolio: Any,
        filter_accepting: Any = None,
        filter_disagreeing: Any = None,
        enable_leaps: bool = True,
) -> tuple[bool, str]:
    """
    Check whether two P4 packet parsers are bisimilar using symbolic execution.

    This algorithm checks for bisimilarity by representing the two parsers as
    modifiers of symbolic formulas. This approach is more efficient than the
    naive bisimulation, as it uses symbolic representations to explore the
    state space of the parsers. This implementation also allows for
    optimisations, such as leaps, to be performed.

    :param parser1: the first P4 parser program
    :param parser2: the second P4 parser program
    :param solver_portfolio: the solver portfolio to use for symbolic execution
    :param filter_accepting: an optional filter for accepting pairs
    :param filter_disagreeing: an optional filter for disagreeing pairs
    :param enable_leaps: whether to enable leaps in the bisimulation
    :return: a boolean indicating bisimilarity, and seen formulas or a counterexample
    """

    knowledge: set[GuardedFormula] = set()
    manager = FormulaManager()
    work_queue = [GuardedFormula.initial_guard()]
    for parser in [parser1, parser2]:
        left = parser.is_left
        for field in parser.get_all_fields():
            field_size = parser.get_header(field)
            var = manager.fresh_variable(field_size)
            work_queue[0].pf.set_header_field_var(field, left, var)
    with solver_portfolio as s:
        while len(work_queue) > 0:
            guarded_form = work_queue.pop(0)
            current_pf = guarded_form.pf
            relevant_pfs = _get_relevant_formulas(knowledge, guarded_form)

            if not _has_new_information(s, relevant_pfs, guarded_form):
                logger.debug(
                    f"Considered guarded formula information known: {guarded_form}"
                )
                continue

            state_l = guarded_form.state_l
            state_r = guarded_form.state_r
            if (state_l == "accept") != (state_r == "accept"):
                if filter_disagreeing is None:
                    return False, _get_trace(s, relevant_pfs, guarded_form)

                constraint_smt = constraint_to_smt(filter_disagreeing, current_pf)
                if not s.is_sat(constraint_smt):
                    return False, _get_trace(s, relevant_pfs, guarded_form)
                else:
                    knowledge.add(guarded_form)
                    continue

            if state_l == "accept" and state_r == "accept" and filter_accepting is not None:
                relation_smt = constraint_to_smt(filter_accepting, current_pf)
                if not s.is_sat(relation_smt):
                    return False, _get_trace(s, relevant_pfs, guarded_form)

            if _is_terminal(state_l) and _is_terminal(state_r):
                logger.debug("Both states are terminal, skipping further processing")
                knowledge.add(guarded_form)
                continue

            terminal_l = _is_terminal(state_l)
            terminal_r = _is_terminal(state_r)

            if not terminal_l:
                buf_len_l = guarded_form.buf_len_l
                op_block_l = parser1.states[state_l].operation_block
                trans_block_l = parser1.states[state_l].transition_block
                op_size_l = op_block_l.size

            if not terminal_r:
                buf_len_r = guarded_form.buf_len_r
                op_block_r = parser2.states[state_r].operation_block
                trans_block_r = parser2.states[state_r].transition_block
                op_size_r = op_block_r.size

            if enable_leaps:
                if not terminal_l and not terminal_r:
                    leap = min(op_size_l - buf_len_l, op_size_r - buf_len_r)
                elif not terminal_l:
                    leap = op_size_l - buf_len_l
                elif not terminal_r:
                    leap = op_size_r - buf_len_r
            else:
                leap = 1

            new_bits_var = manager.fresh_variable(leap)
            new_pf = current_pf.deepcopy()

            def extend_buffer(parser: ParserProgram, *, left: bool) -> None:
                """
                Extend the buffer variable in the current pure formula.

                :param parser: the parser program to use for the extension
                :param left: whether to extend the left or right buffer
                """
                nonlocal terminal_l
                if left and terminal_l:
                    return
                nonlocal terminal_r
                if not left and terminal_r:
                    return
                nonlocal new_pf
                old_buf = current_pf.get_buffer_var(left=left)
                if old_buf is None:
                    new_pf.set_buffer_var(left=left, var=new_bits_var)
                else:
                    new_buf = manager.fresh_variable(len(old_buf) + leap)
                    new_pf.set_buffer_var(left=left, var=new_buf)
                    new_pf.root = And(
                        new_pf.root,
                        Equals(
                            new_buf,
                            Concatenate(parser, left=old_buf, right=new_bits_var),
                        ),
                    )

            extend_buffer(parser1, left=parser1.is_left)
            extend_buffer(parser2, left=parser2.is_left)

            transition_l = not terminal_l and (buf_len_l + leap == op_size_l)
            transition_r = not terminal_r and (buf_len_r + leap == op_size_r)
            logger.info(
                f"Equivalence checking loop status\n"
                f"Left - state: {state_l}, op. size: {op_size_l}, transitioning: {transition_l}\n"
                f"Right - state: {state_r}, op. size: {op_size_r}, transitioning: {transition_r}\n"
            )
            logger.debug(f"Buffers: {new_pf.buf_vars}")

            if transition_l:
                new_pf = op_block_l.strongest_postcondition(manager, new_pf)
            if transition_r:
                new_pf = op_block_r.strongest_postcondition(manager, new_pf)

            true_form = TRUE()
            left_trans = (
                trans_block_l.symbolic_transition(new_pf)
                if transition_l
                else [(true_form, "reject" if terminal_l else state_l)]
            )
            right_trans = (
                trans_block_r.symbolic_transition(new_pf)
                if transition_r
                else [(true_form, "reject" if terminal_r else state_r)]
            )

            for form_l, to_l in left_trans:
                for form_r, to_r in right_trans:
                    copy_pf = PureFormula.clone(
                        And(new_pf.root, And(form_l, form_r)),
                        new_pf.header_field_vars,
                        new_pf.buf_vars,
                        new_bits_var,
                    )
                    work_queue.append(
                        GuardedFormula(
                            to_l,
                            to_r,
                            0 if transition_l else buf_len_l + leap,
                            0 if transition_r else buf_len_r + leap,
                            copy_pf,
                            guarded_form,
                        )
                    )

            knowledge.add(guarded_form)

    return True, "\n".join(str(f) for f in knowledge)
