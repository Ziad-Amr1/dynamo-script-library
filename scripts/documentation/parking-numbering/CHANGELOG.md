# Changelog

All notable changes to Parking Numbering are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this tool follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-10-29

### Fixed

- **Sequential numbering without gap consumption:** When existing spaces are skipped, sequential number allocation is not advanced; newly numbered spaces start strictly from the configured starting number (e.g. `01`).
- **Angled bay label association:** Associates existing numbering notes via proximity to each stall center (3.5 ft radius), eliminating false-positive overlaps caused by axis-aligned bounding boxes on adjacent angled stalls.
- **Geometric center placement:** Centers the number using transformed bounding-box corners (with safe fallbacks), improving placement for rotated/oriented parking spaces and varying dimensions.
- **Safe renumbering mode:** Added an explicit renumbering toggle (`IN[1]`). When `True`, existing numbering notes are updated in-place starting from the chosen start number without creating duplicate notes. When `False` (safe mode), stalls with existing numbering notes are preserved.
- **Protection of unrelated annotations:** Unrelated descriptive text (e.g. "RESERVED", "EV ONLY") is never matched as a parking label and is never modified, overwritten, or deleted.

### Changed

- Added `IN[1]` (`Renumber existing labels`, boolean) to `ParkingNumbering.dyn` and `script.py`.
- Summary now includes `TextNotesCreated`, `TextNotesUpdated`, `TotalNumbered`, `SkippedExistingText`, `ExistingTextConflicts`, `StartNumber`, and `RenumberExisting`.
- Output tuple returns `(numbered_notes, errors, no_location, summary)`.
- README updated with placement, duplicate prevention, and safe-handling guidance.

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
- Row order uses model X/Y, so rotated views may not match the visual order.
- Successful notes remain if a later note fails; errors are returned per item.
- If existing text notes overlap a parking space, placement is skipped (non-destructive). User annotations are never deleted/moved.

[Unreleased]: https://github.com/Ziad-Amr1/dynamo-script-library/compare/parking-numbering-v0.1.1...HEAD
[0.1.1]: https://github.com/Ziad-Amr1/dynamo-script-library/releases/tag/parking-numbering-v0.1.1
[0.1.0]: https://github.com/Ziad-Amr1/dynamo-script-library/releases/tag/parking-numbering-v0.1.0
