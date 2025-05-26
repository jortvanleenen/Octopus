"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from typing import Any

from automata.dfa import DFA
from program.parser_program import ParserProgram
from pysmt.shortcuts import Portfolio


def naive_bisimulation(
    parser1: ParserProgram, parser2: ParserProgram
) -> tuple[bool, tuple[DFA.Configuration, DFA.Configuration]] | tuple[bool, set[Any]]:
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

    work_queue = [(config1, config2)]
    seen = set()
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
            return False, (config1, config2)

        print(f"Seen: {len(seen)}")
        print(f"Work queue: {len(work_queue)}")

    return True, seen


def symbolic_bisimulation(
    parser1: ParserProgram,
    parser2: ParserProgram,
    enable_leaps: bool,
    solver_portfolio: Portfolio,
) -> tuple[bool, tuple[DFA.Configuration, DFA.Configuration]] | tuple[bool, set[Any]]:
    pass
