"""Unit tests for exception classes in port79."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Local imports.
from port79.exceptions import (
    ConnectionError,
    Port79Error,
    ResponseError,
    TimeoutError,
    URIError,
)


##############################################################################
def test_exception_hierarchy() -> None:
    """Test that all custom exceptions inherit from Port79Error."""
    assert issubclass(URIError, Port79Error)
    assert issubclass(ConnectionError, Port79Error)
    assert issubclass(TimeoutError, Port79Error)
    assert issubclass(ResponseError, Port79Error)
    assert issubclass(Port79Error, Exception)


### test_exceptions.py ends here
