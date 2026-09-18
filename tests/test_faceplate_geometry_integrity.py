from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
FACEPLATES = SRC / "faceplates"
CALIBRATIONS = SRC / "calibration"
CARD = SRC / "js" / "switch-vision.js"
REGISTRY = SRC / "devices" / "supported_devices.json"

_CANVAS_SPEC = importlib.util.spec_from_file_location(
    "switch_vision_faceplate_native_canvas",
    SRC / "faceplate_native_canvas.py",
)
assert _CANVAS_SPEC and _CANVAS_SPEC.loader
_CANVAS = importlib.util.module_from_spec(_CANVAS_SPEC)
_CANVAS_SPEC.loader.exec_module(_CANVAS)


def png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    assert header[:8] == b"\x89PNG\r\n\x1a\n", path.name
    return struct.unpack(">II", header[16:24])


def faceplate_calibrations() -> dict[str, dict]:
    result: dict[str, dict] = {}
    for path in sorted(CALIBRATIONS.glob("faceplate-*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        image = payload.get("image") or {}
        filename = Path(str(image.get("file") or "")).name
        assert filename, path.name
        assert filename not in result, filename
        result[filename] = payload
    return result


def profile_faceplates(source: str) -> dict[str, str]:
    match = re.search(
        r"const SV_FACEPLATE_PROFILE_FILES = \{(.*?)\n\};",
        source,
        re.S,
    )
    assert match, "SV_FACEPLATE_PROFILE_FILES missing"
    return dict(
        re.findall(r'^\s*([A-Za-z0-9_]+):\s*"([^"]+)",?\s*$', match.group(1), re.M)
    )


def embedded_faceplates(source: str) -> dict[str, dict]:
    match = re.search(
        r"const SV_FACEPLATE_FACTORY_CALIBRATIONS = (\{.*?\});\n\nfunction faceplateFactoryCalibrationForFile",
        source,
        re.S,
    )
    assert match, "SV_FACEPLATE_FACTORY_CALIBRATIONS missing"
    return json.loads(match.group(1))


def iter_points(payload: object, path: str = ""):
    if isinstance(payload, dict):
        for key, value in payload.items():
            child = f"{path}.{key}" if path else str(key)
            if key in {"center", "number", "label", "led_left", "led_right"}:
                if isinstance(value, list) and len(value) >= 2:
                    yield child, value
            else:
                yield from iter_points(value, child)
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            yield from iter_points(value, f"{path}[{index}]")


def test_all_shipped_faceplates_own_valid_native_geometry() -> None:
    calibrations = faceplate_calibrations()
    shipped = {path.name for path in FACEPLATES.glob("*.png")}
    assert shipped == set(calibrations), (
        f"faceplate/calibration coverage differs: shipped={sorted(shipped)}, "
        f"calibrated={sorted(calibrations)}"
    )

    embedded = embedded_faceplates(CARD.read_text(encoding="utf-8"))
    assert embedded == calibrations, "embedded faceplate defaults drift from authoritative JSON"

    for filename in sorted(shipped):
        calibration = calibrations[filename]
        image = calibration.get("image") or {}
        width, height = png_size(FACEPLATES / filename)
        assert image.get("width") == width, filename
        assert image.get("height") == height, filename
        assert image.get("coordinate_space") == "image-native-v1", filename
        assert Path(str(image.get("file") or "")).name == filename, filename

        for section in ("ports", "sfp", "status_leds", "ui"):
            for point_path, point in iter_points(calibration.get(section) or {}, section):
                x, y = point[:2]
                assert isinstance(x, (int, float)) and isinstance(y, (int, float)), (
                    filename,
                    point_path,
                    point,
                )
                assert 0 <= x <= width and 0 <= y <= height, (
                    filename,
                    point_path,
                    point,
                    (width, height),
                )


def test_every_dashboard_default_profile_resolves_to_its_faceplate_geometry() -> None:
    calibrations = faceplate_calibrations()
    source = CARD.read_text(encoding="utf-8")
    profile_map = profile_faceplates(source)
    devices = json.loads(REGISTRY.read_text(encoding="utf-8")).get("devices", [])

    assert "factoryCalibrationForRecommendation(recommendation)" in source
    assert "faceplateFactoryCalibrationForFile(recommendedFile)" in source

    for row in devices:
        if not isinstance(row, dict) or row.get("dashboard_support") is not True:
            continue
        model = str(row.get("model") or "")
        faceplate = Path(str(row.get("default_faceplate") or "")).name
        profile = str(row.get("calibration_profile") or "")
        visuals = row.get("visuals") or {}

        assert faceplate in calibrations, (model, faceplate)
        assert profile, model
        assert profile_map.get(profile) == faceplate, (
            f"{model}: profile {profile!r} resolves to {profile_map.get(profile)!r}, "
            f"not its shipped faceplate {faceplate!r}"
        )
        assert Path(str(visuals.get("recommended_faceplate") or "")).name == faceplate, model
        assert visuals.get("calibration_profile") == profile, model


def test_brendan_pro_max_keeps_original_standard_24_plus_2_geometry() -> None:
    devices = {
        str(row.get("model")): row
        for row in json.loads(REGISTRY.read_text(encoding="utf-8")).get("devices", [])
        if isinstance(row, dict)
    }
    row = devices["USW Pro Max 24"]
    assert row["default_faceplate"] == "faceplates/unifi-24p-rj45-2sfp.png"
    assert row["calibration_profile"] == "unifi_24p_rj45_2sfp"
    assert row["visuals"]["recommended_faceplate"] == "faceplates/unifi-24p-rj45-2sfp.png"
    assert row["visuals"]["calibration_profile"] == "unifi_24p_rj45_2sfp"


def test_stock_48_port_factory_presentation_contract() -> None:
    expected_fonts = {
        "port_number_font_size": 13.0,
        "sfp_label_font_size": 13.5,
        "status_led_font_size": 16.5,
    }

    for filename in ("48rj45-2sfp.png", "48rj45-4sfp.png"):
        payload = faceplate_calibrations()[filename]
        rendered = _CANVAS.render_space_calibration(payload)
        ui = rendered.get("ui") or {}
        status_leds = ui.get("status_leds") or {}
        assert ui.get("port_number_font_size") == expected_fonts["port_number_font_size"], filename
        assert ui.get("sfp_label_font_size") == expected_fonts["sfp_label_font_size"], filename
        assert status_leds.get("font_size") == expected_fonts["status_led_font_size"], filename

    four = _CANVAS.render_space_calibration(faceplate_calibrations()["48rj45-4sfp.png"])
    assert list(four.get("sfp") or {}) == ["G1", "G2", "G3/TE3", "G4/TE4"]
    assert four["sfp"]["G1"]["label"] == [1709, 188]
    assert four["sfp"]["G2"]["label"] == [1838, 188]
    assert four["sfp"]["G3/TE3"]["label"] == [1710, 402]
    assert four["sfp"]["G4/TE4"]["label"] == [1839, 402]
    assert all(item.get("label_show") is True for item in four["sfp"].values())

    owner_ui = json.loads(json.dumps(four.get("ui") or {}))
    if isinstance(owner_ui.get("faceplate"), dict):
        owner_ui["faceplate"].pop("file", None)
        owner_ui["faceplate"].pop("source", None)
    owner_geometry = {
        "image": {
            "width": 2048,
            "height": 448,
            "coordinate_space": "switch-vision-render-2048x448-v1",
        },
        "ports": four.get("ports") or {},
        "sfp": four.get("sfp") or {},
        "status_leds": four.get("status_leds") or {},
        "ui": owner_ui,
    }
    canonical = json.dumps(
        owner_geometry,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    assert hashlib.sha256(canonical).hexdigest() == (
        "3069b582f48b4a8906907d37ef0b617fe7fdbdfb4bd4aeecc09a43e3f9a59b03"
    )


if __name__ == "__main__":
    test_all_shipped_faceplates_own_valid_native_geometry()
    test_every_dashboard_default_profile_resolves_to_its_faceplate_geometry()
    test_brendan_pro_max_keeps_original_standard_24_plus_2_geometry()
    test_stock_48_port_factory_presentation_contract()
    print("Switch Vision shipped faceplate geometry integrity: PASS")
