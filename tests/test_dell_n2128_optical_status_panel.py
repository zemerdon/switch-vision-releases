from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "js" / "switch-vision.js"


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


class DellN2128OpticalStatusPanelTests(unittest.TestCase):
    def test_optical_entity_contract_and_n2128_panel_fields(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        optics = extract_js_function(
            source, "function selectedSfpOpticalDetails(hass, config, port)"
        )
        self.assertIn("_sfp_10g_$" + "{n}_$" + "{suffix}", optics)
        for suffix in (
            "temperature",
            "voltage",
            "current",
            "tx_optical_power",
            "rx_optical_power",
            "optical_status",
            "transceiver_vendor",
            "transceiver_part",
            "media_type",
        ):
            self.assertIn(f'"{suffix}"', optics)

        self.assertIn("function isDellOpticalModel(config)", source)
        for field in (
            '"optic_status"',
            '"temperature"',
            '"voltage"',
            '"current"',
            '"tx_power"',
            '"rx_power"',
            '"media_type"',
            '"transceiver_vendor"',
            '"transceiver_part"',
        ):
            self.assertIn(field, source)

    def test_only_dell_models_auto_offer_observed_optical_rows(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        classifier = extract_js_function(source, "function isDellOpticalModel(config)")
        harness = f"""
const assert = require("node:assert/strict");
{classifier}
assert.equal(isDellOpticalModel({{switch_model: "N2128PX-ON"}}), true);
assert.equal(isDellOpticalModel({{switch_model: "N4032F"}}), true);
assert.equal(isDellOpticalModel({{switch_model: "PowerConnect 5548P", manufacturer: "Dell"}}), true);
assert.equal(isDellOpticalModel({{switch_model: "Unknown", switch_vendor: "Dell EMC"}}), true);
assert.equal(isDellOpticalModel({{switch_model: "EX3300-48P", manufacturer: "Juniper"}}), false);
assert.equal(isDellOpticalModel({{switch_model: "WS-C3650-48PD-E"}}), false);
assert.equal(isDellOpticalModel({{}}), false);
"""
        result = subprocess.run(["node", "-e", harness], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_metric_display_preserves_home_assistant_units(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        usable = extract_js_function(source, "function usableValue(value)")
        display = extract_js_function(
            source, "function firstEntityDisplayValue(hass, entityIds)"
        )
        harness = f"""
{usable}
{display}
const hass = {{
  states: {{
    'sensor.test': {{state:'33.7', attributes:{{unit_of_measurement:'°C'}}}},
    'sensor.text': {{state:'No Fault', attributes:{{}}}}
  }}
}};
if (firstEntityDisplayValue(hass, ['sensor.test']) !== '33.7 °C') throw new Error('unit lost');
if (firstEntityDisplayValue(hass, ['sensor.text']) !== 'No Fault') throw new Error('text changed');
"""
        result = subprocess.run(
            ["node", "-e", harness],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
