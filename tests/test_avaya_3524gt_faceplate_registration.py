from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.faceplate_native_canvas import png_dimensions, render_space_calibration

PNG = ROOT / "src/faceplates/avaya-3524gt.png"
PROFILE = ROOT / "src/calibration/faceplate-avaya-3524gt.json"
CATALOG = ROOT / "src/faceplates/catalog.json"
MANIFEST = ROOT / "src/custom_components/switch_vision/stock-assets.json"
REGISTRY = ROOT / "src/devices/supported_devices.yaml"


class AvayaFaceplateRegistrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = json.loads(PROFILE.read_text(encoding="utf-8"))

    def test_registration_is_selectable_and_has_integrity_hash(self) -> None:
        self.assertEqual(png_dimensions(PNG), (2925, 323))
        rows = json.loads(CATALOG.read_text(encoding="utf-8"))["faceplates"]
        self.assertEqual(len([row for row in rows if row["filename"] == PNG.name]), 1)
        hashes = json.loads(MANIFEST.read_text(encoding="utf-8"))["assets"]["faceplates"]
        self.assertEqual(hashes[PNG.name], hashlib.sha256(PNG.read_bytes()).hexdigest())
        self.assertEqual(self.profile["model"], "avaya-3524gt")
        self.assertEqual(self.profile["profile"], "avaya_3524gt")
        self.assertEqual(self.profile["image"]["file"], "faceplates/avaya-3524gt.png")
        self.assertEqual(self.profile["ui"]["faceplate"]["file"], PNG.name)
        self.assertEqual(self.profile["image"]["coordinate_space"], "image-native-v1")

    def test_sw1_export_does_not_change_model_contract(self) -> None:
        self.assertEqual(list(self.profile["ports"]), [str(i) for i in range(1, 25)])
        self.assertEqual(list(self.profile["sfp"]), [f"SFP{i}" for i in range(1, 5)])
        self.assertNotIn("SW1", json.dumps(self.profile))
        self.assertNotIn("stock-48rj45", json.dumps(self.profile))
        models = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))["devices"]
        avaya = next(row for row in models if row["model"] == "3524GT-PWR+")
        self.assertEqual(avaya["default_faceplate"], "faceplates/avaya-3524gt.png")
        self.assertEqual(avaya["calibration_profile"], "avaya_3524gt")
        self.assertEqual(avaya["optional_faceplates"], [])
        self.assertEqual(avaya["visuals"]["optional_faceplates"], [])
        self.assertEqual(avaya["ports"]["combo_logical_ports"], [21, 22, 23, 24])
        self.assertEqual(avaya["ports"]["combo_ports"], 4)

    def test_owner_geometry_is_preserved_with_native_renderer(self) -> None:
        self.assertEqual(self.profile["image"]["width"], 2925)
        self.assertEqual(self.profile["image"]["height"], 323)
        render = render_space_calibration(self.profile)
        representative = [
            ("ports", "1", [606.549333333, 174.677333333]),
            ("ports", "21", [2047.658666667, 174.677333333]),
            ("ports", "24", [2182.826666667, 301.994666667]),
            ("sfp", "SFP1", [2396.842666667, 170.581333333]),
            ("sfp", "SFP4", [2584.576, 307.114666667]),
        ]
        for category, key, expected in representative:
            with self.subTest(category=category, key=key):
                self.assertEqual(len(render[category][key]["center"]), 2)
                for actual, wanted in zip(render[category][key]["center"], expected):
                    self.assertAlmostEqual(actual, wanted, places=7)
        for category in ("ports", "sfp"):
            for key, port in self.profile[category].items():
                x, y = port["center"]
                w, h = port["hitbox"]
                self.assertGreaterEqual(x - w / 2, 0, key)
                self.assertLessEqual(x + w / 2, 2925, key)
                self.assertGreaterEqual(y - h / 2, 0, key)
                self.assertLessEqual(y + h / 2, 323, key)


if __name__ == "__main__":
    unittest.main()
