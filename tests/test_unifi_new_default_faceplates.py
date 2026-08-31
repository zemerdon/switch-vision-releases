#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from faceplate_native_canvas import render_space_calibration

FACEPLATES = {
    "unifi-24-rj45-2sfp-inline.png": {
        "calibration": "faceplate-unifi-24-rj45-2sfp-inline.json",
        "profile": "unifi_24_rj45_2sfp_inline",
        "ports": 24,
        "sfp": 2,
        "render_checks": {
            "port1": [-711, 288],
            "port24": [2700, 288],
            "sfp1": [2922, 311],
            "sfp2": [3102, 311],
        },
    },
    "unifi-4-rj45-12sfp.png": {
        "calibration": "faceplate-unifi-4-rj45-12sfp.json",
        "profile": "unifi_4_rj45_12sfp",
        "ports": 4,
        "sfp": 12,
        "render_checks": {
            "port1": [2214, 303],
            "port4": [2694, 303],
            "sfp1": [832, 176],
            "sfp12": [1993, 316],
        },
    },
    "unifi-24-rj45-4sfp-inline.png": {
        "calibration": "faceplate-unifi-24-rj45-4sfp-inline.json",
        "profile": "unifi_24_rj45_4sfp_inline",
        "ports": 24,
        "sfp": 4,
        "render_checks": {
            "port1": [-711, 288],
            "port24": [2700, 288],
            "sfp1": [2922, 201],
            "sfp4": [3102, 311],
        },
    },
}

EXPECTED_24_PLUS_2_MODELS = {
    "USW-Pro-24-PoE",
    "USW Pro 24",
    "USW-24-PoE",
    "USW Pro Max 24",
    "USW Pro XG 24 PoE",
}

NEW_FILES = set(FACEPLATES)


def load_calibration(name: str) -> dict:
    return json.loads((SRC / "calibration" / name).read_text(encoding="utf-8"))


def main() -> None:
    for filename, spec in FACEPLATES.items():
        image_path = SRC / "faceplates" / filename
        assert image_path.is_file(), f"missing faceplate artwork: {filename}"

        calibration = load_calibration(spec["calibration"])
        assert calibration["schema_version"] == 2
        assert calibration["schema"] == "switch-vision-interactive-calibration-v1"
        assert calibration["profile"] == spec["profile"]
        assert Path(calibration["image"]["file"]).name == filename
        assert calibration["image"]["coordinate_space"] == "image-native-v1"
        assert Path(calibration["ui"]["faceplate"]["file"]).name == filename
        assert len(calibration["ports"]) == spec["ports"]
        assert len(calibration["sfp"]) == spec["sfp"]
        assert calibration["ui"]["logo"]["show"] is False
        assert calibration["ui"]["sfp_label_suffix"] == ""
        assert set(calibration["ui"]["status_leds"]["hidden"]) == {
            "STAT", "SYST", "DUPLX", "ACTV", "SPEED", "STACK", "PoE"
        }

        rendered = render_space_calibration(calibration)
        checks = spec["render_checks"]
        if "port1" in checks:
            assert rendered["ports"]["1"]["center"] == checks["port1"]
        if "port4" in checks:
            assert rendered["ports"]["4"]["center"] == checks["port4"]
        if "port24" in checks:
            assert rendered["ports"]["24"]["center"] == checks["port24"]
        if "sfp1" in checks:
            assert rendered["sfp"]["SFP1"]["center"] == checks["sfp1"]
        if "sfp2" in checks:
            assert rendered["sfp"]["SFP2"]["center"] == checks["sfp2"]
        if "sfp4" in checks:
            assert rendered["sfp"]["SFP4"]["center"] == checks["sfp4"]
        if "sfp12" in checks:
            assert rendered["sfp"]["SFP12"]["center"] == checks["sfp12"]

    cal_24_2 = load_calibration("faceplate-unifi-24-rj45-2sfp-inline.json")
    assert cal_24_2["sfp"]["SFP1"]["display_name"] == "SFP1"
    assert cal_24_2["sfp"]["SFP2"]["display_name"] == "SFP2"

    cal_24_4 = load_calibration("faceplate-unifi-24-rj45-4sfp-inline.json")
    assert [cal_24_4["sfp"][f"SFP{i}"]["display_name"] for i in range(1, 5)] == [
        "SFP1", "SFP2", "SFP3", "SFP4"
    ]

    cal_4_12 = load_calibration("faceplate-unifi-4-rj45-12sfp.json")
    assert [cal_4_12["ports"][str(i)]["display_name"] for i in range(1, 5)] == [
        "G1", "G2", "G3", "G4"
    ]

    registry = json.loads((SRC / "devices" / "supported_devices.json").read_text(encoding="utf-8"))
    rows = registry["devices"]
    by_model = {row["model"]: row for row in rows}

    for model in EXPECTED_24_PLUS_2_MODELS:
        row = by_model[model]
        assert row["vendor"] == "Ubiquiti"
        assert row["ports"]["rj45"] == 24
        assert row["ports"]["uplinks"] == 2
        assert row["calibration_profile"] == "unifi_24_rj45_2sfp_inline"
        assert Path(row["default_faceplate"]).name == "unifi-24-rj45-2sfp-inline.png"
        assert row["visuals"]["calibration_profile"] == "unifi_24_rj45_2sfp_inline"
        assert Path(row["visuals"]["recommended_faceplate"]).name == "unifi-24-rj45-2sfp-inline.png"

    xg16 = by_model["US XG 16"]
    assert xg16["vendor"] == "Ubiquiti"
    assert xg16["status"] == "detected"
    assert xg16["dashboard_support"] is True
    assert xg16["mapping_profile"] == "ubiquiti-us-xg-16-api"
    assert xg16["ports"]["rj45"] == 4
    assert xg16["ports"]["uplinks"] == 12
    assert xg16["unifi_api_port_map"]["rj45"] == [13, 14, 15, 16]
    assert xg16["unifi_api_port_map"]["sfp"] == list(range(1, 13))
    assert xg16["calibration_profile"] == "unifi_4_rj45_12sfp"
    assert Path(xg16["default_faceplate"]).name == "unifi-4-rj45-12sfp.png"
    assert xg16["visuals"]["status"] == "detected"
    assert xg16["visuals"]["calibration_profile"] == "unifi_4_rj45_12sfp"
    assert Path(xg16["visuals"]["recommended_faceplate"]).name == "unifi-4-rj45-12sfp.png"

    for row in rows:
        default_name = Path(str(row.get("default_faceplate") or "")).name
        recommended_name = Path(str((row.get("visuals") or {}).get("recommended_faceplate") or "")).name
        selected = {name for name in (default_name, recommended_name) if name in NEW_FILES}
        if not selected:
            continue
        assert row["vendor"] == "Ubiquiti", f"new UniFi faceplate leaked to {row['vendor']} {row['model']}"
        layout = (row["ports"]["rj45"], row["ports"]["uplinks"])
        if "unifi-24-rj45-2sfp-inline.png" in selected:
            assert layout == (24, 2), f"24+2 faceplate assigned to mismatched {row['model']}: {layout}"
        if "unifi-4-rj45-12sfp.png" in selected:
            assert layout == (4, 12), f"4+12 faceplate assigned to mismatched {row['model']}: {layout}"
        assert "unifi-24-rj45-4sfp-inline.png" not in selected, (
            f"24+4 faceplate must remain unassigned until an exact UniFi 24+4 topology is registered: {row['model']}"
        )

    card = (SRC / "js" / "switch-vision.js").read_text(encoding="utf-8")
    for profile, filename in (
        ("unifi_24_rj45_2sfp_inline", "unifi-24-rj45-2sfp-inline.png"),
        ("unifi_4_rj45_12sfp", "unifi-4-rj45-12sfp.png"),
        ("unifi_24_rj45_4sfp_inline", "unifi-24-rj45-4sfp-inline.png"),
    ):
        assert f'{profile}: "{filename}"' in card

    # Keep the historical UniFi 24+2 profile resolvable for stored legacy selections.
    assert 'unifi_24p_rj45_2sfp: "unifi-24p-rj45-2sfp.png"' in card

    print("UniFi new default faceplate contract: PASS")


if __name__ == "__main__":
    main()
