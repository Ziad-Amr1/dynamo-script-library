# Geometry

Tools for geometry generation, analysis, transformation, and interoperability
that support Revit workflows.

## Belongs here

- Ramp, floor, curb, and other model-geometry generators.
- Coordinate and transform helpers.
- Bounding-box and clearance checks.
- Curve, surface, and solid analysis.
- Geometry export and conversion utilities.
- Placement and alignment calculations.

## Does not belong here

- Model cleanup unrelated to geometry (use `model-management`).
- Family content management (use `families`).
- General list and text helpers (use `utilities`).

## Tool naming

Use a lowercase kebab-case folder id, for example `bounding-box-report`. See the
catalog in the root README for current tools and
[docs/ADDING-A-SCRIPT.md](../../docs/ADDING-A-SCRIPT.md) for the package
standard.
