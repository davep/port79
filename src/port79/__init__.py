"""An async-first, fully-typed client library for the Finger protocol (RFC 1288)."""

##############################################################################
# Python imports.
from importlib.metadata import version

######################################################################
# Main library information.
__author__ = "Dave Pearson"
__copyright__ = "Copyright 2026, Dave Pearson"
__credits__ = ["Dave Pearson"]
__maintainer__ = "Dave Pearson"
__email__ = "davep@davep.org"
__version__: str = version("port79")
__licence__ = "MIT"

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
# Public API.
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
