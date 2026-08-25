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


class FaceplateNativeCanvasContract(unittest.TestCase):
    def test_factory_interactive_geometry_is_native_and_in_bounds(self) -> None:
        for path in sorted(CAL.glob("faceplate-*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            image = data["image"]
            filename = Path(str((data.get("ui") or {}).get("faceplate", {}).get("file") or image["file"])).name
            width, height = png_size(FACEPLATES / filename)
            self.assertEqual(image.get("coordinate_space"), "image-native-v1", path.name)
            self.assertEqual((image.get("width"), image.get("height")), (width, height), path.name)

            for collection_name in ("ports", "sfp"):
                for key, item in (data.get(collection_name) or {}).items():
                    for field in ("center", "number", "label", "led_left", "led_right"):
                        point = item.get(field)
                        if not isinstance(point, list) or len(point) < 2:
                            continue
                        self.assertGreaterEqual(float(point[0]), 0, f"{path.name}:{collection_name}:{key}:{field}:x")
                        self.assertGreaterEqual(float(point[1]), 0, f"{path.name}:{collection_name}:{key}:{field}:y")
                        self.assertLessEqual(float(point[0]), width, f"{path.name}:{collection_name}:{key}:{field}:x")
                        self.assertLessEqual(float(point[1]), height, f"{path.name}:{collection_name}:{key}:{field}:y")

            for name, point in (data.get("status_leds") or {}).items():
                self.assertGreaterEqual(float(point[0]), 0, f"{path.name}:status:{name}:x")
                self.assertGreaterEqual(float(point[1]), 0, f"{path.name}:status:{name}:y")
                self.assertLessEqual(float(point[0]), width, f"{path.name}:status:{name}:x")
                self.assertLessEqual(float(point[1]), height, f"{path.name}:status:{name}:y")

            ui = data.get("ui") or {}
            for name in ("calibration_button", "status_panel", "status_panel_2"):
                box = ui.get(name) or {}
                x, y = float(box.get("x") or 0), float(box.get("y") or 0)
                w, h = float(box.get("width") or 0), float(box.get("height") or 0)
                self.assertGreaterEqual(x, 0, f"{path.name}:{name}:x")
                self.assertGreaterEqual(y, 0, f"{path.name}:{name}:y")
                self.assertLessEqual(x + w, width, f"{path.name}:{name}:right")
                self.assertLessEqual(y + h, height, f"{path.name}:{name}:bottom")

    def test_renderer_has_native_to_legacy_compatibility_transform(self) -> None:
        text = FRONTEND.read_text(encoding="utf-8")
        for needle in (
            'const SV_FACEPLATE_NATIVE_COORDINATE_SPACE = "image-native-v1";',
            "function calibrationRenderSpaceData(source)",
            "const renderCal = calibrationRenderSpaceData(cal);",
            "uiFromCalibration(calibrationRenderSpaceData(this.calibrationData()))",
        ):
            self.assertIn(needle, text)


if __name__ == "__main__":
    unittest.main()
