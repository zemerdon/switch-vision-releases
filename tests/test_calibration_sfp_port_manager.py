#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "src" / "js" / "switch-vision.js"
COMPONENT = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
CALIBRATION_DIR = ROOT / "src" / "calibration"


def logical_sfp_number(key: str) -> int:
    numbers = re.findall(r"\d+", str(key))
    return int(numbers[-1]) if numbers else 0


def assert_no_logical_sfp_collisions(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    seen: dict[int, str] = {}
    for key in (data.get("sfp") or {}):
        number = logical_sfp_number(key)
        if number <= 0:
            continue
        previous = seen.get(number)
        assert previous is None, (
            f"{path.relative_to(ROOT)}: SFP keys {previous!r} and {key!r} "
            f"both resolve to logical uplink {number}"
        )
        seen[number] = key


def main() -> int:
    source = CANONICAL.read_text(encoding="utf-8")
    component = COMPONENT.read_text(encoding="utf-8")
    assert source == component, "canonical and Home Assistant card JavaScript must remain byte-identical"

    required = [
        "function sortedCalibrationSfpKeys(cal)",
        "function nextCalibrationSfpNumber(cal)",
        "function cloneCalibrationSfp(cal, sourceKey, newKey, offsetX = 12, offsetY = 0)",
        "function calibrationSfpKeyCollision(entries, ignoredKey = null)",
        "function calibrationSfpKeyValidationMessage(value)",
        'data-cv-action="add-sfp"',
        'data-cv-field="sfp-key"',
        'data-cv-action="rename-sfp"',
        ">Duplicate selected</button>",
        'if (["add-port", "add-sfp", "duplicate-port"].includes(action))',
        'action === "duplicate-port" && editable?.type === "sfp"',
        "const sfpCollision = calibrationSfpKeyCollision(raw.sfp);",
        "calibrationSfpCollisionMessage(sfpCollision)",
        'if (!calibrationEnabled(config) && !configuredPortCountAllows(config, "port_count", n)) continue;',
        'if (!calibrationEnabled(config) && !configuredPortCountAllows(config, "sfp_port_count", sfpPort)) continue;',
        'if (!portCount && !sfpCount) errors.push("The profile contains no RJ45 or SFP/uplink positions.");',
        'const firstSfpKey = sortedCalibrationSfpKeys(cal)[0];',
        'firstSfpKey ? `sfp:${sfpPortNumber(firstSfpKey)}` : "all"',
        'firstPortKey ? `port:${firstPortKey}` : "all"',
        'option("entire", type === "sfps" ? "Entire SFP ports" : "Entire port")',
        'if (editable.type === "sfp" && editable.part === "entire")',
        'const moveEntireSfp = (sfp) => {',
        'movePoint(sfpLedPoint(sfp, "led_left", true), dx, dy);',
        'movePoint(sfpLedPoint(sfp, "led_right", true), dx, dy);',
        'movePoint(sfp.label, dx, dy);',
        'data-target="sfps" data-part="entire">All SFP</button>',
        'geometryTransferKeysMatch(current.status_leds, geometry.status_leds, { ignoreMode: true })',
    ]
    for marker in required:
        assert marker in source, f"missing SFP port-manager contract marker: {marker}"

    assert 'data-cv-action="add-port">Add port</button>' not in source, "legacy generic Add port label returned"
    assert 'data-cv-action="duplicate-port">Duplicate port</button>' not in source, "legacy duplicate label returned"
    assert 'if (!configuredPortCountAllows(config, "port_count", n)) continue;' not in source, "Calibration RJ45 rendering is still capped by physical port_count"
    assert 'if (!configuredPortCountAllows(config, "sfp_port_count", sfpPort)) continue;' not in source, "Calibration SFP rendering is still capped by physical sfp_port_count"
    assert 'At least one visual RJ45 port must remain' not in source, "final RJ45 deletion is still blocked"
    assert 'The profile contains no RJ45 port positions.' not in source, "SFP-only calibration profiles are still rejected"
    assert 'calibration_target: `port:${nextKey}`' not in source, "final RJ45 deletion can still select port:undefined"
    assert 'calibration_target: nextKey ? `sfp:${sfpPortNumber(nextKey)}` : `port:${sortedCalibrationPortKeys(cal)[0]}`' not in source, "final SFP deletion can still select port:undefined"
    assert "RJ45 port geometry does not match the current calibration topology." not in source, "Geometry Import still requires exact RJ45 topology"
    assert "SFP/uplink geometry does not match the current calibration topology." not in source, "Geometry Import still requires exact SFP/uplink topology"
    assert 'geometryTransferKeysMatch(current.status_leds, geometry.status_leds, { ignoreMode: true })' in source, "Geometry Import no longer protects status LED topology"

    for path in sorted(CALIBRATION_DIR.glob("*.json")):
        assert_no_logical_sfp_collisions(path)

    # The legacy Cisco 3650 aliases intentionally remain valid and distinct.
    assert logical_sfp_number("G1") == 1
    assert logical_sfp_number("G3/TE3") == 3
    assert logical_sfp_number("SFP12") == 12
    assert logical_sfp_number("TE12") == 12

    print("Switch Vision calibration SFP port-manager regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
