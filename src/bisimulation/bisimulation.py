"""
This module defines two functions for checking the bisimilarity of two P4 packet parsers.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
from typing import Any

import pysmt.shortcuts as pysmt

from automata.dfa import DFA
from bisimulation.symbolic.formula import (
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


def naive_bisimulation(
    parser1: ParserProgram, parser2: ParserProgram
) -> tuple[bool, set[tuple[DFA.Configuration, DFA.Configuration]]]:
    """
    Check whether two P4 packet parsers are bisimilar.

    This algorithm checks for bisimilarity by representing the two parsers as
    DFAs. This approach is considered naive due to the accompanying state
    explosion, as no symbolic representation is used. Additionally, no
    optimisations, such as leaps, are performed.

    The bisimulation is performed in a forward manner.

    :param parser1: the first P4 parser program
    :param parser2: the second P4 parser program
    :return: a boolean indicating bisimilarity, and seen configurations or a counterexample
    """

    dfa1 = DFA(parser1)
    dfa2 = DFA(parser2)
    config1 = DFA.initial_config()
    config2 = DFA.initial_config()

    seen = set()
    work_queue = [(config1, config2)]
    while len(work_queue) > 0:
        config1, config2 = work_queue.pop(0)

        if (config1, config2) in seen:
            continue

        if config1.is_accepting() == config2.is_accepting():
            seen.add((config1, config2))
            for bit in ["0", "1"]:
                next_config1 = dfa1.step(config1, bit)
                next_config2 = dfa2.step(config2, bit)
                work_queue.append((next_config1, next_config2))
        else:
            return False, {
                (config1, config2),
            }

    return True, seen


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


def get_trace(
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
    buf_vars_left = []
    buf_vars_right = []
    for step, g_form in enumerate(trace):
        buf_var_left = g_form.pf.get_buffer_var(left=True)
        if buf_var_left is not None and (
            len(buf_vars_left) < 1 or buf_vars_left[-1] != buf_var_left
        ):
            buf_vars_left.append(buf_var_left.to_smt(g_form.pf))
        buf_var_right = g_form.pf.get_buffer_var(left=False)
        if buf_var_right is not None and (
            len(buf_vars_right) < 1 or buf_vars_right[-1] != buf_var_right
        ):
            buf_vars_right.append(buf_var_right.to_smt(g_form.pf))

        lines.append(f"Step {step} (left, right):")
        lines.append("  At start:")
        lines.append(f"  - State:   {g_form.state_l}, {g_form.state_r}")
        lines.append(f"  - Buffer:  {g_form.buf_len_l}, {g_form.buf_len_r}")
        lines.append("  After operation(s):")

        buf_l = len(g_form.pf.buf_vars[True] or "")
        buf_r = len(g_form.pf.buf_vars[False] or "")
        lines.append(f"  - Buffer:  {buf_l}, {buf_r}")

        left_fields = [
            name for name, left in g_form.pf.header_field_vars.keys() if left
        ]
        right_fields = [
            name for name, left in g_form.pf.header_field_vars.keys() if not left
        ]
        lines.append("  - Store:")
        lines.append(f"    - Left:  {left_fields}")
        lines.append(f"    - Right: {right_fields}")
        lines.append("")

    solver.is_sat(
        pysmt.Or(
            guarded_form.pf.to_smt(), pysmt.Or(*[pf.to_smt() for pf in relevant_pfs])
        )
    )
    model = solver.get_model()
    if model is not None:
        left_ex = ""
        right_ex = ""
        if len(buf_vars_left) > 0:
            left_ex = bin(model.get_value(pysmt.And(*buf_vars_left)).constant_value())
        if len(buf_vars_right) > 0:
            right_ex = bin(model.get_value(pysmt.And(*buf_vars_right)).constant_value())
        if len(left_ex) > len(right_ex):
            counterexample = left_ex
        else:
            counterexample = right_ex
        if len(buf_vars_left) == 0 and len(buf_vars_right) == 0:
            counterexample = "N/A (no buffer variables were used)"

        lines.insert(
            0, f"A stream for which both parsers differ is:\n{counterexample}\n"
        )

    return "\n".join(lines)


def is_terminal(state_name: str) -> bool:
    """
    Check if a state is terminal.

    :param state_name: the state to check
    :return: True if the state is terminal, False otherwise
    """
    return state_name in ["accept", "reject"]


def has_new_information(
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
    enable_leaps: bool,
    solver_portfolio: Any,
) -> tuple[bool, str]:
    """
    Check whether two P4 packet parsers are bisimilar using symbolic execution.

    This algorithm checks for bisimilarity by representing the two parsers as
    modifiers of symbolic formulas. This approach is considered more efficient
    than the naive bisimulation, as it uses symbolic representations to explore
    the state space of the parsers. This implementation also allows for
    optimisations, such as leaps, to be performed.

    :param parser1: the first P4 parser program
    :param parser2: the second P4 parser program
    :param enable_leaps: whether to enable leaps in the bisimulation
    :param solver_portfolio: the solver portfolio to use for symbolic execution
    :return: a boolean indicating bisimilarity, and seen formulas or a counterexample
    """

    knowledge: set[GuardedFormula] = set()
    manager = FormulaManager()
    work_queue = [GuardedFormula.initial_guard()]
    with solver_portfolio as s:
        while len(work_queue) > 0:
            guarded_form = work_queue.pop(0)
            current_pf = guarded_form.pf
            relevant_pfs = _get_relevant_formulas(knowledge, guarded_form)

            if not has_new_information(s, relevant_pfs, guarded_form):
                logger.debug(
                    f"Considered guarded formula information known: {guarded_form}"
                )
                continue

            state_l = guarded_form.state_l
            state_r = guarded_form.state_r
            if (state_l == "accept") != (state_r == "accept"):
                return False, get_trace(s, relevant_pfs, guarded_form)

            if is_terminal(state_l) and is_terminal(state_r):
                logger.debug("Both states are terminal, skipping further processing")
                knowledge.add(guarded_form)
                continue

            buf_len_l = guarded_form.buf_len_l
            buf_len_r = guarded_form.buf_len_r

            reject_l = state_l == "reject"
            reject_r = state_r == "reject"

            if not reject_l:
                op_block_l = parser1.states[state_l].operation_block
                trans_block_l = parser1.states[state_l].transition_block
                op_size_l = op_block_l.size

            if not reject_r:
                op_block_r = parser2.states[state_r].operation_block
                trans_block_r = parser2.states[state_r].transition_block
                op_size_r = op_block_r.size

            if enable_leaps:
                if not reject_l and not reject_r:
                    leap = min(op_size_l - buf_len_l, op_size_r - buf_len_r)
                elif not reject_l:
                    leap = op_size_l - buf_len_l
                elif not reject_r:
                    leap = op_size_r - buf_len_r
                else:
                    leap = 1
            else:
                leap = 1

            transition_l = not reject_l and (buf_len_l + leap == op_size_l)
            transition_r = not reject_r and (buf_len_r + leap == op_size_r)

            new_bits_var = manager.fresh_variable(leap)
            new_root = current_pf.root

            def extend_buffer(parser: ParserProgram, *, left: bool) -> None:
                """
                Extend the buffer variable in the current pure formula.

                :param parser: the parser program to use for the extension
                :param left: whether to extend the left or right buffer
                """
                nonlocal new_root
                old_buf = current_pf.get_buffer_var(left=left)
                if old_buf is None:
                    current_pf.set_buffer_var(left=left, var=new_bits_var)
                else:
                    new_buf = manager.fresh_variable(len(old_buf) + leap)
                    current_pf.set_buffer_var(left=left, var=new_buf)
                    new_root = And(
                        new_root,
                        Equals(
                            new_buf,
                            Concatenate(parser, left=old_buf, right=new_bits_var),
                        ),
                    )

            extend_buffer(parser1, left=parser1.is_left)
            extend_buffer(parser2, left=parser2.is_left)

            pf = PureFormula(
                new_root, current_pf.header_field_vars, current_pf.buf_vars
            )

            logger.info(
                f"Equivalence checking loop status\n"
                f"Left - state: {state_l}, op. size: {op_size_l}, transitioning: {transition_l}\n"
                f"Right - state: {state_r}, op. size: {op_size_r}, transitioning: {transition_r}\n"
            )
            logger.debug(f"Buffers: {pf.buf_vars}")

            if transition_l:
                pf = op_block_l.strongest_postcondition(manager, pf)
            if transition_r:
                pf = op_block_r.strongest_postcondition(manager, pf)

            true_form = TRUE()
            left_trans = (
                trans_block_l.symbolic_transition(pf)
                if transition_l
                else [(true_form, state_l)]
            )
            right_trans = (
                trans_block_r.symbolic_transition(pf)
                if transition_r
                else [(true_form, state_r)]
            )

            for form_l, to_l in left_trans:
                for form_r, to_r in right_trans:
                    pf_new = PureFormula.clone(
                        And(pf.root, And(form_l, form_r)),
                        pf.header_field_vars,
                        pf.buf_vars,
                    )
                    if s.is_sat(pf_new.to_smt()):
                        work_queue.append(
                            GuardedFormula(
                                to_l,
                                to_r,
                                0 if transition_l else buf_len_l + leap,
                                0 if transition_r else buf_len_r + leap,
                                pf_new,
                                guarded_form,
                            )
                        )
                        logger.debug(
                            f"Found satisfiable:({to_l}, {to_r}) with formula {pf_new}"
                        )

            knowledge.add(guarded_form)

    return True, "\n".join(str(f) for f in knowledge)
