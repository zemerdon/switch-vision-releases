from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "js" / "switch-vision.js"
REGISTRY = ROOT / "src" / "devices" / "supported_devices.yaml"


def extract_js_function(source: str, signature: str) -> str:
    start = source.find(signature)
    if start < 0:
        raise AssertionError(f"JavaScript function not found: {signature}")
    brace = source.find("{", start)
    depth = 0
    quote = None
    escape = False
    for pos in range(brace, len(source)):
        char = source[pos]
        if quote is not None:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"', chr(96)}:
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : pos + 1]
    raise AssertionError(f"Closing brace not found for {signature}")


class DellN4032FFaceplateBindingTests(unittest.TestCase):
    def test_registry_binds_exact_model_to_reviewed_optical_faceplate(self) -> None:
        data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
        row = next(item for item in data["devices"] if item["model"] == "N4032F")
        self.assertEqual(row["status"], "experimental")
        self.assertTrue(row["dashboard_support"])
        self.assertEqual(row["ports"]["uplinks"], 24)
        self.assertEqual(row["default_faceplate"], "faceplates/unifi-32sfp.png")
        self.assertEqual(row["calibration_profile"], "unifi_32sfp")
        rear = row["discovery_optional_interfaces"][0]
        self.assertEqual(rear["interface_names"], ["Fo1/1/1", "Fo1/1/2"])
        self.assertEqual(rear["faceplate_positions"], [25, 26])
        self.assertFalse(rear["telemetry_only"])

    def test_rear_qsfp_slots_resolve_to_real_40g_entities(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        helper = extract_js_function(
            source, "function n4032RearQsfpEntity(config, port, suffix)"
        )
        status = extract_js_function(
            source, "function sfpStatusEntities(config, member, port)"
        )
        harness = f"""
function normalizeEntityPrefix(config) {{ return 'n4032'; }}
{helper}
{status}
const config = {{switch_model:'N4032F'}};
const p25 = sfpStatusEntities(config, 'N4032', 25);
const p26 = sfpStatusEntities(config, 'N4032', 26);
if (p25[0] !== 'sensor.n4032_rear_qsfp_40g_1_status') throw new Error(p25[0]);
if (p26[0] !== 'sensor.n4032_rear_qsfp_40g_2_status') throw new Error(p26[0]);
if (n4032RearQsfpEntity(config, 24, 'status') !== null) throw new Error('front port remapped');
"""
        result = subprocess.run(
            ["node", "-e", harness],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        byte_fn = extract_js_function(source, "function sfpByteEntities(config, port, direction)")
        speed_fn = extract_js_function(source, "function sfpSpeedMbps(hass, config, port)")
        self.assertIn("n4032RearQsfpEntity", byte_fn)
        self.assertIn('"speed_mbps"', speed_fn)
        self.assertIn('"speed_bps"', speed_fn)


if __name__ == "__main__":
    unittest.main()
