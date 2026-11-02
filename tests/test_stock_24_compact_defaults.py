"""Stock 24-port compact defaults must retain topology and calibration identity."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
CANVAS = SOURCE / "faceplate_native_canvas.py"
spec = importlib.util.spec_from_file_location("test_stock_24_canvas", CANVAS)
canvas = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(canvas)


class Stock24CompactDefaultsTests(unittest.TestCase):
    EXPECTED = {
        2: {
            "sha256": "7d2783df6be194a0b5aa200e3f13d57d088bfce06b4347131d91b752ac5d42d7",
            "centers": [(2234, 296), (2463, 296)],
            "display_name": "24 × RJ45 · 2 × SFP · Compact",
        },
        4: {
            "sha256": "ccf4c5d056872c617fc5d16a46968f2dfbe6f18c612474418608e86d4ace1a1c",
            "centers": [(2234, 150), (2473, 150), (2234, 299), (2473, 299)],
            "display_name": "24 × RJ45 · 4 × SFP · Compact",
        },
    }

    def test_current_compact_stock_assets_and_geometry(self):
        import hashlib
        catalog = json.loads((SOURCE / "faceplates" / "catalog.json").read_text())["faceplates"]
        entries = {entry["filename"]: entry["display_name"] for entry in catalog}
        for uplinks, expected in self.EXPECTED.items():
            with self.subTest(uplinks=uplinks):
                slug = f"24rj45-{uplinks}sfp"
                filename = f"{slug}-compact.png"
                png = SOURCE / "faceplates" / filename
                self.assertEqual(canvas.png_dimensions(png), (6000, 750))
                self.assertEqual(hashlib.sha256(png.read_bytes()).hexdigest(), expected["sha256"])
                self.assertEqual(entries[filename], expected["display_name"])

                file = SOURCE / "calibration" / f"faceplate-stock-{slug}-compact.json"
                factory = json.loads(file.read_text())
                self.assertEqual(factory["model"], f"stock-{slug}-compact")
                self.assertEqual(factory["profile"], f"stock_{slug.replace('-', '_')}_compact")
                self.assertEqual(factory["image"]["file"], f"faceplates/{filename}")
                self.assertEqual(factory["ui"]["faceplate"]["file"], filename)
                self.assertEqual(factory["image"]["coordinate_space"], "image-native-v1")
                self.assertEqual(
                    (factory["image"]["width"], factory["image"]["height"]), (6000, 750)
                )
                self.assertEqual(set(factory["ports"]), {str(i) for i in range(1, 25)})
                self.assertEqual(set(factory["sfp"]), {f"G{i}" for i in range(1, uplinks + 1)})
                self.assertNotIn("source_scope", factory)
                self.assertNotIn("source_base_profile", factory)
                self.assertNotIn("source_profile", factory)
                self.assertFalse(factory["stack"]["enabled"])

                rendered = canvas.render_space_calibration(factory)
                self.assertEqual(rendered["ports"]["1"]["center"], [874, 143])
                self.assertEqual(rendered["ports"]["24"]["center"], [2054, 303])
                self.assertEqual(
                    [rendered["sfp"][f"G{i}"]["center"] for i in range(1, uplinks + 1)],
                    [list(pair) for pair in expected["centers"]],
                )
                for index in range(1, uplinks + 1):
                    self.assertEqual(rendered["sfp"][f"G{index}"]["display_name"].split("/")[0], f"G{index}")
                self.assertEqual(
                    set(rendered["status_leds"]),
                    {"STAT", "SYST", "DUPLX", "ACTV", "SPEED", "STACK", "PoE"},
                )
                self.assertEqual(set(rendered["ui"]["status_leds"]["hidden"]), set(rendered["status_leds"]))
                self.assertEqual(rendered["ui"]["faceplate"]["fit"], "fill")

    def test_default_mapping_keeps_legacy_stock_profile_and_per_switch_upgrade(self):
        js = (SOURCE / "js" / "switch-vision.js").read_text()
        for uplinks in (2, 4):
            slug = f"24rj45-{uplinks}sfp"
            self.assertIn(f'stock_{slug.replace("-", "_")}: "{slug}.png"', js)
            self.assertIn(f'stock_{slug.replace("-", "_")}_compact: "{slug}-compact.png"', js)
        self.assertIn("function faceplateFactoryCalibrationForFile(", js)
        self.assertIn("this.factoryCalibrationForCurrentSwitch(", js)
        self.assertIn("await this.resetSavedCalibrations(\"switch\")", js)


if __name__ == "__main__":
    unittest.main()
