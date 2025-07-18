"""
This module defines the deterministic finite automaton (DFA) representation
of the parsed P4 program.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from __future__ import annotations

import copy

from program.parser_program import ParserProgram


class DFA:
    """A class representing the DFA representation of the parsed P4 program."""

    class Configuration:
        """A class representing a state of the automaton."""

        def __init__(self, state_name: str, store: dict[str, str], buffer: str):
            """
            Initialise a configuration of the DFA.

            :param state_name: the name of the state
            :param store: the content of the store (header fields)
            :param buffer: the content of the buffer (input bits)
            """
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

    def step(self, configuration: DFA.Configuration, bit: str) -> DFA.Configuration:
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
            if len(wb) < state.operation_block.size:
                return DFA.Configuration(q, s, wb)

            s_prime, w_prime = state.operation_block.eval(s, wb)
            next_q = state.transition_block.eval(s_prime)
            return DFA.Configuration(next_q, s_prime, w_prime)

        return DFA.Configuration("reject", s, "")

    def multi_step(self, config: DFA.Configuration, bits: str) -> DFA.Configuration:
        """
        Perform multiple steps in the DFA.

        :param config: the current configuration (state, store, buffer)
        :param bits: the bit(s) to process
        :return: the final configuration
        """
        for bit in bits:
            config = self.step(config, bit)
        return config

    @staticmethod
    def initial_config(
        q0: str = "start", store: dict[str, str] = None, buffer: str = ""
    ) -> DFA.Configuration:
        """
        Create the initial configuration of the DFA.

        In P4, the initial state is always called "start".

        :param q0: the initial state of the DFA
        :param store: the initial store (header fields)
        :param buffer: the initial buffer (input bits)
        :return: the initial configuration
        """
        if store is None:
            store = {}
        return DFA.Configuration(q0, store, buffer)
