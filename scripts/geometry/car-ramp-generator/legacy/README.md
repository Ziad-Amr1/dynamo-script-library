# Legacy files (reference only)

These files are the original Car Ramp Generator versions imported into the
repository. They are kept for history and comparison. **Do not use them for new
work.**

Use the maintained files instead:

- [`../CarRampGenerator_Revit2025.dyn`](../CarRampGenerator_Revit2025.dyn)
- [`../script.py`](../script.py)
- [`../README.md`](../README.md)

## Contents

| File | Why it is here |
| --- | --- |
| `CarRamp_Dynamo_Revit2025_All_Nodes_Explained.dyn` | Earlier graph. Its Python reads `.Name` directly, which can raise `Property cannot be read` in Dynamo/Revit. |
| `CarRamp_Dynamo_Revit2025.py` | Standalone Python for the earlier graph. Superseded by the `get_Name()` version. |
| `README_CarRamp_Revit2025_Arabic.txt` | Original Arabic notes for the earlier version. |
| `README_CarRamp_Revit2025_NamePropertyFix_Arabic.txt` | Original Arabic notes explaining the `get_Name()` fix. |

The files under this folder are excluded from release ZIP packages. They may be
removed in a future version after the fixed graph has been verified in Revit.
