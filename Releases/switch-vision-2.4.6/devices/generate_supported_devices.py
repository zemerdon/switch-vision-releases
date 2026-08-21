#!/usr/bin/env python3
"""Generate supported-device documentation from the authoritative YAML registry."""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required to generate supported-device documentation: pip install PyYAML") from exc

ALLOWED_STATUSES = {"detected", "experimental", "community_validated", "confirmed"}
REQUIRED_FIELDS = {
    "vendor", "family", "model", "status", "confirmed_since",
    "last_validated_version", "ports", "stack_support",
    "discovery_support", "dashboard_support", "calibration_profile",
    "default_faceplate", "validation",
}


def yes_no(value: object) -> str:
    return "Yes" if bool(value) else "No"


def status_label(value: str) -> str:
    return value.replace("_", " ").title()


def uplink_text(ports: dict) -> str:
    gigabit = int(ports.get("gigabit_sfp", 0) or 0)
    ten_gigabit = int(ports.get("ten_gigabit_sfp_plus", 0) or 0)
    if gigabit or ten_gigabit:
        parts = []
        if gigabit:
            parts.append(f"{gigabit} Gigabit SFP")
        if ten_gigabit:
            parts.append(f"{ten_gigabit} 10G SFP+")
        return " + ".join(parts)
    return f"{ports['uplinks']} {ports.get('uplink_type', 'uplinks')}"


def load_registry(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("Device registry root must be a mapping")
    devices = data.get("devices")
    if not isinstance(devices, list):
        raise SystemExit("Device registry must contain a devices list")

    seen_models: set[str] = set()
    for index, device in enumerate(devices, start=1):
        if not isinstance(device, dict):
            raise SystemExit(f"Device entry {index} must be a mapping")
        missing = sorted(REQUIRED_FIELDS - set(device))
        if missing:
            raise SystemExit(f"Device entry {index} is missing: {', '.join(missing)}")
        model = str(device["model"]).strip()
        if not model:
            raise SystemExit(f"Device entry {index} has an empty exact model")
        if model in seen_models:
            raise SystemExit(f"Duplicate exact model entry: {model}")
        seen_models.add(model)
        if "aliases" in device:
            raise SystemExit(f"Aliases are not allowed; add exact models separately: {model}")
        status = str(device["status"]).strip()
        if status not in ALLOWED_STATUSES:
            raise SystemExit(f"Unsupported status '{status}' for {model}")
        ports = device.get("ports")
        if not isinstance(ports, dict) or "rj45" not in ports or "uplinks" not in ports:
            raise SystemExit(f"Port details are incomplete for {model}")
        visuals = device.get("visuals")
        if not isinstance(visuals, dict) or "status" not in visuals or "recommended_faceplate" not in visuals or "calibration_profile" not in visuals:
            raise SystemExit(f"Visual recommendation details are incomplete for {model}")
        if device.get("default_faceplate") != visuals.get("recommended_faceplate"):
            raise SystemExit(f"Visual recommendation faceplate differs from default_faceplate for {model}")
        if device.get("calibration_profile") != visuals.get("calibration_profile"):
            raise SystemExit(f"Visual recommendation calibration profile differs for {model}")
        if list(device.get("optional_faceplates") or []) != list(visuals.get("optional_faceplates") or []):
            raise SystemExit(f"Visual recommendation optional faceplates differ for {model}")
        canvas = visuals.get("canvas")
        if not isinstance(canvas, dict) or int(canvas.get("width", 0) or 0) <= 0 or int(canvas.get("height", 0) or 0) <= 0:
            raise SystemExit(f"Visual recommendation canvas is invalid for {model}")
        validation = device.get("validation")
        if not isinstance(validation, dict):
            raise SystemExit(f"Validation details are missing for {model}")
        required_validation = {"exact_model_detection", "rj45_mapping", "poe", "system_sensors", "uplinks", "stack"}
        missing_validation = sorted(required_validation - set(validation))
        if missing_validation:
            raise SystemExit(f"Validation details are incomplete for {model}: {', '.join(missing_validation)}")
    return data


def markdown(data: dict) -> str:
    lines = [
        "# Supported Devices",
        "",
        "This document is generated from `devices/supported_devices.yaml`.",
        "Only exact model identifiers are listed. Support for one SKU does not imply support for nearby variants.",
        "",
        "| Vendor | Family | Exact model | RJ45 | Uplinks | PoE | Stack | Recommended faceplate | Calibration profile | Uplink validation | Status | Last validated |",
        "|---|---|---|---:|---:|---|---|---|---|---|---|---|",
    ]
    for device in data["devices"]:
        ports = device["ports"]
        lines.append(
            "| {vendor} | {family} | `{model}` | {rj45} | {uplink_type} | {poe} | {stack} | `{faceplate}` | `{calibration}` | {uplink_validation} | {status} | v{validated} |".format(
                vendor=device["vendor"], family=device["family"], model=device["model"],
                rj45=ports["rj45"], uplinks="", uplink_type=uplink_text(ports),
                poe=yes_no(ports.get("poe")), stack=yes_no(device["stack_support"]),
                discovery=yes_no(device["discovery_support"]), dashboard=yes_no(device["dashboard_support"]),
                faceplate=(device.get("visuals", {}).get("recommended_faceplate") or "Pending"), calibration=(device.get("visuals", {}).get("calibration_profile") or "Pending"),
                uplink_validation=status_label(device["validation"]["uplinks"]), status=status_label(device["status"]), validated=device["last_validated_version"],
            )
        )
    lines += ["", "## Status definitions", ""]
    for key, description in data.get("support_statuses", {}).items():
        lines.append(f"- **{status_label(key)}:** {description}")
    lines += ["", "## Exact-model policy", "", "Each hardware SKU receives its own entry. The registry does not use aliases to infer support for licence, uplink, PoE, regional, or revision variants.", ""]
    return "\n".join(lines)


def bbcode(data: dict) -> str:
    lines = [
        "[size=150][b]Switch Vision Supported Devices[/b][/size]",
        "",
        "Only exact model identifiers are listed. Support for one SKU does not imply support for nearby variants.",
        "",
        "[table]",
        "[tr][th]Vendor[/th][th]Family[/th][th]Exact model[/th][th]Ports[/th][th]PoE[/th][th]Stack[/th][th]Recommended visual[/th][th]Uplink validation[/th][th]Status[/th][th]Last validated[/th][/tr]",
    ]
    for device in data["devices"]:
        ports = device["ports"]
        port_text = f"{ports['rj45']} RJ45 + {uplink_text(ports)}"
        lines.append(
            "[tr][td]{vendor}[/td][td]{family}[/td][td][code]{model}[/code][/td][td]{ports}[/td][td]{poe}[/td][td]{stack}[/td][td]{visual}[/td][td]{uplink_validation}[/td][td]{status}[/td][td]v{validated}[/td][/tr]".format(
                vendor=device["vendor"], family=device["family"], model=device["model"], ports=port_text,
                poe=yes_no(ports.get("poe")), stack=yes_no(device["stack_support"]),
                visual=(device.get("visuals", {}).get("calibration_profile") or "Pending faceplate/profile"),
                uplink_validation=status_label(device["validation"]["uplinks"]), status=status_label(device["status"]), validated=device["last_validated_version"],
            )
        )
    lines += ["[/table]", "", "[b]Support statuses[/b]"]
    for key, description in data.get("support_statuses", {}).items():
        lines.append(f"[*][b]{status_label(key)}:[/b] {description}")
    lines += ["", "[b]Exact-model policy[/b]", "Each hardware SKU receives its own entry. No aliases are used to infer support for related variants.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    parser.add_argument("docs_dir", type=Path)
    args = parser.parse_args()
    data = load_registry(args.registry)
    args.docs_dir.mkdir(parents=True, exist_ok=True)
    (args.docs_dir / "SUPPORTED_DEVICES.md").write_text(markdown(data), encoding="utf-8", newline="\n")
    (args.docs_dir / "SUPPORTED_DEVICES_FORUM.bbcode").write_text(bbcode(data), encoding="utf-8", newline="\n")
    (args.registry.parent / "supported_devices.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Generated supported-device documentation for {len(data['devices'])} exact model(s).")


if __name__ == "__main__":
    main()
