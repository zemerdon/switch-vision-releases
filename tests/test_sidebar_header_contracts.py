from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text(encoding="utf-8")
FLOW = (ROOT / "src/custom_components/switch_vision/config_flow.py").read_text(encoding="utf-8")
PANEL = (ROOT / "src/custom_components/switch_vision/switch-vision-panel.js").read_text(encoding="utf-8")
STRINGS = (ROOT / "src/custom_components/switch_vision/strings.json").read_text(encoding="utf-8")

for marker in (
    'CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS',
    'CONF_SHOW_HUB_IN_SIDEBAR',
    'CONF_SHOW_INSTALLER_IN_SIDEBAR',
    'AddonsOptions(ingress_panel=bool(show_in_sidebar))',
    'switch_vision/set_native_header_shortcut_order',
    'DATA_NATIVE_HEADER_SETTINGS',
    'DATA_ADDONS_LIST',
    '_resolve_switch_vision_app_slug',
    'slug.endswith(suffix)',
    '"panel_path": f"/{slug}"',
    '"config_path": f"/config/app/{slug}/config"',
    'NATIVE_HEADER_SHORTCUT_OPTION_KEYS',
):
    assert marker in INIT, marker

for marker in (
    'sidebar_hub_not_installed',
    'sidebar_installer_not_installed',
    'shortcut_snmp2mqtt_not_installed',
    'read_only',
    'vol.Required("native_header")',
):
    assert marker in FLOW, marker

for marker in (
    'Switch Vision Hub',
    '/config/integrations/integration/switch_vision',
    'location-changed',
    'shortcut-editor',
    'checkbox.type = "checkbox"',
    '_moveShortcut(id, -1)',
    '_moveShortcut(id, 1)',
    'Cancel',
    'Done',
    'set_native_header_shortcut_order',
    'this._hass?.user?.is_admin === true',
    'panel_path',
    'config_path',
):
    assert marker in PANEL, marker

assert 'hass-navigate' not in PANEL
assert 'dragstart' not in PANEL
assert '.draggable' not in PANEL
assert 'event.clientX < rect.left + rect.width / 2' not in PANEL
assert 'type: "supervisor/api"' not in PANEL
assert 'CONF_SHOW_HUB_IN_SIDEBAR in entry.options' in INIT
assert 'get("ingress_panel", True)' in INIT
assert 'CONF_SHOW_INSTALLER_IN_SIDEBAR in self.config_entry.options' in FLOW
assert 'discovery.get("ingress_panel", True)' in FLOW
assert 'installer.get("ingress_panel", True)' in FLOW
assert 'Not installed' in STRINGS
assert INIT.index("NATIVE_HEADER_SHORTCUT_IDS = (") < INIT.index("SET_NATIVE_HEADER_ORDER_WS_SCHEMA = {")
assert 'switch_vision/get_app_states' in INIT
assert 'websocket_get_app_states' in INIT
assert 'sidebar_master and lovelace_preference' in INIT
assert 'saved.pop(synthetic_key, None)' in FLOW
assert 'switch_vision/get_app_states' in PANEL
print('Core 2.4.5 sidebar/header contracts: PASS')
