"""
This module defines utility objects used throughout the project.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""

import time
import tracemalloc

from contextlib import contextmanager
from typing import Generator, Any

import logging

logger = logging.getLogger(__name__)


class AutoRepr:
    """A base class for objects that automatically generate a representation string."""

    def __repr__(self):
        cls = self.__class__.__name__
        args = ", ".join(f"{k!r}={v!r}" for k, v in self.__dict__.items())
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
def timed_block(label: str) -> Generator[None, Any, None]:
    """
    Context manager to measure wall time, CPU time, and memory usage of a code block.

    :param label: a label for the block of code being timed
    """
    tracemalloc.start()
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    yield
    end_wall = time.perf_counter()
    end_cpu = time.process_time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    duration_msg = (
        f"{label} completed. Timing and memory results:\n"
        f"  Wall time: {end_wall - start_wall:.4f} s\n"
        f"  CPU time:  {end_cpu - start_cpu:.4f} s\n"
        f"  Peak memory: {peak / 1024:.2f} KiB"
    )
    print(duration_msg)