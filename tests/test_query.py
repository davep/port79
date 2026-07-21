"""Unit tests for QueryKind enumeration."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Local imports.
from port79.query import QueryKind


##############################################################################
def test_query_kind_members() -> None:
    """Test that all QueryKind members exist."""
    assert QueryKind.SYSTEM is not None
    assert QueryKind.USER is not None
    assert QueryKind.FORWARDING is not None
    assert QueryKind.USER_FORWARDING is not None


### test_query.py ends here
