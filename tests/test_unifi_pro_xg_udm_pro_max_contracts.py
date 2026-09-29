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
xg = models["USW Pro XG 24 PoE"]
assert xg["status"] == "experimental"
assert xg["ports"]["rj45"] == 24
assert xg["ports"]["poe"] is True
assert xg["ports"]["uplinks"] == 2
assert xg["ports"]["ten_gigabit_sfp_plus"] == 0
assert xg["ports"]["twenty_five_gigabit_sfp28"] == 2
assert xg["unifi_api_port_map"]["rj45"] == list(range(1, 25))
assert xg["unifi_api_port_map"]["sfp"] == [25, 26]
generated_doc = json.loads(GENERATED.read_text(encoding="utf-8"))
generated_models = {d["model"]: d for d in generated_doc["devices"] if isinstance(d, dict)}
assert generated_models["UDM Pro Max"] == udm
assert generated_models["USW Pro XG 24 PoE"] == xg

print("Switch Vision Core UDM Pro Max / USW Pro XG 24 PoE contracts: PASS")
