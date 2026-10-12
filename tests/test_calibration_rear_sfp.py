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
        '<label>rSFP Target',
        'data-cv-field="rear-part"',
        'rearSfpTargetSelected ? "" : "disabled"',
        'this.shadowRoot.querySelectorAll(\'[data-cv-field="part"], [data-cv-field="rear-part"]\')',
        'data-cv-field="rear-sfp-interface"',
        'data-cv-field="rear-sfp-entity-base"',
        'data-cv-action="set-rear-sfp-binding"',
        'calibration_target: `sfp:${sfpPortNumber(newKey)}`',
        '__rear_sfp_bindings: rearSfpBindings(this.config, renderCal)',
        "!rearSfpOrdinalFromPort(sfpPort)",
        "if (rearSfpOrdinalFromPort(n)) {",
    ):
        assert marker in source, f"missing rear SFP contract: {marker}"
    selector_order = (
        'data-cv-target-group="sfp"',
        'data-cv-field="part"',
        'data-cv-target-group="rear_sfp"',
        'data-cv-field="rear-part"',
        'data-cv-action="add-rear-sfp"',
        'data-cv-action="add-port"',
    )
    assert [source.index(marker) for marker in selector_order] == sorted(source.index(marker) for marker in selector_order), "rSFP Target and Part must follow the front selectors before port manager"
    assert source.count('<select class="cv-cal-select" data-cv-field="part"') == 1, "front Part selector must remain unique"
    assert source.count('<select class="cv-cal-select" data-cv-field="rear-part"') == 1, "rear Part selector must remain unique"
    for path in (CANONICAL, CARD):
        subprocess.run(["node", "--check", str(path)], check=True, timeout=30, capture_output=True)

    functions = (
        "rearSfpOrdinal", "rearSfpOrdinalFromPort", "sfpPortNumber",
        "rearSfpEntityBase", "rearSfpEntity", "rearSfpBindings",
        "sortedCalibrationSfpKeys", "nextCalibrationSfpNumber",
        "nextCalibrationRearSfpNumber", "sfpStatusEntities",
        "sfpByteEntities",
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
"""
    body = "\n".join(function(source, name) for name in functions)
    proof = """
const cal = {sfp: {
 SFP1: {center: [50,50]},
 SFP2: {center: [80,50]},
 rSFP1: {rear_interface: "A1", center: [100,100]},
 rSFP2: {rear_interface: "A4", center: [200,100]},
}};
assert.equal(sfpPortNumber("SFP1"), 1);
assert.equal(sfpPortNumber("G3/TE3"), 3);
assert.equal(sfpPortNumber("rSFP1"), 1000001);
assert.equal(sfpPortNumber("rSFP2"), 1000002);
assert.equal(rearSfpOrdinal("rSFP129"), 0);
assert.equal(nextCalibrationSfpNumber(cal), 3);
assert.equal(nextCalibrationRearSfpNumber(cal), 3);
assert.equal(new Set(Object.keys(cal.sfp).map(sfpPortNumber)).size, 4);
const hp = {member: "sw9", switch_model: "HP J8693A Switch 3500yl-48G"};
const bindings = rearSfpBindings(hp, cal);
const render = {...hp, __rear_sfp_bindings: bindings};
assert.equal(bindings["1000001"].entity_base, "sensor.sw9_rear_10g_1");
assert.equal(bindings["1000002"].entity_base, "sensor.sw9_rear_10g_4");
assert.deepEqual(sfpStatusEntities(render, "sw9", 1000001), ["sensor.sw9_rear_10g_1_status"]);
assert.deepEqual(sfpStatusEntities(render, "sw9", 1000002), ["sensor.sw9_rear_10g_4_status"]);
assert.deepEqual(sfpByteEntities(render, 1000002, "tx"), ["sensor.sw9_rear_10g_4_tx_bytes"]);
assert.deepEqual(sfpByteEntities(render, 1000002, "rx"), ["sensor.sw9_rear_10g_4_rx_bytes"]);
assert.deepEqual(sfpStatusEntities(render, "sw9", 1).some(x => x && x.includes("rear_10g")), false);
const unknown = {member: "sw4", switch_model: "Other Vendor 4000"};
assert.equal(rearSfpBindings(unknown, cal)["1000001"].entity_base, null);
assert.deepEqual(sfpStatusEntities({...unknown, __rear_sfp_bindings: rearSfpBindings(unknown, cal)}, "sw4", 1000001), []);
const observed = structuredClone(cal);
observed.sfp.rSFP1.rear_entity_base = "sensor.sw4_uplink_25";
assert.equal(rearSfpBindings(unknown, observed)["1000001"].entity_base, "sensor.sw4_uplink_25");
console.log("Rear SFP behavior: PASS");
"""
    result = subprocess.run(["node", "-e", prelude + body + proof], cwd=ROOT, timeout=30, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr[-2000:]
    assert "Rear SFP behavior: PASS" in result.stdout
    print("Switch Vision rear SFP calibration regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
