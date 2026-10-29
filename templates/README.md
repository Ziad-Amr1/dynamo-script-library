# Templates

Starter files used by `tools/new_tool.py`. They are not runnable tools and are
excluded from the Markdown link check because placeholders like `{{name}}` are
resolved only after scaffolding.

## `tool-package/`

| File | Purpose |
| --- | --- |
| `README.md` | Required tool documentation structure. |
| `script.json` | Manifest schema with safe defaults. |
| `CHANGELOG.md` | Keep a Changelog starter with the initial version. |
| `script.py` | Standard-Python starter that can be tested outside Revit. |

## `release-notes.md`

Copy this file to `docs/releases/vX.Y.Z.md`, replace the placeholders, and use
it with the tag-driven release workflow described in
[`docs/RELEASING.md`](../docs/RELEASING.md).

When changing templates, run:

```powershell
python -m unittest discover -s tests -v
python tools/new_tool.py --id template-check --name "Template Check" --category utilities --description "Temporary scaffold validation."
```

Delete the temporary tool folder afterwards; never commit it.
