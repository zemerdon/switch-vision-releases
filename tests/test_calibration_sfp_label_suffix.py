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

    required = [
        'function sfpVisibleLabel(config, sfpPort, fallback, calibration = null) {',
        'Object.prototype.hasOwnProperty.call(ui, "sfp_label_suffix")',
        'const suffix = String(ui.sfp_label_suffix ?? "").trim().slice(0, 32);',
        'return `${sfpPort}${suffix ? ` ${suffix}` : ""}`;',
        'const defaultSfpLabel = sfpVisibleLabel(config, sfpPort, layoutLabel?.text || name, calibration);',
        'const visibleSfpLabel = String(sfp.display_name || defaultSfpLabel);',
        'data-cv-field="sfp-label-suffix"',
        'data-cv-action="apply-sfp-label-suffix"',
        'cal.ui.sfp_label_suffix = suffix;',
        'suffix ? `SFP/uplink suffix set: ${suffix}` : "SFP/uplink suffix cleared"',
        'delete copy.display_name;',
    ]
    for marker in required:
        assert marker in source, f"missing SFP label-suffix contract marker: {marker}"

    # Absence of the profile-level setting must preserve existing/factory label behaviour.
    helper_start = source.index("function sfpVisibleLabel(")
    helper_end = source.index("\n}\n", helper_start) + 3
    helper = source[helper_start:helper_end]
    assert helper.index('hasOwnProperty.call(ui, "sfp_label_suffix")') < helper.index("isJuniperEx3300(config)")
    assert 'return fallback;' in helper

    # Per-port display names remain the highest-priority presentation override.
    assert 'const visibleSfpLabel = String(sfp.display_name || defaultSfpLabel);' in source

    # The bulk suffix action is presentation-only: it writes the profile UI value,
    # not SFP keys, mappings, entities, numbering, or geometry.
    action_start = source.index('if (action === "apply-sfp-label-suffix")')
    action_end = source.index('\n        if (action === "toggle-port-label-bold")', action_start)
    action = source[action_start:action_end]
    assert "cal.ui.sfp_label_suffix = suffix;" in action
    for forbidden in (
        "cal.sfp[",
        "delete cal.sfp",
        "rename",
        "entity",
        "mapping",
        "center",
        "hitbox",
        "led_left",
        "led_right",
    ):
        assert forbidden not in action, f"suffix action unexpectedly touches {forbidden!r}"

    # New/duplicated SFPs deliberately discard a source custom display name so the
    # profile-level suffix becomes their default display presentation.
    clone_start = source.index("function cloneCalibrationSfp(")
    clone_end = source.index("\n}\n", clone_start) + 3
    clone = source[clone_start:clone_end]
    assert "delete copy.display_name;" in clone

    print("Switch Vision calibration SFP label suffix regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
