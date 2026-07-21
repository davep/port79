# Agent Instructions for Port79

Port79 is an async-first, fully type-hinted client library and command-line interface for the Finger User Information Protocol ([RFC 1288](https://datatracker.ietf.org/doc/html/rfc1288)).

---

## Architecture Overview

- **[`port79.client`][port79.client]**: Contains [`Client`][port79.client.Client], the main asynchronous client interface for executing Finger queries over TCP (port 79). Supports async context management (`async with Client() as client:`).
- **[`port79.uri`][port79.uri]**: Contains [`FingerURI`][port79.uri.FingerURI], representing validated Finger protocol URIs (`finger://host/user`) and target format strings (`user@host`, `/W user@host`, `@host`). Provides immutable modification methods (`with_host`, `with_port`, `with_username`, `with_verbose`, `replace`).
- **[`port79.query`][port79.query]**: Defines the [`QueryKind`][port79.query.QueryKind] enumeration (`SYSTEM`, `USER`, `FORWARDING`, `USER_FORWARDING`) matching RFC 1288 query classifications.
- **[`port79.response`][port79.response]**: Contains [`Response`][port79.response.Response], encapsulating server response text, lines, raw bytes, latency, and query metadata.
- **[`port79.exceptions`][port79.exceptions]**: Exception hierarchy rooted at [`Port79Error`][port79.exceptions.Port79Error], including [`URIError`][port79.exceptions.URIError], [`ConnectionError`][port79.exceptions.ConnectionError], [`TimeoutError`][port79.exceptions.TimeoutError], and [`ResponseError`][port79.exceptions.ResponseError].
- **[`port79.__main__`][port79.__main__]**: Entry point for the `port79` command-line client (`main()`).

---

## Code Style & Guidelines

- **Python Version Target**: Target Python 3.12+ (specified via `requires-python = ">=3.12"`). Favour modern Python syntax including union types (`X | Y`), `Self`, `TypeAlias`, and `collections.abc` generic imports.
- **Type Hints**: Always write strict type hints that pass `mypy --strict`. Avoid using `Any` or `any`; prefer structural protocols or explicit union types.
- **Docstrings**: Write complete Google-style docstrings for every module, class, method, function, and attribute.
  - Do *not* include type annotations in docstring parameter text.
  - Docstrings always start on the same line as the opening triple quote (`"""Summary.`).
  - The closing triple quote is on its own line for multi-line docstrings (`"""`).
  - Document all file-wide types, module-level constants, and instance attributes established via `__init__` with a clear one-line docstring immediately following assignment/definition (e.g. `self._host = host\n"""The target hostname."""`).
  - Cross-references should use mkdocstrings-compatible Markdown formatting (e.g. ``[`FingerURI`][port79.uri.FingerURI]``).
- **Descriptive Naming**: Use full, clear, descriptive names for all classes, methods, functions, parameters, and variables. Avoid cryptic abbreviations.
- **Language**: Use British English for all documentation, docstrings, variable names, comments, and messages (e.g. `normalise`, `initialise`, `behaviour`, `licence`).
- **Modularisation**: Keep modules focused and concise. Put shared test fixtures and mock servers in `tests/conftest.py`.

---

## Development Workflow & Commands

We use `uv` for environment, locking, and dependency management.

- **Dependencies**: Never edit dependency lists in [`pyproject.toml`](pyproject.toml) manually. Always use `uv add <dependency>` or `uv remove <dependency>`.
- **Environment Sync**: Keep [`uv.lock`](uv.lock) updated. Run `uv sync` after modifying dependencies.
- **Canonical Interface**: The [`Makefile`](Makefile) provides standard commands for development and maintenance:
  - `make setup`: Set up local virtual environment and install dev/test dependencies.
  - `make lint`: Run `ruff check` on `src/` and `tests/`.
  - `make codestyle`: Check code formatting with `ruff format --check`.
  - `make stricttypecheck`: Run `mypy --scripts-are-modules --strict` on `src/` and `tests/`.
  - `make test`: Run pytest suite with coverage reporting.
  - `make spellcheck`: Run `codespell` on markdown files, `src/`, `docs/`, and `tests/`.
  - `make checkall`: Execute all checks (`spellcheck`, `codestyle`, `lint`, `stricttypecheck`, `test`). **Always run `make checkall` before committing changes.**
  - `make tidy`: Automatically fix lint issues and reformat code (`ruff check --fix` and `ruff format`).

---

## Testing Guidelines

- Unit and integration tests reside in the [`tests/`](tests/) directory.
- Use `pytest` and `pytest-asyncio` for asynchronous test cases.
- Use `MockFingerServer` in `tests/conftest.py` (`asyncio.start_server`) to simulate server responses for network testing without relying on external services.
- Maintain test coverage at 90%+ across all modules.

---

[//]: # (AGENTS.md ends here)
