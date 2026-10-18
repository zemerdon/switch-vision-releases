from __future__ import annotations

import subprocess
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
            'const PORT_LED_SHAPES = Object.freeze(["circle", "rectangle", "triangle_up", "triangle_down", "triangle_left", "triangle_right"]);',
            'const width = Math.max(2, Math.round(storedWidth * (sideways ? 1.25 : 0.6) * 10) / 10);',
            'const height = Math.max(2, Math.round(storedHeight * (sideways ? 0.6 : 1.25) * 10) / 10);',
            'const sideways = shape === "triangle_left" || shape === "triangle_right";',
            'shape === "triangle_down"',
            '[[x - halfWidth, y - halfHeight], [x + halfWidth, y - halfHeight], [x, y + halfHeight]]',
            '[[x, y - halfHeight], [x + halfWidth, y + halfHeight], [x - halfWidth, y + halfHeight]]',
            '[[x - halfWidth, y], [x + halfWidth, y - halfHeight], [x + halfWidth, y + halfHeight]]',
            '[[x + halfWidth, y], [x - halfWidth, y - halfHeight], [x - halfWidth, y + halfHeight]]',
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
            'data-target="all_link_activity_leds" data-part="both">All Link/Activity</button>',
            'data-target="rj45_link_activity_leds" data-part="both">RJ45 Link/Activity</button>',
            'data-target="sfp_link_activity_leds" data-part="both">SFP Link/Activity</button>',
        ):
            self.assertIn(marker, selection)
            self.assertNotIn(marker, labels)

        for removed in (
            'data-target="ports_led_left" data-part="led_left">RJ45 Link</button>',
            'data-target="ports_led_right" data-part="led_right">RJ45 Activity</button>',
            'data-target="sfps_led_left" data-part="led_left">SFP Link</button>',
            'data-target="sfps_led_right" data-part="led_right">SFP Activity</button>',
        ):
            self.assertNotIn(removed, selection)
        for target in ("ports_led_left", "ports_led_right", "sfps_led_left", "sfps_led_right"):
            self.assertIn('option("'+target+'"', self.source)

        self.assertEqual(
            self.source.count('data-cv-action="select-target"'),
            selection.count('data-cv-action="select-target"'),
        )

    def test_status_box_quick_selects_use_two_compact_dropdowns(self) -> None:
        css = (ROOT / "src/css/switch-vision.css").read_text()
        start = self.source.index('<div class="cv-cal-tools-row cv-cal-status-quick-row">')
        end = self.source.index('<div class="cv-cal-tools-row cv-cal-custom-port-row">', start)
        row = self.source[start:end]
        self.assertEqual(row.count('data-cv-quick-group='), 5)
        self.assertEqual(row.count('<label class="cv-cal-status-quick-group">'), 5)
        self.assertEqual(row.count('data-cv-action="select-target"'), 0)
        self.assertIn('statusBoxQuickOptionsHtml(this.config, 1)', row)
        self.assertIn('statusBoxQuickOptionsHtml(this.config, 2)', row)
        self.assertIn('statusBoxQuickOptionsHtml(this.config, 3)', row)
        self.assertIn('statusBoxQuickOptionsHtml(this.config, 4)', row)
        self.assertIn('statusBoxQuickOptionsHtml(this.config, 5)', row)
        quick_data = self.source.split('const SV_STATUS_BOX_QUICK_GROUPS = Object.freeze(', 1)[1].split('function statusBoxQuickOptionsHtml', 1)[0]
        for group in ("status_box", "status_box_2", "status_fields", "status_fields_2", "ports_odd_entire",
                      "ports_even_numbers", "sfps_odd_entire", "sfps_even_labels", "rsfps_odd_entire", "rsfps_even_labels"):
            self.assertIn('"' + group + '"', quick_data)
        self.assertIn('this.applyCalibrationQuickTarget(cal, target, part);', self.source)
        self.assertIn('this.applyCalibrationQuickTarget(', self.source)
        self.assertIn('.cv-cal-tools .cv-cal-status-quick-row{', css)
        self.assertIn('flex-wrap:wrap;', css)
        self.assertNotIn('.cv-cal-status-quick-actions', css)

    def test_all_link_and_activity_targets_span_rj45_and_sfp(self) -> None:
        required = (
            'return { type: "port_leds", id: "all", part: "led_left" };',
            'return { type: "port_leds", id: "all", part: "led_right" };',
            '...scope.portKeys.flatMap((key) => scope.parts.map((part) => cal.ports?.[key]?.[part]))',
            '...scope.sfpKeys.flatMap((key) => scope.parts.map((part) => sfpLedPoint(cal.sfp?.[key], part, createMissing)))',
            'return { type: "port_leds", id: "rj45", part: "both" };',
            'return { type: "port_leds", id: "sfp", part: "both" };',
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
            'expected circle, rectangle, triangle_up, triangle_down, triangle_left, or triangle_right.',
            self.source,
        )

    def test_sideways_triangle_dropdowns_and_orientation(self) -> None:
        start = self.source.index("const PORT_LED_SHAPES = Object.freeze(")
        stop = self.source.index("\nfunction defaultPortLedRectangleSize", start)
        helpers = self.source[start:stop]
        start = self.source.index("function portLed(svg,")
        stop = self.source.index("\nfunction sfpLedFallbackPoint", start)
        render = self.source[start:stop]
        harness = """
const uiFromCalibration = () => ({});
const layout = {ports:{r:3.1}};
const normalisePortLedRectangleSize = (v) => v;
const polygon = (_svg, points) => points;
const applyPortLedColourOverride = (element) => element;
""" + helpers + "\n" + render + """
for (const shape of ["triangle_left", "triangle_right", "triangle_up", "triangle_down"]) {
 const html = portLedShapeOptionsHtml(shape);
 if (!html.includes('value="' + shape + '" selected')) throw new Error("missing dropdown "+shape);
 if (normalisePortLedShape(shape) !== shape) throw new Error("shape rejected");
}
for (const [part,shape] of [["led_left","triangle_left"],["led_right","triangle_right"]]) {
 const points = portLed(null,100,200,3,"cv-led-green",{},[16,10],part,shape);
 if (portLedShapeKey(part) !== (part==="led_left"?"led_left_shape":"led_right_shape")) throw new Error("storage mismatch");
 if (shape==="triangle_left" && !(points[0][0]<points[1][0] && points[0][0]<points[2][0])) throw new Error("left tip");
 if (shape==="triangle_right" && !(points[0][0]>points[1][0] && points[0][0]>points[2][0])) throw new Error("right tip");
 if (points[0][1]!==200 || Math.abs(points[0][0]-points[1][0])!==20 || Math.abs(points[1][1]-points[2][1])!==6) throw new Error("sideways envelope");
}
for (const shape of ["triangle_up","triangle_down"]) {
 const points=portLed(null,100,200,3,"cv-led-green",{},[16,10],"led_left",shape);
 const xs=points.map(p=>p[0]), ys=points.map(p=>p[1]);
 if (Math.abs(Math.max(...xs)-Math.min(...xs)-9.6)>1e-8 || Math.abs(Math.max(...ys)-Math.min(...ys)-12.5)>1e-8) throw new Error("vertical shape drift");
}
if (normalisePortLedShape("invalid")!=="circle") throw new Error("invalid fallback");
"""
        result = subprocess.run(["node", "-e", harness], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_circle_shape_consumes_saved_led_size(self) -> None:
        self.assertIn("function portLedCircleRadius(value, radius = layout.ports?.r)", self.source)
        self.assertIn("portLedCircleRadius(rectangleSize, r)", self.source)

        def extract(signature: str) -> str:
            start = self.source.index(signature)
            brace = self.source.index("{", start)
            depth = 0
            quote = None
            escape = False
            for pos in range(brace, len(self.source)):
                char = self.source[pos]
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
                        return self.source[start : pos + 1]
            raise AssertionError(f"unterminated function: {signature}")

        helpers = "\n".join(
            [
                extract("function defaultPortLedRectangleSize(radius = layout.ports?.r)"),
                extract("function normalisePortLedRectangleSize(value, radius = layout.ports?.r)"),
                extract("function portLedCircleRadius(value, radius = layout.ports?.r)"),
            ]
        )
        harness = f"""
const layout = {{ports: {{r: 3.1}}}};
{helpers}
const base = portLedCircleRadius(defaultPortLedRectangleSize(3.1), 3.1);
const wider = portLedCircleRadius([20, defaultPortLedRectangleSize(3.1)[1]], 3.1);
const taller = portLedCircleRadius([defaultPortLedRectangleSize(3.1)[0], 20], 3.1);
const square = portLedCircleRadius([20, 20], 3.1);
if (Math.abs(base - 3.1) > 0.1) throw new Error("default circle radius drifted");
if (!(wider > base)) throw new Error("circle width resize did not affect radius");
if (!(taller > base)) throw new Error("circle height resize did not affect radius");
if (!(square > wider && square > taller)) throw new Error("larger saved circle size did not render larger");
"""
        result = subprocess.run(["node", "-e", harness], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
