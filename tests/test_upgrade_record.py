"""Ensure first direct upgrade keeps verified art and never invents choices."""
import hashlib
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/custom_components/switch_vision/faceplate_artwork_history.py"
spec = importlib.util.spec_from_file_location("faceplate_artwork_history", MODULE)
assert spec and spec.loader
history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)


class PreupgradeRecordTests(TestCase):
    def test_verified_before_sha_for_exact_existing_profile_only(self) -> None:
        with TemporaryDirectory() as tmp:
            config = Path(tmp)
            frontend = config / "www/switch-vision"
            name = "cisco-3850-12xs.png"
            old, new = b"installed-before", b"installed-after"
            old_sha, new_sha = (hashlib.sha256(b).hexdigest() for b in (old, new))
            archive = frontend / "faceplate-history" / old_sha / name
            archive.parent.mkdir(parents=True)
            archive.write_bytes(old)
            (config / "switch-vision-faceplate-upgrades.json").write_text(json.dumps({
                "schema": "switch-vision-faceplate-upgrade-record-v1",
                "choices": {"native_SW3": {name: {"before": old_sha, "after": new_sha}}}
            }))
            self.assertEqual(history.recorded_preupgrade_choice(
                frontend, "native_SW3", name, new_sha), old_sha)
            self.assertEqual(history.verified_choice(
                frontend, name, old_sha, new_sha)["path"],
                f"faceplate-history/{old_sha}/{name}")
            self.assertEqual(history.recorded_preupgrade_choice(
                frontend, "native_SW4", name, new_sha), "")
            self.assertEqual(history.recorded_preupgrade_choice(
                frontend, "native_SW3", name, old_sha), "")
            archive.write_bytes(b"damaged")
            self.assertEqual(history.recorded_preupgrade_choice(
                frontend, "native_SW3", name, new_sha), "")
            (config / "switch-vision-faceplate-upgrades.json").unlink()
            self.assertEqual(history.recorded_preupgrade_choice(
                frontend, "native_SW3", name, new_sha), "")

    def test_core_pinned_choice_not_replaced_by_upgrade_record(self) -> None:
        source = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text()
        self.assertIn("recorded_preupgrade_choice", source)
        self.assertLess(source.index("previous = pins.get(base_profile)"),
                        source.index("elif len(pins) < 256 and initial_pin is not None:"))
        self.assertIn("if initial_sha == current_sha and recorded_sha:", source)
