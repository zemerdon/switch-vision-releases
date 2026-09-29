#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
JSON_REGISTRY = ROOT / "src/devices/supported_devices.json"
YAML_REGISTRY = ROOT / "src/devices/supported_devices.yaml"
GENERATOR = ROOT / "src/devices/generate_supported_devices.py"
BUILD = ROOT / "build.py"


class DiscoveryRegistryProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.json_doc = json.loads(JSON_REGISTRY.read_text(encoding="utf-8"))
        cls.yaml_doc = yaml.safe_load(YAML_REGISTRY.read_text(encoding="utf-8"))

    def test_core_registry_is_marked_as_discovery_projection(self) -> None:
        projection = self.json_doc.get("projection") or {}
        self.assertEqual(projection.get("schema"), 1)
        self.assertEqual(projection.get("source_component"), "discovery")
        self.assertRegex(
            str(projection.get("source_registry_sha256") or ""),
            r"^[0-9a-f]{64}$",
        )
        allowlist = projection.get("device_field_allowlist")
        self.assertIsInstance(allowlist, list)
        self.assertIn("model", allowlist)
        self.assertIn("ports", allowlist)
        self.assertIn("visuals", allowlist)
        excluded_fields = (
            "evidence",
            "tested_firmware",
            "contributor",
            "contributions",
            "notes",
            "discovery_optional_interfaces",
            "last_validated_component",
        )
        for field in excluded_fields:
            self.assertNotIn(field, allowlist)
            for device in self.json_doc["devices"]:
                self.assertNotIn(field, device, f"{device.get('model')}: {field}")

    def test_yaml_is_generated_compatibility_output_of_json_projection(self) -> None:
        self.assertEqual(self.yaml_doc, self.json_doc)

    def test_generator_reads_json_and_writes_yaml(self) -> None:
        source = GENERATOR.read_text(encoding="utf-8")
        self.assertIn('json.loads(path.read_text(encoding="utf-8"))', source)
        self.assertIn('args.registry.parent / "supported_devices.yaml"', source)
        self.assertNotIn(
            'args.registry.parent / "supported_devices.json").write_text',
            source,
        )

    def test_build_consumes_json_projection_for_registry_generation(self) -> None:
        source = BUILD.read_text(encoding="utf-8")
        self.assertGreaterEqual(
            source.count('SRC / "devices" / "supported_devices.json"'),
            2,
        )
        self.assertIn(
            'registry = SRC / "devices" / "supported_devices.json"',
            source,
        )
        self.assertIn(
            'registry_path = SRC / "devices" / "supported_devices.json"',
            source,
        )


if __name__ == "__main__":
    unittest.main()
