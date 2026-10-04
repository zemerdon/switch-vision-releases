from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
MIRROR = ROOT / "src" / "js" / "switch-vision.js"


class CalibrationMultiPortMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = CARD.read_text(encoding="utf-8")

    def test_card_sources_remain_exact_mirrors(self) -> None:
        self.assertEqual(CARD.read_bytes(), MIRROR.read_bytes())

    def test_multi_selection_controls_are_enabled_and_report_mixed_values(self) -> None:
        required = (
            "function calibrationPortMetadataTargets(cal, editable)",
            "function commonCalibrationMetadataValue(items, field, normalise)",
            'const metadataEditable = metadataTargets.items.length > 0;',
            'portSupportedSpeedOptionsHtml(supportedSpeedState.value, { mixed: supportedSpeedState.mixed })',
            'portRoleOptionsHtml(portRoleState.value, inheritedPortRole, { mixed: portRoleState.mixed })',
            '<option value="" selected disabled>Mixed</option>',
        )
        for marker in required:
            self.assertIn(marker, self.source)

    def test_supported_speed_and_role_apply_to_every_selected_item(self) -> None:
        required = (
            "const targets = calibrationPortMetadataTargets(cal, editable);",
            "for (const item of targets.items) item.supported_speed = value;",
            "for (const item of targets.items) item.port_role = value;",
        )
        for marker in required:
            self.assertIn(marker, self.source)

    def test_metadata_target_helper_resolves_custom_rj45_and_sfp_sets(self) -> None:
        start = self.source.index("function calibrationPortMetadataTargets(cal, editable)")
        end = self.source.index("\n}\n\nfunction commonCalibrationMetadataValue", start) + 2
        helper = self.source[start:end]
        harness = f"""
function calibrationPortKeysForEditable(cal, editable) {{ return editable.keys || Object.keys(cal.ports || {{}}); }}
function calibrationSfpKeysForEditable(cal, editable) {{ return editable.keys || Object.keys(cal.sfp || {{}}); }}
{helper}
const cal = {{
  ports: {{"1": {{supported_speed:"1G", port_role:"lan"}}, "3": {{supported_speed:"10G", port_role:"uplink"}}}},
  sfp: {{"SFP1": {{supported_speed:"10G", port_role:"uplink"}}, "SFP2": {{supported_speed:"25G", port_role:"wan"}}}},
}};
let result = calibrationPortMetadataTargets(cal, {{type:"ports", keys:["1","3"]}});
if (result.items.length !== 2 || result.portKeys.join(",") !== "1,3" || result.sfpKeys.length !== 0) throw new Error("RJ45 multi-selection mismatch");
result = calibrationPortMetadataTargets(cal, {{type:"sfps", keys:["SFP1","SFP2"]}});
if (result.items.length !== 2 || result.sfpKeys.join(",") !== "SFP1,SFP2" || result.portKeys.length !== 0) throw new Error("SFP multi-selection mismatch");
"""
        result = subprocess.run(["node", "-e", harness], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
