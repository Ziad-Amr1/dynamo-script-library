# Contributing

Thanks for your interest in improving the Dynamo Script Library. Contributions
of new tools, fixes, documentation, and examples are welcome.

## Ways to contribute

- **Report a bug** using the [bug report form](https://github.com/Ziad-Amr1/dynamo-script-library/issues/new?template=bug_report.yml).
- **Request a feature or tool** using the [feature request form](https://github.com/Ziad-Amr1/dynamo-script-library/issues/new?template=feature_request.yml).
- **Improve documentation** by opening a pull request (PR).
- **Add a tool** by following the workflow below.

## Before you start

- Search existing issues and tools to avoid duplicates.
- For large features, open an issue first so the approach can be discussed.
- Do not include secrets, credentials, customer data, or proprietary models.
- By contributing, you agree that your contribution is licensed under the
  repository's [MIT License](LICENSE).

## Add a new tool

The fastest path is the scaffolder:

```powershell
python tools/new_tool.py --id my-tool --name "My Tool" --category utilities --description "One sentence describing the tool."
```

Then:

1. Implement the `.dyn` graph and/or Python script in the generated folder.
2. Fill in every section of the tool `README.md`.
3. Edit `script.json` with verified compatibility information only.
4. Add a changelog entry and set the initial version (start at `0.1.0` for a
   new tool unless it is already stable).
5. Add tests for Python logic that can run outside Revit, under `tests/`.
6. Run the local checks:

   ```powershell
   python -m unittest discover -s tests -v
   python tools/validate_manifests.py
   python tools/generate_catalog.py --check
   python tools/package_tools.py --out dist
   ```

7. Regenerate the catalog and commit the result:

   ```powershell
   python tools/generate_catalog.py
   ```

8. Open a pull request. CI must pass before merge.

Full details, including the metadata schema and README requirements, are in
[docs/ADDING-A-SCRIPT.md](docs/ADDING-A-SCRIPT.md).

## Repository rules

- Keep each tool self-contained in its own folder under
  `scripts/<category>/<tool-id>/`.
- Do not rename or move an existing tool folder without a major version bump
  and a redirect note in its changelog.
- Never claim Revit, Dynamo, or Python compatibility that has not been tested.
- Do not add third-party dependencies without a license check.
- Do not execute Dynamo graphs in CI; test pure Python logic instead.
- Keep commits focused and use clear messages.

## Documentation requirements

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

Validation enforces a subset of these headings. Do not remove the others.

## Maintainer checklist

Use this when reviewing or maintaining tools:

- [ ] Manifest version matches the latest tool changelog entry.
- [ ] Entry points listed in `script.json` exist.
- [ ] Compatibility fields reflect real testing, not assumptions.
- [ ] Deprecated tools are marked `"status": "deprecated"` and explain the
      replacement in their README.
- [ ] Dependencies and minimum versions are documented and still available.
- [ ] Examples contain no confidential data.
- [ ] `python -m unittest discover -s tests -v` passes.
- [ ] `python tools/generate_catalog.py --check` passes.

## Using the GitHub web interface

You do not need Git installed to contribute:

1. Fork the repository with **Fork**.
2. In your fork, use **Add file > Upload files** to add or replace files.
3. Commit the changes to your fork.
4. Select **Contribute > Open pull request** and describe the change.

Maintainers may edit pull requests to keep the catalog and formatting in sync.

## Code of conduct

Be respectful, assume good intent, and keep discussions technical. Harassment
and exclusionary behavior are not tolerated.
