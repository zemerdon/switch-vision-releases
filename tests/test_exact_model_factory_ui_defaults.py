#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "src" / "js" / "switch-vision.js"
CALIBRATION = ROOT / "src" / "calibration"


def main() -> None:
    frontend = FRONTEND.read_text(encoding="utf-8")
    start = frontend.index("  baseCalibrationData() {")
    end = frontend.index("\n  calibrationData() {", start)
    block = frontend[start:end]

    assert "const hasPersistedProfile = Boolean(" in block
    assert 'this._profileLoadInfo?.exists === true' in block
    assert 'typeof this._profileCalibration === "object"' in block
    assert "resolved.ui = uiFromCalibration(resolved);" in block

    preserve_start = block.index("if (hasPersistedProfile) {")
    preserve = block[preserve_start:]
    for marker in (
        "const savedUi = uiFromCalibration(saved);",
        'for (const key of ["logo", "status_panel", "status_panel_2", "calibration_button"])',
        "resolved.stack = cloneCalibrationData(saved?.stack || resolved.stack || {});",
        "resolved.management = cloneCalibrationData(saved?.management || resolved.management || {});",
        "if (savedUi?.faceplate) {",
        "resolved.ui.faceplate = cloneCalibrationData(savedUi.faceplate);",
    ):
        assert marker in preserve, marker

    generic = json.loads((CALIBRATION / "c3650.json").read_text(encoding="utf-8"))
    for filename, profile, faceplate in (
        ("faceplate-unifi-5rj45.json", "default_unifi_5_rj45", "unifi-5rj45.png"),
        ("faceplate-unifi-8rj45.json", "default_unifi_8_rj45", "unifi-8rj45.png"),
    ):
        factory = json.loads((CALIBRATION / filename).read_text(encoding="utf-8"))
        assert factory["profile"] == profile
        assert factory["ui"]["faceplate"]["file"] == faceplate
        assert factory["ui"]["logo"] != generic["ui"]["logo"], filename
        assert factory["ui"]["status_panel"] != generic["ui"]["status_panel"], filename

    print("Core exact-model factory UI default preservation: PASS")


if __name__ == "__main__":
    main()
