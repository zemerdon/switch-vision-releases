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
        if char in {"'", '"', "`"}:
            quote = char
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : pos + 1]
    raise AssertionError(f"Closing brace not found for: {signature}")


class StockFaceplatePresentationInvariantTests(unittest.TestCase):
    def test_runtime_mapping_does_not_rewrite_stock_labels(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        self.assertNotIn("function displayedPortNumber", source)
        self.assertNotIn("function portLabelIsRemapped", source)
        self.assertIn("const visibleLabel = String(port.display_name || n);", source)
        self.assertNotIn("port_label_offset", source)

        sfp_fn = extract_js_function(
            source,
            "function sfpVisibleLabel(config, sfpPort, fallback, calibration = null)",
        )
        harness = f"""
{sfp_fn}
function expect(actual, expected, label) {{
  if (actual !== expected) throw new Error(`${{label}}: got ${{actual}}, expected ${{expected}}`);
}}
const mapped = {{
  data_source: 'unifi_api',
  unifi_device_id: 'device-a',
  unifi_rj45_ports: 8,
  unifi_sfp_port_offset: 8,
  port_entity_offset: -1,
  switch_model: 'Juniper EX3300-48P'
}};
expect(sfpVisibleLabel(mapped, 1, 'SFP1', null), 'SFP1', 'stock SFP label');
expect(sfpVisibleLabel(mapped, 2, 'G2', null), 'G2', 'stock G label');
expect(
  sfpVisibleLabel(mapped, 1, 'SFP1', {{ ui: {{ sfp_label_suffix: 'Uplink' }} }}),
  '1 Uplink',
  'calibration override'
);
"""
        result = subprocess.run(
            ["node", "-e", harness], cwd=ROOT, text=True, capture_output=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_entity_mapping_remains_independent(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        mapped_fn = extract_js_function(source, "function mappedPortNumber(config, port)")
        harness = f"""
{mapped_fn}
if (mappedPortNumber({{ port_entity_offset: -1 }}, 1) !== 0) throw new Error('entity offset lost');
if (mappedPortNumber({{ port_entity_offset: 24 }}, 1) !== 25) throw new Error('entity offset 24 lost');
"""
        result = subprocess.run(
            ["node", "-e", harness], cwd=ROOT, text=True, capture_output=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
