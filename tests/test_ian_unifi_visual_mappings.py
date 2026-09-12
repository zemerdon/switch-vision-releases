#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((ROOT / "src/devices/supported_devices.json").read_text(encoding="utf-8"))
ROWS = {row["model"]: row for row in REGISTRY["devices"]}

EXPECTED = {
    "US-8-150W": {
        "rj45": 8,
        "uplinks": 2,
        "faceplate": "faceplates/unifi-8-rj45-2sfp.png",
        "profile": "unifi_8_rj45_2sfp",
    },
    "US 8 60W": {
        "rj45": 8,
        "uplinks": 0,
        "faceplate": "faceplates/unifi-8rj45.png",
        "profile": "default_unifi_8_rj45",
    },
}

for model, expected in EXPECTED.items():
    row = ROWS[model]
    assert row["status"] == "experimental", (model, row["status"])
    assert row["ports"]["rj45"] == expected["rj45"], (model, row["ports"])
    assert row["ports"]["uplinks"] == expected["uplinks"], (model, row["ports"])
    assert row["default_faceplate"] == expected["faceplate"], (model, row["default_faceplate"])
    assert row["calibration_profile"] == expected["profile"], (model, row["calibration_profile"])
    assert row["visuals"]["recommended_faceplate"] == expected["faceplate"], (model, row["visuals"])
    assert row["visuals"]["calibration_profile"] == expected["profile"], (model, row["visuals"])
    assert row["visuals"]["status"] == "experimental", (model, row["visuals"])

assert (ROOT / "src/faceplates/unifi-8-rj45-2sfp.png").is_file()
assert (ROOT / "src/faceplates/unifi-8rj45.png").is_file()
assert (ROOT / "src/calibration/faceplate-unifi-8-rj45-2sfp.json").is_file()
assert (ROOT / "src/calibration/faceplate-unifi-8rj45.json").is_file()

print("Ian UniFi exact visual mapping regressions: PASS")
