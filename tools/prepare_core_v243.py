#!/usr/bin/env python3
from pathlib import Path
import textwrap
import yaml

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {"S5720-12TP-LI-AC", "S5735-L8P4X-A1"}
PROFILE = "stock_24rj45_4sfp"
FACEPLATE = "faceplates/24rj45-4sfp.png"

registry_path = ROOT / "src/devices/supported_devices.yaml"
doc = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
found = set()
for device in doc.get("devices", []):
    if not isinstance(device, dict) or device.get("model") not in TARGETS:
        continue
    found.add(device["model"])
    device["calibration_profile"] = PROFILE
    device["default_faceplate"] = FACEPLATE
    visuals = device.setdefault("visuals", {})
    visuals["recommended_faceplate"] = FACEPLATE
    visuals["calibration_profile"] = PROFILE
if found != TARGETS:
    raise SystemExit(f"ERROR: Huawei models missing from Core registry: {sorted(TARGETS-found)}")
registry_path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8", newline="\n")

release_notes = """# Switch Vision Core v2.4.3 — Huawei faceplate reset hotfix

- Restores `S5720-12TP-LI-AC` and `S5735-L8P4X-A1` to the neutral `stock_24rj45_4sfp` factory calibration profile.
- Restores `faceplates/24rj45-4sfp.png` as the matching default/recommended faceplate for both Huawei 8 RJ45 + 4 SFP models.
- Fixes Reset Current Faceplate/model-aware reset falling back to Cisco 48-port factory geometry and moving LEDs away from shipped card defaults.
- Adds a permanent regression so these exact Huawei models cannot silently return to `default_cisco_48_port`.
- Preserves physical mappings, S5720 1G SFP speed safeguards, telemetry, Activity LEDs and TEST MODE behavior.

After updating Core through Switch Vision Installer, restart Home Assistant Core when requested and hard-refresh the browser. Existing saved custom calibrations remain preserved until the user chooses a reset.
"""
(ROOT / "RELEASE_NOTES.md").write_text(release_notes, encoding="utf-8", newline="\n")

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = textwrap.dedent("""\
## v2.4.3 — Huawei faceplate reset hotfix

- Restore Huawei S5720/S5735 neutral 24 RJ45 / 4 SFP factory visual assignments that regressed during the v2.4.2 registry synchronization.
- Ensure Reset Current Faceplate and model-aware resets return those switches to `stock_24rj45_4sfp` with `faceplates/24rj45-4sfp.png`, not Cisco 48-port geometry.
- Add permanent regression coverage for both exact Huawei models.

""")
if changelog.startswith("# Changelog\n\n"):
    changelog = "# Changelog\n\n" + entry + changelog[len("# Changelog\n\n"):]
elif changelog.startswith("## v"):
    changelog = entry + changelog
else:
    raise SystemExit("ERROR: unexpected Core CHANGELOG header")
changelog_path.write_text(changelog, encoding="utf-8", newline="\n")

test_path = ROOT / "tests/test_huawei_visual_defaults.py"
test_path.write_text(textwrap.dedent(f"""\
import json
import unittest
from pathlib import Path


class HuaweiVisualDefaultsRegression(unittest.TestCase):
    def test_huawei_8_plus_4_models_use_neutral_factory_visual(self):
        root = Path(__file__).resolve().parents[1]
        payload = json.loads((root / 'src/devices/supported_devices.json').read_text(encoding='utf-8'))
        models = {{str(item.get('model')): item for item in payload.get('devices', []) if isinstance(item, dict)}}
        for model in ('S5720-12TP-LI-AC', 'S5735-L8P4X-A1'):
            device = models[model]
            self.assertEqual(device.get('calibration_profile'), '{PROFILE}')
            self.assertEqual(device.get('default_faceplate'), '{FACEPLATE}')
            visuals = device.get('visuals') or {{}}
            self.assertEqual(visuals.get('calibration_profile'), '{PROFILE}')
            self.assertEqual(visuals.get('recommended_faceplate'), '{FACEPLATE}')


if __name__ == '__main__':
    unittest.main()
"""), encoding="utf-8", newline="\n")

print("Prepared Core v2.4.3 Huawei reset/default hotfix")
