# Car Ramp Generator

**Category:** `geometry`  
**Version:** `0.1.0`  
**Status:** Development  
**Target:** Revit 2025 / Dynamo 3 / CPython 3  
**Python engine:** CPython 3

[التوثيق العربي](README.ar.md)

## Overview

Car Ramp Generator creates a sloping vehicle ramp between two Revit levels. It
builds the ramp as one or more sloped floor segments, adds raised floor strips
for the side curbs and, for two-way traffic, a center divider. All created
elements are placed in a group so the result is easy to select and inspect.

The graph is a cleaned-up copy of the user's original car ramp script. The main
entry point includes the `get_Name()` fix for the Dynamo/Revit
`Property cannot be read` error. The earlier version is retained in
[`legacy/`](legacy/README.md) for reference only and is excluded from release
packages.

![Car Ramp Generator Dynamo graph](images/car-ramp-generator.png)

> **Test status:** this tool has **not** been run in a live Revit session. The
> graph structure and JSON were checked, all 16 inputs are connected, and the
> embedded Python matches [`script.py`](script.py). Always test on a copy of
> your model.

## Features

- Creates a ramp between any two levels; the code sorts the levels by elevation.
- Uses a single main slope or, above 10%, two 3000 mm transition segments at half
  the main slope plus a main ramp.
- Creates side curb strips on both sides.
- Creates a center divider for `two-way` ramps.
- Automatically widens the clear lane to 4000 mm for service and waste vehicles.
- Groups the ramp deck and curbs, and names the group from the levels and traffic
  type when Revit accepts the name.
- Returns a text report with the measured slope, total length, widths, selected
  floor types, thickness warnings, and the overhead clearance target.
- Includes a robust element-name helper for CPython 3 and the `get_Name()` fix.
- Rolls back created elements if an error occurs inside the subtransaction.
- No Dynamo packages or external Python packages are required.

## Requirements

| Requirement | Details |
| --- | --- |
| Revit | Targeted at Revit 2025. **Not yet verified in a live Revit session**; test on a copy. |
| Dynamo | The graph was saved with Dynamo `3.0.3.7597` and uses the CPython 3 engine. Not verified against specific Dynamo releases. |
| Python engine | **CPython 3 only.** IronPython 2.7 is not supported or tested. |
| Dynamo packages | None. |
| Other dependencies | At least two levels and one floor type in the project. |

The compatibility arrays in `script.json` are intentionally empty because no
Revit or Dynamo session has confirmed the result yet.

## Installation

### Option A: Open the Dynamo graph

1. Download this folder or the versioned release package. See
   [docs/DOWNLOADING.md](../../../docs/DOWNLOADING.md).
2. Extract it to a permanent location, for example
   `C:\DynamoTools\car-ramp-generator`. Do not run it from inside the ZIP.
3. Open Revit 2025 and go to **Manage > Dynamo**.
4. In Dynamo, choose **File > Open** and select
   `CarRampGenerator_Revit2025.dyn`.
5. Select the Python node and confirm the engine is **CPython 3**. The graph is
   already saved with CPython 3; this is a verification step.
6. No package installation is required.

### Option B: Paste the Python into a Python node

1. In Dynamo, add a **Python Script** node and set it to **CPython 3**.
2. Open [`script.py`](script.py), copy all of it, and paste it into the node.
3. Connect the 16 inputs in the order documented below. The Python node must
   expose exactly 16 input ports, otherwise `IN[15]` and earlier ports will not
   match.

Option A is recommended because the graph already contains the 16 labeled input
nodes, the output Watch node, and the corrected Python code.

## Usage

1. **Back up the model.** Use **Save As** or **File > Save a Copy** before the
   first run.
2. Open `CarRampGenerator_Revit2025.dyn` in Dynamo.
3. In `IN[0]` and `IN[1]`, select the two levels. The order does not matter; the
   higher level becomes the top of the ramp.
4. In `IN[7]` and `IN[9]`, choose the floor type for the ramp deck and for the
   curb strips. If you run `script.py` directly and leave a selector empty, the
   code falls back to the first floor type for the deck and to the type whose
   thickness is closest to the side curb height for the curbs.
5. Set the slope, clear lane width, start point, direction angle, traffic type,
   curb sizes, vehicle class, and overhead clearance target.
6. Review every value, then select **Run**. The graph is configured to run
   manually.
7. Read the report in the Watch node. Confirm the total length, measured slope,
   total width, and selected floor-type thickness before accepting the geometry.
8. Inspect the result in a 3D view and in a section. Check the ramp slope,
   transitions, curb heights, and the underside clearance to beams, ducts, and
   doors.
9. If the result is wrong, use **Undo** or close the model without saving and
   restore the backup.

### Geometry rules used by the script

- `one-way`: total width = clear lane + two side curbs.
- `two-way`: total width = two clear lanes + two side curbs + center divider.
- `service` and `waste`: the clear lane is forced to 4000 mm, even if `IN[3]`
  contains a different value.
- Above 10% main slope: the graph creates a 3000 mm top transition, a main ramp,
  and a 3000 mm bottom transition. Transition slopes are half the main slope.
- Start point `IN[4]`/`IN[5]` is the top, high end, left corner in project
  coordinates. The ramp descends toward the direction angle.
- `0°` runs toward `+X`; `90°` runs toward `+Y`; `180°` runs toward `-X`; `270°`
  runs toward `-Y`.

### Example

| Input | Example value | Effect |
| --- | --- | --- |
| `IN[0]` | `Level 1` | Top level. |
| `IN[1]` | `Parking B1` | Bottom level. |
| `IN[2]` | `15` | 15% main slope. |
| `IN[3]` | `3000` | 3.0 m clear lane for a standard car. |
| `IN[8]` | `one-way` | One clear lane and two side curbs. |
| `IN[10]` | `500` | 500 mm side curb per side. |
| `IN[12]` | `150` | Side curb top raised 150 mm above the deck. |

## Inputs and Outputs

The graph exposes 16 labeled inputs. The defaults below are the values saved in
the `.dyn` file.

| Port | Input | Type | Graph default | Description |
| --- | --- | --- | --- | --- |
| `IN[0]` | Upper level | Level or exact name | required | One of the two levels. Order does not matter. |
| `IN[1]` | Lower level | Level or exact name | required | The other level. The code sorts by elevation. |
| `IN[2]` | Main slope | number, percent | `15` | Greater than 0 and no more than 15. |
| `IN[3]` | Clear lane width | number, mm | `3000` | Clear driving width per lane. Forced to 4000 for service/waste. |
| `IN[4]` | Start X | number, mm | `0` | Project X coordinate of the high-end left corner. |
| `IN[5]` | Start Y | number, mm | `0` | Project Y coordinate of the high-end left corner. |
| `IN[6]` | Direction angle | number, degrees | `0` | Downhill direction. `0` = +X, `90` = +Y. |
| `IN[7]` | Ramp floor type | FloorType or exact name | selector | Floor type for the ramp deck. Empty/omitted falls back to the first floor type. |
| `IN[8]` | Traffic type | string | `two-way` | `one-way` or `two-way`. The Python fallback is `one-way`; the graph default is `two-way`. |
| `IN[9]` | Curb floor type | FloorType or exact name | selector | Floor type for curb strips. Empty/omitted selects the type closest to the side curb height. |
| `IN[10]` | Side curb width | number, mm | `500` | Width of each side curb. |
| `IN[11]` | Center curb width | number, mm | `300` | Center divider width. Used only for `two-way`. |
| `IN[12]` | Side curb height | number, mm | `150` | Height of each side curb's top above the ramp deck. |
| `IN[13]` | Center curb height | number, mm | `100` | Center divider height above the ramp deck. |
| `IN[14]` | Vehicle class | string | `standard` | `standard`, `service`, or `waste`. |
| `IN[15]` | Overhead clearance target | number, mm | `2200` | Reported only. Does not create or check overhead geometry. |

`IN[8]` and `IN[14]` accept a small set of aliases in `script.py` (for example
`two-way`, `twoway`, `2-way`, and `double` for traffic). Use the documented
values unless you have read the source.

| Output | Type | Description |
| --- | --- | --- |
| `OUT[0]` | Revit Group | The group containing the ramp deck and all curb strips. |
| `OUT[1]` | list of strings | Human-readable report lines, including measured slope and thickness warnings. |
| `OUT[2]` | `[X, Y]` | Ramp endpoint in project coordinates, in millimetres. |

The Watch node in the graph displays the returned list. Expand it if only the
group element is visible at first.

## Warnings and Limitations

- **Not tested in Revit.** The graph was validated structurally, not by running
  it against a real project. Test on a copy and inspect the geometry.
- **Revit 2025 only target.** The script uses the Revit API `Floor.Create`
  overload with a slope arrow. Other Revit versions may reject it.
- **CPython 3 only.** Use the CPython 3 engine. The `get_Name()` fix is intended
  for the CPython 3/.NET property behavior in Dynamo.
- **Curb strips are floors, not walls or railings.** The selected curb floor type
  should be thin enough for the intended build-up. The report prints the type
  thickness; it does not resize the type automatically.
- **Curb height is a top-surface offset.** The curb's top is raised above the
  deck by `IN[12]` or `IN[13]`, but the floor type's own thickness may not match
  that height. Check the section.
- **Center divider width conflict.** The original design draft appears to show a
  500 mm center divider, while this script defaults to 300 mm. Confirm the
  required width with the responsible designer or authority.
- **High-slope transitions can fail.** Above 10%, two 3000 mm transitions are
  required. A small level-to-level drop may not leave a positive main-ramp
  length; the script raises an error and rolls back.
- **Overhead clearance is report-only.** `IN[15]` writes a target and a warning
  below 2200 mm. It does not create a ceiling, measure beams or ducts, or run
  clash detection.
- **No railings, walls, drainage, signage, or floor finishes.**
- **The group only contains elements created by this run.** Existing model
  elements are not added.
- **Group names may be rejected.** Revit can refuse a duplicate group type name.
  The group is still created and the report notes the failure.
- **Manual run.** The graph is saved with manual execution. Review the inputs
  before every run.
- **Units.** All numeric inputs are millimetres and degrees. The script converts
  to Revit internal feet internally.
- **Legacy files are not maintained.** Files under `legacy/` show the earlier
  version with the direct `.Name` access that could raise
  `Property cannot be read`. Use the main graph instead.

## Troubleshooting

| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| `Property cannot be read` | The old graph is reading `.Name` directly | Use `CarRampGenerator_Revit2025.dyn` or the `revit_name()` helper in `script.py`. |
| `IN[0]: enter an exact Level name...` | The level is not in the project or the name differs | Select the level in the graph's Levels node or copy the exact Revit name, including spaces. |
| `No Floor Types were found in this project.` | The project has no floor types | Create or load a floor type, then run again. |
| `Main slope must be greater than 0% and no more than 15%.` | Slope is zero, negative, or above 15 | Enter a value such as `10` or `15`. |
| `Height difference ... is too small for two 3000mm transitions...` | High slope plus a small level drop | Reduce the slope or choose levels with a larger elevation difference. |
| `could not find a valid upward planar face` | The floor type or sketch did not produce a usable top face | Try a simple floor type and check that the level is correct. |
| `measured slope ... differs from target` | Revit could not build the requested slope with that type | Try a different floor type and check the level elevations. |
| `floor slopes in the wrong direction` | Direction angle or slope-arrow behavior is unexpected | Check `IN[6]`; try `0`, `90`, `180`, or `270` to confirm the orientation. |
| `created elements were rolled back` | Any error inside the subtransaction | Read the full `Details` and `Traceback` text; the model should not keep partial geometry from this run. |
| Group created but name is wrong | Duplicate group type name or Revit name restriction | Rename the group type in Revit; the geometry is still created. |
| Nothing appears in the Watch node | The Python node failed, or the output is collapsed | Check Dynamo warnings, then expand the Watch node to see all output items. |
| `SyntaxError` or `.NET` errors | The node is using IronPython 2.7 | Switch the Python node to **CPython 3**. |
| Dimensions look 1000 times too large or small | Project units are not millimetres or values were entered in metres | Enter millimetres; the script converts to feet internally. |
| The graph opens but does not run automatically | Manual run mode | Press **Run** in Dynamo. |

If an error persists, copy the complete error text, especially the `Traceback`
lines, and include it with the Revit and Dynamo versions when reporting the
problem.

## Version History

See [CHANGELOG.md](CHANGELOG.md).

| Version | Date | Summary |
| --- | --- | --- |
| `0.1.0` | 2026-10-29 | First repository import. Adds the fixed `get_Name()` version, curl documentation, Arabic documentation, and a legacy folder. |

## License

Part of the Dynamo Script Library, licensed under the
[MIT License](../../../LICENSE). See
[licensing notes](../../../docs/LICENSING.md).

The graph and script were provided by the repository owner for this library.
The `legacy/` folder is retained for reference and history, but it is not part
of the packaged release.
