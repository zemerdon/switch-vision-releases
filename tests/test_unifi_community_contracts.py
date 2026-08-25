from __future__ import annotations

import hashlib
import json
from pathlib import Path
import yaml

from src.faceplate_native_canvas import render_space_calibration

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "devices" / "supported_devices.yaml"
GENERATED = ROOT / "src" / "devices" / "supported_devices.json"
CALIBRATION = ROOT / "src" / "calibration"
FACEPLATES = ROOT / "src" / "faceplates"

source_doc = yaml.safe_load(SOURCE.read_text(encoding="utf-8")) or {}
source_models = {d["model"]: d for d in source_doc["devices"] if isinstance(d, dict)}

expected = {
    "UCG Ultra": (5, 0, False, True, "ubiquiti-ucg-ultra-api"),
    "US 16 PoE 150W": (16, 2, True, False, "ubiquiti-us-16-poe-150w-api"),
    "USW Pro Max 24": (24, 2, False, True, "ubiquiti-usw-pro-max-24-api"),
    "USW Ultra": (8, 0, True, True, "ubiquiti-usw-ultra-api"),
}
for model, (rj45, uplinks, poe, dashboard, profile) in expected.items():
    item = source_models[model]
    expected_status = "experimental"
    assert item["status"] == expected_status, model
    assert item["ports"]["rj45"] == rj45, model
    assert item["ports"]["uplinks"] == uplinks, model
    assert item["ports"]["poe"] is poe, model
    assert item["dashboard_support"] is dashboard, model
    assert item["mapping_profile"] == profile, model
    assert item["evidence"] == "multiple_real_hardware_unifi_api_contributions", model
    contributions = item.get("contributions") or []
    assert len(contributions) >= 1, model
    for contribution in contributions:
        contributor = contribution.get("contributor") or {}
        assert str(contributor.get("display_name") or "").casefold() == "community contributor", model
        assert contributor.get("public_credit") is False, model
        assert contribution["api_capabilities"]["per_port_traffic"] is False, model

promax = source_models["USW Pro Max 24"]
assert promax["default_faceplate"] == "faceplates/unifi-24p-rj45-2sfp.png"
assert promax["calibration_profile"] == "unifi_24p_rj45_2sfp"
assert "ports 17-24 are 2.5G-capable RJ45" in " ".join(promax["notes"])
assert "ports_25_26_10g_sfp_plus" in promax["validation"]["uplinks"]

us16 = source_models["US 16 PoE 150W"]
assert "ports_17_18_1g_sfp" in us16["validation"]["uplinks"]
assert us16["default_faceplate"] == ""
assert us16["calibration_profile"] == ""

ucg = source_models["UCG Ultra"]
assert "no_poe_output" in ucg["validation"]["poe"]
assert ucg["default_faceplate"] == "faceplates/unifi-5rj45.png"
assert ucg["calibration_profile"] == "default_unifi_5_rj45"
assert ucg["visuals"]["status"] == "experimental"
assert ucg["visuals"]["recommended_faceplate"] == ucg["default_faceplate"]
assert ucg["visuals"]["calibration_profile"] == ucg["calibration_profile"]

ultra = source_models["USW Ultra"]
assert "ports_1_7_only" in ultra["validation"]["poe"]
assert ultra["default_faceplate"] == "faceplates/unifi-8rj45.png"
assert ultra["calibration_profile"] == "default_unifi_8_rj45"
assert ultra["visuals"]["status"] == "experimental"
assert ultra["visuals"]["recommended_faceplate"] == ultra["default_faceplate"]
assert ultra["visuals"]["calibration_profile"] == ultra["calibration_profile"]

small_faceplates = {
    "faceplate-unifi-5rj45.json": {
        "profile": "default_unifi_5_rj45",
        "model": "unifi-5-rj45",
        "image": "faceplates/unifi-5rj45.png",
        "ports": 5,
        "centers": [[1126, 245], [1577, 245], [2021, 245], [2472, 245], [2919, 245]],
    },
    "faceplate-unifi-8rj45.json": {
        "profile": "default_unifi_8_rj45",
        "model": "unifi-8-rj45",
        "image": "faceplates/unifi-8rj45.png",
        "ports": 8,
        "centers": [
            [1126, 245], [1407, 245], [1681, 245], [1967, 245],
            [2244, 245], [2523, 245], [2805, 245], [3087, 245],
        ],
    },
}
for filename, contract in small_faceplates.items():
    calibration = json.loads((CALIBRATION / filename).read_text(encoding="utf-8"))
    rendered_calibration = render_space_calibration(calibration)
    assert calibration["profile"] == contract["profile"], filename
    assert calibration["model"] == contract["model"], filename
    assert calibration["image"]["file"] == contract["image"], filename
    assert calibration["ui"]["faceplate"]["file"] == Path(contract["image"]).name, filename
    assert calibration["stack"] == {
        "enabled": False, "stack_id": "", "uptime_source": "", "members": {}
    }, filename
    assert calibration["management"]["switch_ip"] == "", filename
    assert calibration["sfp"] == {}, filename
    assert list(calibration["ports"]) == [str(index) for index in range(1, contract["ports"] + 1)], filename
    assert [rendered_calibration["ports"][str(index)]["center"] for index in range(1, contract["ports"] + 1)] == contract["centers"], filename
    assert (ROOT / "src" / contract["image"]).is_file(), filename

authoritative_faceplates = {
    "unifi-5rj45.png": {
        "size": 273448,
        "sha256": "8c9bdeb091f477a497579b717fedfc0d87a96c013ddf1def7fb1973f1b896414",
    },
    "unifi-8rj45.png": {
        "size": 261169,
        "sha256": "c7a04169b5cf6834780a579285250ac00f97f56ac450eb757e1e0ba8dbfaf74f",
    },
}
for filename, contract in authoritative_faceplates.items():
    payload = (FACEPLATES / filename).read_bytes()
    assert len(payload) == contract["size"], filename
    assert payload.startswith(b"\x89PNG\r\n\x1a\n"), filename
    assert hashlib.sha256(payload).hexdigest() == contract["sha256"], filename

generated = json.loads(GENERATED.read_text(encoding="utf-8"))
generated_models = {d["model"]: d for d in generated["devices"] if isinstance(d, dict)}
for model in expected:
    assert generated_models[model] == source_models[model], model

print("Switch Vision Core UniFi community hardware contracts: PASS")
