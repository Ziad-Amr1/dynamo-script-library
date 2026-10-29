# Text Find & Replace

**Category:** `utilities`  
**Version:** `0.1.0`  
**Status:** Development  
**Python engine:** CPython 3

## Overview

Text Find & Replace performs bulk find-and-replace on a list of strings. It is
a pure Python helper for Dynamo graphs that need to clean sheet names, view
names, parameter values, or exported text before writing results back to Revit.

It never reads or writes a Revit model by itself. You decide which Revit nodes
receive the returned list.

## Features

- Literal or regular-expression search.
- Case-sensitive and case-insensitive matching.
- Whole-string matching, useful for mapping exact values.
- Optional preview of changes with `plan_changes`.
- Clear validation errors for empty searches, invalid regular expressions, and
  non-string inputs.
- Standard-library only; no Dynamo packages are required.
- Testable outside Revit; the logic has no Revit API dependency.

## Requirements

| Requirement | Details |
| --- | --- |
| Revit | Not yet verified in Revit. Test on a copy of your model. |
| Dynamo | Any Dynamo version with the **CPython 3** engine. Not verified against specific Dynamo releases. |
| Python engine | CPython 3.8 or newer. **Not compatible with IronPython 2.7.** |
| Dynamo packages | None. |
| Other dependencies | None. Standard library only. |

## Installation

### Option A: Use the file directly in Dynamo

1. Download this folder (see [docs/DOWNLOADING.md](../../../docs/DOWNLOADING.md)).
2. Extract it to a permanent location, for example
   `C:\DynamoTools\text-find-replace`.
3. In Dynamo, add a **Python Script** node.
4. Set the node's engine to **CPython 3**.
5. Open `script.py`, copy its contents, and paste them into the Python node.
6. Connect inputs as described below.

### Option B: Import the module from a Python node

```python
import sys

sys.path.append(r"C:\DynamoTools\text-find-replace")
from script import find_replace

values = IN[0]
find = IN[1]
replace = IN[2]
OUT = find_replace(values, find, replace)
```

Adjust the path to the folder where you extracted the tool. Do not point it at a
file inside a ZIP archive.

## Usage

1. Open the Revit project and make a backup copy.
2. In Dynamo, create a list of strings. For example, use **Element.GetParameterValueByName**
   to read sheet names or view names.
3. Connect the list to the Python node, then provide the search text and
   replacement text.
4. Run the graph and inspect the output list before writing anything to Revit.
5. Use the output with nodes such as **Element.SetParameterByName**, or review
   it manually first.

### Preview changes

`plan_changes` returns only the values that would change:

```python
from script import plan_changes

changes = plan_changes(
    ["A-101", "A-102", "B-201"],
    "A-",
    "A-ARCH-",
)
# [
#   {"index": 0, "before": "A-101", "after": "A-ARCH-101"},
#   {"index": 1, "before": "A-102", "after": "A-ARCH-102"},
# ]
```

### Regular expressions

With `use_regex=True`, `find` is a regular expression and `replace` may contain
backreferences:

```python
from script import find_replace

find_replace(
    ["Level 01", "Level 02", "Level 10"],
    r"Level (\d+)",
    r"L\1",
    use_regex=True,
)
# ["L01", "L02", "L10"]
```

## Inputs and Outputs

When the file is used as a Dynamo Python node, the `IN` ports are:

| Port | Name | Type | Default | Description |
| --- | --- | --- | --- | --- |
| `IN[0]` | `values` | list of strings | required | Values to search. A single string is rejected; wrap it in a list. |
| `IN[1]` | `find` | string | required | Non-empty search text or regular expression. |
| `IN[2]` | `replace` | string | `""` | Replacement text. An empty string deletes matches. |
| `IN[3]` | `case_sensitive` | boolean | `True` | Keep case-sensitive matching. |
| `IN[4]` | `whole_value` | boolean | `False` | Match the entire string instead of a substring. |
| `IN[5]` | `use_regex` | boolean | `False` | Treat `find` as a regular expression and allow backreferences in `replace`. |

Use real booleans in Dynamo, not the strings `"true"` or `"false"`.

| Output | Type | Description |
| --- | --- | --- |
| `OUT` | list of strings | A new list with matches replaced. The input list is not modified. |

Example:

| Input | find | replace | Result |
| --- | --- | --- | --- |
| `["GF-Lobby", "GF-Office"]` | `GF-` | `L0-` | `["L0-Lobby", "L0-Office"]` |
| `["Level 1", "level 2"]` | `level` | `L` | `["L 1", "L 2"]` when case-insensitive |
| `["A", "B", "AB"]` | `A` | `X` | `["X", "B", "AB"]` with `whole_value=True` |

## Warnings and Limitations

- This tool does **not** modify the Revit model. Writing values back is the
  responsibility of the surrounding graph.
- It processes strings only. Numbers, element IDs, and other object types must
  be converted first.
- Case-insensitive matching uses Unicode case folding for whole-value matching
  and Python's `re.IGNORECASE` for substring matching. Some scripts may behave
  differently than expected at the edges of Unicode.
- The Dynamo adapter reads boolean inputs with `bool()`. In Dynamo, a string
  such as `"false"` is truthy; connect actual boolean nodes.
- Regular expressions follow Python's `re` syntax, not Revit or .NET syntax.
- Not yet verified against specific Revit or Dynamo releases. Always test on a
  copy before production use.

## Troubleshooting

| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| `SyntaxError` in Dynamo | The node is using IronPython 2.7 | Switch the Python node to **CPython 3**. |
| `TypeError: values must be a list of strings` | A single string was connected | Wrap the value in a list or use a List.Create node. |
| `TypeError: values[2] must be a string` | The list contains numbers or nulls | Filter or convert values before the Python node. |
| `ValueError: find must be a non-empty string` | The search input is empty | Provide a non-empty search value. |
| `ValueError: Invalid regular expression` | Python regex syntax is invalid | Test the pattern with a small example and check escaping. |
| Backreferences appear literally | `use_regex` is not enabled | Enable `use_regex` for patterns such as `\\1`. |
| Nothing changes | Case, spaces, or whole-value settings differ | Use `plan_changes` and inspect the values first. |

## Version History

See [CHANGELOG.md](CHANGELOG.md).

| Version | Date | Summary |
| --- | --- | --- |
| `0.1.0` | 2026-10-29 | Initial development version with literal, case-insensitive, whole-value, and regex modes. |

## License

Part of the Dynamo Script Library, licensed under the
[MIT License](../../../LICENSE). See [licensing notes](../../../docs/LICENSING.md).
