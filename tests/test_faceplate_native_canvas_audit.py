#!/usr/bin/env python3
from __future__ import annotations

import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_DIR = ROOT / "src" / "calibration"
FACEPLATE_DIR = ROOT / "src" / "faceplates"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
LEGACY_WIDTH = 2048.0
LEGACY_HEIGHT = 448.0


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise AssertionError(f"{path}: invalid PNG header")
    return struct.unpack(">II", header[16:24])


def transform_for_native(width: int, height: int) -> tuple[float, float, float, float]:
    native_ratio = width / height
    legacy_ratio = LEGACY_WIDTH / LEGACY_HEIGHT
    if abs(native_ratio - legacy_ratio) < 1e-12:
        return width / LEGACY_WIDTH, height / LEGACY_HEIGHT, 0.0, 0.0
    if native_ratio > legacy_ratio:
        scale = height / LEGACY_HEIGHT
        return scale, scale, (width - (LEGACY_WIDTH * scale)) / 2.0, 0.0
    scale = width / LEGACY_WIDTH
    return scale, scale, 0.0, (height - (LEGACY_HEIGHT * scale)) / 2.0


def geometry_extents(data: dict) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for collection in (data.get("ports"), data.get("sfp")):
        if not isinstance(collection, dict):
            continue
        for item in collection.values():
            if not isinstance(item, dict):
                continue
            for field in ("center", "led_left", "led_right", "number", "label"):
                point = item.get(field)
                if isinstance(point, list) and len(point) >= 2:
                    xs.append(float(point[0]))
                    ys.append(float(point[1]))
    return (min(xs) if xs else 0.0, max(xs) if xs else 0.0, min(ys) if ys else 0.0, max(ys) if ys else 0.0)


class FaceplateNativeCanvasAudit(unittest.TestCase):
    def test_bundled_faceplate_native_dimensions_are_auditable(self) -> None:
        seen = 0
        for profile_path in sorted(CALIBRATION_DIR.glob("faceplate-*.json")):
            data = json.loads(profile_path.read_text(encoding="utf-8"))
            ui = data.get("ui") if isinstance(data.get("ui"), dict) else {}
            faceplate = ui.get("faceplate") if isinstance(ui.get("faceplate"), dict) else {}
            image = data.get("image") if isinstance(data.get("image"), dict) else {}
            filename = Path(str(faceplate.get("file") or image.get("file") or "")).name
            self.assertTrue(filename, f"{profile_path.name}: missing faceplate filename")
            png = FACEPLATE_DIR / filename
            self.assertTrue(png.is_file(), f"{profile_path.name}: missing {filename}")
            width, height = png_dimensions(png)
            sx, sy, ox, oy = transform_for_native(width, height)
            min_x, max_x, min_y, max_y = geometry_extents(data)
            print(
                "FACEPLATE_NATIVE_AUDIT "
                f"profile={profile_path.name} file={filename} native={width}x{height} "
                f"declared={image.get('width')}x{image.get('height')} "
                f"legacy_extents=x[{min_x:g},{max_x:g}] y[{min_y:g},{max_y:g}] "
                f"legacy_to_native=scale({sx:.12g},{sy:.12g}) offset({ox:.12g},{oy:.12g})"
            )
            seen += 1
        self.assertGreater(seen, 0, "no bundled faceplate factory profiles found")


if __name__ == "__main__":
    unittest.main()
