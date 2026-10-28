#!/usr/bin/env python3
"""Owner-supplied compact stock 48 RJ45 / 4 SFP artwork and exact geometry."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from faceplate_native_canvas import png_dimensions, render_space_calibration

ART = ROOT / "src/faceplates/48rj45-4sfp.png"
OWNER = ROOT / "src/calibration/geometry-stock-48rj45-4sfp-compact.json"
FACTORY = ROOT / "src/calibration/faceplate-stock-48rj45-4sfp.json"
ASSETS = ROOT / "src/custom_components/switch_vision/stock-assets.json"
EXPECTED_ART_SHA = "b69bcff85fc4d682fa19a16a9afabc74afa94de9b86504a69646a487b5c8ccd9"
EXPECTED_OWNER_SHA = "c99793343fd3f353fbc0eb5b01389bc7b2575b8ae9d9847371b8d9d69aa46cd8"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CompactStock48By4Tests(unittest.TestCase):
    def test_original_owner_artwork_and_export_are_exact(self) -> None:
        self.assertEqual(sha256(ART), EXPECTED_ART_SHA)
        self.assertEqual(sha256(OWNER), EXPECTED_OWNER_SHA)
        self.assertEqual(png_dimensions(ART), (6000, 900))
        exported = json.loads(OWNER.read_text(encoding="utf-8"))
        self.assertEqual(exported["transfer_type"], "switch-vision-geometry-profile-v1")
        self.assertEqual(exported["model"], "stock-48rj45-4sfp")
        self.assertEqual(exported["geometry"]["image"]["coordinate_space"], "switch-vision-render-2048x448-v1")
        self.assertEqual(set(exported["geometry"]["ports"]), {str(i) for i in range(1, 49)})
        self.assertEqual(set(exported["geometry"]["sfp"]), {"SFP1", "SFP2", "SFP3", "SFP4"})
        self.assertEqual(len(exported["geometry"]["status_leds"]), 7)

    def test_native_factory_round_trips_every_owner_geometry_value(self) -> None:
        source = json.loads(OWNER.read_text(encoding="utf-8"))["geometry"]
        factory = json.loads(FACTORY.read_text(encoding="utf-8"))
        self.assertEqual(factory["model"], "stock-48rj45-4sfp")
        self.assertEqual(factory["profile"], "stock_48rj45_4sfp")
        self.assertEqual(factory["image"]["file"], "faceplates/48rj45-4sfp.png")
        self.assertEqual(factory["ui"]["faceplate"]["file"], "faceplates/48rj45-4sfp.png")
        self.assertEqual(factory["image"]["coordinate_space"], "image-native-v1")
        self.assertEqual((factory["image"]["width"], factory["image"]["height"]), (6000, 900))
        self.assertFalse(factory["stack"]["enabled"])
        self.assertEqual(factory["management"]["switch_ip"], "")
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
        self.assertEqual(factory["sfp"]["SFP4"]["display_name"], "G4/TE2")

    def test_image_sha_is_bound_to_stock_asset_manifest(self) -> None:
        manifest = json.loads(ASSETS.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["assets"]["faceplates"]["48rj45-4sfp.png"], EXPECTED_ART_SHA
        )


if __name__ == "__main__":
    unittest.main()
