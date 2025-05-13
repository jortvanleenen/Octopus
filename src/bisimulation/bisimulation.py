"""
This module defines Component, a class representing an operation in a P4 parser state.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""
from src.program.parser_program import ParserProgram


def naive_bisimulation(parser1: ParserProgram, parser2: ParserProgram):
    """
    Check whether two P4 parser blocks are bisimilar.

    This algorithm checks for bisimilarity by representing the two parsers as
    DFAs. This is considered naive due to their state space explosion.

    Additionally, note that bisimulation is performed in a forward manner.
    """

