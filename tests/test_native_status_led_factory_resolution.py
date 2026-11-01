"""Executable Native fallback and actual SVG status-LED rendering regression."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "src/js/switch-vision.js"
CALIBRATION = ROOT / "src/calibration"


class NativeStatusLedFactoryTests(unittest.TestCase):
    def test_new_native_3650_uses_compact_factory_but_preserves_saved_original(self):
        source = FRONTEND.read_text(encoding="utf-8")
        start = source.index("  baseCalibrationData() {")
        end = source.index("\n  calibrationData() {", start)
        method = source[start:end]
        redraw_start = source.index('  redrawSwitchSvg(activeCalibration = null) {')
        redraw_end = source.index('\n  render() {', redraw_start)
        redraw_method = source[redraw_start:redraw_end]
        led_start = source.index("function statusLedIsHidden(")
        led_end = source.index("\nfunction drawPanel(", led_start)
        panel_start = led_end + 1
        panel_end = source.index("\nfunction calibrationRenderSpaceData(", panel_start)
        generic = json.loads((CALIBRATION / "c3650.json").read_text(encoding="utf-8"))
        compact = json.loads((CALIBRATION / "faceplate-stock-48rj45-4sfp-compact.json").read_text(encoding="utf-8"))
        original = json.loads((CALIBRATION / "faceplate-stock-48rj45-4sfp.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(compact["ui"]["status_leds"]["hidden"]),
            set(compact["status_leds"]),
        )
        self.assertEqual(original["ui"]["status_leds"]["hidden"], [])

        js = (
            'const assert = require("node:assert/strict");\n'
            + "const calibration = " + json.dumps(generic) + ";\n"
            + "const compact = " + json.dumps(compact) + ";\n"
            + "const original = " + json.dumps(original) + ";\n"
            + "const method = " + json.dumps(method) + ";\n"
            + "const redrawMethod = " + json.dumps(redraw_method) + ";\n"
            + "const renderHelper = " + json.dumps(source[led_start:led_end]) + ";\n"
            + "const renderPanel = " + json.dumps(source[panel_start:panel_end]) + ";\n"
            + """
const cloneCalibrationData = (value) => structuredClone(value);
const ensureCalibrationUi = (value) => value;
const uiFromCalibration = (value) => value.ui;
const canonicalFaceplateFilename = (value) => String(value || '').split('/').pop();
const faceplateFactoryCalibrationForFile = (value) => {
  const name = canonicalFaceplateFilename(value);
  if (name === '48rj45-4sfp-compact.png') return compact;
  if (name === '48rj45-4sfp.png') return original;
  return null;
};
const exactModelVisualRecommendation = () => ({
  faceplate: "faceplates/48rj45-4sfp-compact.png",
  profile: "default_cisco_48_port", rj45: 48, uplinks: 4
});
const factoryCalibrationForRecommendation = () => compact;
const TestCard = eval("class TestCard { " +
  "baseCalibrationProfileName() { return 'native_SW3'; } " +
  "detectedExactModel() { return 'WS-C3650-48PD-E'; } " +
  "recommendedFaceplateFilename() { return '48rj45-4sfp-compact.png'; } " +
  method + " }; TestCard");
const statusLedIsHidden = eval("(" + renderHelper + ")");
const drawPanel = eval("(" + renderPanel + ")");
const calibrationTestModeValue = () => "";
const switchPoeActive = () => true;
const configuredStackProfile = () => ({enabled:false});
const statusLedClass = (name) => "cv-led-" + name;
const drawStatusPanel = () => {};
let circles = [];
const circle = (svg,x,y,r,cls) => { circles.push(cls); };
const renderStatus = (cal, selectedFaceplate = '') => {
  const copy = structuredClone(cal);
  copy.ports = {}; copy.sfp = {};
  circles = [];
  drawPanel({}, {
    hass: {},
    config: {show_status_leds:true,show_labels:false,show_status_panel:false,
             __faceplate_filename:selectedFaceplate},
    calibration:copy,
    layout:{status:{mode_radius:3,radius:4}}
  });
  return circles.slice();
};

const fresh = new TestCard();
fresh._profileCalibration = null;
fresh._stockArtworkBase = "";
fresh._stockArtworkChoice = null;
const factory = fresh.baseCalibrationData();
assert.equal(factory.image.file, "faceplates/48rj45-4sfp-compact.png");
assert.equal(factory.profile, "stock_48rj45_4sfp_compact");
assert.deepEqual(factory.ui.status_leds.hidden, compact.ui.status_leds.hidden);
assert.deepEqual(renderStatus(factory), [], "Fresh Native compact must render no status LEDs");

// A saved original-stock profile is user-owned, even when compact is recommended.
// Neither the renderer nor the fallback may silently rewrite it.
const saved = structuredClone(original);
saved.profile = "default_cisco_48_port";
saved.base_profile_name = "native_SW1";
saved.ui.status_leds.hidden = [];
const existing = new TestCard();
existing._profileCalibration = saved;
existing._profileLoadInfo = {exists:true};
existing._stockArtworkBase = "";
const preserved = existing.baseCalibrationData();
assert.deepEqual(preserved, saved);
assert.equal(renderStatus(preserved).length, 7,
  "Saved original-stock LEDs remain visible until per-switch approval");

// REGRESSION: real Native can display the compact asset while an old saved
// source Geometry still contains original-stock LED coordinates. The displayed
// faceplate, not the stale Geometry, must control whether SVG LEDs exist.
assert.deepEqual(
  renderStatus(preserved, "48rj45-4sfp-compact.png"), [],
  "Compact background must never inherit the original stock status LED circles"
);
assert.equal(renderStatus(preserved, "48rj45-4sfp.png").length, 7,
  "Selecting original artwork still preserves original-stock status LEDs");
const oldCompactUi = structuredClone(compact);
oldCompactUi.ui.status_leds.hidden = [];
assert.deepEqual(renderStatus(oldCompactUi, "48rj45-4sfp-compact.png"), [],
  "Old empty hidden list must not resurrect compact LED circles");

// An exact verified old-artwork geometry still takes precedence on a new card.
const oldPin = new TestCard();
oldPin._profileCalibration = null;
oldPin._stockArtworkBase = "native_SW3";
oldPin._stockArtworkChoice = {filename:"48rj45-4sfp.png",geometry:original};
assert.equal(oldPin.baseCalibrationData().image.file, "faceplates/48rj45-4sfp.png");
const TestSvgCard = eval("class TestSvgCard { " + redrawMethod + " }; TestSvgCard");
const calibrationRenderSpaceData = (value) => value;
const normaliseLedOutlineSettings = () => ({enabled:false});
const layout = {status:{mode_radius:3,radius:4}};
const beginCalibrationUiRenderPass = () => null;
const endCalibrationUiRenderPass = () => {};
const rearSfpBindings = () => ({});
const syncRenderedCalibrationControlOverlayBoxes = () => {};
const drawCalibrationOverlay = () => {};
const fakeSvg = {firstChild:null,style:{setProperty(){}},removeChild(){}};
const renderedCard = new TestSvgCard();
renderedCard.shadowRoot = {getElementById:() => fakeSvg};
renderedCard.config = {show_status_leds:true};
renderedCard.calibrationData = () => saved;
renderedCard.resolvedFaceplateFilename = () => "48rj45-4sfp-compact.png";
renderedCard.trackedHassForRender = () => ({});
renderedCard.attachSelectionHandlers = () => {};
renderedCard.cacheActivityAnimationTargets = () => {};
const stale = structuredClone(saved);
stale.ports = {}; stale.sfp = {};
renderedCard.calibrationData = () => stale;
circles = [];
renderedCard.redrawSwitchSvg();
assert.deepEqual(circles, [],
  "Native redraw must suppress stale original LEDs on selected compact artwork");
console.log("NATIVE_STATUS_LED_RUNTIME_PASS fresh=0 saved_original=7 verified_pin_preserved");
"""
        )
        p = subprocess.run(
            ["node", "-e", js], text=True, capture_output=True, timeout=18,
            check=False,
        )
        self.assertEqual(p.returncode, 0, p.stdout + "\n" + p.stderr)
        self.assertIn("NATIVE_STATUS_LED_RUNTIME_PASS", p.stdout)


if __name__ == "__main__":
    unittest.main()
