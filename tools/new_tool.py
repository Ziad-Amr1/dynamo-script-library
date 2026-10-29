#!/usr/bin/env python3
"""Scaffold a new tool package from templates/tool-package.

Usage:
    python tools/new_tool.py --id my-tool --name "My Tool" \
        --category utilities --description "What the tool does."

The command creates scripts/<category>/<id>/ with README.md, CHANGELOG.md,
script.json, and a Python starter file. It never overwrites an existing folder.
After implementing the tool, update the manifest, run the checks, and regenerate
the catalog as described in docs/ADDING-A-SCRIPT.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

from _common import ID_RE, LibraryError, find_root, load_config

TEMPLATE_FILES = ("README.md", "CHANGELOG.md", "script.json", "script.py")


def _render(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    leftover = sorted(set(re.findall(r"\{\{([a-z_]+)\}\}", rendered)))
    if leftover:
        raise LibraryError(f"Unresolved template placeholder(s): {', '.join(leftover)}")
    return rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None, help="Repository root.")
    parser.add_argument("--id", required=True, help="Kebab-case tool id and folder name.")
    parser.add_argument("--name", required=True, help="Human-readable tool name.")
    parser.add_argument("--category", required=True, help="Category folder under scripts/.")
    parser.add_argument("--description", required=True, help="One-sentence description (max 200 characters).")
    parser.add_argument(
        "--python-engine",
        default="CPython 3",
        help="Python engine recorded in the manifest. Defaults to 'CPython 3'.",
    )
    parser.add_argument("--version", default="0.1.0", help="Initial version. Defaults to 0.1.0.")
    args = parser.parse_args(argv)

    try:
        root, config = load_config(find_root(args.root))
    except LibraryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if not ID_RE.fullmatch(args.id):
        print(
            "error: --id must be lowercase kebab-case, for example 'batch-sheet-creator'.",
            file=sys.stderr,
        )
        return 1
    if args.category not in config.category_ids:
        print(
            f"error: category '{args.category}' is not configured. "
            f"Choose one of: {', '.join(config.category_ids)}",
            file=sys.stderr,
        )
        return 1
    if len(args.description) > 200:
        print("error: --description must be 200 characters or fewer.", file=sys.stderr)
        return 1

    tool_dir = root / config.tools_dir / args.category / args.id
    if tool_dir.exists():
        print(f"error: {tool_dir} already exists; refusing to overwrite.", file=sys.stderr)
        return 1

    template_dir = root / "templates" / "tool-package"
    if not template_dir.is_dir():
        print(f"error: template folder not found: {template_dir}", file=sys.stderr)
        return 1

    values = {
        "id": args.id,
        "name": args.name,
        "description": args.description,
        "category": args.category,
        "version": args.version,
        "python_engine": args.python_engine,
        "date": dt.date.today().isoformat(),
    }

    tool_dir.mkdir(parents=True)
    for filename in TEMPLATE_FILES:
        template_path = template_dir / filename
        if not template_path.is_file():
            print(f"error: missing template file: {template_path}", file=sys.stderr)
            return 1
        content = _render(template_path.read_text(encoding="utf-8"), values)
        (tool_dir / filename).write_text(content, encoding="utf-8", newline="\n")

    print(f"Created {tool_dir.relative_to(root)}")
    print("Next steps:")
    print("  1. Implement the Dynamo graph and/or Python logic.")
    print("  2. Complete README.md and script.json (verified compatibility only).")
    print("  3. Add tests for Python logic under tests/.")
    print("  4. python -m unittest discover -s tests -v")
    print("  5. python tools/validate_manifests.py")
    print("  6. python tools/generate_catalog.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
