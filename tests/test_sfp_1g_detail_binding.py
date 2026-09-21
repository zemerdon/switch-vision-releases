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
        raise AssertionError(f"Opening brace not found for: {signature}")
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


class Sfp1gDetailBindingTests(unittest.TestCase):
    def test_selected_sfp_details_include_1g_namespace_for_rich_fields(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        selected = extract_js_function(
            source, "function selectedSfpDetails(hass, config, port)"
        )
        for suffix in (
            "vlan_mode",
            "mode",
            "native_vlan",
            "vlan_id",
            "vlan",
            "trunk_status",
            "alias",
            "description",
            "name",
        ):
            self.assertIn(f"_sfp_1g_${{n}}_{suffix}", selected)
        self.assertIn("const member = normalizeEntityPrefix(config);", selected)

        access = extract_js_function(
            source, "function selectedPortDetails(hass, config, port)"
        )
        self.assertIn("const member = normalizeEntityPrefix(config);", access)

        status = extract_js_function(
            source, "function switchStatusValues(hass, config, cal = calibration)"
        )
        self.assertIn("const member = normalizePanelMember(config).toUpperCase();", status)
        self.assertIn("const m = normalizeEntityPrefix(config).toLowerCase();", status)

    def test_entity_prefix_decouples_display_member_from_telemetry_namespace(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        explicit = extract_js_function(source, "function explicitEntityPrefix(config)")
        panel = extract_js_function(source, "function normalizePanelMember(config)")
        telemetry = extract_js_function(source, "function normalizeEntityPrefix(config)")
        member = extract_js_function(source, "function normalizeMember(config)")
        harness = f'''
{explicit}
{panel}
{telemetry}
{member}

const cases = [
  [{{member:'Switch_master', entity_prefix:'master'}}, 'switch_master', 'master'],
  [{{member:'Switch_master', status_entity_prefix:'sensor.master_port_'}}, 'switch_master', 'master'],
  [{{member:'Switch_master'}}, 'switch_master', 'switch_master'],
];
for (const [config, expectedPanel, expectedTelemetry] of cases) {{
  const panelValue = normalizePanelMember(config);
  const telemetryValue = normalizeEntityPrefix(config);
  const memberValue = normalizeMember(config);
  if (panelValue !== expectedPanel || telemetryValue !== expectedTelemetry || memberValue !== expectedTelemetry) {{
    throw new Error(
      JSON.stringify(config) + ' => panel=' + panelValue + ', telemetry=' + telemetryValue + ', member=' + memberValue
      + ', expected panel=' + expectedPanel + ', telemetry=' + expectedTelemetry
    );
  }}
}}
'''
        result = subprocess.run(
            ["node", "-e", harness],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
