#!/usr/bin/env python3
"""Behavioural regression for the two grouped Status Box Calibration dropdowns."""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/js/switch-vision.js").read_text(encoding="utf-8")


class StatusBoxQuickDropdownTests(unittest.TestCase):
    def test_five_dropdowns_preserve_all_32_target_part_choices(self) -> None:
        self.assertEqual(SOURCE.count('data-cv-quick-group="1"'), 1)
        for i in (2, 3, 4, 5):
            self.assertEqual(SOURCE.count(f'data-cv-quick-group="{i}"'), 1)
        self.assertIn('quickSelect.addEventListener("change"', SOURCE)
        self.assertIn("this.applyCalibrationQuickTarget(cal, target, part);", SOURCE)
        self.assertNotIn('cv-cal-status-quick-actions', SOURCE)

        start = SOURCE.index("const SV_STATUS_BOX_QUICK_GROUPS = Object.freeze(")
        end = SOURCE.index("function calibrationPartOptionsHtml(", start)
        options = SOURCE[start:end]
        method_start = SOURCE.index("  applyCalibrationQuickTarget(cal, nextTarget, nextPart) {")
        method_end = SOURCE.index("  attachCalibrationControlHandlers(cal) {", method_start)
        method = SOURCE[method_start:method_end]

        harness = r"""
const assert=require("node:assert/strict");
const htmlEscape=x=>String(x).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll('"',"&quot;");
const sortedCalibrationPortKeys=cal=>Object.keys(cal.ports).sort((a,b)=>Number(a)-Number(b));
const sortedCalibrationSfpKeys=cal=>Object.keys(cal.sfp).sort();
const rearSfpOrdinal=key=>/^rSFP[1-9][0-9]*$/i.test(key)?Number(key.slice(4)):0;
const calibrationSfpKeysByParity=(cal,which)=>sortedCalibrationSfpKeys(cal)
 .filter(k=>!rearSfpOrdinal(k))
 .filter(k=>Number((k.match(/\d+/g)||["0"]).at(-1))%2===(which==="odd"?1:0));
""" + options + r"""
class Card {
 constructor() { this.config={calibration_target:"logo",calibration_part:"box"};this.renders=0; }
 render() { this.renders++; }
""" + method + r"""
}
const groups=SV_STATUS_BOX_QUICK_GROUPS;
assert.equal(groups.length,5);
for (let i=0;i<5;i++) {
 const tuples=groups[i].flatMap(([, entries])=>entries);
 const count=[4,4,8,8,8][i];
 assert.equal(tuples.length,count);
 assert.equal(new Set(tuples.map(([,t,p])=>t+"|"+p)).size,count);
 assert.equal((statusBoxQuickOptionsHtml({calibration_target:"unknown"},i+1).match(/<option/g)||[]).length,count+1);
 assert.equal((statusBoxQuickOptionsHtml({calibration_target:"unknown"},i+1).match(/<optgroup/g)||[]).length,i<2?1:2);
}
const cal={
 ports:{"1":{},"2":{},"3":{},"4":{}},
 sfp:{"SFP1":{},"SFP2":{},"SFP3":{},"SFP4":{},"rSFP1":{}}
};
const card=new Card();
card.applyCalibrationQuickTarget(cal,"status_fields","label");
assert.equal(card.config.calibration_target,"status_fields");
assert.equal(card.config.calibration_part,"label");
card.applyCalibrationQuickTarget(cal,"ports_odd_entire","entire");
assert.equal(card.config.calibration_port_selection,"1,3");
assert.equal(card.config.calibration_sfp_selection,"");
card.applyCalibrationQuickTarget(cal,"sfps_even_labels","label");
assert.equal(card.config.calibration_sfp_selection,"SFP2,SFP4");
assert.equal(card.config.calibration_port_selection,"");
assert.equal(card.config.calibration_part,"label");
assert.equal(card.renders,3);
assert.equal(statusBoxQuickOptionsHtml(card.config,4).includes('value="sfps_even_labels|label" selected'),true);
card.applyCalibrationQuickTarget(cal,"rsfps_odd_entire","entire");
assert.equal(card.config.calibration_sfp_selection,"rSFP1");
assert.equal(card.config.calibration_port_selection,"");
assert.equal(statusBoxQuickOptionsHtml(card.config,5).includes('value="rsfps_odd_entire|entire" selected'),true);
assert.equal(card.renders,4);
console.log("FIVE_DROPDOWNS_32_ACTIONS_PASS");
"""
        result = subprocess.run(
            ["node", "-e", harness], cwd=ROOT, text=True,
            capture_output=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("FIVE_DROPDOWNS_32_ACTIONS_PASS", result.stdout)

    def test_removed_hint_text_and_height_row_position(self) -> None:
        for removed in (
            "Show or hide every Status LED, or untick individual LEDs.",
            "Link and activity colours apply to every RJ45",
            "Auto by default · Custom minimum",
        ):
            self.assertNotIn(removed, SOURCE)
        asset_row = SOURCE.split('cv-cal-assets-row">', 1)[1].split("</div>", 1)[0]
        self.assertLess(asset_row.index("htmlEscape(assetStatus)"), asset_row.index("<label>Card Height"))
        self.assertLess(asset_row.index("faceplate-height-preset"), asset_row.index("faceplate-height-custom"))
        self.assertNotIn('cv-cal-faceplate-tip">', SOURCE)


if __name__ == "__main__":
    unittest.main()
