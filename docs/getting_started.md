# Getting Started

This guide introduces the primary components of Port79 and demonstrates how to execute Finger requests, parse URIs, and handle errors.

All of the public classes, enumerations, and exceptions are exposed at the top level of the package. You can import them directly from `port79`.

## Core Components

The following classes and enumerations form the core interface of the library:

- **[Client][port79.client.Client]**: The asynchronous client used to configure and dispatch requests over TCP port 79.
- **[Response][port79.response.Response]**: Represents the server's response, exposing the target URI (`uri`), query kind (`query_kind`), decoded response text (`text`), response lines (`lines`), raw bytes (`raw_bytes`), request latency (`latency`), and metadata.
- **[FingerURI][port79.uri.FingerURI]**: A utility class to parse, validate, and manipulate Finger URIs and target strings safely.
- **[QueryKind][port79.query.QueryKind]**: An enumeration representing the RFC 1288 query classifications (`SYSTEM`, `USER`, `FORWARDING`, `USER_FORWARDING`).
- **[Port79Error][port79.exceptions.Port79Error]**: The base exception class for all errors raised by the library.

---

## Basic Request

To execute a request, initialise a [Client][port79.client.Client] and call its [request][port79.client.Client.request] method. The client automatically resolves target host details and executes the network connection:

```python
import asyncio
from port79 import Client, Port79Error

async def main():
    async with Client() as client:
        try:
            # Execute the request (accepts 'user@host' or a FingerURI)
            response = await client.request("davep@plan.cat")

            print(f"Target Host: {response.target_host}")
            print(f"Query Kind:  {response.query_kind.name}")
            print(f"Latency:     {response.latency:.3f}s")
            print("--- Response Body ---")
            print(response.text)

        except Port79Error as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Working with `FingerURI`

The [FingerURI][port79.uri.FingerURI] class allows you to parse both standard URI strings (`finger://plan.cat/davep`) and traditional target format strings (`davep@plan.cat`, `/W davep@plan.cat`, `@plan.cat`):

```python
from port79 import FingerURI

# Parse from a query target string
uri = FingerURI.from_string("/W davep@plan.cat")

print(uri.host)                # 'plan.cat'
print(uri.username)            # 'davep'
print(uri.is_verbose)          # True
print(uri.raw_query)           # '/W davep\r\n'

# FingerURI objects are immutable; construct new instances with updated parts
custom_port_uri = uri.with_port(7979)
system_list_uri = uri.with_username(None)
```

---

## Verbose and System Queries

RFC 1288 supports requesting detailed ("verbose") output using the `/W` switch, as well as system-wide user listings (empty user queries):

```python
async with Client() as client:
    # System query: requests a list of all logged-in users on the host
    system_response = await client.request("plan.cat")
    print(f"Is System Query? {system_response.is_system_query}")

    # Verbose query: requests long-form output from the server
    verbose_response = await client.request("finger://plan.cat/davep?W")
    print(f"Is Verbose? {verbose_response.is_verbose}")
```

---

## Exception Hierarchy

All exceptions raised by the library inherit from the base class [Port79Error][port79.exceptions.Port79Error]. When managing errors, you can catch specific subclasses for finer control:

- **[URIError][port79.exceptions.URIError]**: Raised when a given URI or target string cannot be parsed or validated.
- **[ConnectionError][port79.exceptions.ConnectionError]**: Raised when network connections to the Finger server fail or are refused.
- **[TimeoutError][port79.exceptions.TimeoutError]**: Raised when a Finger query operation times out.
- **[ResponseError][port79.exceptions.ResponseError]**: Raised when processing or parsing response content fails.

---

[//]: # (getting_started.md ends here)
