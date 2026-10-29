# Repository architecture

## Goals

- Make tools easy to find, download, and run without Git knowledge.
- Keep each tool self-contained and independently versioned.
- Generate repetitive documentation and packages instead of maintaining them by
  hand.
- Validate contributions automatically without pretending CI can run Revit.

## Directory roles

| Path | Responsibility |
| --- | --- |
| `scripts/<category>/<tool-id>/` | One tool package: entry points, README, changelog, manifest, examples. |
| `.github/scripts-catalog.yml` | Category order, display names, catalog markers, status labels. |
| `tools/` | Standard-library Python maintenance scripts. Not part of any Dynamo tool. |
| `templates/` | Starter files used by the scaffolder. |
| `docs/` | User and maintainer documentation, including release notes. |
| `resources/` | Shared images, sample data, and reference files. |
| `examples/` | Cross-tool example workflows. |
| `tests/` | Tests for Python logic that runs outside Revit. |
| `.github/workflows/` | Validation, catalog maintenance, packaging, and releases. |

## Source of truth

There is exactly one source of truth for tool metadata:

```text
scripts/<category>/<tool-id>/script.json
```

The root README catalog, package manifests, and release index are derived from
those files. Everything inside the generated markers in `README.md` is replaced
by `tools/generate_catalog.py`; handwritten README content outside the markers
is preserved.

Category order and labels come from `.github/scripts-catalog.yml`.

## Data flow

```text
.github/scripts-catalog.yml ──┐
                              ├──> tools/generate_catalog.py ──> README.md catalog
scripts/*/*/script.json ──────┘

scripts/*/*/script.json ─────────> tools/validate_manifests.py ──> CI status

scripts/*/*/ ────────────────────> tools/package_tools.py ──> dist/*.zip
                                                              dist/index.json
                                                              dist/SHA256SUMS.txt
```

## Maintenance tools

| Tool | Purpose |
| --- | --- |
| `tools/_common.py` | Config loading, YAML subset parser, tool discovery, SemVer checks, shared helpers. |
| `tools/generate_catalog.py` | Renders the catalog between markers; `--check` detects stale output. |
| `tools/validate_manifests.py` | Validates required fields, types, versions, categories, entry points, README headings, and changelog entries. |
| `tools/check_links.py` | Verifies relative Markdown links and images. |
| `tools/package_tools.py` | Builds deterministic ZIPs and checksums for release assets. |
| `tools/new_tool.py` | Scaffolds a tool folder from `templates/tool-package/`. |

All tools use only the Python standard library. They target desktop Python 3.10+
and are tested on current Python 3.12/3.13 in CI.

## Package format

A tool ZIP contains:

```text
<tool-id>/
├── README.md
├── CHANGELOG.md
├── script.json
├── <entry points>
└── PACKAGE_MANIFEST.json   generated at build time
```

`PACKAGE_MANIFEST.json` records the tool version, entry points, dependencies, and
SHA-256 hashes for every file. The archive uses fixed timestamps and sorted file
order so identical input produces an identical ZIP.

## Automation

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `validate.yml` | Push and pull request | Tests, manifest validation, link check, catalog freshness, package smoke build. |
| `catalog.yml` | Push to `main`, manual | Regenerates the catalog and commits it if stale. |
| `package.yml` | Manual | Builds all tool ZIPs and uploads them as a workflow artifact. |
| `release.yml` | Tag `v*` | Validates, builds packages, and publishes a GitHub release with notes from `docs/releases/<tag>.md`. |

CI does not execute `.dyn` graphs. There is no supported Dynamo runtime on
GitHub-hosted runners, so graph behavior must be verified manually and recorded
in the tool README.

## Adding a category

1. Add the category id, name, and description to `.github/scripts-catalog.yml`.
2. Create `scripts/<category-id>/README.md` describing its scope.
3. Run `python tools/validate_manifests.py` and
   `python tools/generate_catalog.py --check`.
4. Open a pull request.

Category ids are stable once tools use them. Renaming a category is a breaking
change for tool paths.

## Deliberate non-goals

- Running Revit or Dynamo inside CI.
- Publishing a release on every commit.
- Automatically changing tool versions.
- Committing generated `dist/` output.
- Vendoring third-party Dynamo packages.
