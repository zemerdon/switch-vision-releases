#!/usr/bin/env python3
"""Temporary targeted registry patch for SV-2026-000002 review.

Edits only the three existing UniFi evidence blocks and inserts the three new exact
models; it intentionally avoids round-tripping the whole YAML file.
"""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "src" / "devices" / "supported_devices.yaml"
CONTRIBUTION_ID = "SV-2026-000002"


def span_for_model(text: str, model: str) -> tuple[int, int]:
    marker = f"  model: {model}\n"
    pos = text.find(marker)
    if pos < 0:
        raise SystemExit(f"registry model not found: {model}")
    start = text.rfind("\n- vendor:", 0, pos)
    start = 0 if start < 0 else start + 1
    end = text.find("\n- vendor:", pos)
    if end < 0:
        end = len(text)
    return start, end


def replace_model_block(text: str, model: str, block: str) -> str:
    start, end = span_for_model(text, model)
    return text[:start] + block.rstrip() + "\n" + text[end:].lstrip("\n")


def add_evidence(text: str, model: str, units: int, notes: list[str]) -> str:
    start, end = span_for_model(text, model)
    block = text[start:end]
    if CONTRIBUTION_ID in block:
        return text
    contribution = f'''  contributions:
  - id: {CONTRIBUTION_ID}
    source_component: UniFi2MQTT 2.0.47
    devices_observed: {units}
    validation_scope: physical_api_contract
    api_capabilities:
      port_detail: true
      per_port_traffic: false
    dashboard_validation: pending
    contributor:
      display_name: bignick8t3
      public_credit: true
'''
    notes_marker = "  notes:\n"
    if notes_marker not in block:
        raise SystemExit(f"{model}: notes block missing")
    block = block.replace(notes_marker, contribution + notes_marker, 1)
    validation_marker = "  validation:\n"
    if validation_marker not in block:
        raise SystemExit(f"{model}: validation block missing")
    additions = "".join(f"  - {note}\n" for note in notes)
    block = block.replace(validation_marker, additions + validation_marker, 1)
    return text[:start] + block + text[end:]


text = PATH.read_text(encoding="utf-8")
text = add_evidence(
    text,
    "US 8 60W",
    1,
    [
        "SV-2026-000002 from bignick8t3 independently reconfirms one 8x 1G RJ45 unit with PoE capability limited to physical/API ports 5-8 using 802.3af.",
        "SV-2026-000002 was captured with UniFi2MQTT 2.0.47 and did not include explicit Switch Vision dashboard/card validation, so Experimental status is unchanged.",
    ],
)
text = add_evidence(
    text,
    "USW Flex Mini",
    2,
    [
        "SV-2026-000002 from bignick8t3 independently reconfirms two additional units with the same five-port 1G RJ45 topology.",
        "SV-2026-000002 was captured with UniFi2MQTT 2.0.47 and did not include explicit Switch Vision dashboard/card validation, so Experimental status is unchanged.",
    ],
)
text = add_evidence(
    text,
    "US 48 PoE 500W",
    2,
    [
        "SV-2026-000002 from bignick8t3 independently reconfirms two units with 48 PoE-capable 1G RJ45 ports, API ports 49-50 as 10G SFP+, and API ports 51-52 as 1G SFP.",
        "SV-2026-000002 was captured with UniFi2MQTT 2.0.47 and did not include explicit Switch Vision dashboard/card validation, so Experimental status is unchanged.",
    ],
)

NEW_BLOCKS = '''- vendor: Ubiquiti
  family: UniFi Switch
  model: US 48
  status: experimental
  confirmed_since: 2.4.9
  last_validated_version: 2.4.9
  evidence: support_my_switch_SV-2026-000002_unifi_api
  ports:
    rj45: 48
    poe: false
    uplinks: 4
    uplink_type: 2x 1G SFP + 2x 10G SFP+
    gigabit_sfp: 2
    ten_gigabit_sfp_plus: 2
  stack_support: false
  discovery_support: true
  dashboard_support: true
  mapping_profile: ubiquiti-us-48-api
  calibration_profile: stock_48rj45_4sfp
  default_faceplate: faceplates/48rj45-4sfp.png
  optional_faceplates: []
  tested_firmware: []
  contributor:
    display_name: bignick8t3
    public_credit: true
  contributions:
  - id: SV-2026-000002
    source_component: UniFi2MQTT 2.0.47
    devices_observed: 1
    validation_scope: physical_api_contract
    api_capabilities:
      port_detail: true
      per_port_traffic: false
    dashboard_validation: pending
    contributor:
      display_name: bignick8t3
      public_credit: true
  notes:
  - Support My Switch contribution SV-2026-000002 captured one real US 48 with 48x 1G RJ45, no PoE, API ports 49-50 as 10G SFP+, and API ports 51-52 as 1G SFP.
  - The verified physical geometry matches the existing US 48 PoE 500W 48-RJ45 + 4-optical layout, so the existing stock_48rj45_4sfp calibration is reused rather than fabricating a new faceplate.
  - The model deliberately remains on the legacy sequential UniFi mapping path: RJ45 API ports 1-48 followed by optical API ports 49-52.
  - Port detail is available while per-port traffic is unavailable through the contributed UniFi API path; that capability distinction is not treated as a device failure.
  - Rendered dashboard/card validation remains pending before promotion beyond Experimental.
  validation:
    exact_model_detection: live_api_confirmed
    rj45_mapping: live_api_confirmed_port_indices_1_48
    poe: live_api_confirmed_no_poe_output_capability
    system_sensors: pending
    uplinks: live_api_confirmed_ports_49_50_10g_sfp_plus_51_52_1g_sfp
    stack: not_applicable
  visuals:
    status: experimental
    recommended_faceplate: faceplates/48rj45-4sfp.png
    optional_faceplates: []
    calibration_profile: stock_48rj45_4sfp
    canvas:
      width: 2048
      height: 448
- vendor: Ubiquiti
  family: UniFi Switch XG
  model: US XG 16
  status: detected
  confirmed_since: 2.4.9
  last_validated_version: 2.4.9
  evidence: support_my_switch_SV-2026-000002_unifi_api
  ports:
    rj45: 4
    poe: false
    uplinks: 12
    uplink_type: 12x 10G SFP+
    gigabit_sfp: 0
    ten_gigabit_sfp_plus: 12
  stack_support: false
  discovery_support: true
  dashboard_support: false
  mapping_profile: ubiquiti-us-xg-16-api
  unifi_api_port_map:
    rj45:
    - 13
    - 14
    - 15
    - 16
    sfp:
    - 1
    - 2
    - 3
    - 4
    - 5
    - 6
    - 7
    - 8
    - 9
    - 10
    - 11
    - 12
  calibration_profile: ''
  default_faceplate: ''
  optional_faceplates: []
  tested_firmware: []
  contributor:
    display_name: bignick8t3
    public_credit: true
  contributions:
  - id: SV-2026-000002
    source_component: UniFi2MQTT 2.0.47
    devices_observed: 2
    validation_scope: physical_api_contract
    api_capabilities:
      port_detail: true
      per_port_traffic: false
    dashboard_validation: pending
    contributor:
      display_name: bignick8t3
      public_credit: true
  notes:
  - Two independent SV-2026-000002 units expose matching optical-first geometry: API/physical ports 1-12 are 10G SFP+ and ports 13-16 are 10G-capable RJ45.
  - The explicit UniFi API-port map is authoritative and must not be replaced with a copper-first offset approximation.
  - One contributed 10G-capable RJ45 port was negotiating at 1G, confirming that live negotiated speed must remain independent from maximum connector capability.
  - Port detail is available while per-port traffic is unavailable through the contributed UniFi API path.
  - No verified 12-SFP+ + 4-RJ45 faceplate coordinates are available yet, so dashboard support and calibration remain pending rather than assigning an inaccurate generic visual.
  validation:
    exact_model_detection: live_api_confirmed_two_units
    rj45_mapping: live_api_confirmed_api_ports_13_16
    poe: live_api_confirmed_no_poe_output_capability
    system_sensors: pending
    uplinks: live_api_confirmed_api_ports_1_12_10g_sfp_plus
    stack: not_applicable
  visuals:
    status: detected
    recommended_faceplate: ''
    optional_faceplates: []
    calibration_profile: ''
    canvas:
      width: 2048
      height: 448
- vendor: Ubiquiti
  family: UniFi Switch Pro Aggregation
  model: USW Pro Aggregation
  status: detected
  confirmed_since: 2.4.9
  last_validated_version: 2.4.9
  evidence: support_my_switch_SV-2026-000002_unifi_api
  ports:
    rj45: 0
    poe: false
    uplinks: 32
    uplink_type: 28x 10G SFP+ + 4x 25G SFP28
    gigabit_sfp: 0
    ten_gigabit_sfp_plus: 28
    twenty_five_gigabit_sfp28: 4
  stack_support: false
  discovery_support: true
  dashboard_support: false
  mapping_profile: ubiquiti-usw-pro-aggregation-api
  unifi_api_port_map:
    rj45: []
    sfp:
    - 1
    - 2
    - 3
    - 4
    - 5
    - 6
    - 7
    - 8
    - 9
    - 10
    - 11
    - 12
    - 13
    - 14
    - 15
    - 16
    - 17
    - 18
    - 19
    - 20
    - 21
    - 22
    - 23
    - 24
    - 25
    - 26
    - 27
    - 28
    - 29
    - 30
    - 31
    - 32
  calibration_profile: ''
  default_faceplate: ''
  optional_faceplates: []
  tested_firmware: []
  contributor:
    display_name: bignick8t3
    public_credit: true
  contributions:
  - id: SV-2026-000002
    source_component: UniFi2MQTT 2.0.47
    devices_observed: 1
    validation_scope: physical_api_contract
    api_capabilities:
      port_detail: true
      per_port_traffic: false
    dashboard_validation: pending
    contributor:
      display_name: bignick8t3
      public_credit: true
  notes:
  - SV-2026-000002 confirms a 32-port optical-only switch: physical/API ports 1-28 are SFP+ with 10G maximum capability and ports 29-32 are SFP28 with 25G maximum capability.
  - Ports 29 and 30 were observed negotiating at 10G despite 25G SFP28 capability; Switch Vision must display the current 10G link speed while retaining 25G as maximum capability metadata.
  - Port detail is available while per-port traffic is unavailable through the contributed UniFi API path.
  - Core calibration storage supports the required connector count after the optical-only validation fix, but no verified 32-port faceplate coordinates are available yet.
  - Dashboard support remains disabled until a proper high-density optical faceplate/calibration profile is verified; a four-uplink fallback is intentionally not used.
  validation:
    exact_model_detection: live_api_confirmed
    rj45_mapping: not_applicable
    poe: not_applicable
    system_sensors: pending
    uplinks: live_api_confirmed_28x10g_sfp_plus_4x25g_sfp28
    stack: not_applicable
  visuals:
    status: detected
    recommended_faceplate: ''
    optional_faceplates: []
    calibration_profile: ''
    canvas:
      width: 2048
      height: 448
'''

if "  model: US XG 16\n" not in text:
    _, insert_pos = span_for_model(text, "US 48 PoE 500W")
    text = text[:insert_pos] + "\n" + NEW_BLOCKS.rstrip() + "\n" + text[insert_pos:]

PATH.write_text(text, encoding="utf-8", newline="\n")
print("SV-2026-000002 targeted registry patch applied")
