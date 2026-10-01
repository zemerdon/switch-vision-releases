from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
MIRROR = ROOT / "src" / "js" / "switch-vision.js"


class PortLedShapeCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = CARD.read_text(encoding="utf-8")

    def test_card_sources_remain_exact_mirrors(self) -> None:
        self.assertEqual(CARD.read_bytes(), MIRROR.read_bytes())

    def test_supported_shapes_include_tall_up_and_down_triangles(self) -> None:
        required = (
            'const PORT_LED_SHAPES = Object.freeze(["circle", "rectangle", "triangle_up", "triangle_down"]);',
            'const width = Math.max(2, Math.round(storedWidth * 0.6 * 10) / 10);',
            'const height = Math.max(2, Math.round(storedHeight * 1.25 * 10) / 10);',
            'shape === "triangle_down"',
            '[[x - halfWidth, y - halfHeight], [x + halfWidth, y - halfHeight], [x, y + halfHeight]]',
            '[[x, y - halfHeight], [x + halfWidth, y + halfHeight], [x - halfWidth, y + halfHeight]]',
        )
        for marker in required:
            self.assertIn(marker, self.source)

    def test_link_and_activity_shapes_are_stored_per_interface(self) -> None:
        required = (
            'if (part === "led_left") return "led_left_shape";',
            'if (part === "led_right") return "led_right_shape";',
            'port.led_left_shape = normalisePortLedShape(port.led_left_shape, cal.ui.port_led_shape);',
            'port.led_right_shape = normalisePortLedShape(port.led_right_shape, cal.ui.port_led_shape);',
            'sfp.led_left_shape = normalisePortLedShape(sfp.led_left_shape, cal.ui.port_led_shape);',
            'sfp.led_right_shape = normalisePortLedShape(sfp.led_right_shape, cal.ui.port_led_shape);',
            'portLedShapeForItem(port, "led_left", calibration)',
            'portLedShapeForItem(port, "led_right", calibration)',
            'portLedShapeForItem(sfp, part, activeCalibration)',
        )
        for marker in required:
            self.assertIn(marker, self.source)

    def test_legacy_profile_shape_is_fallback_only(self) -> None:
        self.assertIn('port_led_shape: "circle"', self.source)
        self.assertIn('normalisePortLedShape(uiFromCalibration(activeCalibration)?.port_led_shape || "circle")', self.source)
        self.assertNotIn('data-cv-field="port-led-shape"', self.source)

    def test_selection_owns_all_quick_select_actions(self) -> None:
        selection_start = self.source.index('data-cv-section="selection"')
        selection_end = self.source.index('data-cv-section="position-size"', selection_start)
        selection = self.source[selection_start:selection_end]

        labels_start = self.source.index('data-cv-section="labels-leds"')
        labels_end = self.source.index('data-cv-section="status-boxes"', labels_start)
        labels = self.source[labels_start:labels_end]

        self.assertIn('${portPresentationControls}', labels)
        self.assertIn('cv-cal-port-presentation-row', self.source)
        self.assertIn('Port Label Style', self.source)
        self.assertIn('data-cv-field="link-led-shape"', self.source)
        self.assertIn('data-cv-field="activity-led-shape"', self.source)

        for marker in (
            'data-target="all_numbers" data-part="number">Port Labels</button>',
            'data-target="all_link_leds" data-part="led_left">All Link LEDs</button>',
            'data-target="all_activity_leds" data-part="led_right">All Activity LEDs</button>',
            'data-target="ports_led_left" data-part="led_left">RJ45 Link</button>',
            'data-target="ports_led_right" data-part="led_right">RJ45 Activity</button>',
            'data-target="sfps_led_left" data-part="led_left">SFP Link</button>',
            'data-target="sfps_led_right" data-part="led_right">SFP Activity</button>',
        ):
            self.assertIn(marker, selection)
            self.assertNotIn(marker, labels)

        self.assertEqual(
            self.source.count('data-cv-action="select-target"'),
            selection.count('data-cv-action="select-target"'),
        )

    def test_all_link_and_activity_targets_span_rj45_and_sfp(self) -> None:
        required = (
            'return { type: "port_leds", id: "all", part: "led_left" };',
            'return { type: "port_leds", id: "all", part: "led_right" };',
            '...Object.values(cal.ports || {}).map((port) => port?.[editable.part])',
            '...Object.values(cal.sfp || {}).map((sfp) => sfpLedPoint(sfp, editable.part, createMissing))',
            'editable?.type === "port_leds"',
            '? sortedCalibrationPortKeys(cal)',
            '? sortedCalibrationSfpKeys(cal)',
        )
        for marker in required:
            self.assertIn(marker, self.source)

    def test_shape_controls_apply_independently_to_selected_link_and_activity_leds(self) -> None:
        required = (
            'bindSelectedPortLedShape("link-led-shape", "led_left");',
            'bindSelectedPortLedShape("activity-led-shape", "led_right");',
            'const key = portLedShapeKey(part);',
            'cal.ports[portKey][key] = shape;',
            'cal.sfp[sfpKey][key] = shape;',
        )
        for marker in required:
            self.assertIn(marker, self.source)

    def test_shape_fields_transfer_and_import_validation_are_persisted(self) -> None:
        self.assertIn(
            '"led_left_size", "led_right_size", "led_left_shape", "led_right_shape", "led_left_show", "led_right_show"',
            self.source,
        )
        self.assertIn('for (const shapeField of ["led_left_shape", "led_right_shape"])', self.source)
        self.assertIn(
            'expected circle, rectangle, triangle_up, or triangle_down.',
            self.source,
        )


if __name__ == "__main__":
    unittest.main()
