# Changelog

All notable changes to Parking Numbering are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this tool follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-29

### Added

- First repository import of the active-view parking numbering graph.
- Collects parking elements visible in the active view.
- Groups elements into rows, sorts top-to-bottom and left-to-right, and numbers
  them from a chosen starting value.
- Creates centered text notes using the default text note type, with a 150 mm
  text size when the parameter is writable.
- Returns created notes, per-element errors, parking without a location, and a
  summary dictionary.
- Standalone `script.py` copy matching the embedded Python node.
- Documentation for inputs, outputs, behavior, and known limitations.
- `legacy/` copy of the original graph for reference.

### Changed

- Removed the unused Boolean input from the maintained graph.
- Renumbered the start-number port from `IN[1]` to `IN[0]`.
- Made the start-number input visible on the Dynamo canvas.

### Known limitations

- Not yet verified inside a live Revit session; compatibility fields are empty.
- Target environment is Revit 2025, Dynamo 3, and the CPython 3 engine.
- The tool creates text notes only; it does not write parking parameters or
  create tags.
- Re-running the graph creates duplicate notes; no cleanup is performed.
- Row order uses model X/Y, so rotated views may not match the visual order.
- Successful notes remain if a later note fails; errors are returned per item.

[0.1.0]: https://github.com/Ziad-Amr1/dynamo-script-library/commits/main/scripts/documentation/parking-numbering
