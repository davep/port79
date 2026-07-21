"""Command-line interface entry point for the port79 Finger client."""

##############################################################################
# Future imports.
from __future__ import annotations

##############################################################################
# Python imports.
import argparse
import asyncio
import sys
from collections.abc import Sequence

##############################################################################
# Local imports.
from .client import DEFAULT_TIMEOUT, Client
from .exceptions import ConnectionError, Port79Error, TimeoutError, URIError
from .uri import FingerURI


##############################################################################
def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Sequence of command-line argument strings, or None for sys.argv[1:].

    Returns:
        The parsed Namespace object.
    """
    parser = argparse.ArgumentParser(
        prog="port79",
        description="Async Finger protocol client (RFC 1288).",
    )
    parser.add_argument(
        "target",
        help="Target query string (e.g. davep@plan.cat, finger://plan.cat/davep, or plan.cat).",
    )
    parser.add_argument(
        "-w",
        "--verbose",
        action="store_true",
        help="Request verbose/detailed output from the Finger server.",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=None,
        help="Override TCP port number (defaults to port in URI or 79).",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Network timeout in seconds (default: 10.0).",
    )
    return parser.parse_args(args)


##############################################################################
async def run_cli(
    target: str,
    verbose: bool,
    port: int | None,
    timeout: float,
) -> int:
    """Execute the Finger CLI request asynchronously.

    Args:
        target: Target query string.
        verbose: True to request verbose output.
        port: Optional TCP port override.
        timeout: Network timeout in seconds.

    Returns:
        Exit code integer (0 for success, 1 for error).
    """
    try:
        uri = FingerURI.from_string(target)
        if verbose:
            uri = uri.with_verbose(True)
        if port is not None:
            uri = uri.with_port(port)

        async with Client(timeout=timeout) as client:
            response = await client.request(uri)
            sys.stdout.write(response.text)
            if response.text and not response.text.endswith("\n"):
                sys.stdout.write("\n")
            sys.stdout.flush()
            return 0
    except (URIError, ConnectionError, TimeoutError, Port79Error) as e:
        sys.stderr.write(f"port79: error: {e}\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"port79: unexpected error: {e}\n")
        return 1


##############################################################################
def main(args: Sequence[str] | None = None) -> None:
    """Main entry point for the port79 command-line client.

    Args:
        args: Sequence of command-line argument strings, or None for sys.argv[1:].
    """
    parsed = parse_args(args)
    try:
        exit_code = asyncio.run(
            run_cli(
                target=parsed.target,
                verbose=parsed.verbose,
                port=parsed.port,
                timeout=parsed.timeout,
            )
        )
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.stderr.write("\nport79: interrupted\n")
        sys.exit(130)


##############################################################################
if __name__ == "__main__":
    main()

### __main__.py ends here
