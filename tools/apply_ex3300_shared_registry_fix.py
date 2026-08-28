#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/devices/supported_devices.json"

old_ports = '''      "ports": {\n        "rj45": 48,\n        "poe": true,\n        "uplinks": 4,\n        "uplink_type": "SFP/SFP+",\n        "gigabit_sfp": 4,\n        "ten_gigabit_sfp_plus": 4\n      },\n      "stack_support": false,\n      "discovery_support": true,\n      "dashboard_support": true,\n      "mapping_profile": "juniper-ex3300-48p",\n'''
new_ports = '''      "ports": {\n        "rj45": 48,\n        "poe": true,\n        "uplinks": 4,\n        "uplink_type": "4 dual-speed 1G/10G SFP+ cages",\n        "gigabit_sfp": 0,\n        "ten_gigabit_sfp_plus": 4\n      },\n      "stack_support": false,\n      "discovery_support": true,\n      "dashboard_support": true,\n      "mapping_profile": "juniper-ex3300-48p",\n'''
old_note = '''        "Physical SFP/SFP+ uplink link state, activity, and 64-bit traffic counters validated on real hardware.",\n'''
new_note = '''        "Physical SFP/SFP+ uplink link state, activity, and 64-bit traffic counters validated on real hardware.",\n        "The four physical uplink cages are dual-speed: ge-0/1/N and xe-0/1/N are alternate identities for the same four cages and are not additive physical ports.",\n'''

text = TARGET.read_text(encoding="utf-8")
if text.count(old_ports) != 1:
    raise SystemExit(f"expected one EX3300 ports block, found {text.count(old_ports)}")
text = text.replace(old_ports, new_ports, 1)

before, marker, after = text.partition('"model": "EX3300-48P"')
if not marker:
    raise SystemExit("EX3300 model entry not found")
if after.count(old_note) < 1:
    raise SystemExit("EX3300 validation note not found")
after = after.replace(old_note, new_note, 1)
TARGET.write_text(before + marker + after, encoding="utf-8")
