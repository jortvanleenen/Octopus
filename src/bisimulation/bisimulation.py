"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging

import pysmt.shortcuts as pysmt

from automata.dfa import DFA
from bisimulation.symbolic.formula import (
    TRUE,
    And,
    Concatenate,
    Equals,
    FormulaManager,
    GuardedFormula,
    PureFormula,
)
from program.parser_program import ParserProgram

logger = logging.getLogger(__name__)


def naive_bisimulation(
    parser1: ParserProgram, parser2: ParserProgram
) -> tuple[bool, set[tuple[DFA.Configuration, DFA.Configuration]]]:
    """
    Check whether two P4 parser programs are bisimilar.

    This algorithm checks for bisimilarity by representing the two parsers as
    DFAs. This approach is considered naive due to the accompanying state
    explosion, as no symbolic representation is used. Additionally, no
    optimisations, such as leaps, are performed.

    The bisimulation is performed in a forward manner.

    :param parser1: the first P4 parser program
    :param parser2: the second P4 parser program
    :return: a boolean indicating bisimilarity and seen configurations or counterexample
    """

    # In P4, the initial state is always called 'start'
    dfa1 = DFA(parser1)
    dfa2 = DFA(parser2)
    config1 = DFA.initial_config("start", {})
    config2 = DFA.initial_config("start", {})

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


def symbolic_bisimulation(
    parser1: ParserProgram,
    parser2: ParserProgram,
    enable_leaps: bool,
    solver_portfolio: pysmt.Portfolio,
) -> tuple[bool, set[GuardedFormula]]:
    """
    Check whether two P4 parser programs are bisimilar using symbolic execution.

    This algorithm checks for bisimilarity by representing the two parsers as
    modifiers of symbolic formulas. This approach is considered more efficient
    than the naive bisimulation, as it uses symbolic execution to explore the
    state space of the parsers. It also allows for optimisations, such as leaps,
    to be performed.

    :param parser1: the first P4 parser program
    :param parser2: the second P4 parser program
    :param enable_leaps: whether to enable leaps in the bisimulation
    :param solver_portfolio: the solver portfolio to use for symbolic execution
    :return: a boolean indicating bisimilarity and seen formulas or counterexample
    """

    def is_terminal(state_name: str) -> bool:
        """
        Check if a state is terminal.

        :param state_name: the state to check
        :return: True if the state is terminal, False otherwise
        """
        return state_name in ["accept", "reject"]

    knowledge: set[GuardedFormula] = set()
    manager = FormulaManager()
    # In P4, the initial state is always called 'start'
    work_queue = [GuardedFormula("start", "start", 0, 0, PureFormula(TRUE()))]
    with solver_portfolio as s:
        while len(work_queue) > 0:
            guarded_form = work_queue.pop(0)

            relevant_pfs = set()
            for seen_guarded_form in knowledge:
                if guarded_form.has_equal_guard(seen_guarded_form):
                    relevant_pfs.add(seen_guarded_form.pf)
            current_pf = guarded_form.pf

            implication = pysmt.Implies(
                current_pf.to_smt(), pysmt.Or(*[pf.to_smt() for pf in relevant_pfs])
            )
            if not s.is_sat(current_pf.to_smt()):
                print("current is unsat, continiueing")
                continue
            else:
                print("current is sat")
            if s.is_sat(implication):
                continue

            state_l = guarded_form.state_l
            state_r = guarded_form.state_r
            if (state_l == "accept") != (state_r == "accept"):
                trace = []
                current = guarded_form
                while current is not None:
                    trace.append(current)
                    current = current.prev_guarded_formula
                trace.reverse()

                lines = []
                for step, g in enumerate(trace):
                    lines.append(f"Step {step}:")
                    lines.append(f"  Left state: {g.state_l}, Right state: {g.state_r}")
                    lines.append(
                        f"  Buffer lengths: left={g.buf_len_l}, right={g.buf_len_r}"
                    )
                    lines.append(f"  Header fields: {g.pf.header_field_vars}")
                    lines.append(f"  Buffer vars: {g.pf.buf_vars}")
                    lines.append(f"  Formula root: {g.pf.root}")
                    lines.append("")

                trace_output = "\n".join(lines)

                return False, {trace_output}

            if is_terminal(state_l) and is_terminal(state_r):
                # TODO: correct?
                continue

            buf_len_l = guarded_form.buf_len_l
            print("buf_len_l", buf_len_l)
            buf_len_r = guarded_form.buf_len_r
            print("buf len r", buf_len_r)
            op_block_l = parser1.states[state_l].operation_block
            op_block_r = parser2.states[state_r].operation_block
            trans_block_l = parser1.states[state_l].transition_block
            trans_block_r = parser2.states[state_r].transition_block

            op_size_l = op_block_l.size
            op_size_r = op_block_r.size

            leap = (
                min(op_size_l - buf_len_l, op_size_r - buf_len_r) if enable_leaps else 1
            )
            print("leap", leap)

            transition_l = buf_len_l + leap == op_size_l
            transition_r = buf_len_r + leap == op_size_r

            new_bits_var = manager.fresh_variable(leap)
            new_root = current_pf.root

            old_buf_l = current_pf.get_buffer_var(left=True)
            if old_buf_l is None:
                current_pf.set_buffer_var(left=True, var=new_bits_var)
            else:
                new_buf_l = manager.fresh_variable(len(old_buf_l) + leap)
                current_pf.set_buffer_var(left=True, var=new_buf_l)
                buf_eq_l = Equals(new_buf_l, Concatenate(old_buf_l, new_bits_var))
                new_root = And(new_root, buf_eq_l)

            old_buf_r = current_pf.get_buffer_var(left=False)
            if old_buf_r is None:
                print("setting length buf to: ", leap)
                current_pf.set_buffer_var(left=False, var=new_bits_var)
            else:
                new_buf_r = manager.fresh_variable(len(old_buf_r) + leap)
                print("setting length buf to: ", len(old_buf_r), leap)
                current_pf.set_buffer_var(left=False, var=new_buf_r)
                buf_eq_r = Equals(new_buf_r, Concatenate(old_buf_r, new_bits_var))
                new_root = And(new_root, buf_eq_r)

            pf = PureFormula(
                new_root,
                current_pf.header_field_vars,
                current_pf.buf_vars,
            )

            logger.debug(
                f"Parser status\n"
                f"Left: state {state_l} - op. size {op_size_l} {'transitioning' if transition_l else ''}\n"
                f"Right: state {state_r} - op. size {op_size_r} {'transitioning' if transition_r else ''}\n"
                f"Buffers: {pf.buf_vars}"
            )

            if transition_l and transition_r:
                logger.info("Both parsers transition.")
                pf = op_block_l.strongest_postcondition(manager, pf)
                pf = op_block_r.strongest_postcondition(manager, pf)

                for form_l, to_l in trans_block_l.symbolic_transition(pf):
                    for form_r, to_r in trans_block_r.symbolic_transition(pf):
                        pf_new = PureFormula.clone(
                            And(pf.root, And(form_l, form_r)),
                            pf.header_field_vars,
                            pf.buf_vars,
                        )

                        if s.is_sat(pf_new.to_smt()):
                            work_queue.append(
                                GuardedFormula(to_l, to_r, 0, 0, pf_new, guarded_form)
                            )

            elif transition_l:
                logger.info("Only the left-hand parser transitions.")
                pf = op_block_l.strongest_postcondition(manager, pf)

                for form, to_l in trans_block_l.symbolic_transition(pf):
                    pf_new = PureFormula.clone(
                        And(pf.root, form),
                        pf.header_field_vars,
                        pf.buf_vars,
                    )
                    if s.is_sat(pf_new.to_smt()):
                        work_queue.append(
                            GuardedFormula(
                                to_l, state_r, 0, buf_len_r + leap, pf_new, guarded_form
                            )
                        )

            elif transition_r:
                logger.info("Only the right-hand parser transitions.")
                pf = op_block_r.strongest_postcondition(manager, pf)

                for form, to_r in trans_block_r.symbolic_transition(pf):
                    pf_new = PureFormula.clone(
                        And(pf.root, form),
                        pf.header_field_vars,
                        pf.buf_vars,
                    )
                    if s.is_sat(pf_new.to_smt()):
                        work_queue.append(
                            GuardedFormula(
                                state_l, to_r, buf_len_l + leap, 0, pf_new, guarded_form
                            )
                        )

            knowledge.add(guarded_form)

    return True, knowledge
