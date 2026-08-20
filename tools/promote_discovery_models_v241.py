#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import urllib.request

import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.4.1"
DISCOVERY_REGISTRY_URL = (
    "https://raw.githubusercontent.com/zemerdon/"
    "switch-vision-discovery/main/runtime_src/opt/switch-vision/devices/supported_devices.json"
)
EXPECTED_MISSING_COUNT = 11
EXPECTED_MISSING_VENDORS = {"Dell", "Ubiquiti"}


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Switch-Vision-Core-Model-Promotion/1"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def model_map(payload: dict) -> dict[str, dict]:
    devices = payload.get("devices")
    if not isinstance(devices, list):
        raise SystemExit("ERROR: devices is not a list")
    result: dict[str, dict] = {}
    for item in devices:
        if not isinstance(item, dict):
            continue
        model = str(item.get("model") or "").strip()
        if not model:
            raise SystemExit("ERROR: device entry has no exact model")
        if model in result:
            raise SystemExit(f"ERROR: duplicate exact model {model!r}")
        result[model] = item
    return result


def append_missing_devices() -> list[dict]:
    core_path = ROOT / "src" / "devices" / "supported_devices.yaml"
    core_payload = yaml.safe_load(core_path.read_text(encoding="utf-8")) or {}
    discovery_payload = fetch_json(DISCOVERY_REGISTRY_URL)
    core_models = model_map(core_payload)
    discovery_models = model_map(discovery_payload)

    missing_names = sorted(discovery_models.keys() - core_models.keys())
    if len(missing_names) != EXPECTED_MISSING_COUNT:
        raise SystemExit(
            f"ERROR: expected {EXPECTED_MISSING_COUNT} Discovery-only exact models, "
            f"found {len(missing_names)}: {missing_names}"
        )

    missing = [discovery_models[name] for name in missing_names]
    vendors = {str(item.get("vendor") or "").strip() for item in missing}
    if not vendors.issubset(EXPECTED_MISSING_VENDORS):
        raise SystemExit(
            f"ERROR: unexpected Discovery-only vendor(s): {sorted(vendors - EXPECTED_MISSING_VENDORS)}"
        )

    # Promotion means moving exact-model knowledge into Core. It must never
    # silently inflate support status: preserve every Discovery entry verbatim.
    for item in missing:
        status = str(item.get("status") or "").strip()
        if not status:
            raise SystemExit(f"ERROR: {item.get('model')} has no support status")

    original = core_path.read_text(encoding="utf-8").rstrip() + "\n"
    fragment = yaml.safe_dump(
        missing,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=100,
    )
    core_path.write_text(original + fragment, encoding="utf-8", newline="\n")

    merged_payload = yaml.safe_load(core_path.read_text(encoding="utf-8")) or {}
    merged_models = model_map(merged_payload)
    if set(merged_models) != set(discovery_models):
        missing_after = sorted(set(discovery_models) - set(merged_models))
        extra_after = sorted(set(merged_models) - set(discovery_models))
        raise SystemExit(
            "ERROR: promoted Core exact-model set does not equal Discovery: "
            f"missing={missing_after}, extra={extra_after}"
        )

    print("Promoting Discovery-only exact models into Core:")
    for item in missing:
        print(
            f"- {item['model']} [{item.get('vendor')}; status={item.get('status')}; "
            f"RJ45={item.get('ports', {}).get('rj45')}; uplinks={item.get('ports', {}).get('uplinks')}]"
        )
    return missing


def make_registry_visuals_authoritative() -> None:
    path = ROOT / "build.py"
    text = path.read_text(encoding="utf-8")
    start_marker = "    # Generic stock visual policy:\n"
    end_marker = "\n    if errors:\n"
    start = text.find(start_marker)
    if start < 0:
        # Idempotence for a rerun after the patch has already landed.
        if "# Registry-authoritative visual policy:" in text:
            return
        raise SystemExit("ERROR: old generic visual-policy block not found")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit("ERROR: visual-policy end marker not found")

    replacement = '''    # Registry-authoritative visual policy:
    # exact-model visual/profile choices are evidence owned by the device
    # registry. Do not derive them from vendor or coarse port counts here.
    # This is essential for UniFi hardware whose exact models range from
    # compact 5/8-port devices through 48-port switches.
    dedicated_model = "WS-C3560CG-8PC-S"
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

        if not expected_profile:
            errors.append(f"{model}: registry calibration_profile is missing")
        if not expected_faceplate:
            errors.append(f"{model}: registry default_faceplate is missing")

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
        if item is None:
            errors.append(f"{model}: embedded model visual recommendation is missing")
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

        if model != dedicated_model:
            if item.get("profile") == "cisco_3560cg_8pc":
                errors.append(f"{model}: dedicated 3560CG calibration leaked into another exact model")
            if item.get("faceplate") == "faceplates/c3560cg-8pc-s.png":
                errors.append(f"{model}: dedicated 3560CG faceplate leaked into another exact model")
'''
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8", newline="\n")


def write_release_notes(missing: list[dict]) -> None:
    names = [str(item.get("model") or "").strip() for item in missing]
    formatted_names = ", ".join(f"`{name}`" for name in names)
    notes = f'''# Switch Vision Core v{VERSION} — Discovery model promotion

- Promotes all {len(names)} exact models currently known by Discovery but missing from Core into the Core supported-device index.
- Promoted models: {formatted_names}.
- Preserves each model's existing Discovery support status, validation evidence, port geometry, mapping profile and visual recommendation; Experimental models remain Experimental.
- Makes explicit per-model registry visuals authoritative instead of forcing every Ubiquiti model into one 24-port faceplate family.
- Keeps the dedicated v2.4.0 UniFi 24 RJ45 / 2 SFP faceplate for the exact models that currently recommend it, while preserving Discovery's existing stock/model geometry for other UniFi hardware.
- Does not change SNMP/UniFi telemetry protocols, MQTT topics, saved calibrations, or TEST MODE behaviour.

After updating Core through Switch Vision Installer, restart Home Assistant Core when prompted and hard-refresh the browser.
'''
    (ROOT / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8", newline="\n")

    changelog_path = ROOT / "CHANGELOG.md"
    old = changelog_path.read_text(encoding="utf-8")
    if old.startswith(f"## v{VERSION}\n"):
        return
    entry = f'''## v{VERSION}\n\n- Promoted {len(names)} Discovery-only exact model entries into the Core supported-device index without changing their support status.\n- Preserved Discovery's exact model evidence, geometry, mapping profiles and visual recommendations.\n- Replaced the blanket Ubiquiti 24-port visual validation rule with registry-authoritative per-model visual validation.\n- Kept existing saved/custom calibrations and telemetry contracts unchanged.\n\n'''
    changelog_path.write_text(entry + old, encoding="utf-8", newline="\n")


def main() -> int:
    missing = append_missing_devices()
    make_registry_visuals_authoritative()
    write_release_notes(missing)
    print(f"Prepared Core v{VERSION} model promotion source.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
