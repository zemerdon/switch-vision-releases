from __future__ import annotations

import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "src" / "calibration"
FACEPLATES = ROOT / "src" / "faceplates"
FRONTEND = ROOT / "src" / "js" / "switch-vision.js"


def png_size(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()[:24]
    if len(raw) < 24 or raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
        raise AssertionError(f"invalid PNG: {path}")
    return struct.unpack(">II", raw[16:24])


def assert_point(case: unittest.TestCase, point: object, width: float, height: float, label: str) -> None:
    if not isinstance(point, list) or len(point) < 2:
        return
    x, y = map(float, point[:2])
    case.assertGreaterEqual(x, 0.0, f"{label}: negative x={x}")
    case.assertGreaterEqual(y, 0.0, f"{label}: negative y={y}")
    case.assertLessEqual(x, width, f"{label}: x={x} exceeds width={width}")
    case.assertLessEqual(y, height, f"{label}: y={y} exceeds height={height}")


def assert_centered_box(case: unittest.TestCase, center: object, size: object, width: float, height: float, label: str) -> None:
    if not isinstance(center, list) or len(center) < 2 or not isinstance(size, list) or len(size) < 2:
        return
    cx, cy = map(float, center[:2])
    box_w, box_h = map(float, size[:2])
    case.assertGreater(box_w, 0.0, f"{label}: width must be positive")
    case.assertGreater(box_h, 0.0, f"{label}: height must be positive")
    case.assertGreaterEqual(cx - box_w / 2.0, 0.0, f"{label}: crosses left canvas edge")
    case.assertGreaterEqual(cy - box_h / 2.0, 0.0, f"{label}: crosses top canvas edge")
    case.assertLessEqual(cx + box_w / 2.0, width, f"{label}: crosses right canvas edge")
    case.assertLessEqual(cy + box_h / 2.0, height, f"{label}: crosses bottom canvas edge")


def assert_top_left_box(case: unittest.TestCase, box: object, width: float, height: float, label: str) -> None:
    if not isinstance(box, dict):
        return
    x = float(box.get("x") or 0)
    y = float(box.get("y") or 0)
    box_w = float(box.get("width") or 0)
    box_h = float(box.get("height") or 0)
    case.assertGreaterEqual(x, 0.0, f"{label}: negative x={x}")
    case.assertGreaterEqual(y, 0.0, f"{label}: negative y={y}")
    case.assertGreater(box_w, 0.0, f"{label}: width must be positive")
    case.assertGreater(box_h, 0.0, f"{label}: height must be positive")
    case.assertLessEqual(x + box_w, width, f"{label}: crosses right canvas edge")
    case.assertLessEqual(y + box_h, height, f"{label}: crosses bottom canvas edge")


class FaceplateNativeCanvasContract(unittest.TestCase):
    def test_factory_geometry_is_native_nonnegative_and_fully_in_bounds(self) -> None:
        profiles = sorted(CAL.glob("faceplate-*.json"))
        self.assertTrue(profiles, "no bundled faceplate factory profiles found")

        for path in profiles:
            data = json.loads(path.read_text(encoding="utf-8"))
            image = data["image"]
            ui = data.get("ui") or {}
            filename = Path(str((ui.get("faceplate") or {}).get("file") or image["file"])).name
            width, height = png_size(FACEPLATES / filename)

            coordinate_space = image.get("coordinate_space")
            if coordinate_space == "image-native-v1":
                geometry_width, geometry_height = width, height
                self.assertEqual((image.get("width"), image.get("height")), (width, height), path.name)
            elif coordinate_space == "switch-vision-render-2048x448-v1":
                geometry_width, geometry_height = 2048, 448
                self.assertEqual((image.get("width"), image.get("height")), (2048, 448), path.name)
                self.assertEqual((image.get("native_width"), image.get("native_height")), (width, height), path.name)
            else:
                self.fail(f"{path.name}: unsupported coordinate space {coordinate_space!r}")

            extended_sfp = data.get("allow_out_of_bounds_sfp_geometry") is True
            if extended_sfp:
                self.assertEqual(
                    path.name,
                    "faceplate-dell-4032f.json",
                    "extended SFP geometry requires a deliberately reviewed factory profile",
                )

            for collection_name in ("ports", "sfp"):
                collection_width = geometry_width * 2 if collection_name == "sfp" and extended_sfp else geometry_width
                for key, item in (data.get(collection_name) or {}).items():
                    prefix = f"{path.name}:{collection_name}:{key}"
                    for field in ("center", "number", "label", "led_left", "led_right"):
                        assert_point(self, item.get(field), collection_width, geometry_height, f"{prefix}:{field}")
                    assert_centered_box(self, item.get("center"), item.get("hitbox"), collection_width, geometry_height, f"{prefix}:hitbox")
                    assert_centered_box(self, item.get("led_left"), item.get("led_left_size"), collection_width, geometry_height, f"{prefix}:led_left")
                    assert_centered_box(self, item.get("led_right"), item.get("led_right_size"), collection_width, geometry_height, f"{prefix}:led_right")

            for name, point in (data.get("status_leds") or {}).items():
                assert_point(self, point, geometry_width, geometry_height, f"{path.name}:status:{name}")

            extended_ui = data.get("allow_out_of_bounds_ui_geometry") is True
            if extended_ui:
                self.assertEqual(
                    path.name,
                    "faceplate-dell-4032f.json",
                    "extended UI geometry requires a deliberately reviewed factory profile",
                )
            for name in ("logo", "calibration_button", "status_panel", "status_panel_2"):
                box = ui.get(name)
                if extended_ui and isinstance(box, dict):
                    x = float(box.get("x") or 0)
                    y = float(box.get("y") or 0)
                    box_w = float(box.get("width") or 0)
                    box_h = float(box.get("height") or 0)
                    self.assertGreaterEqual(x, -geometry_width, f"{path.name}:{name}: x below safe range")
                    self.assertGreaterEqual(y, -geometry_height, f"{path.name}:{name}: y below safe range")
                    self.assertLessEqual(x, geometry_width * 2, f"{path.name}:{name}: x above safe range")
                    self.assertLessEqual(y, geometry_height * 2, f"{path.name}:{name}: y above safe range")
                    self.assertGreater(box_w, 0.0, f"{path.name}:{name}: width must be positive")
                    self.assertGreater(box_h, 0.0, f"{path.name}:{name}: height must be positive")
                else:
                    assert_top_left_box(self, box, geometry_width, geometry_height, f"{path.name}:{name}")

    def test_renderer_has_native_to_legacy_compatibility_transform(self) -> None:
        text = FRONTEND.read_text(encoding="utf-8")
        for needle in (
            'const SV_FACEPLATE_NATIVE_COORDINATE_SPACE = "image-native-v1";',
            "function calibrationRenderSpaceData(source)",
            "const renderCal = calibrationRenderSpaceData(cal);",
            "uiFromCalibration(calibrationRenderSpaceData(this.calibrationData()))",
            'viewBox="0 0 2048 448" preserveAspectRatio="none"',
        ):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
