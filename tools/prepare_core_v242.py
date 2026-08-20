#!/usr/bin/env python3
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_SHA = "cf040dd1363eefa761c91ee864ce53c580ae8425"
DISCOVERY_REGISTRY_URL = (
    "https://raw.githubusercontent.com/zemerdon/switch-vision-discovery/"
    + DISCOVERY_SHA
    + "/runtime_src/opt/switch-vision/devices/supported_devices.json"
)
TARGET_STATUS_MODELS = {
    "WS-C2960X-24TS-L",
    "WS-C3560CG-8PC-S",
    "SG500X-24",
    "S5735-L8P4X-A1",
    "S5720-12TP-LI-AC",
}


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Switch-Vision-Core-v2.4.2-Prepare/1"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def by_model(payload: dict) -> dict[str, dict]:
    return {
        str(item.get("model")): item
        for item in payload.get("devices", [])
        if isinstance(item, dict) and item.get("model")
    }


def write(path: Path, text: str) -> None:
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


discovery = fetch_json(DISCOVERY_REGISTRY_URL)
discovery_models = by_model(discovery)
if len(discovery_models) != 28:
    raise SystemExit(f"ERROR: expected 28 Discovery models, found {len(discovery_models)}")

registry_path = ROOT / "src" / "devices" / "supported_devices.yaml"
core_doc = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
core_devices = core_doc.get("devices")
if not isinstance(core_devices, list):
    raise SystemExit("ERROR: Core registry devices is not a list")
core_models = by_model(core_doc)
if set(core_models) != set(discovery_models):
    raise SystemExit(
        "ERROR: Core/Discovery exact model sets differ before v2.4.2 preparation: "
        f"missing={sorted(set(discovery_models)-set(core_models))} "
        f"extra={sorted(set(core_models)-set(discovery_models))}"
    )

# Copy the complete, evidence-backed Discovery records for the five promoted
# models and every Ubiquiti model.  This keeps public status/notes and explicit
# per-model visual choices in lock-step while leaving unrelated vendor records
# untouched.
replacement_models = {
    model
    for model, item in discovery_models.items()
    if model in TARGET_STATUS_MODELS or item.get("vendor") == "Ubiquiti"
}
for index, device in enumerate(core_devices):
    if not isinstance(device, dict):
        continue
    model = str(device.get("model") or "")
    if model in replacement_models:
        core_devices[index] = json.loads(json.dumps(discovery_models[model]))

# Guard the intended status promotion and explicit UniFi visual inventory.
post = by_model(core_doc)
for model in TARGET_STATUS_MODELS:
    if post[model].get("status") != "community_validated":
        raise SystemExit(f"ERROR: {model} is not Community Validated after sync")
for model, device in post.items():
    if device.get("vendor") != "Ubiquiti":
        continue
    profile = str(device.get("calibration_profile") or "")
    faceplate = str(device.get("default_faceplate") or "")
    if not profile or not faceplate:
        raise SystemExit(f"ERROR: {model}: explicit UniFi visual assignment missing")
    if profile.lower().startswith("cisco_") or "cisco" in faceplate.lower():
        raise SystemExit(f"ERROR: {model}: Cisco visual fallback remains ({profile}, {faceplate})")

write(registry_path, yaml.safe_dump(core_doc, sort_keys=False, allow_unicode=True))

release_notes = """# Switch Vision Core v2.4.2 — Hardware validation safeguards

- Promotes `WS-C2960X-24TS-L`, `WS-C3560CG-8PC-S`, `SG500X-24`, `S5735-L8P4X-A1`, and `S5720-12TP-LI-AC` to **Community Validated** from existing real-hardware evidence.
- Preserves `WS-C3560CG-8PC-S` Gi0/9 and Gi0/10 dual-purpose combo-uplink semantics.
- Records the Huawei `S5720-12TP-LI-AC` physical layout as 8 RJ45 + 4 physical 1G SFP cages; Discovery v2.1.27 owns the matching 1G speed-cap safeguard.
- Keeps all 28 exact-model records aligned with Discovery and gives every known Ubiquiti model an explicit non-Cisco faceplate/profile assignment based on its real API geometry.
- Adds permanent Core regression coverage proving 2500 Mbps renders as `2.5G`, never `3G`.
- Makes the HAOS/manual Lovelace resource cache-buster a mandatory release contract: `/local/switch-vision/js/switch-vision.js?v=<version>` must match the Core release.
- Keeps MQTT topics, saved calibrations, Activity LED behaviour, and TEST MODE behaviour unchanged.

After updating Core through Switch Vision Installer, restart Home Assistant Core when prompted and hard-refresh the browser. If a manual Lovelace resource is configured, ensure its `?v=` suffix is `2.4.2`.
"""
write(ROOT / "RELEASE_NOTES.md", release_notes)

changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
entry = """## v2.4.2 — Hardware validation safeguards

- Promote five real-hardware-tested exact models to Community Validated while preserving model-specific physical semantics.
- Align Core's Ubiquiti exact-model visual/profile metadata with Discovery's explicit real-API geometry assignments; remove remaining Cisco-profile fallbacks from Ubiquiti records.
- Preserve Huawei S5720 8 RJ45 + 4 physical 1G SFP layout metadata; Discovery v2.1.27 enforces the physical 1G speed cap while retaining ifHighSpeed preference.
- Add permanent 2.5G display regression coverage and explicit HAOS/manual Lovelace resource version checks.
- Correct build documentation to reflect explicit release-version requirements.

"""
if changelog.startswith("# Changelog\n\n"):
    changelog = "# Changelog\n\n" + entry + changelog[len("# Changelog\n\n"):]
elif changelog.startswith("## v"):
    changelog = entry + changelog
else:
    raise SystemExit("ERROR: unexpected Core changelog header")
write(changelog_path, changelog)

print(
    "Prepared Core v2.4.2 from Discovery exact hardware metadata "
    f"({len(post)} models; {len(replacement_models)} synchronized records)"
)
