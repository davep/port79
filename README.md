# Port79: Async Finger Protocol Client Library

Port79 is an async-first, fully type-hinted Python client library for the Finger User Information Protocol ([RFC 1288](https://datatracker.ietf.org/doc/html/rfc1288)).

## Features

- **Async First**: Built on top of Python's standard `asyncio` networking loop.
- **RFC 1288 Support**: Full support for standard system queries, user queries, verbose (`/W`) requests, and remote host forwarding.
- **Type Safe**: Fully typed API passing strict static type checking (`mypy --strict`).
- **FingerURI Representation**: Rich URI class to parse, inspect, validate, and manipulate Finger URIs and query targets.
- **Zero Dependencies**: Built entirely on Python's standard library.
- **CLI Utility**: Includes a `port79` command-line interface out of the box.

---

## Installation

`port79` requires Python 3.12 or later and can be installed with your package manager of choice.

With `pip`:

```shell
pip install port79
```

With `uv`:

```shell
uv add port79
```

---

## Quick Start

### 1. Make a Simple Request

Use `Client` with standard async context managers to query a Finger server:

```python
import asyncio
from port79 import Client, Port79Error

async def main():
    async with Client() as client:
        try:
            # Query a user at a target host
            response = await client.request("davep@plan.cat")

            print(f"Target host: {response.target_host}")
            print(f"Query kind: {response.query_kind.name}")
            print(f"Latency: {response.latency:.3f}s")
            print("--- Response Text ---")
            print(response.text)
        except Port79Error as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Working with `FingerURI`

The `FingerURI` class parses both URI strings (`finger://host/user`) and target format strings (`user@host`, `/W user@host`, `@host`):

```python
from port79 import FingerURI

# Parse from email-style target or full URI
uri = FingerURI.from_string("/W davep@plan.cat")

print(uri.host)          # 'plan.cat'
print(uri.username)      # 'davep'
print(uri.is_verbose)    # True
print(uri.raw_query)     # '/W davep\r\n'

# Create modified copies
custom_port_uri = uri.with_port(7979)
system_uri = uri.with_username(None)
```

### 3. Verbose and System Queries

You can issue verbose queries or system-wide logged-in user listings:

```python
async with Client() as client:
    # System query (requests logged-in user list)
    system_response = await client.request("plan.cat")
    assert system_response.is_system_query

    # Verbose user query
    verbose_response = await client.request("finger://plan.cat/davep?W")
    assert verbose_response.is_verbose
```

---

## Command Line Interface (CLI)

`port79` includes a command-line client:

```bash
# Query a user
uv run port79 davep@plan.cat

# Request verbose output
uv run port79 -w davep@plan.cat

# Query system user list on a custom port
uv run port79 -p 7979 plan.cat

# Display CLI help
uv run port79 --help
```

---

## Licence

MIT

[//]: # (README.md ends here)
