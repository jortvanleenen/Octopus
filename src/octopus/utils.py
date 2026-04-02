"""
This module defines utility objects used throughout the project.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Generator

import psutil

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


@contextmanager
def stat_block(label: str) -> Generator[None, Any, None]:
    """
    Context manager to measure wall time, CPU time, and memory usage of a code block.

    :param label: a label for the block of code that is being measured
    :return: a generator that yields control to the block of code
    """
    process = psutil.Process(os.getpid())

    start_wall = time.perf_counter()
    start_cpu = time.process_time()

    peak = process.memory_info().rss

    yield

    end_wall = time.perf_counter()
    end_cpu = time.process_time()
    peak = max(peak, process.memory_info().rss)

    print(
        f"{label} completed. Timing and memory results:\n"
        f"  Wall time: {end_wall - start_wall:.4f} s\n"
        f"  CPU time:  {end_cpu - start_cpu:.4f} s\n"
        f"  Peak RSS:  {peak / (1024 ** 2):.2f} MiB"
    )
