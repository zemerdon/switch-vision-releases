import re
import unittest
from pathlib import Path


class CiscoTelemetryBindingRegression(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.source = (root / "src/js/switch-vision.js").read_text(encoding="utf-8")

    def test_cisco_envmon_state_mapping_is_explicit(self):
        for marker in (
            '1: "NORMAL"',
            '2: "WARNING"',
            '3: "CRITICAL"',
            '4: "SHUTDOWN"',
            '5: "NOT PRESENT"',
            '6: "NOT FUNCTIONING"',
        ):
            self.assertIn(marker, self.source)

    def test_indexed_fan_and_psu_states_are_aggregated_without_synthesizing_health(self):
        self.assertIn('summarizeIndexedTelemetryStates(hass, m, "fan") || "—"', self.source)
        self.assertIn('summarizeIndexedTelemetryStates(hass, m, "psu") || "—"', self.source)
        self.assertIn('if (!states.length) return null;', self.source)
        self.assertIn('if (counts.size === 1) return `${states.length}/${states.length} ${states[0]}`;', self.source)

    def test_generic_snmp_port_poe_entities_are_bound(self):
        for marker in (
            'configuredEntity(config, internalPort, "poe_status_code")',
            '`sensor.${member}_port_${n}_poe_status_code`',
            'configuredEntity(config, internalPort, "poe_power")',
            '`sensor.${member}_port_${n}_poe_power`',
            'configuredEntity(config, internalPort, "poe_class_code")',
            '`sensor.${member}_port_${n}_poe_class_code`',
            'poe: poeStatus',
            'poePower: poePortPowerLabel(poePowerCandidate)',
            'poeClass: poePortClassLabel(poeClassCandidate, poeStatus)',
        ):
            self.assertIn(marker, self.source)

    def test_rfc3621_poe_state_and_class_mapping(self):
        self.assertRegex(self.source, r'1: "DISABLED".*2: "SEARCHING".*3: "ACTIVE".*4: "FAULT".*5: "TEST".*6: "OTHER FAULT"')
        self.assertIn('if (status !== "ACTIVE") return "—";', self.source)
        self.assertIn('return `CLASS ${numeric - 1}`;', self.source)

    def test_missing_generic_poe_rows_are_filtered_from_status_panel(self):
        self.assertIn('if (values.poe === "—") fields = fields.filter((field) => field !== "poe");', self.source)
        self.assertIn('if (values.poe_power === "—") fields = fields.filter((field) => field !== "poe_power");', self.source)
        self.assertIn('if (values.poe_class === "—") fields = fields.filter((field) => field !== "poe_class");', self.source)


if __name__ == "__main__":
    unittest.main()
