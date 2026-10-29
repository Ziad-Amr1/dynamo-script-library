"""Shared helpers for the repository maintenance tools.

This module deliberately uses only the Python standard library so the tools
work on a clean workstation and in GitHub Actions without installing packages.

It is not part of any Dynamo tool. It targets standard desktop Python 3.10+.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SKIP_DIRS = {"__pycache__", ".git", "dist", "build", "backup", ".venv", "venv"}
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$"
)
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PYTHON_ENGINES = {
    "CPython 3",
    "IronPython 2.7",
    "CPython 3 / IronPython 2.7",
    "N/A",
}
REQUIRED_MANIFEST_KEYS = (
    "name",
    "id",
    "description",
    "category",
    "version",
    "status",
    "revit_versions",
    "dynamo_versions",
    "python_engine",
    "entry_points",
    "dependencies",
    "tags",
)
REQUIRED_README_HEADINGS = (
    "Overview",
    "Features",
    "Requirements",
    "Installation",
    "Usage",
    "Inputs and Outputs",
    "Warnings and Limitations",
    "Troubleshooting",
    "Version History",
    "License",
)
VALIDATED_README_HEADINGS = (
    "Overview",
    "Requirements",
    "Installation",
    "Usage",
    "Troubleshooting",
    "Version History",
)


class LibraryError(Exception):
    """Raised when repository configuration or metadata is invalid."""


@dataclass
class Tool:
    """A discovered tool package."""

    manifest: dict[str, Any]
    path: Path
    root: Path

    @property
    def id(self) -> str:
        return str(self.manifest["id"])

    @property
    def name(self) -> str:
        return str(self.manifest["name"])

    @property
    def category(self) -> str:
        return str(self.manifest["category"])

    @property
    def version(self) -> str:
        return str(self.manifest["version"])

    @property
    def status(self) -> str:
        return str(self.manifest["status"])

    @property
    def description(self) -> str:
        return str(self.manifest["description"])

    @property
    def entry_points(self) -> list[str]:
        return list(self.manifest.get("entry_points", []))

    @property
    def readme(self) -> Path:
        return self.path / "README.md"

    @property
    def changelog(self) -> Path:
        return self.path / "CHANGELOG.md"

    def relative_path(self) -> str:
        return self.path.relative_to(self.root).as_posix()

    def readme_link(self) -> str:
        return f"{self.relative_path()}/README.md"


@dataclass
class CatalogConfig:
    """Repository catalog configuration loaded from scripts-catalog.yml."""

    readme: str = "README.md"
    tools_dir: str = "scripts"
    catalog_start: str = "<!-- BEGIN GENERATED: TOOLS -->"
    catalog_end: str = "<!-- END GENERATED: TOOLS -->"
    status_labels: dict[str, str] = field(default_factory=dict)
    categories: list[dict[str, str]] = field(default_factory=list)

    @property
    def category_ids(self) -> list[str]:
        return [category["id"] for category in self.categories]

    def category_name(self, category_id: str) -> str:
        for category in self.categories:
            if category.get("id") == category_id:
                return category.get("name", category_id)
        return category_id

    def status_label(self, status: str) -> str:
        return self.status_labels.get(status, status)


def find_root(start: Path | None = None) -> Path:
    """Return the repository root, allowing tools to be run from any directory."""
    if start is None:
        start = Path(__file__).resolve()
    else:
        start = start.resolve()
    current = start if start.is_dir() else start.parent
    for candidate in (current, *current.parents):
        if (candidate / ".github" / "scripts-catalog.yml").is_file():
            return candidate
    raise LibraryError(
        "Could not find .github/scripts-catalog.yml. Run this tool from inside "
        "the repository."
    )


def _strip_comment(line: str) -> str:
    """Remove a YAML comment while respecting single and double quotes."""
    quote: str | None = None
    for index, char in enumerate(line):
        if quote:
            if char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            quote = char
        elif char == "#" and (index == 0 or line[index - 1].isspace()):
            return line[:index]
    return line


def _parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value == "":
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    if value in ("true", "false"):
        return value == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part) for part in inner.split(",")]
    return value


def _tokenize_yaml(text: str) -> list[tuple[int, str, int]]:
    tokens: list[tuple[int, str, int]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw_line).rstrip()
        if not line.strip():
            continue
        leading = line[: len(line) - len(line.lstrip())]
        if "\t" in leading:
            raise LibraryError(f"Line {line_number}: tabs are not allowed for indentation.")
        indent = len(line) - len(line.lstrip(" "))
        tokens.append((indent, line.strip(), line_number))
    return tokens


def _parse_block(
    tokens: list[tuple[int, str, int]], index: int, indent: int
) -> tuple[Any, int]:
    if index >= len(tokens):
        return None, index
    if tokens[index][1].startswith("- "):
        return _parse_list(tokens, index, indent)
    return _parse_mapping(tokens, index, indent)


def _parse_mapping(
    tokens: list[tuple[int, str, int]], index: int, indent: int
) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    while index < len(tokens):
        current_indent, content, line_number = tokens[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise LibraryError(f"Line {line_number}: unexpected indentation.")
        if content.startswith("- "):
            break
        key, separator, rest = content.partition(":")
        if not separator or not key.strip():
            raise LibraryError(f"Line {line_number}: expected 'key: value'.")
        key = key.strip()
        if rest.strip():
            result[key] = _parse_scalar(rest)
            index += 1
            continue
        index += 1
        if index < len(tokens) and tokens[index][0] > indent:
            value, index = _parse_block(tokens, index, tokens[index][0])
            result[key] = value
        else:
            result[key] = None
    return result, index


def _parse_list(
    tokens: list[tuple[int, str, int]], index: int, indent: int
) -> tuple[list[Any], int]:
    result: list[Any] = []
    while index < len(tokens):
        current_indent, content, line_number = tokens[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise LibraryError(f"Line {line_number}: unexpected indentation.")
        if not content.startswith("- "):
            break
        item_text = content[2:].strip()
        if ":" not in item_text:
            result.append(_parse_scalar(item_text))
            index += 1
            continue
        key, _, rest = item_text.partition(":")
        item: dict[str, Any] = {key.strip(): _parse_scalar(rest)} if rest.strip() else {key.strip(): None}
        index += 1
        while index < len(tokens) and tokens[index][0] > indent:
            child_indent, child_content, child_line = tokens[index]
            if child_indent != indent + 2:
                raise LibraryError(f"Line {child_line}: nested list items must be indented by 2 spaces.")
            if child_content.startswith("- "):
                break
            child_key, separator, child_rest = child_content.partition(":")
            if not separator:
                raise LibraryError(f"Line {child_line}: expected 'key: value'.")
            item[child_key.strip()] = _parse_scalar(child_rest)
            index += 1
        result.append(item)
    return result, index


def load_yaml(path: Path) -> dict[str, Any]:
    """Parse the small YAML subset used by this repository's configuration."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise LibraryError(f"Cannot read {path}: {exc}") from exc
    tokens = _tokenize_yaml(text)
    if not tokens:
        return {}
    value, index = _parse_block(tokens, 0, tokens[0][0])
    if index != len(tokens):
        raise LibraryError(f"{path}: could not parse the whole file.")
    if not isinstance(value, dict):
        raise LibraryError(f"{path}: the top level must be a mapping.")
    return value


def load_config(root: Path | None = None) -> tuple[Path, CatalogConfig]:
    root = find_root(root)
    data = load_yaml(root / ".github" / "scripts-catalog.yml")
    config = CatalogConfig(
        readme=str(data.get("readme") or "README.md"),
        tools_dir=str(data.get("tools_dir") or "scripts"),
        catalog_start=str(data.get("catalog_start") or "<!-- BEGIN GENERATED: TOOLS -->"),
        catalog_end=str(data.get("catalog_end") or "<!-- END GENERATED: TOOLS -->"),
        status_labels=dict(data.get("status_labels") or {}),
        categories=list(data.get("categories") or []),
    )
    if not config.categories:
        raise LibraryError("No categories are configured in .github/scripts-catalog.yml.")
    for category in config.categories:
        for key in ("id", "name"):
            if not category.get(key):
                raise LibraryError(f"Category entry is missing '{key}': {category}")
        category_path = root / config.tools_dir / str(category["id"])
        if not category_path.is_dir():
            raise LibraryError(f"Category folder does not exist: {category_path}")
    return root, config


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except OSError as exc:
        raise LibraryError(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise LibraryError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise LibraryError(f"{path}: the top level must be an object.")
    return data


def discover_tool_paths(root: Path, config: CatalogConfig) -> list[Path]:
    tools_root = root / config.tools_dir
    if not tools_root.is_dir():
        return []
    return sorted(path for path in tools_root.glob("*/*/script.json") if path.is_file())


def discover_tools(root: Path, config: CatalogConfig) -> list[Tool]:
    tools = []
    for manifest_path in discover_tool_paths(root, config):
        tools.append(Tool(read_json(manifest_path), manifest_path.parent, root))
    return tools


def is_semver(value: str) -> bool:
    return bool(SEMVER_RE.fullmatch(value))


def iter_package_files(tool: Tool) -> list[Path]:
    """Return the files that belong in a distributable tool package."""
    files: list[Path] = []
    for path in sorted(tool.path.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(tool.path)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        if path.name == "PACKAGE_MANIFEST.json":
            continue
        files.append(path)
    return files


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()
