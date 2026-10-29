# Utilities

General-purpose helpers that support many kinds of Dynamo workflows.

## Belongs here

- Text, list, and data-cleaning helpers.
- Unit conversion and formatting.
- File and path utilities.
- Small pure-Python functions reused across graphs.
- Reference implementations that demonstrate repository standards.

## Does not belong here

- Tools tied to a specific Revit domain; place them in the matching category.
- One-off project logic that is not reusable.

## Current tools

- [Text Find & Replace](text-find-replace/README.md) — bulk literal or regex
  find-and-replace for lists of strings.

## Tool naming

Use a lowercase kebab-case folder id, for example `text-find-replace`. See the
catalog in the root README for all tools and
[docs/ADDING-A-SCRIPT.md](../../docs/ADDING-A-SCRIPT.md) for the package
standard.
