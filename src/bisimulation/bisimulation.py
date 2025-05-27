"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""
import copy

from automata.dfa import DFA
from bisimulation.symbolic.formula import GuardedFormula, PureFormula
from program.expression import Concatenate
from program.parser_program import ParserProgram
from pysmt.shortcuts import Portfolio, Implies, Or


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
    """

    # In P4, the initial state is always called 'start'
    dfa1 = DFA(parser1)
    dfa2 = DFA(parser2)
    config1 = dfa1.initial_config("start", {})
    config2 = dfa2.initial_config("start", {})

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
    solver_portfolio: Portfolio,
):
    knowledge: set[GuardedFormula] = set()
    # In P4, the initial state is always called 'start'
    work_queue = [GuardedFormula("start", "start", 0, 0, PureFormula.TRUE())]
    while len(work_queue) > 0:
        formula = work_queue.pop(0)

        relevant_pfs = set()
        for seen_formula in knowledge:
            if formula.equal_template(seen_formula):
                relevant_pfs.add(seen_formula.pf)
        current_pf = formula.pf

        # TODO: Update logic to BV when possible?
        if Implies(
            current_pf.to_smt(), Or(*[pf.to_smt() for pf in relevant_pfs])
        ).is_sat(logic="BVt", portfolio=solver_portfolio):
            continue

        # Both transition
        if (
            formula.buf_len_l + 1 == parser1.states[formula.state_l].operationBlock.size
            and formula.buf_len_r + 1
            == parser2.states[formula.state_r].operationBlock.size
        ):
            new_pf = parser1.states[
                formula.state_l
            ].operationBlock.strongest_postcondition(
                parser2.states[formula.state_r].operationBlock.strongest_postcondition(
                    formula.pf, left=False
                ),
                left=True,
            )

            for form_l, to_state_l in parser1.states[
                formula.state_l
            ].transitionBlock.symbolic_transition(new_pf):
                for form_r, to_state_r in parser2.states[
                    formula.state_r
                ].transitionBlock.symbolic_transition(new_pf):
                    new_pf_copy = copy.deepcopy(new_pf)
                    new_pf_copy = PureFormula.And(new_pf_copy, PureFormula.And(form_l, form_r))
                    work_queue.append(
                        GuardedFormula(
                            to_state_l,
                            to_state_r,
                            0,
                            0,
                            new_pf_copy,
                        )
                    )
        # Left transitions, right does not
        elif (
            formula.buf_len_l + 1 == parser1.states[formula.state_l].operationBlock.size
            and formula.buf_len_r + 1
            < parser2.states[formula.state_r].operationBlock.size
        ):
            new_pf = parser1.states[
                formula.state_l
            ].operationBlock.strongest_postcondition(formula.pf, left=True)

            for form, to_state in parser1.states[
                formula.state_l
            ].transitionBlock.symbolic_transition(new_pf):
                new_pf_copy = copy.deepcopy(new_pf)
                new_pf_copy = PureFormula.And(new_pf_copy, form)
                work_queue.append(
                    GuardedFormula(
                        to_state,
                        formula.state_r,
                        0,
                        formula.buf_len_r + 1,
                        new_pf_copy,
                    )
                )
        # Right transitions, left does not
        elif (
            formula.buf_len_l + 1 < parser1.states[formula.state_l].operationBlock.size
            and formula.buf_len_r + 1
            == parser2.states[formula.state_r].operationBlock.size
        ):
            new_pf = parser2.states[
                formula.state_r
            ].operationBlock.strongest_postcondition(formula.pf, left=False)

            for form, to_state in parser2.states[
                formula.state_r
            ].transitionBlock.symbolic_transition(new_pf):
                new_pf_copy = copy.deepcopy(new_pf)
                new_pf_copy = PureFormula.And(new_pf_copy, form)
                work_queue.append(
                    GuardedFormula(
                        formula.state_l,
                        to_state,
                        formula.buf_len_l + 1,
                        0,
                        new_pf_copy,
                    )
                )

        # Both do not transition
        else:
            new_bit = formula.pf.fresh_variable(1)
            old_buf_l = formula.pf.get_buffer_var(left=True)
            new_buf_l = formula.pf.fresh_variable(len(old_buf_l) + 1)
            buf_l = PureFormula.Equals(new_buf_l, Concatenate(old_buf_l, new_bit))
            old_buf_r = formula.pf.get_buffer_var(left=False)
            new_buf_r = formula.pf.fresh_variable(len(old_buf_r) + 1)
            formula.pf.set_buffer_var(left=False, var=new_buf_r)
            buf_r = PureFormula.Equals(new_buf_r, Concatenate(old_buf_r, new_bit))
            new_pf = PureFormula.And(
                formula.pf,
                PureFormula.And(buf_l, buf_r),
            )
            work_queue.append(
                GuardedFormula(
                    formula.state_l,
                    formula.state_r,
                    formula.buf_len_l + 1,
                    formula.buf_len_r + 1,
                    new_pf,
                )
            )

