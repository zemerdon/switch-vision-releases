from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

import yaml

from src.faceplate_native_canvas import normalize_faceplate_factory_calibrations, render_space_calibration

PROJECT_ROOT = Path(__file__).resolve().parent
ROOT = PROJECT_ROOT
SRC = PROJECT_ROOT / "src"
RELEASES = PROJECT_ROOT / "Releases"
VERSION_FILE = PROJECT_ROOT / "VERSION"

EXACT_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
WILDCARD_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(?:x|\*)$", re.I)
PROJECT_NAME = "switch-vision"
def is_gold_version(version: str) -> bool:
    """Return true when a semantic version is eligible for Gold packaging."""
    major, _, _ = map(int, version.split("."))
    return major >= 1


def write_text_lf(path: Path, text: str) -> None:
    """Write UTF-8 text with Linux LF line endings on every platform."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.replace("\r\n", "\n").replace("\r", "\n"))


def is_shell_script(path: Path) -> bool:
    return path.name in {"run", "run.sh"} or path.suffix == ".sh"


def normalize_shell_scripts(root: Path) -> None:
    """Force LF endings and executable permissions for all shell entrypoints."""
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not is_shell_script(path):
            continue
        raw = path.read_bytes()
        normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        path.write_bytes(normalized)
        try:
            path.chmod(path.stat().st_mode | 0o111)
        except OSError:
            pass


def validate_shell_scripts(root: Path) -> None:
    errors: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not is_shell_script(path):
            continue
        raw = path.read_bytes()
        rel = path.relative_to(root)
        if b"\r" in raw:
            errors.append(f"{rel}: contains CR/CRLF line endings")
        first = raw.split(b"\n", 1)[0]
        if first.startswith(b"#!") and b"\r" in first:
            errors.append(f"{rel}: invalid CR in shebang")
    if errors:
        raise SystemExit("Shell-script validation failed:\n- " + "\n- ".join(errors))


def read_version() -> str:
    if not VERSION_FILE.exists():
        raise SystemExit(f"Missing version file: {VERSION_FILE}")
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def validate_version(version: str) -> str:
    value = str(version).strip().lstrip("v")
    if not EXACT_VERSION_RE.fullmatch(value):
        raise SystemExit(
            f"Invalid version '{version}'. Use an exact semantic version such as 0.9.0 "
            "or a wildcard such as 0.9.x."
        )
    return value


def increment_version(version: str, part: str) -> str:
    major, minor, patch = map(int, validate_version(version).split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise SystemExit(f"Unknown version bump: {part}")


def increment_patch(version: str) -> str:
    return increment_version(version, "patch")


def find_next_patch_version(major: int, minor: int) -> str:
    patches: set[int] = set()
    if RELEASES.exists():
        for path in RELEASES.glob(f"{PROJECT_NAME}-{major}.{minor}.*"):
            match = re.fullmatch(
                rf"{re.escape(PROJECT_NAME)}-{major}\.{minor}\.(\d+)(?:\.zip)?",
                path.name,
            )
            if match:
                patches.add(int(match.group(1)))
    current = read_version().lstrip("v")
    match = EXACT_VERSION_RE.fullmatch(current)
    if match and int(match.group(1)) == major and int(match.group(2)) == minor:
        patches.add(int(match.group(3)))
    return f"{major}.{minor}.{(max(patches) + 1) if patches else 0}"


def resolve_version(version_arg: str | None, bump: str | None = None) -> str:
    """Resolve an explicit release version; implicit/automatic bumps are forbidden."""
    if bump:
        raise SystemExit(
            "Automatic version bumping is disabled. Pass an explicit -v/--version instead."
        )
    if version_arg is None:
        raise SystemExit(
            "An explicit release version is required. Pass -v/--version, for example: -v 2.2.1"
        )
    requested = str(version_arg).strip().lstrip("v")
    if EXACT_VERSION_RE.fullmatch(requested):
        return validate_version(requested)
    wildcard = WILDCARD_VERSION_RE.fullmatch(requested)
    if wildcard:
        resolved = find_next_patch_version(int(wildcard.group(1)), int(wildcard.group(2)))
        print(f"Resolved {requested} -> {resolved}")
        return resolved
    raise SystemExit(
        f"Invalid version '{version_arg}'. Use an exact semantic version such as 2.2.1 "
        "or a wildcard such as 2.2.x."
    )













def generate_supported_device_docs() -> None:
    """Validate the exact-model registry and regenerate Markdown/BBCode outputs."""
    generator = SRC / "devices" / "generate_supported_devices.py"
    registry = SRC / "devices" / "supported_devices.yaml"
    result = subprocess.run(
        [sys.executable, str(generator), str(registry), str(SRC / "docs")],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "unknown generator error"
        raise SystemExit(f"Supported-device generation failed: {message}")
    if result.stdout.strip():
        print(result.stdout.strip())






FACEPLATE_FACTORY_CONSTANT = "SV_FACEPLATE_FACTORY_CALIBRATIONS"
FACEPLATE_FACTORY_FUNCTION_MARKER = "function faceplateFactoryCalibrationForFile"


def load_faceplate_factory_calibrations(calibration_dir: Path) -> dict[str, dict]:
    """Load authoritative bundled faceplate-default profiles keyed by faceplate filename."""
    profiles: dict[str, dict] = {}
    if not calibration_dir.exists():
        return profiles
    for path in sorted(calibration_dir.glob("faceplate-*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"Invalid faceplate factory calibration {path}: {exc}") from exc
        if not isinstance(data, dict):
            raise SystemExit(f"Faceplate factory calibration must be a JSON object: {path}")
        ui_faceplate = data.get("ui", {}).get("faceplate", {}) if isinstance(data.get("ui"), dict) else {}
        image = data.get("image", {}) if isinstance(data.get("image"), dict) else {}
        filename = Path(str(ui_faceplate.get("file") or image.get("file") or "")).name
        if not filename:
            raise SystemExit(f"Faceplate factory calibration has no faceplate filename: {path}")
        if filename in profiles:
            raise SystemExit(f"Duplicate faceplate factory calibration for {filename}: {path}")
        profiles[filename] = data
    return profiles


def render_faceplate_factory_calibrations(profiles: dict[str, dict]) -> str:
    """Render the authoritative faceplate-default table as deterministic JavaScript."""
    lines = [f"const {FACEPLATE_FACTORY_CONSTANT} = {{"]
    items = sorted(profiles.items())
    for index, (filename, data) in enumerate(items):
        comma = "," if index < len(items) - 1 else ""
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
        lines.append(f"  {json.dumps(filename, ensure_ascii=False)}: {payload}{comma}")
    lines.append("};")
    return "\n".join(lines)


def extract_embedded_faceplate_factory_calibrations(path: Path) -> dict[str, dict]:
    """Parse the embedded faceplate-default table from a card JavaScript source."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    start_marker = f"const {FACEPLATE_FACTORY_CONSTANT} = "
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"Faceplate factory calibration constant not found in {path}")
    payload_start = start + len(start_marker)
    marker = f"\n\n{FACEPLATE_FACTORY_FUNCTION_MARKER}"
    marker_pos = text.find(marker, payload_start)
    if marker_pos < 0:
        raise SystemExit(f"Faceplate factory calibration end marker not found in {path}")
    payload = text[payload_start:marker_pos].strip()
    if not payload.endswith(";"):
        raise SystemExit(f"Faceplate factory calibration table is malformed in {path}")
    payload = payload[:-1].strip()
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Embedded faceplate factory calibration is not valid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Embedded faceplate factory calibration must be an object in {path}")
    return data


def sync_faceplate_factory_calibrations() -> None:
    """Regenerate card-embedded faceplate defaults from authoritative calibration JSON files."""
    profiles = load_faceplate_factory_calibrations(SRC / "calibration")
    canonical = SRC / "js" / "switch-vision.js"
    text = canonical.read_text(encoding="utf-8", errors="ignore")
    start_marker = f"const {FACEPLATE_FACTORY_CONSTANT} = "
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"Faceplate factory calibration constant not found in {canonical}")
    marker = f"\n\n{FACEPLATE_FACTORY_FUNCTION_MARKER}"
    marker_pos = text.find(marker, start)
    if marker_pos < 0:
        raise SystemExit(f"Faceplate factory calibration end marker not found in {canonical}")
    replacement = render_faceplate_factory_calibrations(profiles)
    write_text_lf(canonical, text[:start] + replacement + text[marker_pos:])


def validate_faceplate_factory_calibrations(base: Path, source_layout: bool = False) -> None:
    """Fail the build when embedded faceplate defaults drift from authoritative JSON files."""
    prefix = base / "src" if source_layout else base
    expected = load_faceplate_factory_calibrations(prefix / "calibration")
    paths = [
        prefix / "js" / "switch-vision.js",
        prefix / "custom_components" / "switch_vision" / "switch-vision-card.js",
    ]
    errors: list[str] = []
    for path in paths:
        if not path.exists():
            errors.append(f"missing card JavaScript source: {path}")
            continue
        actual = extract_embedded_faceplate_factory_calibrations(path)
        if actual != expected:
            expected_keys = sorted(expected)
            actual_keys = sorted(actual)
            if actual_keys != expected_keys:
                errors.append(f"{path}: embedded keys {actual_keys!r}, expected {expected_keys!r}")
            else:
                mismatched = [key for key in expected_keys if actual.get(key) != expected.get(key)]
                errors.append(f"{path}: stale embedded defaults for {', '.join(mismatched)}")
    required_stock = {
        "24rj45-2sfp.png": ("stock_24rj45_2sfp", 24, 2),
        "24rj45-4sfp.png": ("stock_24rj45_4sfp", 24, 4),
        "48rj45-2sfp.png": ("stock_48rj45_2sfp", 48, 2),
        "48rj45-4sfp.png": ("stock_48rj45_4sfp", 48, 4),
    }

    for filename, (profile, rj45_count, sfp_count) in required_stock.items():
        calibration = expected.get(filename)

        if calibration is None:
            errors.append(
                f"missing required stock faceplate calibration: {filename}"
            )
            continue

        if calibration.get("profile") != profile:
            errors.append(
                f"{filename}: profile={calibration.get('profile')!r}, "
                f"expected {profile!r}"
            )

        ports = calibration.get("ports")
        sfp = calibration.get("sfp")

        if not isinstance(ports, dict) or len(ports) != rj45_count:
            errors.append(
                f"{filename}: expected {rj45_count} RJ45 calibration entries"
            )

        if not isinstance(sfp, dict) or len(sfp) != sfp_count:
            errors.append(
                f"{filename}: expected {sfp_count} SFP calibration entries"
            )

        image = calibration.get("image")
        image_file = (
            image.get("file")
            if isinstance(image, dict)
            else ""
        )

        if Path(str(image_file)).name != filename:
            errors.append(
                f"{filename}: calibration image points to {image_file!r}"
            )

    dedicated_3560 = expected.get("c3560cg-8pc-s.png")

    if dedicated_3560 is None:
        errors.append(
            "missing dedicated c3560cg-8pc-s.png factory calibration"
        )
    else:
        if dedicated_3560.get("profile") != "cisco_3560cg_8pc":
            errors.append(
                "c3560cg-8pc-s.png: dedicated profile is incorrect"
            )

        if dedicated_3560.get("model") != "cisco-3560cg-8pc-8p-2dual":
            errors.append(
                "c3560cg-8pc-s.png: dedicated model identity is incorrect"
            )

        ports = dedicated_3560.get("ports")
        sfp = dedicated_3560.get("sfp")

        if not isinstance(ports, dict) or len(ports) != 8:
            errors.append(
                "c3560cg-8pc-s.png: expected exactly 8 RJ45 entries"
            )

        if not isinstance(sfp, dict) or list(sfp) != ["G1", "G2"]:
            errors.append(
                "c3560cg-8pc-s.png: expected exactly G1 and G2 uplinks"
            )

    if errors:
        raise SystemExit("Faceplate factory calibration validation failed:\n- " + "\n- ".join(errors))

FACTORY_CALIBRATION_SENSITIVE_KEYS = {
    "switch_ip",
    "management_ip",
    "host",
    "hostname",
    "snmp_community",
    "community",
    "username",
    "password",
    "credential",
    "credentials",
    "instance",
    "instance_id",
    "instance_name",
    "switch_name",
    "selected_switch",
    "discovery_selected_switch",
}


def _nonempty_factory_value(value: object) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return bool(value)


def validate_factory_calibration_privacy(base: Path, source_layout: bool = False) -> None:
    """Reject site-specific identity, addressing, or credentials in bundled factory profiles."""
    prefix = base / "src" if source_layout else base
    calibration_dir = prefix / "calibration"
    errors: list[str] = []

    def visit(value: object, location: str, path: Path) -> None:
        if isinstance(value, dict):
            for raw_key, child in value.items():
                key = str(raw_key).strip().lower()
                child_location = f"{location}.{raw_key}" if location else str(raw_key)
                if key in FACTORY_CALIBRATION_SENSITIVE_KEYS and _nonempty_factory_value(child):
                    errors.append(f"{path}: non-empty factory field {child_location}")
                visit(child, child_location, path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{location}[{index}]", path)

    for path in sorted(calibration_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        stack = data.get("stack") if isinstance(data, dict) else None
        if isinstance(stack, dict):
            if stack.get("enabled") is True:
                errors.append(f"{path}: factory stack.enabled must be false")
            for key in ("stack_id", "uptime_source", "members"):
                if _nonempty_factory_value(stack.get(key)):
                    errors.append(f"{path}: factory stack.{key} must be empty")
        visit(data, "", path)

    if errors:
        raise SystemExit("Factory calibration privacy validation failed:\n- " + "\n- ".join(errors))


STATUS_PANEL_SWITCH_FIELDS = [
    "model", "ip", "cpu", "temp", "poe", "uptime", "vendor", "os",
    "firmware", "serial", "stack", "fans", "psu",
]
STATUS_PANEL_SWITCH_HIDDEN = ["vendor", "os", "firmware", "serial", "stack", "fans", "psu"]
STATUS_PANEL_FIELD_DEFAULTS = {
    **{f"row{i}_key": [24, y] for i, y in enumerate((55, 72, 89, 106, 123, 140), 1)},
    **{f"row{i}_value": [112, y] for i, y in enumerate((55, 72, 89, 106, 123, 140), 1)},
}
STATUS_PANEL_1_FIELD_DEFAULTS = {
    **{f"row{i}_key": [19, y] for i, y in enumerate((39, 58, 78, 97, 116, 135), 1)},
    **{f"row{i}_value": [107, y] for i, y in enumerate((39, 58, 78, 97, 116, 135), 1)},
}
STATUS_PANEL_FACTORY_DEFAULTS = {
    1: {
        "show": True, "x": 345, "y": 47, "width": 305, "height": 132, "font_size": 16,
        "field_order": {"switch": list(STATUS_PANEL_SWITCH_FIELDS)},
        "hidden_fields": {"switch": list(STATUS_PANEL_SWITCH_HIDDEN)},
        "fields": STATUS_PANEL_1_FIELD_DEFAULTS,
    },
    2: {
        "show": True, "x": 1605, "y": 20, "width": 278, "height": 55, "font_size": 16,
        "field_order": {"switch": ["vendor", "uptime"] + [
            field for field in STATUS_PANEL_SWITCH_FIELDS if field not in {"vendor", "uptime"}
        ]},
        "hidden_fields": {"switch": [
            field for field in STATUS_PANEL_SWITCH_FIELDS if field not in {"vendor", "uptime"}
        ]},
        "fields": STATUS_PANEL_FIELD_DEFAULTS,
    },
}


def _merged_factory_status_panel(raw_panel: object, panel_number: int) -> dict:
    defaults = json.loads(json.dumps(STATUS_PANEL_FACTORY_DEFAULTS[panel_number]))
    panel = raw_panel if isinstance(raw_panel, dict) else {}
    merged = {**defaults, **panel}
    merged_fields = {**defaults["fields"], **(panel.get("fields") if isinstance(panel.get("fields"), dict) else {})}
    merged_fields.pop("title", None)
    merged["fields"] = merged_fields

    raw_order = (panel.get("field_order") if isinstance(panel.get("field_order"), dict) else {}).get("switch")
    order: list[str] = []
    seen: set[str] = set()
    for field in raw_order if isinstance(raw_order, list) else defaults["field_order"]["switch"]:
        field = str(field).strip().lower()
        if field in STATUS_PANEL_SWITCH_FIELDS and field not in seen:
            order.append(field)
            seen.add(field)
    for field in STATUS_PANEL_SWITCH_FIELDS:
        if field not in seen:
            order.append(field)
    merged["field_order"] = {**defaults["field_order"], **(panel.get("field_order") if isinstance(panel.get("field_order"), dict) else {})}
    merged["field_order"]["switch"] = order

    raw_hidden = (panel.get("hidden_fields") if isinstance(panel.get("hidden_fields"), dict) else {}).get("switch")
    hidden_source = raw_hidden if isinstance(raw_hidden, list) else defaults["hidden_fields"]["switch"]
    hidden: list[str] = []
    for field in hidden_source:
        field = str(field).strip().lower()
        if field in STATUS_PANEL_SWITCH_FIELDS and field not in hidden:
            hidden.append(field)
    merged["hidden_fields"] = {**defaults["hidden_fields"], **(panel.get("hidden_fields") if isinstance(panel.get("hidden_fields"), dict) else {})}
    merged["hidden_fields"]["switch"] = hidden
    return merged


def _factory_status_display_position(panel: dict, key: str, panel_number: int) -> tuple[float, float]:
    fallback = STATUS_PANEL_FIELD_DEFAULTS.get(key, [24, 55])
    reference = STATUS_PANEL_1_FIELD_DEFAULTS.get(key, fallback) if panel_number == 1 else fallback
    saved = panel.get("fields", {}).get(key, reference)
    match = re.fullmatch(r"row(\d+)_(key|value)", key)
    if not match:
        return float(panel["x"]) + float(saved[0]), float(panel["y"]) + float(saved[1])

    row_index = max(0, int(match.group(1)) - 1)
    kind = match.group(2)
    font_size = max(8.0, float(panel.get("font_size") or 16))
    row_spacing = max(17.0, font_size + 2.0)
    horizontal_shift = 15.0 if panel_number == 2 else 5.0
    panel_left = float(panel["x"]) + 4.0
    panel_right = float(panel["x"]) + float(panel["width"]) - 4.0
    default_label_x = max(
        panel_left + 4.0,
        min(panel_right - 96.0, float(panel["x"]) + float(fallback[0]) - horizontal_shift),
    )
    default_value_x = min(panel_right - 24.0, default_label_x + 33.0)
    default_x = default_label_x if kind == "key" else default_value_x
    x = default_x + (float(saved[0]) - float(reference[0]))
    compact_baseline = float(panel["y"]) + 4.0 + font_size + (row_index * row_spacing)
    y = compact_baseline + (float(saved[1]) - float(reference[1]))
    return x, y


def validate_factory_status_panel_bounds(base: Path, source_layout: bool = False) -> None:
    """Fail on clipped factory rows unless a profile explicitly opts into runtime suppression."""
    prefix = base / "src" if source_layout else base
    calibration_dir = prefix / "calibration"
    errors: list[str] = []

    for path in sorted(calibration_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        data = render_space_calibration(data)
        ui = data.get("ui") if isinstance(data, dict) else None
        ui = ui if isinstance(ui, dict) else {}

        for panel_number, panel_name in ((1, "status_panel"), (2, "status_panel_2")):
            panel = _merged_factory_status_panel(ui.get(panel_name), panel_number)
            if panel.get("show") is False:
                continue
            try:
                panel_left = float(panel["x"]) + 4.0
                panel_right = float(panel["x"]) + float(panel["width"]) - 4.0
                panel_top = float(panel["y"]) + 4.0
                panel_bottom = float(panel["y"]) + float(panel["height"]) - 4.0
                font_size = max(8.0, float(panel.get("font_size") or 16))
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"{path}: invalid {panel_name} geometry: {exc}")
                continue

            hidden = set(panel["hidden_fields"]["switch"])
            visible_fields = [field for field in panel["field_order"]["switch"] if field not in hidden]
            # The runtime currently exposes six calibrated switch-summary row targets.
            # Factory profiles must keep every enabled factory row within those targets.
            if len(visible_fields) > 6:
                errors.append(
                    f"{path}: {panel_name} enables {len(visible_fields)} switch rows but only 6 calibrated row targets exist"
                )
                continue

            for index, field in enumerate(visible_fields, 1):
                key_name = f"row{index}_key"
                value_name = f"row{index}_value"
                kx, ky = _factory_status_display_position(panel, key_name, panel_number)
                vx, vy = _factory_status_display_position(panel, value_name, panel_number)
                inside = (
                    panel_left <= kx <= panel_right
                    and panel_left <= vx <= panel_right
                    and (ky - (font_size * 0.7)) >= panel_top
                    and (ky + (font_size * 0.35)) <= panel_bottom
                    and (vy - (font_size * 0.7)) >= panel_top
                    and (vy + (font_size * 0.35)) <= panel_bottom
                )
                if not inside and panel.get("allow_out_of_bounds_rows") is not True:
                    errors.append(
                        f"{path}: {panel_name} row {index} ({field}) renders outside panel "
                        f"[key=({kx:.1f},{ky:.1f}), value=({vx:.1f},{vy:.1f}), "
                        f"bounds=({panel_left:.1f},{panel_top:.1f})-({panel_right:.1f},{panel_bottom:.1f})]"
                    )

    if errors:
        raise SystemExit("Factory status-panel bounds validation failed:\n- " + "\n- ".join(errors))


PRIMARY_FACTORY_START = "const calibration = "
PRIMARY_FACTORY_END = "\nconst calibration2960X24 = "
PRIMARY_FACTORY_GENERATED_BY = "__SWITCH_VISION_VERSION__"
PRIMARY_FACTORY_JS_GENERATED_BY = "`Switch Vision v${SV_VERSION}`"


def _normalise_primary_factory_calibration(data: dict) -> dict:
    normalized = json.loads(json.dumps(data))
    normalized["generated_by"] = PRIMARY_FACTORY_GENERATED_BY
    return normalized


def render_primary_factory_calibration(data: dict) -> str:
    normalized = _normalise_primary_factory_calibration(data)
    payload = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    payload = payload.replace(json.dumps(PRIMARY_FACTORY_GENERATED_BY), PRIMARY_FACTORY_JS_GENERATED_BY, 1)
    return PRIMARY_FACTORY_START + payload + ";"


def extract_primary_factory_calibration(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    start = text.find(PRIMARY_FACTORY_START)
    if start < 0:
        raise SystemExit(f"Primary factory calibration not found in {path}")
    payload_start = start + len(PRIMARY_FACTORY_START)
    end = text.find(PRIMARY_FACTORY_END, payload_start)
    if end < 0:
        raise SystemExit(f"Primary factory calibration end marker not found in {path}")
    payload = text[payload_start:end].strip()
    if not payload.endswith(";"):
        raise SystemExit(f"Primary factory calibration is malformed in {path}")
    payload = payload[:-1].strip().replace(
        PRIMARY_FACTORY_JS_GENERATED_BY,
        json.dumps(PRIMARY_FACTORY_GENERATED_BY),
        1,
    )
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Primary factory calibration is not valid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Primary factory calibration must be an object in {path}")
    return data


def sync_primary_factory_calibration() -> None:
    """Regenerate the main C3650 frontend calibration from authoritative c3650.json."""
    source = SRC / "calibration" / "c3650.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    canonical = SRC / "js" / "switch-vision.js"
    text = canonical.read_text(encoding="utf-8", errors="ignore")
    start = text.find(PRIMARY_FACTORY_START)
    if start < 0:
        raise SystemExit(f"Primary factory calibration not found in {canonical}")
    end = text.find(PRIMARY_FACTORY_END, start + len(PRIMARY_FACTORY_START))
    if end < 0:
        raise SystemExit(f"Primary factory calibration end marker not found in {canonical}")
    replacement = render_primary_factory_calibration(data)
    write_text_lf(canonical, text[:start] + replacement + text[end:])


def validate_primary_factory_calibration(base: Path, source_layout: bool = False) -> None:
    """Fail when the primary frontend C3650 factory calibration drifts from c3650.json."""
    prefix = base / "src" if source_layout else base
    source = prefix / "calibration" / "c3650.json"
    expected = _normalise_primary_factory_calibration(json.loads(source.read_text(encoding="utf-8")))
    errors: list[str] = []
    for path in (
        prefix / "js" / "switch-vision.js",
        prefix / "custom_components" / "switch_vision" / "switch-vision-card.js",
    ):
        if not path.exists():
            errors.append(f"missing card JavaScript source: {path}")
            continue
        actual = extract_primary_factory_calibration(path)
        if actual != expected:
            errors.append(f"{path}: embedded primary factory calibration is stale")
    if errors:
        raise SystemExit("Primary factory calibration validation failed:\n- " + "\n- ".join(errors))


def remove_historical_release_notes() -> None:
    """Keep version history in CHANGELOG.md instead of accumulated note files."""
    for docs_dir in (SRC / "docs",):
        if not docs_dir.exists():
            continue
        for path in docs_dir.iterdir():
            if path.is_file() and re.match(r"RELEASE_NOTES(?:_|\.|$)", path.name, re.I):
                path.unlink()


def ensure_required_sources() -> None:
    required = [
        SRC / "js" / "switch-vision.js",
        SRC / "css" / "switch-vision.css",
        SRC / "layouts" / "c3650.json",
        SRC / "calibration" / "c3650.json",
        SRC / "custom_components" / "switch_vision" / "manifest.json",
        SRC / "custom_components" / "switch_vision" / "switch-vision-panel.js",
        SRC / "custom_components" / "switch_vision" / "switch-vision-dashboard-strategy.js",
        SRC / "custom_components" / "switch_vision" / "switch-vision-card.js",
        SRC / "custom_components" / "switch_vision" / "switch-vision-iconset.js",
        SRC / "custom_components" / "switch_vision" / "brand" / "icon.png",
        SRC / "custom_components" / "switch_vision" / "brand" / "logo.png",
        SRC / "examples" / "README.md",
        SRC / "docs" / "REQUIREMENTS.md",
        SRC / "docs" / "INSTALLATION.md",
        SRC / "docs" / "FIELD_REFERENCE.md",
        SRC / "docs" / "UPGRADING.md",
        SRC / "devices" / "supported_devices.yaml",
        SRC / "devices" / "generate_supported_devices.py",
        SRC / "devices" / "supported_devices.json",
        ROOT / "RELEASE_NOTES.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "SECURITY.md",
    ]
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing required source files:\n- " + "\n- ".join(missing))


def copy_tree_files(source: Path, destination: Path) -> None:
    if not source.exists():
        return
    for path in sorted(source.rglob("*")):
        if "__pycache__" in path.parts or ".pytest_cache" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_file():
            output = destination / path.relative_to(source)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, output)


def replace_build_tokens(text: str, version: str) -> str:
    """Replace only explicit current-build tokens, never historical versions."""
    replacements = {
        "{{SWITCH_VISION_VERSION}}": version,
        "{{SWITCH_VISION_VERSION_V}}": f"v{version}",
        "{{SWITCH_VISION_RELEASE}}": f"{PROJECT_NAME}-{version}",
    }
    for token, value in replacements.items():
        text = text.replace(token, value)
    return text


def patch_js_version(path: Path, version: str) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    patterns = [
        (r'(const\s+SV_VERSION\s*=\s*["\'])[^"\']+(["\']\s*;)', rf'\g<1>{version}\g<2>'),
        (r'(const\s+CV_VERSION\s*=\s*["\'])[^"\']+(["\']\s*;)', rf'\g<1>{version}\g<2>'),
    ]
    for pattern, replacement in patterns:
        if re.search(pattern, text):
            text = re.sub(pattern, replacement, text, count=1)
            break
    else:
        text = f'const SV_VERSION = "{version}";\n' + text
    write_text_lf(path, text)



def patch_panel_runtime_versions(component_dir: Path, version: str) -> None:
    panel_js = component_dir / "switch-vision-panel.js"
    text = panel_js.read_text(encoding="utf-8", errors="ignore")
    text, panel_count = re.subn(
        r'const\s+PANEL_VERSION\s*=\s*["\'][^"\']+["\']\s*;',
        f'const PANEL_VERSION = "{version}";',
        text,
        count=1,
    )
    if panel_count == 0:
        raise SystemExit(f"Panel version constant not found in {panel_js}")
    write_text_lf(panel_js, text)

    strategy_js = component_dir / "switch-vision-dashboard-strategy.js"
    text = strategy_js.read_text(encoding="utf-8", errors="ignore")
    text, strategy_count = re.subn(
        r'const\s+SWITCH_VISION_DASHBOARD_VERSION\s*=\s*["\'][^"\']+["\']\s*;',
        f'const SWITCH_VISION_DASHBOARD_VERSION = "{version}";',
        text,
        count=1,
    )
    if strategy_count == 0:
        raise SystemExit(f"Dashboard strategy version constant not found in {strategy_js}")
    write_text_lf(strategy_js, text)

    init_py = component_dir / "__init__.py"
    text = init_py.read_text(encoding="utf-8", errors="ignore")
    text, backend_count = re.subn(
        r'PANEL_VERSION\s*=\s*["\'][^"\']+["\']',
        f'PANEL_VERSION = "{version}"',
        text,
        count=1,
    )
    if backend_count == 0:
        raise SystemExit(f"Backend panel version constant not found in {init_py}")
    write_text_lf(init_py, text)

def patch_json_version(path: Path, version: str) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data["version"] = version
        if path.name == "manifest.json" and path.parent == SRC:
            data["resource"] = f"/local/switch-vision/js/switch-vision.js?v={version}"
            data["release_name"] = f"{PROJECT_NAME}-{version}"
    write_text_lf(path, json.dumps(data, indent=2) + "\n")


def patch_text_file(path: Path, version: str) -> None:
    """Patch explicit build tokens without rewriting release history."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    write_text_lf(path, replace_build_tokens(text, version))


def patch_current_release_metadata(version: str) -> None:
    """Update only current-release labels in authoritative documentation."""
    readme = ROOT / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8", errors="ignore")
        text, count = re.subn(
            r"(?m)^### Switch Vision v\d+\.\d+\.\d+$",
            f"### Switch Vision v{version}",
            text,
            count=1,
        )
        if count == 0:
            raise SystemExit("README current-release heading not found")

        text, count = re.subn(
            r"(?m)^\*\*v\d+\.\d+\.\d+\*\* is the current tested public Switch Vision Core/dashboard release\.$",
            f"**v{version}** is the current tested public Switch Vision Core/dashboard release.",
            text,
            count=1,
        )
        if count == 0:
            raise SystemExit("README current-release description not found")
        text = re.sub(
            r"No dashboard YAML copying is required for the normal v\d+\.\d+\.\d+ workflow\.",
            f"No dashboard YAML copying is required for the normal v{version} workflow.",
            text,
            count=1,
        )
        text = re.sub(
            r"/local/switch-vision/js/switch-vision\.js\?v=\d+\.\d+\.\d+",
            f"/local/switch-vision/js/switch-vision.js?v={version}",
            text,
        )
        write_text_lf(readme, text)

def sync_authoritative_documents() -> None:
    """Keep duplicate source-document copies byte-identical."""
    for filename in ("README.md", "CHANGELOG.md", "RELEASE_NOTES.md"):
        source = ROOT / filename
        destination = SRC / filename
        if source.exists():
            shutil.copy2(source, destination)












def sync_device_visual_recommendations() -> None:
    """Regenerate exact-model visual/API mapping metadata from the registry."""
    registry_path = SRC / "devices" / "supported_devices.yaml"
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    devices = data.get("devices", []) if isinstance(data, dict) else []
    recommendations = []
    for device in devices if isinstance(devices, list) else []:
        if not isinstance(device, dict):
            continue
        visuals = device.get("visuals") if isinstance(device.get("visuals"), dict) else {}
        ports = device.get("ports") if isinstance(device.get("ports"), dict) else {}
        faceplate = visuals.get("recommended_faceplate") or ""
        profile = visuals.get("calibration_profile") or ""
        api_port_map = device.get("unifi_api_port_map")
        has_api_port_map = isinstance(api_port_map, dict)
        if not (faceplate and profile) and not has_api_port_map:
            continue
        item = {
            "model": device.get("model"),
            "status": device.get("status"),
            "family": device.get("family"),
            "rj45": ports.get("rj45"),
            "uplinks": ports.get("uplinks"),
            "visual_status": visuals.get("status"),
            "faceplate": faceplate,
            "optional_faceplates": visuals.get("optional_faceplates") or [],
            "profile": profile,
            "canvas": visuals.get("canvas"),
        }
        if has_api_port_map:
            item["unifi_api_port_map"] = api_port_map
        recommendations.append(item)
    canonical = SRC / "js" / "switch-vision.js"
    text = canonical.read_text(encoding="utf-8", errors="ignore")
    replacement = "const SV_DEVICE_VISUAL_RECOMMENDATIONS = " + json.dumps(
        recommendations, ensure_ascii=False, separators=(",", ":")
    ) + ";"
    updated, count = re.subn(
        r"const SV_DEVICE_VISUAL_RECOMMENDATIONS = \[.*?\];",
        replacement,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("Could not synchronize device visual recommendations")
    write_text_lf(canonical, updated)



def validate_unifi_main_runtime(base: Path, source_layout: bool = False) -> None:
    """Validate UniFi data consumption owned by the main Switch Vision runtime."""
    prefix = base / "src" if source_layout else base
    component = prefix / "custom_components" / "switch_vision"
    backend = (component / "__init__.py").read_text(encoding="utf-8", errors="ignore")
    card_js = (prefix / "js" / "switch-vision.js").read_text(encoding="utf-8", errors="ignore")
    registry = json.loads((prefix / "devices" / "supported_devices.json").read_text(encoding="utf-8"))

    required_backend = [
        'switch_vision/get_unifi_device',
        'UNIFI_DEVICES_PATH = Path("/share/switch_vision/unifi/devices.json")',
    ]
    required_card = [
        'data_source: "home_assistant"',
        'maybeLoadUnifiDevice',
        'unifi_per_port_traffic',
        'configuredPortCountAllows(config, "sfp_port_count", sfpPort)',
        'configuredPortCountAllows(config, "port_count", n)',
        'const unifi = unifiSfpPort(config, port)',
        'const liveSfpSpeed = sfpSpeedMbps(hass, config, sfpPort)',
    ]
    missing = [marker for marker in required_backend if marker not in backend]
    missing.extend(marker for marker in required_card if marker not in card_js)
    if missing:
        raise SystemExit("UniFi main-runtime validation failed: missing " + ", ".join(missing))

    count_match = re.search(
        r"function configuredPortCountAllows\(config, field, port\) \{.*?\n\}",
        card_js,
        re.S,
    )
    if not count_match:
        raise SystemExit("UniFi/card geometry validation failed: configuredPortCountAllows function missing")
    count_test = f"""
{count_match.group(0)}
function check(value, expected, label) {{ if (value !== expected) throw new Error(label + ': ' + value); }}
check(configuredPortCountAllows({{__raw_config: {{}} , port_count: 0}}, 'port_count', 1), true, 'omitted raw count');
check(configuredPortCountAllows({{__raw_config: {{port_count: 0}}, port_count: 0}}, 'port_count', 1), false, 'explicit zero');
check(configuredPortCountAllows({{__raw_config: {{port_count: 8}}, port_count: 8}}, 'port_count', 8), true, 'exact upper bound');
check(configuredPortCountAllows({{__raw_config: {{port_count: 8}}, port_count: 8}}, 'port_count', 9), false, 'above upper bound');
"""
    result = subprocess.run(["node", "-e", count_test], text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(
            "UniFi/card geometry semantics validation failed:\n"
            + (result.stdout + result.stderr).strip()
        )

    devices = {
        str(item.get("model")): item
        for item in registry.get("devices", [])
        if isinstance(item, dict)
    }
    for model in ("USW Lite 16 PoE", "UDM Pro", "USW-Enterprise-8-PoE", "USW Pro XG 8 PoE"):
        item = devices.get(model)
        if not item:
            raise SystemExit(f"UniFi support validation failed: {model} missing from registry")
        if item.get("dashboard_support") is not True:
            raise SystemExit(
                f"UniFi support validation failed: {model} dashboard_support is not enabled"
            )


def patch_source_versions(version: str) -> None:
    """Synchronise every authoritative source version before packaging."""
    patch_current_release_metadata(version)
    sync_authoritative_documents()
    validate_factory_calibration_privacy(PROJECT_ROOT, source_layout=True)
    normalize_faceplate_factory_calibrations(SRC / "calibration", SRC / "faceplates")
    validate_factory_status_panel_bounds(PROJECT_ROOT, source_layout=True)
    sync_primary_factory_calibration()
    sync_faceplate_factory_calibrations()
    sync_device_visual_recommendations()
    patch_js_version(SRC / "js" / "switch-vision.js", version)
    shutil.copy2(SRC / "js" / "switch-vision.js", SRC / "custom_components" / "switch_vision" / "switch-vision-card.js")
    patch_js_version(SRC / "custom_components" / "switch_vision" / "switch-vision-card.js", version)
    patch_json_version(SRC / "custom_components" / "switch_vision" / "manifest.json", version)
    patch_panel_runtime_versions(SRC / "custom_components" / "switch_vision", version)
    patch_json_version(SRC / "manifest.json", version)
    rename_versioned_examples(SRC / "examples", version)
    write_text_lf(VERSION_FILE, version + "\n")


def validate_dashboard_strategy_resource_wiring(base: Path, source_layout: bool = False) -> None:
    """Verify the backend registers the community strategy as a Lovelace resource."""
    prefix = base / "src" if source_layout else base
    component = prefix / "custom_components" / "switch_vision"
    init_py = (component / "__init__.py").read_text(encoding="utf-8", errors="ignore")
    manifest = json.loads((component / "manifest.json").read_text(encoding="utf-8"))
    required = [
        "_ensure_dashboard_strategy_lovelace_resource",
        "LOVELACE_DATA",
        "MODE_STORAGE",
        "CONF_RESOURCE_TYPE_WS",
        "async_create_item",
        "async_update_item",
        'CONF_RESOURCE_TYPE_WS: "module"',
        "DASHBOARD_STRATEGY_JS_URL",
    ]
    missing = [token for token in required if token not in init_py]
    if missing:
        raise SystemExit(
            "Dashboard strategy resource wiring validation failed: missing " + ", ".join(missing)
        )
    if "lovelace" not in manifest.get("dependencies", []):
        raise SystemExit("Dashboard strategy resource wiring validation failed: lovelace dependency missing")



def validate_dashboard_sidebar_controls(base: Path, source_layout: bool = False) -> None:
    """Verify Native and Lovelace sidebar controls remain independent."""
    prefix = base / "src" if source_layout else base
    component = prefix / "custom_components" / "switch_vision"
    init_py = (component / "__init__.py").read_text(encoding="utf-8", errors="ignore")
    config_flow = (component / "config_flow.py").read_text(encoding="utf-8", errors="ignore")
    strings = json.loads((component / "strings.json").read_text(encoding="utf-8"))

    required_init = [
        'CONF_SHOW_PANEL_IN_SIDEBAR = "show_panel_in_sidebar"',
        'CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR = "show_lovelace_dashboard_in_sidebar"',
        "_sync_switch_vision_lovelace_dashboard_sidebar",
        "_is_switch_vision_lovelace_strategy",
        '"custom:switch-vision"',
        "DashboardsCollection",
        "EVENT_LOVELACE_UPDATED",
        "frontend.async_register_built_in_panel",
    ]
    missing = [token for token in required_init if token not in init_py]
    if missing:
        raise SystemExit(
            "Dashboard sidebar control validation failed: missing " + ", ".join(missing)
        )

    for token in (
        "CONF_SHOW_PANEL_IN_SIDEBAR",
        "CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR",
    ):
        if token not in config_flow:
            raise SystemExit(
                f"Dashboard sidebar control validation failed: {token} missing from config flow"
            )

    # Presentation-only options must never reload the whole config entry. A
    # reload removes/re-registers the Native panel and can disturb unrelated
    # ingress/sidebar entries (notably Switch Vision Installer).
    if "OptionsFlowWithReload" in config_flow:
        raise SystemExit(
            "Dashboard sidebar control validation failed: presentation options still reload the integration"
        )
    for token in (
        "class SwitchVisionOptionsFlow(OptionsFlow)",
        "entry.add_update_listener(_async_entry_options_updated)",
        "await _apply_entry_options(hass, entry)",
    ):
        if token not in (config_flow + "\n" + init_py):
            raise SystemExit(
                f"Dashboard sidebar control validation failed: live option token missing: {token}"
            )

    setup_start = init_py.find("async def async_setup_entry")
    unload_start = init_py.find("async def async_unload_entry", setup_start)
    setup_block = init_py[setup_start:unload_start]
    if "async_remove_panel(hass, PANEL_URL_PATH)" in setup_block:
        raise SystemExit(
            "Dashboard sidebar control validation failed: setup/update path still removes the Native panel"
        )

    option_step = strings["options"]["step"]["init"]
    option_strings = option_step.get("data", {})
    sections = option_step.get("sections", {})
    dashboard_strings = sections.get("dashboard", {}).get("data", {})
    sidebar_strings = sections.get("sidebar", {}).get("data", {})
    combined_option_strings = {**option_strings, **dashboard_strings, **sidebar_strings}
    if (
        "show_panel_in_sidebar" not in combined_option_strings
        or "show_lovelace_dashboard_in_sidebar" not in combined_option_strings
    ):
        raise SystemExit("Dashboard sidebar control validation failed: option strings incomplete")

def validate_dashboard_strategy_registration(base: Path, source_layout: bool = False) -> None:
    """Execute the dashboard strategy bootstrap and verify both HA strategy tags register."""
    prefix = base / "src" if source_layout else base
    strategy = prefix / "custom_components" / "switch_vision" / "switch-vision-dashboard-strategy.js"
    if not strategy.exists():
        raise SystemExit(f"Dashboard strategy registration validation failed: missing {strategy}")
    harness = r"""
const fs = require('fs');
const vm = require('vm');
class HTMLElement {}
const registry = new Map();
const customElements = {
  get(name) { return registry.get(name); },
  define(name, ctor) {
    if (registry.has(name)) throw new Error(`duplicate element ${name}`);
    for (const existing of registry.values()) {
      if (existing === ctor) throw new Error(`constructor reused for ${name}`);
    }
    registry.set(name, ctor);
  },
};
const window = { customStrategies: [] };
const context = {
  HTMLElement,
  customElements,
  window,
  console: { info() {}, warn() {}, error() {}, log() {} },
  document: {},
  encodeURIComponent,
};
vm.createContext(context);
const source = fs.readFileSync(process.argv[1], 'utf8');
vm.runInContext(source, context, { filename: process.argv[1] });
for (const tag of ['ll-strategy-dashboard-switch-vision', 'll-strategy-switch-vision']) {
  if (!registry.has(tag)) throw new Error(`missing ${tag}`);
}
const meta = window.customStrategies.find(
  (item) => item && item.type === 'switch-vision' && item.strategyType === 'dashboard'
);
if (!meta) throw new Error('missing Switch Vision customStrategies metadata');
// Re-evaluate to prove duplicate frontend/resource loads are safe.
vm.runInContext(source, context, { filename: process.argv[1] });
if (window.customStrategies.filter((item) => item && item.type === 'switch-vision').length !== 1) {
  throw new Error('duplicate Switch Vision customStrategies metadata');
}
"""
    result = subprocess.run(
        ["node", "-e", harness, str(strategy)],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        message = (result.stdout + result.stderr).strip()
        raise SystemExit("Dashboard strategy registration validation failed:\n" + message)


def validate_card_source_sync(base: Path, source_layout: bool = False) -> None:
    prefix = base / "src" if source_layout else base
    canonical = prefix / "js" / "switch-vision.js"
    component = prefix / "custom_components" / "switch_vision" / "switch-vision-card.js"
    if not canonical.exists() or not component.exists():
        raise SystemExit("Card-source validation failed: required JavaScript source is missing")
    if canonical.read_bytes() != component.read_bytes():
        raise SystemExit(
            "Card-source validation failed: switch-vision-card.js differs from the canonical "
            "src/js/switch-vision.js source"
        )


def validate_source_manifest(base: Path, version: str, source_layout: bool = False) -> None:
    prefix = base / "src" if source_layout else base
    manifest_path = prefix / "manifest.json"
    if not manifest_path.exists():
        return
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {
        "version": version,
        "resource": f"/local/switch-vision/js/switch-vision.js?v={version}",
        "release_name": f"{PROJECT_NAME}-{version}",
    }
    errors = [f"{key}={data.get(key)!r}, expected {value!r}" for key, value in expected.items() if data.get(key) != value]
    if errors:
        raise SystemExit("Manifest metadata validation failed:\n- " + "\n- ".join(errors))


def run_maintenance_tests() -> None:
    tests_dir = PROJECT_ROOT / "tests"
    if not tests_dir.exists():
        return
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir), "-p", "test_*.py"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        message = result.stdout + result.stderr
        raise SystemExit("Maintenance tests failed:\n" + message.strip())
    if result.stdout.strip() or result.stderr.strip():
        print((result.stdout + result.stderr).strip())










def validate_device_visual_recommendations(base: Path, source_layout: bool = False) -> None:
    prefix = base / "src" if source_layout else base
    registry_path = prefix / "devices" / "supported_devices.json"
    js_path = prefix / "js" / "switch-vision.js"
    if not registry_path.exists() or not js_path.exists():
        raise SystemExit("Device visual validation failed: registry or canonical JavaScript is missing")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    devices = {str(item.get("model")): item for item in registry.get("devices", []) if isinstance(item, dict)}
    text = js_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"const SV_DEVICE_VISUAL_RECOMMENDATIONS = (\[.*?\]);", text, re.S)
    if not match:
        raise SystemExit("Device visual validation failed: embedded recommendation table is missing")
    try:
        recommendations = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Device visual validation failed: invalid embedded JSON: {exc}") from exc
    errors = []
    for item in recommendations:
        if not isinstance(item, dict):
            errors.append("embedded recommendation is not an object")
            continue
        model = str(item.get("model") or "")
        device = devices.get(model)
        if device is None:
            errors.append(f"{model}: no authoritative registry entry")
            continue
        visuals = device.get("visuals") if isinstance(device.get("visuals"), dict) else {}
        ports = device.get("ports") if isinstance(device.get("ports"), dict) else {}
        expected = {
            "status": device.get("status"),
            "family": device.get("family"),
            "rj45": ports.get("rj45"),
            "uplinks": ports.get("uplinks"),
            "visual_status": visuals.get("status"),
            "faceplate": visuals.get("recommended_faceplate"),
            "optional_faceplates": visuals.get("optional_faceplates") or [],
            "profile": visuals.get("calibration_profile"),
            "canvas": visuals.get("canvas"),
            "unifi_api_port_map": device.get("unifi_api_port_map"),
        }
        for key, value in expected.items():
            if item.get(key) != value:
                errors.append(f"{model}: {key}={item.get(key)!r}, expected {value!r}")
    # Registry-authoritative visual policy:
    # exact-model visual/profile choices are evidence owned by the device
    # registry. Do not derive them from vendor or coarse port counts here.
    # This is essential for UniFi hardware whose exact models range from
    # compact 5/8-port devices through 48-port switches.
    compact_8x2_visual_models = {"WS-C3560CG-8PC-S", "XS1930-10"}
    profile_faceplate_pairs = {
        "stock_24rj45_2sfp": "faceplates/24rj45-2sfp.png",
        "stock_24rj45_4sfp": "faceplates/24rj45-4sfp.png",
        "stock_48rj45_2sfp": "faceplates/48rj45-2sfp.png",
        "stock_48rj45_4sfp": "faceplates/48rj45-4sfp.png",
        "unifi_24p_rj45_2sfp": "faceplates/unifi-24p-rj45-2sfp.png",
    }

    for model, device in devices.items():
        visuals = device.get("visuals") if isinstance(device.get("visuals"), dict) else {}
        expected_profile = str(device.get("calibration_profile") or "").strip()
        expected_faceplate = str(device.get("default_faceplate") or "").strip()

        dashboard_supported = device.get("dashboard_support") is True
        api_port_map = device.get("unifi_api_port_map")
        has_api_port_map = isinstance(api_port_map, dict)
        has_visual = bool(expected_profile and expected_faceplate)

        if dashboard_supported and not has_visual:
            errors.append(f"{model}: dashboard_support requires a calibration profile and faceplate")
        if bool(expected_profile) != bool(expected_faceplate):
            errors.append(f"{model}: calibration profile and faceplate must either both be set or both be pending")

        paired_faceplate = profile_faceplate_pairs.get(expected_profile)
        if paired_faceplate and expected_faceplate != paired_faceplate:
            errors.append(
                f"{model}: profile {expected_profile!r} must use {paired_faceplate!r}, "
                f"not {expected_faceplate!r}"
            )

        if visuals.get("calibration_profile") != expected_profile:
            errors.append(
                f"{model}: visuals.calibration_profile={visuals.get('calibration_profile')!r}, "
                f"expected registry calibration_profile {expected_profile!r}"
            )
        if visuals.get("recommended_faceplate") != expected_faceplate:
            errors.append(
                f"{model}: visuals.recommended_faceplate={visuals.get('recommended_faceplate')!r}, "
                f"expected registry default_faceplate {expected_faceplate!r}"
            )

        item = next(
            (row for row in recommendations if row.get("model") == model),
            None,
        )
        if has_visual or has_api_port_map:
            if item is None:
                errors.append(f"{model}: embedded model recommendation is missing")
                continue
            if item.get("profile") != expected_profile:
                errors.append(
                    f"{model}: embedded profile={item.get('profile')!r}, "
                    f"expected {expected_profile!r}"
                )
            if item.get("faceplate") != expected_faceplate:
                errors.append(
                    f"{model}: embedded faceplate={item.get('faceplate')!r}, "
                    f"expected {expected_faceplate!r}"
                )
            if item.get("unifi_api_port_map") != (api_port_map if has_api_port_map else None):
                errors.append(
                    f"{model}: embedded UniFi API-port map differs from registry"
                )
        elif item is not None:
            errors.append(f"{model}: unexpected embedded recommendation without a visual or API-port map")

        if item is not None and model not in compact_8x2_visual_models:
            if item.get("profile") == "cisco_3560cg_8pc":
                errors.append(f"{model}: compact 8+2 calibration leaked into an unapproved exact model")
            if item.get("faceplate") == "faceplates/c3560cg-8pc-s.png":
                errors.append(f"{model}: compact 8+2 faceplate leaked into an unapproved exact model")

    if errors:
        raise SystemExit("Device visual recommendation validation failed:\n- " + "\n- ".join(errors))




def validate_status_panel_field_registry(base: Path, source_layout: bool = False) -> None:
    """Keep retired Status Box rows out while preserving their telemetry plumbing."""
    prefix = base / "src" if source_layout else base
    js_path = prefix / "js" / "switch-vision.js"
    text = js_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"const STATUS_PANEL_ROW_DEFS = \{(.*?)\n\};", text, re.S)
    if not match:
        raise SystemExit("Status Box field validation failed: STATUS_PANEL_ROW_DEFS is missing")
    registry = match.group(1)
    forbidden = ['"memory"', '"uplink_rx"', '"uplink_tx"', '"MEM"', '"UP RX"', '"UP TX"']
    present = [token for token in forbidden if token in registry]
    if present:
        raise SystemExit(
            "Status Box field validation failed: retired switch fields remain: " + ", ".join(present)
        )
    # Underlying telemetry remains intentionally supported outside the Status Box selector.
    telemetry_markers = [
        "system.memory_utilization_pct",
        "system.uplink_rx_rate_bps",
        "system.uplink_tx_rate_bps",
        '`sensor.${m}_memory`',
    ]
    missing = [marker for marker in telemetry_markers if marker not in text]
    if missing:
        raise SystemExit(
            "Status Box field validation failed: telemetry plumbing was removed: " + ", ".join(missing)
        )



def validate_faceplate_profile_isolation(base: Path, source_layout: bool = False) -> None:
    """Prevent whole-calibration mirroring and faceplate Status Box cross-taint."""
    prefix = base / "src" if source_layout else base
    js_text = (prefix / "js" / "switch-vision.js").read_text(encoding="utf-8", errors="ignore")
    backend = (prefix / "custom_components" / "switch_vision" / "__init__.py").read_text(encoding="utf-8", errors="ignore")

    required_backend = [
        'data.setdefault("active_profiles", {})',
        '_migrate_legacy_faceplate_mirrors',
        'active_profiles[base_profile] = profile',
        '"active_profile": active_profile',
    ]
    missing = [marker for marker in required_backend if marker not in backend]
    if missing:
        raise SystemExit(
            "Faceplate isolation validation failed: active-profile pointer plumbing is missing: " + ", ".join(missing)
        )

    forbidden_backend = [
        'base_calibration = dict(calibration)',
        'profiles[base_profile] = base_calibration',
    ]
    present = [marker for marker in forbidden_backend if marker in backend]
    if present:
        raise SystemExit(
            "Faceplate isolation validation failed: whole-calibration base mirroring remains: " + ", ".join(present)
        )

    required_js = [
        'const resolvedProfile = String(result?.profile || profile)',
        'const modelStarter = this.factoryCalibrationForCurrentSwitch({',
        'mirror_to_base: scopedProfile && profile !== baseProfile',
    ]
    missing_js = [marker for marker in required_js if marker not in js_text]
    if missing_js:
        raise SystemExit(
            "Faceplate isolation validation failed: frontend isolation plumbing is missing: " + ", ".join(missing_js)
        )

    forbidden_js = 'cloneCalibrationData(cal);\n        ensureCalibrationUi(starter).ui.faceplate'
    if forbidden_js in js_text:
        raise SystemExit(
            "Faceplate isolation validation failed: new faceplates still inherit the current faceplate calibration"
        )

def validate_activity_led_2_0(base: Path, source_layout: bool = False) -> None:
    """Guard the v2.2 Activity LED settings and integration-wide wiring."""
    prefix = base / "src" if source_layout else base
    js_text = (prefix / "js" / "switch-vision.js").read_text(encoding="utf-8", errors="ignore")
    component = prefix / "custom_components" / "switch_vision"
    backend = (component / "__init__.py").read_text(encoding="utf-8", errors="ignore")
    config_flow = (component / "config_flow.py").read_text(encoding="utf-8", errors="ignore")
    strings = (component / "strings.json").read_text(encoding="utf-8", errors="ignore")

    required_js = [
        'const SV_ACTIVITY_LED_PRESETS = Object.freeze({',
        'normal: Object.freeze({ mediumStartsPct: 0.10, fastStartsPct: 1.0 })',
        'function activityThresholds(config = {})',
        'function activityLevel(utilization, config = {}, previousLevel = 0)',
        'activity_hysteresis_pct ?? 20',
        'activity_slow_period_ms ?? 500',
        'activity_medium_period_ms ?? 250',
        'activity_fast_period_ms ?? 120',
        'activity_led_sensitivity_preset: "normal"',
        'activity_hold_seconds: 12',
        'activityConfigFromGlobalSettings',
        'cacheSwitchVisionGlobalUiSettings',
        '...(this._globalActivitySettings || {})',
    ]
    missing = [marker for marker in required_js if marker not in js_text]
    if missing:
        raise SystemExit(
            "Activity LED 2.0 validation failed: frontend wiring is missing: " + ", ".join(missing)
        )

    forbidden_js = [
        'activity_slow_period_ms ?? 750',
        'activity_medium_period_ms ?? 350',
        'activity_fast_period_ms ?? 180',
        'activity_slow_max_utilization_pct ?? 1)) / 100',
        'activity_medium_max_utilization_pct ?? 20)) / 100',
    ]
    present = [marker for marker in forbidden_js if marker in js_text]
    if present:
        raise SystemExit(
            "Activity LED 2.0 validation failed: legacy hard-coded tuning remains: " + ", ".join(present)
        )

    required_backend = [
        'CONF_ACTIVITY_LED_SENSITIVITY_PRESET = "activity_led_sensitivity_preset"',
        'CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT = "activity_slow_max_utilization_pct"',
        'CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT = "activity_medium_max_utilization_pct"',
        'CONF_ACTIVITY_HYSTERESIS_PCT = "activity_hysteresis_pct"',
        'CONF_ACTIVITY_HOLD_SECONDS = "activity_hold_seconds"',
        '"normal": {"slow_max_utilization_pct": 0.10, "medium_max_utilization_pct": 1.0}',
        'CONF_ACTIVITY_SLOW_PERIOD_MS: 500',
        'CONF_ACTIVITY_MEDIUM_PERIOD_MS: 250',
        'CONF_ACTIVITY_FAST_PERIOD_MS: 120',
        'DATA_ACTIVITY_LED_SETTINGS = "activity_led_settings"',
        '"activity_leds": activity_led_settings',
        '"activity_leds": _activity_led_settings(entry)',
    ]
    missing_backend = [marker for marker in required_backend if marker not in backend]
    if missing_backend:
        raise SystemExit(
            "Activity LED 2.0 validation failed: backend settings wiring is missing: "
            + ", ".join(missing_backend)
        )

    required_flow = [
        'vol.Required("activity_leds"): section(',
        'CONF_RESET_TO_DEFAULTS = "reset_to_defaults"',
        'if user_input.get(CONF_RESET_TO_DEFAULTS):',
        'return self.async_create_entry(data=dict(DEFAULT_OPTIONS))',
        'errors["base"] = "invalid_activity_thresholds"',
        'errors["base"] = "invalid_activity_periods"',
    ]
    missing_flow = [marker for marker in required_flow if marker not in config_flow]
    if missing_flow:
        raise SystemExit(
            "Activity LED 2.0 validation failed: options flow wiring is missing: " + ", ".join(missing_flow)
        )

    required_strings = [
        '"name": "Activity LEDs"',
        '"Sensitivity preset"',
        '"Reset all Switch Vision Core settings to defaults"',
    ]
    missing_strings = [marker for marker in required_strings if marker not in strings]
    if missing_strings:
        raise SystemExit(
            "Activity LED 2.0 validation failed: option translations are missing: " + ", ".join(missing_strings)
        )


def validate_embedded_versions(base: Path, version: str, source_layout: bool = False) -> None:
    prefix = base / "src" if source_layout else base
    checks = {
        prefix / "custom_components" / "switch_vision" / "manifest.json": f'"version": "{version}"',
        prefix / "custom_components" / "switch_vision" / "__init__.py": f'PANEL_VERSION = "{version}"',
        prefix / "custom_components" / "switch_vision" / "switch-vision-panel.js": f'const PANEL_VERSION = "{version}";',
        prefix / "custom_components" / "switch_vision" / "switch-vision-dashboard-strategy.js": f'const SWITCH_VISION_DASHBOARD_VERSION = "{version}";',
        prefix / "js" / "switch-vision.js": f'const SV_VERSION = "{version}";',
    }
    errors = []
    for path, marker in checks.items():
        if not path.exists() or marker not in path.read_text(encoding="utf-8", errors="ignore"):
            errors.append(f"{path}: missing {marker}")
    if source_layout:
        root_version = (base / "VERSION").read_text(encoding="utf-8").strip() if (base / "VERSION").exists() else "missing"
        if root_version != version:
            errors.append(f"VERSION is {root_version}, expected {version}")
    validate_card_source_sync(base, source_layout=source_layout)
    validate_factory_calibration_privacy(base, source_layout=source_layout)
    validate_factory_status_panel_bounds(base, source_layout=source_layout)
    validate_primary_factory_calibration(base, source_layout=source_layout)
    validate_faceplate_factory_calibrations(base, source_layout=source_layout)
    validate_discovery_example_version_independence(base, source_layout=source_layout)
    validate_generated_dashboard_safety(base, source_layout=source_layout)
    validate_device_visual_recommendations(base, source_layout=source_layout)
    validate_unifi_main_runtime(base, source_layout=source_layout)
    validate_status_panel_field_registry(base, source_layout=source_layout)
    validate_faceplate_profile_isolation(base, source_layout=source_layout)
    validate_activity_led_2_0(base, source_layout=source_layout)
    validate_source_manifest(base, version, source_layout=source_layout)
    if errors:
        raise SystemExit("Version propagation validation failed:\n- " + "\n- ".join(errors))


def validate_release_sources(release_dir: Path, version: str, gold: bool = False) -> None:
    if (release_dir / "local_apps").exists():
        raise SystemExit("Release validation failed: repository-managed local app source was bundled")

    card_js = (release_dir / "js" / "switch-vision.js").read_text(encoding="utf-8", errors="ignore")
    generated_examples = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in (release_dir / "examples").glob("*.yaml")
    )
    forbidden_last_change = [
        "last_change_entity_prefix",
        "last_change_entity_suffix",
        "_last_change",
    ]
    for forbidden in forbidden_last_change:
        if forbidden in card_js or forbidden in generated_examples:
            raise SystemExit(f"Release validation failed: obsolete last-change dependency remains: {forbidden}")
    if 'portByteEntity(config, port, "rx")' not in card_js or 'portByteEntity(config, port, "tx")' not in card_js:
        raise SystemExit("Release validation failed: counter-derived port activity is missing")

    compact_header_forbidden = [
        'cv-cal-workspace-title',
        'cv-cal-state-badge',
        'cv-cal-profile-path',
        'cv-cal-profile-scope',
        '>Editing profile<',
    ]
    for forbidden in compact_header_forbidden:
        if forbidden in card_js:
            raise SystemExit(f"Release validation failed: obsolete calibration-header element remains: {forbidden}")
    for required_label in ['<small>Switch</small>', '<small>Model</small>', '<small>Faceplate</small>', '<small>Profile</small>']:
        if required_label not in card_js:
            raise SystemExit(f"Release validation failed: compact calibration-header label missing: {required_label}")

    for forbidden in ["faceplate_label", "member_faceplate(", "parent_faceplate("]:
        if forbidden in card_js:
            raise SystemExit(f"Release validation failed: removed faceplate-label system remains: {forbidden}")

    component_manifest = json.loads(
        (release_dir / "custom_components" / "switch_vision" / "manifest.json").read_text(encoding="utf-8")
    )
    if component_manifest.get("documentation") != "https://switch-vision.zemerdon.com":
        raise SystemExit("Release validation failed: public integration documentation URL is incorrect")
    if component_manifest.get("issue_tracker") != "https://github.com/zemerdon/switch-vision-releases/issues":
        raise SystemExit("Release validation failed: public integration issue tracker is incorrect")
    if "@zemerdon" not in component_manifest.get("codeowners", []):
        raise SystemExit("Release validation failed: public integration codeowner is missing")

    strategy_text = (
        release_dir / "custom_components" / "switch_vision" / "switch-vision-dashboard-strategy.js"
    ).read_text(encoding="utf-8", errors="ignore")
    if 'documentationURL: "https://switch-vision.zemerdon.com"' not in strategy_text:
        raise SystemExit("Release validation failed: dashboard strategy documentation URL is not public")

    gold_files = [release_dir / "GOLD_MASTER.md", release_dir / "GOLD_CHECKLIST.md"]
    if gold:
        missing_gold = [str(p.name) for p in gold_files if not p.exists()]
        if missing_gold:
            raise SystemExit("Release validation failed; Gold files missing:\n- " + "\n- ".join(missing_gold))
        manifest_data = json.loads((release_dir / "manifest.json").read_text(encoding="utf-8"))
        if manifest_data.get("status") != "gold":
            raise SystemExit("Release validation failed: Gold manifest status is not 'gold'")
    else:
        found_gold = [str(p.name) for p in gold_files if p.exists()]
        if found_gold:
            raise SystemExit("Release validation failed; Gold files included in non-Gold release:\n- " + "\n- ".join(found_gold))
        manifest_data = json.loads((release_dir / "manifest.json").read_text(encoding="utf-8"))
        if manifest_data.get("status") != "public-release":
            raise SystemExit("Release validation failed: non-Gold manifest status is not 'public-release'")

    if manifest_data.get("contains_discovery_app") is not False:
        raise SystemExit("Release validation failed: manifest must declare Discovery source as external")
    if manifest_data.get("contains_snmp2mqtt_app") is not False:
        raise SystemExit("Release validation failed: manifest must declare SNMP2MQTT source as external")
    if manifest_data.get("contains_unifi2mqtt_app") is not False:
        raise SystemExit("Release validation failed: manifest must declare UniFi2MQTT source as external")

    registry_path = release_dir / "devices" / "supported_devices.yaml"
    supported_md = release_dir / "docs" / "SUPPORTED_DEVICES.md"
    supported_bbcode = release_dir / "docs" / "SUPPORTED_DEVICES_FORUM.bbcode"
    for required_device_file in [registry_path, supported_md, supported_bbcode]:
        if not required_device_file.exists():
            raise SystemExit(f"Release validation failed: missing device-registry output: {required_device_file.name}")
    registry_text = registry_path.read_text(encoding="utf-8", errors="ignore")
    if "model: WS-C3650-48PD" not in registry_text or "aliases:" in registry_text:
        raise SystemExit("Release validation failed: exact-model registry policy is not satisfied")

    historical_notes = [p for p in (release_dir / "docs").glob("RELEASE_NOTES*") if p.is_file()]
    if historical_notes:
        raise SystemExit("Release validation failed: historical release-note files remain:\n- " + "\n- ".join(p.name for p in historical_notes))

    for path in release_dir.rglob("*"):
        if "__pycache__" in path.parts or ".pytest_cache" in path.parts or path.suffix in {".pyc", ".pyo"}:
            raise SystemExit(f"Release validation failed: Python cache artifact included: {path}")




def rename_versioned_examples(examples_dir: Path, version: str) -> None:
    """Version Core-owned examples while keeping independently-versioned Discovery examples neutral."""
    for path in sorted(list(examples_dir.iterdir())):
        if not path.is_file():
            continue
        is_discovery = path.name.startswith("discovery-")
        text = path.read_text(encoding="utf-8", errors="ignore")
        if is_discovery:
            # Discovery is a separately versioned component. Only Core frontend cache-busters
            # inside a cross-component example may follow the Core release.
            text = re.sub(r"(?<=\?v=)\d+\.\d+\.\d+", version, text)
            text = re.sub(r"Switch Vision Discovery v\d+\.\d+\.\d+", "Switch Vision Discovery", text)
            write_text_lf(path, text)
            new_name = re.sub(r"-v\d+\.\d+\.\d+", "", path.name)
        else:
            text = re.sub(r"v\d+\.\d+\.\d+", f"v{version}", text)
            text = re.sub(r"(?<=\?v=)\d+\.\d+\.\d+", version, text)
            write_text_lf(path, text)
            new_name = re.sub(r"v\d+\.\d+\.\d+", f"v{version}", path.name)
        if new_name != path.name:
            destination = path.with_name(new_name)
            if destination.exists():
                destination.unlink()
            path.rename(destination)


def validate_discovery_example_version_independence(base: Path, source_layout: bool = False) -> None:
    """Prevent Core builds from relabelling independently-versioned Discovery examples."""
    prefix = base / "src" if source_layout else base
    examples = prefix / "examples"
    errors: list[str] = []
    for path in sorted(examples.glob("discovery-*")):
        if re.search(r"-v\d+\.\d+\.\d+", path.name):
            errors.append(f"{path}: Discovery example filename is tied to the Core version")
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"Switch Vision Discovery v\d+\.\d+\.\d+", text):
                errors.append(f"{path}: Discovery product label is tied to the Core version")
    if errors:
        raise SystemExit("Discovery example version-independence validation failed:\n- " + "\n- ".join(errors))


def validate_generated_dashboard_safety(base: Path, source_layout: bool = False) -> None:
    """Ensure native dashboard loading keeps a bounded generated-YAML read path."""
    prefix = base / "src" if source_layout else base
    backend_path = prefix / "custom_components" / "switch_vision" / "__init__.py"
    backend = backend_path.read_text(encoding="utf-8", errors="ignore")
    required = [
        "MAX_GENERATED_DASHBOARD_BYTES = 4 * 1024 * 1024",
        "initial_stat.st_size > MAX_GENERATED_DASHBOARD_BYTES",
        "Generated dashboard YAML exceeds the Switch Vision safety limit.",
    ]
    missing = [marker for marker in required if marker not in backend]
    if missing:
        raise SystemExit(
            "Generated-dashboard safety validation failed: missing " + ", ".join(missing)
        )


def write_release_manifest(release_dir: Path, version: str, gold: bool = False) -> None:
    manifest = {
        "name": "Switch Vision",
        "version": version,
        "status": "gold" if gold else "public-release",
        "release_name": f"{PROJECT_NAME}-{version}",
        "resource": f"/local/switch-vision/js/switch-vision.js?v={version}",
        "card_type": "custom:switch-vision-3650",
        "custom_component_domain": "switch_vision",
        "installer_repository": "https://github.com/zemerdon/switch-vision-installer",
        "repository_managed_apps": [
            "switch-vision-discovery",
            "switch-vision-snmp2mqtt-addon",
            "switch-vision-unifi2mqtt",
        ],
        "contains_discovery_app": False,
        "contains_snmp2mqtt_app": False,
        "contains_snmp2mqtt_addon": False,
        "contains_unifi2mqtt_app": False,
        "gold_master": gold,
        "validated_snmp2mqtt_core": "0.9.3" if gold else None,
        "validated_snmp2mqtt_app": "0.9.3" if gold else None,
        "validated_snmp2mqtt_addon": "0.9.3" if gold else None,
    }
    write_text_lf(release_dir / "manifest.json", json.dumps(manifest, indent=2) + "\n")


def zip_directory(source_dir: Path, zip_path: Path, arc_base: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_dir.rglob("*")):
            if "__pycache__" in path.parts or ".pytest_cache" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            if path.is_file():
                arcname = path.relative_to(arc_base)
                if is_shell_script(path):
                    info = zipfile.ZipInfo.from_file(path, arcname)
                    info.create_system = 3
                    info.external_attr = (0o100755 & 0xFFFF) << 16
                    with path.open("rb") as handle:
                        archive.writestr(info, handle.read(), compress_type=zipfile.ZIP_DEFLATED)
                else:
                    archive.write(path, arcname)


def write_source_zip(version: str, gold: bool = False) -> Path:
    """Create the private source archive from an explicit allowlist."""
    output = PROJECT_ROOT / f"Switch_Vision_v{version}_source.zip"
    if output.exists():
        output.unlink()

    release_folder = RELEASES / f"{PROJECT_NAME}-{version}"
    if not release_folder.is_dir():
        raise SystemExit(f"Missing extracted release folder: {release_folder}")

    root_names = [
        ".gitattributes",
        ".gitignore",
        "README.md",
        "CHANGELOG.md",
        "RELEASE_NOTES.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "VERSION",
        "build.py",
    ]
    if (PROJECT_ROOT / "LICENSE").exists():
        root_names.append("LICENSE")
    if gold:
        root_names.extend(["GOLD_MASTER.md", "GOLD_CHECKLIST.md"])

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in root_names:
            path = PROJECT_ROOT / name
            if not path.is_file():
                raise SystemExit(f"Missing source-archive root file: {name}")
            archive.write(path, path.relative_to(PROJECT_ROOT))

        for source_root in (SRC, release_folder):
            for path in sorted(source_root.rglob("*")):
                if not path.is_file():
                    continue
                if "__pycache__" in path.parts or ".pytest_cache" in path.parts:
                    continue
                if path.suffix in {".pyc", ".pyo"}:
                    continue
                archive.write(path, path.relative_to(PROJECT_ROOT))
    return output


def validate_public_documentation(version: str) -> None:
    """Catch stale public instructions before archives are built."""
    required = [
        ROOT / "README.md",
        ROOT / "RELEASE_NOTES.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "SECURITY.md",
        SRC / "docs" / "INSTALLATION.md",
        SRC / "docs" / "UPGRADING.md",
        SRC / "docs" / "FIELD_REFERENCE.md",
        SRC / "docs" / "TROUBLESHOOTING.md",
        SRC / "examples" / "README.md",
    ]
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Public documentation is incomplete:\n- " + "\n- ".join(missing))

    checks = {
        ROOT / "README.md": [
            f"### Switch Vision v{version}",
            f"**v{version}** is the current tested public Switch Vision Core/dashboard release.",
            "https://github.com/zemerdon/switch-vision-installer",
            "https://github.com/zemerdon/switch-vision-releases",
        ],
        ROOT / "RELEASE_NOTES.md": [f"# Switch Vision Core v{version}"],
        SRC / "README.md": [
            f"### Switch Vision v{version}",
            f"**v{version}** is the current tested public Switch Vision Core/dashboard release.",
        ],
        SRC / "examples" / "README.md": [f"switch-vision.js?v={version}"],
    }
    errors: list[str] = []
    for path, markers in checks.items():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in markers:
            if marker not in text:
                errors.append(f"{path.relative_to(PROJECT_ROOT)}: missing {marker!r}")

    combined = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in required
    )
    stale_phrases = [
        "single default bundled faceplate",
        "dark 3650 faceplate",
        "None (no faceplate image)",
        "discovery-addon-options-v0.9.0",
        "Discovery local app",
        "bundled `switch_vision_unifi2mqtt` local app",
        "local_apps/switch_vision_discovery",
        "/local_apps/switch_vision_discovery",
        "local_apps/switch_vision_unifi2mqtt",
        "rebuilds Switch Vision Discovery when its bundled version changes",
        "github.com/zemerdon/switch-vision\n",
        "v2.1.x",
    ]
    for phrase in stale_phrases:
        if phrase in combined:
            errors.append(f"stale public documentation phrase remains: {phrase!r}")
    if errors:
        raise SystemExit("Public documentation validation failed:\n- " + "\n- ".join(errors))


def write_checksums(version: str, release_zip: Path, source_zip: Path) -> tuple[Path, Path]:
    """Write separate public-release and private-source checksum files."""
    import hashlib

    private_output = PROJECT_ROOT / f"Switch_Vision_v{version}_SHA256SUMS.txt"
    public_output = release_zip.with_name(release_zip.name + ".sha256")

    for path in (private_output, public_output):
        if path.exists():
            path.unlink()

    release_digest = hashlib.sha256(release_zip.read_bytes()).hexdigest()
    source_digest = hashlib.sha256(source_zip.read_bytes()).hexdigest()

    private_lines = [
        f"{release_digest}  {release_zip.relative_to(PROJECT_ROOT).as_posix()}",
        f"{source_digest}  {source_zip.relative_to(PROJECT_ROOT).as_posix()}",
    ]
    write_text_lf(private_output, "\n".join(private_lines) + "\n")

    write_text_lf(public_output, f"{release_digest}  {release_zip.name}\n")
    return private_output, public_output




def validate_source_archive(zip_path: Path, version: str, gold: bool = False) -> None:
    """Validate source-archive layout and hygiene."""
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
    forbidden = [
        name for name in names
        if "__pycache__/" in name
        or "/.pytest_cache/" in name
        or name.endswith((".pyc", ".pyo", ".bak", ".tmp", ".psd"))
        or name.startswith("tests/")
        or "/.git/" in name
        or name.startswith("src/local_apps/")
        or "/local_apps/" in name
    ]
    if forbidden:
        raise SystemExit("Source archive contains forbidden artifacts:\n- " + "\n- ".join(forbidden[:30]))
    release_prefix = f"Releases/{PROJECT_NAME}-{version}/"
    unexpected_releases = [
        name for name in names
        if name.startswith("Releases/") and not name.startswith(release_prefix)
    ]
    if unexpected_releases:
        raise SystemExit("Source archive contains unrelated releases:\n- " + "\n- ".join(unexpected_releases[:30]))
    gold_names = {"GOLD_MASTER.md", "GOLD_CHECKLIST.md"}
    present_gold = gold_names.intersection(names)
    if gold and present_gold != gold_names:
        raise SystemExit("Gold source archive is missing Gold documents")
    if not gold and present_gold:
        raise SystemExit("Non-Gold source archive includes Gold-only documents")


def clean_release(version: str) -> None:
    """Remove only build outputs for the release version being rebuilt."""
    RELEASES.mkdir(parents=True, exist_ok=True)

    release_dir = RELEASES / f"{PROJECT_NAME}-{version}"
    release_zip = RELEASES / f"{PROJECT_NAME}-{version}.zip"
    public_checksum = RELEASES / f"{PROJECT_NAME}-{version}.zip.sha256"

    if release_dir.exists():
        shutil.rmtree(release_dir)

    for path in (release_zip, public_checksum):
        if path.exists():
            path.unlink()


def build(version: str, gold: bool = False) -> tuple[Path, Path]:
    remove_historical_release_notes()
    patch_source_versions(version)
    validate_dashboard_strategy_resource_wiring(SRC)
    validate_dashboard_sidebar_controls(SRC)
    validate_dashboard_strategy_registration(SRC)
    validate_public_documentation(version)
    generate_supported_device_docs()
    validate_embedded_versions(PROJECT_ROOT, version, source_layout=True)
    ensure_required_sources()
    run_maintenance_tests()
    clean_release(version)
    release_dir = RELEASES / f"{PROJECT_NAME}-{version}"
    release_zip = RELEASES / f"{PROJECT_NAME}-{version}.zip"
    release_dir.mkdir(parents=True)
    for folder in [
        "logos", "faceplates", "css", "layouts", "calibration", "js", "examples",
        "custom_components", "docs", "devices"
    ]:
        copy_tree_files(SRC / folder, release_dir / folder)

    root_files = ["README.md", "CHANGELOG.md", "RELEASE_NOTES.md", "CONTRIBUTING.md", "SECURITY.md"]
    if gold:
        root_files.extend(["GOLD_MASTER.md", "GOLD_CHECKLIST.md"])
    for filename in root_files:
        source = ROOT / filename
        if source.exists():
            shutil.copy2(source, release_dir / filename)

    patch_js_version(release_dir / "js" / "switch-vision.js", version)
    component_dir = release_dir / "custom_components" / "switch_vision"
    patch_json_version(component_dir / "manifest.json", version)
    patch_panel_runtime_versions(component_dir, version)
    rename_versioned_examples(release_dir / "examples", version)
    for path in (release_dir / "docs").rglob("*.md"):
        patch_text_file(path, version)
    write_release_manifest(release_dir, version, gold=gold)
    normalize_shell_scripts(release_dir)
    validate_shell_scripts(release_dir)
    validate_release_sources(release_dir, version, gold=gold)
    validate_embedded_versions(release_dir, version, source_layout=False)
    zip_directory(release_dir, release_zip, arc_base=RELEASES)
    return release_dir, release_zip


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the main Switch Vision project release. An explicit release version is required."
        )
    )
    parser.add_argument(
        "-v", "--version",
        required=True,
        help=(
            "Required release version, such as 2.2.1. A wildcard such as 2.2.x may "
            "be used to select the next free patch explicitly."
        ),
    )
    parser.add_argument(
        "--gold",
        action="store_true",
        help="Build an actual Gold Master. Gold builds must use version 1.0.0 or later and include Gold-only validation material.",
    )
    return parser.parse_args()
def main() -> None:
    args = parse_args()
    version = resolve_version(args.version)
    if args.gold and not is_gold_version(version):
        raise SystemExit("Gold Master builds must use version 1.0.0 or later.")
    release_dir, release_zip = build(version, gold=args.gold)

    # Keep the root VERSION aligned with the archive and extracted release.
    write_text_lf(VERSION_FILE, version + "\n")
    validate_embedded_versions(PROJECT_ROOT, version, source_layout=True)

    source_zip = write_source_zip(version, gold=args.gold)
    validate_source_archive(source_zip, version, gold=args.gold)
    private_checksums, public_checksum = write_checksums(version, release_zip, source_zip)

    print(f"Built release folder: {release_dir}")
    print(f"Built release ZIP:    {release_zip}")
    print(f"Built public SHA256:  {public_checksum}")
    print(f"Built source ZIP:     {source_zip}")
    print(f"Built private sums:   {private_checksums}")
    print(f"Release status:       {'GOLD MASTER' if args.gold else 'PUBLIC RELEASE'}")
    print(f"VERSION after build:  {read_version()}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Build cancelled.", file=sys.stderr)
        raise SystemExit(130)
