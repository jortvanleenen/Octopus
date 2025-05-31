"""
This module defines utility objects used throughout the project.

Author: Jort van Leenen
License: MIT (See LICENSE file or https://opensource.org/licenses/MIT for details)
"""


class AutoRepr:
    """A base class for objects that automatically generate a representation string."""

    def __repr__(self):
        cls = self.__class__.__name__
        args = ", ".join(f"{k!r}={v!r}" for k, v in self.__dict__.items())
        return f"{cls}({args})"
