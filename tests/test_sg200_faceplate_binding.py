#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "devices" / "supported_devices.json"
PROFILE = ROOT / "src" / "calibration" / "faceplate-stock-24rj45-2sfp.json"


class SG200FaceplateBindingTests(unittest.TestCase):
    def test_sg200_uses_stock_24_plus_2_visual(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        row = next(item for item in registry["devices"] if item.get("model") == "SG200-26")
        self.assertEqual(row["ports"]["rj45"], 24)
        self.assertEqual(row["ports"]["uplinks"], 2)
        self.assertEqual(row["ports"]["combo_ports"], 2)
        self.assertEqual(row["ports"]["combo_logical_ports"], [25, 26])
        self.assertEqual(row["default_faceplate"], "faceplates/24rj45-2sfp.png")
        self.assertEqual(row["calibration_profile"], "stock_24rj45_2sfp")
        self.assertEqual(row["visuals"]["recommended_faceplate"], "faceplates/24rj45-2sfp.png")
        self.assertEqual(row["visuals"]["calibration_profile"], "stock_24rj45_2sfp")

    def test_stock_24_plus_2_geometry_matches_visual_contract(self) -> None:
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        self.assertEqual(profile["profile"], "stock_24rj45_2sfp")
        self.assertEqual(profile["image"]["file"], "faceplates/24rj45-2sfp.png")
        self.assertEqual(len(profile.get("ports") or {}), 24)
        self.assertEqual(len(profile.get("sfp") or {}), 2)


if __name__ == "__main__":
    unittest.main()
