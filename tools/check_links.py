#!/usr/bin/env python3
"""Check relative links and images in repository Markdown files.

External URLs, anchors, and template placeholders are ignored. Links to files
that do not exist are reported with their file and line number.

Usage:
    python tools/check_links.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

from _common import SKIP_DIRS, find_root

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:")
EXCLUDED_DIRS = SKIP_DIRS | {"templates"}


def _iter_markdown(root: Path) -> list[Path]:
    files = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        files.append(path)
    return files


def _extract_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split()[0] if target.split() else ""
    return target.strip()


def check_file(path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for match in LINK_RE.finditer(text):
        target = _extract_target(match.group(1))
        if not target or target.startswith(EXTERNAL_PREFIXES) or target.startswith("#"):
            continue
        if "{{" in target or target.startswith("//"):
            continue
        target_without_anchor = unquote(target.split("#", 1)[0].split("?", 1)[0])
        if not target_without_anchor:
            continue
        if target_without_anchor.startswith("/"):
            resolved = (root / target_without_anchor.lstrip("/")).resolve()
        else:
            resolved = (path.parent / target_without_anchor).resolve()
        if not resolved.exists():
            line_number = text.count("\n", 0, match.start()) + 1
            errors.append(
                f"{path.relative_to(root).as_posix()}:{line_number}: "
                f"broken link '{target}'"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None, help="Repository root.")
    args = parser.parse_args(argv)

    root = find_root(args.root)
    errors: list[str] = []
    files = _iter_markdown(root)
    for path in files:
        errors.extend(check_file(path, root))

    if errors:
        print(f"Found {len(errors)} broken link(s):", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"Checked {len(files)} Markdown file(s); all relative links resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
