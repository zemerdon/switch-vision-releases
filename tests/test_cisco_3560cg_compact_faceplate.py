#!/usr/bin/env python3
"""Owner Cisco 3560CG Compact artwork: original isolation, exact model and native projection."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from faceplate_native_canvas import png_dimensions, render_space_calibration

IMAGE = ROOT / "src/faceplates/c3560cg-8pc-s-compact.png"
OWNER_GEOMETRY = ROOT / "src/calibration/geometry-c3560cg-8pc-s-compact.json"
FACTORY = ROOT / "src/calibration/faceplate-c3560cg-8pc-s-compact.json"
ORIGINAL = ROOT / "src/faceplates/c3560cg-8pc-s.png"
REGISTRY = ROOT / "src/devices/supported_devices.json"
CATALOG = ROOT / "src/faceplates/catalog.json"
OLD_LABEL = "Cisco Catalyst 3560CG-8PC-S · 8 × RJ45 · 2 × SFP"
MODEL = "WS-C3560CG-8PC-S"


class Cisco3560CGCompactFaceplateTests(unittest.TestCase):
    def test_owner_artwork_and_geometry_copies_are_exact(self):
        self.assertEqual(
            hashlib.sha256(IMAGE.read_bytes()).hexdigest(),
            "c0c3c68b72654b2b7dc6daa89e7b7fec4d27cc4946ea699e2258c1b546177f0c",
        )
        self.assertEqual(
            hashlib.sha256(OWNER_GEOMETRY.read_bytes()).hexdigest(),
            "fd9d1f470dfb4dd5ebf5383fdcc67fbcf103b6aa85cdab2fda12afc997ca52d9",
        )
        self.assertEqual(png_dimensions(IMAGE), (2680, 356))
        self.assertEqual(png_dimensions(ORIGINAL), (2048, 329))
        self.assertEqual(
            hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
            "99378eefb832de346ef9a777071de837af08a03af30541764f50889a22fa6101",
        )

    def test_default_only_for_exact_cisco_and_original_remains_selectable(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        matches = [x for x in registry["devices"] if x.get("model") == MODEL]
        self.assertEqual(len(matches), 1)
        row = matches[0]
        self.assertEqual(row["status"], "experimental")
        self.assertEqual(row["ports"]["rj45"], 8)
        self.assertEqual(row["ports"]["uplinks"], 2)
        self.assertIn("dual-purpose", row["ports"]["uplink_type"])
        self.assertEqual(row["mapping_profile"], "cisco-3560cg-8pc-8p-2dual")
        self.assertEqual(row["calibration_profile"], "cisco_3560cg_8pc_compact")
        self.assertEqual(row["default_faceplate"], "faceplates/c3560cg-8pc-s-compact.png")
        self.assertEqual(
            row["optional_faceplates"],
            ["faceplates/c3560cg-8pc-s.png", "faceplates/24rj45-2sfp.png"],
        )
        self.assertEqual(row["visuals"]["recommended_faceplate"], row["default_faceplate"])
        self.assertEqual(row["visuals"]["optional_faceplates"], row["optional_faceplates"])
        self.assertEqual(row["visuals"]["canvas"], {"width": 2680, "height": 356})
        others = [x for x in registry["devices"] if x.get("model") != MODEL]
        self.assertTrue(any(x.get("default_faceplate") == "faceplates/c3560cg-8pc-s.png" for x in others))
        self.assertFalse(any(x.get("default_faceplate") == row["default_faceplate"] for x in others))

    def test_catalog_label_old_and_compact(self):
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
        labels = {x["filename"]: x["display_name"] for x in data["faceplates"]}
        self.assertEqual(labels["c3560cg-8pc-s.png"], OLD_LABEL)
        self.assertEqual(labels["c3560cg-8pc-s-compact.png"], OLD_LABEL + " Compact")

    def test_native_round_trip_preserves_geometry_and_not_source_device(self):
        export = json.loads(OWNER_GEOMETRY.read_text(encoding="utf-8"))
        source = export["geometry"]
        factory = json.loads(FACTORY.read_text(encoding="utf-8"))
        self.assertEqual(export["transfer_type"], "switch-vision-geometry-profile-v1")
        # Exported source_scope/model/SW1 are capture context, NEVER model identity.
        self.assertEqual(factory["model"], "cisco-3560cg-8pc-8p-2dual")
        self.assertEqual(factory["profile"], "cisco_3560cg_8pc_compact")
        self.assertNotEqual(export["model"], factory["model"])
        self.assertNotEqual(export["source_profile"], factory["profile"])
        self.assertEqual(factory["image"]["file"], "faceplates/c3560cg-8pc-s-compact.png")
        self.assertEqual(factory["image"]["coordinate_space"], "image-native-v1")
        self.assertEqual((factory["image"]["width"], factory["image"]["height"]), (2680, 356))
        self.assertEqual(factory["ui"]["faceplate"]["file"], "c3560cg-8pc-s-compact.png")
        self.assertEqual(set(factory["ports"]), {str(i) for i in range(1, 11)})
        self.assertEqual(set(factory["sfp"]), {"SFP1", "SFP2"})
        render = render_space_calibration(factory)
        self.assertEqual((render["image"]["width"], render["image"]["height"]), (2048, 448))
        # Owner export's row 6 extends below its 121px status panel. Only the
        # Preserve even the owner's out-of-panel sixth status-row position.
        # The existing factory opt-in uses the runtime's normal clipping
        # behavior; it does not change any submitted geometry coordinate.
        self.assertAlmostEqual(render["ui"]["status_panel"]["height"], 121.070933333, delta=2e-7)
        self.assertTrue(factory["ui"]["status_panel"]["allow_out_of_bounds_rows"])
        self.assertEqual(source["ui"]["status_panel"]["height"], 121.070933333)

        def compare(left, right, path="geometry"):
            if isinstance(left, dict):
                for k, value in left.items():
                    if path == "geometry.ui.faceplate" and k == "file":
                        continue
                    self.assertIn(k, right, path)
                    compare(value, right[k], path + "." + k)
            elif isinstance(left, list):
                self.assertEqual(len(left), len(right), path)
                for index, (a, b) in enumerate(zip(left, right)):
                    compare(a, b, path + "." + str(index))
            elif isinstance(left, (int, float)) and not isinstance(left, bool):
                self.assertAlmostEqual(left, right, delta=2e-7, msg=path)
            else:
                self.assertEqual(left, right, path)

        for section in ("ports", "sfp", "status_leds", "ui"):
            compare(source[section], render[section], "geometry." + section)

    def test_stock_factory_card_remains_old_and_new_is_embedded(self):
        old = json.loads((ROOT / "src/calibration/faceplate-c3560cg-8pc-s.json").read_text())
        new = json.loads(FACTORY.read_text())
        self.assertEqual(set(old["ports"]), {str(i) for i in range(1, 9)})
        self.assertEqual(set(old["sfp"]), {"G1", "G2"})
        self.assertEqual(new["model"], old["model"])
        for rel in ("src/js/switch-vision.js", "src/custom_components/switch_vision/switch-vision-card.js"):
            content = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn('"c3560cg-8pc-s-compact.png": {"schema_version":2', content)
            self.assertIn('cisco_3560cg_8pc_compact: "c3560cg-8pc-s-compact.png"', content)
            self.assertIn('cisco_3560cg_8pc: "c3560cg-8pc-s.png"', content)
            self.assertIn(OLD_LABEL + " Compact", content)


if __name__ == "__main__":
    unittest.main()
