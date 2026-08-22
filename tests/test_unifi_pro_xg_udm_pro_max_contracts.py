from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "devices" / "supported_devices.yaml"
GENERATED = ROOT / "src" / "devices" / "supported_devices.json"

source_doc = yaml.safe_load(SOURCE.read_text(encoding="utf-8")) or {}
models = {d["model"]: d for d in source_doc["devices"] if isinstance(d, dict)}

udm = models["UDM Pro Max"]
assert udm["status"] == "experimental"
assert udm["ports"]["rj45"] == 9
assert udm["ports"]["poe"] is False
assert udm["ports"]["ten_gigabit_sfp_plus"] == 2
assert udm["unifi_api_port_map"]["rj45"] == list(range(1, 10))
assert udm["unifi_api_port_map"]["sfp"] == [10, 11]
assert udm["tested_firmware"] == ["5.1.31"]
assert udm["contributor"]["display_name"].casefold() == "community contributor"
assert udm["contributor"]["public_credit"] is False
assert "2.5G-capable RJ45" in " ".join(udm["notes"])
assert "must not synthesize per-port traffic" in " ".join(udm["notes"])

xg = models["USW Pro XG 24 PoE"]
assert xg["status"] == "experimental"
assert xg["ports"]["rj45"] == 24
assert xg["ports"]["poe"] is True
assert xg["ports"]["uplinks"] == 2
assert xg["ports"]["ten_gigabit_sfp_plus"] == 0
assert xg["ports"]["twenty_five_gigabit_sfp28"] == 2
assert xg["unifi_api_port_map"]["rj45"] == list(range(1, 25))
assert xg["unifi_api_port_map"]["sfp"] == [25, 26]
assert xg["tested_firmware"] == ["7.5.10"]
assert xg["contributor"]["display_name"].casefold() == "community contributor"
assert xg["contributor"]["public_credit"] is False
notes = " ".join(xg["notes"])
assert "ports 1-8 are 2.5G-capable RJ45" in notes
assert "ports 9-24 are 10G-capable RJ45" in notes
assert "ports 25-26 are 25G SFP28" in notes
assert "802.3bt Type 4" in notes
assert "100M, 1G and 10G" in notes
assert "both 10G and 25G" in notes

for item in (udm, xg):
    public_text = json.dumps(item).casefold()
    assert "kc1koc" not in public_text
    assert "sv-2026-000011" not in public_text
    assert "switch_vision_contribution" not in public_text

generated_doc = json.loads(GENERATED.read_text(encoding="utf-8"))
generated_models = {d["model"]: d for d in generated_doc["devices"] if isinstance(d, dict)}
assert generated_models["UDM Pro Max"] == udm
assert generated_models["USW Pro XG 24 PoE"] == xg

print("Switch Vision Core UDM Pro Max / USW Pro XG 24 PoE contracts: PASS")
