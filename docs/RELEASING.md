# Publishing a release

Releases are deliberate snapshots of the repository. Never publish a release on
every commit, and never bump a version automatically without review.

The automated path uses the **Release** workflow
(`.github/workflows/release.yml`), which runs only for tags matching `v*`.

## Prerequisites

- Push access to the repository.
- A green **Validate** workflow on the target commit.
- All tool versions and changelogs updated.
- A release notes file at `docs/releases/vX.Y.Z.md`.
- GitHub CLI (`gh`) authenticated if releasing manually.

## 1. Decide the repository version

Use SemVer. For the first public snapshot, `v0.1.0` is appropriate while tools
are still under development. See [VERSIONING.md](VERSIONING.md).

## 2. Update the changelogs

Move entries from `## [Unreleased]` in the root `CHANGELOG.md` into a dated
section:

```markdown
## [0.1.0] - 2026-10-29

### Added

- Initial public release.
```

Add link definitions at the bottom, for example:

```markdown
[Unreleased]: https://github.com/Ziad-Amr1/dynamo-script-library/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Ziad-Amr1/dynamo-script-library/releases/tag/v0.1.0
```

Confirm every changed tool has a matching tool-level changelog entry.

## 3. Prepare release notes

Copy `templates/release-notes.md` to `docs/releases/vX.Y.Z.md` and replace every
placeholder. Notes must be human-readable and include:

- Highlights.
- New and updated tools with versions.
- Breaking changes and upgrade steps.
- Verified compatibility (or an explicit statement that nothing is verified).
- Download asset descriptions.

The release workflow fails if this file is missing.

## 4. Run the checks

From the repository root:

```powershell
python -m unittest discover -s tests -v
python tools/validate_manifests.py
python tools/check_links.py
python tools/generate_catalog.py --check
python tools/package_tools.py --out dist
```

Inspect `dist/index.json`, open one ZIP, and confirm the tool folders contain
the expected files.

## 5. Commit and tag

```powershell
git add .
git commit -m "Release v0.1.0"
git push origin main
git tag -a v0.1.0 -m "Dynamo Script Library v0.1.0"
git push origin v0.1.0
```

Pushing the tag starts the **Release** workflow.

## 6. What the workflow does

For tag `vX.Y.Z`, `.github/workflows/release.yml`:

1. Checks out the tagged commit.
2. Runs tests, manifest validation, the link check, and the catalog check.
3. Builds deterministic tool ZIPs plus `index.json` and `SHA256SUMS.txt`.
4. Verifies that `docs/releases/vX.Y.Z.md` exists.
5. Creates a GitHub release with that tag, those notes, and the packaged assets.

The workflow does not create tags, bump versions, or run on ordinary commits.

## 7. Verify the release

1. Open the [Releases](https://github.com/Ziad-Amr1/dynamo-script-library/releases)
   page.
2. Confirm the tag, title, notes, and assets.
3. Download one ZIP and check it against `SHA256SUMS.txt`.
4. Confirm the `main` branch still validates.

## Manual fallback

If Actions are unavailable, run the same steps locally:

```powershell
python tools/package_tools.py --out dist
gh release create v0.1.0 dist/*.zip dist/index.json dist/SHA256SUMS.txt `
  --title "Dynamo Script Library v0.1.0" `
  --notes-file docs/releases/v0.1.0.md
```

Add `--prerelease` for a release candidate. Do not use `--draft` and then forget
to publish it.

## Release checklist

- [ ] Root changelog has a dated version section.
- [ ] Every tool changelog matches its manifest version.
- [ ] Compatibility claims are verified or absent.
- [ ] `docs/releases/vX.Y.Z.md` is complete.
- [ ] All five local checks pass.
- [ ] `main` is pushed and green.
- [ ] Tag uses `vMAJOR.MINOR.PATCH`.
- [ ] Release assets include tool ZIPs, `index.json`, and `SHA256SUMS.txt`.
- [ ] Download and installation instructions still match the assets.

## If something is wrong after publishing

- Do **not** move or delete a published tag.
- Fix the problem and publish a new PATCH release.
- If the release is unsafe, mark it as a pre-release or delete the GitHub
  release, keep the tag, and publish a corrected patch with clear notes.
