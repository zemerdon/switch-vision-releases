from __future__ import annotations

import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "devices" / "supported_devices.yaml"
GENERATED = ROOT / "src" / "devices" / "supported_devices.json"

source_doc = yaml.safe_load(SOURCE.read_text(encoding="utf-8")) or {}
source_models = {d["model"]: d for d in source_doc["devices"] if isinstance(d, dict)}

expected = {
    "UCG Ultra": (5, 0, False, False, "ubiquiti-ucg-ultra-api"),
    "US 16 PoE 150W": (16, 2, True, False, "ubiquiti-us-16-poe-150w-api"),
    "USW Pro Max 24": (24, 2, False, True, "ubiquiti-usw-pro-max-24-api"),
    "USW Ultra": (8, 0, True, False, "ubiquiti-usw-ultra-api"),
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
ultra = source_models["USW Ultra"]
assert "ports_1_7_only" in ultra["validation"]["poe"]
ucg = source_models["UCG Ultra"]
assert "no_poe_output" in ucg["validation"]["poe"]

for model in ("UCG Ultra", "US 16 PoE 150W", "USW Ultra"):
    item = source_models[model]
    assert item["default_faceplate"] == "", model
    assert item["calibration_profile"] == "", model

generated = json.loads(GENERATED.read_text(encoding="utf-8"))
generated_models = {d["model"]: d for d in generated["devices"] if isinstance(d, dict)}
for model in expected:
    assert generated_models[model] == source_models[model], model

print("Switch Vision Core UniFi community hardware contracts: PASS")
