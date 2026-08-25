import re
import unittest
from pathlib import Path


class StatusPanelMissingTelemetryRegression(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.source = (root / "src/js/switch-vision.js").read_text(encoding="utf-8")

    def _fallback_for(self, variable: str) -> str:
        pattern = re.compile(
            rf'const {re.escape(variable)} = firstEntityValue\(hass, \[(.*?)\]\)\s*\|\|\s*"([^"]+)";',
            re.S,
        )
        match = pattern.search(self.source)
        self.assertIsNotNone(match, f"{variable} status-panel assignment missing")
        return match.group(2)

    def test_missing_fan_and_psu_telemetry_is_not_synthesized_as_healthy(self):
        self.assertEqual(self._fallback_for("fans"), "—")
        self.assertEqual(self._fallback_for("psu"), "—")

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
