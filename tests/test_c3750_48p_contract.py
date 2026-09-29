from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "devices" / "supported_devices.json"


class Catalyst3750ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.device = next(
            d for d in payload["devices"]
            if isinstance(d, dict) and d.get("model") == "WS-C3750-48P"
        )

    def test_exact_model_and_physical_contract(self) -> None:
        device = self.device
        ports = device["ports"]
        self.assertEqual(device["status"], "experimental")
        self.assertEqual(device["mapping_profile"], "cisco-3750-48p-48fe-4sfp")
        self.assertEqual(ports["rj45"], 48)
        self.assertIs(ports["poe"], True)
        self.assertEqual(ports["uplinks"], 4)
        self.assertEqual(ports["gigabit_sfp"], 4)
        self.assertEqual(ports["ten_gigabit_sfp_plus"], 0)
        self.assertIs(device["stack_support"], True)

    def test_visual_contract(self) -> None:
        self.assertEqual(self.device["default_faceplate"], "faceplates/48rj45-4sfp.png")
        self.assertEqual(self.device["calibration_profile"], "default_cisco_48_port")



if __name__ == "__main__":
    unittest.main()
