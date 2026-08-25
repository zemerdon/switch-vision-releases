from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "src" / "calibration" / "faceplate-c3560cg-8pc-s.json"


class C3560CGFactoryGeometryTests(unittest.TestCase):
    def test_port_3_factory_position_and_hitbox_preserve_owner_default(self) -> None:
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        self.assertEqual((profile.get("image") or {}).get("coordinate_space"), "image-native-v1")
        self.assertEqual((profile.get("image") or {}).get("width"), 2048)
        self.assertEqual((profile.get("image") or {}).get("height"), 329)

        # Native stored coordinates are the no-letterbox form of the owner
        # default. Inverting the exact 329/448 migration returns the calibrated
        # legacy-render values [786, 329] and [84, 76].
        port = profile["ports"]["3"]
        self.assertEqual(port["center"], [849.21875, 241.609375])
        self.assertEqual(port["hitbox"], [61.6875, 55.8125])

        scale = 329 / 448
        offset_x = 272
        legacy_center = [
            (float(port["center"][0]) - offset_x) / scale,
            float(port["center"][1]) / scale,
        ]
        legacy_hitbox = [
            float(port["hitbox"][0]) / scale,
            float(port["hitbox"][1]) / scale,
        ]
        self.assertAlmostEqual(legacy_center[0], 786.0, places=7)
        self.assertAlmostEqual(legacy_center[1], 329.0, places=7)
        self.assertAlmostEqual(legacy_hitbox[0], 84.0, places=7)
        self.assertAlmostEqual(legacy_hitbox[1], 76.0, places=7)


if __name__ == "__main__":
    unittest.main()
