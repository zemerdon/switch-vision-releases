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
    assert 'const workingUi = uiFromCalibration(calibrationRenderSpaceData(this.calibrationData()));' in source
    assert 'const ui = workingUi.calibration_button || {};' in source
    assert 'const testModeUi = workingUi.test_mode_button || {};' in source
    assert 'const testModeUi = ui.test_mode_button || {};' not in source
    assert 'cal.ui.test_mode_button = original.ui.test_mode_button;' in source

    # Test Mode position is part of exported/persisted calibration UI state.
    export_start = source.index("function calibrationExportData(cal) {")
    export_end = source.index("\n}\n", export_start) + 2
    export_block = source[export_start:export_end]
    assert "ui: uiFromCalibration(cal)," in export_block
    assert "return stableCalibrationJson(calibrationExportData(cal));" in source

    # The working calibration must drive the live TEST MODE badge immediately.
    assert 'calibration.ui?.test_mode_button' not in source
    assert 'const workingUi = uiFromCalibration(calibrationRenderSpaceData(this.calibrationData()));' in source

    # Test Mode persists after Done for unobstructed faceplate inspection.
    # Cancel remains the explicit path that turns it off.
    handler_start = source.index("  attachCalibrationButtonHandler() {")
    handler_end = source.index("\n  baseCalibrationData() {", handler_start)
    handler = source[handler_start:handler_end]
    assert "calibration_test_mode: this.config?.calibration_test_mode === true" in handler
    assert "return config?.calibration_test_mode === true;" in source
    cancel_start = source.index('if (action === "cancel-calibration")')
    cancel_end = source.index('if (action === "refresh-assets")', cancel_start)
    cancel_block = source[cancel_start:cancel_end]
    assert "calibration_test_mode: false" in cancel_block

    # Persistent Test Mode owns the activity LEDs after Done. Live telemetry
    # may still trigger normal card redraws, but the independent activity
    # animation loop must neither start nor repaint while Test Mode is active.
    refresh_start = source.index("  refreshActivityLeds() {")
    refresh_end = source.index("\n  stopActivityAnimation() {", refresh_start)
    refresh_block = source[refresh_start:refresh_end]
    assert "calibrationTestModeEnabled(this.config)" in refresh_block
    scheduler_start = source.index("  scheduleActivityAnimationIfNeeded() {")
    scheduler_end = source.index("\n  set hass(hass) {", scheduler_start)
    scheduler_block = source[scheduler_start:scheduler_end]
    assert scheduler_block.count("calibrationTestModeEnabled(this.config)") >= 2

    # Position-only means no W/H sizing and no pointer hitbox/drag target.
    size_block = source[source.index("function calibrationSizePairs"):source.index("function nextCalibrationPortNumber")]
    assert '"test_mode_button"' not in size_block
    assert 'hitbox: null, ui: true' in source
    assert 'Position-only target: selected and movable via nudge or direct X/Y' in source

    # Build parity will copy canonical JS into the HA component.
    if SOURCE.read_bytes() == COMPONENT.read_bytes():
        component = COMPONENT.read_text(encoding="utf-8")
        assert 'const testModeUi = workingUi.test_mode_button || {};' in component
        assert 'const testModeUi = ui.test_mode_button || {};' not in component

    print("Core Test Mode calibration position contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
