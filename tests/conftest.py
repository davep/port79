"""Pytest test fixtures and helper mock server for port79 tests."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Python imports.
import asyncio
from collections.abc import AsyncGenerator

##############################################################################
# Third party imports.
import pytest_asyncio


##############################################################################
class MockFingerServer:
    """A mock Finger server running on localhost for integration testing."""

    def __init__(self) -> None:
        """Initialise mock server instance."""
        self.server: asyncio.Server | None = None
        """The underlying asyncio Server object."""
        self.port: int = 0
        """The dynamically allocated TCP port."""
        self.received_commands: list[bytes] = []
        """Recorded command bytes received from clients."""

    async def start(self) -> None:
        """Start listening on an ephemeral port."""
        self.server = await asyncio.start_server(
            self._handle_client,
            "127.0.0.1",
            0,
        )
        sockets = self.server.sockets
        assert sockets is not None and len(sockets) > 0
        self.port = sockets[0].getsockname()[1]

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle incoming client connection."""
        data = await reader.readuntil(b"\r\n")
        self.received_commands.append(data)

        if b"/W davep" in data or b"davep" in data:
            response_text = (
                "Login: davep\r\nName: Dave Pearson\r\nPlan:\r\nBuilding port79\r\n"
            )
        else:
            response_text = "Login: alice\r\nLogin: bob\r\n"

        writer.write(response_text.encode("utf-8"))
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def stop(self) -> None:
        """Stop listening and close server."""
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()


##############################################################################
@pytest_asyncio.fixture
async def mock_server() -> AsyncGenerator[MockFingerServer, None]:
    """Pytest fixture providing a running MockFingerServer."""
    server = MockFingerServer()
    await server.start()
    yield server
    await server.stop()


### conftest.py ends here
