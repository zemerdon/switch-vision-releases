#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD_SOURCES = (
    ROOT / "src" / "js" / "switch-vision.js",
    ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js",
)
CHANGELOG = ROOT / "src" / "CHANGELOG.md"
RELEASE_NOTES = ROOT / "src" / "RELEASE_NOTES.md"
BUILD = ROOT / "build.py"

marker = '''function readFirstCounter(hass, entityIds) {
  return readFirstCounterSample(hass, entityIds)?.value ?? null;
}

function portByteEntity(config, port, direction) {'''
replacement = '''function readFirstCounter(hass, entityIds) {
  return readFirstCounterSample(hass, entityIds)?.value ?? null;
}

function unifiTrafficCounterSample(port, direction) {
  const key = direction === "rx" ? "rx_bytes" : direction === "tx" ? "tx_bytes" : "";
  if (!key) return null;
  const traffic = port?.traffic && typeof port.traffic === "object" ? port.traffic : null;
  if (!traffic || traffic.available !== true) return null;

  const value = Number(traffic[key]);
  if (!Number.isFinite(value) || value < 0) return null;

  const sampledAt = Number(traffic.sampled_at || 0);
  const updated = Number.isFinite(sampledAt) && sampledAt > 0 ? sampledAt * 1000 : 0;
  return { value, updated };
}

function portTrafficCounterSample(hass, config, port, direction) {
  const isUnifi = String(config?.data_source || "").toLowerCase() === "unifi_api";
  if (isUnifi && rawUnifiRuntime(config)) {
    const runtimePort = unifiAccessPort(config, port);
    return runtimePort ? unifiTrafficCounterSample(runtimePort, direction) : null;
  }
  return readCounterSample(hass, portByteEntity(config, port, direction));
}

function sfpTrafficCounterSample(hass, config, port, direction) {
  const isUnifi = String(config?.data_source || "").toLowerCase() === "unifi_api";
  if (isUnifi && rawUnifiRuntime(config)) {
    const runtimePort = unifiSfpPort(config, port);
    return runtimePort ? unifiTrafficCounterSample(runtimePort, direction) : null;
  }
  return readFirstCounterSample(hass, sfpByteEntities(config, port, direction));
}

function portByteEntity(config, port, direction) {'''

old_port = '''  const rx = readCounterSample(hass, portByteEntity(config, port, "rx"));
  const tx = readCounterSample(hass, portByteEntity(config, port, "tx"));'''
new_port = '''  const rx = portTrafficCounterSample(hass, config, port, "rx");
  const tx = portTrafficCounterSample(hass, config, port, "tx");'''

old_sfp = '''  const rx = readFirstCounterSample(hass, sfpByteEntities(config, port, "rx"));
  const tx = readFirstCounterSample(hass, sfpByteEntities(config, port, "tx"));'''
new_sfp = '''  const rx = sfpTrafficCounterSample(hass, config, port, "rx");
  const tx = sfpTrafficCounterSample(hass, config, port, "tx");'''


def patch_card(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    already_patched = "function unifiTrafficCounterSample(port, direction)" in text

    if not already_patched:
        if marker not in text:
            raise SystemExit(f"Core activity helper insertion marker not found in {path}")
        text = text.replace(marker, replacement, 1)

    old_port_count = text.count(old_port)
    if old_port_count:
        if old_port_count != 2:
            raise SystemExit(
                f"Expected two RJ45 activity/rate counter readers in {path}, found {old_port_count}"
            )
        text = text.replace(old_port, new_port)
    elif text.count(new_port) != 2:
        raise SystemExit(f"Core RJ45 activity readers are neither old nor fully patched in {path}")

    old_sfp_count = text.count(old_sfp)
    if old_sfp_count:
        if old_sfp_count != 2:
            raise SystemExit(
                f"Expected two SFP activity/rate counter readers in {path}, found {old_sfp_count}"
            )
        text = text.replace(old_sfp, new_sfp)
    elif text.count(new_sfp) != 2:
        raise SystemExit(f"Core SFP activity readers are neither old nor fully patched in {path}")

    path.write_text(text, encoding="utf-8", newline="\n")


for card_path in CARD_SOURCES:
    patch_card(card_path)

build_text = BUILD.read_text(encoding="utf-8")
old_release_guard = '''    if 'portByteEntity(config, port, "rx")' not in card_js or 'portByteEntity(config, port, "tx")' not in card_js:
        raise SystemExit("Release validation failed: counter-derived port activity is missing")
'''
new_release_guard = '''    activity_counter_markers = [
        'function portTrafficCounterSample(hass, config, port, direction)',
        'readCounterSample(hass, portByteEntity(config, port, direction))',
        'portTrafficCounterSample(hass, config, port, "rx")',
        'portTrafficCounterSample(hass, config, port, "tx")',
    ]
    missing_activity_markers = [marker for marker in activity_counter_markers if marker not in card_js]
    if missing_activity_markers:
        raise SystemExit(
            "Release validation failed: counter-derived port activity is missing: "
            + ", ".join(missing_activity_markers)
        )
'''
if old_release_guard in build_text:
    build_text = build_text.replace(old_release_guard, new_release_guard, 1)
elif new_release_guard not in build_text:
    raise SystemExit("Core release activity validation marker not found")
BUILD.write_text(build_text, encoding="utf-8", newline="\n")

changelog = CHANGELOG.read_text(encoding="utf-8")
anchor = "- Add permanent exact-model regressions that lock faceplate/profile pairs, preserve known-good compact UniFi mappings, and keep non-exact fallback models' physical counts authoritative.\n"
activity_bullets = (
    "- Consume UniFi2MQTT 4.0 per-port RX/TX counters directly from the fresh native UniFi snapshot for activity LEDs and throughput calculations, using each classic telemetry sample timestamp instead of requiring Home Assistant RX/TX sensor entities.\n"
    "- Fail native UniFi traffic closed when the runtime snapshot is stale or a port has no validated traffic enrichment, while retaining the legacy Home Assistant counter path when no native UniFi runtime has loaded.\n"
)
if activity_bullets not in changelog:
    if anchor not in changelog:
        raise SystemExit("Core 2.7.9 changelog insertion marker not found")
    changelog = changelog.replace(anchor, anchor + activity_bullets, 1)
old_status = "- Keep support-confidence states unchanged; this release corrects presentation assignments only and does not promote hardware validation status.\n"
new_status = "- Keep support-confidence states unchanged; this release corrects presentation assignments and completes the native UniFi2MQTT 4.0 activity-counter bridge without promoting hardware validation status.\n"
if old_status in changelog:
    changelog = changelog.replace(old_status, new_status, 1)
elif new_status not in changelog:
    raise SystemExit("Core 2.7.9 changelog support-status marker not found")
CHANGELOG.write_text(changelog, encoding="utf-8", newline="\n")

notes = RELEASE_NOTES.read_text(encoding="utf-8")
notes_anchor = "The release does not infer faceplates from vendor name alone and does not force a visually similar asset onto hardware whose physical topology has no exact bundled match. Permanent regressions now protect the corrected exact-model matrix and the true physical counts of intentional fallback models.\n"
notes_paragraph = "Core 2.7.9 also completes the frontend side of UniFi2MQTT 4.0 activity telemetry. When a fresh native UniFi runtime snapshot contains validated per-port traffic enrichment, the card now reads cumulative RX/TX counters and their sample timestamp directly from that snapshot for activity LEDs and throughput calculations. Raw counter entities do not need to be created in Home Assistant. Stale or unavailable native traffic fails closed, while older non-native entity-counter dashboards retain their existing compatibility path.\n"
if notes_paragraph not in notes:
    if notes_anchor not in notes:
        raise SystemExit("Core 2.7.9 release-note insertion marker not found")
    notes = notes.replace(notes_anchor, notes_anchor + "\n" + notes_paragraph, 1)
RELEASE_NOTES.write_text(notes, encoding="utf-8", newline="\n")

print("Core 2.7.9 native UniFi activity integration patch applied")
