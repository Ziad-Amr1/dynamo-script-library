# Adding a script or tool

This is the complete workflow for adding a tool. The short version is in
[CONTRIBUTING.md](../CONTRIBUTING.md).

## 1. Choose a category

Pick the closest folder under `scripts/`:

| Category | Use for |
| --- | --- |
| `model-management` | Model audits, cleanup, links, worksets, batch project operations |
| `sheets-and-views` | Sheets, views, viewports, numbering, exports |
| `parameters` | Parameter setup, transfer, validation, CSV/Excel data |
| `families` | Family loading, auditing, placement, type catalogs |
| `geometry` | Geometry generation, analysis, transforms, placement calculations |
| `documentation` | Annotations, numbering, schedules, reports, registers, handover data |
| `utilities` | Reusable text, list, file, and data helpers |

If no category fits, open an issue before adding a new category. Categories are
configured in `.github/scripts-catalog.yml` and each one needs a folder with a
README.

## 2. Scaffold the tool

From the repository root:

```powershell
python tools/new_tool.py `
  --id batch-sheet-creator `
  --name "Batch Sheet Creator" `
  --category sheets-and-views `
  --description "Creates sheets in bulk from structured input."
```

The id must be lowercase kebab-case and becomes the folder name. The command
refuses to overwrite an existing folder.

Result:

```text
scripts/sheets-and-views/batch-sheet-creator/
├── README.md
├── CHANGELOG.md
├── script.json
└── script.py
```

Delete `script.py` only if the tool is a Dynamo graph with no Python logic, and
update `entry_points` to the `.dyn` file first.

## 3. Implement the tool

- A `.dyn` graph is the main deliverable when the workflow is primarily visual.
- A `.py` file is appropriate for a Python node, a reusable function, or a
  standalone utility.
- Keep Revit-specific handling separate from pure logic where practical.
- State whether the code targets **CPython 3** or **IronPython 2.7**.
- Do not assume standard Python packages are available inside Dynamo. List
  every non-standard dependency in the manifest and README.
- Add useful error messages instead of silent failures.
- Do not include customer models, API keys, or private project data.

Python expectations:

- Module docstring explaining purpose, inputs, outputs, and target engine.
- PEP 8 formatting where practical.
- Type hints only when the target engine supports them.
- Tests for logic that does not require Revit, under `tests/`.

## 4. Complete the manifest

Edit `script.json`. This file is the single source of truth for the generated
catalog and packaging.

| Field | Required | Rules |
| --- | --- | --- |
| `name` | Yes | Human-readable, unique, 1-80 characters recommended. |
| `id` | Yes | Lowercase kebab-case; must equal the folder name. |
| `description` | Yes | One sentence, 200 characters maximum, no trailing period required. |
| `category` | Yes | Must match a configured category id. |
| `version` | Yes | SemVer, for example `0.1.0` or `1.2.3`. |
| `status` | Yes | `stable`, `beta`, `development`, or `deprecated`. |
| `revit_versions` | Yes | Array of tested Revit versions, for example `["2024", "2025"]`. Use `[]` when unverified. |
| `dynamo_versions` | Yes | Array of tested Dynamo versions. Use `[]` when unverified. |
| `python_engine` | Yes | `CPython 3`, `IronPython 2.7`, `CPython 3 / IronPython 2.7`, or `N/A`. |
| `entry_points` | Yes | Array of existing files relative to the tool folder. At least one. |
| `dependencies` | Yes | Array of Dynamo packages or Python packages. Use `[]` when none. |
| `tags` | Yes | Array of short search tags. Use `[]` if none. |

Example:

```json
{
  "name": "Batch Sheet Creator",
  "id": "batch-sheet-creator",
  "description": "Creates sheets in bulk from structured input.",
  "category": "sheets-and-views",
  "version": "0.1.0",
  "status": "development",
  "revit_versions": [],
  "dynamo_versions": [],
  "python_engine": "CPython 3",
  "entry_points": ["BatchSheetCreator.dyn"],
  "dependencies": ["Clockwork for Dynamo 2.x"],
  "tags": ["sheets", "automation"]
}
```

Never claim a Revit or Dynamo version you have not tested. Empty arrays are
honest and expected for new tools.

## 5. Write the README

Every tool README must contain these headings:

- `## Overview`
- `## Features`
- `## Requirements`
- `## Installation`
- `## Usage`
- `## Inputs and Outputs`
- `## Warnings and Limitations`
- `## Troubleshooting`
- `## Version History`
- `## License`

Write for someone who has never opened Dynamo. Explain where to click, what to
connect, and how to test safely. Document inputs and outputs with types and
examples. State limitations and what the tool does not do.

Useful additions: screenshots, a short GIF, example data, and a before/after
table. Store images in the tool folder or in `resources/` and use relative
links.

## 6. Test

For pure Python logic, add a test file under `tests/`. A simple pattern:

```python
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "utilities" / "my-tool" / "script.py"
spec = importlib.util.spec_from_file_location("my_tool_script", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
```

Test happy paths, edge cases, and error states. Do not attempt to execute Dynamo
graphs in CI unless a real Dynamo runtime is available.

If you cannot test in Revit, say so in the README and leave compatibility arrays
empty.

## 7. Run the checks

From the repository root:

```powershell
python -m unittest discover -s tests -v
python tools/validate_manifests.py
python tools/check_links.py
python tools/generate_catalog.py --check
python tools/package_tools.py --out dist
```

All five must pass. `package_tools.py` writes to `dist/`, which is ignored by
Git.

## 8. Generate the catalog

```powershell
python tools/generate_catalog.py
```

This updates only the block between the generated markers in the root
`README.md`. Commit the change. Do not edit that block by hand.

## 9. Version and changelog

- New tool: start at `0.1.0` while it is under development, or `1.0.0` when it
  is stable and verified.
- Add a matching entry to the tool's `CHANGELOG.md`.
- For a repository-wide release, update the root `CHANGELOG.md` and follow
  [RELEASING.md](RELEASING.md).

Do not bump versions or publish releases unless the change authorizes it.

## 10. Submit

1. Commit your changes with a focused message.
2. Push your branch and open a pull request, **or** use the GitHub web interface:
   fork, upload the files, and select **Contribute > Open pull request**.
3. Fill in the pull request template, including what you tested.
4. Wait for the **Validate** workflow to pass.

## Tool checklist

- [ ] Folder is `scripts/<category>/<id>/`.
- [ ] `script.json` passes validation.
- [ ] `README.md` has all required headings.
- [ ] `CHANGELOG.md` contains the current version.
- [ ] Entry points exist.
- [ ] Compatibility fields reflect real testing or are empty.
- [ ] Examples contain no confidential data.
- [ ] Tests pass locally.
- [ ] Root catalog regenerated.
