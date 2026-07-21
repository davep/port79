"""An async-first, fully-typed client library for the Finger protocol (RFC 1288)."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Local imports.
from .client import DEFAULT_TIMEOUT, Client
from .exceptions import (
    ConnectionError,
    Port79Error,
    ResponseError,
    TimeoutError,
    URIError,
)
from .query import QueryKind
from .response import Response
from .uri import (
    FINGER_DEFAULT_PORT,
    FINGER_PREFIX,
    FINGER_SCHEME,
    FingerURI,
)

##############################################################################
__all__ = [
    "Client",
    "ConnectionError",
    "DEFAULT_TIMEOUT",
    "FINGER_DEFAULT_PORT",
    "FINGER_PREFIX",
    "FINGER_SCHEME",
    "FingerURI",
    "Port79Error",
    "QueryKind",
    "Response",
    "ResponseError",
    "TimeoutError",
    "URIError",
]

### __init__.py ends here
