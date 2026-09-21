from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "devices" / "supported_devices.json"


class Catalyst3750x48pSContractTests(unittest.TestCase):
    def test_exact_sku_uses_reviewed_c3kx_contract(self) -> None:
        devices = json.loads(REGISTRY.read_text(encoding="utf-8"))["devices"]
        row = next(device for device in devices if device.get("model") == "WS-C3750X-48P-S")
        self.assertEqual(row["status"], "experimental")
        self.assertEqual(row["ports"]["rj45"], 48)
        self.assertEqual(row["ports"]["gigabit_sfp"], 2)
        self.assertEqual(row["ports"]["ten_gigabit_sfp_plus"], 2)
        self.assertEqual(row["mapping_profile"], "cisco-3750x-48p-c3kx")
        self.assertEqual(row["default_faceplate"], "faceplates/48rj45-4sfp.png")
        self.assertIn("15.2(4)E10", row["tested_firmware"])


if __name__ == "__main__":
    unittest.main()
