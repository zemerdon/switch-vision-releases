#!/usr/bin/env python3
"""Temporary review-branch patcher for Support My Switch SV-2026-000002.

This file exists only to let GitHub Actions patch the exact checked-out Core tree
without reconstructing large source files through the connector. Remove it before
final review/merge.
"""
from __future__ import annotations

from pathlib import Path

from ruamel.yaml import YAML


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "js" / "switch-vision.js"
BACKEND = ROOT / "src" / "custom_components" / "switch_vision" / "__init__.py"
BUILD = ROOT / "build.py"
GENERATOR = ROOT / "src" / "devices" / "generate_supported_devices.py"
REGISTRY = ROOT / "src" / "devices" / "supported_devices.yaml"
SPEED_TEST = ROOT / "tests" / "test_speed_formatting.py"
CONTRIBUTION_ID = "SV-2026-000002"
CREDIT = "bignick8t3"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one patch target, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def replace_between(path: Path, start_marker: str, end_marker: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    if replacement in text:
        return
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{path}: start marker missing: {start_marker!r}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"{path}: end marker missing: {end_marker!r}")
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8", newline="\n")


OLD_UNIFI_LOOKUP = '''function unifiAccessPort(config, port) {
  if (String(config?.data_source || "").toLowerCase() !== "unifi_api") return null;
  return unifiPortByIndex(config, mappedPortNumber(config, port));
}

function unifiSfpPort(config, port) {
  if (String(config?.data_source || "").toLowerCase() !== "unifi_api") return null;
  const offset = Math.max(0, Number(config?.unifi_sfp_port_offset || config?.unifi_rj45_ports || 0));
  return unifiPortByIndex(config, offset + Number(port));
}'''

NEW_UNIFI_LOOKUP = '''function unifiApiPortMapForGroup(config, group) {
  const key = String(group || "").trim().toLowerCase();
  if (!new Set(["rj45", "sfp"]).has(key)) return null;

  const directMap = config?.unifi_api_port_map;
  if (directMap && typeof directMap === "object" && Array.isArray(directMap[key])) {
    return directMap[key];
  }

  const runtime = unifiRuntime(config);
  const modelCandidates = [
    runtime?.model,
    config?.model,
    config?.switch_model,
    config?.detected_model,
  ];
  for (const model of modelCandidates) {
    const exact = String(model || "").trim();
    if (!exact) continue;
    const recommendation = exactModelVisualRecommendation(exact);
    const modelMap = recommendation?.unifi_api_port_map;
    if (modelMap && typeof modelMap === "object" && Array.isArray(modelMap[key])) {
      return modelMap[key];
    }
  }
  return null;
}

function unifiApiPortIndex(config, group, port) {
  const key = String(group || "").trim().toLowerCase();
  const n = Number(port);
  if (!Number.isInteger(n) || n < 1) return null;

  const explicitMap = unifiApiPortMapForGroup(config, key);
  if (Array.isArray(explicitMap)) {
    const mapped = Number(explicitMap[n - 1]);
    return Number.isInteger(mapped) && mapped > 0 ? mapped : null;
  }

  if (key === "rj45") {
    const mapped = Number(mappedPortNumber(config, n));
    return Number.isFinite(mapped) ? mapped : null;
  }
  if (key === "sfp") {
    // Preserve the pre-explicit-map Core contract byte-for-byte in semantics:
    // an omitted map still uses unifi_sfp_port_offset, then unifi_rj45_ports.
    const offset = Math.max(0, Number(config?.unifi_sfp_port_offset || config?.unifi_rj45_ports || 0));
    return offset + n;
  }
  return null;
}

function unifiAccessPort(config, port) {
  if (String(config?.data_source || "").toLowerCase() !== "unifi_api") return null;
  const index = unifiApiPortIndex(config, "rj45", port);
  return index == null ? null : unifiPortByIndex(config, index);
}

function unifiSfpPort(config, port) {
  if (String(config?.data_source || "").toLowerCase() !== "unifi_api") return null;
  const index = unifiApiPortIndex(config, "sfp", port);
  return index == null ? null : unifiPortByIndex(config, index);
}'''

replace_once(CARD, OLD_UNIFI_LOOKUP, NEW_UNIFI_LOOKUP)

OLD_CALIBRATION_COUNT = '''    if not 1 <= len(ports) <= MAX_CALIBRATION_PORTS:
        raise vol.Invalid(
            f"calibration must contain between 1 and {MAX_CALIBRATION_PORTS} RJ45 ports"
        )
    if len(uplinks) > MAX_CALIBRATION_UPLINKS:
'''
NEW_CALIBRATION_COUNT = '''    if len(ports) > MAX_CALIBRATION_PORTS:
        raise vol.Invalid(
            f"calibration contains more than {MAX_CALIBRATION_PORTS} RJ45 ports"
        )
    if not ports and not uplinks:
        raise vol.Invalid("calibration must contain at least one RJ45 or optical port")
    if len(uplinks) > MAX_CALIBRATION_UPLINKS:
'''
replace_once(BACKEND, OLD_CALIBRATION_COUNT, NEW_CALIBRATION_COUNT)

OLD_SYNC_FUNCTION = '''def sync_device_visual_recommendations() -> None:
    """Regenerate the card's exact-model visual table from the authoritative registry."""
    registry_path = SRC / "devices" / "supported_devices.yaml"
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    devices = data.get("devices", []) if isinstance(data, dict) else []
    recommendations = []
    for device in devices if isinstance(devices, list) else []:
        if not isinstance(device, dict):
            continue
        visuals = device.get("visuals") if isinstance(device.get("visuals"), dict) else {}
        ports = device.get("ports") if isinstance(device.get("ports"), dict) else {}
        faceplate = visuals.get("recommended_faceplate")
        profile = visuals.get("calibration_profile")
        if not faceplate or not profile:
            continue
        recommendations.append({
            "model": device.get("model"),
            "status": device.get("status"),
            "family": device.get("family"),
            "rj45": ports.get("rj45"),
            "uplinks": ports.get("uplinks"),
            "visual_status": visuals.get("status"),
            "faceplate": faceplate,
            "optional_faceplates": visuals.get("optional_faceplates") or [],
            "profile": profile,
            "canvas": visuals.get("canvas"),
        })
    canonical = SRC / "js" / "switch-vision.js"
    text = canonical.read_text(encoding="utf-8", errors="ignore")
    replacement = "const SV_DEVICE_VISUAL_RECOMMENDATIONS = " + json.dumps(
        recommendations, ensure_ascii=False, separators=(",", ":")
    ) + ";"
    updated, count = re.subn(
        r"const SV_DEVICE_VISUAL_RECOMMENDATIONS = \\[.*?\\];",
        replacement,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("Could not synchronize device visual recommendations")
    write_text_lf(canonical, updated)


'''
NEW_SYNC_FUNCTION = '''def sync_device_visual_recommendations() -> None:
    """Regenerate exact-model visual/API mapping metadata from the registry."""
    registry_path = SRC / "devices" / "supported_devices.yaml"
    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    devices = data.get("devices", []) if isinstance(data, dict) else []
    recommendations = []
    for device in devices if isinstance(devices, list) else []:
        if not isinstance(device, dict):
            continue
        visuals = device.get("visuals") if isinstance(device.get("visuals"), dict) else {}
        ports = device.get("ports") if isinstance(device.get("ports"), dict) else {}
        faceplate = visuals.get("recommended_faceplate") or ""
        profile = visuals.get("calibration_profile") or ""
        api_port_map = device.get("unifi_api_port_map")
        has_api_port_map = isinstance(api_port_map, dict)
        if not (faceplate and profile) and not has_api_port_map:
            continue
        item = {
            "model": device.get("model"),
            "status": device.get("status"),
            "family": device.get("family"),
            "rj45": ports.get("rj45"),
            "uplinks": ports.get("uplinks"),
            "visual_status": visuals.get("status"),
            "faceplate": faceplate,
            "optional_faceplates": visuals.get("optional_faceplates") or [],
            "profile": profile,
            "canvas": visuals.get("canvas"),
        }
        if has_api_port_map:
            item["unifi_api_port_map"] = api_port_map
        recommendations.append(item)
    canonical = SRC / "js" / "switch-vision.js"
    text = canonical.read_text(encoding="utf-8", errors="ignore")
    replacement = "const SV_DEVICE_VISUAL_RECOMMENDATIONS = " + json.dumps(
        recommendations, ensure_ascii=False, separators=(",", ":")
    ) + ";"
    updated, count = re.subn(
        r"const SV_DEVICE_VISUAL_RECOMMENDATIONS = \\[.*?\\];",
        replacement,
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("Could not synchronize device visual recommendations")
    write_text_lf(canonical, updated)


'''
replace_once(BUILD, OLD_SYNC_FUNCTION, NEW_SYNC_FUNCTION)

# Add optional API-port-map parity to the first recommendation validation loop.
build_text = BUILD.read_text(encoding="utf-8")
expected_anchor = '''            "profile": visuals.get("calibration_profile"),
            "canvas": visuals.get("canvas"),
        }
'''
expected_replacement = '''            "profile": visuals.get("calibration_profile"),
            "canvas": visuals.get("canvas"),
            "unifi_api_port_map": device.get("unifi_api_port_map"),
        }
'''
if expected_replacement not in build_text:
    if build_text.count(expected_anchor) != 1:
        raise SystemExit("build.py: recommendation expected-map anchor is ambiguous")
    build_text = build_text.replace(expected_anchor, expected_replacement, 1)
    BUILD.write_text(build_text, encoding="utf-8", newline="\n")

NEW_VISUAL_POLICY = '''        dashboard_supported = device.get("dashboard_support") is True
        api_port_map = device.get("unifi_api_port_map")
        has_api_port_map = isinstance(api_port_map, dict)
        has_visual = bool(expected_profile and expected_faceplate)

        if dashboard_supported and not has_visual:
            errors.append(f"{model}: dashboard_support requires a calibration profile and faceplate")
        if bool(expected_profile) != bool(expected_faceplate):
            errors.append(f"{model}: calibration profile and faceplate must either both be set or both be pending")

        paired_faceplate = profile_faceplate_pairs.get(expected_profile)
        if paired_faceplate and expected_faceplate != paired_faceplate:
            errors.append(
                f"{model}: profile {expected_profile!r} must use {paired_faceplate!r}, "
                f"not {expected_faceplate!r}"
            )

        if visuals.get("calibration_profile") != expected_profile:
            errors.append(
                f"{model}: visuals.calibration_profile={visuals.get('calibration_profile')!r}, "
                f"expected registry calibration_profile {expected_profile!r}"
            )
        if visuals.get("recommended_faceplate") != expected_faceplate:
            errors.append(
                f"{model}: visuals.recommended_faceplate={visuals.get('recommended_faceplate')!r}, "
                f"expected registry default_faceplate {expected_faceplate!r}"
            )

        item = next(
            (row for row in recommendations if row.get("model") == model),
            None,
        )
        if has_visual or has_api_port_map:
            if item is None:
                errors.append(f"{model}: embedded model recommendation is missing")
                continue
            if item.get("profile") != expected_profile:
                errors.append(
                    f"{model}: embedded profile={item.get('profile')!r}, "
                    f"expected {expected_profile!r}"
                )
            if item.get("faceplate") != expected_faceplate:
                errors.append(
                    f"{model}: embedded faceplate={item.get('faceplate')!r}, "
                    f"expected {expected_faceplate!r}"
                )
            if item.get("unifi_api_port_map") != (api_port_map if has_api_port_map else None):
                errors.append(
                    f"{model}: embedded UniFi API-port map differs from registry"
                )
        elif item is not None:
            errors.append(f"{model}: unexpected embedded recommendation without a visual or API-port map")

'''
replace_between(
    BUILD,
    '        if not expected_profile:\n',
    '        if model not in compact_8x2_visual_models:\n',
    NEW_VISUAL_POLICY,
)

OLD_UPLINK_TEXT = '''def uplink_text(ports: dict) -> str:
    gigabit = int(ports.get("gigabit_sfp", 0) or 0)
    ten_gigabit = int(ports.get("ten_gigabit_sfp_plus", 0) or 0)
    if gigabit or ten_gigabit:
        parts = []
        if gigabit:
            parts.append(f"{gigabit} Gigabit SFP")
        if ten_gigabit:
            parts.append(f"{ten_gigabit} 10G SFP+")
        return " + ".join(parts)
    return f"{ports['uplinks']} {ports.get('uplink_type', 'uplinks')}"
'''
NEW_UPLINK_TEXT = '''def uplink_text(ports: dict) -> str:
    gigabit = int(ports.get("gigabit_sfp", 0) or 0)
    ten_gigabit = int(ports.get("ten_gigabit_sfp_plus", 0) or 0)
    twenty_five_gigabit = int(ports.get("twenty_five_gigabit_sfp28", 0) or 0)
    if gigabit or ten_gigabit or twenty_five_gigabit:
        parts = []
        if gigabit:
            parts.append(f"{gigabit} Gigabit SFP")
        if ten_gigabit:
            parts.append(f"{ten_gigabit} 10G SFP+")
        if twenty_five_gigabit:
            parts.append(f"{twenty_five_gigabit} 25G SFP28")
        return " + ".join(parts)
    return f"{ports['uplinks']} {ports.get('uplink_type', 'uplinks')}"
'''
replace_once(GENERATOR, OLD_UPLINK_TEXT, NEW_UPLINK_TEXT)

# Validate registry-owned explicit maps: complete group arrays, positive API indices,
# exact group counts, and no duplicate API binding across visual connector groups.
generator_text = GENERATOR.read_text(encoding="utf-8")
map_validation_anchor = '''        if not isinstance(ports, dict) or "rj45" not in ports or "uplinks" not in ports:
            raise SystemExit(f"Port details are incomplete for {model}")
'''
map_validation = map_validation_anchor + '''        api_port_map = device.get("unifi_api_port_map")
        if api_port_map is not None:
            if not isinstance(api_port_map, dict):
                raise SystemExit(f"UniFi API-port map must be a mapping for {model}")
            if set(api_port_map) != {"rj45", "sfp"}:
                raise SystemExit(f"UniFi API-port map must contain exactly rj45 and sfp groups for {model}")
            expected_counts = {
                "rj45": int(ports.get("rj45", 0) or 0),
                "sfp": int(ports.get("uplinks", 0) or 0),
            }
            mapped_indices: list[int] = []
            for group, expected_count in expected_counts.items():
                values = api_port_map.get(group)
                if not isinstance(values, list) or len(values) != expected_count:
                    raise SystemExit(
                        f"UniFi API-port map {group} count differs from physical port count for {model}"
                    )
                for value in values:
                    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                        raise SystemExit(f"UniFi API-port map contains an invalid index for {model}")
                mapped_indices.extend(values)
            if len(mapped_indices) != len(set(mapped_indices)):
                raise SystemExit(f"UniFi API-port map reuses an API index for {model}")
'''
if map_validation not in generator_text:
    if generator_text.count(map_validation_anchor) != 1:
        raise SystemExit("supported-device generator map-validation anchor is ambiguous")
    GENERATOR.write_text(
        generator_text.replace(map_validation_anchor, map_validation, 1),
        encoding="utf-8",
        newline="\n",
    )

# Extend speed formatting regression values and pin live-vs-capability field selection.
speed_text = SPEED_TEST.read_text(encoding="utf-8")
old_cases = '''const cases = [
  [1000, '1G'],
  [2500, '2.5G'],
  [5000, '5G'],
  [10000, '10G'],
];'''
new_cases = '''const cases = [
  [100, '100M'],
  [1000, '1G'],
  [2500, '2.5G'],
  [5000, '5G'],
  [10000, '10G'],
  [25000, '25G'],
];'''
if new_cases not in speed_text:
    if speed_text.count(old_cases) != 1:
        raise SystemExit("speed-format test cases anchor is ambiguous")
    speed_text = speed_text.replace(old_cases, new_cases, 1)

method_anchor = '''    def test_fractional_gigabit_speed_is_not_rounded_up(self) -> None:
'''
new_method = '''    def test_unifi_current_speed_stays_separate_from_max_capability(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        port_speed = extract_js_function(source, "function portSpeed(hass, config, port)")
        sfp_speed = extract_js_function(source, "function sfpSpeedMbps(hass, config, port)")
        self.assertIn("unifi.speed_mbps", port_speed)
        self.assertIn("unifi.speed_mbps", sfp_speed)
        self.assertNotIn("max_speed_mbps", port_speed)
        self.assertNotIn("max_speed_mbps", sfp_speed)

'''
if new_method not in speed_text:
    if speed_text.count(method_anchor) != 1:
        raise SystemExit("speed-format test method anchor is ambiguous")
    speed_text = speed_text.replace(method_anchor, new_method + method_anchor, 1)
SPEED_TEST.write_text(speed_text, encoding="utf-8", newline="\n")

# Registry updates use round-trip YAML so existing validated entries retain formatting/order.
yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 4096
with REGISTRY.open("r", encoding="utf-8") as handle:
    registry = yaml.load(handle)
devices = registry["devices"]
by_model = {str(item.get("model")): item for item in devices}


def contribution_record(units: int) -> dict:
    return {
        "id": CONTRIBUTION_ID,
        "source_component": "UniFi2MQTT 2.0.47",
        "devices_observed": units,
        "validation_scope": "physical_api_contract",
        "dashboard_validation": "pending",
        "contributor": {"display_name": CREDIT, "public_credit": True},
    }


def add_independent_evidence(model: str, units: int, notes: list[str]) -> None:
    item = by_model[model]
    contributions = item.setdefault("contributions", [])
    if not any(str(row.get("id")) == CONTRIBUTION_ID for row in contributions if isinstance(row, dict)):
        contributions.append(contribution_record(units))
    item_notes = item.setdefault("notes", [])
    for note in notes:
        if note not in item_notes:
            item_notes.append(note)


add_independent_evidence(
    "US 8 60W",
    1,
    [
        "SV-2026-000002 from bignick8t3 independently reconfirms one 8x 1G RJ45 unit with PoE capability limited to physical/API ports 5-8 using 802.3af.",
        "SV-2026-000002 was captured with UniFi2MQTT 2.0.47 and did not include explicit Switch Vision dashboard/card validation, so Experimental status is unchanged.",
    ],
)
add_independent_evidence(
    "USW Flex Mini",
    2,
    [
        "SV-2026-000002 from bignick8t3 independently reconfirms two additional units with the same five-port 1G RJ45 topology.",
        "SV-2026-000002 was captured with UniFi2MQTT 2.0.47 and did not include explicit Switch Vision dashboard/card validation, so Experimental status is unchanged.",
    ],
)
add_independent_evidence(
    "US 48 PoE 500W",
    2,
    [
        "SV-2026-000002 from bignick8t3 independently reconfirms two units with 48 PoE-capable 1G RJ45 ports, API ports 49-50 as 10G SFP+, and API ports 51-52 as 1G SFP.",
        "SV-2026-000002 was captured with UniFi2MQTT 2.0.47 and did not include explicit Switch Vision dashboard/card validation, so Experimental status is unchanged.",
    ],
)

new_devices = [
    {
        "vendor": "Ubiquiti",
        "family": "UniFi Switch",
        "model": "US 48",
        "status": "experimental",
        "confirmed_since": "pending_next_core_release",
        "last_validated_version": "pending_next_core_release",
        "evidence": "support_my_switch_SV-2026-000002_unifi_api",
        "ports": {
            "rj45": 48,
            "poe": False,
            "uplinks": 4,
            "uplink_type": "2x 1G SFP + 2x 10G SFP+",
            "gigabit_sfp": 2,
            "ten_gigabit_sfp_plus": 2,
        },
        "stack_support": False,
        "discovery_support": True,
        "dashboard_support": True,
        "mapping_profile": "ubiquiti-us-48-api",
        "calibration_profile": "stock_48rj45_4sfp",
        "default_faceplate": "faceplates/48rj45-4sfp.png",
        "optional_faceplates": [],
        "tested_firmware": [],
        "contributor": {"display_name": CREDIT, "public_credit": True},
        "contributions": [contribution_record(1)],
        "notes": [
            "Support My Switch contribution SV-2026-000002 captured one real US 48 with 48x 1G RJ45, no PoE, API ports 49-50 as 10G SFP+, and API ports 51-52 as 1G SFP.",
            "The verified physical geometry matches the existing US 48 PoE 500W 48-RJ45 + 4-optical layout, so the existing stock_48rj45_4sfp calibration is reused rather than fabricating a new faceplate.",
            "The model deliberately remains on the legacy sequential UniFi mapping path: RJ45 API ports 1-48 followed by optical API ports 49-52.",
            "Port detail is available while per-port traffic is unavailable through the contributed UniFi API path; that capability distinction is not treated as a device failure.",
            "Rendered dashboard/card validation remains pending before promotion beyond Experimental.",
        ],
        "validation": {
            "exact_model_detection": "live_api_confirmed",
            "rj45_mapping": "live_api_confirmed_port_indices_1_48",
            "poe": "live_api_confirmed_no_poe_output_capability",
            "system_sensors": "pending",
            "uplinks": "live_api_confirmed_ports_49_50_10g_sfp_plus_51_52_1g_sfp",
            "stack": "not_applicable",
        },
        "visuals": {
            "status": "experimental",
            "recommended_faceplate": "faceplates/48rj45-4sfp.png",
            "optional_faceplates": [],
            "calibration_profile": "stock_48rj45_4sfp",
            "canvas": {"width": 2048, "height": 448},
        },
    },
    {
        "vendor": "Ubiquiti",
        "family": "UniFi Switch XG",
        "model": "US XG 16",
        "status": "detected",
        "confirmed_since": "pending_next_core_release",
        "last_validated_version": "pending_next_core_release",
        "evidence": "support_my_switch_SV-2026-000002_unifi_api",
        "ports": {
            "rj45": 4,
            "poe": False,
            "uplinks": 12,
            "uplink_type": "12x 10G SFP+",
            "gigabit_sfp": 0,
            "ten_gigabit_sfp_plus": 12,
        },
        "stack_support": False,
        "discovery_support": True,
        "dashboard_support": False,
        "mapping_profile": "ubiquiti-us-xg-16-api",
        "unifi_api_port_map": {
            "rj45": [13, 14, 15, 16],
            "sfp": list(range(1, 13)),
        },
        "calibration_profile": "",
        "default_faceplate": "",
        "optional_faceplates": [],
        "tested_firmware": [],
        "contributor": {"display_name": CREDIT, "public_credit": True},
        "contributions": [contribution_record(2)],
        "notes": [
            "Two independent SV-2026-000002 units expose matching optical-first geometry: API/physical ports 1-12 are 10G SFP+ and ports 13-16 are 10G-capable RJ45.",
            "The explicit UniFi API-port map is authoritative and must not be replaced with a copper-first offset approximation.",
            "One contributed 10G-capable RJ45 port was negotiating at 1G, confirming that live negotiated speed must remain independent from maximum connector capability.",
            "Port detail is available while per-port traffic is unavailable through the contributed UniFi API path.",
            "No verified 12-SFP+ + 4-RJ45 faceplate coordinates are available yet, so dashboard support and calibration remain pending rather than assigning an inaccurate generic visual.",
        ],
        "validation": {
            "exact_model_detection": "live_api_confirmed_two_units",
            "rj45_mapping": "live_api_confirmed_api_ports_13_16",
            "poe": "live_api_confirmed_no_poe_output_capability",
            "system_sensors": "pending",
            "uplinks": "live_api_confirmed_api_ports_1_12_10g_sfp_plus",
            "stack": "not_applicable",
        },
        "visuals": {
            "status": "detected",
            "recommended_faceplate": "",
            "optional_faceplates": [],
            "calibration_profile": "",
            "canvas": {"width": 2048, "height": 448},
        },
    },
    {
        "vendor": "Ubiquiti",
        "family": "UniFi Switch Pro Aggregation",
        "model": "USW Pro Aggregation",
        "status": "detected",
        "confirmed_since": "pending_next_core_release",
        "last_validated_version": "pending_next_core_release",
        "evidence": "support_my_switch_SV-2026-000002_unifi_api",
        "ports": {
            "rj45": 0,
            "poe": False,
            "uplinks": 32,
            "uplink_type": "28x 10G SFP+ + 4x 25G SFP28",
            "gigabit_sfp": 0,
            "ten_gigabit_sfp_plus": 28,
            "twenty_five_gigabit_sfp28": 4,
        },
        "stack_support": False,
        "discovery_support": True,
        "dashboard_support": False,
        "mapping_profile": "ubiquiti-usw-pro-aggregation-api",
        "unifi_api_port_map": {
            "rj45": [],
            "sfp": list(range(1, 33)),
        },
        "calibration_profile": "",
        "default_faceplate": "",
        "optional_faceplates": [],
        "tested_firmware": [],
        "contributor": {"display_name": CREDIT, "public_credit": True},
        "contributions": [contribution_record(1)],
        "notes": [
            "SV-2026-000002 confirms a 32-port optical-only switch: physical/API ports 1-28 are SFP+ with 10G maximum capability and ports 29-32 are SFP28 with 25G maximum capability.",
            "Ports 29 and 30 were observed negotiating at 10G despite 25G SFP28 capability; Switch Vision must display the current 10G link speed while retaining 25G as maximum capability metadata.",
            "Port detail is available while per-port traffic is unavailable through the contributed UniFi API path.",
            "Core calibration storage supports the required connector count after the optical-only validation fix, but no verified 32-port faceplate coordinates are available yet.",
            "Dashboard support remains disabled until a proper high-density optical faceplate/calibration profile is verified; a four-uplink fallback is intentionally not used.",
        ],
        "validation": {
            "exact_model_detection": "live_api_confirmed",
            "rj45_mapping": "not_applicable",
            "poe": "not_applicable",
            "system_sensors": "pending",
            "uplinks": "live_api_confirmed_28x10g_sfp_plus_4x25g_sfp28",
            "stack": "not_applicable",
        },
        "visuals": {
            "status": "detected",
            "recommended_faceplate": "",
            "optional_faceplates": [],
            "calibration_profile": "",
            "canvas": {"width": 2048, "height": 448},
        },
    },
]

insert_after = next(i for i, item in enumerate(devices) if str(item.get("model")) == "US 48 PoE 500W")
for new_item in reversed(new_devices):
    model = new_item["model"]
    if model not in by_model:
        devices.insert(insert_after + 1, new_item)
        by_model[model] = new_item

with REGISTRY.open("w", encoding="utf-8", newline="\n") as handle:
    yaml.dump(registry, handle)

print("SV-2026-000002 review patch applied")
