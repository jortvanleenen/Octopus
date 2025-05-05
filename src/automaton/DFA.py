"""
This module defines the DFA representation of the parsed P4 program.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

from typing import Dict, Optional, Set


class DFA:
    """A class representing the DFA representation of the parsed P4 program."""

    class Configuration:
        """A class representing a state of the automaton."""

        def __init__(self, state: str, store: Dict[str, str], buffer: str):
            self.state = state
            self.store = store
            self.buffer = buffer

        def is_accepting(self) -> bool:
            """
            Check if the configuration is in an accepting state.

            :return: True if in an accepting state, False otherwise
            """
            return self.state == "accept" and self.buffer == ""

        def is_terminal(self) -> bool:
            """
            Check if the configuration is in a terminal state.

            :return: True if in a terminal state, False otherwise
            """
            return self.state in {"accept", "reject"}

        def __repr__(self):
            return f"<{self.state}, {self.store}, {self.buffer}>"

    def __init__(self, q: Set[str], op_size: Dict[str, int], transition):
        self.q = q
        self.op_size = op_size
        self.transition = transition

    def delta(
        self, config: "DFA.Configuration", bit: str
    ) -> Optional["DFA.Configuration"]:
        q, s, w = config.state, config.store, config.buffer

        if q in self.q:
            w_new = w + bit
            required = self.op_size[q]

            if len(w_new) < required:
                return DFA.Configuration(q, s, w_new)

            s_prime, leftover, next_q = self.transition[q](s, w_new)
            return DFA.Configuration(next_q, s_prime, leftover)

        return DFA.Configuration("reject", s, "")

    def delta_star(
        self, config: "DFA.Configuration", bits: str
    ) -> Optional["DFA.Configuration"]:
        for b in bits:
            config = self.delta(config, b)
            if config is None:
                return None
        return config

    def is_accepted(self, config: "DFA.Configuration", bits: str) -> bool:
        final_config = self.delta_star(config, bits)
        return final_config is not None and final_config.is_accepting()

    def initial_config(
        self, q0: str, store: Dict[str, str]
    ) -> "DFA.Configuration":
        return DFA.Configuration(q0, store, "")
