from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "src" / "calibration"
FACEPLATES = ROOT / "src" / "faceplates"


class UniFiNewFaceplateFactoryDefaultsTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((CAL / name).read_text(encoding="utf-8"))

    def assert_clean_factory(self, profile: dict, filename: str) -> None:
        self.assertEqual((profile.get("image") or {}).get("file"), f"faceplates/{filename}")
        self.assertEqual(((profile.get("ui") or {}).get("faceplate") or {}).get("file"), filename)
        self.assertEqual(((profile.get("ui") or {}).get("faceplate") or {}).get("source"), "custom")
        self.assertEqual(profile.get("stack"), {"enabled": False, "stack_id": "", "uptime_source": "", "members": {}})
        self.assertEqual(profile.get("management"), {"switch_ip": ""})
        for key in {"transfer_type", "source_scope", "source_profile", "source_base_profile", "required_faceplate", "faceplate_included"}:
            self.assertNotIn(key, profile)

    def test_unifi_8_rj45_2sfp_defaults_are_faceplate_specific(self) -> None:
        filename = "unifi-8-rj45-2sfp.png"
        profile = self.load("faceplate-unifi-8-rj45-2sfp.json")
        self.assertEqual(profile.get("model"), "unifi-8-rj45-2sfp")
        self.assertEqual(profile.get("profile"), "unifi_8_rj45_2sfp")
        self.assertEqual(set((profile.get("ports") or {}).keys()), {str(i) for i in range(1, 9)})
        self.assertEqual(set((profile.get("sfp") or {}).keys()), {"SFP1", "SFP2"})
        self.assertTrue((FACEPLATES / filename).is_file())
        self.assert_clean_factory(profile, filename)

    def test_unifi_28sfp_defaults_preserve_28_plus_4_optical_layout(self) -> None:
        filename = "unifi-28sfp.png"
        profile = self.load("faceplate-unifi-28sfp.json")
        self.assertEqual(profile.get("model"), "unifi-28sfp")
        self.assertEqual(profile.get("profile"), "unifi_28sfp")
        self.assertEqual(profile.get("ports"), {})
        sfp = profile.get("sfp") or {}
        self.assertEqual(set(sfp.keys()), {f"SFP{i}" for i in range(1, 33)})
        self.assertEqual({sfp[f"SFP{i}"].get("display_name") for i in range(29, 33)}, {"TWE1", "TWE2", "TWE3", "TWE4"})
        self.assertEqual(sfp["SFP29"].get("display_name"), "TWE1")
        self.assertEqual(sfp["SFP30"].get("display_name"), "TWE2")
        self.assertEqual(sfp["SFP31"].get("display_name"), "TWE3")
        self.assertEqual(sfp["SFP32"].get("display_name"), "TWE4")
        self.assertTrue((FACEPLATES / filename).is_file())
        self.assert_clean_factory(profile, filename)


if __name__ == "__main__":
    unittest.main()
