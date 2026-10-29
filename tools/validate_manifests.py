#!/usr/bin/env python3
"""Validate tool manifests, README structure, changelogs, and categories.

Usage:
    python tools/validate_manifests.py
    python tools/validate_manifests.py --root path/to/repository

Exit status is 1 when any error is found. This tool never modifies files.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from _common import (
    ID_RE,
    PYTHON_ENGINES,
    REQUIRED_MANIFEST_KEYS,
    VALIDATED_README_HEADINGS,
    CatalogConfig,
    LibraryError,
    Tool,
    discover_tools,
    find_root,
    is_semver,
    load_config,
)


def _require_string_list(
    manifest: dict[str, Any], key: str, path: str, errors: list[str]
) -> None:
    value = manifest.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{path}: '{key}' must be an array of strings.")


def _has_heading(markdown: str, heading: str) -> bool:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.MULTILINE)
    return bool(pattern.search(markdown))


def _changelog_mentions(changelog: str, version: str) -> bool:
    pattern = re.compile(
        rf"^##\s*\[?v?{re.escape(version)}\]?", re.IGNORECASE | re.MULTILINE
    )
    return bool(pattern.search(changelog))


def validate_tool(tool: Tool, config: CatalogConfig) -> list[str]:
    errors: list[str] = []
    manifest = tool.manifest
    folder = tool.path.name
    relative = tool.relative_path()

    missing = [key for key in REQUIRED_MANIFEST_KEYS if key not in manifest]
    for key in missing:
        errors.append(f"{relative}: manifest is missing required key '{key}'.")
    if missing:
        return errors

    for key in ("name", "id", "description", "category", "version", "python_engine"):
        value = manifest.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{relative}: '{key}' must be a non-empty string.")
    if errors:
        return errors

    if not ID_RE.fullmatch(tool.id):
        errors.append(
            f"{relative}: id '{tool.id}' must use lowercase kebab-case "
            "(letters, digits, and single hyphens)."
        )
    if folder != tool.id:
        errors.append(
            f"{relative}: manifest id '{tool.id}' must match the folder name '{folder}'."
        )
    if not is_semver(tool.version):
        errors.append(
            f"{relative}: version '{tool.version}' is not valid SemVer "
            "(expected MAJOR.MINOR.PATCH, for example 1.2.0)."
        )
    if len(tool.description) > 200:
        errors.append(f"{relative}: description is longer than 200 characters.")
    if tool.status not in config.status_labels:
        allowed = ", ".join(sorted(config.status_labels))
        errors.append(
            f"{relative}: status '{tool.status}' is not one of: {allowed}."
        )
    if tool.category not in config.category_ids:
        errors.append(
            f"{relative}: category '{tool.category}' is not configured in "
            ".github/scripts-catalog.yml."
        )
    elif (tool.root / config.tools_dir / tool.category).resolve() != tool.path.parent.resolve():
        errors.append(
            f"{relative}: tool must live directly inside its category folder "
            f"'{config.tools_dir}/{tool.category}/'."
        )
    engine = str(manifest["python_engine"])
    if engine not in PYTHON_ENGINES:
        allowed = ", ".join(sorted(PYTHON_ENGINES))
        errors.append(f"{relative}: python_engine '{engine}' is not one of: {allowed}.")

    for key in ("revit_versions", "dynamo_versions", "entry_points", "dependencies", "tags"):
        _require_string_list(manifest, key, relative, errors)

    entry_points = manifest.get("entry_points")
    if isinstance(entry_points, list):
        if not entry_points:
            errors.append(f"{relative}: entry_points must list at least one file.")
        for entry in entry_points:
            if not isinstance(entry, str) or not entry.strip():
                errors.append(f"{relative}: entry_points contains an empty value.")
                continue
            entry_path = Path(entry)
            if entry_path.is_absolute() or ".." in entry_path.parts:
                errors.append(
                    f"{relative}: entry point '{entry}' must be a relative path "
                    "inside the tool folder."
                )
                continue
            resolved = (tool.path / entry_path).resolve()
            if tool.path.resolve() not in resolved.parents and resolved != tool.path.resolve():
                errors.append(f"{relative}: entry point '{entry}' escapes the tool folder.")
            elif not resolved.is_file():
                errors.append(f"{relative}: entry point '{entry}' does not exist.")

    if not tool.readme.is_file():
        errors.append(f"{relative}: README.md is missing.")
    else:
        readme_text = tool.readme.read_text(encoding="utf-8")
        for heading in VALIDATED_README_HEADINGS:
            if not _has_heading(readme_text, heading):
                errors.append(
                    f"{relative}/README.md: missing required heading '## {heading}'."
                )

    if not tool.changelog.is_file():
        errors.append(f"{relative}: CHANGELOG.md is missing.")
    else:
        changelog_text = tool.changelog.read_text(encoding="utf-8")
        if not _changelog_mentions(changelog_text, tool.version):
            errors.append(
                f"{relative}/CHANGELOG.md: no entry found for version {tool.version}."
            )

    return errors


def validate_repository(root: Path, config: CatalogConfig) -> list[str]:
    tools = discover_tools(root, config)
    errors: list[str] = []
    seen_ids: dict[str, Path] = {}
    seen_names: dict[str, Path] = {}
    for tool in tools:
        for error in validate_tool(tool, config):
            errors.append(error)
        key = tool.id.casefold()
        if key in seen_ids:
            errors.append(
                f"Duplicate tool id '{tool.id}' in {seen_ids[key]} and {tool.path}."
            )
        else:
            seen_ids[key] = tool.path
        name_key = tool.name.casefold()
        if name_key in seen_names:
            errors.append(
                f"Duplicate tool name '{tool.name}' in {seen_names[name_key]} and {tool.path}."
            )
        else:
            seen_names[name_key] = tool.path
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None, help="Repository root.")
    args = parser.parse_args(argv)

    try:
        root, config = load_config(find_root(args.root))
    except LibraryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    errors = validate_repository(root, config)
    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    tool_count = len(discover_tools(root, config))
    print(f"Validated {tool_count} tool manifest(s) successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
