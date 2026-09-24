from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
MIRROR = ROOT / "src" / "js" / "switch-vision.js"


class PortLabelStyleModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = CARD.read_text(encoding="utf-8")

    def test_card_sources_remain_exact_mirrors(self) -> None:
        self.assertEqual(CARD.read_bytes(), MIRROR.read_bytes())

    def test_calibration_defaults_to_static_port_label_style(self) -> None:
        self.assertIn('port_number_mode: "static"', self.source)
        self.assertIn(
            'cal.ui.port_number_mode = normalisePortNumberMode(cal.ui.port_number_mode || defaults.port_number_mode || "static");',
            self.source,
        )
        self.assertIn('function normalisePortNumberMode(value)', self.source)
        self.assertIn('["activity", "link_speed"].includes(mode) ? mode : "static"', self.source)

    def test_port_label_style_control_precedes_port_label_visibility(self) -> None:
        block_start = self.source.index('const numberLabelVisibilityControls = numberLabelCount ?')
        block_end = self.source.index('const isPortLedSize', block_start)
        block = self.source[block_start:block_end]
        style_at = block.index('Port Label Style')
        label_at = block.index('cv-cal-quick-label">Port Label')
        show_at = block.index('data-cv-action="show-number-label"')
        hide_at = block.index('data-cv-action="hide-number-label"')
        self.assertLess(style_at, label_at)
        self.assertLess(label_at, show_at)
        self.assertLess(show_at, hide_at)
        self.assertIn('value="static"', block)
        self.assertIn('value="activity"', block)
        self.assertIn('value="link_speed"', block)
        self.assertNotIn('SFP label"', block)
        self.assertNotIn('Port number"', block)

    def test_user_facing_port_label_wording_is_port_type_agnostic(self) -> None:
        required = (
            'option("all_numbers", "Port Labels")',
            'option("ports_numbers", "All RJ45 Port Labels")',
            'option("number", "All Port Labels")',
            'option("number", "Port Label")',
            'data-target="all_numbers" data-part="number">Port Labels</button>',
        )
        for marker in required:
            self.assertIn(marker, self.source)
        self.assertNotIn('>Port Numbers</button>', self.source)
        self.assertNotIn('"Port number")', self.source)
        self.assertIn('option("label", type === "sfps" ? "All Port Labels" : "Port Label")', self.source)
        self.assertNotIn('"SFP label"', self.source)

    def test_rj45_and_sfp_labels_share_activity_and_link_speed_modes(self) -> None:
        required = (
            'portNumberText.dataset.cvActivityPortNumber = String(n);',
            'sfpLabelText.dataset.cvActivitySfpLabel = String(sfpPort);',
            'updatePortNumberVisualState(portNumberText, calibration, portNumberMode, activityCls, portUi);',
            'updatePortNumberVisualState(portNumberText, calibration, portNumberMode, linkCls, portUi);',
            'updatePortNumberVisualState(sfpLabelText, calibration, portNumberMode, activityCls, portUi, staticSfpColour);',
            'updatePortNumberVisualState(sfpLabelText, calibration, portNumberMode, linkCls, portUi, staticSfpColour);',
        )
        for marker in required:
            self.assertIn(marker, self.source)

    def test_retained_activity_refresh_uses_cached_visible_targets_and_evaluates_each_port_once(self) -> None:
        cache_start = self.source.index('  cacheActivityAnimationTargets() {')
        refresh_start = self.source.index('  refreshActivityLeds() {', cache_start)
        cache_block = self.source[cache_start:refresh_start]
        refresh_end = self.source.index('\n  stopActivityAnimation() {', refresh_start)
        refresh_block = self.source[refresh_start:refresh_end]

        for marker in (
            'this.shadowRoot.querySelectorAll("[data-cv-activity-port]")',
            'this.shadowRoot.querySelectorAll("[data-cv-activity-port-number]")',
            'this.shadowRoot.querySelectorAll("[data-cv-activity-sfp]")',
            'this.shadowRoot.querySelectorAll("[data-cv-activity-sfp-label]")',
            'this._activityAnimationTargets = {',
        ):
            self.assertIn(marker, cache_block)

        self.assertIn('const cachedTargets = this._activityAnimationTargets;', refresh_block)
        self.assertIn('for (const [port, targets] of cachedTargets.ports.entries())', refresh_block)
        self.assertIn('for (const [port, targets] of cachedTargets.sfp.entries())', refresh_block)
        self.assertNotIn('querySelectorAll(', refresh_block)
        self.assertEqual(refresh_block.count('testPortActivity(this._hass, this.config, port)'), 1)
        self.assertEqual(refresh_block.count('testSfpActivity(this._hass, this.config, port)'), 1)
        self.assertIn('for (const element of targets.leds)', refresh_block)
        self.assertIn('for (const element of targets.labels)', refresh_block)

        redraw_start = self.source.index('  redrawSwitchSvg(activeCalibration = null) {')
        redraw_end = self.source.index('\n  render() {', redraw_start)
        self.assertIn('this.cacheActivityAnimationTargets();', self.source[redraw_start:redraw_end])

        schedule_start = self.source.index('  scheduleActivityAnimationIfNeeded() {')
        schedule_end = self.source.index('\n  set hass(hass) {', schedule_start)
        schedule_block = self.source[schedule_start:schedule_end]
        self.assertEqual(schedule_block.count('!this.hasActivityAnimationTargets()'), 2)


    def test_style_helpers_execute_expected_static_activity_and_link_speed_colours(self) -> None:
        source = self.source

        def extract(signature: str) -> str:
            start = source.index(signature)
            brace = source.index("{", start)
            depth = 0
            quote = None
            escape = False
            for pos in range(brace, len(source)):
                char = source[pos]
                if quote is not None:
                    if escape:
                        escape = False
                    elif char == "\\":
                        escape = True
                    elif char == quote:
                        quote = None
                    continue
                if char in {"'", '"', "`"}:
                    quote = char
                    continue
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        return source[start : pos + 1]
            raise AssertionError(f"unterminated function: {signature}")

        helpers = "\n".join(
            [
                extract("function normalisePortNumberMode(value)"),
                extract("function portNumberIndicatorColour(activeCalibration, part, cls, uiOverride = null)"),
                extract("function updatePortNumberVisualState(element, activeCalibration, mode, cls, uiOverride = null, staticColour = null)"),
            ]
        )
        harness = f"""
function normaliseHexColour(value, fallback = "#eef7ff") {{
  const text = String(value || "").trim();
  return /^#[0-9a-f]{{6}}$/i.test(text) ? text.toLowerCase() : String(fallback).toLowerCase();
}}
function uiFromCalibration(value) {{ return value?.ui || {{}}; }}
function portLedColourOverride(activeCalibration, part, uiOverride = null) {{
  const ui = uiOverride || uiFromCalibration(activeCalibration);
  const field = part === "led_left" ? "link_led_color" : (part === "led_right" ? "activity_led_color" : "");
  const value = field ? String(ui?.[field] || "").trim() : "";
  return /^#[0-9a-f]{{6}}$/i.test(value) ? value.toLowerCase() : "";
}}
{helpers}
function fakeElement() {{
  return {{
    style: {{
      fill: "",
      filter: "",
      removeProperty(name) {{
        if (name === "filter") this.filter = "";
        if (name === "fill") this.fill = "";
      }}
    }}
  }};
}}
const ui = {{
  port_number_color: "#eeeeee",
  port_label_color: "#dddddd",
  activity_led_color: "",
  link_led_color: ""
}};
let el = fakeElement();
updatePortNumberVisualState(el, {{ui}}, "static", "", ui, "#eeeeee");
if (el.style.fill !== "#eeeeee" || el.style.filter !== "") throw new Error("static mode mismatch");
el = fakeElement();
updatePortNumberVisualState(el, {{ui}}, "activity", "cv-led-off", ui, "#eeeeee");
if (el.style.fill !== "#eeeeee" || el.style.filter !== "") throw new Error("activity off mismatch");
el = fakeElement();
updatePortNumberVisualState(el, {{ui}}, "activity", "cv-led-amber", ui, "#eeeeee");
if (el.style.fill !== "#ffb321" || !el.style.filter.includes("#ffb321")) throw new Error("activity on mismatch");
el = fakeElement();
updatePortNumberVisualState(el, {{ui}}, "link_speed", "cv-led-blue", ui, "#eeeeee");
if (el.style.fill !== "#29a8ff" || !el.style.filter.includes("#29a8ff")) throw new Error("link speed mismatch");
const custom = {{...ui, link_led_color: "#123456"}};
el = fakeElement();
updatePortNumberVisualState(el, {{ui: custom}}, "link_speed", "cv-led-blue", custom, "#eeeeee");
if (el.style.fill !== "#123456") throw new Error("custom link colour override mismatch");
"""
        result = subprocess.run(
            ["node", "-e", harness],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_style_change_is_persisted_in_calibration_ui(self) -> None:
        marker = 'const portNumberModeSelect = this.shadowRoot.querySelector(\'[data-cv-field="port-number-mode"]\');'
        self.assertIn(marker, self.source)
        self.assertIn(
            'cal.ui.port_number_mode = normalisePortNumberMode(event.target.value);',
            self.source,
        )
        self.assertIn('this.markCalibrationDirty();', self.source)


if __name__ == "__main__":
    unittest.main()
