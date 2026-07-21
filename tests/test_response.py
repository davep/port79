"""Unit tests for Response class."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Local imports.
from port79.query import QueryKind
from port79.response import Response
from port79.uri import FingerURI


##############################################################################
def test_response_properties() -> None:
    """Test Response class properties and methods."""
    uri = FingerURI("finger://plan.cat/davep?W")
    raw_data = b"Login: davep\nName: Dave Pearson\nPlan:\nWorking on port79 library.\n"
    res = Response(uri=uri, raw_bytes=raw_data, encoding="utf-8", latency=0.045)

    assert res.uri == uri
    assert res.target_host == "plan.cat"
    assert res.username == "davep"
    assert res.is_verbose
    assert res.is_user_query
    assert not res.is_system_query
    assert not res.is_forwarding_query
    assert res.query_kind == QueryKind.USER
    assert res.raw_query == "/W davep\r\n"
    assert res.raw_bytes == raw_data
    assert res.encoding == "utf-8"
    assert res.latency == 0.045
    assert str(res) == raw_data.decode("utf-8")
    assert res.lines == [
        "Login: davep",
        "Name: Dave Pearson",
        "Plan:",
        "Working on port79 library.",
    ]
    assert "Response(uri=" in repr(res)


##############################################################################
def test_response_decoding_fallback() -> None:
    """Test decoding fallback when invalid UTF-8 bytes are encountered."""
    uri = FingerURI("finger://plan.cat/davep")
    bad_bytes = b"Hello \xff\xfe World"
    res = Response(uri=uri, raw_bytes=bad_bytes, encoding="utf-8")
    assert "Hello" in res.text
    assert "World" in res.text


### test_response.py ends here
