# Release notes

Each repository release requires a human-written notes file named after its tag:

```text
docs/releases/v0.1.0.md
docs/releases/v1.2.0.md
```

The **Release** workflow reads `docs/releases/<tag>.md` and uses it as the GitHub
release body. If the file is missing, the workflow fails instead of publishing
an empty release.

## Create notes for a release

1. Copy [../../templates/release-notes.md](../../templates/release-notes.md) to
   `docs/releases/vX.Y.Z.md`.
2. Replace every placeholder, including the version, date, highlights, tool
   versions, compatibility, and asset names.
3. Remove sections that do not apply, but keep breaking changes explicit.
4. Follow the checklist in [../RELEASING.md](../RELEASING.md).

## Rules

- Notes describe what changed for users, not a raw commit list.
- Do not claim compatibility that was not tested.
- Always state breaking changes and upgrade steps.
- Keep released notes files in the repository for history.
- Do not create a notes file for a version you are not ready to tag.
