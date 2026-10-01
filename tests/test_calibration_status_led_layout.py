from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
MIRROR = ROOT / "src" / "js" / "switch-vision.js"
CALIBRATION = ROOT / "src" / "calibration"


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

    def test_missing_status_led_visibility_defaults_to_hide_all(self) -> None:
        for marker in (
            'statusLedVisibilityExplicit = Array.isArray(cal.ui?.status_leds?.hidden);',
            'statusLedVisibilityExplicit ? explicitStatusLedHidden : Object.keys(cal.status_leds || {})',
            'status_leds: { hidden: ["STAT", "SYST", "DUPLX", "ACTV", "SPEED", "STACK", "PoE"]',
        ):
            self.assertIn(marker, self.source)

    def test_factory_profiles_never_explicitly_default_status_leds_visible(self) -> None:
        checked = 0
        for path in sorted(CALIBRATION.glob("*.json")):
            try:
                profile = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            status = profile.get("status_leds")
            if not isinstance(status, dict) or not status:
                continue
            ui = profile.get("ui")
            if not isinstance(ui, dict):
                continue
            status_ui = ui.get("status_leds")
            if not isinstance(status_ui, dict) or "hidden" not in status_ui:
                continue
            hidden = {str(value).upper() for value in status_ui["hidden"]}
            expected = {str(name).upper() for name in status}
            self.assertTrue(
                expected.issubset(hidden),
                f"{path.name} explicitly defaults one or more Status LEDs visible",
            )
            checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
