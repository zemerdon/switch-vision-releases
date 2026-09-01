#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "src" / "js" / "switch-vision.js"
COMPONENT = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"

def main() -> int:
    source = CANONICAL.read_text(encoding="utf-8")
    component = COMPONENT.read_text(encoding="utf-8")
    assert source == component, "canonical and Home Assistant card JavaScript must remain byte-identical"

    version_line = next((line for line in source.splitlines() if line.startswith('const SV_VERSION = \"')), "")
    assert version_line, "Core version marker is missing"
    version_text = version_line.split('\"', 2)[1]
    version = tuple(int(part) for part in version_text.split("."))
    assert version >= (2, 6, 21), f"v2.6.21 Calibration Core contract requires Core >= 2.6.21, got {version}"

    required = [
        '"assets": false,',
        'this.calibrationSectionOpen("assets", false)',
        'const part = requestedPart === "number" ? "label" : requestedPart;',
        'calibration_target: `sfp:${sfpNumber}`',
        'calibration_part: "entire"',
        'return ["center", "number", "led_left", "led_right"].includes(part);',
        'movePoint(editable.item.number, dx, dy);',
        'movePoint(port.number, dx, dy);',
        'copy.number = [...copy.center];',
        'copy.label = [...copy.center];',
        'function calibrationSfpKeysByParity(cal, parity = "all")',
        'sfpPortNumber(key) % 2 === 1',
        'sfpPortNumber(key) % 2 === 0',
        'data-target="sfps_odd_entire" data-part="entire"',
        'data-target="sfps_odd_led_left" data-part="led_left"',
        'data-target="sfps_odd_led_right" data-part="led_right"',
        'data-target="sfps_odd_labels" data-part="label"',
        'data-target="sfps_even_entire" data-part="entire"',
        'data-target="sfps_even_led_left" data-part="led_left"',
        'data-target="sfps_even_led_right" data-part="led_right"',
        'data-target="sfps_even_labels" data-part="label"',
        'nextConfig.calibration_port_selection = key;',
        'nextConfig.calibration_sfp_selection = found.key;',
        'nextConfig.calibration_sfp_selection = resolvedSfpKeys.join(",");',
        'const isInterfaceTarget =',
        'value.startsWith("sfp:")',
        'value === "sfps"',
    ]
    for marker in required:
        assert marker in source, f"missing v2.6.21 Calibration Core contract marker: {marker}"
    assert source.count("movePoint(port.number, dx, dy);") >= 2, "RJ45 entire-port moves must carry the number label in group and direct-coordinate paths"

    forbidden = [
        'const SV_VERSION = "2.6.20";',
        '"assets": true,',
        'this.calibrationSectionOpen("assets", true)',
        'const part = requestedPart === "entire"\n              ? "center"',
        'calibration_target: `sfp:${sfpNumber}`, calibration_part: "center"',
    ]
    for marker in forbidden:
        assert marker not in source, f"legacy v2.6.20 Calibration Core behavior remains: {marker}"

    print("Switch Vision v2.6.21+ Calibration Core regression: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
