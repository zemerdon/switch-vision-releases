#!/usr/bin/env python3
"""Calibration compact-control and target-group behaviour regressions."""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/js/switch-vision.js"
CSS = ROOT / "src/css/switch-vision.css"


class CalibrationCompactControlsTest(unittest.TestCase):
    def test_target_options_are_disjoint_and_have_one_active_group(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        begin = source.index("function targetOptionsHtml(")
        end = source.index("function calibrationPartOptionsHtml(", begin)
        function_source = source[begin:end]
        runner = r"""
const assert = require("node:assert/strict");
const STATUS_PANEL_FIELD_DEFS = [["model", "MODEL"], ["ip", "IP"]];
const htmlEscape = value => String(value).replace(/&/g,"&amp;").replace(/"/g,"&quot;").replace(/</g,"&lt;");
const sortedCalibrationPortKeys = cal => Object.keys(cal.ports).sort((a,b) => +a - +b);
const sortedCalibrationSfpKeys = cal => Object.keys(cal.sfp).sort();
const rearSfpOrdinal = value => +(String(value).match(/^rSFP([1-9][0-9]*)$/i) || ["", "0"])[1];
const rearSfpOrdinalFromPort = value => +value > 1000000 ? +value - 1000000 : 0;
const sfpPortNumber = value => rearSfpOrdinal(value) ? 1000000 + rearSfpOrdinal(value) : +(String(value).match(/\d+/g) || ["0"]).slice(-1)[0];
""" + function_source + r"""
const cal = {
  ports: {"1": {display_name:"Server"}, "2": {}},
  sfp: {"SFP1": {display_name:"Uplink"}, "SFP2": {}, "rSFP1": {rear_interface:"A1"}},
  status_leds: {STAT:[0,0], SYST:[0,0], MODE:[0,0]},
};
const groups = ["misc", "rj45", "sfp", "rear_sfp"];
const cases = [
  ["logo", "misc"],
  ["status:STAT", "misc"],
  ["all_link_leds", "misc"],
  ["all_numbers", "misc"],
  ["port:1", "rj45"],
  ["ports", "rj45"],
  ["ports_custom", "rj45"],
  ["ports_odd_entire", "rj45"],
  ["sfp:1", "sfp"],
  ["sfps", "sfp"],
  ["sfps_custom", "sfp"],
  ["sfps_even_labels", "sfp"],
  ["sfp:1000001", "rear_sfp"],
  ["rear_sfps", "rear_sfp"],
];
for (const [target, active] of cases) {
  const outputs = Object.fromEntries(groups.map(g => [g, targetOptionsHtml(cal, target, g)]));
  for (const group of groups) {
    const output = outputs[group];
    const match = output.match(/<option value="([^"]+)" selected>/g) || [];
    assert.equal(match.length, group === active ? 1 : 0, target + " " + group);
    assert.equal(output.includes('value="' + target + '"'), group === active, target + " " + group);
    assert.equal(output.includes('value="" disabled selected'), group !== active, target + " " + group);
  }
}
const rj45 = targetOptionsHtml(cal, "port:1", "rj45");
const sfp = targetOptionsHtml(cal, "sfp:1", "sfp");
const rear = targetOptionsHtml(cal, "sfp:1000001", "rear_sfp");
const misc = targetOptionsHtml(cal, "status:STAT", "misc");
assert.ok(rj45.includes('value="port:2"'));
assert.ok(!rj45.includes('value="sfp:1"'));
assert.ok(sfp.includes('value="sfp:2"'));
assert.ok(!sfp.includes('value="port:1"'));
assert.ok(!sfp.includes('value="sfp:1000001"'));
assert.ok(rear.includes('>rSFP1</option>'));
assert.ok(!rear.includes("→ A1"));
assert.ok(!rear.includes('value="sfp:1"'));
assert.ok(misc.includes('value="status:SYST"'));
assert.ok(!misc.includes('value="status:MODE"'));
console.log("Calibration grouped targets: PASS");
"""
        result = subprocess.run(["node", "-e", runner], capture_output=True, text=True, cwd=ROOT, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

    def test_target_controls_reuse_existing_selection_state(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(source.count('data-cv-target-group="misc"'), 1)
        self.assertEqual(source.count('data-cv-target-group="rj45"'), 1)
        self.assertEqual(source.count('data-cv-target-group="sfp"'), 1)
        self.assertEqual(source.count('data-cv-target-group="rear_sfp"'), 1)
        self.assertNotIn('data-cv-field="target"', source)
        self.assertIn("const targetSelects = this.shadowRoot.querySelectorAll('[data-cv-target-group]');", source)
        self.assertIn("calibration_target: value, calibration_part: part", source)
        self.assertIn("this.config = nextConfig;", source)

    def test_port_manager_controls_follow_card_height_before_target_selectors(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        card_height = source.index('data-cv-field="faceplate-height-preset"')
        manager = source.index('cv-cal-port-manager-row cv-cal-port-manager-actions', card_height)
        targets = source.index('cv-cal-port-targets-row cv-cal-port-manager-main', card_height)
        metadata = source.index('cv-cal-port-meta-row', targets)
        quick = source.index('cv-cal-subsection-divider', metadata)
        self.assertTrue(card_height < manager < targets < metadata < quick)
        manager_block = source[manager:targets]
        for action in ("add-port", "add-sfp", "duplicate-port", "remove-port",
                       "remove-all-rj45", "remove-all-sfp"):
            self.assertIn('data-cv-action="' + action + '"', manager_block)
        self.assertNotIn('data-cv-field="port-number"', manager_block)

    def test_rear_selector_adjacent_to_front_sfp_and_wraps_with_auto_width(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")
        block = source.split('<div class="cv-cal-tools-row cv-cal-port-targets-row cv-cal-port-manager-main">', 1)[1].split('</div>', 1)[0]
        self.assertLess(block.index('data-cv-target-group="misc"'), block.index('data-cv-target-group="rj45"'))
        self.assertLess(block.index('data-cv-target-group="rj45"'), block.index('data-cv-target-group="sfp"'))
        self.assertLess(block.index('data-cv-target-group="sfp"'), block.index('data-cv-target-group="rear_sfp"'))
        self.assertLess(block.index('data-cv-target-group="rear_sfp"'), block.index('data-cv-field="part"'))
        self.assertIn('data-cv-field="rear-part"', block)
        self.assertEqual(source.count('data-cv-target-group="rear_sfp"'), 1)
        actions = source.split('<div class="cv-cal-tools-row cv-cal-rear-sfp-actions-row">', 1)[1].split('</div>', 1)[0]
        self.assertIn('data-cv-action="add-rear-sfp"', actions)
        self.assertIn('data-cv-action="remove-all-rear-sfp"', actions)
        self.assertNotIn('.cv-cal-port-manager-main,', css)
        self.assertIn('flex-wrap:wrap;', css)

    def test_port_label_show_and_led_shape_labels_stay_compact(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        css = CSS.read_text(encoding="utf-8")
        block = source.split('const selectedPortLedControls = selectedPortCount ? `', 1)[1].split('` : "";', 1)[0]
        for text, field in (("Link LED Shape", "link-led-shape"), ("Activity LED Shape", "activity-led-shape")):
            self.assertIn(f'>{text}', block)
            self.assertIn(f'data-cv-field="{field}"', block)
        self.assertIn('.cv-cal-port-presentation-row > .cv-cal-quick-label', css)
        self.assertIn('.cv-cal-port-presentation-row > .cv-cal-led-shape-label', css)
        self.assertIn('white-space: nowrap;', css)

    def test_compact_size_rules(self) -> None:
        css = CSS.read_text(encoding="utf-8")
        control = css.split(".cv-cal-tools input.cv-cal-input,", 1)[1].split("}", 1)[0]
        for token in ("height: 16px;", "min-height: 16px;", "padding: 1px 2px;", "line-height: 12px;", "font-size: 12px;"):
            self.assertIn(token, control)
        dropdown = css.split(".cv-cal-tools select.cv-cal-select {", 1)[1].split("}", 1)[0]
        for token in ("appearance: none;", "height: 16px;", "min-height: 16px;", "max-height: 16px;", "padding: 1px 18px 1px 2px;", "font-size: 12px;", "background-image:"):
            self.assertIn(token, dropdown)
        button = css.split(".cv-cal-tools button:not(.cv-cal-toggle) {", 1)[1].split("}", 1)[0]
        for token in ("height: 16px;", "padding: 1px 2px;", "font-size: 12px;"):
            self.assertIn(token, button)
        self.assertIn("width: 59px !important;", css)
        self.assertIn("width: 21px;", css)
        self.assertIn("width: 127px;", css)
        self.assertIn(".cv-cal-tools .cv-cal-target-select-shell > button.cv-cal-select-trigger {", css)
        self.assertNotIn("max-width: min(100%, 185px);", css)
        self.assertIn("padding-right: max(24px, var(--cv-cal-select-arrow-gutter, 24px)) !important;", css)

    def test_quick_links_remain_unchanged(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for marker in (
            '<span class="cv-cal-quick-label">Quick select</span>',
            'data-target="ports" data-part="entire">All RJ45</button>',
            'data-target="sfps" data-part="entire">All SFP</button>',
            'data-target="ports_odd_entire" data-part="entire">Ports</button>',
            'data-target="sfps_even_labels" data-part="label">Labels</button>',
            'data-cv-action="select-custom-ports"',
        ):
            self.assertIn(marker, source)


    def test_white_select_and_button_text_uses_regular_weight(self) -> None:
        css = CSS.read_text(encoding="utf-8")
        selector = ".cv-cal-tools select.cv-cal-select,\n.cv-cal-tools button:not(.cv-cal-toggle):not(.cv-cal-bold-toggle):not(.cv-cal-warning):not(.cv-cal-danger):not(.cv-cal-purple) {"
        self.assertIn(selector, css)
        rule = css.split(selector, 1)[1].split("}", 1)[0]
        self.assertIn("font-size: 11px;", rule)
        self.assertIn("font-weight: 400;", rule)
        self.assertIn("line-height: 12px;", css)
        self.assertIn("height: 16px;", css)
        # The heavy control base remains, but is overridden only for the white controls.
        self.assertIn("font-weight:800;", css)
        self.assertIn(".cv-cal-tools button.cv-cal-bold-toggle.is-active", css)


if __name__ == "__main__":
    unittest.main()
