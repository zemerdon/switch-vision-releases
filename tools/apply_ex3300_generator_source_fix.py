#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src/devices/supported_devices.yaml"

old = '''- vendor: Juniper\n  family: EX3300\n  model: EX3300-48P\n  status: confirmed\n  confirmed_since: 1.8.26\n  last_validated_version: 1.8.26\n  evidence: real_hardware_standalone_full_port_and_uplink_validation\n  ports:\n    rj45: 48\n    poe: true\n    uplinks: 4\n    uplink_type: SFP/SFP+\n    gigabit_sfp: 4\n    ten_gigabit_sfp_plus: 4\n'''
new = '''- vendor: Juniper\n  family: EX3300\n  model: EX3300-48P\n  status: confirmed\n  confirmed_since: 1.8.26\n  last_validated_version: 1.8.26\n  evidence: real_hardware_standalone_full_port_and_uplink_validation\n  ports:\n    rj45: 48\n    poe: true\n    uplinks: 4\n    uplink_type: 4 dual-speed 1G/10G SFP+ cages\n    gigabit_sfp: 0\n    ten_gigabit_sfp_plus: 4\n'''
old_note = '''  - Physical SFP/SFP+ uplink link state, activity, and 64-bit traffic counters validated\n    on real hardware.\n'''
new_note = '''  - Physical SFP/SFP+ uplink link state, activity, and 64-bit traffic counters validated\n    on real hardware.\n  - The four physical uplink cages are dual-speed; ge-0/1/N and xe-0/1/N are alternate\n    identities for the same four cages and are not additive physical ports.\n'''

text = TARGET.read_text(encoding="utf-8")
if text.count(old) != 1:
    raise SystemExit(f"expected exactly one old EX3300 source block, found {text.count(old)}")
text = text.replace(old, new, 1)

before, marker, after = text.partition("  model: EX3300-48P")
if not marker:
    raise SystemExit("EX3300 source entry not found")
if after.count(old_note) < 1:
    raise SystemExit("EX3300 source validation note not found")
after = after.replace(old_note, new_note, 1)
TARGET.write_text(before + marker + after, encoding="utf-8", newline="\n")
print("EX3300 authoritative YAML source corrected")
