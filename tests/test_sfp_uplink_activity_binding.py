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


class SfpUplinkActivityBindingTests(unittest.TestCase):
    def test_generic_uplink_byte_counters_cover_first_four_uplinks(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        helper = extract_js_function(
            source, "function sfpByteEntities(config, port, direction)"
        )
        harness = f"""
function normalizeMember() {{ return "hp1"; }}
{helper}

for (const port of [1, 2, 3, 4]) {{
  for (const direction of ["rx", "tx"]) {{
    const actual = sfpByteEntities({{}}, port, direction);
    const expectedPreferred = [
      `sensor.hp1_sfp_10g_${{port}}_${{direction}}_bytes`,
      `sensor.hp1_sfp_1g_${{port}}_${{direction}}_bytes`,
      `sensor.hp1_uplink_${{port}}_${{direction}}_bytes`,
    ];
    for (let index = 0; index < expectedPreferred.length; index += 1) {{
      if (actual[index] !== expectedPreferred[index]) {{
        throw new Error(
          `uplink ${{port}} ${{direction}} candidate ${{index}} was ${{actual[index]}}, expected ${{expectedPreferred[index]}}`
        );
      }}
    }}
  }}
}}

const unifiDisabled = sfpByteEntities(
  {{ data_source: "unifi_api", unifi_per_port_traffic: false }},
  4,
  "rx"
);
if (unifiDisabled.length !== 0) {{
  throw new Error("UniFi no-per-port-traffic guard changed unexpectedly");
}}
"""
        result = subprocess.run(
            ["node", "-e", harness],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_activity_and_rate_paths_share_the_same_uplink_counter_resolver(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        rates = extract_js_function(
            source, "function sfpTrafficRates(hass, config, port)"
        )
        activity = extract_js_function(
            source, "function testSfpActivity(hass, config, port)"
        )
        for function in (rates, activity):
            self.assertIn(
                'sfpByteEntities(config, port, "rx")',
                function,
            )
            self.assertIn(
                'sfpByteEntities(config, port, "tx")',
                function,
            )
            self.assertIn("sfpSpeedMbps(hass, config, port)", function)

    def test_speed_resolver_already_supports_generic_uplink_numbers(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        speed = extract_js_function(
            source, "function sfpSpeedMbps(hass, config, port)"
        )
        self.assertIn(
            "`sensor.${member}_uplink_${n}_speed_mbps`",
            speed,
        )
        self.assertIn(
            "`sensor.${member}_uplink_${n}_speed_bps`",
            speed,
        )


if __name__ == "__main__":
    unittest.main()
