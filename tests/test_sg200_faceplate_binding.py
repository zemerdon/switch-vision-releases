#!/usr/bin/env python3
"""Cisco SG200-26 exact owner artwork, geometry and independent physical mapping."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from faceplate_native_canvas import render_space_calibration
REGISTRY = ROOT / "src/devices/supported_devices.json"
FACEPLATE = ROOT / "src/faceplates/cisco-sg200-26.png"
GEOMETRY = ROOT / "src/calibration/geometry-cisco-sg200-26.json"
PROFILE = ROOT / "src/calibration/faceplate-cisco-sg200-26.json"
STOCK = ROOT / "src/calibration/faceplate-stock-24rj45-2sfp.json"

SOURCE_PNG_SHA256 = "680a0d1f38f9455b5b172606960e8a5059be8afbad900f5ff9c48c8a05e39ebe"
SOURCE_GEOMETRY_SHA256 = "2b1a49ae002888b57814b6534ad888d9f44e341b32b7e39b61ac55fa33a9a0d1"


class SG200FaceplateBindingTests(unittest.TestCase):
    def test_exact_sg200_is_the_only_default(self) -> None:
        registry = json.loads(REGISTRY.read_text())
        rows = [r for r in registry["devices"] if r.get("model") == "SG200-26"]
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["ports"]["rj45"], 24)
        self.assertEqual(row["ports"]["uplinks"], 2)
        self.assertEqual(row["ports"]["combo_ports"], 2)
        self.assertEqual(row["ports"]["combo_logical_ports"], [25, 26])
        self.assertEqual(row["mapping_profile"], "cisco-sg200-26-24p-2dual")
        self.assertEqual(row["default_faceplate"], "faceplates/cisco-sg200-26.png")
        self.assertEqual(row["calibration_profile"], "cisco_sg200_26")
        source = (ROOT / "src/js/switch-vision.js").read_text(encoding="utf-8")
        self.assertIn('cisco_sg200_26: "cisco-sg200-26.png"', source)
        self.assertEqual(row["optional_faceplates"], [])
        self.assertEqual(row["visuals"]["recommended_faceplate"], row["default_faceplate"])
        self.assertEqual(row["visuals"]["calibration_profile"], row["calibration_profile"])
        self.assertEqual(row["visuals"]["optional_faceplates"], [])

    def test_original_png_and_json_are_byte_identical(self) -> None:
        self.assertEqual(hashlib.sha256(FACEPLATE.read_bytes()).hexdigest(), SOURCE_PNG_SHA256)
        self.assertEqual(hashlib.sha256(GEOMETRY.read_bytes()).hexdigest(), SOURCE_GEOMETRY_SHA256)

    def test_renderer_round_trip_preserves_exact_source_geometry(self) -> None:
        raw = json.loads(GEOMETRY.read_text())
        source = raw["geometry"]
        native = json.loads(PROFILE.read_text())
        rendered = render_space_calibration(native)
        self.assertEqual(raw["schema_version"], 2)
        self.assertEqual(raw["transfer_type"], "switch-vision-geometry-profile-v1")
        self.assertEqual(native["profile"], "cisco_sg200_26")
        self.assertEqual(native["model"], "cisco-sg200-26")
        self.assertEqual(native["image"]["file"], "faceplates/cisco-sg200-26.png")
        self.assertEqual(native["image"]["coordinate_space"], "image-native-v1")
        self.assertEqual((native["image"]["width"], native["image"]["height"]), (1935, 257))
        self.assertEqual(set(native["ports"]), {str(i) for i in range(1, 27)})
        self.assertEqual(set(native["sfp"]), {"SFP1", "SFP2"})
        self.assertEqual(native["ui"]["faceplate"]["file"], "cisco-sg200-26.png")
        self.assertEqual(native["ui"]["logo"]["show"], False)

        def assert_same(expected, actual, where="geometry"):
            if isinstance(expected, dict):
                self.assertIsInstance(actual, dict, where)
                for key, value in expected.items():
                    self.assertIn(key, actual, where)
                    assert_same(value, actual[key], where + "." + key)
            elif isinstance(expected, list):
                self.assertIsInstance(actual, list, where)
                self.assertEqual(len(expected), len(actual), where)
                for index, (a, b) in enumerate(zip(expected, actual)):
                    assert_same(a, b, where + "." + str(index))
            elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
                self.assertAlmostEqual(float(expected), float(actual), delta=2e-7, msg=where)
            else:
                self.assertEqual(expected, actual, where)

        for section in ("ports", "sfp", "status_leds", "ui"):
            assert_same(source[section], rendered[section], section)
        self.assertEqual(rendered["image"]["width"], source["image"]["width"])
        self.assertEqual(rendered["image"]["height"], source["image"]["height"])

    def test_other_stock_factory_remains_unchanged(self) -> None:
        profile = json.loads(STOCK.read_text())
        self.assertEqual(profile["profile"], "stock_24rj45_2sfp")
        self.assertEqual(profile["image"]["file"], "faceplates/24rj45-2sfp.png")
        self.assertEqual(len(profile["ports"]), 24)
        self.assertEqual(len(profile["sfp"]), 2)


if __name__ == "__main__":
    unittest.main()
