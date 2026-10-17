"""Privacy-history scan must read every archived registry but parse identical bytes once."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests" / "test_public_attribution_privacy.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("core_public_attribution_privacy_dedup", SOURCE)
    checker = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(checker)
    return checker


class PrivacyRegistryContentIdentityTests(unittest.TestCase):
    def test_every_archive_read_with_single_parsing_of_identical_bytes(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            locations = (
                "src/devices/supported_devices.json",
                "Releases/switch-vision-8.0.1/devices/supported_devices.json",
                "Releases/switch-vision-8.0.2/devices/supported_devices.json",
            )
            raw = json.dumps({"devices": [{"display_name": "anonymous",
                                           "public_credit": False}]}).encode()
            for relative in locations:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)

            actual_read = Path.read_bytes
            reads: list[str] = []
            def tracked_read(path):
                reads.append(path.relative_to(root).as_posix())
                return actual_read(path)

            validations: list[str] = []
            actual_validation = checker._assert_structured_private_refs_removed
            def tracked_validation(data, path):
                validations.append(path.relative_to(root).as_posix())
                return actual_validation(data, path)

            with (mock.patch.object(checker, "ROOT", root),
                  mock.patch.object(Path, "read_bytes", tracked_read),
                  mock.patch.object(checker.json, "loads", wraps=checker.json.loads) as parser,
                  mock.patch.object(checker, "_assert_structured_private_refs_removed", tracked_validation)):
                checker.test_all_public_device_registries_are_neutral()

            self.assertEqual(set(reads), set(locations))
            self.assertEqual(len(reads), 3)
            self.assertEqual(parser.call_count, 1)
            self.assertEqual(len(set(validations)), 1)

    def test_changed_archived_registry_is_not_hidden_by_clean_duplicate(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            earlier = root / "src/devices/supported_devices.json"
            changed = root / "Releases/switch-vision-8.0.2/devices/supported_devices.json"
            earlier.parent.mkdir(parents=True)
            changed.parent.mkdir(parents=True)
            earlier.write_text(json.dumps({"display_name": "anonymous",
                                           "public_credit": False}))
            changed.write_text(json.dumps({"display_name": "private contributor",
                                           "public_credit": True}))
            with mock.patch.object(checker, "ROOT", root):
                with self.assertRaises(AssertionError):
                    checker.test_all_public_device_registries_are_neutral()

    def test_identical_json_and_yaml_content_keep_separate_parser_contracts(self):
        checker = load_checker()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in ("supported_devices.json", "supported_devices.yaml"):
                path = root / "src/devices" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"devices":[]}')
            seen: list[str] = []
            original = checker._assert_structured_private_refs_removed
            def check(data, path):
                seen.append(path.suffix)
                return original(data, path)
            with (mock.patch.object(checker, "ROOT", root),
                  mock.patch.object(checker, "_assert_structured_private_refs_removed", check)):
                checker.test_all_public_device_registries_are_neutral()
            self.assertEqual(set(seen), {".json", ".yaml"})


if __name__ == "__main__":
    unittest.main()
