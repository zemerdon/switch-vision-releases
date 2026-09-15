from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.7.9"

CHANGELOG_SECTION = """## v2.7.9 — Exact-model faceplate mapping integrity

- Replace stale oversized visual fallbacks with already-shipped exact UniFi faceplates for `USW Flex`, `USW Flex Mini`, `USW-Lite-8-PoE`, `USW-Enterprise-8-PoE`, `USW Pro XG 8 PoE`, and `USW Pro HD 24 PoE`.
- Enable the existing owner-calibrated 32-position optical faceplate/profile for `USW Pro Aggregation`, preserving its authoritative 28 × SFP+ + 4 × SFP28 topology and API-port map.
- Enable the approved stock 24+2 canvas for `US 16 PoE 150W` while preserving its authoritative 16 RJ45 + 2 SFP physical counts; no nonexistent 16-port artwork is invented.
- Add permanent exact-model regressions that lock faceplate/profile pairs, preserve known-good compact UniFi mappings, and keep non-exact fallback models' physical counts authoritative.
- Keep support-confidence states unchanged; this release corrects presentation assignments only and does not promote hardware validation status.

"""

RELEASE_NOTES_SECTION = """# Switch Vision Core v2.7.9

Core 2.7.9 corrects exact-model faceplate assignments after field testing exposed the USW Flex Mini using an obsolete oversized 24-port fallback. The audit was expanded across the supported-model registry instead of treating the Mini as a one-off fix.

Existing bundled exact assets are now used for the USW Flex and Flex Mini (5 RJ45), USW-Lite-8-PoE (8 RJ45), USW-Enterprise-8-PoE and USW Pro XG 8 PoE (8 RJ45 + 2 optical), USW Pro HD 24 PoE (24 RJ45 + 4 optical), and USW Pro Aggregation (32 optical positions). US 16 PoE 150W is enabled with the approved oversized 24+2 stock canvas because no exact 16+2 artwork is bundled; its physical 16+2 count remains authoritative.

The release does not infer faceplates from vendor name alone and does not force a visually similar asset onto hardware whose physical topology has no exact bundled match. Permanent regressions now protect the corrected exact-model matrix and the true physical counts of intentional fallback models.

Manual installs must replace `/config/custom_components/switch_vision/` and restart Home Assistant Core because the packaged registry and frontend visual recommendation metadata change in this release.

"""

OLD_PRO_AGG_TEST = '''    def test_pro_aggregation_preserves_25g_capability_contract_without_fake_visual(self) -> None:\n        device = self.models["USW Pro Aggregation"]\n        ports = device.get("ports") or {}\n        self.assertEqual(device.get("status"), "detected")\n        self.assertIs(device.get("dashboard_support"), False)\n        self.assertEqual(ports.get("rj45"), 0)\n        self.assertEqual(ports.get("uplinks"), 32)\n        self.assertEqual(ports.get("ten_gigabit_sfp_plus"), 28)\n        self.assertEqual(ports.get("twenty_five_gigabit_sfp28"), 4)\n        self.assertEqual(device.get("calibration_profile"), "")\n        self.assertEqual(device.get("default_faceplate"), "")\n        self.assertEqual(device.get("unifi_api_port_map"), {"rj45": [], "sfp": list(range(1, 33))})\n        notes = "\\n".join(str(note) for note in device.get("notes") or [])\n        self.assertIn("Ports 29 and 30", notes)\n        self.assertIn("negotiating at 10G", notes)\n        self.assertIn("25G", notes)\n'''

NEW_PRO_AGG_TEST = '''    def test_pro_aggregation_preserves_25g_capability_contract_with_exact_optical_visual(self) -> None:\n        device = self.models["USW Pro Aggregation"]\n        ports = device.get("ports") or {}\n        self.assertEqual(device.get("status"), "detected")\n        self.assertIs(device.get("dashboard_support"), True)\n        self.assertEqual(ports.get("rj45"), 0)\n        self.assertEqual(ports.get("uplinks"), 32)\n        self.assertEqual(ports.get("ten_gigabit_sfp_plus"), 28)\n        self.assertEqual(ports.get("twenty_five_gigabit_sfp28"), 4)\n        self.assertEqual(device.get("calibration_profile"), "unifi_32sfp")\n        self.assertEqual(device.get("default_faceplate"), "faceplates/unifi-32sfp.png")\n        self.assertEqual(device.get("unifi_api_port_map"), {"rj45": [], "sfp": list(range(1, 33))})\n        visuals = device.get("visuals") or {}\n        self.assertEqual(visuals.get("recommended_faceplate"), "faceplates/unifi-32sfp.png")\n        self.assertEqual(visuals.get("calibration_profile"), "unifi_32sfp")\n        notes = "\\n".join(str(note) for note in device.get("notes") or [])\n        self.assertIn("Ports 29 and 30", notes)\n        self.assertIn("negotiating at 10G", notes)\n        self.assertIn("25G", notes)\n'''


def write_lf(path: Path, text: str) -> None:
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


def prepend_once(path: Path, heading: str, section: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.startswith(heading):
        return
    write_lf(path, section + text)


def patch_readme(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace("### Switch Vision v2.7.8", "### Switch Vision v2.7.9", 1)
    text = text.replace(
        "**v2.7.8** is the current tested Switch Vision Core/dashboard source version.",
        "**v2.7.9** is the current tested Switch Vision Core/dashboard source version.",
        1,
    )
    if "### Switch Vision v2.7.9" not in text:
        raise RuntimeError(f"could not update current Core heading in {path}")
    write_lf(path, text)


def patch_stale_regressions() -> None:
    path = ROOT / "tests" / "test_device_registry_contracts.py"
    text = path.read_text(encoding="utf-8")
    if NEW_PRO_AGG_TEST in text:
        return
    if OLD_PRO_AGG_TEST not in text:
        raise RuntimeError("could not locate stale USW Pro Aggregation regression")
    write_lf(path, text.replace(OLD_PRO_AGG_TEST, NEW_PRO_AGG_TEST, 1))


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    run(sys.executable, "tools/apply_faceplate_matrix.py")
    patch_stale_regressions()
    prepend_once(ROOT / "CHANGELOG.md", "## v2.7.9 —", CHANGELOG_SECTION)
    prepend_once(ROOT / "RELEASE_NOTES.md", "# Switch Vision Core v2.7.9", RELEASE_NOTES_SECTION)
    patch_readme(ROOT / "README.md")
    patch_readme(ROOT / "src" / "README.md")
    run(sys.executable, "build.py", "-v", VERSION)
    run(sys.executable, "tests/test_exact_model_faceplate_matrix.py")
    run(sys.executable, "tools/check_core_release_parity.py")
    print("Core 2.7.9 faceplate repair release preparation: PASS")


if __name__ == "__main__":
    main()
