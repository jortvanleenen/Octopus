"""
This module defines two functions for checking the bisimilarity of two P4 packet parsers.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from collections import deque
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
        lines.append(f"  - State:   {g_form.state_l}, {g_form.state_r}")
        lines.append(f"  - Buffer:  {g_form.buf_len_l}, {g_form.buf_len_r}")
        lines.append("")

    solver.is_sat(
        pysmt.Or(
            guarded_form.pf.to_smt(), pysmt.Or(*[pf.to_smt() for pf in relevant_pfs])
        )
    )
    model = solver.get_model()
    if model is not None:
        buffer_vars_smt = [v.to_smt() for v in buffer_vars]

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
        solver: Any, relevant_pfs: set[PureFormula], guarded_form: GuardedFormula, manager: FormulaManager
) -> bool:
    """
    Check if the guarded formula contains new information.

    :param solver: a solver instance to check satisfiability
    :param relevant_pfs: a set of relevant, previously seen pure formulas
    :param guarded_form: the guarded formula to check
    :return: True if the guarded formula contains new information, False otherwise
    """
    lhs = pysmt.Exists(
        [v.to_smt() for v in guarded_form.pf.exists_vars()],
        guarded_form.pf.to_smt(),
    )
    rhs = pysmt.Or(*[
        pysmt.Exists(
            [v.to_smt() for v in pf.exists_vars()],
            pf.to_smt(),
        )
        for pf in relevant_pfs
    ])
    return not solver.is_valid(pysmt.Implies(lhs, rhs))


def check_certificate(
        knowledge: set[GuardedFormula],
        parser1: ParserProgram,
        parser2: ParserProgram,
        solver: Any,
        filter_accepting: Any = None,
        filter_disagreeing: Any = None,
) -> tuple[bool, str]:
    """
    Validate a bisimulation certificate produced by symbolic_bisimulation().

    :param knowledge: the set of TGFs forming the certificate
    :param parser1: the first P4 parser program
    :param parser2: the second P4 parser program
    :param solver: an open solver instance to use for SMT queries
    :param filter_accepting: an optional filter for accepting pairs
    :param filter_disagreeing: an optional filter for disagreeing pairs
    :return: a tuple (valid, message) where valid is True iff the certificate
             is a valid bisimulation witness, and message describes the outcome
             or the violation found
    """
    # Check 1: the certificate contains the TGF for the initial states of both parsers
    initial_guard = GuardedFormula.initial_guard()
    if not any(initial_guard.has_equal_guard(gf) and gf.prev_guarded_formula is None for gf in knowledge):
        return False, (
            "Certificate is invalid: no TGF found for the initial configuration "
            "(state_l='start', state_r='start', buf_len_l=0, buf_len_r=0)."
        )

    manager = FormulaManager(count_up=False)

    for guarded_form in knowledge:
        current_pf = guarded_form.pf
        state_l = guarded_form.state_l
        state_r = guarded_form.state_r

        # Check 3: acceptance consistency
        if (state_l == "accept") != (state_r == "accept"):
            if filter_disagreeing is None:
                relevant_pfs = _get_relevant_formulas(knowledge, guarded_form)
                return False, (
                        "Certificate is invalid: TGF has inconsistent acceptance.\n"
                        + _get_trace(solver, relevant_pfs, guarded_form)
                )

            constraint_smt = constraint_to_smt(filter_disagreeing, current_pf)
            if not solver.is_valid(constraint_smt):
                relevant_pfs = _get_relevant_formulas(knowledge, guarded_form)
                return False, (
                        "Certificate is invalid: TGF violates the disagreement filter.\n"
                        + _get_trace(solver, relevant_pfs, guarded_form)
                )
            continue

        if state_l == "accept" and state_r == "accept" and filter_accepting is not None:
            relation_smt = constraint_to_smt(filter_accepting, current_pf)
            if not solver.is_valid(relation_smt):
                relevant_pfs = _get_relevant_formulas(knowledge, guarded_form)
                return False, (
                        "Certificate is invalid: TGF violates the acceptance filter.\n"
                        + _get_trace(solver, relevant_pfs, guarded_form)
                )

        terminal_l = _is_terminal(state_l)
        terminal_r = _is_terminal(state_r)

        if terminal_l and terminal_r:
            continue

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

        if not terminal_l and not terminal_r:
            leap = min(op_size_l - buf_len_l, op_size_r - buf_len_r)
        elif not terminal_l:
            leap = op_size_l - buf_len_l
        else:
            leap = op_size_r - buf_len_r

        new_bits_var = manager.fresh_variable(leap)
        new_pf = current_pf.deepcopy()
        new_pf.add_used_vars({new_bits_var})

        def extend_buffer(
                parser: ParserProgram, buf_size: int, leap_size: int, pf: PureFormula
        ) -> None:
            """
            Extend the buffer variable in the current pure formula.

            :param parser: the parser program to use for the extension
            :param buf_size: the size of the buffer
            :param leap_size: the number of bits to add to the buffer
            :param pf: the pure formula to capture the extension in buffer size
            """
            if buf_size == 0:
                new_buf_var = parser.get_buffer_var(leap_size)
                pf.root = And(
                    pf.root,
                    Equals(
                        new_buf_var,
                        new_bits_var,
                    ),
                )
            else:
                buf_var = parser.get_buffer_var(buf_size)
                fresh_var = manager.fresh_variable(buf_size)
                pf.substitute({buf_var: fresh_var})

                new_buf_var = parser.get_buffer_var(buf_size + leap_size)
                pf.root = And(
                    pf.root,
                    Equals(
                        new_buf_var,
                        Concatenate(parser, left=fresh_var, right=new_bits_var),
                    ),
                )

        if not terminal_l:
            extend_buffer(parser1, buf_len_l, leap, new_pf)
        if not terminal_r:
            extend_buffer(parser2, buf_len_r, leap, new_pf)

        transition_l = not terminal_l and (buf_len_l + leap == op_size_l)
        transition_r = not terminal_r and (buf_len_r + leap == op_size_r)

        if transition_l:
            new_pf, _ = op_block_l.strongest_postcondition(manager, new_pf, buf_len_l + leap)
        if transition_r:
            new_pf, _ = op_block_r.strongest_postcondition(manager, new_pf, buf_len_r + leap)

        true_form = TRUE()

        if terminal_l:
            left_trans = []
        elif transition_l:
            left_trans = trans_block_l.symbolic_transition()
        else:
            left_trans = [(true_form, state_l)]

        if terminal_r:
            right_trans = []
        elif transition_r:
            right_trans = trans_block_r.symbolic_transition()
        else:
            right_trans = [(true_form, state_r)]

        # Check 2: every successor must be covered by the certificate
        for form_l, to_l in left_trans:
            for form_r, to_r in right_trans:
                successor_pf = PureFormula.clone(
                    And(new_pf.root, And(form_l, form_r)),
                    new_pf.used_vars | form_l.used_vars() | form_r.used_vars(),
                    new_pf.stream_var,
                )
                successor_buf_len_l = 0 if transition_l else buf_len_l + leap
                successor_buf_len_r = 0 if transition_r else buf_len_r + leap
                successor = GuardedFormula(
                    to_l, to_r,
                    successor_buf_len_l, successor_buf_len_r,
                    successor_pf, guarded_form,
                )
                relevant_pfs = _get_relevant_formulas(knowledge, successor)
                if _has_new_information(solver, relevant_pfs, successor, manager):
                    return False, (
                            f"Certificate is invalid: successor "
                            f"(state_l={to_l!r}, state_r={to_r!r}, "
                            f"buf_len_l={successor_buf_len_l}, "
                            f"buf_len_r={successor_buf_len_r}) "
                            f"is not covered by the certificate.\n"
                            + _get_trace(solver, relevant_pfs, successor)
                    )

    return True, (
        f"Certificate is valid: all {len(knowledge)} TGF(s) checked successfully."
    )


def symbolic_bisimulation(
        parser1: ParserProgram,
        parser2: ParserProgram,
        solver_portfolio: Any,
        filter_accepting: Any = None,
        filter_disagreeing: Any = None,
        enable_leaps: bool = True,
        validate_certificate: bool = False,
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
    :param validate_certificate: if True, validate the generated certificate via
           check_certificate() before returning; raises AssertionError if the
           certificate produced by this function is found to be invalid
    :return: a boolean indicating bisimilarity, and seen formulas or a counterexample
    """
    manager = FormulaManager()
    knowledge: set[GuardedFormula] = set()
    work_queue = deque([GuardedFormula.initial_guard()])
    with solver_portfolio as s:
        while len(work_queue) > 0:
            guarded_form = work_queue.popleft()
            current_pf = guarded_form.pf
            relevant_pfs = _get_relevant_formulas(knowledge, guarded_form)

            if not _has_new_information(s, relevant_pfs, guarded_form, manager):
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
                if not s.is_valid(constraint_smt):
                    return False, _get_trace(s, relevant_pfs, guarded_form)
                else:
                    knowledge.add(guarded_form)
                    continue

            if state_l == "accept" and state_r == "accept" and filter_accepting is not None:
                relation_smt = constraint_to_smt(filter_accepting, current_pf)
                if not s.is_valid(relation_smt):
                    return False, _get_trace(s, relevant_pfs, guarded_form)

            terminal_l = _is_terminal(state_l)
            terminal_r = _is_terminal(state_r)

            if terminal_l and terminal_r:
                logger.debug("Both states are terminal, skipping further processing")
                knowledge.add(guarded_form)
                continue

            if not terminal_l:
                buf_len_l = guarded_form.buf_len_l
                op_block_l = parser1.states[state_l].operation_block
                op_size_l = op_block_l.size
                trans_block_l = parser1.states[state_l].transition_block

            if not terminal_r:
                buf_len_r = guarded_form.buf_len_r
                op_block_r = parser2.states[state_r].operation_block
                op_size_r = op_block_r.size
                trans_block_r = parser2.states[state_r].transition_block

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
            new_pf.add_used_vars({new_bits_var})

            def extend_buffer(
                    parser: ParserProgram, buf_size: int, leap_size: int, pf: PureFormula
            ) -> None:
                """
                Extend the buffer variable in the current pure formula.

                :param parser: the parser program to use for the extension
                :param buf_size: the size of the buffer
                :param leap_size: the number of bits to add to the buffer
                :param pf: the pure formula to capture the extension in buffer size
                """
                if buf_size == 0:
                    new_buf_var = parser.get_buffer_var(leap_size)
                    pf.root = And(
                        pf.root,
                        Equals(
                            new_buf_var,
                            new_bits_var,
                        ),
                    )
                else:
                    buf_var = parser.get_buffer_var(buf_size)
                    fresh_var = manager.fresh_variable(buf_size)
                    pf.substitute({buf_var: fresh_var})

                    new_buf_var = parser.get_buffer_var(buf_size + leap_size)
                    pf.root = And(
                        pf.root,
                        Equals(
                            new_buf_var,
                            Concatenate(parser, left=fresh_var, right=new_bits_var),
                        ),
                    )

            if not terminal_l:
                extend_buffer(parser1, buf_len_l, leap, new_pf)
            if not terminal_r:
                extend_buffer(parser2, buf_len_r, leap, new_pf)

            transition_l = not terminal_l and (buf_len_l + leap == op_size_l)
            transition_r = not terminal_r and (buf_len_r + leap == op_size_r)
            logger.info(
                f"Equivalence checking loop status\n"
                f"Left - state: {state_l}, op. size: {op_size_l}, transitioning: {transition_l}\n"
                f"Right - state: {state_r}, op. size: {op_size_r}, transitioning: {transition_r}\n"
                f"Leap size: {leap}\n"
            )

            if transition_l:
                new_pf, _ = op_block_l.strongest_postcondition(manager, new_pf, buf_len_l + leap)
            if transition_r:
                new_pf, _ = op_block_r.strongest_postcondition(manager, new_pf, buf_len_r + leap)

            true_form = TRUE()

            if terminal_l:
                left_trans = []
            elif transition_l:
                left_trans = trans_block_l.symbolic_transition()
            else:
                left_trans = [(true_form, state_l)]

            if terminal_r:
                right_trans = []
            elif transition_r:
                right_trans = trans_block_r.symbolic_transition()
            else:
                right_trans = [(true_form, state_r)]

            for form_l, to_l in left_trans:
                for form_r, to_r in right_trans:
                    copy_pf = PureFormula.clone(
                        And(new_pf.root, And(form_l, form_r)),
                        new_pf.used_vars | form_l.used_vars() | form_r.used_vars(),
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

        if validate_certificate:
            valid, message = check_certificate(
                knowledge, parser1, parser2, s,
                filter_accepting, filter_disagreeing,
            )
            assert valid, f"Certificate self-check failed: {message}"

    return True, "\n".join(str(f) for f in knowledge)
