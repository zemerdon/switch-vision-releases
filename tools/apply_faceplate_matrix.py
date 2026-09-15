from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
YAML_PATH = ROOT / "src" / "devices" / "supported_devices.yaml"
JSON_PATH = ROOT / "src" / "devices" / "supported_devices.json"
GENERATOR = ROOT / "src" / "devices" / "generate_supported_devices.py"
CANONICAL_JS = ROOT / "src" / "js" / "switch-vision.js"
HA_JS = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"

# Exact-model visual corrections.  Oversized fallbacks are left alone where no
# matching bundled faceplate exists; this table only replaces mappings for
# models where Switch Vision already ships a better matching visual, plus the
# two stale dashboard-disabled records now covered by an approved safe canvas.
MATRIX = {
    "USW Flex": {
        "faceplate": "faceplates/unifi-5rj45.png",
        "profile": "default_unifi_5_rj45",
    },
    "USW Flex Mini": {
        "faceplate": "faceplates/unifi-5rj45.png",
        "profile": "default_unifi_5_rj45",
    },
    "USW-Lite-8-PoE": {
        "faceplate": "faceplates/unifi-8rj45.png",
        "profile": "default_unifi_8_rj45",
    },
    "USW-Enterprise-8-PoE": {
        "faceplate": "faceplates/unifi-8-rj45-2sfp.png",
        "profile": "unifi_8_rj45_2sfp",
    },
    "USW Pro XG 8 PoE": {
        "faceplate": "faceplates/unifi-8-rj45-2sfp.png",
        "profile": "unifi_8_rj45_2sfp",
    },
    "USW Pro HD 24 PoE": {
        "faceplate": "faceplates/unifi-24-rj45-4sfp-inline.png",
        "profile": "unifi_24_rj45_4sfp_inline",
    },
    "USW Pro Aggregation": {
        "faceplate": "faceplates/unifi-32sfp.png",
        "profile": "unifi_32sfp",
        "dashboard_support": True,
    },
    "US 16 PoE 150W": {
        "faceplate": "faceplates/24rj45-2sfp.png",
        "profile": "stock_24rj45_2sfp",
        "dashboard_support": True,
        "visual_status": "experimental",
    },
}

NOTE_REPLACEMENTS = {
    "USW Flex": {
        "No exact five-port Switch Vision visual is assigned yet; the universal temporary\n    fallback preserves the real API port count.":
        "The bundled five-RJ45 UniFi faceplate/profile matches the authoritative five-port\n    API topology and replaces the obsolete oversized fallback.",
    },
    "USW Flex Mini": {
        "The universal temporary faceplate is used while preserving the real five-port\n    count.":
        "The bundled five-RJ45 UniFi faceplate/profile matches the authoritative five-port\n    API topology and replaces the obsolete oversized fallback.",
    },
    "USW-Lite-8-PoE": {
        "A dedicated 8-port Switch Vision visual is not currently assigned to this registry\n    profile; the universal temporary fallback preserves the real port count.":
        "The bundled eight-RJ45 UniFi faceplate/profile matches the authoritative eight-port\n    API topology and replaces the obsolete oversized fallback.",
    },
    "USW-Enterprise-8-PoE": {
        "v2.0.32 uses the generic 48 RJ45 + 4 SFP faceplate as the universal temporary\n    fallback until a smaller matching generic visual is supplied.":
        "The bundled UniFi eight-RJ45 plus two-SFP faceplate/profile matches the repeated\n    physical/API topology and replaces the obsolete oversized fallback.",
    },
    "USW Pro XG 8 PoE": {
        "v2.0.32 uses the generic 48 RJ45 + 4 SFP faceplate as the universal temporary\n    fallback until a smaller matching generic visual is supplied.":
        "The bundled UniFi eight-RJ45 plus two-SFP faceplate/profile matches the confirmed\n    physical/API topology and replaces the obsolete oversized fallback.",
    },
    "USW Pro Aggregation": {
        "Core calibration storage supports the required connector count after the optical-only\n    validation fix, but no verified 32-port faceplate coordinates are available yet.":
        "The bundled owner-calibrated 32-position optical faceplate provides SFP1-SFP28 plus\n    four SFP28 positions for this exact topology.",
        "Dashboard support remains disabled until a proper high-density optical faceplate/calibration\n    profile is verified; a four-uplink fallback is intentionally not used.":
        "Dashboard support uses the bundled 32-position optical profile; no reduced optical\n    fallback is used.",
    },
    "US 16 PoE 150W": {
        "A dedicated 16 RJ45 + 2 SFP faceplate is not yet verified, so exact dashboard\n    visuals remain pending; Discovery may use its safe generic 24+2 visual with the\n    true 16+2 counts.":
        "No dedicated 16+2 artwork is bundled; the approved stock 24+2 canvas is used while\n    preserving the authoritative 16-RJ45 plus 2-SFP physical counts.",
    },
}


def _split_device_blocks(text: str) -> tuple[str, list[str]]:
    match = re.search(r"(?m)^devices:\s*$", text)
    if not match:
        raise RuntimeError("supported_devices.yaml has no devices section")
    prefix = text[: match.end()] + "\n"
    body = text[match.end() :].lstrip("\n")
    blocks = re.split(r"(?m)(?=^- )", body)
    return prefix, [block for block in blocks if block.strip()]


def _model_from_block(block: str) -> str | None:
    match = re.search(r"(?m)^  model:\s*(.+?)\s*$", block)
    if not match:
        return None
    value = match.group(1).strip()
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        value = value[1:-1]
    return value


def _replace_scalar(block: str, key: str, value: str, indent: int, required: bool = True) -> str:
    pattern = rf"(?m)^{' ' * indent}{re.escape(key)}:\s*.*$"
    replacement = f"{' ' * indent}{key}: {value}"
    updated, count = re.subn(pattern, replacement, block, count=1)
    if required and count != 1:
        raise RuntimeError(f"missing {key!r} at indent {indent}")
    return updated


def _patch_block(model: str, block: str, spec: dict[str, object]) -> str:
    faceplate = str(spec["faceplate"])
    profile = str(spec["profile"])

    if "dashboard_support" in spec:
        block = _replace_scalar(
            block,
            "dashboard_support",
            "true" if bool(spec["dashboard_support"]) else "false",
            2,
        )

    block = _replace_scalar(block, "calibration_profile", profile, 2)
    block = _replace_scalar(block, "default_faceplate", faceplate, 2)
    block = _replace_scalar(block, "recommended_faceplate", faceplate, 4)
    block = _replace_scalar(block, "calibration_profile", profile, 4)

    if "visual_status" in spec:
        # The first status at four spaces belongs to visuals; contribution status
        # fields are deeper and therefore cannot be touched by this expression.
        visual_match = re.search(r"(?ms)^  visuals:\s*\n(?P<body>.*?)(?=^- |\Z)", block)
        if not visual_match:
            raise RuntimeError(f"{model}: missing visuals block")
        body = visual_match.group("body")
        changed, count = re.subn(
            r"(?m)^    status:\s*.*$",
            f"    status: {spec['visual_status']}",
            body,
            count=1,
        )
        if count != 1:
            raise RuntimeError(f"{model}: missing visuals.status")
        block = block[: visual_match.start("body")] + changed + block[visual_match.end("body") :]

    for old, new in NOTE_REPLACEMENTS.get(model, {}).items():
        block = block.replace(old, new)

    return block


def patch_yaml() -> None:
    original = YAML_PATH.read_text(encoding="utf-8")
    parsed_before = yaml.safe_load(original)
    before_models = [row.get("model") for row in parsed_before.get("devices", []) if isinstance(row, dict)]

    prefix, blocks = _split_device_blocks(original)
    seen: set[str] = set()
    patched: list[str] = []
    for block in blocks:
        model = _model_from_block(block)
        if model in MATRIX:
            block = _patch_block(model, block, MATRIX[model])
            seen.add(model)
        patched.append(block)

    missing = set(MATRIX) - seen
    if missing:
        raise RuntimeError(f"exact-model rows missing from YAML: {sorted(missing)}")

    updated = prefix + "".join(patched)
    parsed_after = yaml.safe_load(updated)
    after_models = [row.get("model") for row in parsed_after.get("devices", []) if isinstance(row, dict)]
    if before_models != after_models:
        raise RuntimeError("device ordering/count changed while applying visual matrix")

    YAML_PATH.write_text(updated, encoding="utf-8", newline="\n")


def regenerate_registry_and_docs() -> None:
    result = subprocess.run(
        [sys.executable, str(GENERATOR), str(YAML_PATH), str(ROOT / "src" / "docs")],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "supported-device generator failed")


def sync_runtime_recommendations() -> None:
    spec = importlib.util.spec_from_file_location("switch_vision_build", ROOT / "build.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.sync_device_visual_recommendations()
    shutil.copy2(CANONICAL_JS, HA_JS)


def validate_result() -> None:
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    rows = {str(row.get("model")): row for row in payload.get("devices", []) if isinstance(row, dict)}
    for model, spec in MATRIX.items():
        row = rows[model]
        visuals = row.get("visuals") or {}
        if row.get("default_faceplate") != spec["faceplate"]:
            raise RuntimeError(f"{model}: generated default_faceplate is stale")
        if row.get("calibration_profile") != spec["profile"]:
            raise RuntimeError(f"{model}: generated calibration_profile is stale")
        if visuals.get("recommended_faceplate") != spec["faceplate"]:
            raise RuntimeError(f"{model}: generated visuals faceplate is stale")
        if visuals.get("calibration_profile") != spec["profile"]:
            raise RuntimeError(f"{model}: generated visuals profile is stale")
        if spec.get("dashboard_support") is True and row.get("dashboard_support") is not True:
            raise RuntimeError(f"{model}: dashboard_support was not enabled")


if __name__ == "__main__":
    patch_yaml()
    regenerate_registry_and_docs()
    sync_runtime_recommendations()
    validate_result()
    print(f"Applied exact-model faceplate matrix to {len(MATRIX)} models")
