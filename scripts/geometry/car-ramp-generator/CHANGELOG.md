# Changelog

All notable changes to Car Ramp Generator are recorded here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this tool follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-29

### Added

- First repository import of the car ramp generator for Revit 2025 and Dynamo 3.
- Dynamo graph with 16 labeled inputs and a Watch output for the report.
- Sloped ramp floors, side curb floors, and an optional center divider for
  two-way ramps.
- Automatic 4000 mm clear lane for service and waste vehicles.
- High-slope transition segments for slopes above 10%.
- Group creation and a text report with measured slope, widths, floor type
  thickness, and overhead clearance target.
- Robust `get_Name()` helper for the Dynamo/Revit `Property cannot be read`
  error, plus `traceback` details on failure.
- Standalone `script.py` copy matching the embedded Python node.
- English and Arabic documentation, plus a graph screenshot.
- `legacy/` folder retaining the earlier graph and Python version for reference.

### Known limitations

- Not yet verified inside a live Revit session; compatibility fields are empty.
- Target environment is Revit 2025, Dynamo 3, and the CPython 3 engine.
- Curb strips are floors, not walls or railings, and the selected floor type
  thickness is not adjusted automatically.
- Overhead clearance is reported only; no beams, ducts, or clash checks are
  performed.
- The 300 mm center divider default must be confirmed against the original
  design draft, which appears to show 500 mm.
- Legacy files are excluded from release packages and are not maintained.

[0.1.0]: https://github.com/Ziad-Amr1/dynamo-script-library/commits/main/scripts/geometry/car-ramp-generator
