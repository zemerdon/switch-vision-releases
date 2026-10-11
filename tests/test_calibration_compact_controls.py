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
const sfpPortNumber = value => +(String(value).match(/\d+/g) || ["0"]).slice(-1)[0];
""" + function_source + r"""
const cal = {
  ports: {"1": {display_name:"Server"}, "2": {}},
  sfp: {"SFP1": {display_name:"Uplink"}, "SFP2": {}},
  status_leds: {STAT:[0,0], SYST:[0,0], MODE:[0,0]},
};
const groups = ["misc", "rj45", "sfp"];
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
const misc = targetOptionsHtml(cal, "status:STAT", "misc");
assert.ok(rj45.includes('value="port:2"'));
assert.ok(!rj45.includes('value="sfp:1"'));
assert.ok(sfp.includes('value="sfp:2"'));
assert.ok(!sfp.includes('value="port:1"'));
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
        self.assertNotIn('data-cv-field="target"', source)
        self.assertIn("const targetSelects = this.shadowRoot.querySelectorAll('[data-cv-target-group]');", source)
        self.assertIn("calibration_target: value, calibration_part: part", source)
        self.assertIn("this.config = nextConfig;", source)

    def test_compact_size_rules(self) -> None:
        css = CSS.read_text(encoding="utf-8")
        self.assertRegex(css, r"(?s)\.cv-cal-tools input\.cv-cal-input \{[^}]*height: 20px;[^}]*min-height: 20px;[^}]*padding: 3px;[^}]*line-height: 12px;")
        self.assertRegex(css, r"(?s)\.cv-cal-colour-controls input\.cv-cal-hex-input \{[^}]*width: 59px !important;[^}]*padding: 3px;")
        self.assertRegex(css, r"(?s)\.cv-cal-colour-controls \.cv-cal-colour-swatch \{[^}]*width: 21px;[^}]*height: 20px;[^}]*min-height: 20px;")
        self.assertRegex(css, r"(?s)\.cv-cal-tools input\.cv-cal-input\[type=\"number\"\][^{]*\{[^}]*width: 61px;")
        self.assertRegex(css, r"(?s)\.cv-cal-tools select\.cv-cal-select \{[^}]*height: 20px;[^}]*min-height: 20px;[^}]*padding: 3px 18px 3px 3px;[^}]*line-height: 12px;")
        self.assertRegex(css, r"(?s)\.cv-cal-tools button:not\(\.cv-cal-toggle\) \{[^}]*height: 20px;[^}]*min-height: 20px;[^}]*padding: 3px;[^}]*line-height: 12px;")
        self.assertIn("width: 127px;", css)
        self.assertIn("max-width: min(100%, 185px);", css)

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


if __name__ == "__main__":
    unittest.main()
