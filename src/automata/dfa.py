"""
This module defines the deterministic finite automaton (DFA) representation
of the parsed P4 program.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import copy
from typing import Dict, Optional, Set

from src.program.parser_program import ParserProgram


class DFA:
    """A class representing the DFA representation of the parsed P4 program."""

    class Configuration:
        """A class representing a state of the automaton."""

        def __init__(self, state_name: str, store: Dict[str, str], buffer: str):
            self.state = state_name
            self.store = store
            self.buffer = buffer

        def is_accepting(self) -> bool:
            """
            Check if the configuration is accepting.

            :return: True if accepting, False otherwise
            """
            return self.state == "accept" and self.buffer == ""

        def is_terminal(self) -> bool:
            """
            Check if the configuration is terminal.

            :return: True if terminal, False otherwise
            """
            return self.state in ["accept", "reject"]

        def __eq__(self, other):
            if not isinstance(other, DFA.Configuration):
                return NotImplemented
            return (
                self.state == other.state
                and self.buffer == other.buffer
                and self.store == other.store
            )

        def __hash__(self):
            return hash((self.state, self.buffer, frozenset(self.store.items())))

        def __repr__(self):
            return f"<{self.state}, {self.store}, {self.buffer}>"

    def __init__(self, program: ParserProgram):
        self.program = program

    def step(self, configuration: "DFA.Configuration", bit: str) -> "DFA.Configuration":
        """
        Perform a single step (configuration -> configuration) in the DFA.

        :param configuration: the current configuration (state, store, buffer)
        :param bit: the bit to process
        :return: the next configuration
        """
        q = configuration.state
        s = copy.deepcopy(configuration.store)
        w = configuration.buffer

        if q in self.program.states:  # Does not include accept and reject states
            state = self.program.states[q]
            wb = w + bit
            if len(wb) < state.operationBlock.size:
                return DFA.Configuration(q, s, wb)

            s_prime, w_prime = state.operationBlock.eval(s, wb)
            next_q = state.transitionBlock.eval(s_prime)
            return DFA.Configuration(next_q, s_prime, w_prime)

        return DFA.Configuration("reject", s, "")

    def multi_step(self, config: "DFA.Configuration", bits: str) -> "DFA.Configuration":
        """
        Perform multiple steps in the DFA.

        :param config: the current configuration (state, store, buffer)
        :param bits: the bit(s) to process
        :return: the final configuration
        """
        for bit in bits:
            config = self.step(config, bit)
        return config

    def is_accepted(self, config: "DFA.Configuration", bits: str) -> bool:
        final_config = self.multi_step(config, bits)
        return final_config.is_accepting()

    def initial_config(self, q0: str, store: Dict[str, str]) -> "DFA.Configuration":
        return DFA.Configuration(q0, store, "")
