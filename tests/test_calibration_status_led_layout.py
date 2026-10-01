from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
MIRROR = ROOT / "src" / "js" / "switch-vision.js"
CALIBRATION = ROOT / "src" / "calibration"

FACTORY_PROFILES_REVERTED_FROM_2737 = (
    "faceplate-c3560cg-8pc-s.json",
    "faceplate-stock-24rj45-2sfp.json",
    "faceplate-stock-24rj45-4sfp.json",
    "faceplate-stock-48rj45-2sfp.json",
    "faceplate-stock-48rj45-4sfp.json",
    "faceplate-submarine-48rj45-4sfp.json",
)


class CalibrationStatusLedLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = CARD.read_text(encoding="utf-8")

    def test_card_sources_remain_exact_mirrors(self) -> None:
        self.assertEqual(CARD.read_bytes(), MIRROR.read_bytes())

    def test_labels_leds_order_is_status_then_port_leds_then_compact_presentation(self) -> None:
        start = self.source.index('data-cv-section="labels-leds"')
        end = self.source.index('data-cv-section="status-boxes"', start)
        section = self.source[start:end]

        self.assertLess(
            section.index('cv-cal-status-led-visibility'),
            section.index('cv-cal-port-led-shape'),
        )
        self.assertLess(
            section.index('cv-cal-port-led-shape'),
            section.index('${portPresentationControls}'),
        )
        self.assertLess(
            section.index('${portPresentationControls}'),
            section.index('cv-cal-port-label-style'),
        )

    def test_port_label_and_led_shape_controls_share_one_responsive_row(self) -> None:
        block_start = self.source.index('const selectedPortLedControls')
        block_end = self.source.index('const isPortLedSize', block_start)
        block = self.source[block_start:block_end]

        self.assertIn(
            'const portPresentationControls = \x60<div class="cv-cal-tools-row cv-cal-style-row cv-cal-port-presentation-row">',
            block,
        )
        for marker in (
            'Port Label Style',
            'data-cv-action="show-number-label"',
            'data-cv-action="hide-number-label"',
            '>Link LED</span>',
            'data-cv-field="link-led-shape"',
            '>Activity LED</span>',
            'data-cv-field="activity-led-shape"',
        ):
            self.assertIn(marker, block)

        self.assertNotIn(
            'const selectedPortLedControls = selectedPortCount ? \x60<div class="cv-cal-tools-row',
            block,
        )
        self.assertNotIn(
            'const selectedNumberLabelVisibilityControls = numberLabelCount ? \x60<div class="cv-cal-tools-row',
            block,
        )

    def test_factory_and_generic_defaults_do_not_hide_status_leds(self) -> None:
        self.assertIn(
            'status_leds: { hidden: [], text_color: "#eef7ff"',
            self.source,
        )
        self.assertNotIn(
            'statusLedVisibilityExplicit = Array.isArray(cal.ui?.status_leds?.hidden);',
            self.source,
        )
        self.assertIn(
            'cal.ui.status_leds.hidden = [...new Set((Array.isArray(cal.ui.status_leds.hidden) ? cal.ui.status_leds.hidden : []).map((name) => String(name)))];',
            self.source,
        )

        for name in FACTORY_PROFILES_REVERTED_FROM_2737:
            profile = json.loads((CALIBRATION / name).read_text(encoding="utf-8"))
            self.assertEqual(
                profile["ui"]["status_leds"]["hidden"],
                [],
                f"{name} must retain its factory Status LED presentation",
            )

    def test_new_calibration_session_starts_status_led_checkboxes_unticked(self) -> None:
        helper_start = self.source.index("function applyNewCalibrationStatusLedDefaults")
        helper_end = self.source.index("let activeCalibrationUiRenderPass", helper_start)
        helper = self.source[helper_start:helper_end]
        self.assertIn(
            "next.ui.status_leds.hidden = Object.keys(next.status_leds || {})",
            helper,
        )
        self.assertIn(
            '.filter((name) => String(name).toUpperCase() !== "MODE");',
            helper,
        )

        open_start = self.source.index("attachCalibrationButtonHandler()")
        open_end = self.source.index("      this.config = {", open_start)
        opening = self.source[open_start:open_end]
        self.assertIn("info.exists !== true", opening)
        self.assertIn("info.invalid !== true", opening)
        self.assertIn("!this._profileLoadError", opening)
        self.assertIn(
            "if (openingNewCalibration) applyNewCalibrationStatusLedDefaults(this._calibrationWorking);",
            opening,
        )

        checkbox_start = self.source.index("const hiddenStatusLeds = new Set")
        checkbox_end = self.source.index("const customFontValue", checkbox_start)
        checkbox = self.source[checkbox_start:checkbox_end]
        self.assertIn('hidden ? "" : "checked"', checkbox)

    def test_existing_saved_status_led_visibility_remains_authoritative(self) -> None:
        open_start = self.source.index("attachCalibrationButtonHandler()")
        open_end = self.source.index("      this.config = {", open_start)
        opening = self.source[open_start:open_end]
        self.assertIn("const openingNewCalibration = Boolean(", opening)
        self.assertIn("info.exists !== true", opening)
        self.assertNotIn(
            "applyNewCalibrationStatusLedDefaults(this._profileCalibration)",
            opening,
        )

        ensure_start = self.source.index("function ensureCalibrationUi(cal)")
        ensure_end = self.source.index("function applyNewCalibrationStatusLedDefaults", ensure_start)
        ensure = self.source[ensure_start:ensure_end]
        self.assertIn(
            "Array.isArray(cal.ui.status_leds.hidden) ? cal.ui.status_leds.hidden : []",
            ensure,
        )
        self.assertNotIn("Object.keys(cal.status_leds || {})", ensure)


if __name__ == "__main__":
    unittest.main()
