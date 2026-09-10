#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
YAML_REGISTRY = ROOT / "src/devices/supported_devices.yaml"
JSON_REGISTRY = ROOT / "src/devices/supported_devices.json"

WALK_BACKED_MODELS = {
    "HP 1810-24G",
    "GS1900-8",
    "SR-S25G3420F",
    "US-8-150W",
    "US-24-250W",
    "PowerConnect 5548P",
    "GS1900-24E",
    "WS-C3750X-48P",
    "SG350-20",
    "HP J8693A Switch 3500yl-48G",
    "USW Pro HD 24 PoE",
    "USW Aggregation",
    "USW Enterprise 24 PoE",
    "USW Flex 2.5G 5",
    "USW WAN",
    "GS1915-24EP",
}


class WalkBackedRegistrySyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.yaml_doc = yaml.safe_load(YAML_REGISTRY.read_text(encoding="utf-8"))
        cls.json_doc = json.loads(JSON_REGISTRY.read_text(encoding="utf-8"))
        cls.yaml_rows = {row["model"]: row for row in cls.yaml_doc["devices"]}
        cls.json_rows = {row["model"]: row for row in cls.json_doc["devices"]}

    def test_walk_backed_models_are_in_stable_core_registry(self):
        missing = sorted(WALK_BACKED_MODELS - set(self.yaml_rows))
        self.assertEqual(missing, [])
        for model in WALK_BACKED_MODELS:
            row = self.yaml_rows[model]
            self.assertEqual(row["status"], "experimental", model)
            self.assertTrue(row.get("evidence"), model)
            self.assertTrue(row.get("discovery_support"), model)
            self.assertEqual(
                (row.get("contributor") or {}).get("public_credit"),
                False,
                model,
            )

    def test_generated_json_matches_authoritative_yaml_for_walk_backed_models(self):
        for model in WALK_BACKED_MODELS:
            self.assertEqual(self.json_rows.get(model), self.yaml_rows[model], model)

    def test_gs1915_exact_walk_contract_is_registered_without_phantom_uplinks(self):
        row = self.yaml_rows["GS1915-24EP"]
        self.assertEqual(row["family"], "GS1915")
        self.assertEqual(row["mapping_profile"], "zyxel-gs1915-24ep")
        self.assertEqual(row["ports"]["rj45"], 24)
        self.assertEqual(row["ports"]["uplinks"], 0)
        self.assertEqual(row["ports"]["gigabit_sfp"], 0)
        self.assertEqual(row["ports"]["ten_gigabit_sfp_plus"], 0)
        self.assertTrue(row["ports"]["poe"])
        self.assertEqual(row["default_faceplate"], "faceplates/24rj45-2sfp.png")
        self.assertEqual(row["calibration_profile"], "stock_24rj45_2sfp")
        self.assertIn("zero-uplink", " ".join(row.get("notes") or []).lower())


if __name__ == "__main__":
    unittest.main()
