#!/usr/bin/env python3
"""Owner-supplied 48 RJ45 / 2 SFP compact stock artwork and exact Geometry."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from faceplate_native_canvas import png_dimensions, render_space_calibration

ART = ROOT / "src/faceplates/48rj45-2sfp.png"
OWNER = ROOT / "src/calibration/geometry-stock-48rj45-2sfp-compact.json"
FACTORY = ROOT / "src/calibration/faceplate-stock-48rj45-2sfp.json"
ASSETS = ROOT / "src/custom_components/switch_vision/stock-assets.json"
ART_SHA = "b397891df10499016b0617d0967ec90269493e5708df6b5d8d4c76460934f772"
OWNER_SHA = "b1f730aea388d9a3cd9cfbc267481e29aabdf115d95a590d958d044c6a9cf148"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CompactStock48By2Tests(unittest.TestCase):
    def test_exact_original_artwork_and_geometry_transfer(self) -> None:
        self.assertEqual(sha256(ART), ART_SHA)
        self.assertEqual(sha256(OWNER), OWNER_SHA)
        self.assertEqual(png_dimensions(ART), (6000, 900))
        source = json.loads(OWNER.read_text(encoding="utf-8"))
        self.assertEqual(source["transfer_type"], "switch-vision-geometry-profile-v1")
        self.assertEqual(source["geometry"]["image"]["coordinate_space"], "switch-vision-render-2048x448-v1")
        self.assertEqual(set(source["geometry"]["ports"]), {str(i) for i in range(1, 49)})
        self.assertEqual(set(source["geometry"]["sfp"]), {"SFP1", "SFP2"})
        self.assertEqual(len(source["geometry"]["status_leds"]), 7)
        # The owner export was made from a 48/4 Custom source. The factory
        # identity must reflect the target 48/2 topology, not that source.
        self.assertEqual(source["model"], "stock-48rj45-4sfp")

    def test_new_factory_preserves_all_exported_geometry(self) -> None:
        source = json.loads(OWNER.read_text(encoding="utf-8"))["geometry"]
        factory = json.loads(FACTORY.read_text(encoding="utf-8"))
        self.assertEqual(factory["schema"], "switch-vision-interactive-calibration-v1")
        self.assertEqual(factory["model"], "stock-48rj45-2sfp")
        self.assertEqual(factory["profile"], "stock_48rj45_2sfp")
        self.assertEqual(factory["image"]["file"], "faceplates/48rj45-2sfp.png")
        self.assertEqual(factory["ui"]["faceplate"]["file"], "faceplates/48rj45-2sfp.png")
        self.assertEqual(factory["image"]["coordinate_space"], "image-native-v1")
        self.assertEqual((factory["image"]["width"], factory["image"]["height"]), (6000, 900))
        self.assertFalse(factory["stack"]["enabled"])
        self.assertEqual(factory["management"]["switch_ip"], "")
        self.assertEqual(set(factory["sfp"]), {"SFP1", "SFP2"})
        rendered = render_space_calibration(factory)
        self.assertEqual((rendered["image"]["width"], rendered["image"]["height"]), (2048, 448))

        def compare(expected: object, actual: object, path: str) -> None:
            if isinstance(expected, dict):
                self.assertIsInstance(actual, dict, path)
                for key, value in expected.items():
                    self.assertIn(key, actual, path)
                    compare(value, actual[key], f"{path}.{key}")
            elif isinstance(expected, list):
                self.assertIsInstance(actual, list, path)
                self.assertEqual(len(expected), len(actual), path)
                for index, (left, right) in enumerate(zip(expected, actual)):
                    compare(left, right, f"{path}[{index}]")
            elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
                self.assertAlmostEqual(expected, actual, delta=2e-7, msg=path)
            else:
                self.assertEqual(expected, actual, path)

        for section in ("ports", "sfp", "status_leds", "ui"):
            compare(source[section], rendered[section], section)
        self.assertEqual(factory["sfp"]["SFP1"]["display_name"], "G1")
        self.assertEqual(factory["sfp"]["SFP2"]["display_name"], "G2")

    def test_stock_manifest_hashes_current_image(self) -> None:
        manifest = json.loads(ASSETS.read_text(encoding="utf-8"))
        self.assertEqual(manifest["assets"]["faceplates"]["48rj45-2sfp.png"], ART_SHA)


if __name__ == "__main__":
    unittest.main()
