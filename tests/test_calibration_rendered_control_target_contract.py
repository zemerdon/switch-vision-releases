#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "js" / "switch-vision.js"
COMPONENT = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")

    for marker in (
        "function calibrationControlBoxFromRenderedElement(svg, element)",
        "element.getBoundingClientRect()",
        "svg.getScreenCTM()",
        "matrix.inverse()",
        'data-cv-calibration-control="calibration_button"',
        'data-cv-calibration-control="test_mode_button"',
        'visibility:hidden',
        "function syncRenderedCalibrationControlOverlayBoxes(svg, calibration, root)",
        "syncRenderedCalibrationControlOverlayBoxes(svg, renderCal, this.shadowRoot);",
    ):
        assert marker in source, marker

    redraw_start = source.index("  redrawSwitchSvg(activeCalibration = null) {")
    redraw_end = source.index("\n  render() {", redraw_start)
    redraw = source[redraw_start:redraw_end]
    sync_at = redraw.index("syncRenderedCalibrationControlOverlayBoxes(svg, renderCal, this.shadowRoot);")
    overlay_at = redraw.index("drawCalibrationOverlay(svg, {")
    assert sync_at < overlay_at, "rendered control boxes must be synchronized before the calibration overlay is drawn"

    helper_start = source.index("function calibrationControlBoxFromRenderedElement(svg, element)")
    helper_end = source.index("\n}\n\nfunction syncRenderedCalibrationControlOverlayBoxes", helper_start) + 2
    helper = source[helper_start:helper_end]
    assert "getBoundingClientRect" in helper
    assert "getScreenCTM" in helper
    assert "matrixTransform(inverse)" in helper

    assert SOURCE.read_bytes() == COMPONENT.read_bytes(), "card JS copies must remain byte-identical"

    print("Core rendered Calibration/Test Mode target alignment contract: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
