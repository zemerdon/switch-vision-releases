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
    '/app/switch_vision_discovery',
    '/config/app/switch_vision_discovery/config',
    '/config/app/switch_vision_installer/config',
    '/config/app/switch_vision_snmp2mqtt/config',
    '/config/app/switch_vision_unifi2mqtt/config',
    'Drag shortcuts, then Done',
    'set_native_header_shortcut_order',
    'overflow-x:auto',
):
    assert marker in PANEL, marker

assert 'CONF_SHOW_HUB_IN_SIDEBAR in entry.options' in INIT
assert 'get("ingress_panel", True)' in INIT
assert 'CONF_SHOW_INSTALLER_IN_SIDEBAR in self.config_entry.options' in FLOW
assert 'discovery.get("ingress_panel", True)' in FLOW
assert 'installer.get("ingress_panel", True)' in FLOW
assert 'Not installed' in STRINGS

# Final 2.4.4 safety contracts.
assert INIT.index("NATIVE_HEADER_SHORTCUT_IDS = (") < INIT.index("SET_NATIVE_HEADER_ORDER_WS_SCHEMA = {")
assert 'switch_vision/get_app_states' in INIT
assert 'websocket_get_app_states' in INIT
assert 'sidebar_master and lovelace_preference' in INIT
assert 'saved.pop(synthetic_key, None)' in FLOW
assert 'switch_vision/get_app_states' in PANEL
assert 'type: "supervisor/api"' not in PANEL
assert 'event.clientX < rect.left + rect.width / 2' in PANEL
print('Core 2.4.4 sidebar/header contracts: PASS')
