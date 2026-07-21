"""Unit and integration tests for __main__.py CLI module."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Python imports.
from unittest.mock import AsyncMock, patch

##############################################################################
# Third party imports.
import pytest

##############################################################################
# Local imports.
from port79.__main__ import main, parse_args, run_cli
from tests.conftest import MockFingerServer


##############################################################################
def test_parse_args() -> None:
    """Test argument parsing for CLI parameters."""
    parsed1 = parse_args(["davep@plan.cat"])
    assert parsed1.target == "davep@plan.cat"
    assert not parsed1.verbose
    assert parsed1.port is None
    assert parsed1.timeout == 10.0

    parsed2 = parse_args(["-w", "-p", "7979", "-t", "5.0", "finger://plan.cat/davep"])
    assert parsed2.target == "finger://plan.cat/davep"
    assert parsed2.verbose
    assert parsed2.port == 7979
    assert parsed2.timeout == 5.0


##############################################################################
@pytest.mark.asyncio
async def test_run_cli_success(
    mock_server: MockFingerServer,  # noqa: F811
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test run_cli execution with a mock server."""
    target = f"davep@127.0.0.1:{mock_server.port}"
    exit_code = await run_cli(
        target=target,
        verbose=True,
        port=None,
        timeout=5.0,
    )
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Dave Pearson" in captured.out


##############################################################################
@pytest.mark.asyncio
async def test_run_cli_connection_error(capsys: pytest.CaptureFixture[str]) -> None:
    """Test run_cli reporting connection errors gracefully."""
    exit_code = await run_cli(
        target="davep@127.0.0.1:59998",
        verbose=False,
        port=None,
        timeout=1.0,
    )
    assert exit_code == 1

    captured = capsys.readouterr()
    assert "port79: error:" in captured.err


##############################################################################
def test_main_entry_point(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test main entry point calling sys.exit."""
    with (
        patch("sys.argv", ["port79", "davep@plan.cat"]),
        patch(
            "port79.__main__.run_cli", new_callable=AsyncMock, return_value=0
        ) as mock_run,
        pytest.raises(SystemExit) as exc_info,
    ):
        main()
    assert exc_info.value.code == 0
    mock_run.assert_called_once_with(
        target="davep@plan.cat",
        verbose=False,
        port=None,
        timeout=10.0,
    )


### test_main.py ends here
