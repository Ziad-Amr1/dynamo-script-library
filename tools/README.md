# Maintenance tools

Standard-library Python 3.10+ utilities that keep the repository consistent.
They are not Dynamo tools and must not import Revit or Dynamo APIs.

| Tool | Command | Purpose |
| --- | --- | --- |
| Catalog generator | `python tools/generate_catalog.py` | Rewrites the tool catalog between the markers in the root README. Add `--check` for CI. |
| Validator | `python tools/validate_manifests.py` | Checks manifests, versions, categories, entry points, README headings, and changelogs. |
| Link checker | `python tools/check_links.py` | Verifies relative links and images in Markdown. |
| Packager | `python tools/package_tools.py --out dist` | Builds deterministic tool ZIPs, `index.json`, and `SHA256SUMS.txt`. |
| Scaffolder | `python tools/new_tool.py --help` | Creates a new tool folder from `templates/tool-package/`. |

`_common.py` contains shared configuration parsing, discovery, and validation
helpers. It intentionally includes a small YAML subset parser so no third-party
package is needed.

See [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for the data flow and
[docs/ADDING-A-SCRIPT.md](../docs/ADDING-A-SCRIPT.md) for the contributor
workflow.
