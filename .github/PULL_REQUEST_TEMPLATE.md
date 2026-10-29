## Summary

Describe what this pull request changes and why.

## Type of change

- [ ] New tool
- [ ] Bug fix
- [ ] New feature in an existing tool
- [ ] Documentation
- [ ] Repository tooling or CI
- [ ] Breaking change

## Tool details

Fill this in for new or changed tools:

| Field | Value |
| --- | --- |
| Tool id | |
| Previous version | |
| New version | |
| Category | |
| Entry points | |
| Python engine | |

## Testing

- [ ] `python -m unittest discover -s tests -v`
- [ ] `python tools/validate_manifests.py`
- [ ] `python tools/check_links.py`
- [ ] `python tools/generate_catalog.py --check`
- [ ] `python tools/package_tools.py --out dist`
- [ ] Tested manually in Revit and Dynamo (state versions below)
- [ ] Not tested in Revit/Dynamo; compatibility fields left empty

Revit version:
Dynamo version:
Python engine:

## Compatibility

List only versions actually verified. Write "none verified" when applicable.

## Checklist

- [ ] I preserved existing behavior unless the change is intentional and documented.
- [ ] The tool README has all required sections.
- [ ] `script.json` is updated and valid.
- [ ] The tool `CHANGELOG.md` contains the current version.
- [ ] Entry points exist and are listed in the manifest.
- [ ] No secrets, credentials, or confidential project data are included.
- [ ] Examples use synthetic data.
- [ ] The root catalog was regenerated, not edited by hand.
- [ ] Third-party code and assets have compatible licenses.
