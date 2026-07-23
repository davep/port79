# Port79 ChangeLog

## v0.2.0

**Released: 2026-07-23**

- Made `FingerURI` constructor strict so that it requires a valid `finger:`
  URI string. ([#2](https://github.com/davep/port79/pull/2))
- Updated `FingerURI.from_string` to implement permissive parsing for target
  strings (such as `user@host`, `/W user@host`, `@host`).
  ([#2](https://github.com/davep/port79/pull/2))

## v0.1.0

**Released: 2026-07-21**

- Initial version of the library.

## v0.0.1

**Released: 2026-07-21**

- Initial placeholder package to test that the name is available in PyPI.

[//]: # (ChangeLog.md ends here)
