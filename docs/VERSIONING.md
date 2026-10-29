# Versioning

The repository uses [Semantic Versioning 2.0.0](https://semver.org/). Versions
have the form `MAJOR.MINOR.PATCH`.

| Part | Increment when... | Example |
| --- | --- | --- |
| `MAJOR` | An incompatible change requires users to update graphs, inputs, or workflows. | `1.4.2` → `2.0.0` |
| `MINOR` | Backward-compatible functionality is added. | `1.4.2` → `1.5.0` |
| `PATCH` | Backward-compatible fixes, documentation corrections, or performance improvements are made. | `1.4.2` → `1.4.3` |

Pre-release identifiers are allowed for testing, for example `1.0.0-rc.1`.

## What is versioned

There are two independent levels:

1. **Tool version** — the `version` field in a tool's `script.json`, repeated in
   its `CHANGELOG.md`. Tools evolve independently.
2. **Repository release version** — a coordinated snapshot of the whole library,
   tagged `vMAJOR.MINOR.PATCH` (for example `v0.1.0`). A repository release may
   contain tools at different versions.

A tool version does not have to match the repository release version. For
example, repository `v0.2.0` may ship `text-find-replace` version `0.3.1` and
`batch-sheet-creator` version `0.1.0`.

## Commit, tag, release, and tool version

These four concepts are related but not interchangeable:

| Concept | What it is | User-facing? |
| --- | --- | --- |
| **Tool version** | Metadata for one tool package. Used in ZIP filenames and its changelog. | Yes |
| **Git commit** | An immutable point in history identified by a hash. It has no release notes and is not a supported download. | No |
| **Git tag** | A human-readable pointer to a commit, such as `v1.0.0`. Tags are cheap and can exist without a release. | Sometimes |
| **GitHub release** | A tag plus release notes and downloadable assets. This is what users should download. | Yes |

Creating a tag does not automatically mean a release was published. In this
repository, the release workflow reacts to tags, but only after the tagged
commit passes validation and a release-notes file exists.

## When to bump a tool version

| Change | Bump |
| --- | --- |
| Rename or move a tool folder, remove an input, change output type | MAJOR |
| Add an input, mode, or feature without breaking existing use | MINOR |
| Fix a bug, typo, or documentation error without behavior changes | PATCH |

Rules:

- A new tool starts at `0.1.0` while it is under development.
- Use `1.0.0` when the tool is stable and has been verified in the Revit and
  Dynamo versions documented in its README.
- Changing compatibility claims is at least a MINOR change; dropping support is
  a MAJOR change.
- Marking a tool deprecated does not delete it. Set `"status": "deprecated"` and
  document the replacement.
- Never reuse a version number for different content.

## Changelog rules

Each tool has a `CHANGELOG.md` using
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The current version
must have an entry, because validation checks it.

Use the sections that apply: `Added`, `Changed`, `Deprecated`, `Removed`,
`Fixed`, `Security`, and `Known limitations`.

The root `CHANGELOG.md` records repository-level changes and release snapshots.

## Repository tags

- Format: `vMAJOR.MINOR.PATCH`, for example `v0.1.0`.
- Create annotated tags with a message.
- Tag the exact commit used to build the release assets.
- Do not move or delete a published tag; publish a new patch version instead.
- Pre-release tags such as `v1.0.0-rc.1` are allowed and should be marked as a
  pre-release on GitHub.

## Downloads and versions

- A release ZIP is named `<tool-id>-v<tool-version>.zip`.
- The release page is the supported way to obtain a reproducible snapshot.
- The `main` branch ZIP is convenient but changes over time.
- Each release includes `index.json` and `SHA256SUMS.txt` for verification.

See [RELEASING.md](RELEASING.md) for the release procedure.
