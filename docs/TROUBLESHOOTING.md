# Troubleshooting

Start with the tool's own README. It lists inputs, dependencies, warnings, and
known errors. This page covers problems that affect many tools.

## Before asking for help

1. Confirm the tool version from `script.json` or the release asset name.
2. Note your Revit version, Dynamo version, and Python engine.
3. Read the tool `CHANGELOG.md` for recent breaking changes.
4. Test on a copy of the model with a minimal example.
5. Search existing issues.

Include those details when opening a bug report.

## Download and extraction

| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| ZIP will not open | Incomplete download | Delete and download again. |
| Files are read-only or blocked | Windows attachment policy | Right-click the ZIP > **Properties** > **Unblock**, then extract. |
| Dynamo cannot find a related file | Running from inside the ZIP or a moved folder | Extract the full folder and keep its structure. |
| `__MACOSX` folder appears | macOS ZIP metadata | Ignore or delete it; it is not part of the tool. |

## Dynamo packages and custom nodes

| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| Yellow warning: custom node not found | Missing Dynamo package | **Packages > Manage Packages**, install the package named in the README. |
| Package installs but nodes still missing | Version mismatch | Install the version range documented by the tool, then restart Dynamo. |
| Graph opens with red nodes | Missing package or newer Dynamo node | Check the tool requirements; do not assume forward compatibility. |
| Graph saved in a newer Dynamo will not open | File format is newer than your Dynamo | Use a matching Dynamo/Revit version or ask for a back-saved graph. |

Do not install packages from untrusted publishers. Prefer the package source
named in the tool documentation.

## Python engine problems

| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| `SyntaxError` on type hints, f-strings, or `from __future__` | Node is using IronPython 2.7 | Switch the Python node to **CPython 3**. |
| `NameError: name 'IN' is not defined` | Script run outside Dynamo without inputs | Run it in Dynamo or call the functions directly in tests. |
| `ModuleNotFoundError` | Module not on `sys.path`, or package not installed in Dynamo's Python | Add the tool folder to `sys.path` or install the dependency for the engine Dynamo uses. |
| Works in desktop Python, fails in Dynamo | Different engine or missing packages | Match the engine documented by the tool; avoid assuming desktop packages exist. |
| `PermissionError` writing files | Protected folder or file open elsewhere | Write to a user folder and close the file in Excel or another program. |

Many Dynamo installations support both IronPython 2.7 and CPython 3, but
installed packages are engine-specific. Installing a library with desktop
`pip` does not make it available to Dynamo's CPython engine.

## Model safety and unexpected results

| Symptom | Resolution |
| --- | --- |
| Tool changed more than expected | Close without saving, restore the backup, and re-read the warnings and input types. |
| Undo does not fully revert | Some operations create new elements or external files. Restore from backup. |
| Results differ between runs | Check for selection-dependent inputs, random behavior, or unsorted lists. |
| Elements are missing from output | Check filters, worksets, linked models, and phase or design-option settings. |

Always work on a copy, save before running, and keep versioned backups for
production models.

## Repository maintenance tools

| Symptom | Likely cause | Resolution |
| --- | --- | --- |
| `validate_manifests.py` reports a missing heading | README structure is incomplete | Add the exact `## Heading` from the template. |
| Catalog check fails | `script.json` changed without regenerating | Run `python tools/generate_catalog.py` and commit the README. |
| Link check fails | Relative path is wrong or a file moved | Fix the link or move the target; do not add an external mirror. |
| Packaging fails on a missing entry point | Manifest lists a file that does not exist | Add the file or correct `entry_points`. |
| YAML parse error | Tabs or inconsistent indentation | Use two spaces per level in `.github/scripts-catalog.yml`. |

## Getting help

- [Open a bug report](https://github.com/Ziad-Amr1/dynamo-script-library/issues/new?template=bug_report.yml)
- [Request a feature](https://github.com/Ziad-Amr1/dynamo-script-library/issues/new?template=feature_request.yml)
- Report security issues privately as described in [SECURITY.md](../SECURITY.md)
