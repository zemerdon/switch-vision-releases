from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "src" / "calibration" / "faceplate-c3560cg-8pc-s.json"


class C3560CGFactoryGeometryTests(unittest.TestCase):
    def test_port_3_factory_position_and_hitbox(self) -> None:
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        port = profile["ports"]["3"]
        self.assertEqual(port["center"], [786, 329])
        self.assertEqual(port["hitbox"], [84, 76])


if __name__ == "__main__":
    unittest.main()
