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

    def test_completed_real_hardware_checklist_promotes_exact_models(self) -> None:
        expected = {
            "SG500X-24": {
                "mapping_profile": "cisco-sg500x-24-24p-4x10g",
                "rj45": 24,
                "uplinks": 4,
                "gigabit_sfp": 0,
                "ten_gigabit_sfp_plus": 4,
                "rj45_validation": "community_confirmed_ports_1_24",
                "poe_validation": "not_applicable",
                "uplink_validation": "community_confirmed_four_uplink_positions",
                "stack_validation": "pending",
            },
            "S5720-12TP-LI-AC": {
                "mapping_profile": "huawei-s5720-12tp-li-ac",
                "rj45": 8,
                "uplinks": 4,
                "gigabit_sfp": 4,
                "ten_gigabit_sfp_plus": 0,
                "rj45_validation": "community_confirmed_ports_1_8",
                "poe_validation": "not_applicable_not_exposed",
                "uplink_validation": "community_confirmed_ports_9_12_1g_sfp_link_and_speed",
                "stack_validation": "not_applicable",
            },
            "S5735-L8P4X-A1": {
                "mapping_profile": "huawei-s5735-l8p4x-a1",
                "rj45": 8,
                "uplinks": 4,
                "gigabit_sfp": 0,
                "ten_gigabit_sfp_plus": 4,
                "rj45_validation": "community_confirmed_two_devices_ports_1_8",
                "poe_validation": "community_confirmed",
                "uplink_validation": "community_confirmed_two_devices_four_10g_sfp_plus_positions_and_link_speed",
                "stack_validation": "not_applicable",
            },
        }
        for model, contract in expected.items():
            device = self.models[model]
            self.assertEqual(device.get("status"), "community_validated", model)
            self.assertEqual(device.get("last_validated_version"), "2.6.7", model)
            self.assertEqual(device.get("mapping_profile"), contract["mapping_profile"], model)
            ports = device.get("ports") or {}
            for field in ("rj45", "uplinks", "gigabit_sfp", "ten_gigabit_sfp_plus"):
                self.assertEqual(ports.get(field), contract[field], (model, field))
            validation = device.get("validation") or {}
            self.assertEqual(validation.get("rj45_mapping"), contract["rj45_validation"], model)
            self.assertEqual(validation.get("poe"), contract["poe_validation"], model)
            self.assertEqual(validation.get("system_sensors"), "community_confirmed", model)
            self.assertEqual(validation.get("uplinks"), contract["uplink_validation"], model)
            self.assertEqual(validation.get("stack"), contract["stack_validation"], model)
            self.assertEqual((device.get("visuals") or {}).get("status"), "community_validated", model)
            notes = "\n".join(str(note) for note in device.get("notes") or [])
            self.assertIn("link/activity", notes, model)
            self.assertIn("rendered alignment", notes, model)

        payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
        community_definition = str((payload.get("support_statuses") or {}).get("community_validated") or "")
        self.assertIn("rendered alignment", community_definition)

    def test_mikrotik_crs328_experimental_registry_contract(self) -> None:
        device = self.models["CRS328-24P-4S+RM"]
        self.assertEqual(device.get("vendor"), "MikroTik")
        self.assertEqual(device.get("family"), "CRS328")
        self.assertEqual(device.get("status"), "experimental")
        self.assertEqual(device.get("confirmed_since"), "2.6.11")
        self.assertEqual(device.get("last_validated_version"), "2.3.21")
        self.assertEqual(device.get("last_validated_component"), "Discovery")
        self.assertEqual(device.get("mapping_profile"), "mikrotik-crs328-24p-4splus")
        self.assertEqual(device.get("calibration_profile"), "stock_24rj45_4sfp")
        self.assertEqual(device.get("default_faceplate"), "faceplates/24rj45-4sfp.png")

        ports = device.get("ports") or {}
        self.assertEqual(ports.get("rj45"), 24)
        self.assertIs(ports.get("poe"), True)
        self.assertEqual(ports.get("uplinks"), 4)
        self.assertEqual(ports.get("gigabit_sfp"), 0)
        self.assertEqual(ports.get("ten_gigabit_sfp_plus"), 4)

        contributor = device.get("contributor") or {}
        self.assertEqual(contributor.get("display_name"), "Patrik Kästel")
        self.assertIs(contributor.get("public_credit"), True)

        validation = device.get("validation") or {}
        self.assertEqual(
            validation.get("exact_model_detection"),
            "contribution_confirmed_local_routeros_identity",
        )
        self.assertEqual(
            validation.get("rj45_mapping"),
            "contribution_confirmed_ether1_through_ether24_pending_rendered_validation",
        )
        self.assertEqual(
            validation.get("uplinks"),
            "contribution_confirmed_four_sfp_plus_positions_live_link_pending",
        )
        self.assertEqual(validation.get("stack"), "not_applicable")

        visuals = device.get("visuals") or {}
        self.assertEqual(visuals.get("status"), "experimental")
        self.assertEqual(visuals.get("recommended_faceplate"), "faceplates/24rj45-4sfp.png")
        self.assertEqual(visuals.get("calibration_profile"), "stock_24rj45_4sfp")

        notes = "\n".join(str(note) for note in device.get("notes") or [])
        self.assertIn("Discovery 2.3.21", notes)
        self.assertIn("Core 2.6.11", notes)
        self.assertIn("four SFP+ cages were empty", notes)
        self.assertIn("rendered", notes.lower())

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
