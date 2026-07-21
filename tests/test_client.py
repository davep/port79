"""Unit and integration tests for Client class."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Python imports.
import asyncio

import pytest

##############################################################################
# Local imports.
from port79.client import Client
from port79.exceptions import ConnectionError, TimeoutError, URIError
from port79.query import QueryKind
from port79.uri import FingerURI
from tests.conftest import MockFingerServer


##############################################################################
@pytest.mark.asyncio
async def test_client_request_string(mock_server: MockFingerServer) -> None:
    """Test Client.request with a target string."""
    async with Client() as client:
        query_str = f"davep@127.0.0.1:{mock_server.port}"
        response = await client.request(query_str)

        assert response.username == "davep"
        assert response.target_host == "127.0.0.1"
        assert response.query_kind == QueryKind.USER
        assert "Dave Pearson" in response.text
        assert len(response.lines) > 0
        assert response.latency >= 0.0


##############################################################################
@pytest.mark.asyncio
async def test_client_request_finger_uri(mock_server: MockFingerServer) -> None:
    """Test Client.request with a FingerURI instance."""
    uri = FingerURI(f"finger://127.0.0.1:{mock_server.port}/davep?W")
    async with Client() as client:
        response = await client.request(uri)

        assert response.is_verbose
        assert response.username == "davep"
        assert "Dave Pearson" in response.text
        assert mock_server.received_commands[-1] == b"/W davep\r\n"


##############################################################################
@pytest.mark.asyncio
async def test_client_request_system_query(mock_server: MockFingerServer) -> None:
    """Test Client.request with a system user listing query."""
    async with Client() as client:
        query_str = f"127.0.0.1:{mock_server.port}"
        response = await client.request(query_str)

        assert response.is_system_query
        assert response.username is None
        assert "alice" in response.text
        assert "bob" in response.text


##############################################################################
@pytest.mark.asyncio
async def test_client_connection_error() -> None:
    """Test Client.request raising ConnectionError when target port is closed."""
    async with Client() as client:
        with pytest.raises(ConnectionError):
            await client.request("davep@127.0.0.1:59999", timeout=1.0)


##############################################################################
@pytest.mark.asyncio
async def test_client_timeout_error() -> None:
    """Test Client.request raising TimeoutError when server hangs."""

    async def _hanging_handler(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            await reader.read()
        except Exception:
            pass
        finally:
            writer.close()

    server = await asyncio.start_server(_hanging_handler, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]

    try:
        async with Client(timeout=0.1) as client:
            with pytest.raises(TimeoutError):
                await client.request(f"davep@127.0.0.1:{port}")
    finally:
        server.close()
        await server.wait_closed()


##############################################################################
@pytest.mark.asyncio
async def test_client_invalid_query_type() -> None:
    """Test Client.request raising URIError when passed an invalid argument type."""
    async with Client() as client:
        with pytest.raises(URIError):
            await client.request(12345)  # type: ignore[arg-type]


### test_client.py ends here
