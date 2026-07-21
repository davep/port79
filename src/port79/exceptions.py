"""Exception hierarchy for the port79 Finger client library."""

##############################################################################
# Future imports.
from __future__ import annotations


##############################################################################
class Port79Error(Exception):
    """Base exception class for all port79 errors."""


##############################################################################
class URIError(Port79Error):
    """Exception raised when a Finger URI is invalid or parsing fails."""


##############################################################################
class ConnectionError(Port79Error):
    """Exception raised when a network connection to a Finger server fails."""


##############################################################################
class TimeoutError(Port79Error):
    """Exception raised when a network operation times out."""


##############################################################################
class ResponseError(Port79Error):
    """Exception raised when processing a Finger response fails."""


### exceptions.py ends here
