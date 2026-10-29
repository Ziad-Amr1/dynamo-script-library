# Changelog

All notable changes to this repository are recorded in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Individual tools keep their own `CHANGELOG.md` inside their tool folder. This
file only describes repository-level changes and coordinated releases.

## [Unreleased]

## [0.1.1] - 2026-10-29

### Fixed

- **Parking Numbering:** Fixed sequential numbering to never consume numbers for skipped stalls; newly numbered stalls strictly start from the configured starting number (e.g. `01`).
- **Parking Numbering:** Replaced axis-aligned bounding-box overlap with 3.5 ft proximity matching to eliminate false-positive conflicts across adjacent angled stalls.
- **Parking Numbering:** Added an explicit, safe renumbering mode (`IN[1]`) allowing in-place updating of existing parking numbers without creating duplicate notes.
- **Parking Numbering:** Centers text notes using local family symbol geometry via `GetTransform()` and parameter offsets, accurately computing physical centers for stalls facing North, West, South, East, and diagonal angles even when insertion origins are at curb edges.
- **Parking Numbering:** Discriminates between numbering notes and unrelated text (e.g. "RESERVED", "EV ONLY") to protect user annotations.

### Added

- Unit tests for geometric center calculation across rotated parking spaces (dimensions 2.3 × 5.0 m, 2.4 × 5.0 m, 2.5 × 5.0 m), sequential numbering with skipped spaces, and renumbering mode.
- Release notes for `v0.1.1` in `docs/releases/v0.1.1.md`.

## [0.1.0] - 2026-10-29

### Added

- Initial repository scaffold with a scalable `scripts/` category structure.
- Script catalog generation, manifest validation, ZIP packaging, and tool
  scaffolding utilities under `tools/`.
- A working reference tool: Text Find & Replace (`scripts/utilities/text-find-replace`).
- Car Ramp Generator (`scripts/geometry/car-ramp-generator`), imported from the
  owner's Revit 2025 graph with the `get_Name()` fix and bilingual docs.
- Parking Numbering (`scripts/documentation/parking-numbering`), an active-view
  text-note numbering workflow with a cleaned single-input graph.
- GitHub Actions for validation, catalog maintenance, package builds, and
  tag-driven releases.
- Beginner-oriented documentation for downloading, adding tools, versioning,
  releasing, and troubleshooting.
- Issue templates, pull request template, security policy, and contribution
  guidelines.

[Unreleased]: https://github.com/Ziad-Amr1/dynamo-script-library/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/Ziad-Amr1/dynamo-script-library/releases/tag/v0.1.1
[0.1.0]: https://github.com/Ziad-Amr1/dynamo-script-library/releases/tag/v0.1.0
