"""Protect verified Core changelog continuity and contributor privacy."""
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LegacyChangelogHistoryTests(unittest.TestCase):
    def test_recovered_earliest_verified_versions_are_present(self):
        text = (ROOT / "src" / "CHANGELOG.md").read_text(encoding="utf-8")
        versions = re.findall(r"^## v(\d+)\.(\d+)\.(\d+)\b", text, re.MULTILINE)
        self.assertGreaterEqual(len(set(versions)), 450)
        self.assertTrue(all(version in versions for version in (
            ("0", "9", "0"), ("1", "0", "0"), ("1", "9", "97"),
            ("2", "0", "0"), ("2", "3", "0"), ("2", "4", "0"), ("2", "8", "37"),
        )))
        self.assertEqual(text, (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
        current_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertTrue(text.startswith(f"## v{current_version} "))

    def test_recovered_history_does_not_expose_private_source_identifiers(self):
        text = (ROOT / "src" / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertNotRegex(text, r"\bSV-\d{4}-\d{6}\b")
        self.assertNotIn("switch-vision@zemerdon.com", text)
        self.assertIn("## v0.9.0", text)


if __name__ == "__main__":
    unittest.main()
