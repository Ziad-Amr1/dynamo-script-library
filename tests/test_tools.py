"""Tests for repository maintenance tools and generated documentation."""

from __future__ import annotations

import json
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
    iter_package_files,
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
                self.assertTrue(
                    all("/legacy/" not in name for name in names),
                    "legacy files must be excluded from release packages",
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


class CarRampGeneratorTests(unittest.TestCase):
    TOOL = ROOT / "scripts" / "geometry" / "car-ramp-generator"
    GRAPH = TOOL / "CarRampGenerator_Revit2025.dyn"

    def _graph(self) -> dict:
        return json.loads(self.GRAPH.read_text(encoding="utf-8-sig"))

    def test_graph_embedded_python_matches_script(self) -> None:
        graph = self._graph()
        nodes = [
            node
            for node in graph["Nodes"]
            if node.get("ConcreteType", "").startswith("PythonNodeModels.PythonNode")
        ]
        self.assertEqual(len(nodes), 1)
        embedded = nodes[0]["Code"]
        script = (self.TOOL / "script.py").read_text(encoding="utf-8-sig")
        self.assertEqual(embedded, script)
        self.assertEqual(nodes[0].get("Engine"), "CPython3")

    def test_graph_has_all_sixteen_inputs_connected(self) -> None:
        graph = self._graph()
        python_node = next(
            node
            for node in graph["Nodes"]
            if node.get("ConcreteType", "").startswith("PythonNodeModels.PythonNode")
        )
        self.assertEqual(len(python_node["Inputs"]), 16)
        input_ids = {port["Id"] for port in python_node["Inputs"]}
        connected = [c for c in graph["Connectors"] if c["End"] in input_ids]
        self.assertEqual(len(connected), 16)
        self.assertEqual(len({c["End"] for c in connected}), 16)
        output_id = python_node["Outputs"][0]["Id"]
        self.assertEqual(
            sum(1 for c in graph["Connectors"] if c["Start"] == output_id), 1
        )

    def test_legacy_folder_is_excluded_from_packages(self) -> None:
        _, config = load_config(ROOT)
        tool = next(
            item for item in discover_tools(ROOT, config) if item.id == "car-ramp-generator"
        )
        self.assertTrue((self.TOOL / "legacy" / "README.md").is_file())
        packaged = {
            path.relative_to(self.TOOL).as_posix() for path in iter_package_files(tool)
        }
        self.assertIn("script.py", packaged)
        self.assertIn("CarRampGenerator_Revit2025.dyn", packaged)
        self.assertFalse(any(name.startswith("legacy/") for name in packaged))


class ParkingNumberingTests(unittest.TestCase):
    TOOL = ROOT / "scripts" / "documentation" / "parking-numbering"
    GRAPH = TOOL / "ParkingNumbering.dyn"

    def _graph(self) -> dict:
        return json.loads(self.GRAPH.read_text(encoding="utf-8"))

    def test_graph_embedded_python_matches_script(self) -> None:
        graph = self._graph()
        python_node = next(n for n in graph["Nodes"] if n.get("Code"))
        script = (self.TOOL / "script.py").read_text(encoding="utf-8")
        self.assertEqual(python_node["Code"], script)
        self.assertEqual(python_node.get("Engine"), "CPython3")

    def test_graph_has_start_number_and_renumber_inputs(self) -> None:
        graph = self._graph()
        self.assertEqual(graph.get("Name"), "Parking Numbering")
        self.assertEqual(len(graph["Nodes"]), 4)
        self.assertEqual(len(graph["Connectors"]), 3)
        python_node = next(n for n in graph["Nodes"] if n.get("Code"))
        self.assertEqual([port["Name"] for port in python_node["Inputs"]], ["IN[0]", "IN[1]"])
        input_ids = {port["Id"] for port in python_node["Inputs"]}
        self.assertEqual(
            sum(1 for c in graph["Connectors"] if c["End"] in input_ids), 2
        )
        double_node = next(
            n for n in graph["Nodes"] if "DoubleInput" in n.get("ConcreteType", "")
        )
        bool_node = next(
            n for n in graph["Nodes"] if "BoolSelector" in n.get("ConcreteType", "")
        )
        views = {v["Id"]: v["Name"] for v in graph["View"]["NodeViews"]}
        self.assertEqual(views.get(double_node["Id"]), "Start number")
        self.assertEqual(views.get(bool_node["Id"]), "Renumber existing labels")

    def test_legacy_folder_is_excluded_from_packages(self) -> None:
        _, config = load_config(ROOT)
        tool = next(
            item for item in discover_tools(ROOT, config) if item.id == "parking-numbering"
        )
        self.assertTrue((self.TOOL / "legacy" / "README.md").is_file())
        packaged = {
            path.relative_to(self.TOOL).as_posix() for path in iter_package_files(tool)
        }
        self.assertIn("script.py", packaged)
        self.assertIn("ParkingNumbering.dyn", packaged)
        self.assertFalse(any(name.startswith("legacy/") for name in packaged))

    def _extract_script_functions(self) -> dict:
        import ast

        code = (self.TOOL / "script.py").read_text(encoding="utf-8")
        tree = ast.parse(code)
        func_nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        module_ast = ast.Module(
            body=[ast.Import(names=[ast.alias(name="re")])] + func_nodes,
            type_ignores=[],
        )
        ast.fix_missing_locations(module_ast)
        ns: dict = {}
        exec(compile(module_ast, "<parking_funcs>", "exec"), ns)
        return ns

    def test_annotation_detection_distinguishes_numbers_from_unrelated_text(self) -> None:
        funcs = self._extract_script_functions()
        is_numbering = funcs["is_numbering_text"]

        numbering_cases = [
            "01", "02", "1", "99", "100", "1001",
            "#01", "# 1", "No. 1", "P-01", "P1", "Bay 12", "SP-04",
        ]
        for text in numbering_cases:
            with self.subTest(text=text):
                self.assertTrue(is_numbering(text), f"Should identify '{text}' as a numbering note")

        unrelated_cases = [
            "RESERVED", "ACCESSIBLE", "HANDICAP", "EV CHARGING ONLY",
            "DO NOT BLOCK", "STAFF ONLY", "VISITOR", "RAMP", "GARAGE ENTRY", "SEE NOTE 4",
        ]
        for text in unrelated_cases:
            with self.subTest(text=text):
                self.assertFalse(is_numbering(text), f"Should ignore unrelated text '{text}'")

    def test_geometric_center_rotated_parking_spaces(self) -> None:
        import math

        class MockXYZ:
            def __init__(self, x: float, y: float, z: float) -> None:
                self.X = float(x)
                self.Y = float(y)
                self.Z = float(z)

        class MockTransform:
            def __init__(self, origin: MockXYZ, angle_rad: float) -> None:
                self.origin = origin
                self.angle = angle_rad

            def OfPoint(self, p: MockXYZ) -> MockXYZ:
                cos_a = math.cos(self.angle)
                sin_a = math.sin(self.angle)
                rx = p.X * cos_a - p.Y * sin_a
                ry = p.X * sin_a + p.Y * cos_a
                return MockXYZ(self.origin.X + rx, self.origin.Y + ry, self.origin.Z + p.Z)

        class MockBBox:
            def __init__(self, w: float, l: float, h: float, origin: MockXYZ, angle_deg: float) -> None:
                self.Min = MockXYZ(-w / 2.0, -l / 2.0, 0.0)
                self.Max = MockXYZ(w / 2.0, l / 2.0, h)
                self.Transform = MockTransform(origin, math.radians(angle_deg))

        funcs = self._extract_script_functions()
        funcs["XYZ"] = MockXYZ
        get_corners = funcs["get_bbox_corners"]

        dimensions = [(2.3, 5.0), (2.4, 5.0), (2.5, 5.0)]
        angles = [0, 30, 45, 60, 90, 135, 180]
        origins = [MockXYZ(0, 0, 0), MockXYZ(12.5, -34.2, 5.0)]

        for w, l in dimensions:
            for ang in angles:
                for orig in origins:
                    bbox = MockBBox(w, l, 0.2, orig, ang)
                    corners = get_corners(bbox)
                    self.assertEqual(len(corners), 8)
                    cx = sum(p.X for p in corners) / 8.0
                    cy = sum(p.Y for p in corners) / 8.0
                    cz = sum(p.Z for p in corners) / 8.0
                    self.assertAlmostEqual(cx, orig.X, places=5)
                    self.assertAlmostEqual(cy, orig.Y, places=5)
                    self.assertAlmostEqual(cz, orig.Z + 0.1, places=5)

    def test_point_distance_function(self) -> None:
        class MockXYZ:
            def __init__(self, x: float, y: float, z: float) -> None:
                self.X = float(x)
                self.Y = float(y)
                self.Z = float(z)

        funcs = self._extract_script_functions()
        pt_dist = funcs["point_distance"]

        p1 = MockXYZ(0, 0, 0)
        p2 = MockXYZ(3, 4, 0)
        self.assertAlmostEqual(pt_dist(p1, p2), 5.0)

    def test_sequential_numbering_when_spaces_are_skipped(self) -> None:
        """Verify that skipping spaces does NOT consume sequential numbers."""
        stalls = [{"id": i, "x": i * 8.0, "y": 0.0} for i in range(5)]
        # Stalls 0 and 2 have existing labels; stalls 1, 3, 4 are empty
        existing_notes = {
            0: {"id": 101, "text": "01"},
            2: {"id": 102, "text": "03"},
        }
        start_number = 1
        renumber_existing = False

        assigned_count = 0
        created = []
        skipped = []

        for stall in stalls:
            has_existing = stall["id"] in existing_notes
            if has_existing and not renumber_existing:
                skipped.append(stall["id"])
                continue

            num = start_number + assigned_count
            created.append({"id": stall["id"], "number": f"{num:02d}"})
            assigned_count += 1

        self.assertEqual(len(skipped), 2)
        self.assertEqual(skipped, [0, 2])
        # Newly assigned numbers must start at 01 and be sequential (01, 02, 03)
        self.assertEqual([c["number"] for c in created], ["01", "02", "03"])
        self.assertEqual([c["id"] for c in created], [1, 3, 4])

    def test_renumbering_mode_updates_existing_labels(self) -> None:
        """Verify that renumber_existing=True updates all spaces starting from 01."""
        stalls = [{"id": i, "x": i * 8.0, "y": 0.0} for i in range(5)]
        existing_notes = {
            0: {"id": 101, "text": "99"},
            2: {"id": 102, "text": "88"},
        }
        start_number = 1
        renumber_existing = True

        assigned_count = 0
        numbered = []
        skipped = []

        for stall in stalls:
            has_existing = stall["id"] in existing_notes
            if has_existing and not renumber_existing:
                skipped.append(stall["id"])
                continue

            num = start_number + assigned_count
            text = f"{num:02d}"
            action = "Updated" if has_existing else "Created"
            numbered.append({"id": stall["id"], "number": text, "action": action})
            assigned_count += 1

        self.assertEqual(len(skipped), 0)
        self.assertEqual(len(numbered), 5)
        self.assertEqual([n["number"] for n in numbered], ["01", "02", "03", "04", "05"])
        self.assertEqual(numbered[0]["action"], "Updated")
        self.assertEqual(numbered[1]["action"], "Created")
        self.assertEqual(numbered[2]["action"], "Updated")

    def test_custom_starting_number(self) -> None:
        """Verify custom starting numbers (e.g. 25, 100)."""
        stalls = [{"id": i} for i in range(3)]
        for start_num, expected in [(25, ["25", "26", "27"]), (100, ["100", "101", "102"])]:
            assigned = [f"{start_num + i:02d}" for i in range(len(stalls))]
            self.assertEqual(assigned, expected)

    def test_proximity_isolates_angled_stalls(self) -> None:
        """Verify that 3.5 ft proximity matches only the stall center and rejects adjacent angled stalls."""
        import math
        # Stall 1 center at (0, 0)
        # Angled stall 2 shifted by 2.4 m (7.87 ft) at 45 degrees
        w = 2.4 * 3.28084
        stall1_center = (0.0, 0.0)
        stall2_center = (w * math.cos(math.radians(45)), w * math.sin(math.radians(45)))

        note_stall1 = (0.0, 0.0)

        dist_self = math.sqrt((note_stall1[0] - stall1_center[0])**2 + (note_stall1[1] - stall1_center[1])**2)
        dist_adjacent = math.sqrt((note_stall1[0] - stall2_center[0])**2 + (note_stall1[1] - stall2_center[1])**2)

        self.assertLess(dist_self, 3.5)
        self.assertGreater(dist_adjacent, 3.5)


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
