"""LED outline profile contract: off by default, opt-in style, and numeric input."""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "src/js/switch-vision.js"
MIRROR = ROOT / "src/custom_components/switch_vision/switch-vision-card.js"
CSS = ROOT / "src/css/switch-vision.css"


class LedOutlineCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js = JS.read_text(encoding="utf-8")
        cls.css = CSS.read_text(encoding="utf-8")

    def test_card_source_is_mirrored(self):
        self.assertEqual(JS.read_bytes(), MIRROR.read_bytes())

    def test_led_strokes_are_opt_in_and_cover_all_states(self):
        selector = ".cv-led-off,.cv-led-green,.cv-led-amber,.cv-led-blue,.cv-led-red,.cv-led-poe"
        self.assertIn(selector + "{stroke:var(--cv-led-outline-color,none);stroke-width:var(--cv-led-outline-width,0)}", self.css)
        self.assertIn(".cv-led-off{fill:var(--cv-off)}", self.css)
        self.assertNotIn("stroke:rgba(0,0,0,.8);stroke-width:1", self.css)
        self.assertNotIn("stroke:rgba(0,0,0,.85);stroke-width:1", self.css)

    def test_profile_defaults_and_runtime_apply_to_both_port_types(self):
        self.assertIn('led_outline: { enabled: false, color: "#000000", thickness: 1 }', self.js)
        self.assertIn("cal.ui.led_outline = normaliseLedOutlineSettings(cal.ui.led_outline)", self.js)
        self.assertIn('svg.style.setProperty("--cv-led-outline-color", outline.enabled ? outline.color : "none")', self.js)
        self.assertIn('svg.style.setProperty("--cv-led-outline-width", outline.enabled ? String(outline.thickness) : "0")', self.js)
        self.assertIn("return applyPortLedColourOverride(element, activeCalibration, part, cls)", self.js)
        self.assertIn("return portLed(", self.js)

    def test_controls_are_in_existing_port_labels_section(self):
        start = self.js.index('data-cv-section="labels-leds"')
        end = self.js.index('data-cv-section="status-boxes"', start)
        html = self.js[start:end]
        self.assertIn("LED Outlines", html)
        self.assertIn('data-cv-field="led-outline-enabled"', html)
        self.assertIn('customColourControlsHtml("led-outline-color"', html)
        self.assertIn('data-cv-field="led-outline-thickness" type="number" min="0.25" max="3" step="0.25"', html)
        self.assertIn('placeholder="0.25 – 3.00"', html)
        self.assertNotIn('data-cv-field="led-outline-thickness" type="range"', html)
        self.assertIn("this.markCalibrationDirty()", self.js)
        self.assertIn("cal.ui.led_outline.enabled = event.target.checked", self.js)
        self.assertIn("cal.ui.led_outline.thickness = normaliseLedOutlineThickness(event.target.value || 1)", self.js)
        self.assertIn('"led-outline-color": () => { cal.ui.led_outline.color = colour; }', self.js)

    def test_numeric_normalisation_and_legacy_profile_defaults(self):
        start = self.js.index("function normaliseLedOutlineThickness(")
        end = self.js.index("function defaultUiLayout()", start)
        fragment = self.js[start:end]
        probe = r"""
const normaliseHexColour = (input, fallback) => /^#[0-9a-f]{6}$/i.test(input) ? input.toLowerCase() : fallback;
""" + fragment + r"""
const assert = require("assert");
assert.deepStrictEqual(normaliseLedOutlineSettings(undefined), {enabled:false,color:"#000000",thickness:1});
assert.deepStrictEqual(normaliseLedOutlineSettings({enabled:true,color:"#a0b0c0",thickness:0.62}), {enabled:true,color:"#a0b0c0",thickness:0.5});
assert.strictEqual(normaliseLedOutlineThickness(0),0.25);
assert.strictEqual(normaliseLedOutlineThickness(3.6),3);
assert.strictEqual(normaliseLedOutlineThickness(2.61),2.5);
assert.strictEqual(normaliseLedOutlineThickness(NaN),1);
assert.strictEqual(normaliseLedOutlineSettings({enabled:"true",thickness:"bad"}).enabled,false);
"""
        run = subprocess.run(["node", "-e", probe], capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == "__main__":
    unittest.main()
