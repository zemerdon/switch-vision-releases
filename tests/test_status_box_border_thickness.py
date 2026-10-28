#!/usr/bin/env python3
"""Independent Status Box border thickness controls and saved-profile contract."""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "src/js/switch-vision.js").read_text(encoding="utf-8")


def segment(start: str, end: str) -> str:
    return JS[JS.index(start):JS.index(end, JS.index(start))]


class StatusBoxBorderThicknessTests(unittest.TestCase):
    def test_card_sources_are_identical(self) -> None:
        self.assertEqual(
            (ROOT / "src/js/switch-vision.js").read_bytes(),
            (ROOT / "src/custom_components/switch_vision/switch-vision-card.js").read_bytes(),
        )

    def test_each_thickness_control_follows_its_own_hide_button(self) -> None:
        first = segment('data-cv-action="status-row-toggle"', 'cv-cal-dual-port-status-outputs')
        second_start = first.index('data-cv-action="status2-row-toggle"')
        first_row, second_row = first[:second_start], first[second_start:]
        for row, field in (
            (first_row, "status-border-width"),
            (second_row, "status2-border-width"),
        ):
            self.assertRegex(
                row,
                r'data-cv-field="' + field +
                r'" type="number" min="0.25" max="3" step="0.25"',
            )
            self.assertIn('placeholder="0.25 – 3.00"', row)
            self.assertLess(row.index('"Hide"}</button>'), row.index('>Thickness'))
            self.assertIn('"disabled"', row)
        self.assertEqual(len(re.findall('data-cv-field="status-border-width"', first)), 1)
        self.assertEqual(len(re.findall('data-cv-field="status2-border-width"', JS)), 1)

    def test_legacy_profiles_keep_the_1_5_px_default(self) -> None:
        defaults = segment("function defaultUiLayout()", "\nfunction ")
        self.assertEqual(defaults.count("border_width: 1.5,"), 2)
        ensure = segment("function ensureCalibrationUi(cal)", "\nfunction ")
        self.assertIn(
            "cal.ui.status_panel.border_width = normaliseStatusPanelBorderWidth(cal.ui.status_panel.border_width)",
            ensure,
        )
        self.assertIn(
            "cal.ui.status_panel_2.border_width = normaliseStatusPanelBorderWidth(cal.ui.status_panel_2.border_width)",
            ensure,
        )

    def test_editor_writes_each_profile_without_card_override(self) -> None:
        binder = segment("const bindPanelStyleControls =", "bindPanelStyleControls(\"status2\"")
        self.assertIn('const borderWidth = this.shadowRoot.querySelector(', binder)
        self.assertIn('panel.border_width = normaliseStatusPanelBorderWidth(event.target.value || 1.5)', binder)
        self.assertNotIn('setConfigOverride("border_width"', binder)
        first = segment('const statusBorderWidth = this.shadowRoot.querySelector(', "const refreshCustomColourPicker")
        self.assertIn('cal.ui.status_panel.border_width = normaliseStatusPanelBorderWidth(event.target.value || 1.5)', first)
        self.assertIn("this.markCalibrationDirty()", first)

    def test_svg_renders_border_width_only_when_enabled(self) -> None:
        renderer = segment("function drawStatusPanel(", "\nfunction ")
        self.assertIn('panel.border_show ? String(panel.border_width) : "0"', renderer)
        self.assertIn('borderRect.setAttribute("stroke-width", panelStrokeWidth)', renderer)
        self.assertIn('borderRect.setAttribute("vector-effect", "non-scaling-stroke")', renderer)
        self.assertIn("strokeWidth: panelStrokeWidth", renderer)

    def test_normalization_and_per_box_runtime_are_independent(self) -> None:
        normalize = segment("function normaliseStatusPanelBorderWidth(", "\nfunction ")
        panel_ui = segment("function statusPanelUi(", "\nfunction ")
        script = (
            'const assert=require("node:assert/strict");\n'
            'const calibrationControlsEnabled=()=>true;\n'
            'const uiFromCalibration=(cal)=>cal.ui;\n'
            + normalize + "\n" + panel_ui + "\n"
            + """
const cal = {ui: {status_panel:{show:true,border_width:0.75},
                  status_panel_2:{show:true,border_width:2.25}}};
const a=statusPanelUi({},cal,1), b=statusPanelUi({},cal,2);
assert.equal(a.border_width,0.75);
assert.equal(b.border_width,2.25);
assert.equal(normaliseStatusPanelBorderWidth(undefined),1.5);
assert.equal(normaliseStatusPanelBorderWidth(""),1.5);
assert.equal(normaliseStatusPanelBorderWidth("bad"),1.5);
assert.equal(normaliseStatusPanelBorderWidth(0),0.25);
assert.equal(normaliseStatusPanelBorderWidth(4),3);
assert.equal(normaliseStatusPanelBorderWidth(1.64),1.75);
cal.ui.status_panel.border_width=undefined;
assert.equal(statusPanelUi({},cal,1).border_width,1.5);
cal.ui.status_panel_2.border_width=99;
assert.equal(statusPanelUi({},cal,2).border_width,3);
"""
        )
        proc = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)


if __name__ == "__main__":
    unittest.main()
