"""Finger query classification and types as defined by RFC 1288."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Python imports.
from enum import Enum, auto


##############################################################################
class QueryKind(Enum):
    """Enumeration of Finger query kinds defined by RFC 1288."""

    SYSTEM = auto()
    """A standard system query requesting logged-in user information."""
    USER = auto()
    """A query requesting information for a specific user."""
    FORWARDING = auto()
    """A system query requesting remote host forwarding."""
    USER_FORWARDING = auto()
    """A user query requesting remote host forwarding."""


### query.py ends here
