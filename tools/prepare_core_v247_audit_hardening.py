#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
VERSION = "2.4.7"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


# 1) Home Assistant mutation services must be admin-only.
init_path = SRC / "custom_components" / "switch_vision" / "__init__.py"
init = read(init_path)
import_marker = "from homeassistant.helpers.storage import Store\n"
admin_import = "from homeassistant.helpers.service import async_register_admin_service\n"
if admin_import not in init:
    if import_marker not in init:
        raise SystemExit("Home Assistant helper import marker missing")
    init = init.replace(import_marker, admin_import + import_marker, 1)

service_replacements = {
    'hass.services.async_register(DOMAIN, "save_calibration", handle_save, schema=SAVE_SCHEMA)':
        'async_register_admin_service(hass, DOMAIN, "save_calibration", handle_save, schema=SAVE_SCHEMA)',
    'hass.services.async_register(DOMAIN, "delete_calibration", handle_delete, schema=DELETE_SCHEMA)':
        'async_register_admin_service(hass, DOMAIN, "delete_calibration", handle_delete, schema=DELETE_SCHEMA)',
    'hass.services.async_register(DOMAIN, "reset_calibrations", handle_reset, schema=RESET_SCHEMA)':
        'async_register_admin_service(hass, DOMAIN, "reset_calibrations", handle_reset, schema=RESET_SCHEMA)',
    'hass.services.async_register(DOMAIN, "reload_calibrations", handle_reload)':
        'async_register_admin_service(hass, DOMAIN, "reload_calibrations", handle_reload)',
    'hass.services.async_register(DOMAIN, "set_ui_density", handle_set_ui_density, schema=UI_DENSITY_SCHEMA)':
        'async_register_admin_service(hass, DOMAIN, "set_ui_density", handle_set_ui_density, schema=UI_DENSITY_SCHEMA)',
}
for old, new in service_replacements.items():
    if old not in init:
        raise SystemExit(f"Core admin-service marker missing: {old}")
    init = init.replace(old, new, 1)
write(init_path, init)

# 2) Align the Zyxel XS1930-10 visual with its proven 8 RJ45 + 2 SFP+ layout.
registry_path = SRC / "devices" / "supported_devices.yaml"
registry = read(registry_path)
model_marker = "  model: XS1930-10\n"
pos = registry.find(model_marker)
if pos < 0:
    raise SystemExit("XS1930-10 exact-model registry entry missing")
start = registry.rfind("\n- vendor:", 0, pos)
start = 0 if start < 0 else start + 1
end = registry.find("\n- vendor:", pos)
end = len(registry) if end < 0 else end
block = registry[start:end]
required = {
    "  calibration_profile: stock_24rj45_2sfp": "  calibration_profile: cisco_3560cg_8pc",
    "  default_faceplate: faceplates/24rj45-2sfp.png": "  default_faceplate: faceplates/c3560cg-8pc-s.png",
    "    recommended_faceplate: faceplates/24rj45-2sfp.png": "    recommended_faceplate: faceplates/c3560cg-8pc-s.png",
    "    calibration_profile: stock_24rj45_2sfp": "    calibration_profile: cisco_3560cg_8pc",
    "      height: 448": "      height: 329",
}
for old, new in required.items():
    if old not in block:
        raise SystemExit(f"XS1930-10 visual marker missing: {old}")
    block = block.replace(old, new, 1)
old_note = (
    "  - Uses the stock 24-RJ45 + 2-SFP visual as the closest temporary fallback until\n"
    "    a Zyxel-specific faceplate is supplied."
)
new_note = (
    "  - Uses the existing compact 8-RJ45 + 2-SFP visual as the temporary fallback, "
    "matching the contributed physical port count until a Zyxel-specific faceplate is supplied."
)
if old_note in block:
    block = block.replace(old_note, new_note, 1)
registry = registry[:start] + block + registry[end:]
write(registry_path, registry)

# 3) Permanent regression for admin-only mutation services.
admin_test = ROOT / "tests" / "test_admin_service_contracts.py"
write(admin_test, '''#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "src" / "custom_components" / "switch_vision" / "__init__.py").read_text(encoding="utf-8")

assert "from homeassistant.helpers.service import async_register_admin_service" in source
services = {
    "save_calibration": "SAVE_SCHEMA",
    "delete_calibration": "DELETE_SCHEMA",
    "reset_calibrations": "RESET_SCHEMA",
    "reload_calibrations": None,
    "set_ui_density": "UI_DENSITY_SCHEMA",
}
for name, schema in services.items():
    marker = f'async_register_admin_service(hass, DOMAIN, "{name}"'
    assert marker in source, f"{name} is not registered through Home Assistant's admin-service helper"
    assert f'hass.services.async_register(DOMAIN, "{name}"' not in source, f"{name} still has ordinary service registration"
    if schema:
        line = next(line for line in source.splitlines() if marker in line)
        assert f"schema={schema}" in line, f"{name} lost its validation schema"

# Native-header ordering remains separately protected at the WebSocket layer.
ws_marker = "async def websocket_set_native_header_shortcut_order"
pos = source.index(ws_marker)
prefix = source[max(0, pos - 250):pos]
assert "@websocket_api.require_admin" in prefix
print("Core admin-only mutation service contract: PASS")
''')

# 4) Permanent Zyxel exact-model visual regression.
zyxel_test = ROOT / "tests" / "test_zyxel_visual_defaults.py"
write(zyxel_test, '''#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
payload = json.loads((ROOT / "src" / "devices" / "supported_devices.json").read_text(encoding="utf-8"))
row = next(item for item in payload["devices"] if item.get("model") == "XS1930-10")

assert row["ports"]["rj45"] == 8
assert row["ports"]["uplinks"] == 2
assert row["calibration_profile"] == "cisco_3560cg_8pc"
assert row["default_faceplate"] == "faceplates/c3560cg-8pc-s.png"
visuals = row["visuals"]
assert visuals["recommended_faceplate"] == "faceplates/c3560cg-8pc-s.png"
assert visuals["calibration_profile"] == "cisco_3560cg_8pc"
assert visuals["canvas"] == {"width": 2048, "height": 329}
print("Core XS1930-10 visual default contract: PASS")
''')

# 5) Repair the missing 2.4.6 changelog entry and add 2.4.7.
entry_246 = '''## v2.4.6 — UniFi dark alternative faceplate\n\n- Add `unifi-24-rj45-2sfp-dark.png` as a manually selectable alternative UniFi faceplate.\n- Use the exact factory calibration geometry/defaults of `unifi-24p-rj45-2sfp.png`.\n- Keep the dark artwork manual-only: no exact-model mapping, no default replacement, and no change to existing UniFi device recommendations.\n- Add permanent regression coverage proving the alternative remains unmapped and calibration-equivalent.\n\n'''
entry_247 = '''## v2.4.7 — Audit hardening\n\n- Register calibration and Switch Vision UI mutation services with Home Assistant's admin-only service helper, including save/delete/reset/reload calibration actions and UI density changes.\n- Add permanent regression coverage proving those mutation services cannot regress to ordinary service registration.\n- Align Zyxel XS1930-10 visual defaults with its contributed physical 8-RJ45 + 2-SFP+ layout using the existing compact 8+2 calibration/faceplate fallback.\n- Add a permanent XS1930-10 visual-default regression.\n- Make permanent Core CI execute every `tests/test_*.py` regression automatically in isolated Python processes (workflow wiring applied in the release PR).\n- Restore the missing Core 2.4.6 changelog entry.\n\n'''
for changelog_path in (ROOT / "CHANGELOG.md", SRC / "CHANGELOG.md"):
    text = read(changelog_path)
    if "## v2.4.6" not in text:
        text = entry_246 + text
    if "## v2.4.7" not in text:
        text = entry_247 + text
    write(changelog_path, text)

notes = '''# Switch Vision Core v2.4.7\n\nCore 2.4.7 is an audit-hardening release. Calibration/UI mutation services are now admin-only, permanent regression coverage is expanded, and the Zyxel XS1930-10 factory visual is aligned to its contributed 8-RJ45 + 2-SFP+ physical layout.\n\nNo SNMP telemetry, Activity LED, Discovery handoff, saved calibration format, or existing non-Zyxel device mapping semantics are changed by this release.\n'''
write(ROOT / "RELEASE_NOTES.md", notes)
write(SRC / "RELEASE_NOTES.md", notes)

print("Prepared Switch Vision Core v2.4.7 audit hardening")
