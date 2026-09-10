#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "js" / "switch-vision.js"
COMPONENT = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")

    # Test Mode is position-only: direct X/Y and arrow nudging are supported.
    position_marker = '["logo", "calibration_button", "test_mode_button", "status_box", "status_box_2"].includes(editable.type)'
    assert source.count(position_marker) >= 2
    assert 'if (editable.type === "calibration_button" || editable.type === "test_mode_button") {' in source
    assert 'const testModeUi = ui.test_mode_button || {};' in source
    assert 'cal.ui.test_mode_button = original.ui.test_mode_button;' in source

    # Test Mode position is part of exported/persisted calibration UI state.
    export_start = source.index("function calibrationExportData(cal) {")
    export_end = source.index("\n}\n", export_start) + 2
    export_block = source[export_start:export_end]
    assert "ui: uiFromCalibration(cal)," in export_block
    assert "return stableCalibrationJson(calibrationExportData(cal));" in source

    # The working calibration must drive the live TEST MODE badge immediately.
    assert 'calibration.ui?.test_mode_button' not in source
    assert 'uiFromCalibration(calibrationRenderSpaceData(this.calibrationData())).calibration_button || {}' in source

    # Position-only means no W/H sizing and no pointer hitbox/drag target.
    size_block = source[source.index("function calibrationSizePairs"):source.index("function nextCalibrationPortNumber")]
    assert '"test_mode_button"' not in size_block
    assert 'hitbox: null, ui: true' in source
    assert 'Position-only target: selected and movable via nudge or direct X/Y' in source

    # Build parity will copy canonical JS into the HA component.
    if SOURCE.read_bytes() == COMPONENT.read_bytes():
        assert 'const testModeUi = ui.test_mode_button || {};' in COMPONENT.read_text(encoding="utf-8")

    print("Core Test Mode calibration position contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
