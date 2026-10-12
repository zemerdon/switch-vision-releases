#!/usr/bin/env python3
"""HP 3500yl-48G owner geometry preserved independently of capture test switch."""
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from faceplate_native_canvas import render_space_calibration, png_dimensions

MODEL = "HP J8693A Switch 3500yl-48G"
FILE = "hp-3500yl-48g.png"
PROFILE = "hp_3500yl_48g"
PNG_HASH = "bb7d88a3b8b5faaa64557a12783bc1f4386ee488fcce175f0126a99272734c3d"
GEOM_HASH = "3a256baf49090d9b07381064be1529dbc5054aa9bbef07313c903030e21bface"


class HP3500ylFaceplateTests(unittest.TestCase):
    def test_artwork_and_raw_geometry_untouched(self):
        png = ROOT / "src/faceplates" / FILE
        raw = ROOT / "src/calibration/geometry-hp-3500yl-48g.json"
        self.assertEqual(png_dimensions(png), (6000, 1600))
        self.assertEqual(hashlib.sha256(png.read_bytes()).hexdigest(), PNG_HASH)
        self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(), GEOM_HASH)

    def test_original_geometry_survives_renderer_transform(self):
        raw = json.loads((ROOT / "src/calibration/geometry-hp-3500yl-48g.json").read_text())["geometry"]
        native = json.loads((ROOT / "src/calibration/faceplate-hp-3500yl-48g.json").read_text())
        self.assertEqual(native["model"], "hp-3500yl-48g")
        self.assertEqual(native["profile"], PROFILE)
        self.assertEqual(native["image"]["coordinate_space"], "image-native-v1")
        self.assertEqual((native["image"]["width"], native["image"]["height"]), (6000, 1600))
        self.assertEqual(native["ui"]["faceplate"]["file"], FILE)
        self.assertEqual(set(native["ports"]), {str(i) for i in range(1, 49)})
        self.assertEqual(set(native["sfp"]), {"SFP1", "SFP2", "SFP3", "SFP4", "rSFP1", "rSFP2", "rSFP3", "rSFP4"})
        render = render_space_calibration(native)

        def compare(expected, actual, where):
            if isinstance(expected, dict):
                self.assertIsInstance(actual, dict, where)
                for k, v in expected.items():
                    self.assertIn(k, actual, where)
                    compare(v, actual[k], where + "." + k)
            elif isinstance(expected, list):
                self.assertEqual(len(expected), len(actual), where)
                for i, (x, y) in enumerate(zip(expected, actual)):
                    compare(x, y, where + "." + str(i))
            elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
                self.assertAlmostEqual(expected, actual, delta=2e-7, msg=where)
            else:
                self.assertEqual(expected, actual, where)

        for section in ("ports", "sfp", "status_leds", "ui"):
            compare(raw[section], render[section], section)

    def test_hp_exact_default_and_mapping_unchanged(self):
        devices = json.loads((ROOT / "src/devices/supported_devices.json").read_text())["devices"]
        matching = [d for d in devices if d.get("model") == MODEL]
        self.assertEqual(len(matching), 1)
        d = matching[0]
        self.assertEqual(d["ports"]["rj45"], 44)
        self.assertEqual(d["ports"]["combo_logical_ports"], [45, 46, 47, 48])
        self.assertEqual(d["ports"]["gigabit_sfp"], 4)
        self.assertEqual(d["mapping_profile"], "hp-3500yl-48g-44p-4dual")
        self.assertEqual(d["status"], "experimental")
        self.assertEqual(d["default_faceplate"], "faceplates/" + FILE)
        self.assertEqual(d["calibration_profile"], PROFILE)
        self.assertEqual(d["visuals"]["recommended_faceplate"], d["default_faceplate"])
        self.assertEqual(d["visuals"]["calibration_profile"], PROFILE)
        source = (ROOT / "src/js/switch-vision.js").read_text()
        self.assertIn('hp_3500yl_48g: "hp-3500yl-48g.png"', source)
        catalog = json.loads((ROOT / "src/faceplates/catalog.json").read_text())
        self.assertEqual(sum(x["filename"] == FILE for x in catalog["faceplates"]), 1)
        self.assertEqual(d["optional_faceplates"], [])


if __name__ == "__main__":
    unittest.main()
