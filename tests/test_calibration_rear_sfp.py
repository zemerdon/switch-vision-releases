#!/usr/bin/env python3
"""Rear SFP identity, telemetry and calibration UI regression (no hardware mutation)."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
CANONICAL = ROOT / "src" / "js" / "switch-vision.js"


def function(source: str, name: str) -> str:
    start = source.index(f"function {name}(")
    end = source.index("\n}\n", start) + 2
    return source[start:end]


def main() -> int:
    source = CANONICAL.read_text(encoding="utf-8")
    assert source == CARD.read_text(encoding="utf-8")
    for marker in (
        "SV_REAR_SFP_SLOT_BASE = 1000000",
        'data-cv-action="add-rear-sfp"',
        'data-cv-target-group="rear_sfp"',
        '<label>rSFP Targets',
        'data-cv-field="rear-part"',
        'rearSfpTargetSelected ? "" : "disabled"',
        'this.shadowRoot.querySelectorAll(\'[data-cv-field="part"], [data-cv-field="rear-part"]\')',
        'calibration_target: `sfp:${sfpPortNumber(newKey)}`',
        '__rear_sfp_bindings: rearSfpBindings(this.config, renderCal)',
        "!rearSfpOrdinalFromPort(sfpPort)",
        "if (rearSfpOrdinalFromPort(n)) {",
        "const sfpPort = sfpPortNumber(name);",
    ):
        assert marker in source, f"missing rear SFP contract: {marker}"
    for mapping_control in ('data-cv-field="rear-sfp-interface"', 'data-cv-field="rear-sfp-entity-base"', 'data-cv-action="set-rear-sfp-binding"'):
        assert mapping_control not in source, f"mapping should belong to Discovery, not Calibration: {mapping_control}"
    assert "const hp3500 = " not in function(source, "rearSfpBindings"), "rSFP binding must not depend on model"
    manager_order = (
        'data-cv-action="add-port"',
        'data-cv-action="add-sfp"',
        'data-cv-action="add-rear-sfp"',
        'data-cv-action="duplicate-port"',
        'data-cv-action="remove-port"',
        'data-cv-action="remove-all-rj45"',
        'data-cv-action="remove-all-sfp"',
        'data-cv-action="remove-all-rear-sfp"',
    )
    assert [source.index(marker) for marker in manager_order] == sorted(source.index(marker) for marker in manager_order), "rSFP actions belong in the Port manager in hardware-type order"
    targets = source.split('cv-cal-port-targets-row cv-cal-port-manager-main', 1)[1].split('</div>', 1)[0]
    selector_order = (
        'data-cv-target-group="sfp"',
        'data-cv-field="part"',
        'data-cv-target-group="rear_sfp"',
        'data-cv-field="rear-part"',
    )
    assert [targets.index(marker) for marker in selector_order] == sorted(targets.index(marker) for marker in selector_order), "front SFP/Part must precede rear SFP/Part"
    assert source.count('data-cv-action="add-rear-sfp"') == 1
    assert source.count('data-cv-action="remove-all-rear-sfp"') == 1
    assert 'cv-cal-rear-sfp-actions-row' not in source
    assert source.count("const sfpPort = sfpPortNumber(name);") == 2, "rendered rear slots and click hitboxes must share the collision-safe rear identity"
    assert source.count('<select class="cv-cal-select" data-cv-field="part"') == 1, "front Part selector must remain unique"
    assert source.count('<select class="cv-cal-select" data-cv-field="rear-part"') == 1, "rear Part selector must remain unique"
    for path in (CANONICAL, CARD):
        subprocess.run(["node", "--check", str(path)], check=True, timeout=30, capture_output=True)

    functions = (
        "rearSfpOrdinal", "rearSfpOrdinalFromPort", "sfpPortNumber",
        "rearSfpEntityBase", "rearSfpEntity", "rearSfpBindings",
        "hp3500ylOpticalPilot", "hpRearOpticIfIndex", "hpOpticalSfpIndex",
        "sortedCalibrationSfpKeys", "nextCalibrationSfpNumber",
        "nextCalibrationRearSfpNumber", "sfpStatusEntities",
        "sfpByteEntities", "selectedSfpDetails",
    )
    prelude = """
const assert = require("node:assert/strict");
const SV_PROFILE_MAX_UPLINKS = 128;
const SV_REAR_SFP_SLOT_BASE = 1000000;
function normalizeEntityPrefix(config) { return config.member || "sw1"; }
function normalizeMember(config) { return config.member || "sw1"; }
function n4032QsfpEntity() { return null; }
function n4032RearQsfpEntity() { return null; }
function templateEntity() { return null; }
function entityState(hass, id) { return hass?.states?.[id] ? String(hass.states[id].state).toLowerCase() : null; }
function firstEntityValue(hass, ids) { return ids.map(id => hass?.states?.[id]?.state).find(v => v !== undefined) || null; }
function trimText(value) { return String(value); }
function sfpSpeedMbps() { return 10000; }
function sfpIsUp(hass, config, n) { const id = rearSfpEntity(config, n, "status"); return entityState(hass,id) === "up"; }
function speedLabel(speed, up) { return up ? "10G Full" : "Down"; }
"""
    body = "\n".join(function(source, name) for name in functions)
    proof = """
const cal = {sfp: {
 SFP1: {center: [50,50]},
 SFP2: {center: [80,50]},
 rSFP1: {rear_interface: "A1", center: [100,100]},
 rSFP2: {center: [200,100]},
 rSFP3: {center: [300,100]},
 rSFP4: {rear_interface: "A4", center: [400,100]},
}};
assert.equal(sfpPortNumber("SFP1"), 1);
assert.equal(sfpPortNumber("G3/TE3"), 3);
assert.equal(sfpPortNumber("rSFP1"), 1000001);
assert.equal(sfpPortNumber("rSFP2"), 1000002);
assert.equal(rearSfpOrdinal("rSFP129"), 0);
assert.equal(nextCalibrationSfpNumber(cal), 3);
assert.equal(nextCalibrationRearSfpNumber(cal), 5);
assert.equal(new Set(Object.keys(cal.sfp).map(sfpPortNumber)).size, 6);
assert.deepEqual(Object.keys(cal.sfp).filter(rearSfpOrdinal), ["rSFP1", "rSFP2", "rSFP3", "rSFP4"]);
assert.deepEqual([2, 3].map(n => cal.sfp[`rSFP${n}`].center), [[200,100], [300,100]]);
// A model label, calibration label, or inactive port must not fabricate sensors.
const hp = {member: "sw9", switch_model: "HP J8693A Switch 3500yl-48G"};
const noBindings = rearSfpBindings(hp, cal);
for (let slot = 1; slot <= 4; slot++) {
  assert.equal(noBindings[String(1000000 + slot)].entity_base, null);
}
assert.equal(noBindings["1000001"].interface_name, "A1");
assert.equal(noBindings["1000004"].interface_name, "A4");
assert.equal(hpRearOpticIfIndex(hp, 1000001), null, "artwork alone is not module evidence");
const hpObserved = {...hp, rear_sfp_bindings: {
  rSFP1: {interface_name:"A1", entity_base:"sensor.sw9_rear_10g_1", if_index:49},
  rSFP2: {interface_name:"A2", entity_base:"sensor.sw9_rear_10g_2", if_index:50},
  rSFP3: {interface_name:"A3", entity_base:"sensor.sw9_rear_10g_3", if_index:51},
  rSFP4: {interface_name:"A4", entity_base:"sensor.sw9_rear_10g_4", if_index:52}
}};
assert.equal(hpRearOpticIfIndex(hpObserved, 1000001), 49);
assert.equal(hpRearOpticIfIndex(hpObserved, 1000004), 52);
assert.equal(hpOpticalSfpIndex(hpObserved, 1000002), null, "CX4 A2 cannot refresh optical DOM");
assert.equal(hpOpticalSfpIndex(hpObserved, 1000003), null, "CX4 A3 cannot refresh optical DOM");
for (const bad of [
  {interface_name:"A1", entity_base:"sensor.sw9_rear_10g_1", if_index:52},
  {interface_name:"A1", if_index:49},
  {interface_name:"A1", entity_base:"sensor.sw9_rear_10g_1", if_index:"49"}
]) {
  assert.equal(hpRearOpticIfIndex({...hpObserved, rear_sfp_bindings:{...hpObserved.rear_sfp_bindings, rSFP1:bad}},1000001),null);
}
assert.equal(hpRearOpticIfIndex({...hpObserved,switch_model:"Other Vendor"},1000001),null);
assert.equal(rearSfpBindings(hpObserved,cal)["1000001"].if_index,49);
assert.equal(rearSfpBindings(hpObserved,cal)["1000002"].if_index,50);
const generic = {member: "sw9", switch_model: "Other Vendor 4000", rear_sfp_bindings: {
  rSFP1: {interface_name: "xe-0/1/0", entity_base: "sensor.sw9_rear_10g_1"},
  rSFP4: {interface_name: "xe-0/1/3", entity_base: "sensor.sw9_rear_10g_4"},
}};
const bindings = rearSfpBindings(generic, cal);
const render = {...generic, __rear_sfp_bindings: bindings};
assert.equal(bindings["1000001"].interface_name, "xe-0/1/0");
assert.equal(bindings["1000001"].entity_base, "sensor.sw9_rear_10g_1");
assert.equal(bindings["1000002"].entity_base, null);
assert.equal(bindings["1000003"].entity_base, null);
assert.equal(bindings["1000004"].entity_base, "sensor.sw9_rear_10g_4");
assert.deepEqual(sfpStatusEntities(render, "sw9", 1000001), ["sensor.sw9_rear_10g_1_status"]);
assert.deepEqual(sfpStatusEntities(render, "sw9", 1000002), []);
assert.deepEqual(sfpStatusEntities(render, "sw9", 1000003), []);
assert.deepEqual(sfpStatusEntities(render, "sw9", 1000004), ["sensor.sw9_rear_10g_4_status"]);
assert.deepEqual(sfpByteEntities(render, 1000004, "tx"), ["sensor.sw9_rear_10g_4_tx_bytes"]);
assert.deepEqual(sfpByteEntities(render, 1000004, "rx"), ["sensor.sw9_rear_10g_4_rx_bytes"]);
assert.deepEqual(sfpStatusEntities(render, "sw9", 1).some(x => x && x.includes("rear_10g")), false);
const observed = structuredClone(cal);
observed.sfp.rSFP1.rear_entity_base = "sensor.sw4_uplink_25";
assert.equal(rearSfpBindings({member: "sw4"}, observed)["1000001"].entity_base, "sensor.sw4_uplink_25");
const explicitlyUnmapped = {rear_sfp_bindings: {rSFP1: {interface_name: "xe-0/1/0"}}};
assert.equal(rearSfpBindings(explicitlyUnmapped, observed)["1000001"].entity_base, null);
const noModule = {...hp, __rear_sfp_bindings: noBindings};
assert.equal(selectedSfpDetails({states: {}}, noModule, 1000001).link, "—", "no module has no known Down state");
assert.equal(selectedSfpDetails({states: {}}, render, 1000004).link, "—", "missing sensor is unknown");
const liveId = "sensor.sw9_rear_10g_4_status";
assert.equal(selectedSfpDetails({states: {[liveId]: {state: "unavailable"}}}, render, 1000004).link, "—", "unavailable sensor is unknown");
assert.equal(selectedSfpDetails({states: {[liveId]: {state: "up"}}}, render, 1000004).link, "10G Full", "A4 live link is shown");
assert.equal(selectedSfpDetails({states: {[liveId]: {state: "down"}}}, render, 1000004).link, "Down", "real down remains down");
console.log("Rear SFP behavior: PASS");
"""
    result = subprocess.run(["node", "-e", prelude + body + proof], cwd=ROOT, timeout=30, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr[-2000:]
    assert "Rear SFP behavior: PASS" in result.stdout
    print("Switch Vision rear SFP calibration regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
