from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "js" / "switch-vision.js"
MIRROR = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"


def js_function(source: str, name: str) -> str:
    match = re.search(r"^function " + re.escape(name) + r"\(", source, re.MULTILINE)
    if not match:
        raise AssertionError(f"Missing JavaScript function: {name}")
    close = re.search(r"^}", source[match.start():], re.MULTILINE)
    if not close:
        raise AssertionError(f"Unclosed JavaScript function: {name}")
    return source[match.start():match.start() + close.end()]


class PerPortPoeLedTests(unittest.TestCase):
    def test_dedicated_poe_option_without_power_or_quick_select(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        self.assertIn('const SV_OPTIONAL_PORT_LED_PARTS = Object.freeze(["led_poe"])', source)
        for marker in (
            'option("led_poe", "PoE LED")',
            'data-cv-field="poe-led-shape"',
            'data-cv-action="show-poe-led"',
            'data-cv-action="hide-poe-led"',
            'if (port[`${part}_show`] !== true) continue;',
            'led_poe_size', 'led_poe_shape',
            'optionalPortLedClass(hass, config, n, part, calibrationTestMode)',
        ):
            self.assertIn(marker, source)
        for removed in ("led_power", "power-led-shape", "all_poe_leds", "All PoE LEDs"):
            self.assertNotIn(removed, source)

    def test_live_poe_requires_mapped_direct_port_evidence(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        helpers = "\n".join(js_function(source, name) for name in (
            "usableValue", "firstEntityValue", "poePortStatusLabel",
            "mappedPortNumber", "snmpPortPoeActive", "optionalPortLedClass",
        ))
        script = r"""
const assert = require('node:assert/strict');
function rawEntityState(hass, id) { return hass?.states?.[id]?.state ?? null; }
function normalizeEntityPrefix(config) { return config.member || 'sw1'; }
function configuredEntity(config, n, type) {
  return config?.entities?.[`${n}:${type}`] || null;
}
function hasUnifiBinding(config) { return Boolean(config.unifi_device_id); }
function unifiBoundAccessPort(config, port) { return config?.unifi_ports?.[port] || null; }
""" + helpers + r"""
const off = 'cv-led-off', on = 'cv-led-poe';
function hass(data) {
  return {states:Object.fromEntries(Object.entries(data).map(([id,state])=>[id,{state}]))};
}
const cfg = {member:'sw1',port_entity_offset:24};
assert.equal(optionalPortLedClass(hass({'sensor.sw1_port_25_poe_status_code':'3'}),cfg,1,'led_poe'),on);
assert.equal(optionalPortLedClass(hass({'sensor.sw1_port_25_poe_status_code':'2'}),cfg,1,'led_poe'),off);
assert.equal(optionalPortLedClass(hass({'sensor.sw1_port_25_poe_status_code':'4','sensor.sw1_port_25_poe_power':'6'}),cfg,1,'led_poe'),off);
assert.equal(optionalPortLedClass(hass({'sensor.sw1_port_25_poe_power':'6.5'}),cfg,1,'led_poe'),on);
assert.equal(optionalPortLedClass(hass({'sensor.sw1_port_25_poe_power':'0'}),cfg,1,'led_poe'),off);
assert.equal(optionalPortLedClass(hass({'sensor.sw1_port_25_poe_power':'unavailable'}),cfg,1,'led_poe'),off);
assert.equal(optionalPortLedClass(hass({'sensor.sw1_port_1_poe_status_code':'3'}),cfg,1,'led_poe'),off);
assert.equal(optionalPortLedClass(hass({}),cfg,1,'led_poe',true),on);
assert.equal(optionalPortLedClass(hass({}),cfg,1,'led_power',true),off);
const explicit = {member:'sw1',entities:{'1:poe_status':'sensor.special_pse'}};
assert.equal(optionalPortLedClass(hass({'sensor.special_pse':'deliveringPower'}),explicit,1,'led_poe'),on);
const unifi = {unifi_device_id:'switch1',unifi_ports:{1:{poe:{available:true,enabled:true,state:'DOWN'}}}};
assert.equal(optionalPortLedClass(hass({'sensor.sw1_port_1_poe_status_code':'3'}),unifi,1,'led_poe'),off);
unifi.unifi_ports[1].poe.state='UP';
assert.equal(optionalPortLedClass(hass({}),unifi,1,'led_poe'),on);
unifi.unifi_ports[1].poe.available=false;
assert.equal(optionalPortLedClass(hass({}),unifi,1,'led_poe'),off);
console.log('PASS_PER_PORT_POE_SNMP_UNIFI_OFF_UNKNOWN_MAPPING_TEST');
"""
        result = subprocess.run(
            ["node", "-e", script],
            cwd=ROOT,
            text=True, capture_output=True, check=False, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS_PER_PORT_POE_SNMP_UNIFI_OFF_UNKNOWN_MAPPING_TEST", result.stdout)

    def test_mirror_after_build(self) -> None:
        self.assertEqual(CARD.read_bytes(), MIRROR.read_bytes())


if __name__ == "__main__":
    unittest.main()
