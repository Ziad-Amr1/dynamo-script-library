# Parameters

Tools that read, write, validate, map, or transfer Revit parameter data.

## Belongs here

- Shared and project parameter setup.
- Parameter transfer between elements, families, or documents.
- Data validation and cleanup for parameter values.
- Excel or CSV import/export of parameter tables.
- Type and instance parameter audits.

## Does not belong here

- Sheet or view naming (use `sheets-and-views`).
- Family geometry editing (use `families` or `geometry`).
- Schedules and reports (use `documentation`).

## Tool naming

Use a lowercase kebab-case folder id, for example `parameter-transfer`. See the
catalog in the root README for current tools and
[docs/ADDING-A-SCRIPT.md](../../docs/ADDING-A-SCRIPT.md) for the package
standard.
