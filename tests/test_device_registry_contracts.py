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

    def test_evidence_backed_real_hardware_promotions_remain_community_validated(self) -> None:
        for model in {
            "SG500X-24",
            "S5735-L8P4X-A1",
            "S5720-12TP-LI-AC",
        }:
            self.assertEqual(self.models[model].get("status"), "community_validated", model)

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

    def test_unifi_dashboard_visual_contracts_are_explicit(self) -> None:
        for model, device in self.models.items():
            if device.get("vendor") != "Ubiquiti":
                continue
            profile = str(device.get("calibration_profile") or "")
            faceplate = str(device.get("default_faceplate") or "")
            visuals = device.get("visuals") or {}
            dashboard_support = device.get("dashboard_support") is True
            if dashboard_support:
                self.assertTrue(profile, model)
                self.assertTrue(faceplate, model)
                self.assertFalse(profile.lower().startswith("cisco_"), (model, profile))
                self.assertNotIn("cisco", faceplate.lower(), (model, faceplate))
            else:
                self.assertEqual(bool(profile), bool(faceplate), model)
                if not profile:
                    self.assertIn(device.get("status"), {"detected", "experimental"}, model)
            self.assertEqual(visuals.get("calibration_profile"), profile, model)
            self.assertEqual(visuals.get("recommended_faceplate"), faceplate, model)

    def test_existing_models_gain_community_evidence_without_promotion(self) -> None:
        expected_units = {
            "US 8 60W": 1,
            "USW Flex Mini": 2,
            "US 48 PoE 500W": 2,
        }
        for model, units in expected_units.items():
            device = self.models[model]
            self.assertEqual(device.get("status"), "experimental", model)
            rows = [
                row
                for row in device.get("contributions") or []
                if isinstance(row, dict)
                and row.get("source_component") == "UniFi2MQTT 2.0.47"
                and row.get("devices_observed") == units
            ]
            self.assertEqual(len(rows), 1, model)
            row = rows[0]
            self.assertEqual(row.get("dashboard_validation"), "pending", model)
            self.assertEqual(
                row.get("api_capabilities"),
                {"port_detail": True, "per_port_traffic": False},
                model,
            )
            contributor = row.get("contributor") or {}
            self.assertEqual(str(contributor.get("display_name") or "").casefold(), "community contributor", model)
            self.assertIs(contributor.get("public_credit"), False, model)

    def test_us_48_reuses_verified_geometry_and_legacy_sequential_mapping(self) -> None:
        device = self.models["US 48"]
        ports = device.get("ports") or {}
        self.assertEqual(device.get("status"), "experimental")
        self.assertIs(device.get("dashboard_support"), True)
        self.assertEqual(ports.get("rj45"), 48)
        self.assertIs(ports.get("poe"), False)
        self.assertEqual(ports.get("uplinks"), 4)
        self.assertEqual(ports.get("gigabit_sfp"), 2)
        self.assertEqual(ports.get("ten_gigabit_sfp_plus"), 2)
        self.assertEqual(device.get("calibration_profile"), "stock_48rj45_4sfp")
        self.assertEqual(device.get("default_faceplate"), "faceplates/48rj45-4sfp.png")
        self.assertNotIn("unifi_api_port_map", device)

    def test_us_xg_16_uses_authoritative_optical_first_api_map(self) -> None:
        device = self.models["US XG 16"]
        ports = device.get("ports") or {}
        self.assertEqual(device.get("status"), "detected")
        self.assertIs(device.get("dashboard_support"), False)
        self.assertEqual(ports.get("rj45"), 4)
        self.assertEqual(ports.get("uplinks"), 12)
        self.assertEqual(ports.get("ten_gigabit_sfp_plus"), 12)
        self.assertEqual(device.get("calibration_profile"), "")
        self.assertEqual(device.get("default_faceplate"), "")
        self.assertEqual(
            device.get("unifi_api_port_map"),
            {"rj45": [13, 14, 15, 16], "sfp": list(range(1, 13))},
        )

    def test_pro_aggregation_preserves_25g_capability_contract_without_fake_visual(self) -> None:
        device = self.models["USW Pro Aggregation"]
        ports = device.get("ports") or {}
        self.assertEqual(device.get("status"), "detected")
        self.assertIs(device.get("dashboard_support"), False)
        self.assertEqual(ports.get("rj45"), 0)
        self.assertEqual(ports.get("uplinks"), 32)
        self.assertEqual(ports.get("ten_gigabit_sfp_plus"), 28)
        self.assertEqual(ports.get("twenty_five_gigabit_sfp28"), 4)
        self.assertEqual(device.get("calibration_profile"), "")
        self.assertEqual(device.get("default_faceplate"), "")
        self.assertEqual(device.get("unifi_api_port_map"), {"rj45": [], "sfp": list(range(1, 33))})
        notes = "\n".join(str(note) for note in device.get("notes") or [])
        self.assertIn("Ports 29 and 30", notes)
        self.assertIn("negotiating at 10G", notes)
        self.assertIn("25G", notes)


if __name__ == "__main__":
    unittest.main()
