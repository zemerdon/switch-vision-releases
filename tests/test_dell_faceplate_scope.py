from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "devices" / "supported_devices.json"
PROFILE = ROOT / "src" / "calibration" / "faceplate-dell-28-rj45-2sfp.json"
DELL_FACEPLATE = "faceplates/dell-28-rj45-2sfp.png"


class DellFaceplateScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.devices = [item for item in payload.get("devices", []) if isinstance(item, dict)]

    def dell_device(self) -> dict:
        return next(item for item in self.devices if item.get("model") == "N2128PX-ON")

    def test_n2128px_on_uses_exact_dell_visual(self) -> None:
        device = self.dell_device()
        self.assertEqual(device.get("vendor"), "Dell")
        self.assertEqual(device.get("default_faceplate"), DELL_FACEPLATE)
        self.assertEqual(device.get("calibration_profile"), "dell_28rj45_2sfp")
        self.assertEqual((device.get("visuals") or {}).get("recommended_faceplate"), DELL_FACEPLATE)
        self.assertEqual((device.get("visuals") or {}).get("calibration_profile"), "dell_28rj45_2sfp")
        self.assertEqual(device.get("status"), "experimental")

    def test_dell_faceplate_never_escapes_vendor_or_topology_boundary(self) -> None:
        users = [item for item in self.devices if item.get("default_faceplate") == DELL_FACEPLATE]
        self.assertTrue(users)
        for device in users:
            ports = device.get("ports") or {}
            self.assertEqual(device.get("vendor"), "Dell", device.get("model"))
            self.assertLessEqual(int(ports.get("rj45") or 0), 28, device.get("model"))
            self.assertLessEqual(int(ports.get("uplinks") or 0), 2, device.get("model"))

    def test_n2128px_on_public_evidence_is_neutral(self) -> None:
        device = self.dell_device()
        self.assertEqual(device.get("evidence"), "community_hardware_validation")
        notes = "\n".join(str(note) for note in device.get("notes") or []).casefold()
        self.assertNotIn("contribution id", notes)
        self.assertNotIn("bundle received", notes)

    def test_factory_profile_is_dell_only_28_plus_2_and_contains_no_instance_state(self) -> None:
        profile = json.loads(PROFILE.read_text(encoding="utf-8"))
        self.assertEqual(profile.get("model"), "dell-n2128px-on")
        self.assertEqual(profile.get("profile"), "dell_28rj45_2sfp")
        self.assertEqual((profile.get("image") or {}).get("file"), DELL_FACEPLATE)
        self.assertEqual(len(profile.get("ports") or {}), 28)
        self.assertEqual(set((profile.get("sfp") or {}).keys()), {"G1", "G2"})
        self.assertEqual(profile.get("stack"), {"enabled": False, "stack_id": "", "uptime_source": "", "members": {}})
        self.assertEqual(profile.get("management"), {"switch_ip": ""})
        for key in {"transfer_type", "source_scope", "source_profile", "source_base_profile", "required_faceplate", "faceplate_included"}:
            self.assertNotIn(key, profile)


if __name__ == "__main__":
    unittest.main()
