"""
This module defines utility objects used throughout the project.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging

logger = logging.getLogger(__name__)


class ReprMixin:
    """A base class for objects that automatically generates a representation string."""

    def __repr__(self):
        cls = self.__class__.__name__
        str_filter = ["_program", "program"]
        filtered_items = {k: v for k, v in self.__dict__.items() if k not in str_filter}
        args = ", ".join(f"{k!r}={v!r}" for k, v in filtered_items.items())
        return f"{cls}({args})"


def setup_logging(verbosity: int) -> None:
    """
    Set up the logging configuration based on the verbosity level.

    :param verbosity: the verbosity level
    """
    level = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG][
        min(verbosity, 3)
    ]
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(
            format="[%(levelname)s - %(filename)s, line %(lineno)d]: %(message)s",
            level=level,
        )
    else:
        root_logger.setLevel(level)
