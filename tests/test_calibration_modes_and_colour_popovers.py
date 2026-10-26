#!/usr/bin/env python3
"""Calibration LED preview and Status Box colour pop-up regressions."""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "src/js/switch-vision.js").read_text(encoding="utf-8")
CSS = (ROOT / "src/css/switch-vision.css").read_text(encoding="utf-8")


def segment(start: str, end: str) -> str:
    return JS[JS.index(start):JS.index(end, JS.index(start))]


class CalibrationModesAndColourPopovers(unittest.TestCase):
    def test_sticky_button_order_colours_and_actions(self) -> None:
        toolbar = segment('class="cv-cal-sticky-buttons"', "\n        </div>")
        actions = re.findall(r'data-cv-action="([^"]+)"', toolbar)
        self.assertEqual(actions, [
            "cancel-calibration", "toggle-led-test-mode",
            "toggle-led-test-mode-off", "refresh-faceplate",
            "reset-current-faceplate", "reset-current-switch",
            "reset-all-switches", "save-profile",
        ])
        expected = {
            "cancel-calibration": "cv-cal-danger",
            "toggle-led-test-mode": "cv-cal-warning",
            "toggle-led-test-mode-off": "cv-cal-orange-alt",
            "refresh-faceplate": "cv-cal-success",
            "reset-current-faceplate": "cv-cal-danger",
            "reset-current-switch": "cv-cal-pink",
            "reset-all-switches": "cv-cal-danger",
            "save-profile": "cv-cal-primary",
        }
        for action, colour_class in expected.items():
            self.assertRegex(
                toolbar,
                r'class="' + re.escape(colour_class) +
                r'"[^>]*data-cv-action="' + re.escape(action) + r'"',
            )
            self.assertIn(".cv-cal-tools button." + colour_class, CSS)
            self.assertIn(":not(." + colour_class + ")", CSS)
        self.assertIn('calibration_test_mode: calibrationTestModeValue(this.config) === "on" ? false : "on"', JS)
        self.assertIn('calibration_test_mode: calibrationTestModeValue(this.config) === "off" ? false : "off"', JS)

    def test_status_box_picker_escapes_horizontal_scroll_clip(self) -> None:
        self.assertIn(".cv-cal-status-combined-row{", CSS)
        self.assertIn("overflow-x:auto;", CSS)
        self.assertIn(".cv-cal-colour-popover.cv-cal-colour-popover-viewport{position:fixed;", CSS)
        self.assertIn('if (opening && control.closest(".cv-cal-status-combined-row"))', JS)
        self.assertIn("positionCalibrationColourPopover(popover, event.currentTarget);", JS)
        helper = segment("function positionCalibrationColourPopover(", "\nfunction normaliseLedOutlineThickness")
        script = helper + r"""
const assert = require("node:assert/strict");
const panel = {
  classList: {add(name){this.name=name}},
  getBoundingClientRect(){return {width:224,height:220}},
  style:{}
};
const anchor = {getBoundingClientRect(){return {left:330,top:300,bottom:324}}};
positionCalibrationColourPopover(panel,anchor);
assert.equal(panel.classList.name,"cv-cal-colour-popover-viewport");
assert.equal(panel.style.left,"128px");
assert.equal(panel.style.top,"74px");
const anchorTop = {getBoundingClientRect(){return {left:24,top:20,bottom:44}}};
positionCalibrationColourPopover(panel,anchorTop);
assert.equal(panel.style.left,"24px");
"""
        script = "const window={innerWidth:360,innerHeight:420};\n" + script
        proc = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)

    def test_status_box_factory_colour_resets_keep_alpha(self) -> None:
        self.assertIn(
            'const colour = calibrationControlColourValue(field, value, factoryDefaults[field] || "#ffffff");',
            JS,
        )
        self.assertIn('style="background:${previewColour}"', JS)
        helpers = segment("function normaliseHexColour(", "\nfunction hexToHsvColour")
        script = helpers + r"""
const assert = require("node:assert/strict");
assert.equal(calibrationControlColourValue("status-box-color","transparent"),"transparent");
assert.equal(calibrationControlColourValue("status2-box-color","transparent"),"transparent");
assert.equal(calibrationControlColourValue("status-border-color","rgba(245,248,250,.75)"),"rgba(245,248,250,.75)");
assert.equal(calibrationControlColourValue("status2-border-color","rgba(245,248,250,.75)"),"rgba(245,248,250,.75)");
assert.equal(calibrationControlColourValue("status-box-color","#aBcDeF"),"#abcdef");
assert.equal(calibrationControlColourValue("port-number-color","transparent"),"#ffffff");
"""
        proc = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=15)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)

    def test_all_visible_leds_force_off_and_live_mode_returns(self) -> None:
        functions = [
            segment("function optionalPortLedClass(", "\nfunction portLedColourOverride"),
            segment("function speedClass(", "\nfunction activityClass"),
            segment("function activityClass(", "\nfunction calibrationTestStatusLedClass"),
            segment("function calibrationTestStatusLedClass(", "\nfunction statusLedClass"),
            segment("function statusLedClass(", "\nconst portActivityState"),
            segment("function calibrationTestModeValue(", "\nfunction calibrationTestModeEnabled"),
            segment("function calibrationTestModeEnabled(", "\nasync function copyTextToClipboard"),
            segment("function drawPanel(", "\nfunction calibrationRenderSpaceData"),
        ]
        harness = r"""
const assert = require("node:assert/strict");
let observed=[];
const SV_OPTIONAL_PORT_LED_PARTS=["led_poe"];
const circle=(svg,x,y,r,cls)=>observed.push(cls);
const portLed=(svg,x,y,r,cls)=>{observed.push(cls);return {dataset:{}};};
const sfpLed=(svg,sfp,part,cls)=>{observed.push(cls);return {dataset:{}};};
const image=()=>{}, text=()=>{}, drawStatusPanel=()=>{};
const uiFromCalibration=()=>({port_number_mode:"static",show_activity_leds:true});
const switchPoeActive=()=>true, configuredStackProfile=()=>({enabled:true});
const statusLedIsHidden=()=>false, calibrationEnabled=()=>false;
const configuredPortCountAllows=()=>true, portIsUp=()=>true;
const portSpeed=()=>1000, normalisePortNumberMode=(v)=>v;
const testPortActivity=()=>true, testSfpActivity=()=>true;
const portLedShapeForItem=()=>"circle",portLedSizeKey=()=>"led_poe_size";
const optionalPortLedPoint=()=>[3,3];
const hasUnifiBinding=()=>false,snmpPortPoeActive=()=>true;
const sfpPortNumber=()=>1,rearSfpOrdinalFromPort=()=>true;
const n4032VisualSfpPosition=()=>false,sfpIsUp=()=>true,sfpSpeedMbps=()=>10000;
const layout={
  status:{radius:2,mode_radius:2,labels:{}},
  ports:{r:2},sfp:{labels:{}}
};
const calibration={
  status_leds:{STAT:[1,1],PoE:[2,2],STACK:[3,3]},
  ports:{"1":{led_left:[1,1],led_right:[2,2],led_poe:[3,3],led_poe_show:true}},
  sfp:{SFP1:{center:[4,4],led_left:[5,5],led_right:[6,6],label_show:false}}
};
function render(mode) {
  observed=[];
  const config={show_labels:false,show_status_leds:true,show_port_leds:true,
    show_numbers:false,show_status_panel:false,port_count:1,sfp_port_count:1,
    demo:true,calibration_test_mode:mode};
  drawPanel({}, {hass:{},config,calibration,layout});
  return [...observed];
}
assert.equal(calibrationTestModeValue({calibration_test_mode:true}),"on");
assert.equal(calibrationTestModeValue({calibration_test_mode:"on"}),"on");
assert.equal(calibrationTestModeValue({calibration_test_mode:"off"}),"off");
assert.equal(calibrationTestModeValue({calibration_test_mode:false}),"");
assert.equal(calibrationTestModeEnabled({calibration_test_mode:"off"}),true);
const off=render("off");
assert.ok(off.length>=8,off.length);
assert.ok(off.every((cls)=>cls==="cv-led-off"),off.join(","));
assert.equal(optionalPortLedClass({}, {}, 1, "led_poe", "off"),"cv-led-off");
const on=render("on");
assert.equal(on.length,off.length);
assert.ok(on.includes("cv-led-blue"));
assert.ok(on.includes("cv-led-poe"));
assert.ok(on.includes("cv-led-amber"));
assert.ok(on.includes("cv-led-green"));
const live=render(false);
assert.equal(live.length,on.length);
assert.ok(live.some((cls)=>cls!=="cv-led-off"));
"""
        proc = subprocess.run(
            ["node", "-e", "\n".join(functions) + "\n" + harness],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)


if __name__ == "__main__":
    unittest.main()
