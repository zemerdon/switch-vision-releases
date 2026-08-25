import json
import unittest
from pathlib import Path

import yaml


class SupportStatusIntegrityRegression(unittest.TestCase):
    MODELS = ("WS-C2960X-24TS-L", "WS-C3560CG-8PC-S")

    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        yaml_data = yaml.safe_load((root / "src/devices/supported_devices.yaml").read_text(encoding="utf-8"))
        json_data = json.loads((root / "src/devices/supported_devices.json").read_text(encoding="utf-8"))
        self.yaml_devices = {item["model"]: item for item in yaml_data["devices"]}
        self.json_devices = {item["model"]: item for item in json_data["devices"]}

    def test_pending_models_are_not_overstated_as_community_validated(self):
        for model in self.MODELS:
            with self.subTest(model=model):
                self.assertEqual(self.yaml_devices[model]["status"], "experimental")
                self.assertEqual(self.json_devices[model]["status"], "experimental")
                notes = " ".join(self.yaml_devices[model].get("notes", []))
                self.assertIn("Remains Experimental", notes)

    def test_pending_validation_evidence_is_preserved_not_faked_green(self):
        d2960 = self.yaml_devices["WS-C2960X-24TS-L"]["validation"]
        self.assertIn("pending", d2960["rj45_mapping"])
        self.assertEqual(d2960["system_sensors"], "pending")
        self.assertEqual(d2960["uplinks"], "pending")
        self.assertIn("pending", d2960["stack"])

        d3560 = self.yaml_devices["WS-C3560CG-8PC-S"]["validation"]
        self.assertEqual(d3560["rj45_mapping"], "candidate")
        self.assertEqual(d3560["poe"], "candidate")
        self.assertEqual(d3560["system_sensors"], "pending")
        self.assertEqual(d3560["uplinks"], "pending")


if __name__ == "__main__":
    unittest.main()
