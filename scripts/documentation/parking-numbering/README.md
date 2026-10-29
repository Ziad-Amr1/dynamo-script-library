# Parking Numbering

**Category:** `documentation`  
**Version:** `0.1.0`  
**Status:** Development  
**Target:** Revit 2025 / Dynamo 3 / CPython 3  
**Python engine:** CPython 3

## Overview

Parking Numbering places centered text notes on the parking elements visible in
the active view. It groups the parking elements into rows, sorts each row from
left to right, numbers the rows from top to bottom, and starts from a number you
choose.

The graph is a cleaned-up copy of the owner's `number_active_view_start_number`
graph. The unused Boolean input was removed, the start-number input is now
`IN[0]` and visible on the canvas, and the original file is retained in
[`legacy/`](legacy/README.md) for reference only.

> **Test status:** this tool has not been run in a live Revit session. The graph
> structure, all connectors, and the embedded Python were checked, but the
> result still needs testing on a copy of a real model.

## Features

- Collects parking elements visible in the active view.
- Uses the view-specific bounding-box center of each parking element, not the
  family origin.
- Sorts rows from top to bottom and each row from left to right.
- Groups parking elements into rows using a fixed 1 foot (about 304.8 mm)
  vertical tolerance.
- Starts numbering at any integer supplied through the graph.
- Formats numbers with at least two digits: `01`, `02`, ..., `99`, `100`.
- Creates centered, horizontal text notes using the project's default text note
  type.
- Sets the text size to 150 mm when the size parameter is writable.
- Returns created notes, per-element errors, parking without a bounding box, and
  a summary dictionary.
- Skips parking elements without a usable bounding box instead of stopping the
  whole run.
- No Dynamo packages or external Python packages are required.

## Requirements

| Requirement | Details |
| --- | --- |
| Revit | Targeted at Revit 2025. **Not yet verified in a live Revit session**; test on a copy. |
| Dynamo | The graph was saved with Dynamo `3.0.3.7597` and uses the CPython 3 engine. Not verified against specific Dynamo releases. |
| Python engine | **CPython 3 only.** IronPython 2.7 is not supported or tested. |
| Dynamo packages | None. |
| Other dependencies | An active view that supports text notes, at least one parking element visible in that view, and a default text note type. |

The compatibility arrays in `script.json` are intentionally empty because no
Revit or Dynamo session has confirmed the result yet.

## Installation

### Option A: Open the Dynamo graph

1. Download this folder or the versioned release package. See
   [docs/DOWNLOADING.md](../../../docs/DOWNLOADING.md).
2. Extract it to a permanent location, for example
   `C:\DynamoTools\parking-numbering`. Do not run it from inside the ZIP.
3. Open Revit 2025 and go to **Manage > Dynamo**.
4. In Dynamo, choose **File > Open** and select `ParkingNumbering.dyn`.
5. Select the Python node and confirm the engine is **CPython 3**. The graph is
   already saved with CPython 3; this is a verification step.
6. No package installation is required.

### Option B: Paste the Python into a Python node

1. In Dynamo, add a **Python Script** node and set it to **CPython 3**.
2. Open [`script.py`](script.py), copy all of it, and paste it into the node.
3. Connect one number input to `IN[0]`. This is the starting number. The graph
   provides a visible **Start number** node with a default of `1`.

Option A is recommended because the graph already contains the start-number
input, the Python node, and the Watch output.

## Usage

1. **Back up the model.** Use **Save As** or **File > Save a Copy** before the
   first run.
2. Open the plan or section view that contains the parking elements and make it
   the **active view** in Revit.
3. Open `ParkingNumbering.dyn` in Dynamo.
4. Set the **Start number** node. For example, `1` produces `01`, `02`, ...;
   `25` produces `25`, `26`, ...
5. Select **Run**. The graph is configured to run manually.
6. Read the Watch output. It returns four items:
   - created text-note records,
   - per-parking errors,
   - parking element IDs without a bounding box,
   - a summary dictionary.
7. Inspect the text notes in the view. Check row order, left-to-right order, and
   text size.
8. If the result is wrong, use **Undo** or close the model without saving and
   restore the backup.

### Numbering order

1. The active view is filtered for the `OST_Parking` category.
2. Each parking element's center is calculated from its bounding box in that
   view.
3. Parking elements are sorted by model Y from highest to lowest.
4. Elements whose Y values differ by 1 foot or less are treated as one row.
5. Each row is sorted by model X from lowest to highest.
6. Rows are numbered in order, and each row is numbered left to right.

The sort uses the model's X/Y axes, not the rotated orientation of the view. A
rotated view can therefore produce a different visual order than expected. See
[Warnings and Limitations](#warnings-and-limitations).

### Example

| Input | Value | Result |
| --- | --- | --- |
| Start number | `1` | `01`, `02`, `03`, ... |
| Start number | `25` | `25`, `26`, `27`, ... |
| Start number | `100` | `100`, `101`, `102`, ... |

The text-note size is fixed at 150 mm in the script. Change `TEXT_SIZE_MM` near
the top of [`script.py`](script.py) if the project requires another size.

## Inputs and Outputs

The cleaned graph has exactly one input port.

| Port | Input | Type | Graph default | Description |
| --- | --- | --- | --- | --- |
| `IN[0]` | Start number | number | `1` | First number in the sequence. It is rounded to the nearest integer. A missing or non-numeric value falls back to `1`. |

The original graph used a second port (`IN[1]`) and an unused Boolean node. Both
were removed in the maintained version; see [`legacy/`](legacy/README.md).

| Output | Type | Description |
| --- | --- | --- |
| `OUT[0]` | list of dictionaries | One record for each created text note: `ParkingId`, `Number`, `TextNoteId`, `X`, `Y`. |
| `OUT[1]` | list of dictionaries | One record for each failed parking element: `ParkingId`, `Number`, `Error`. |
| `OUT[2]` | list of integers | Parking element IDs that had no usable bounding box in the active view. |
| `OUT[3]` | dictionary | Summary with `ParkingFound`, `ParkingWithLocation`, `RowsDetected`, `TextNotesCreated`, `NoLocation`, `Errors`, and `ActiveView`. |

`X` and `Y` in the created-note records are Revit internal units (feet), not
millimetres. The text-note position itself is correct in the view.

The Watch node displays the four-item output tuple. Expand it to inspect the
summary and the error lists.

## Warnings and Limitations

- **Not tested in Revit.** The graph was validated structurally, not by running
  it against a real model. Test on a copy and inspect the notes.
- **Text notes are annotations, not parking parameters.** The tool does not
  write a number into the parking element's properties and does not create
  Revit tags.
- **Running the tool twice creates duplicate notes.** There is no check for
  existing text notes and no cleanup step. Delete the previous notes or undo
  before running again.
- **The notes do not follow the parking elements.** They are independent text
  notes. Moving or deleting a parking element does not move or delete its note.
- **Row detection is fixed.** Rows are grouped with a 1 foot tolerance
  (`ROW_TOLERANCE = 1.0`) and ordered top-to-bottom (`ROWS_TOP_TO_BOTTOM =
  True`). These are constants in the script, not graph inputs.
- **View rotation is not considered.** Ordering uses model X/Y. A rotated view
  may show a different visual order.
- **The text type and size are fixed.** The script uses the default text note
  type and a 150 mm text size. If the text-size parameter is read-only, the
  default size remains.
- **Partial success is possible.** Each text note is wrapped in its own error
  handler. Notes created before an error remain in the model, and the error is
  reported in `OUT[1]`. The graph does not roll back successful notes.
- **Parking without a bounding box is skipped.** Its element ID is returned in
  `OUT[2]`.
- **The start number is not range-checked.** Zero and negative numbers are
  accepted; negative values may produce unexpected labels. Use a positive start
  number.
- **The active view must support text notes.** A 3D view or a view type that does
  not allow annotation may fail for every parking element.
- **Only the `OST_Parking` category is processed.** Generic model families or
  other categories are ignored even if they look like parking spaces.
- **Element centers come from the bounding box.** Irregular or nested families
  can produce a center that is not the visual center of the parking bay.
- **Units.** The start number is unitless. Text size is set from millimetres, and
  row tolerance uses Revit feet internally.
- **No grouping, no numbering schedule, and no automatic view creation.** This
  tool only creates text notes in the active view.

## Troubleshooting

| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| No text notes are created | The active view has no visible `OST_Parking` elements, or the view does not allow text notes | Activate the correct plan or section view and confirm the parking category is visible. |
| `ParkingFound` is greater than `TextNotesCreated` | Some notes failed or parking elements had no bounding box | Inspect `OUT[1]` and `OUT[2]` in the Watch node. |
| Numbers are in the wrong order | The view is rotated, or the rows use a different visual axis | Check the model X/Y orientation. The ordering constants are in `script.py`. |
| Rows are merged or split incorrectly | The 1 foot row tolerance does not match the layout | Adjust `ROW_TOLERANCE` in `script.py` and update the Python node in the graph. |
| Duplicate numbers or duplicate notes | The graph was run more than once without cleanup | Undo the previous run or delete the old text notes, then run again. |
| Text is too small or too large | The project text size differs from 150 mm | Change `TEXT_SIZE_MM` in `script.py` and update the graph's Python node. |
| Notes appear away from the parking bay center | The family's bounding box is irregular | Check the family geometry; the script uses the bounding-box center, not the family origin. |
| `NameError` or `IN[1]` errors | The old script or old graph is being used | Use the maintained files: `IN[0]` is the only input. |
| `SyntaxError` or `.NET` errors | The Python node uses IronPython 2.7 | Switch the node to **CPython 3**. |
| Every item is in the error list | The active view or default text note type cannot create annotations | Try a plan view, confirm a default text note type exists, and read the `Error` text. |
| Coordinates in the output look too large | `X` and `Y` are stored in Revit feet | Divide by `0.3048` for metres or multiply by `304.8` for millimetres. |
| The graph does nothing when opened | Manual run mode | Press **Run** in Dynamo. |

If an error persists, copy the contents of the `errors` output and include the
Revit and Dynamo versions when reporting the problem.

## Version History

See [CHANGELOG.md](CHANGELOG.md).

| Version | Date | Summary |
| --- | --- | --- |
| `0.1.0` | 2026-10-29 | First repository import. Removes the unused Boolean, exposes the start number as `IN[0]`, and adds package documentation. |

## License

Part of the Dynamo Script Library, licensed under the
[MIT License](../../../LICENSE). See
[licensing notes](../../../docs/LICENSING.md).

The original graph was provided by the repository owner and is retained in
`legacy/` for reference. The legacy folder is excluded from release packages.
