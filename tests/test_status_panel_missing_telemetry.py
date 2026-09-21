import re
import unittest
from pathlib import Path


class StatusPanelMissingTelemetryRegression(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.source = (root / "src/js/switch-vision.js").read_text(encoding="utf-8")

    def test_missing_fan_and_psu_telemetry_is_not_synthesized_as_healthy(self):
        self.assertIn('summarizeIndexedTelemetryStates(hass, m, "fan") || "—"', self.source)
        self.assertIn('summarizeIndexedTelemetryStates(hass, m, "psu") || "—"', self.source)
        self.assertIn('if (!states.length) return null;', self.source)
        fan_assignment = re.search(r'const fans = firstEntityValue\\(hass, \\[.*?\\]\\) \\|\\| summarizeIndexedTelemetryStates\\(hass, m, "fan"\\) \\|\\| "—";', self.source, re.S)
        psu_assignment = re.search(r'const psu = firstEntityValue\\(hass, \\[.*?\\]\\) \\|\\| summarizeIndexedTelemetryStates\\(hass, m, "psu"\\) \\|\\| "—";', self.source, re.S)
        self.assertIsNotNone(fan_assignment)
        self.assertIsNotNone(psu_assignment)

    def test_real_fan_and_psu_entity_candidates_are_preserved(self):
        for token in (
            'switchConfiguredEntity(config, "fans")',
            '`sensor.${m}_fan_status`',
            'switchConfiguredEntity(config, "psu")',
            '`sensor.${m}_psu_status`',
        ):
            self.assertIn(token, self.source)


if __name__ == "__main__":
    unittest.main()
