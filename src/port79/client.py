"""Async Finger protocol client implementation."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Python imports.
import asyncio
import builtins
import time
from typing import Final, Self

##############################################################################
# Local imports.
from .exceptions import ConnectionError, TimeoutError, URIError
from .response import Response
from .uri import FingerURI

##############################################################################
DEFAULT_TIMEOUT: Final[float] = 10.0
"""Default timeout in seconds for Finger network operations."""


##############################################################################
class Client:
    """An asynchronous client for the Finger protocol (RFC 1288)."""

    def __init__(
        self,
        *,
        timeout: float | None = DEFAULT_TIMEOUT,
        encoding: str = "utf-8",
    ) -> None:
        """Initialise a Finger client instance.

        Args:
            timeout: Default timeout in seconds for requests, or None for no timeout.
            encoding: Default character encoding for response text.
        """
        self._timeout: float | None = timeout
        """Default timeout in seconds for network operations."""

        self._encoding: str = encoding
        """Default text encoding for decoding responses."""

    @property
    def timeout(self) -> float | None:
        """The default timeout in seconds for requests."""
        return self._timeout

    @property
    def encoding(self) -> str:
        """The default character encoding for decoding responses."""
        return self._encoding

    async def request(
        self,
        query: str | FingerURI,
        *,
        timeout: float | None = None,
        encoding: str | None = None,
    ) -> Response:
        """Send a Finger query request to a server.

        Args:
            query: Either a query target string (e.g. 'davep@plan.cat') or a FingerURI.
            timeout: Optional timeout override in seconds for this request.
            encoding: Optional character encoding override for decoding the response.

        Returns:
            A Response instance containing the server output and query metadata.

        Raises:
            URIError: If the query string cannot be parsed as a valid Finger URI.
            ConnectionError: If network connection to the server fails.
            TimeoutError: If the request times out.
        """
        if isinstance(query, FingerURI):
            finger_uri = query
        elif isinstance(query, str):
            finger_uri = FingerURI.from_string(query)
        else:
            raise URIError(f"Expected str or FingerURI, got {type(query).__name__}")

        effective_timeout = timeout if timeout is not None else self._timeout
        effective_encoding = encoding if encoding is not None else self._encoding

        host = finger_uri.host
        port = finger_uri.port
        command_bytes = finger_uri.raw_query.encode("ascii")

        start_time = time.monotonic()
        try:
            if effective_timeout is not None:
                async with asyncio.timeout(effective_timeout):
                    raw_bytes = await self._send_and_receive(host, port, command_bytes)
            else:
                raw_bytes = await self._send_and_receive(host, port, command_bytes)
        except TimeoutError:
            raise
        except builtins.TimeoutError as e:
            raise TimeoutError(
                f"Finger query to {host}:{port} timed out after {effective_timeout}s"
            ) from e
        except OSError as e:
            raise ConnectionError(
                f"Failed to connect to Finger server at {host}:{port}: {e}"
            ) from e

        latency = time.monotonic() - start_time

        return Response(
            uri=finger_uri,
            raw_bytes=raw_bytes,
            encoding=effective_encoding,
            latency=latency,
        )

    async def _send_and_receive(
        self,
        host: str,
        port: int,
        command_bytes: bytes,
    ) -> bytes:
        """Connect to the server, send command bytes, and read response bytes.

        Args:
            host: Target hostname or IP address.
            port: Target TCP port.
            command_bytes: Encoded command string to send.

        Returns:
            The raw bytes returned by the server.
        """
        reader, writer = await asyncio.open_connection(host, port)
        try:
            writer.write(command_bytes)
            await writer.drain()
            return await reader.read()
        finally:
            writer.close()
            try:
                async with asyncio.timeout(0.5):
                    await writer.wait_closed()
            except Exception:
                pass

    async def __aenter__(self) -> Self:
        """Enter the async context manager block.

        Returns:
            The Client instance itself.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit the async context manager block."""
        pass


### client.py ends here
