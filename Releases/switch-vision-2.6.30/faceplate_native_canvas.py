from __future__ import annotations

import json
from pathlib import Path

COORDINATE_SPACE = "image-native-v1"
RENDER_WIDTH = 2048.0
RENDER_HEIGHT = 448.0
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise ValueError(f"invalid PNG header: {path}")
    return int.from_bytes(header[16:20], "big"), int.from_bytes(header[20:24], "big")


def _transform(native_width: float, native_height: float, render_width: float, render_height: float) -> tuple[float, float, float]:
    if native_width <= 0 or native_height <= 0 or render_width <= 0 or render_height <= 0:
        raise ValueError("canvas dimensions must be positive")
    scale = min(native_width / render_width, native_height / render_height)
    offset_x = (native_width - (render_width * scale)) / 2.0
    offset_y = (native_height - (render_height * scale)) / 2.0
    return scale, offset_x, offset_y


def _rounded(value: float) -> float | int:
    result = round(float(value), 9)
    if abs(result) < 1e-9:
        result = 0.0
    integer = round(result)
    if abs(result - integer) < 1e-9:
        return int(integer)
    return result


def _point_to_native(point: object, scale: float, offset_x: float, offset_y: float) -> None:
    if not isinstance(point, list) or len(point) < 2:
        return
    point[0] = _rounded((float(point[0]) * scale) + offset_x)
    point[1] = _rounded((float(point[1]) * scale) + offset_y)


def _point_to_render(point: object, scale: float, offset_x: float, offset_y: float) -> None:
    if not isinstance(point, list) or len(point) < 2:
        return
    point[0] = _rounded((float(point[0]) - offset_x) / scale)
    point[1] = _rounded((float(point[1]) - offset_y) / scale)


def _size_to_native(size: object, scale: float) -> None:
    if not isinstance(size, list) or len(size) < 2:
        return
    size[0] = _rounded(float(size[0]) * scale)
    size[1] = _rounded(float(size[1]) * scale)


def _size_to_render(size: object, scale: float) -> None:
    if not isinstance(size, list) or len(size) < 2:
        return
    size[0] = _rounded(float(size[0]) / scale)
    size[1] = _rounded(float(size[1]) / scale)


def _scalar_to_native(container: dict, key: str, scale: float) -> None:
    if key in container and isinstance(container.get(key), (int, float)):
        container[key] = _rounded(float(container[key]) * scale)


def _scalar_to_render(container: dict, key: str, scale: float) -> None:
    if key in container and isinstance(container.get(key), (int, float)):
        container[key] = _rounded(float(container[key]) / scale)


def _transform_profile(data: dict, *, to_native: bool, native_width: int, native_height: int, render_width: float, render_height: float) -> dict:
    result = json.loads(json.dumps(data))
    scale, offset_x, offset_y = _transform(float(native_width), float(native_height), render_width, render_height)
    point_fn = _point_to_native if to_native else _point_to_render
    size_fn = _size_to_native if to_native else _size_to_render
    scalar_fn = _scalar_to_native if to_native else _scalar_to_render

    def point(point: object, *, relative: bool = False) -> None:
        if relative:
            point_fn(point, scale, 0.0, 0.0)
        else:
            point_fn(point, scale, offset_x, offset_y)

    def size(value: object) -> None:
        size_fn(value, scale)

    for collection_name in ("ports", "sfp"):
        collection = result.get(collection_name)
        if not isinstance(collection, dict):
            continue
        for item in collection.values():
            if not isinstance(item, dict):
                continue
            for key in ("center", "number", "label", "led_left", "led_right"):
                point(item.get(key))
            for key in ("hitbox", "led_left_size", "led_right_size"):
                size(item.get(key))

    status_leds = result.get("status_leds")
    if isinstance(status_leds, dict):
        for value in status_leds.values():
            point(value)

    ui = result.get("ui")
    if isinstance(ui, dict):
        for key in ("logo", "calibration_button", "status_panel", "status_panel_2"):
            box = ui.get(key)
            if not isinstance(box, dict):
                continue
            if isinstance(box.get("x"), (int, float)):
                box["x"] = _rounded((float(box["x"]) * scale + offset_x) if to_native else ((float(box["x"]) - offset_x) / scale))
            if isinstance(box.get("y"), (int, float)):
                box["y"] = _rounded((float(box["y"]) * scale + offset_y) if to_native else ((float(box["y"]) - offset_y) / scale))
            scalar_fn(box, "width", scale)
            scalar_fn(box, "height", scale)
            scalar_fn(box, "font_size", scale)
            scalar_fn(box, "title_font_size", scale)
            fields = box.get("fields")
            if isinstance(fields, dict):
                for field_point in fields.values():
                    point(field_point, relative=True)

        scalar_fn(ui, "port_number_font_size", scale)
        scalar_fn(ui, "sfp_label_font_size", scale)
        status_style = ui.get("status_leds")
        if isinstance(status_style, dict):
            scalar_fn(status_style, "font_size", scale)

    image = result.get("image")
    if not isinstance(image, dict):
        image = {}
        result["image"] = image
    if to_native:
        image["width"] = int(native_width)
        image["height"] = int(native_height)
        image["coordinate_space"] = COORDINATE_SPACE
    else:
        image["width"] = int(round(render_width))
        image["height"] = int(round(render_height))
        image.pop("coordinate_space", None)
    return result


def normalize_faceplate_factory_calibrations(calibration_dir: Path, faceplate_dir: Path) -> list[Path]:
    changed: list[Path] = []
    for path in sorted(calibration_dir.glob("faceplate-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"factory profile must be an object: {path}")
        image = data.get("image") if isinstance(data.get("image"), dict) else {}
        ui = data.get("ui") if isinstance(data.get("ui"), dict) else {}
        faceplate = ui.get("faceplate") if isinstance(ui.get("faceplate"), dict) else {}
        filename = Path(str(faceplate.get("file") or image.get("file") or "")).name
        if not filename:
            raise ValueError(f"factory profile has no faceplate filename: {path}")
        png = faceplate_dir / filename
        native_width, native_height = png_dimensions(png)

        if image.get("coordinate_space") == COORDINATE_SPACE:
            if int(image.get("width") or 0) != native_width or int(image.get("height") or 0) != native_height:
                raise ValueError(f"native canvas mismatch for {path}: profile={image.get('width')}x{image.get('height')} png={native_width}x{native_height}")
            continue

        render_width = float(image.get("width") or RENDER_WIDTH)
        render_height = float(image.get("height") or RENDER_HEIGHT)
        normalized = _transform_profile(
            data,
            to_native=True,
            native_width=native_width,
            native_height=native_height,
            render_width=render_width,
            render_height=render_height,
        )
        path.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        changed.append(path)
    return changed


def render_space_calibration(data: dict) -> dict:
    image = data.get("image") if isinstance(data, dict) and isinstance(data.get("image"), dict) else {}
    if image.get("coordinate_space") != COORDINATE_SPACE:
        return json.loads(json.dumps(data))
    native_width = int(image.get("width") or 0)
    native_height = int(image.get("height") or 0)
    if native_width <= 0 or native_height <= 0:
        raise ValueError("native profile has invalid image dimensions")
    return _transform_profile(
        data,
        to_native=False,
        native_width=native_width,
        native_height=native_height,
        render_width=RENDER_WIDTH,
        render_height=RENDER_HEIGHT,
    )
