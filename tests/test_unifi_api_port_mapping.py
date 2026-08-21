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


class UniFiApiPortMappingTests(unittest.TestCase):
    def test_legacy_and_explicit_mapping_contracts(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        signatures = (
            "function mappedPortNumber(config, port)",
            "function unifiApiPortMapForGroup(config, group)",
            "function unifiApiPortIndex(config, group, port)",
            "function unifiPortByIndex(config, index)",
            "function unifiAccessPort(config, port)",
            "function unifiSfpPort(config, port)",
        )
        functions = "\n\n".join(extract_js_function(source, sig) for sig in signatures)

        harness = f"""
const MODEL_MAPS = {{
  'US XG 16': {{
    rj45: [13, 14, 15, 16],
    sfp: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
  }}
}};
function unifiRuntime(config) {{ return config?.__runtime || null; }}
function exactModelVisualRecommendation(model) {{
  const map = MODEL_MAPS[String(model || '')];
  return map ? {{ unifi_api_port_map: map }} : null;
}}
{functions}
function runtime(max, model = '') {{
  return {{ model, ports: Array.from({{ length: max }}, (_, i) => ({{ idx: i + 1 }})) }};
}}
function expectIdx(actual, expected, label) {{
  const got = actual?.idx ?? null;
  if (got !== expected) throw new Error(`${{label}}: got ${{got}}, expected ${{expected}}`);
}}
function expectNull(actual, label) {{
  if (actual !== null) throw new Error(`${{label}}: expected null, got ${{JSON.stringify(actual)}}`);
}}

// Existing sequential UniFi devices must retain the Core 2.4.8 contract.
const legacy48 = {{
  data_source: 'unifi_api',
  unifi_rj45_ports: 48,
  __runtime: runtime(52, 'US 48 PoE 500W')
}};
expectIdx(unifiAccessPort(legacy48, 1), 1, 'legacy RJ45 1');
expectIdx(unifiAccessPort(legacy48, 48), 48, 'legacy RJ45 48');
expectIdx(unifiSfpPort(legacy48, 1), 49, 'legacy optical 1');
expectIdx(unifiSfpPort(legacy48, 4), 52, 'legacy optical 4');

// Preserve the historical explicit SFP-offset path unchanged.
const legacyOffset = {{
  data_source: 'unifi_api',
  unifi_rj45_ports: 99,
  unifi_sfp_port_offset: 24,
  __runtime: runtime(30)
}};
expectIdx(unifiSfpPort(legacyOffset, 1), 25, 'legacy explicit SFP offset');

// Card/config explicit maps take priority and support optical-first hardware.
const directXg = {{
  data_source: 'unifi_api',
  unifi_api_port_map: MODEL_MAPS['US XG 16'],
  unifi_rj45_ports: 4,
  __runtime: runtime(16, 'US XG 16')
}};
expectIdx(unifiAccessPort(directXg, 1), 13, 'direct XG16 RJ45 1');
expectIdx(unifiAccessPort(directXg, 4), 16, 'direct XG16 RJ45 4');
expectIdx(unifiSfpPort(directXg, 1), 1, 'direct XG16 optical 1');
expectIdx(unifiSfpPort(directXg, 12), 12, 'direct XG16 optical 12');
expectNull(unifiAccessPort(directXg, 5), 'direct XG16 out-of-range RJ45');
expectNull(unifiSfpPort(directXg, 13), 'direct XG16 out-of-range optical');

// Exact-model registry metadata supplies the same map when YAML has no override.
const registryXg = {{
  data_source: 'unifi_api',
  unifi_rj45_ports: 4,
  __runtime: runtime(16, 'US XG 16')
}};
expectIdx(unifiAccessPort(registryXg, 1), 13, 'registry XG16 RJ45 1');
expectIdx(unifiSfpPort(registryXg, 12), 12, 'registry XG16 optical 12');

// A card-level override wins over exact-model registry metadata.
const override = {{
  data_source: 'unifi_api',
  unifi_api_port_map: {{ rj45: [9], sfp: [8] }},
  __runtime: runtime(16, 'US XG 16')
}};
expectIdx(unifiAccessPort(override, 1), 9, 'explicit override RJ45');
expectIdx(unifiSfpPort(override, 1), 8, 'explicit override optical');
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
