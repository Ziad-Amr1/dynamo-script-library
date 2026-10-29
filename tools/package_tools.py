#!/usr/bin/env python3
"""Build deterministic, ready-to-use ZIP packages for tool folders.

Each ZIP contains one top-level folder named after the tool id, the tool's
files, and a generated ``PACKAGE_MANIFEST.json`` with hashes. The output
directory also receives an ``index.json`` and ``SHA256SUMS.txt`` file.

Usage:
    python tools/package_tools.py
    python tools/package_tools.py --out dist --tool text-find-replace

The build is reproducible: file order, timestamps, and JSON formatting are
fixed, so rebuilding an unchanged tool produces an identical archive.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

from _common import (
    LibraryError,
    Tool,
    discover_tools,
    find_root,
    iter_package_files,
    load_config,
)

FIXED_DATE = (1980, 1, 1, 0, 0, 0)


def _zip_write(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=FIXED_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def build_package(tool: Tool, out_dir: Path) -> dict[str, object]:
    """Create one tool ZIP and return its index entry."""
    zip_name = f"{tool.id}-v{tool.version}.zip"
    zip_path = out_dir / zip_name
    buffer = io.BytesIO()
    files: list[dict[str, object]] = []

    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in iter_package_files(tool):
            relative = file_path.relative_to(tool.path).as_posix()
            data = file_path.read_bytes()
            _zip_write(archive, f"{tool.id}/{relative}", data)
            files.append(
                {
                    "path": relative,
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
            )

        package_manifest = {
            "package_format": 1,
            "id": tool.id,
            "name": tool.name,
            "version": tool.version,
            "description": tool.description,
            "category": tool.category,
            "status": tool.status,
            "python_engine": tool.manifest.get("python_engine"),
            "entry_points": tool.entry_points,
            "dependencies": tool.manifest.get("dependencies", []),
            "files": files,
        }
        manifest_bytes = (
            json.dumps(package_manifest, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        _zip_write(archive, f"{tool.id}/PACKAGE_MANIFEST.json", manifest_bytes)

    archive_bytes = buffer.getvalue()
    zip_path.write_bytes(archive_bytes)
    return {
        "id": tool.id,
        "name": tool.name,
        "version": tool.version,
        "category": tool.category,
        "status": tool.status,
        "zip": zip_name,
        "bytes": len(archive_bytes),
        "sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "file_count": len(files),
    }


def _clean_output(out_dir: Path) -> None:
    for pattern in ("*.zip", "index.json", "SHA256SUMS.txt"):
        for stale in out_dir.glob(pattern):
            stale.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None, help="Repository root.")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output directory. Defaults to <root>/dist.",
    )
    parser.add_argument(
        "--tool",
        action="append",
        default=None,
        help="Only package this tool id. Repeat to select more than one tool.",
    )
    args = parser.parse_args(argv)

    try:
        root, config = load_config(find_root(args.root))
    except LibraryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    out_dir = (args.out or (root / "dist")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    tools = discover_tools(root, config)
    if args.tool:
        requested = set(args.tool)
        known = {tool.id for tool in tools}
        unknown = sorted(requested - known)
        if unknown:
            print(
                f"error: unknown tool id(s): {', '.join(unknown)}",
                file=sys.stderr,
            )
            return 1
        tools = [tool for tool in tools if tool.id in requested]

    if not tools:
        print("No tools found to package.")
        return 0

    _clean_output(out_dir)
    index: list[dict[str, object]] = []
    for tool in tools:
        entry = build_package(tool, out_dir)
        index.append(entry)
        print(f"Built {entry['zip']} ({entry['file_count']} files).")

    index.sort(key=lambda item: str(item["id"]))
    (out_dir / "index.json").write_text(
        json.dumps({"tools": index}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    checksums = "".join(
        f"{entry['sha256']}  {entry['zip']}\n" for entry in index
    )
    (out_dir / "SHA256SUMS.txt").write_text(
        checksums, encoding="utf-8", newline="\n"
    )
    print(f"Wrote {len(index)} package(s) to {out_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
