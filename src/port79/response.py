"""Response class representing Finger query results and protocol metadata."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Python imports.
from functools import cached_property

##############################################################################
# Local imports.
from .query import QueryKind
from .uri import FingerURI


##############################################################################
class Response:
    """Represents a response received from a Finger server."""

    def __init__(
        self,
        uri: FingerURI,
        raw_bytes: bytes,
        *,
        encoding: str = "utf-8",
        latency: float = 0.0,
    ) -> None:
        """Initialise a Response instance.

        Args:
            uri: The FingerURI associated with this response.
            raw_bytes: The raw bytes returned by the Finger server.
            encoding: Text encoding for decoding response bytes (defaults to 'utf-8').
            latency: Request latency in seconds.
        """
        self._uri: FingerURI = uri
        """The FingerURI associated with this response."""

        self._raw_bytes: bytes = raw_bytes
        """The raw bytes received from the Finger server."""

        self._encoding: str = encoding
        """Text encoding used to decode raw bytes."""

        self._latency: float = latency
        """Request latency in seconds."""

    @property
    def uri(self) -> FingerURI:
        """The FingerURI associated with this response."""
        return self._uri

    @property
    def query_kind(self) -> QueryKind:
        """The QueryKind enumeration value representing the request query type."""
        return self._uri.query_kind

    @property
    def is_verbose(self) -> bool:
        """Whether the query was made with the /W verbose switch."""
        return self._uri.is_verbose

    @property
    def is_user_query(self) -> bool:
        """Whether the query was for a specific user."""
        return self._uri.is_user_query

    @property
    def is_system_query(self) -> bool:
        """Whether the query was a system-wide query for logged-in users."""
        return self._uri.is_system_query

    @property
    def is_forwarding_query(self) -> bool:
        """Whether the query involved remote host forwarding."""
        return self._uri.is_forwarding_query

    @property
    def username(self) -> str | None:
        """The username queried, or None for a system query."""
        return self._uri.username

    @property
    def target_host(self) -> str:
        """The target server host to which the query was sent."""
        return self._uri.host

    @property
    def raw_query(self) -> str:
        """The exact formatted Finger protocol command string sent over TCP."""
        return self._uri.raw_query

    @property
    def raw_bytes(self) -> bytes:
        """The raw bytes received from the Finger server."""
        return self._raw_bytes

    @property
    def encoding(self) -> str:
        """The character encoding used to decode the response bytes."""
        return self._encoding

    @property
    def latency(self) -> float:
        """The request round-trip latency in seconds."""
        return self._latency

    @cached_property
    def text(self) -> str:
        """The decoded text content of the response."""
        try:
            return self._raw_bytes.decode(self._encoding)
        except UnicodeDecodeError:
            return self._raw_bytes.decode(self._encoding, errors="replace")

    @cached_property
    def lines(self) -> list[str]:
        """The decoded response text split into lines."""
        return self.text.splitlines()

    def __str__(self) -> str:
        """Return the decoded text response."""
        return self.text

    def __repr__(self) -> str:
        return (
            f"Response(uri={self._uri!r}, query_kind={self.query_kind!r}, "
            f"size={len(self._raw_bytes)}B, latency={self._latency:.3f}s)"
        )


### response.py ends here
