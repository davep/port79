"""Finger URI representation and parsing based on RFC 1288."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Python imports.
from functools import cached_property
from typing import Final, Self
from urllib.parse import (
    unquote,
    urlparse,
    uses_fragment,
    uses_netloc,
    uses_params,
    uses_query,
    uses_relative,
)

##############################################################################
# Local imports.
from .exceptions import URIError
from .query import QueryKind

##############################################################################
FINGER_SCHEME: Final[str] = "finger"
"""The default URL scheme for the Finger protocol."""
FINGER_PREFIX: Final[str] = f"{FINGER_SCHEME}://"
"""The standard prefix for Finger URIs."""
FINGER_DEFAULT_PORT: Final[int] = 79
"""The default TCP network port for the Finger protocol."""


##############################################################################
def _normalise_scheme(uri: str) -> str:
    """Normalise the scheme portion of a URI to lowercase."""
    scheme, separator, rest = uri.partition("://")
    return f"{scheme.lower()}{separator}{rest}" if separator else uri


##############################################################################
class _UnsetType:
    """Sentinel class to distinguish between omitted arguments and None."""


_UNSET: Final[_UnsetType] = _UnsetType()
"""Sentinel value to indicate that an argument has not been provided."""


##############################################################################
class FingerURI:
    """Represents a validated Finger protocol URI."""

    MAXIMUM_LENGTH: Final[int] = 1024
    """The maximum length of a Finger URI string."""

    def __init__(self, uri: str | FingerURI) -> None:
        """Initialise and validate a Finger URI.

        Args:
            uri: The raw URI string, query string, or an existing FingerURI to clone.

        Raises:
            URIError: If the URI is empty, the host is missing or invalid,
                or if parsing of the URI fails.
        """
        self._scheme: str
        """The scheme portion of the URI (always 'finger')."""
        self._host: str
        """The target hostname or IP address."""
        self._port: int
        """The target port number, defaulting to 79."""
        self._username: str | None
        """The username being queried, or None for a system query."""
        self._target_host: str | None
        """The remote target host for forwarding queries, if applicable."""
        self._is_verbose: bool
        """Whether the /W verbose switch is set."""
        self._path: str
        """The path portion of the URI."""
        self._query: str | None
        """The raw query parameters string of the URI, if any."""

        if isinstance(uri, FingerURI):
            self._scheme = uri.scheme
            self._host = uri.host
            self._port = uri.port
            self._username = uri.username
            self._target_host = uri.target_host
            self._is_verbose = uri.is_verbose
            self._path = uri.path
            self._query = uri.query
            return

        if not uri or not uri.strip():
            raise URIError("URI cannot be empty")

        cleaned = uri.strip()
        parsed_uri = self._parse_input_string(cleaned)

        self._scheme = parsed_uri._scheme
        self._host = parsed_uri._host
        self._port = parsed_uri._port
        self._username = parsed_uri._username
        self._target_host = parsed_uri._target_host
        self._is_verbose = parsed_uri._is_verbose
        self._path = parsed_uri._path
        self._query = parsed_uri._query

    @classmethod
    def _parse_input_string(cls, raw: str) -> FingerURI:
        """Parse an input string into a FingerURI instance.

        Args:
            raw: The raw input string to parse.

        Returns:
            A new FingerURI instance.

        Raises:
            URIError: If parsing fails or required fields are missing.
        """
        normalised = _normalise_scheme(raw)

        # Handle full URI form: finger://...
        if normalised.startswith(FINGER_PREFIX) or "://" in normalised:
            return cls._parse_full_uri(normalised)

        # Handle target string form: e.g. "davep@plan.cat", "/W davep@plan.cat", "plan.cat"
        return cls._parse_target_string(raw)

    @classmethod
    def _parse_full_uri(cls, uri_str: str) -> FingerURI:
        """Parse a full URI string with scheme.

        Args:
            uri_str: A URI string starting with a scheme.

        Returns:
            A FingerURI instance.

        Raises:
            URIError: If scheme or host is invalid.
        """
        to_parse = (
            "https://" + uri_str.removeprefix(FINGER_PREFIX)
            if uri_str.startswith(FINGER_PREFIX)
            else uri_str
        )

        try:
            parsed = urlparse(to_parse)
            scheme = parsed.scheme.lower()
            if scheme == "https" and uri_str.startswith(FINGER_PREFIX):
                scheme = FINGER_SCHEME

            if scheme != FINGER_SCHEME:
                raise URIError(
                    f"Invalid URI scheme: '{scheme}'. Expected '{FINGER_SCHEME}'"
                )

            if not parsed.hostname:
                raise URIError("URI host is missing or invalid")

            host = parsed.hostname
            port = parsed.port if parsed.port is not None else FINGER_DEFAULT_PORT
            path = parsed.path or "/"
            query_str = parsed.query if parsed.query else None

            # Determine verbose flag and username from path and query
            is_verbose = False
            username: str | None = None
            target_host: str | None = None

            if query_str and query_str.upper() == "W":
                is_verbose = True

            clean_path = unquote(path).lstrip("/")
            if clean_path:
                parts = clean_path.split("/")
                if parts[0].upper() in ("W", "/W"):
                    is_verbose = True
                    parts = parts[1:]

                if parts:
                    user_token = "/".join(parts)
                    if user_token:
                        username, target_host = cls._extract_user_and_target_host(
                            user_token
                        )

            instance = object.__new__(cls)
            instance._scheme = FINGER_SCHEME
            instance._host = host
            instance._port = port
            instance._username = username
            instance._target_host = target_host
            instance._is_verbose = is_verbose
            instance._path = path
            instance._query = query_str
            return instance
        except URIError:
            raise
        except Exception as e:
            raise URIError(f"Failed to parse URI: {e}") from e

    @classmethod
    def _parse_target_string(cls, target: str) -> FingerURI:
        """Parse a plain target string such as 'user@host' or '/W user@host'.

        Args:
            target: The query target string.

        Returns:
            A FingerURI instance.

        Raises:
            URIError: If the target format is invalid or missing a host.
        """
        cleaned = target.strip()
        is_verbose = False

        if cleaned.upper().startswith("/W"):
            is_verbose = True
            cleaned = cleaned[2:].strip()

        if "@" in cleaned:
            user_part, host_part = cleaned.rsplit("@", 1)
            username = user_part.strip() or None
            host_part = host_part.strip()

            if not host_part:
                raise URIError("URI host is missing or invalid")

            if ":" in host_part:
                host_str, port_str = host_part.split(":", 1)
                try:
                    port = int(port_str)
                except ValueError as e:
                    raise URIError(f"Invalid port number: '{port_str}'") from e
                host = host_str.strip()
            else:
                host = host_part
                port = FINGER_DEFAULT_PORT

            target_host: str | None = None
            if username and "@" in username:
                username, target_host = cls._extract_user_and_target_host(username)

        else:
            # No '@' symbol - target must be a host
            if not cleaned:
                raise URIError("URI host is missing or invalid")

            if ":" in cleaned:
                host_str, port_str = cleaned.split(":", 1)
                try:
                    port = int(port_str)
                except ValueError as e:
                    raise URIError(f"Invalid port number: '{port_str}'") from e
                host = host_str.strip()
            else:
                host = cleaned
                port = FINGER_DEFAULT_PORT

            username = None
            target_host = None

        if not host:
            raise URIError("URI host is missing or invalid")

        path = f"/{username}" if username else "/"
        query_str = "W" if is_verbose else None

        instance = object.__new__(cls)
        instance._scheme = FINGER_SCHEME
        instance._host = host
        instance._port = port
        instance._username = username
        instance._target_host = target_host
        instance._is_verbose = is_verbose
        instance._path = path
        instance._query = query_str
        return instance

    @classmethod
    def _extract_user_and_target_host(cls, token: str) -> tuple[str | None, str | None]:
        """Extract username and target host from a token.

        Args:
            token: The user token to inspect.

        Returns:
            A tuple of (username, target_host).
        """
        if "@" in token:
            user_part, target_part = token.split("@", 1)
            return (user_part.strip() or None, target_part.strip() or None)
        return (token.strip() or None, None)

    _KNOWN_SCHEMES: Final[set[str]] = set(
        scheme
        for scheme in (
            FINGER_SCHEME,
            *uses_netloc,
            *uses_params,
            *uses_relative,
            *uses_query,
            *uses_fragment,
        )
        if scheme
    )
    """Set of known URI schemes for validation."""

    @classmethod
    def with_default_scheme(cls, uri: str) -> Self:
        """Add the Finger scheme to a URI if it is missing.

        Args:
            uri: The URI string to check and potentially modify.

        Returns:
            A new FingerURI instance with the scheme added if missing.

        Raises:
            URIError: If the URI is invalid or missing required components.
        """
        cleaned = uri.strip()
        if cleaned and not cleaned.startswith(FINGER_PREFIX) and "://" not in cleaned:
            cleaned = f"{FINGER_PREFIX}{cleaned}"
        return cls(cleaned)

    @classmethod
    def from_string(cls, target: str) -> Self:
        """Create a FingerURI from a target string or URI.

        Args:
            target: The target string (e.g., 'davep@plan.cat' or 'finger://plan.cat/davep').

        Returns:
            A new FingerURI instance.

        Raises:
            URIError: If parsing fails or required host is missing.
        """
        return cls(target)

    @property
    def scheme(self) -> str:
        """The URI scheme (always 'finger')."""
        return self._scheme

    @property
    def host(self) -> str:
        """The target hostname or IP address."""
        return self._host

    @property
    def port(self) -> int:
        """The target TCP port (defaults to 79)."""
        return self._port

    @property
    def username(self) -> str | None:
        """The username being queried, or None for a system query."""
        return self._username

    @property
    def target_host(self) -> str | None:
        """The remote target host for forwarding queries, if applicable."""
        return self._target_host

    @property
    def is_verbose(self) -> bool:
        """Whether the /W verbose switch is requested."""
        return self._is_verbose

    @property
    def path(self) -> str:
        """The path portion of the URI."""
        return self._path

    @property
    def query(self) -> str | None:
        """The raw query parameter string of the URI, or None."""
        return self._query

    @property
    def is_user_query(self) -> bool:
        """Whether this is a query for a specific user."""
        return self._username is not None

    @property
    def is_system_query(self) -> bool:
        """Whether this is a system-wide query for logged-in users."""
        return self._username is None

    @property
    def is_forwarding_query(self) -> bool:
        """Whether this query involves remote host forwarding."""
        return self._target_host is not None

    @property
    def query_kind(self) -> QueryKind:
        """The QueryKind enumeration value representing this query type."""
        if self.is_forwarding_query:
            return (
                QueryKind.USER_FORWARDING
                if self.is_user_query
                else QueryKind.FORWARDING
            )
        return QueryKind.USER if self.is_user_query else QueryKind.SYSTEM

    @property
    def raw_query(self) -> str:
        """The formatted Finger command string including CRLF sequence."""
        prefix = "/W " if self._is_verbose else ""
        if self._target_host:
            user = self._username or ""
            return f"{prefix}{user}@{self._target_host}\r\n"
        if self._username:
            return f"{prefix}{self._username}\r\n"
        return "/W\r\n" if self._is_verbose else "\r\n"

    def replace(
        self,
        *,
        host: str | _UnsetType = _UNSET,
        port: int | _UnsetType = _UNSET,
        username: str | None | _UnsetType = _UNSET,
        target_host: str | None | _UnsetType = _UNSET,
        is_verbose: bool | _UnsetType = _UNSET,
        path: str | None | _UnsetType = _UNSET,
        query: str | None | _UnsetType = _UNSET,
    ) -> Self:
        """Create a new FingerURI by replacing specific parts of this URI.

        Args:
            host: The new hostname, or _UNSET to keep current host.
            port: The new port number, or _UNSET to keep current port.
            username: The new username, None to clear, or _UNSET to keep current.
            target_host: The new target host for forwarding, None to clear, or _UNSET.
            is_verbose: The new verbose status, or _UNSET to keep current.
            path: The new path, or _UNSET to derive from username/verbose.
            query: The new query string, or _UNSET to derive from verbose.

        Returns:
            A new FingerURI instance with updated components.

        Raises:
            URIError: If the resulting URI components are invalid.
        """
        new_host = self._host if isinstance(host, _UnsetType) else host
        new_port = self._port if isinstance(port, _UnsetType) else port
        new_username = self._username if isinstance(username, _UnsetType) else username
        new_target_host = (
            self._target_host if isinstance(target_host, _UnsetType) else target_host
        )
        new_verbose = (
            self._is_verbose if isinstance(is_verbose, _UnsetType) else is_verbose
        )

        if not new_host:
            raise URIError("URI host cannot be empty")

        port_str = f":{new_port}" if new_port != FINGER_DEFAULT_PORT else ""
        user_str = f"/{new_username}" if new_username else "/"
        if new_target_host:
            user_str = f"/{new_username or ''}@{new_target_host}"

        query_str = "?W" if new_verbose else ""
        new_uri_str = f"{FINGER_PREFIX}{new_host}{port_str}{user_str}{query_str}"
        return self.__class__(new_uri_str)

    def with_host(self, host: str) -> Self:
        """Return a new FingerURI with the host replaced.

        Args:
            host: The new target hostname.

        Returns:
            A new FingerURI instance with the updated host.

        Raises:
            URIError: If the resulting host is invalid or empty.
        """
        return self.replace(host=host)

    def with_port(self, port: int) -> Self:
        """Return a new FingerURI with the port replaced.

        Args:
            port: The new target TCP port number.

        Returns:
            A new FingerURI instance with the updated port.

        Raises:
            URIError: If the resulting port is invalid.
        """
        return self.replace(port=port)

    def with_username(self, username: str | None) -> Self:
        """Return a new FingerURI with the username replaced or cleared.

        Args:
            username: The new username, or None to convert to a system query.

        Returns:
            A new FingerURI instance with the updated username.
        """
        return self.replace(username=username)

    def with_verbose(self, verbose: bool = True) -> Self:
        """Return a new FingerURI with the verbose switch updated.

        Args:
            verbose: True to enable verbose mode, False to disable.

        Returns:
            A new FingerURI instance with updated verbose setting.
        """
        return self.replace(is_verbose=verbose)

    @cached_property
    def bytes_left(self) -> int:
        """The number of characters remaining before reaching maximum URI length."""
        return max(0, self.MAXIMUM_LENGTH - len(self))

    @cached_property
    def is_too_long(self) -> bool:
        """Whether the URI string length exceeds the maximum allowed length."""
        return len(self) > self.MAXIMUM_LENGTH

    def __str__(self) -> str:
        """Return the string representation of the URI."""
        port_str = f":{self._port}" if self._port != FINGER_DEFAULT_PORT else ""
        user_part = f"/{self._username}" if self._username else "/"
        if self._target_host:
            user_part = f"/{self._username or ''}@{self._target_host}"
        query_part = "?W" if self._is_verbose else ""
        return f"{FINGER_PREFIX}{self._host}{port_str}{user_part}{query_part}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self}')"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            try:
                other = FingerURI(other)
            except URIError:
                return False
        if not isinstance(other, FingerURI):
            return NotImplemented
        return (
            self.scheme == other.scheme
            and self.host == other.host
            and self.port == other.port
            and self.username == other.username
            and self.target_host == other.target_host
            and self.is_verbose == other.is_verbose
        )

    def __hash__(self) -> int:
        """Return the hash value of the URI."""
        return hash(
            (
                self._scheme,
                self._host,
                self._port,
                self._username,
                self._target_host,
                self._is_verbose,
            )
        )

    def __len__(self) -> int:
        """Return the length of the string representation of the URI."""
        return len(str(self))


### uri.py ends here
