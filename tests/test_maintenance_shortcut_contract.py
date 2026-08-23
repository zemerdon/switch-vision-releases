from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text(encoding="utf-8")
FLOW = (ROOT / "src/custom_components/switch_vision/config_flow.py").read_text(encoding="utf-8")
PANEL = (ROOT / "src/custom_components/switch_vision/switch-vision-panel.js").read_text(encoding="utf-8")
STRINGS = (ROOT / "src/custom_components/switch_vision/strings.json").read_text(encoding="utf-8")
TRANSLATION = (ROOT / "src/custom_components/switch_vision/translations/en.json").read_text(encoding="utf-8")

assert 'CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE = "native_header_shortcut_maintenance"' in INIT
assert '"maintenance",' in INIT
assert '"maintenance": CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE' in INIT
assert 'CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE: True' in INIT
assert 'CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE' in FLOW
assert 'vol.Required(\n                    CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE,' in FLOW
assert 'maintenance: { label: "Maintenance", app: "discovery", path: `${panelPath("discovery")}?view=maintenance` }' in PANEL
assert '"native_header_shortcut_maintenance": "Shortcut: Maintenance"' in STRINGS
assert 'Open Switch Vision Hub directly to the Maintenance page.' in STRINGS
assert STRINGS == TRANSLATION
assert INIT.index('"hub",') < INIT.index('"maintenance",') < INIT.index('"switch_vision_settings",')
print("Core 2.5.0 Maintenance shortcut contract: PASS")
