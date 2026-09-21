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
    if brace < 0:
        raise AssertionError(f"Opening brace not found: {signature}")
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


class SharedSfpLogicalPortMappingTests(unittest.TestCase):
    def test_mapping_parser_and_visible_label(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        mapping = extract_js_function(source, "function sfpLogicalPort(config, sfpPort)")
        label = extract_js_function(source, "function sfpVisibleLabel(config, sfpPort, fallback, calibration = null)")
        harness = f'''
{mapping}
{label}

const arrayConfig = {{sfp_logical_port_map:[23,24]}};
if (sfpLogicalPort(arrayConfig, 1) !== 23) throw new Error('array G1 mapping failed');
if (sfpLogicalPort(arrayConfig, 2) !== 24) throw new Error('array G2 mapping failed');
if (sfpLogicalPort(arrayConfig, 3) !== null) throw new Error('array out-of-range should be null');
if (sfpVisibleLabel(arrayConfig, 1, 'G1') !== '23') throw new Error('shared label should show logical port 23');

const objectConfig = {{sfp_logical_port_map:{{'1':17,'2':18}}}};
if (sfpLogicalPort(objectConfig, 1) !== 17) throw new Error('object G1 mapping failed');
if (sfpLogicalPort(objectConfig, 2) !== 18) throw new Error('object G2 mapping failed');
if (sfpLogicalPort({{}}, 1) !== null) throw new Error('ordinary SFP must stay independent');
if (sfpVisibleLabel({{}}, 1, 'G1') !== 'G1') throw new Error('ordinary SFP label changed');
'''
        result = subprocess.run(["node", "-e", harness], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_shared_cage_uses_access_port_telemetry(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        expectations = {
            "function sfpIsUp(hass, config, port)": "return portIsUp(hass, config, logicalPort);",
            "function sfpSpeedMbps(hass, config, port)": "portSpeed(hass, config, logicalPort)",
            "function sfpTrafficCounterSample(hass, config, port, direction)": "return portTrafficCounterSample(hass, config, logicalPort, direction);",
            "function sfpTrafficRates(hass, config, port)": "return portTrafficRates(hass, config, logicalPort);",
            "function testSfpActivity(hass, config, port)": "return testPortActivity(hass, config, logicalPort);",
            "function selectedSfpDetails(hass, config, port)": "return selectedPortDetails(hass, config, logicalPort);",
        }
        for signature, expected in expectations.items():
            with self.subTest(signature=signature):
                body = extract_js_function(source, signature)
                self.assertIn("sfpLogicalPort(config", body)
                self.assertIn(expected, body)

    def test_shared_cage_click_selects_logical_access_port_outside_calibration(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        method_start = source.find("  attachSelectionHandlers(svg, activeCalibration = calibration) {")
        self.assertGreaterEqual(method_start, 0)
        fragment = source[method_start : method_start + 4200]
        self.assertIn('type === "sfp"', fragment)
        self.assertIn("sfpLogicalPort(this.config, id)", fragment)
        self.assertIn('const selectedType = sharedLogicalPort ? "port" : type;', fragment)
        self.assertIn('selected_port: selectedType === "port" ? selectedId : null', fragment)
        self.assertIn('nextConfig.calibration_target = `${type}:${id}`;', fragment)


if __name__ == "__main__":
    unittest.main()
