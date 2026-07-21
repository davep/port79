# Port79: Async Finger Protocol Client Library

Port79 is an asynchronous, object-oriented, fully type-hinted client library for the Finger User Information Protocol ([RFC 1288](https://datatracker.ietf.org/doc/html/rfc1288)). It is designed to target Python 3.12 and later, relying entirely on the Python standard library.

Features of the library:

- **Asynchronous throughout**: Built on top of standard `asyncio` for non-blocking I/O.
- **Strictly typed**: Complete type safety utilising modern Python standards, strictly avoiding `Any`.
- **RFC 1288 Compliant**: Native support for standard system listings, user queries, verbose (`/W`) requests, and remote host forwarding.
- **FingerURI representation**: Powerful object-oriented representation to parse, validate, and manipulate Finger URIs and query target strings.
- **Zero dependencies**: Relies only on Python's standard library.
- **CLI utility**: Includes a command-line interface out of the box.

## Installation

You can install Port79 in your environment. The recommended tool for modern Python projects is `uv`, but standard `pip` is also fully supported.

### Using uv

To add Port79 to your project as a dependency:

```bash
uv add port79
```

To install Port79 directly into your active virtual environment:

```bash
uv pip install port79
```

To run the Port79 command-line interface without installing it globally:

```bash
uvx port79 davep@plan.cat
```

### Using pip

To install Port79 from PyPI using standard packaging tools:

```bash
pip install port79
```

[//]: # (index.md ends here)
