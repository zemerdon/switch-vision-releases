from __future__ import annotations

from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.4.15"
CARD = ROOT / "src/js/switch-vision.js"


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement target, found {count}")
    write(path, text.replace(old, new, 1))


def replace_exact_count(path: Path, old: str, new: str, expected: int) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{path}: expected {expected} replacement targets, found {count}")
    write(path, text.replace(old, new))


def replace_anchored_block(path: Path, anchor: str, start: str, end: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    anchor_pos = text.find(anchor)
    if anchor_pos < 0:
        raise SystemExit(f"{path}: anchor not found: {anchor}")
    start_pos = text.find(start, anchor_pos)
    if start_pos < 0:
        raise SystemExit(f"{path}: start marker not found after anchor")
    end_pos = text.find(end, start_pos)
    if end_pos < 0:
        raise SystemExit(f"{path}: end marker not found after anchor")
    write(path, text[:start_pos] + replacement + text[end_pos:])


if (ROOT / "VERSION").read_text(encoding="utf-8").strip() != "2.4.14":
    raise SystemExit("Core preparation expected the 2.4.14 main baseline")

# Keep the generic/SNMP row contract unchanged, but teach the renderer labels
# for API-native rows selected only by the UniFi-aware presentation path.
replace_once(
    CARD,
    'labels: { model: "MODEL", vendor: "VENDOR", os: "OS", firmware: "FIRMWARE", serial: "SERIAL", stack: "STACK", cpu: "CPU", temp: "TEMP", uptime: "UPTIME", fans: "FANS", psu: "PSU", poe: "POE", ip: "IP" }',
    'labels: { model: "MODEL", vendor: "VENDOR", os: "OS", firmware: "FIRMWARE", serial: "SERIAL", stack: "STACK", cpu: "CPU", memory: "MEMORY", temp: "TEMP", uptime: "UPTIME", uplink: "UPLINK", fans: "FANS", psu: "PSU", poe: "POE", ip: "IP" }',
)
replace_exact_count(
    CARD,
    'labels: { vlan: "VLAN", mode: "MODE", desc: "DESC", link: "LINK", rx: "RX", tx: "TX" }',
    'labels: { vlan: "VLAN", mode: "MODE", desc: "DESC", link: "LINK", rx: "RX", tx: "TX", max_speed: "MAX", media: "MEDIA", poe: "POE", poe_standard: "STANDARD" }',
    2,
)
replace_once(
    CARD,
    '''      unifi_refresh_seconds: 30,\n      unifi_per_port_traffic: false,\n      port_count: 0,''',
    '''      unifi_refresh_seconds: 30,\n      unifi_per_port_traffic: false,\n      unifi_native_status_fields: true,\n      port_count: 0,''',
)

# API-native formatting and capability helpers. These use only normalized
# UniFi2MQTT fields and never manufacture telemetry that the API did not return.
helper_anchor = '''function unifiSfpPort(config, port) {\n  if (String(config?.data_source || "").toLowerCase() !== "unifi_api") return null;\n  const index = unifiApiPortIndex(config, "sfp", port);\n  return index == null ? null : unifiPortByIndex(config, index);\n}\n'''
helpers = helper_anchor + '''\nfunction formatUnifiCapabilitySpeed(value) {\n  const n = Number(value);\n  if (!Number.isFinite(n) || n <= 0) return "—";\n  if (n >= 1000) {\n    const g = n / 1000;\n    const label = Number.isInteger(g) ? String(g) : g.toFixed(1).replace(/\\.0$/, "");\n    return `${label}G`;\n  }\n  return `${n}M`;\n}\n\nfunction formatUnifiConnector(value) {\n  const raw = String(value || "").trim().toUpperCase();\n  if (raw === "SFPPLUS" || raw === "SFP+") return "SFP+";\n  if (raw === "SFP28") return "SFP28";\n  if (raw === "SFP") return "SFP";\n  if (raw === "RJ45") return "RJ45";\n  return raw || "—";\n}\n\nfunction formatUnifiRate(value) {\n  const n = Number(value);\n  return Number.isFinite(n) && n >= 0 ? formatBps(n) : "—";\n}\n\nfunction unifiPoePortState(port) {\n  const poe = port?.poe && typeof port.poe === "object" ? port.poe : null;\n  if (!poe?.available) return "—";\n  if (String(poe.state || "").toUpperCase() === "UP") return "ACTIVE";\n  if (poe.enabled === true) return "ENABLED";\n  if (poe.enabled === false) return "OFF";\n  return "AVAILABLE";\n}\n\nfunction unifiPoeStandard(port) {\n  const poe = port?.poe && typeof port.poe === "object" ? port.poe : null;\n  if (!poe?.available) return "—";\n  const standard = usableValue(poe.standard);\n  const type = usableValue(poe.type);\n  if (standard && type) {\n    const typeLabel = /^\\d+$/.test(String(type)) ? `Type ${type}` : String(type);\n    return `${standard} ${typeLabel}`;\n  }\n  return standard || type || "—";\n}\n\nfunction unifiSwitchPoeSummary(runtime) {\n  const ports = Array.isArray(runtime?.ports) ? runtime.ports : [];\n  const poePorts = ports.filter((port) => port?.poe?.available);\n  if (!poePorts.length) return { available: false, label: "—" };\n  const active = poePorts.filter((port) => String(port?.poe?.state || "").toUpperCase() === "UP").length;\n  const enabled = poePorts.filter((port) => port?.poe?.enabled === true).length;\n  return {\n    available: true,\n    label: active > 0 ? `${active} active / ${poePorts.length}` : `${enabled} enabled / ${poePorts.length}`\n  };\n}\n\nfunction hasExplicitStatusPanelFields(config, type, panelNumber = 1) {\n  const prefix = panelNumber === 2 ? "status_panel_2" : "status_panel";\n  if (fieldListFromValue(config?.[`${prefix}_${type}_fields`])) return true;\n  const generic = config?.[`${prefix}_fields`];\n  if (Array.isArray(generic) || typeof generic === "string") {\n    return type === "switch" && Boolean(fieldListFromValue(generic));\n  }\n  return Boolean(generic && typeof generic === "object" && fieldListFromValue(generic[type]));\n}\n\nfunction useUnifiNativeStatusFields(config, type, panelNumber = 1) {\n  return panelNumber === 1\n    && String(config?.data_source || "").toLowerCase() === "unifi_api"\n    && config?.unifi_native_status_fields !== false\n    && !hasExplicitStatusPanelFields(config, type, panelNumber);\n}\n'''
replace_once(CARD, helper_anchor, helpers)

# Enrich the UniFi switch summary from real normalized runtime data. The IP
# fallback is backward-compatible with older snapshots and manual card config.
switch_runtime = '''  const runtime = unifiRuntime(config);\n  if (runtime) {\n    const system = runtime.system && typeof runtime.system === "object" ? runtime.system : {};\n    const poeSummary = unifiSwitchPoeSummary(runtime);\n    const uplinkRx = formatUnifiRate(system.uplink_rx_rate_bps);\n    const uplinkTx = formatUnifiRate(system.uplink_tx_rate_bps);\n    const uplink = uplinkRx === "—" && uplinkTx === "—" ? "—" : `RX ${uplinkRx} / TX ${uplinkTx}`;\n    return {\n      member,\n      model: usableValue(runtime.model) || usableValue(config.switch_model) || "—",\n      vendor: "Ubiquiti",\n      os: "UniFi Network",\n      firmware: usableValue(runtime.firmware) || "—",\n      serial: "—",\n      stack: "Standalone",\n      cpu: formatPercent(system.cpu_utilization_pct),\n      memory: formatPercent(system.memory_utilization_pct),\n      temp: "—",\n      uptime: formatUptimeSeconds(system.uptime_sec),\n      fans: "—",\n      psu: "—",\n      poe: poeSummary.label,\n      poeAvailable: poeSummary.available,\n      ip: usableValue(runtime.ip_address) || usableValue(runtime.ipAddress) || explicitConfigValue(config, ["switch_ip", "management_ip"]) || "—",\n      uplink,\n      uplink_rx: uplinkRx,\n      uplink_tx: uplinkTx,\n    };\n  }'''
replace_anchored_block(
    CARD,
    "function switchStatusValues(hass, config, cal = calibration)",
    "  const runtime = unifiRuntime(config);",
    "\n\n  const cpu = firstEntityValue(hass, [",
    switch_runtime,
)

replace_once(
    CARD,
    '''  let fields = statusPanelFieldSelection(config, "switch", cal, panelNumber);\n  if (!values.poeAvailable) fields = fields.filter((field) => field !== "poe");''',
    '''  let fields = statusPanelFieldSelection(config, "switch", cal, panelNumber);\n  if (useUnifiNativeStatusFields(config, "switch", panelNumber)) {\n    fields = values.poeAvailable\n      ? ["model", "ip", "cpu", "memory", "poe", "uptime"]\n      : ["model", "ip", "cpu", "memory", "uplink", "uptime"];\n  }\n  if (!values.poeAvailable) fields = fields.filter((field) => field !== "poe");''',
)

# Selected-port panels use the physical details the UniFi API actually exposes
# instead of presenting VLAN/DESC/RX/TX rows that cannot be populated.
replace_anchored_block(
    CARD,
    "let rows;\n  if (selected?.type === \"port\")",
    '''  if (selected?.type === "port") {''',
    '''  } else if (selected?.type === "sfp") {''',
    '''  if (selected?.type === "port") {\n    const details = selectedPortDetails(hass, config, selected.id);\n    const rates = portTrafficRates(hass, config, selected.id);\n    const unifi = unifiAccessPort(config, selected.id);\n    const values = {\n      vlan: details.vlan,\n      mode: details.mode,\n      desc: details.description,\n      link: details.link,\n      rx: formatBps(rates.rxBps),\n      tx: formatBps(rates.txBps),\n      max_speed: unifi ? formatUnifiCapabilitySpeed(unifi.max_speed_mbps) : "—",\n      media: unifi ? formatUnifiConnector(unifi.connector) : "—",\n      poe: unifiPoePortState(unifi),\n      poe_standard: unifiPoeStandard(unifi)\n    };\n    let fields = statusPanelFieldSelection(config, "port", cal, panelNumber);\n    if (useUnifiNativeStatusFields(config, "port", panelNumber)) {\n      fields = unifi?.poe?.available\n        ? ["link", "max_speed", "media", "poe", "poe_standard"]\n        : ["link", "max_speed", "media"];\n    } else if (!details.isJuniper) {\n      // MODE is a Juniper-only optional row for the generic/SNMP path.\n      fields = fields.filter((field) => field !== "mode");\n    }\n    const labels = { ...STATUS_PANEL_ROW_DEFS.port.labels, vlan: details.vlanLabel || "VLAN" };\n    rows = makeRows(values, fields, labels);\n''',
)

replace_anchored_block(
    CARD,
    '''  } else if (selected?.type === "sfp") {''',
    '''  } else if (selected?.type === "sfp") {''',
    '''  } else {\n    rows = switchSummaryDetails(hass, config, cal, panelNumber).rows;\n  }''',
    '''  } else if (selected?.type === "sfp") {\n    const details = selectedSfpDetails(hass, config, selected.id);\n    const rates = sfpTrafficRates(hass, config, selected.id);\n    const unifi = unifiSfpPort(config, selected.id);\n    const values = {\n      vlan: details.vlan,\n      mode: details.mode,\n      desc: details.description,\n      link: details.link,\n      rx: formatBps(rates.rxBps),\n      tx: formatBps(rates.txBps),\n      max_speed: unifi ? formatUnifiCapabilitySpeed(unifi.max_speed_mbps) : "—",\n      media: unifi ? formatUnifiConnector(unifi.connector) : "—",\n      poe: unifiPoePortState(unifi),\n      poe_standard: unifiPoeStandard(unifi)\n    };\n    let fields = statusPanelFieldSelection(config, "sfp", cal, panelNumber);\n    if (useUnifiNativeStatusFields(config, "sfp", panelNumber)) {\n      fields = unifi?.poe?.available\n        ? ["link", "max_speed", "media", "poe", "poe_standard"]\n        : ["link", "max_speed", "media"];\n    } else if (!details.isJuniper) {\n      fields = fields.filter((field) => field !== "mode");\n    }\n    rows = makeRows(values, fields, STATUS_PANEL_ROW_DEFS.sfp.labels);\n  }''',
)

write(ROOT / "VERSION", VERSION + "\n")

release_notes = f'''# Switch Vision Core v{VERSION}\n\nCore {VERSION} makes the dashboard status panels data-source aware for UniFi API devices.\n\nThe main UniFi switch summary now prioritizes telemetry the official Integration API actually provides: model, management IP when supplied by UniFi2MQTT 2.0.49 or newer, CPU, memory, uptime, real PoE capability/active-port summary where applicable, and live aggregate uplink RX/TX rate where PoE is not available.\n\nSelected UniFi ports now show negotiated link speed, maximum physical capability, connector/media type, and real PoE state/standard when the API provides it. Switch Vision no longer wastes the default UniFi port panel on VLAN, description, or per-port RX/TX rows that the current Integration API path cannot populate. Temperature and per-port traffic remain absent rather than being synthesized.\n\nSNMP-backed cards keep their existing status-panel behavior unchanged. Explicit card-level status-field configuration is respected, and `unifi_native_status_fields: false` restores the generic field-selection path for UniFi cards.\n'''
write(ROOT / "RELEASE_NOTES.md", release_notes)
write(ROOT / "src/RELEASE_NOTES.md", release_notes)

entry = f'''## v{VERSION} — UniFi-native status telemetry\n\n- Make the primary status panel data-source aware for UniFi API cards so it presents telemetry the Integration API actually exposes instead of defaulting to SNMP-only blank rows.\n- Surface normalized management IP, memory utilization and aggregate uplink RX/TX rate in the UniFi switch summary when available.\n- Derive switch-level PoE availability/activity from real UniFi port metadata and show connector type, maximum physical speed, PoE state and PoE standard in selected-port details.\n- Keep temperature, VLAN/description and per-port RX/TX absent when the current UniFi API path does not expose them; no synthetic telemetry is introduced.\n- Preserve existing SNMP status-panel behavior and explicit field configuration; `unifi_native_status_fields: false` restores the generic UniFi row-selection path.\n- Add permanent regressions for the UniFi-native field contract, management-IP fallback, PoE presentation and preserved per-port-traffic boundary.\n\n'''
for changelog_path in (ROOT / "CHANGELOG.md", ROOT / "src/CHANGELOG.md"):
    text = changelog_path.read_text(encoding="utf-8")
    if f"## v{VERSION} —" in text:
        raise SystemExit(f"{changelog_path}: v{VERSION} changelog entry already exists")
    write(changelog_path, entry + text)

regression = r'''from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "src/js/switch-vision.js",
    ROOT / "src/custom_components/switch_vision/switch-vision-card.js",
]


def main() -> None:
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        assert "unifi_native_status_fields: true" in text, path
        assert "usableValue(runtime.ip_address)" in text, path
        assert '["model", "ip", "cpu", "memory", "poe", "uptime"]' in text, path
        assert '["model", "ip", "cpu", "memory", "uplink", "uptime"]' in text, path
        assert '["link", "max_speed", "media", "poe", "poe_standard"]' in text, path
        assert '["link", "max_speed", "media"]' in text, path
        assert 'poeSummary = unifiSwitchPoeSummary(runtime)' in text, path
        assert 'function formatUnifiCapabilitySpeed(value)' in text, path
        assert 'function useUnifiNativeStatusFields(config, type, panelNumber = 1)' in text, path
        # The established generic/SNMP rows must not change as a side effect.
        assert 'defaults: ["vlan", "mode", "desc", "link", "rx", "tx"]' in text, path
        assert 'defaults: ["model", "ip", "cpu", "temp", "poe", "uptime", "vendor", "os", "firmware", "serial", "stack", "fans", "psu"]' in text, path
        # UniFi per-port traffic remains explicitly disabled unless a future API
        # genuinely exposes it; this release must not fabricate byte counters.
        assert 'config?.unifi_per_port_traffic !== true' in text, path
    print("UniFi-native status panel regressions: PASS")


if __name__ == "__main__":
    main()
'''
write(ROOT / "tests/test_unifi_native_status_panel.py", regression)

subprocess.run(["python3", "build.py", "-v", VERSION], cwd=ROOT, check=True)

for generated in (
    ROOT / f"Releases/switch-vision-{VERSION}.zip",
    ROOT / f"Releases/switch-vision-{VERSION}.zip.sha256",
    ROOT / f"Switch_Vision_v{VERSION}_source.zip",
    ROOT / f"Switch_Vision_v{VERSION}_SHA256SUMS.txt",
):
    generated.unlink(missing_ok=True)

subprocess.run(["node", "--check", "src/js/switch-vision.js"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/custom_components/switch_vision/switch-vision-card.js"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/custom_components/switch_vision/switch-vision-panel.js"], cwd=ROOT, check=True)
subprocess.run(["python3", "tools/check_core_release_parity.py"], cwd=ROOT, check=True)

for path in sorted((ROOT / "tests").glob("test_*.py")):
    subprocess.run(["python3", str(path.relative_to(ROOT))], cwd=ROOT, check=True)

print(f"Core {VERSION} preparation and regression suite: PASS")
