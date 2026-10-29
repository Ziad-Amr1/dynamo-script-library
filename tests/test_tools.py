"""Tests for repository maintenance tools and generated documentation."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_links  # noqa: E402
import generate_catalog  # noqa: E402
import new_tool  # noqa: E402
import package_tools  # noqa: E402
import validate_manifests  # noqa: E402
from _common import (  # noqa: E402
    LibraryError,
    discover_tools,
    is_semver,
    load_config,
    load_yaml,
)


class CommonTests(unittest.TestCase):
    def test_semver(self) -> None:
        for value in ("0.1.0", "1.2.3", "10.20.30", "1.0.0-rc.1", "1.0.0+build.5"):
            self.assertTrue(is_semver(value), value)
        for value in ("1.0", "1.0.0.0", "v1.0.0", "01.0.0", "1.0.0-"):
            self.assertFalse(is_semver(value), value)

    def test_yaml_parser_rejects_tabs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "config.yml"
            path.write_text("categories:\n\t- id: test\n", encoding="utf-8")
            with self.assertRaises(LibraryError):
                load_yaml(path)

    def test_config_has_expected_categories(self) -> None:
        _, config = load_config(ROOT)
        self.assertIn("utilities", config.category_ids)
        self.assertIn("sheets-and-views", config.category_ids)
        self.assertEqual(config.status_label("development"), "Development")


class RepositoryValidationTests(unittest.TestCase):
    def test_manifests_are_valid(self) -> None:
        root, config = load_config(ROOT)
        errors = validate_manifests.validate_repository(root, config)
        self.assertEqual(errors, [])

    def test_catalog_is_up_to_date(self) -> None:
        root, config = load_config(ROOT)
        readme_path, expected = generate_catalog.build_expected_readme(root, config)
        self.assertEqual(
            readme_path.read_text(encoding="utf-8"),
            expected,
            "README catalog is stale; run python tools/generate_catalog.py",
        )

    def test_catalog_lists_reference_tool(self) -> None:
        root, config = load_config(ROOT)
        tools = discover_tools(root, config)
        rendered = generate_catalog.render_catalog(tools, config)
        self.assertIn("text-find-replace/README.md", rendered)
        self.assertIn("Text Find & Replace", rendered)
        self.assertIn("Development", rendered)

    def test_relative_links_resolve(self) -> None:
        root, _ = load_config(ROOT)
        errors = []
        for path in check_links._iter_markdown(root):
            errors.extend(check_links.check_file(path, root))
        self.assertEqual(errors, [])


class PackagingTests(unittest.TestCase):
    def test_package_is_deterministic_and_contains_manifest(self) -> None:
        root, config = load_config(ROOT)
        tool = discover_tools(root, config)[0]
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_entry = package_tools.build_package(tool, Path(first))
            second_entry = package_tools.build_package(tool, Path(second))
            first_zip = Path(first) / str(first_entry["zip"])
            second_zip = Path(second) / str(second_entry["zip"])
            self.assertEqual(first_zip.read_bytes(), second_zip.read_bytes())
            self.assertEqual(first_entry["sha256"], second_entry["sha256"])

            with zipfile.ZipFile(first_zip) as archive:
                names = archive.namelist()
                self.assertIn(f"{tool.id}/README.md", names)
                self.assertIn(f"{tool.id}/PACKAGE_MANIFEST.json", names)
                self.assertIn(f"{tool.id}/script.py", names)
                self.assertTrue(
                    all(not name.startswith("__pycache__") for name in names)
                )


class NewToolTests(unittest.TestCase):
    def test_scaffold_creates_a_valid_tool(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            (temp_root / ".github").mkdir()
            shutil.copy2(
                ROOT / ".github" / "scripts-catalog.yml",
                temp_root / ".github" / "scripts-catalog.yml",
            )
            for category in (
                "model-management",
                "sheets-and-views",
                "parameters",
                "families",
                "geometry",
                "documentation",
                "utilities",
            ):
                (temp_root / "scripts" / category).mkdir(parents=True, exist_ok=True)
            shutil.copytree(
                ROOT / "templates" / "tool-package",
                temp_root / "templates" / "tool-package",
            )

            exit_code = new_tool.main(
                [
                    "--root",
                    str(temp_root),
                    "--id",
                    "sample-tool",
                    "--name",
                    "Sample Tool",
                    "--category",
                    "utilities",
                    "--description",
                    "A synthetic tool used to validate the scaffolder.",
                ]
            )
            self.assertEqual(exit_code, 0)

            root, config = load_config(temp_root)
            tools = discover_tools(root, config)
            self.assertEqual(len(tools), 1)
            tool = tools[0]
            self.assertEqual(tool.id, "sample-tool")
            self.assertEqual(tool.version, "0.1.0")
            errors = validate_manifests.validate_tool(tool, config)
            self.assertEqual(errors, [])

            readme = (tool.path / "README.md").read_text(encoding="utf-8")
            self.assertNotIn("{{", readme)

    def test_render_rejects_unresolved_placeholders(self) -> None:
        with self.assertRaises(LibraryError):
            new_tool._render("Hello {{name}} {{missing}}", {"name": "World"})

    def test_refuses_to_overwrite_existing_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            (temp_root / ".github").mkdir()
            shutil.copy2(
                ROOT / ".github" / "scripts-catalog.yml",
                temp_root / ".github" / "scripts-catalog.yml",
            )
            for category in (
                "model-management",
                "sheets-and-views",
                "parameters",
                "families",
                "geometry",
                "documentation",
                "utilities",
            ):
                (temp_root / "scripts" / category).mkdir(parents=True, exist_ok=True)
            shutil.copytree(
                ROOT / "templates" / "tool-package",
                temp_root / "templates" / "tool-package",
            )
            existing = temp_root / "scripts" / "utilities" / "sample-tool"
            existing.mkdir()

            exit_code = new_tool.main(
                [
                    "--root",
                    str(temp_root),
                    "--id",
                    "sample-tool",
                    "--name",
                    "Sample Tool",
                    "--category",
                    "utilities",
                    "--description",
                    "Should not overwrite.",
                ]
            )
            self.assertEqual(exit_code, 1)


class LinkCheckerTests(unittest.TestCase):
    def test_reports_missing_relative_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs = root / "docs"
            docs.mkdir()
            (root / "exists.md").write_text("# Exists\n", encoding="utf-8")
            page = docs / "page.md"
            page.write_text(
                "[ok](../exists.md)\n[bad](missing.md)\n[web](https://example.com)\n",
                encoding="utf-8",
            )
            errors = check_links.check_file(page, root)
            self.assertEqual(len(errors), 1)
            self.assertIn("missing.md", errors[0])


if __name__ == "__main__":
    unittest.main()
