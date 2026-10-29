# Model Management

Tools that audit, clean, compare, or batch-process Revit models, links, and
project files.

## Belongs here

- Model audits and health checks.
- Purge, cleanup, and warning-management workflows.
- Link and workset inventory.
- Batch operations that affect a whole project.

## Does not belong here

- Sheet or view creation (use `sheets-and-views`).
- Parameter-only workflows (use `parameters`).
- Geometry calculations (use `geometry`).

## Tool naming

Use a lowercase kebab-case folder id, for example `model-health-audit`, and a
human-readable name in `script.json`. See the catalog in the root README for
current tools and [docs/ADDING-A-SCRIPT.md](../../docs/ADDING-A-SCRIPT.md) for
the package standard.
