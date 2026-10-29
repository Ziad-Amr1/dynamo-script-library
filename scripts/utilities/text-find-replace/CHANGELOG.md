# Changelog

All notable changes to Text Find & Replace are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this tool follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-29

### Added

- Initial development version.
- Literal and regular-expression find-and-replace.
- Case-sensitive, case-insensitive, and whole-value matching modes.
- `plan_changes` helper for previewing changed values.
- Dynamo `IN`/`OUT` adapter compatible with the CPython 3 engine.
- Unit tests for pure Python behavior.

### Known limitations

- Not yet verified inside Revit or Dynamo; compatibility fields are empty.
- IronPython 2.7 is not supported.

[0.1.0]: https://github.com/Ziad-Amr1/dynamo-script-library/commits/main/scripts/utilities/text-find-replace
