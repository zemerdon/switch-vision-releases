from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "devices" / "supported_devices.json"


class DeviceRegistryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.models = {
            str(item.get("model")): item
            for item in payload.get("devices", [])
            if isinstance(item, dict)
        }

    def test_real_hardware_promotions_remain_community_validated(self) -> None:
        for model in {
            "WS-C2960X-24TS-L",
            "WS-C3560CG-8PC-S",
            "SG500X-24",
            "S5735-L8P4X-A1",
            "S5720-12TP-LI-AC",
        }:
            self.assertEqual(
                self.models[model].get("status"),
                "community_validated",
                model,
            )

    def test_3560cg_combo_port_semantics_are_documented(self) -> None:
        device = self.models["WS-C3560CG-8PC-S"]
        ports = device.get("ports") or {}
        self.assertEqual(ports.get("rj45"), 8)
        self.assertEqual(ports.get("uplinks"), 2)
        notes = "\n".join(str(note) for note in device.get("notes") or [])
        self.assertIn("Gi0/9", notes)
        self.assertIn("Gi0/10", notes)
        self.assertIn("dual-purpose", notes.lower())

    def test_s5720_physical_layout_is_8_plus_4_one_gig_sfp(self) -> None:
        device = self.models["S5720-12TP-LI-AC"]
        ports = device.get("ports") or {}
        self.assertEqual(ports.get("rj45"), 8)
        self.assertEqual(ports.get("uplinks"), 4)
        self.assertEqual(ports.get("gigabit_sfp"), 4)
        self.assertEqual(ports.get("ten_gigabit_sfp_plus"), 0)

    def test_unifi_models_have_explicit_non_cisco_visual_profiles(self) -> None:
        for model, device in self.models.items():
            if device.get("vendor") != "Ubiquiti":
                continue
            profile = str(device.get("calibration_profile") or "")
            faceplate = str(device.get("default_faceplate") or "")
            visuals = device.get("visuals") or {}
            self.assertTrue(profile, model)
            self.assertTrue(faceplate, model)
            self.assertFalse(profile.lower().startswith("cisco_"), (model, profile))
            self.assertNotIn("cisco", faceplate.lower(), (model, faceplate))
            self.assertEqual(visuals.get("calibration_profile"), profile, model)
            self.assertEqual(visuals.get("recommended_faceplate"), faceplate, model)


if __name__ == "__main__":
    unittest.main()
