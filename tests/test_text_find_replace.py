"""Tests for the Text Find & Replace reference tool."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "utilities"
    / "text-find-replace"
    / "script.py"
)

spec = importlib.util.spec_from_file_location("text_find_replace_script", SCRIPT_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {SCRIPT_PATH}")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

find_replace = module.find_replace
plan_changes = module.plan_changes


class FindReplaceTests(unittest.TestCase):
    def test_literal_replacement_all_occurrences(self) -> None:
        result = find_replace(["GF-Lobby", "GF-Office", "GF"], "GF-", "L0-")
        self.assertEqual(result, ["L0-Lobby", "L0-Office", "GF"])

    def test_input_is_not_mutated(self) -> None:
        values = ["A-101", "A-102"]
        result = find_replace(values, "A-", "A-ARCH-")
        self.assertEqual(values, ["A-101", "A-102"])
        self.assertIsNot(result, values)

    def test_case_insensitive(self) -> None:
        result = find_replace(
            ["Level 1", "level 2", "LEVEL 3"], "level", "L", case_sensitive=False
        )
        self.assertEqual(result, ["L 1", "L 2", "L 3"])

    def test_case_sensitive_default(self) -> None:
        result = find_replace(["Level", "level"], "level", "L")
        self.assertEqual(result, ["Level", "L"])

    def test_whole_value(self) -> None:
        result = find_replace(["A", "B", "AB"], "A", "X", whole_value=True)
        self.assertEqual(result, ["X", "B", "AB"])

    def test_whole_value_case_insensitive(self) -> None:
        result = find_replace(
            ["A", "a", "AB"], "a", "X", case_sensitive=False, whole_value=True
        )
        self.assertEqual(result, ["X", "X", "AB"])

    def test_regex_with_backreference(self) -> None:
        result = find_replace(
            ["Level 01", "Level 02", "Level 10"],
            r"Level (\d+)",
            r"L\1",
            use_regex=True,
        )
        self.assertEqual(result, ["L01", "L02", "L10"])

    def test_regex_whole_value_anchors_pattern(self) -> None:
        result = find_replace(
            ["A-101", "A-101 extra"], r"A-\d+", "MATCH", use_regex=True, whole_value=True
        )
        self.assertEqual(result, ["MATCH", "A-101 extra"])

    def test_literal_replacement_does_not_expand_backreferences(self) -> None:
        result = find_replace(["value"], "value", r"\1")
        self.assertEqual(result, [r"\1"])

    def test_empty_find_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            find_replace(["value"], "")

    def test_invalid_regex_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            find_replace(["value"], "(", use_regex=True)

    def test_single_string_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            find_replace("A-101", "A", "B")

    def test_non_string_value_is_rejected_with_index(self) -> None:
        with self.assertRaisesRegex(TypeError, r"values\[1\]"):
            find_replace(["ok", 42], "x", "y")

    def test_non_string_replace_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            find_replace(["value"], "value", None)

    def test_plan_changes_only_returns_changes(self) -> None:
        changes = plan_changes(["A-101", "B-201", "A-102"], "A-", "A-ARCH-")
        self.assertEqual(
            changes,
            [
                {"index": 0, "before": "A-101", "after": "A-ARCH-101"},
                {"index": 2, "before": "A-102", "after": "A-ARCH-102"},
            ],
        )

    def test_tuple_input_is_supported(self) -> None:
        self.assertEqual(find_replace(("a", "b"), "a", "x"), ["x", "b"])


if __name__ == "__main__":
    unittest.main()
