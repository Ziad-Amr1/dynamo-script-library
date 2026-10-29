# Legacy file (reference only)

This folder contains the original `number_active_view_start_number.dyn` graph
imported into the repository. **Do not use it for new work.**

Use the maintained files instead:

- [`../ParkingNumbering.dyn`](../ParkingNumbering.dyn)
- [`../script.py`](../script.py)
- [`../README.md`](../README.md)

## Why this file is superseded

- The graph contains an unused Boolean node connected to `IN[0]`.
- The working start-number value is connected to `IN[1]`.
- The start-number `DoubleInput` node has no node view, so it is not visible on
  the Dynamo canvas.
- The graph name is the generic `number`, with no description.

The maintained graph removes the unused Boolean, renumbers the start number to
`IN[0]`, adds a visible **Start number** node, and includes a descriptive graph
name. The Python logic is otherwise preserved.

This legacy folder is excluded from release packages.
