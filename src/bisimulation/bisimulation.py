"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import copy

import pysmt.shortcuts as pysmt

from automata.dfa import DFA
from bisimulation.symbolic.formula import (
    GuardedFormula,
    PureFormula,
    FormulaManager,
    And,
    Equals,
    TRUE,
    Concatenate,
)
from program.parser_program import ParserProgram


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
    knowledge: set[GuardedFormula] = set()
    manager = FormulaManager()
    # In P4, the initial state is always called 'start'
    work_queue = [GuardedFormula("start", "start", 0, 0, PureFormula(TRUE()))]
    with solver_portfolio as s:
        while len(work_queue) > 0:
            formula = work_queue.pop(0)

            relevant_pfs = set()
            for seen_formula in knowledge:
                if formula.equal_guard(seen_formula):
                    relevant_pfs.add(seen_formula.pf)
            current_pf = formula.pf

            implication = pysmt.Implies(
                current_pf.to_smt(), pysmt.Or(*[pf.to_smt() for pf in relevant_pfs])
            )
            if s.is_sat(implication):
                continue

            state_l = formula.state_l
            state_r = formula.state_r
            if (state_l == "accept") != (state_r == "accept"):
                return False, {formula}

            buf_l = formula.buf_len_l
            buf_r = formula.buf_len_r
            opblock_l = parser1.states[state_l].operationBlock
            opblock_r = parser2.states[state_r].operationBlock
            transblock_l = parser1.states[state_l].transitionBlock
            transblock_r = parser2.states[state_r].transitionBlock

            size_l = opblock_l.size
            size_r = opblock_r.size

            transition_l = buf_l + 1 == size_l
            transition_r = buf_r + 1 == size_r

            new_bit = manager.fresh_variable(1)

            old_buf_l = formula.pf.get_buffer_var(left=True)
            if old_buf_l is None:
                new_buf_l = manager.fresh_variable(1)
                formula.pf.set_buffer_var(left=True, var=new_buf_l)
                buf_eq_l = Equals(new_buf_l, new_bit)
            else:
                new_buf_l = manager.fresh_variable(len(old_buf_l) + 1)
                formula.pf.set_buffer_var(left=True, var=new_buf_l)
                buf_eq_l = Equals(new_buf_l, Concatenate(old_buf_l, new_bit))

            old_buf_r = formula.pf.get_buffer_var(left=False)
            if old_buf_r is None:
                new_buf_r = manager.fresh_variable(1)
                formula.pf.set_buffer_var(left=False, var=new_buf_r)
                buf_eq_r = Equals(new_buf_r, new_bit)
            else:
                new_buf_r = manager.fresh_variable(len(old_buf_r) + 1)
                formula.pf.set_buffer_var(left=False, var=new_buf_r)
                buf_eq_r = Equals(new_buf_r, Concatenate(old_buf_r, new_bit))

            pf = PureFormula.clone_with_new_root(
                formula.pf, And(formula.pf.root, And(buf_eq_l, buf_eq_r))
            )

            if transition_l and transition_r:
                pf = opblock_l.strongest_postcondition(manager, formula.pf, left=True)
                pf = opblock_r.strongest_postcondition(manager, pf, left=False)

                for form_l, to_l in transblock_l.symbolic_transition(manager, pf):
                    for form_r, to_r in transblock_r.symbolic_transition(manager, pf):
                        pf_root = copy.deepcopy(pf.root)
                        pf_new = PureFormula.clone_with_new_root(
                            formula.pf, And(pf_root, And(form_l, form_r))
                        )
                        work_queue.append(GuardedFormula(to_l, to_r, 0, 0, pf_new))

            elif transition_l:
                pf = opblock_l.strongest_postcondition(manager, formula.pf, left=True)

                for form, to_l in transblock_l.symbolic_transition(manager, pf):
                    pf_root = copy.deepcopy(pf.root)
                    pf_new = PureFormula.clone_with_new_root(
                        formula.pf, And(pf_root, form)
                    )
                    work_queue.append(
                        GuardedFormula(to_l, state_r, 0, buf_r + 1, pf_new)
                    )

            elif transition_r:
                pf = opblock_r.strongest_postcondition(manager, formula.pf, left=False)

                for form, to_r in transblock_r.symbolic_transition(manager, pf):
                    pf_root = copy.deepcopy(pf.root)
                    pf_new = PureFormula.clone_with_new_root(
                        formula.pf, And(pf_root, form)
                    )
                    work_queue.append(
                        GuardedFormula(state_l, to_r, buf_l + 1, 0, pf_new)
                    )

            else:
                work_queue.append(
                    GuardedFormula(state_l, state_r, buf_l + 1, buf_r + 1, pf)
                )

            knowledge.add(formula)

    return True, knowledge
