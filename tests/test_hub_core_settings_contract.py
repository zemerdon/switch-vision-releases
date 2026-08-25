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

print('Core Hub settings contract: PASS')
