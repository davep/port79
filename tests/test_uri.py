"""Unit tests for FingerURI class."""

##############################################################################
# Third party imports.
import pytest

##############################################################################
# Local imports.
from port79.exceptions import URIError
from port79.query import QueryKind
from port79.uri import FingerURI


##############################################################################
def test_finger_uri_standard_user() -> None:
    """Test parsing a standard user URI."""
    uri = FingerURI("finger://plan.cat/davep")
    assert uri.scheme == "finger"
    assert uri.host == "plan.cat"
    assert uri.port == 79
    assert uri.username == "davep"
    assert uri.target_host is None
    assert not uri.is_verbose
    assert uri.is_user_query
    assert not uri.is_system_query
    assert not uri.is_forwarding_query
    assert uri.query_kind == QueryKind.USER
    assert uri.raw_query == "davep\r\n"
    assert str(uri) == "finger://plan.cat/davep"


##############################################################################
def test_finger_uri_standard_system() -> None:
    """Test parsing a system-wide user listing URI."""
    uri = FingerURI("finger://plan.cat/")
    assert uri.scheme == "finger"
    assert uri.host == "plan.cat"
    assert uri.port == 79
    assert uri.username is None
    assert not uri.is_verbose
    assert not uri.is_user_query
    assert uri.is_system_query
    assert uri.query_kind == QueryKind.SYSTEM
    assert uri.raw_query == "\r\n"
    assert str(uri) == "finger://plan.cat/"


##############################################################################
def test_finger_uri_verbose_query() -> None:
    """Test parsing verbose query URIs."""
    uri1 = FingerURI("finger://plan.cat/davep?W")
    assert uri1.is_verbose
    assert uri1.raw_query == "/W davep\r\n"

    uri2 = FingerURI("finger://plan.cat/w/davep")
    assert uri2.is_verbose
    assert uri2.username == "davep"
    assert uri2.raw_query == "/W davep\r\n"

    uri3 = FingerURI("finger://plan.cat/?W")
    assert uri3.is_verbose
    assert uri3.username is None
    assert uri3.raw_query == "/W\r\n"


##############################################################################
def test_finger_uri_from_target_string() -> None:
    """Test parsing target strings like 'davep@plan.cat' and '/W davep@plan.cat'."""
    uri1 = FingerURI.from_string("davep@plan.cat")
    assert uri1.host == "plan.cat"
    assert uri1.username == "davep"
    assert not uri1.is_verbose
    assert uri1.raw_query == "davep\r\n"

    uri2 = FingerURI.from_string("/W davep@plan.cat")
    assert uri2.host == "plan.cat"
    assert uri2.username == "davep"
    assert uri2.is_verbose
    assert uri2.raw_query == "/W davep\r\n"

    uri3 = FingerURI.from_string("@plan.cat")
    assert uri3.host == "plan.cat"
    assert uri3.username is None
    assert uri3.raw_query == "\r\n"

    uri4 = FingerURI.from_string("/W @plan.cat")
    assert uri4.host == "plan.cat"
    assert uri4.username is None
    assert uri4.is_verbose
    assert uri4.raw_query == "/W\r\n"

    uri5 = FingerURI.from_string("plan.cat")
    assert uri5.host == "plan.cat"
    assert uri5.username is None
    assert uri5.raw_query == "\r\n"


##############################################################################
def test_finger_uri_custom_port() -> None:
    """Test FingerURI with custom TCP port."""
    uri = FingerURI("finger://plan.cat:7979/davep")
    assert uri.port == 7979
    assert uri.host == "plan.cat"
    assert uri.raw_query == "davep\r\n"
    assert str(uri) == "finger://plan.cat:7979/davep"

    uri_target = FingerURI.from_string("davep@plan.cat:7979")
    assert uri_target.port == 7979
    assert uri_target.host == "plan.cat"


##############################################################################
def test_finger_uri_forwarding_query() -> None:
    """Test FingerURI with forwarding targets."""
    uri = FingerURI.from_string("davep@remotehost@gateway.org")
    assert uri.host == "gateway.org"
    assert uri.username == "davep"
    assert uri.target_host == "remotehost"
    assert uri.is_forwarding_query
    assert uri.query_kind == QueryKind.USER_FORWARDING
    assert uri.raw_query == "davep@remotehost\r\n"


##############################################################################
def test_finger_uri_with_default_scheme() -> None:
    """Test with_default_scheme method."""
    uri1 = FingerURI.with_default_scheme("plan.cat/davep")
    assert uri1.scheme == "finger"
    assert uri1.host == "plan.cat"
    assert uri1.username == "davep"

    uri2 = FingerURI.with_default_scheme("finger://plan.cat/davep")
    assert uri2.host == "plan.cat"


##############################################################################
def test_finger_uri_modification_methods() -> None:
    """Test with_host, with_port, with_username, with_verbose, and replace methods."""
    base = FingerURI("finger://plan.cat/davep")

    u_host = base.with_host("example.com")
    assert u_host.host == "example.com"
    assert u_host.username == "davep"

    u_port = base.with_port(7979)
    assert u_port.port == 7979

    u_user = base.with_username("alice")
    assert u_user.username == "alice"

    u_nouser = base.with_username(None)
    assert u_nouser.username is None
    assert u_nouser.is_system_query

    u_verbose = base.with_verbose(True)
    assert u_verbose.is_verbose

    u_replaced = base.replace(host="test.org", port=7900, is_verbose=True)
    assert u_replaced.host == "test.org"
    assert u_replaced.port == 7900
    assert u_replaced.is_verbose


##############################################################################
def test_finger_uri_validation_errors() -> None:
    """Test that invalid URIs raise URIError."""
    with pytest.raises(URIError):
        FingerURI("")

    with pytest.raises(URIError):
        FingerURI("   ")

    with pytest.raises(URIError):
        FingerURI("davep")

    with pytest.raises(URIError):
        FingerURI("davep@plan.cat")

    with pytest.raises(URIError):
        FingerURI("/W davep@plan.cat")

    with pytest.raises(URIError):
        FingerURI("plan.cat")

    with pytest.raises(URIError):
        FingerURI("http://plan.cat/davep")

    with pytest.raises(URIError):
        FingerURI.from_string("davep@plan.cat:invalid_port")

    with pytest.raises(URIError):
        FingerURI("finger://")

    with pytest.raises(URIError):
        base = FingerURI("finger://plan.cat/davep")
        base.with_host("")


##############################################################################
def test_finger_uri_dunder_methods() -> None:
    """Test __repr__, __eq__, __hash__, and __len__ dunder methods."""
    uri1 = FingerURI("finger://plan.cat/davep")
    uri2 = FingerURI("finger://plan.cat/davep")
    uri3 = FingerURI("finger://plan.cat/alice")

    assert repr(uri1) == "FingerURI('finger://plan.cat/davep')"
    assert uri1 == uri2
    assert uri1 == "finger://plan.cat/davep"
    assert uri1 != uri3
    assert uri1 != 123
    assert hash(uri1) == hash(uri2)
    assert len(uri1) == len("finger://plan.cat/davep")
    assert uri1.bytes_left == uri1.MAXIMUM_LENGTH - len(uri1)
    assert not uri1.is_too_long


##############################################################################
def test_finger_uri_resolve_relative_username() -> None:
    """Test resolving relative usernames and paths against a base FingerURI."""
    base = FingerURI("finger://plan.cat/davep")

    resolved_user = base.resolve("alice")
    assert resolved_user.host == "plan.cat"
    assert resolved_user.port == 79
    assert resolved_user.username == "alice"
    assert str(resolved_user) == "finger://plan.cat/alice"

    resolved_abs = base.resolve("/alice")
    assert resolved_abs.host == "plan.cat"
    assert resolved_abs.username == "alice"
    assert str(resolved_abs) == "finger://plan.cat/alice"

    resolved_system = base.resolve("/")
    assert resolved_system.host == "plan.cat"
    assert resolved_system.username is None
    assert str(resolved_system) == "finger://plan.cat/"

    resolved_empty = base.resolve("")
    assert resolved_empty.host == "plan.cat"
    assert resolved_empty.username == "davep"
    assert str(resolved_empty) == "finger://plan.cat/davep"


##############################################################################
def test_finger_uri_resolve_from_system_base() -> None:
    """Test resolving from a system-wide query base URI."""
    base = FingerURI("finger://plan.cat/")

    resolved = base.resolve("alice")
    assert resolved.host == "plan.cat"
    assert resolved.username == "alice"
    assert str(resolved) == "finger://plan.cat/alice"

    resolved_system = base.resolve("/")
    assert resolved_system.host == "plan.cat"
    assert resolved_system.username is None
    assert str(resolved_system) == "finger://plan.cat/"


##############################################################################
def test_finger_uri_resolve_custom_port() -> None:
    """Test that resolving preserves custom TCP ports."""
    base = FingerURI("finger://plan.cat:7979/davep")

    resolved = base.resolve("alice")
    assert resolved.host == "plan.cat"
    assert resolved.port == 7979
    assert resolved.username == "alice"
    assert str(resolved) == "finger://plan.cat:7979/alice"

    resolved_system = base.resolve("/")
    assert resolved_system.host == "plan.cat"
    assert resolved_system.port == 7979
    assert resolved_system.username is None
    assert str(resolved_system) == "finger://plan.cat:7979/"


##############################################################################
def test_finger_uri_resolve_scheme_and_absolute() -> None:
    """Test resolving absolute URIs, scheme-relative URIs, and FingerURI instances."""
    base = FingerURI("finger://plan.cat/davep")

    resolved_abs = base.resolve("finger://example.com/alice")
    assert resolved_abs.host == "example.com"
    assert resolved_abs.username == "alice"
    assert str(resolved_abs) == "finger://example.com/alice"

    resolved_net = base.resolve("//example.com/alice")
    assert resolved_net.host == "example.com"
    assert resolved_net.username == "alice"
    assert str(resolved_net) == "finger://example.com/alice"

    resolved_obj = base.resolve(FingerURI("finger://example.com:7980/carol"))
    assert resolved_obj.host == "example.com"
    assert resolved_obj.port == 7980
    assert resolved_obj.username == "carol"
    assert str(resolved_obj) == "finger://example.com:7980/carol"

    resolved_upper = base.resolve("FINGER://example.com/alice")
    assert resolved_upper.host == "example.com"
    assert resolved_upper.username == "alice"
    assert str(resolved_upper) == "finger://example.com/alice"


##############################################################################
def test_finger_uri_resolve_query_and_verbose() -> None:
    """Test resolving query parameters and verbose switch."""
    base = FingerURI("finger://plan.cat/davep")

    resolved_w = base.resolve("?W")
    assert resolved_w.host == "plan.cat"
    assert resolved_w.username == "davep"
    assert resolved_w.is_verbose
    assert str(resolved_w) == "finger://plan.cat/davep?W"

    resolved_user_w = base.resolve("alice?W")
    assert resolved_user_w.host == "plan.cat"
    assert resolved_user_w.username == "alice"
    assert resolved_user_w.is_verbose
    assert str(resolved_user_w) == "finger://plan.cat/alice?W"

    resolved_sys_w = base.resolve("/?W")
    assert resolved_sys_w.host == "plan.cat"
    assert resolved_sys_w.username is None
    assert resolved_sys_w.is_verbose
    assert str(resolved_sys_w) == "finger://plan.cat/?W"

    base_w = FingerURI("finger://plan.cat/davep?W")
    resolved_from_w = base_w.resolve("alice")
    assert resolved_from_w.host == "plan.cat"
    assert resolved_from_w.username == "alice"
    assert not resolved_from_w.is_verbose
    assert str(resolved_from_w) == "finger://plan.cat/alice"


##############################################################################
def test_finger_uri_resolve_forwarding() -> None:
    """Test resolving forwarding queries."""
    base = FingerURI("finger://plan.cat/davep")

    resolved_fwd = base.resolve("alice@gateway.org")
    assert resolved_fwd.host == "plan.cat"
    assert resolved_fwd.username == "alice"
    assert resolved_fwd.target_host == "gateway.org"
    assert resolved_fwd.is_forwarding_query
    assert resolved_fwd.query_kind == QueryKind.USER_FORWARDING

    resolved_fwd_sys = base.resolve("@gateway.org")
    assert resolved_fwd_sys.host == "plan.cat"
    assert resolved_fwd_sys.username is None
    assert resolved_fwd_sys.target_host == "gateway.org"
    assert resolved_fwd_sys.is_forwarding_query
    assert resolved_fwd_sys.query_kind == QueryKind.FORWARDING


##############################################################################
def test_finger_uri_resolve_errors() -> None:
    """Test that resolving invalid targets raises URIError."""
    base = FingerURI("finger://plan.cat/davep")

    with pytest.raises(URIError, match="Failed to resolve relative URI"):
        base.resolve("http://google.com")

    with pytest.raises(URIError, match="Failed to resolve relative URI"):
        base.resolve("finger://plan.cat:invalid_port/")


### test_uri.py ends here
