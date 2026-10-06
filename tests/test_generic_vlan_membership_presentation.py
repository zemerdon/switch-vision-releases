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


class GenericVlanMembershipPresentationTests(unittest.TestCase):
    def test_non_juniper_membership_list_and_single_vlan_compatibility(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        functions = "\n\n".join(
            extract_js_function(source, signature)
            for signature in (
                "function usableValue(value)",
                "function trimText(value, max = 24)",
                "function cleanVlanValue(value)",
                "function cleanVlanList(value)",
                "function cleanTrunkStatus(value)",
                "function deriveVlan(vlanCandidate, trunkStatusCandidate = null)",
                "function vlanPresentation(vlanCandidate, allowedVlansCandidate = null, trunkStatusCandidate = null, isJuniper = false)",
            )
        )
        harness = f"""
{functions}
const multi = vlanPresentation("1", "20,10,1", "TRUNK", false);
if (multi.label !== "VLANS") throw new Error(JSON.stringify(multi));
if (multi.value !== "1, 10, 20") throw new Error(JSON.stringify(multi));

const single = vlanPresentation("100", null, "ACCESS", false);
if (single.label !== "VLAN") throw new Error(JSON.stringify(single));
if (single.value !== "100") throw new Error(JSON.stringify(single));

const legacyTrunk = vlanPresentation(null, null, "TRUNK", false);
if (legacyTrunk.value !== "TRUNK") throw new Error(JSON.stringify(legacyTrunk));

const juniper = vlanPresentation("10", null, "TRUNK", true);
if (juniper.label !== "VLAN") throw new Error(JSON.stringify(juniper));
if (juniper.value !== "10") throw new Error(JSON.stringify(juniper));
"""
        result = subprocess.run(
            ["node", "-e", harness],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_copper_ports_bind_generated_vlan_mode_entity(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        selected = extract_js_function(
            source, "function selectedPortDetails(hass, config, port)"
        )
        self.assertIn('configuredEntity(config, internalPort, "native_vlan")', selected)
        self.assertIn("sensor.${member}_port_${n}_native_vlan", selected)
        self.assertIn('configuredEntity(config, internalPort, "vlan_mode")', selected)
        self.assertIn("sensor.${member}_port_${n}_vlan_mode", selected)
        self.assertIn("vlanPresentation(", selected)


if __name__ == "__main__":
    unittest.main()
