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

    def test_shared_cage_prefers_sfp_telemetry_then_logical_fallback(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        entity_state = extract_js_function(source, "function entityState(hass, entityId)")
        port_range = extract_js_function(source, "function portRange(port)")
        template_entity = extract_js_function(source, "function templateEntity(template, port)")
        mapping = extract_js_function(source, "function sfpLogicalPort(config, sfpPort)")
        status_entities = extract_js_function(source, "function sfpStatusEntities(config, member, port)")
        sfp_is_up = extract_js_function(source, "function sfpIsUp(hass, config, port)")

        harness = f"""
{entity_state}
{port_range}
{template_entity}
{mapping}
function n4032RearQsfpEntity() {{ return null; }}
function unifiSfpPort() {{ return null; }}
function linkStateIsUp(value) {{ return String(value || '').toLowerCase() === 'up'; }}
function portEntity(config, port, type) {{
  return 'sensor.' + config.entity_prefix + '_port_' + port + '_' + type;
}}
function portIsUp(hass, config, port) {{
  const state = entityState(hass, portEntity(config, port, 'status'));
  return state === 'up' || state === '1';
}}
{status_entities}
{sfp_is_up}

const config = {{
  entity_prefix: 'sgcava53',
  member: 'sgcava53',
  sfp_logical_port_map: [21, 22, 23, 24],
  sfp_status_entity_template: 'sensor.sgcava53_sfp_1g_{{port}}_status'
}};

let hass = {{states: {{
  'sensor.sgcava53_sfp_1g_1_status': {{state: 'up'}},
  'sensor.sgcava53_port_21_status': {{state: 'down'}}
}}}};
if (!sfpIsUp(hass, config, 1)) throw new Error('explicit SFP status must win over shared logical-port status');

hass = {{states: {{
  'sensor.sgcava53_sfp_1g_1_status': {{state: 'down'}},
  'sensor.sgcava53_port_21_status': {{state: 'up'}}
}}}};
if (sfpIsUp(hass, config, 1)) throw new Error('explicit SFP down state must remain authoritative');

hass = {{states: {{
  'sensor.sgcava53_port_21_status': {{state: 'up'}}
}}}};
if (!sfpIsUp(hass, config, 1)) throw new Error('shared logical-port status must remain a fallback');
"""
        result = subprocess.run(["node", "-e", harness], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        counter = extract_js_function(source, "function sfpTrafficCounterSample(hass, config, port, direction)")
        self.assertLess(
            counter.index("readFirstCounterSample(hass, sfpByteEntities"),
            counter.index("const logicalPort = sfpLogicalPort(config, port)"),
        )

        speed = extract_js_function(source, "function sfpSpeedMbps(hass, config, port)")
        self.assertLess(
            speed.index("const mbpsCandidates"),
            speed.index("const logicalPort = sfpLogicalPort(config, port)"),
        )

        rates = extract_js_function(source, "function sfpTrafficRates(hass, config, port)")
        activity = extract_js_function(source, "function testSfpActivity(hass, config, port)")
        self.assertIn("!sfpHasDedicatedTelemetry(hass, config, port)", rates)
        self.assertIn("return portTrafficRates(hass, config, logicalPort);", rates)
        self.assertIn("!sfpHasDedicatedTelemetry(hass, config, port)", activity)
        self.assertIn("return testPortActivity(hass, config, logicalPort);", activity)

        details = extract_js_function(source, "function selectedSfpDetails(hass, config, port)")
        self.assertIn("!sfpHasDedicatedTelemetry(hass, config, n)", details)
        self.assertIn("return selectedPortDetails(hass, config, logicalPort);", details)

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
