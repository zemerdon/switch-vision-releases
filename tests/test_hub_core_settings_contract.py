from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INIT = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text(encoding="utf-8")
FLOW = (ROOT / "src/custom_components/switch_vision/config_flow.py").read_text(encoding="utf-8")

for marker in (
    'switch_vision/get_settings',
    'switch_vision/set_settings',
    'CORE_SETTINGS_GROUP_KEYS',
    '_core_settings_payload',
    '_normalise_core_settings_update',
    'websocket_get_core_settings',
    'websocket_set_core_settings',
    '@websocket_api.require_admin',
    'hass.config_entries.async_update_entry(entry, options=options)',
    'reset_to_defaults',
    'Unknown Core settings group',
    'Unknown Core setting',
    'fast_period <= medium_period <= slow_period',
    'slow_max >= medium_max',
):
    assert marker in INIT, marker

for option in (
    'CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS',
    'CONF_SHOW_PANEL_IN_SIDEBAR',
    'CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR',
    'CONF_SHOW_HUB_IN_SIDEBAR',
    'CONF_SHOW_INSTALLER_IN_SIDEBAR',
    'CONF_SHOW_DASHBOARD_HEADER',
    'CONF_NATIVE_HEADER_SHOW_SUMMARY',
    'CONF_NATIVE_HEADER_SHOW_REFRESH',
    'CONF_NATIVE_HEADER_SHOW_VERSION',
    'CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS',
    'CONF_NATIVE_HEADER_SHORTCUT_HUB',
    'CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE',
    'CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS',
    'CONF_NATIVE_HEADER_SHORTCUT_INSTALLER',
    'CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS',
    'CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS',
    'CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS',
    'CONF_NATIVE_HEADER_SHORTCUT_ORDER',
    'CONF_SHOW_CALIBRATION_BUTTONS',
    'CONF_SHOW_CARD_HEADERS',
    'CONF_ACTIVITY_LED_SENSITIVITY_PRESET',
    'CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT',
    'CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT',
    'CONF_ACTIVITY_SLOW_PERIOD_MS',
    'CONF_ACTIVITY_MEDIUM_PERIOD_MS',
    'CONF_ACTIVITY_FAST_PERIOD_MS',
    'CONF_ACTIVITY_HOLD_SECONDS',
    'CONF_ACTIVITY_HYSTERESIS_PCT',
    'CONF_DISCOVERY_UI_DENSITY',
    'CONF_DISCOVERY_TEXT_SIZE',
    'CONF_DISCOVERY_CONTENT_WIDTH',
    'CONF_SHOW_UNIFI_INTEGRATION',
    'CONF_INSTALLER_UI_DENSITY',
    'CONF_INSTALLER_TEXT_SIZE',
    'CONF_INSTALLER_CONTENT_WIDTH',
):
    assert option in INIT, option

# The native Home Assistant Configure screen remains a synchronized fallback.
assert 'class SwitchVisionOptionsFlow' in FLOW
assert 'DEFAULT_OPTIONS' in FLOW
assert 'switch_vision/get_ui_settings' in INIT
assert 'switch_vision/set_native_header_shortcut_order' in INIT

# Explicit 10-20 px text-size contract with backward compatibility for the
# two legacy labels shipped through Core 2.6.2. Execute the real helper body so
# this is a behavioral regression rather than a string-only marker check.
import ast

tree = ast.parse(INIT)
helper = next(
    node for node in tree.body
    if isinstance(node, ast.FunctionDef) and node.name == 'normalise_ui_text_size'
)
namespace = {
    'Any': object,
    'UI_TEXT_SIZE_MIN_PX': 10,
    'UI_TEXT_SIZE_MAX_PX': 20,
    'UI_TEXT_SIZE_DEFAULT_PX': 16,
    'UI_TEXT_SIZE_LEGACY': {'normal': 16, 'small': 14},
}
exec(compile(ast.Module(body=[helper], type_ignores=[]), '<ui-text-size>', 'exec'), namespace)
normalise = namespace['normalise_ui_text_size']
assert normalise('normal') == 16
assert normalise('small') == 14
for pixels in range(10, 21):
    assert normalise(pixels) == pixels
    assert normalise(str(pixels)) == pixels
    assert normalise(f'{pixels}px') == pixels
for invalid in (9, 21, '9', '21px', '', 'giant', None, True, 14.5):
    assert normalise(invalid) == 16
assert 'CONF_DISCOVERY_TEXT_SIZE: (UI_TEXT_SIZE_MIN_PX, UI_TEXT_SIZE_MAX_PX)' in INIT
assert 'CONF_INSTALLER_TEXT_SIZE: (UI_TEXT_SIZE_MIN_PX, UI_TEXT_SIZE_MAX_PX)' in INIT
assert 'vol.In(\n                                list(range(UI_TEXT_SIZE_MIN_PX, UI_TEXT_SIZE_MAX_PX + 1))' in FLOW

print('Core Hub settings contract: PASS')
