from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "devices" / "supported_devices.json"
CATALOG = ROOT / "src" / "faceplates" / "catalog.json"
CARD = ROOT / "src" / "js" / "switch-vision.js"


def extract_js_function(source: str, signature: str) -> str:
    start = source.find(signature)
    if start < 0:
        raise AssertionError(f"JavaScript function not found: {signature}")
    brace = source.find("{", start)
    depth = 0
    quote: str | None = None
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
    raise AssertionError(f"Closing brace not found for: {signature}")


class HpJ9774aFaceplateBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.models = {row["model"]: row for row in data["devices"]}

    def test_registry_uses_stock_24_plus_2_with_shared_ports(self) -> None:
        device = self.models["HP J9774A 2530-8G-PoEP"]
        ports = device["ports"]
        self.assertEqual(device["status"], "experimental")
        self.assertTrue(device["dashboard_support"])
        self.assertEqual(device["mapping_profile"], "hp-2530-8g-poep-8p-2dual")
        self.assertEqual(device["default_faceplate"], "faceplates/24rj45-2sfp.png")
        self.assertEqual(device["calibration_profile"], "stock_24rj45_2sfp")
        self.assertEqual(ports["rj45"], 8)
        self.assertEqual(ports["combo_ports"], 2)
        self.assertEqual(ports["combo_logical_ports"], [9, 10])
        self.assertEqual(ports["uplinks"], 2)
        self.assertEqual(ports["gigabit_sfp"], 2)
        self.assertEqual(ports["rj45"] + ports["combo_ports"], 10)

        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        serialized = json.dumps(catalog)
        self.assertIn("24rj45-2sfp.png", serialized)

    def test_shared_sfp_cages_resolve_to_logical_ports_9_and_10(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        mapping = extract_js_function(source, "function sfpLogicalPort(config, sfpPort)")
        visible = extract_js_function(source, "function sfpVisibleLabel(config, sfpPort, fallback, calibration = null)")
        harness = f"""
{mapping}
{visible}
const config = {{sfp_logical_port_map:[9,10], port_count:10, sfp_port_count:2}};
if (sfpLogicalPort(config, 1) !== 9) throw new Error('SFP 1 must map to logical port 9');
if (sfpLogicalPort(config, 2) !== 10) throw new Error('SFP 2 must map to logical port 10');
if (sfpVisibleLabel(config, 1, 'G1') !== '9') throw new Error('SFP 1 label must be logical port 9');
if (sfpVisibleLabel(config, 2, 'G2') !== '10') throw new Error('SFP 2 label must be logical port 10');
"""
        result = subprocess.run(["node", "-e", harness], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_shared_cages_use_access_port_telemetry(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        for signature in (
            "function sfpIsUp(hass, config, port)",
            "function sfpSpeedMbps(hass, config, port)",
            "function sfpTrafficCounterSample(hass, config, port, direction)",
            "function sfpTrafficRates(hass, config, port)",
            "function testSfpActivity(hass, config, port)",
            "function selectedSfpDetails(hass, config, port)",
        ):
            with self.subTest(signature=signature):
                self.assertIn("sfpLogicalPort(config", extract_js_function(source, signature))


if __name__ == "__main__":
    unittest.main()
