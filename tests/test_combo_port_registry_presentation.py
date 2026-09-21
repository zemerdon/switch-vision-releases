from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / "src" / "devices" / "generate_supported_devices.py"
REGISTRY_YAML = ROOT / "src" / "devices" / "supported_devices.yaml"
CARD = ROOT / "src" / "js" / "switch-vision.js"


def load_generator():
    spec = importlib.util.spec_from_file_location("sv_supported_devices_generator", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load supported-device generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ComboPortRegistryPresentationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = load_generator()
        self.registry = yaml.safe_load(REGISTRY_YAML.read_text(encoding="utf-8"))
        self.devices = {row["model"]: row for row in self.registry["devices"]}

    def test_visible_rj45_count_includes_combo_positions(self) -> None:
        expected = {
            "HP ProCurve 1810G-24": 24,
            "SG350-20": 18,
            "HP J8693A Switch 3500yl-48G": 48,
            "GS1900-24E": 24,
        }
        for model, count in expected.items():
            with self.subTest(model=model):
                self.assertEqual(
                    self.generator.visible_rj45_count(self.devices[model]["ports"]),
                    count,
                )

    def test_generated_supported_device_docs_show_physical_socket_counts(self) -> None:
        markdown = self.generator.markdown(self.registry)
        bbcode = self.generator.bbcode(self.registry)
        expected = {
            "HP ProCurve 1810G-24": ("| 24 | 2 Gigabit SFP |", "24 RJ45 + 2 Gigabit SFP"),
            "SG350-20": ("| 18 | 4 Gigabit SFP |", "18 RJ45 + 4 Gigabit SFP"),
            "HP J8693A Switch 3500yl-48G": ("| 48 | 4 Gigabit SFP |", "48 RJ45 + 4 Gigabit SFP"),
        }
        for model, (md_fragment, bb_fragment) in expected.items():
            with self.subTest(model=model):
                md_line = next(line for line in markdown.splitlines() if f"`{model}`" in line)
                bb_line = next(line for line in bbcode.splitlines() if f"[code]{model}[/code]" in line)
                self.assertIn(md_fragment, md_line)
                self.assertIn(bb_fragment, bb_line)

    def test_embedded_visual_recommendations_use_visible_combo_counts(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        match = re.search(r"const SV_DEVICE_VISUAL_RECOMMENDATIONS = (\[.*?\]);", source, re.S)
        self.assertIsNotNone(match)
        rows = {row["model"]: row for row in json.loads(match.group(1))}
        expected = {
            "HP ProCurve 1810G-24": 24,
            "SG350-20": 18,
            "HP J8693A Switch 3500yl-48G": 48,
            "WS-C3750X-48P-S": 48,
        }
        for model, count in expected.items():
            with self.subTest(model=model):
                self.assertIn(model, rows)
                self.assertEqual(rows[model]["rj45"], count)


if __name__ == "__main__":
    unittest.main()
