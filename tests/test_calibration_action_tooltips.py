"""Permanent Core Calibration sticky-action tooltip contract (no action rewiring)."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/js/switch-vision.js").read_text(encoding="utf-8")

EXPECTED = {
    "toggle-led-test-mode": ("Toggle LED Test Mode 1", "Does not save or change Calibration"),
    "toggle-led-test-mode-off": ("Toggle LED Test Mode 2", "Does not save or change Calibration"),
    "cancel-calibration": ("Close Calibration", "discard unsaved edits"),
    "refresh-faceplate": ("Reload the faceplate image", "without changing its selected artwork"),
    "reset-current-faceplate": ("Keep the selected faceplate artwork", "factory defaults"),
    "reset-current-switch": ("newest verified factory faceplate", "Requires confirmation"),
    "reset-all-switches": ("dashboard scope only", "Two confirmations required"),
    "save-profile": ("Save your current Calibration changes", "Home Assistant"),
}

class CalibrationActionTooltips(unittest.TestCase):
    def test_every_sticky_button_has_precise_plain_text_tooltip(self) -> None:
        markup = SOURCE[SOURCE.index('class="cv-cal-sticky-buttons"'):
                        SOURCE.index("\n        </div>", SOURCE.index('class="cv-cal-sticky-buttons"'))]
        self.assertEqual(markup.count('data-cv-action='), len(EXPECTED))
        for action, fragments in EXPECTED.items():
            match = re.search(r'<button\b[^>]*\bdata-cv-action="' + re.escape(action)
                              + r'"[^>]*>', markup, re.S)
            self.assertIsNotNone(match, action)
            tag = match.group(0)
            tooltips = re.findall(r'\btitle="([^"]+)"', tag)
            self.assertEqual(len(tooltips), 1, action)
            for fragment in fragments:
                self.assertIn(fragment, tooltips[0], action)
            self.assertNotIn("<", tooltips[0], action)
            self.assertNotIn(">", tooltips[0], action)

    def test_handlers_and_reset_confirmations_are_unchanged(self) -> None:
        for action in EXPECTED:
            self.assertIn('if (action === "' + action + '")', SOURCE)
        self.assertIn('confirmLabel: "Reset Switch", danger: true', SOURCE)
        self.assertIn('title: "Reset Current Faceplate", confirmLabel: "Reset Faceplate"', SOURCE)
        self.assertIn('title: "Final Reset Confirmation", confirmLabel: "Reset All"', SOURCE)
        self.assertIn('data-cv-action="save-profile" title=', SOURCE)
        self.assertIn(' ${dirty ? "" : "disabled"}>Save Profile', SOURCE)

if __name__ == "__main__":
    unittest.main()
