#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "src/custom_components/switch_vision"
VERSION = "2.4.4"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


def replace_once(path: Path, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise SystemExit(f"Missing expected marker in {path}: {old[:120]!r}")
    write(path, text.replace(old, new, 1))


def regex_once(path: Path, pattern: str, replacement: str) -> None:
    text = read(path)
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"Expected one regex match in {path}, got {count}: {pattern}")
    write(path, updated)


# ---------------------------------------------------------------------------
# Core backend: centralized Switch Vision sidebar control + native header state.
# ---------------------------------------------------------------------------
init_py = COMP / "__init__.py"
text = read(init_py)

if "from aiohasupervisor import SupervisorError, SupervisorNotFoundError" not in text:
    text = text.replace(
        "import yaml\n\nfrom homeassistant.config_entries import ConfigEntry",
        "import yaml\n\nfrom aiohasupervisor import SupervisorError, SupervisorNotFoundError\n"
        "from aiohasupervisor.models import AddonsOptions\n\n"
        "from homeassistant.config_entries import ConfigEntry",
        1,
    )
if "from homeassistant.components.hassio.handler import get_supervisor_client" not in text:
    text = text.replace(
        "from homeassistant.components.http import StaticPathConfig\n",
        "from homeassistant.components.http import StaticPathConfig\n"
        "from homeassistant.components.hassio.handler import get_supervisor_client\n",
        1,
    )

constants_marker = 'CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR = "show_lovelace_dashboard_in_sidebar"\n'
constants_add = '''CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS = "show_all_switch_vision_sidebar_items"\nCONF_SHOW_HUB_IN_SIDEBAR = "show_hub_in_sidebar"\nCONF_SHOW_INSTALLER_IN_SIDEBAR = "show_installer_in_sidebar"\nCONF_NATIVE_HEADER_SHOW_SUMMARY = "native_header_show_summary"\nCONF_NATIVE_HEADER_SHOW_REFRESH = "native_header_show_refresh"\nCONF_NATIVE_HEADER_SHOW_VERSION = "native_header_show_version"\nCONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS = "native_header_shortcut_switch_vision_settings"\nCONF_NATIVE_HEADER_SHORTCUT_HUB = "native_header_shortcut_hub"\nCONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS = "native_header_shortcut_discovery_settings"\nCONF_NATIVE_HEADER_SHORTCUT_INSTALLER = "native_header_shortcut_installer"\nCONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS = "native_header_shortcut_installer_settings"\nCONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS = "native_header_shortcut_snmp2mqtt_settings"\nCONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS = "native_header_shortcut_unifi2mqtt_settings"\nCONF_NATIVE_HEADER_SHORTCUT_ORDER = "native_header_shortcut_order"\n\nDISCOVERY_APP_SLUG = "switch_vision_discovery"\nINSTALLER_APP_SLUG = "switch_vision_installer"\nSNMP2MQTT_APP_SLUG = "switch_vision_snmp2mqtt"\nUNIFI2MQTT_APP_SLUG = "switch_vision_unifi2mqtt"\n\nNATIVE_HEADER_SHORTCUT_IDS = (\n    "hub",\n    "switch_vision_settings",\n    "discovery_settings",\n    "installer",\n    "installer_settings",\n    "snmp2mqtt_settings",\n    "unifi2mqtt_settings",\n)\n'''
if constants_add not in text:
    if constants_marker not in text:
        raise SystemExit("sidebar constants marker missing")
    text = text.replace(constants_marker, constants_marker + constants_add, 1)

# Extend defaults immediately after the two existing sidebar defaults.
defaults_marker = '''    CONF_SHOW_PANEL_IN_SIDEBAR: True,\n    CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR: True,\n'''
defaults_add = '''    CONF_SHOW_PANEL_IN_SIDEBAR: True,\n    CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR: True,\n    CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS: True,\n    CONF_SHOW_HUB_IN_SIDEBAR: True,\n    CONF_SHOW_INSTALLER_IN_SIDEBAR: True,\n    CONF_NATIVE_HEADER_SHOW_SUMMARY: True,\n    CONF_NATIVE_HEADER_SHOW_REFRESH: True,\n    CONF_NATIVE_HEADER_SHOW_VERSION: True,\n    CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS: True,\n    CONF_NATIVE_HEADER_SHORTCUT_HUB: True,\n    CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS: True,\n    CONF_NATIVE_HEADER_SHORTCUT_INSTALLER: True,\n    CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS: True,\n    CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS: True,\n    CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS: True,\n    CONF_NATIVE_HEADER_SHORTCUT_ORDER: list(NATIVE_HEADER_SHORTCUT_IDS),\n'''
if defaults_add not in text:
    if defaults_marker not in text:
        raise SystemExit("DEFAULT_OPTIONS marker missing")
    text = text.replace(defaults_marker, defaults_add, 1)

if 'DATA_NATIVE_HEADER_SETTINGS = "native_header_settings"' not in text:
    text = text.replace(
        'DATA_ACTIVITY_LED_SETTINGS = "activity_led_settings"\n',
        'DATA_ACTIVITY_LED_SETTINGS = "activity_led_settings"\n'
        'DATA_NATIVE_HEADER_SETTINGS = "native_header_settings"\n',
        1,
    )

supervisor_helpers = '''\n\nasync def async_switch_vision_app_states(hass: HomeAssistant) -> dict[str, dict[str, Any]]:\n    """Return safe installed/ingress state for Switch Vision managed apps."""\n    specs = {\n        "discovery": DISCOVERY_APP_SLUG,\n        "installer": INSTALLER_APP_SLUG,\n        "snmp2mqtt": SNMP2MQTT_APP_SLUG,\n        "unifi2mqtt": UNIFI2MQTT_APP_SLUG,\n    }\n    states = {\n        key: {\n            "slug": slug,\n            "installed": False,\n            "ingress": False,\n            "ingress_panel": False,\n            "available": False,\n        }\n        for key, slug in specs.items()\n    }\n    try:\n        client = get_supervisor_client(hass)\n    except (KeyError, RuntimeError):\n        return states\n\n    for key, slug in specs.items():\n        try:\n            info = await client.addons.addon_info(slug)\n        except SupervisorNotFoundError:\n            continue\n        except SupervisorError as err:\n            _LOGGER.debug("Could not read Switch Vision app %s state: %s", slug, err)\n            continue\n        states[key] = {\n            "slug": slug,\n            "installed": True,\n            "ingress": bool(getattr(info, "ingress", False)),\n            "ingress_panel": bool(getattr(info, "ingress_panel", False)),\n            "available": bool(getattr(info, "available", True)),\n            "state": str(getattr(getattr(info, "state", None), "value", getattr(info, "state", "")) or ""),\n        }\n    return states\n\n\nasync def _sync_switch_vision_app_ingress_panel(\n    hass: HomeAssistant, slug: str, show_in_sidebar: bool\n) -> bool:\n    """Apply one supported Supervisor ingress-panel preference if installed."""\n    try:\n        client = get_supervisor_client(hass)\n        info = await client.addons.addon_info(slug)\n    except (KeyError, RuntimeError, SupervisorNotFoundError):\n        return False\n    except SupervisorError as err:\n        _LOGGER.warning("Could not read %s ingress-panel state: %s", slug, err)\n        return False\n\n    if not bool(getattr(info, "ingress", False)):\n        return False\n    if bool(getattr(info, "ingress_panel", False)) == bool(show_in_sidebar):\n        return True\n\n    try:\n        await client.addons.set_addon_options(\n            slug, AddonsOptions(ingress_panel=bool(show_in_sidebar))\n        )\n    except SupervisorError as err:\n        _LOGGER.warning("Could not update %s ingress-panel state: %s", slug, err)\n        return False\n    return True\n\n\ndef _native_header_settings(entry: ConfigEntry) -> dict[str, Any]:\n    """Return the ordered Native dashboard shortcut/header configuration."""\n    raw_order = entry.options.get(\n        CONF_NATIVE_HEADER_SHORTCUT_ORDER,\n        DEFAULT_OPTIONS[CONF_NATIVE_HEADER_SHORTCUT_ORDER],\n    )\n    order = []\n    for shortcut_id in raw_order if isinstance(raw_order, list) else []:\n        shortcut = str(shortcut_id)\n        if shortcut in NATIVE_HEADER_SHORTCUT_IDS and shortcut not in order:\n            order.append(shortcut)\n    order.extend(shortcut for shortcut in NATIVE_HEADER_SHORTCUT_IDS if shortcut not in order)\n    return {\n        "enabled": bool(entry.options.get(CONF_SHOW_DASHBOARD_HEADER, DEFAULT_OPTIONS[CONF_SHOW_DASHBOARD_HEADER])),\n        "show_summary": bool(entry.options.get(CONF_NATIVE_HEADER_SHOW_SUMMARY, DEFAULT_OPTIONS[CONF_NATIVE_HEADER_SHOW_SUMMARY])),\n        "show_refresh": bool(entry.options.get(CONF_NATIVE_HEADER_SHOW_REFRESH, DEFAULT_OPTIONS[CONF_NATIVE_HEADER_SHOW_REFRESH])),\n        "show_version": bool(entry.options.get(CONF_NATIVE_HEADER_SHOW_VERSION, DEFAULT_OPTIONS[CONF_NATIVE_HEADER_SHOW_VERSION])),\n        "order": order,\n        "shortcuts": {\n            "switch_vision_settings": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS, True)),\n            "hub": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_HUB, True)),\n            "discovery_settings": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS, True)),\n            "installer": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_INSTALLER, True)),\n            "installer_settings": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS, True)),\n            "snmp2mqtt_settings": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS, True)),\n            "unifi2mqtt_settings": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS, True)),\n        },\n    }\n'''
helper_marker = '\n\ndef _activity_led_settings(entry: ConfigEntry) -> dict[str, Any]:\n'
if supervisor_helpers not in text:
    if helper_marker not in text:
        raise SystemExit("activity helper marker missing")
    text = text.replace(helper_marker, supervisor_helpers + helper_marker, 1)

# Add WebSocket schema for admin-only shortcut reordering.
ws_marker = '''UI_SETTINGS_WS_SCHEMA = {\n    vol.Required("type"): "switch_vision/get_ui_settings",\n}\n'''
ws_add = '''UI_SETTINGS_WS_SCHEMA = {\n    vol.Required("type"): "switch_vision/get_ui_settings",\n}\n\nSET_NATIVE_HEADER_ORDER_WS_SCHEMA = {\n    vol.Required("type"): "switch_vision/set_native_header_shortcut_order",\n    vol.Required("order"): [vol.In(NATIVE_HEADER_SHORTCUT_IDS)],\n}\n'''
if ws_add not in text:
    if ws_marker not in text:
        raise SystemExit("UI_SETTINGS_WS_SCHEMA marker missing")
    text = text.replace(ws_marker, ws_add, 1)

# Enrich native dashboard payload with the header contract.
old_payload = '''        payload = await hass.async_add_executor_job(\n            _dashboard_file_payload,\n            dashboard_path,\n            bool(show_calibration_buttons),\n            bool(show_dashboard_header),\n            bool(show_card_headers),\n        )\n        connection.send_result(msg["id"], payload)\n'''
new_payload = '''        payload = await hass.async_add_executor_job(\n            _dashboard_file_payload,\n            dashboard_path,\n            bool(show_calibration_buttons),\n            bool(show_dashboard_header),\n            bool(show_card_headers),\n        )\n        payload["native_header"] = dict(\n            hass.data.setdefault(DOMAIN, {}).get(\n                DATA_NATIVE_HEADER_SETTINGS,\n                {\n                    "enabled": bool(show_dashboard_header),\n                    "show_summary": True,\n                    "show_refresh": True,\n                    "show_version": True,\n                    "order": list(NATIVE_HEADER_SHORTCUT_IDS),\n                    "shortcuts": {shortcut: True for shortcut in NATIVE_HEADER_SHORTCUT_IDS},\n                },\n            )\n        )\n        connection.send_result(msg["id"], payload)\n'''
if old_payload not in text:
    raise SystemExit("dashboard payload marker missing")
text = text.replace(old_payload, new_payload, 1)

# Admin-only WebSocket command to save a drag-reordered shortcut list.
register_marker = '    websocket_api.async_register_command(hass, websocket_get_ui_settings)\n'
order_handler = '''\n    @websocket_api.websocket_command(SET_NATIVE_HEADER_ORDER_WS_SCHEMA)\n    @websocket_api.require_admin\n    @websocket_api.async_response\n    async def websocket_set_native_header_shortcut_order(hass: HomeAssistant, connection, msg):\n        """Persist Native dashboard shortcut ordering from drag-and-drop customization."""\n        requested = [str(value) for value in msg.get("order", [])]\n        order = []\n        for shortcut in requested:\n            if shortcut in NATIVE_HEADER_SHORTCUT_IDS and shortcut not in order:\n                order.append(shortcut)\n        order.extend(shortcut for shortcut in NATIVE_HEADER_SHORTCUT_IDS if shortcut not in order)\n        entries = hass.config_entries.async_entries(DOMAIN)\n        if not entries:\n            connection.send_error(msg["id"], "not_configured", "Switch Vision integration is not configured")\n            return\n        entry = entries[0]\n        options = dict(entry.options)\n        options[CONF_NATIVE_HEADER_SHORTCUT_ORDER] = order\n        hass.config_entries.async_update_entry(entry, options=options)\n        connection.send_result(msg["id"], {"order": order})\n\n'''
if order_handler not in text:
    if register_marker not in text:
        raise SystemExit("websocket register marker missing")
    # Handler must be defined before registration block.
    text = text.replace(register_marker, order_handler + register_marker + '    websocket_api.async_register_command(hass, websocket_set_native_header_shortcut_order)\n', 1)

# Apply and synchronize the new sidebar/header options live.
apply_marker = '''    show_in_sidebar = bool(entry.options.get(CONF_SHOW_PANEL_IN_SIDEBAR, DEFAULT_OPTIONS[CONF_SHOW_PANEL_IN_SIDEBAR]))\n    show_lovelace_in_sidebar = bool(\n        entry.options.get(CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR, DEFAULT_OPTIONS[CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR])\n    )\n'''
apply_replacement = '''    sidebar_master = bool(\n        entry.options.get(\n            CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS,\n            DEFAULT_OPTIONS[CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS],\n        )\n    )\n    show_in_sidebar = sidebar_master and bool(\n        entry.options.get(CONF_SHOW_PANEL_IN_SIDEBAR, DEFAULT_OPTIONS[CONF_SHOW_PANEL_IN_SIDEBAR])\n    )\n    show_lovelace_in_sidebar = sidebar_master and bool(\n        entry.options.get(CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR, DEFAULT_OPTIONS[CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR])\n    )\n    show_hub_in_sidebar = sidebar_master and bool(\n        entry.options.get(CONF_SHOW_HUB_IN_SIDEBAR, DEFAULT_OPTIONS[CONF_SHOW_HUB_IN_SIDEBAR])\n    )\n    show_installer_in_sidebar = sidebar_master and bool(\n        entry.options.get(CONF_SHOW_INSTALLER_IN_SIDEBAR, DEFAULT_OPTIONS[CONF_SHOW_INSTALLER_IN_SIDEBAR])\n    )\n'''
if apply_marker not in text:
    raise SystemExit("apply sidebar marker missing")
text = text.replace(apply_marker, apply_replacement, 1)

state_marker = '    activity_led_settings = _activity_led_settings(entry)\n\n    domain_state = hass.data.setdefault(DOMAIN, {})\n'
state_replacement = '    activity_led_settings = _activity_led_settings(entry)\n    native_header_settings = _native_header_settings(entry)\n\n    domain_state = hass.data.setdefault(DOMAIN, {})\n'
if state_marker not in text:
    raise SystemExit("activity state marker missing")
text = text.replace(state_marker, state_replacement, 1)
text = text.replace(
    '    domain_state[DATA_ACTIVITY_LED_SETTINGS] = activity_led_settings\n',
    '    domain_state[DATA_ACTIVITY_LED_SETTINGS] = activity_led_settings\n'
    '    domain_state[DATA_NATIVE_HEADER_SETTINGS] = native_header_settings\n',
    1,
)
text = text.replace(
    '            "activity_leds": activity_led_settings,\n',
    '            "activity_leds": activity_led_settings,\n'
    '            "native_header": native_header_settings,\n',
    1,
)
text = text.replace(
    '        "show_card_headers": show_card_headers,\n    }\n',
    '        "show_card_headers": show_card_headers,\n'
    '        "native_header": native_header_settings,\n    }\n',
    1,
)

sync_marker = '''    try:\n        await _sync_switch_vision_lovelace_dashboard_sidebar(\n            hass, show_lovelace_in_sidebar\n        )\n    except (OSError, ValueError, TypeError) as err:\n        _LOGGER.warning(\n            "Could not update Switch Vision Lovelace dashboard sidebar visibility: %s",\n            err,\n        )\n'''
sync_add = sync_marker + '''\n    await _sync_switch_vision_app_ingress_panel(\n        hass, DISCOVERY_APP_SLUG, show_hub_in_sidebar\n    )\n    await _sync_switch_vision_app_ingress_panel(\n        hass, INSTALLER_APP_SLUG, show_installer_in_sidebar\n    )\n'''
if sync_add not in text:
    if sync_marker not in text:
        raise SystemExit("Lovelace sync marker missing")
    text = text.replace(sync_marker, sync_add, 1)

write(init_py, text)

# ---------------------------------------------------------------------------
# Integration Options flow.
# ---------------------------------------------------------------------------
config_flow = COMP / "config_flow.py"
text = read(config_flow)
if "from homeassistant.helpers import selector" not in text:
    text = text.replace(
        "from homeassistant.data_entry_flow import section\n",
        "from homeassistant.data_entry_flow import section\nfrom homeassistant.helpers import selector\n",
        1,
    )

# Extend imports from the integration module.
imports_to_add = [
    "CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS",
    "CONF_NATIVE_HEADER_SHORTCUT_HUB",
    "CONF_NATIVE_HEADER_SHORTCUT_INSTALLER",
    "CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS",
    "CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS",
    "CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS",
    "CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS",
    "CONF_NATIVE_HEADER_SHOW_REFRESH",
    "CONF_NATIVE_HEADER_SHOW_SUMMARY",
    "CONF_NATIVE_HEADER_SHOW_VERSION",
    "CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS",
    "CONF_SHOW_HUB_IN_SIDEBAR",
    "CONF_SHOW_INSTALLER_IN_SIDEBAR",
    "async_switch_vision_app_states",
]
for name in imports_to_add:
    if f"    {name},\n" not in text:
        text = text.replace("    DEFAULT_DASHBOARD_CONFIG_PATH,\n", f"    {name},\n    DEFAULT_DASHBOARD_CONFIG_PATH,\n", 1)

new_schema_method = r'''    async def _schema(self) -> vol.Schema:
        """Build grouped Core settings with installation-aware app controls."""
        app_states = await async_switch_vision_app_states(self.hass)
        discovery = app_states.get("discovery", {})
        installer = app_states.get("installer", {})
        snmp2mqtt = app_states.get("snmp2mqtt", {})
        unifi2mqtt = app_states.get("unifi2mqtt", {})

        read_only_bool = selector.selector({"boolean": {"read_only": True}})

        sidebar_fields: dict[Any, Any] = {
            vol.Required(
                CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS,
                default=self._value(CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS),
            ): bool,
            vol.Required(
                CONF_SHOW_PANEL_IN_SIDEBAR,
                default=self._value(CONF_SHOW_PANEL_IN_SIDEBAR),
            ): bool,
            vol.Required(
                CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR,
                default=self._value(CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR),
            ): bool,
        }
        if discovery.get("installed") and discovery.get("ingress"):
            sidebar_fields[
                vol.Required(
                    CONF_SHOW_HUB_IN_SIDEBAR,
                    default=self._value(CONF_SHOW_HUB_IN_SIDEBAR),
                )
            ] = bool
        else:
            sidebar_fields[vol.Optional("sidebar_hub_not_installed", default=False)] = read_only_bool
        if installer.get("installed") and installer.get("ingress"):
            sidebar_fields[
                vol.Required(
                    CONF_SHOW_INSTALLER_IN_SIDEBAR,
                    default=self._value(CONF_SHOW_INSTALLER_IN_SIDEBAR),
                )
            ] = bool
        else:
            sidebar_fields[vol.Optional("sidebar_installer_not_installed", default=False)] = read_only_bool

        header_fields: dict[Any, Any] = {
            vol.Required(
                CONF_SHOW_DASHBOARD_HEADER,
                default=self._value(CONF_SHOW_DASHBOARD_HEADER),
            ): bool,
            vol.Required(
                CONF_NATIVE_HEADER_SHOW_SUMMARY,
                default=self._value(CONF_NATIVE_HEADER_SHOW_SUMMARY),
            ): bool,
            vol.Required(
                CONF_NATIVE_HEADER_SHOW_REFRESH,
                default=self._value(CONF_NATIVE_HEADER_SHOW_REFRESH),
            ): bool,
            vol.Required(
                CONF_NATIVE_HEADER_SHOW_VERSION,
                default=self._value(CONF_NATIVE_HEADER_SHOW_VERSION),
            ): bool,
            vol.Required(
                CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS,
                default=self._value(CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS),
            ): bool,
        }
        if discovery.get("installed"):
            header_fields[
                vol.Required(
                    CONF_NATIVE_HEADER_SHORTCUT_HUB,
                    default=self._value(CONF_NATIVE_HEADER_SHORTCUT_HUB),
                )
            ] = bool
            header_fields[
                vol.Required(
                    CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS,
                    default=self._value(CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS),
                )
            ] = bool
        else:
            header_fields[vol.Optional("shortcut_discovery_not_installed", default=False)] = read_only_bool
        if installer.get("installed"):
            header_fields[
                vol.Required(
                    CONF_NATIVE_HEADER_SHORTCUT_INSTALLER,
                    default=self._value(CONF_NATIVE_HEADER_SHORTCUT_INSTALLER),
                )
            ] = bool
            header_fields[
                vol.Required(
                    CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS,
                    default=self._value(CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS),
                )
            ] = bool
        else:
            header_fields[vol.Optional("shortcut_installer_not_installed", default=False)] = read_only_bool
        if snmp2mqtt.get("installed"):
            header_fields[
                vol.Required(
                    CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS,
                    default=self._value(CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS),
                )
            ] = bool
        else:
            header_fields[vol.Optional("shortcut_snmp2mqtt_not_installed", default=False)] = read_only_bool
        if unifi2mqtt.get("installed"):
            header_fields[
                vol.Required(
                    CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS,
                    default=self._value(CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS),
                )
            ] = bool
        else:
            header_fields[vol.Optional("shortcut_unifi2mqtt_not_installed", default=False)] = read_only_bool

        return vol.Schema(
            {
                vol.Required("sidebar"): section(
                    vol.Schema(sidebar_fields),
                    {"collapsed": False},
                ),
                vol.Required("native_header"): section(
                    vol.Schema(header_fields),
                    {"collapsed": False},
                ),
                vol.Required("dashboard"): section(
                    vol.Schema(
                        {
                            vol.Required(
                                CONF_SHOW_CALIBRATION_BUTTONS,
                                default=self._value(CONF_SHOW_CALIBRATION_BUTTONS),
                            ): bool,
                            vol.Required(
                                CONF_SHOW_CARD_HEADERS,
                                default=self._value(CONF_SHOW_CARD_HEADERS),
                            ): bool,
                        }
                    ),
                    {"collapsed": True},
                ),
                vol.Required("activity_leds"): section(
                    vol.Schema(
                        {
                            vol.Required(
                                CONF_ACTIVITY_LED_SENSITIVITY_PRESET,
                                default=self._value(CONF_ACTIVITY_LED_SENSITIVITY_PRESET),
                            ): vol.In([*ACTIVITY_LED_PRESETS, "custom"]),
                            vol.Required(
                                CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT,
                                default=self._value(CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT),
                            ): vol.All(vol.Coerce(float), vol.Range(min=0.001, max=100.0)),
                            vol.Required(
                                CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT,
                                default=self._value(CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT),
                            ): vol.All(vol.Coerce(float), vol.Range(min=0.001, max=100.0)),
                            vol.Required(
                                CONF_ACTIVITY_SLOW_PERIOD_MS,
                                default=self._value(CONF_ACTIVITY_SLOW_PERIOD_MS),
                            ): vol.All(vol.Coerce(int), vol.Range(min=120, max=2000)),
                            vol.Required(
                                CONF_ACTIVITY_MEDIUM_PERIOD_MS,
                                default=self._value(CONF_ACTIVITY_MEDIUM_PERIOD_MS),
                            ): vol.All(vol.Coerce(int), vol.Range(min=120, max=2000)),
                            vol.Required(
                                CONF_ACTIVITY_FAST_PERIOD_MS,
                                default=self._value(CONF_ACTIVITY_FAST_PERIOD_MS),
                            ): vol.All(vol.Coerce(int), vol.Range(min=120, max=2000)),
                            vol.Required(
                                CONF_ACTIVITY_HOLD_SECONDS,
                                default=self._value(CONF_ACTIVITY_HOLD_SECONDS),
                            ): vol.All(vol.Coerce(float), vol.Range(min=1.0, max=120.0)),
                            vol.Required(
                                CONF_ACTIVITY_HYSTERESIS_PCT,
                                default=self._value(CONF_ACTIVITY_HYSTERESIS_PCT),
                            ): vol.All(vol.Coerce(float), vol.Range(min=0.0, max=50.0)),
                        }
                    ),
                    {"collapsed": True},
                ),
                vol.Required("discovery"): section(
                    vol.Schema(
                        {
                            vol.Required(
                                CONF_DISCOVERY_UI_DENSITY,
                                default=self._value(CONF_DISCOVERY_UI_DENSITY),
                            ): vol.In(["comfortable", "compact", "dense"]),
                            vol.Required(
                                CONF_DISCOVERY_TEXT_SIZE,
                                default=self._value(CONF_DISCOVERY_TEXT_SIZE),
                            ): vol.In(["normal", "small"]),
                            vol.Required(
                                CONF_DISCOVERY_CONTENT_WIDTH,
                                default=self._value(CONF_DISCOVERY_CONTENT_WIDTH),
                            ): vol.In(["standard", "wide", "full"]),
                            vol.Required(
                                CONF_SHOW_UNIFI_INTEGRATION,
                                default=self._value(CONF_SHOW_UNIFI_INTEGRATION),
                            ): bool,
                        }
                    ),
                    {"collapsed": True},
                ),
                vol.Required("installer"): section(
                    vol.Schema(
                        {
                            vol.Required(
                                CONF_INSTALLER_UI_DENSITY,
                                default=self._value(CONF_INSTALLER_UI_DENSITY),
                            ): vol.In(["comfortable", "compact", "dense"]),
                            vol.Required(
                                CONF_INSTALLER_TEXT_SIZE,
                                default=self._value(CONF_INSTALLER_TEXT_SIZE),
                            ): vol.In(["normal", "small"]),
                            vol.Required(
                                CONF_INSTALLER_CONTENT_WIDTH,
                                default=self._value(CONF_INSTALLER_CONTENT_WIDTH),
                            ): vol.In(["standard", "wide", "full"]),
                        }
                    ),
                    {"collapsed": True},
                ),
                vol.Optional(CONF_RESET_TO_DEFAULTS, default=False): bool,
            }
        )

'''
updated, count = re.subn(
    r"    def _schema\(self\) -> vol\.Schema:.*?(?=    async def async_step_init)",
    new_schema_method,
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f"Could not replace OptionsFlow _schema method ({count})")
text = updated
text = text.replace("data_schema=self._schema(),", "data_schema=await self._schema(),", 1)
text = text.replace(
    'for group in ("dashboard", "activity_leds", "discovery", "installer"):',
    'for group in ("sidebar", "native_header", "dashboard", "activity_leds", "discovery", "installer"):',
    1,
)
write(config_flow, text)

# ---------------------------------------------------------------------------
# Native dashboard shortcut header frontend.
# ---------------------------------------------------------------------------
panel = COMP / "switch-vision-panel.js"
text = read(panel)
text = text.replace(
    "    this._showDashboardHeader = true;\n",
    "    this._showDashboardHeader = true;\n"
    "    this._nativeHeader = { enabled: true, show_summary: true, show_refresh: true, show_version: true, order: [], shortcuts: {} };\n"
    "    this._shortcutAvailability = { discovery: false, installer: false, snmp2mqtt: false, unifi2mqtt: false };\n"
    "    this._customizingShortcuts = false;\n"
    "    this._draggedShortcutId = null;\n"
    "    this._lastNativeHeaderSignature = null;\n",
    1,
)

text = text.replace(
    '        .compact-head{display:flex;align-items:center;gap:12px;margin:0 0 10px;min-height:38px}\n',
    '        .native-header{margin:0 0 12px}.native-header[hidden]{display:none!important}\n'
    '        .shortcut-row{display:flex;align-items:center;gap:8px;margin:0 0 8px;overflow-x:auto;padding:1px 0 3px;scrollbar-width:thin}\n'
    '        .shortcut-row[hidden]{display:none!important}.shortcut{flex:0 0 auto;white-space:nowrap;background:var(--secondary-background-color,#34414a);font-size:12px;padding:7px 10px}\n'
    '        .shortcut:hover,.shortcut:focus-visible{background:var(--primary-color,#2b8cc4);outline:none}.shortcut[disabled]{opacity:.45;cursor:not-allowed}.shortcut.dragging{opacity:.45}.shortcut.customizing{cursor:grab;border:1px dashed rgba(127,180,220,.75)}\n'
    '        .shortcut-tools{display:flex;gap:8px;align-items:center;flex:0 0 auto}.shortcut-tools button{font-size:12px;padding:7px 9px}.shortcut-hint{font-size:12px;opacity:.72;white-space:nowrap}\n'
    '        .compact-head{display:flex;align-items:center;gap:12px;margin:0;min-height:38px}\n',
    1,
)
text = text.replace(
    '        @media(max-width:650px){.page{padding:8px 8px 28px}.compact-head{gap:7px}.summary{font-size:13px;padding:8px 9px}.version{font-size:11px;padding:4px 7px}button{padding:7px 9px}.menu-toggle{padding:0}}\n',
    '        @media(max-width:650px){.page{padding:8px 8px 28px}.compact-head{gap:7px}.summary{font-size:13px;padding:8px 9px}.version{font-size:11px;padding:4px 7px}button{padding:7px 9px}.menu-toggle{padding:0}.shortcut-row{gap:6px}.shortcut{font-size:11px;padding:6px 8px}}\n',
    1,
)

old_header = '''        <div id="compact-head" class="compact-head">\n          <button id="menu-toggle" class="menu-toggle" title="Open Home Assistant menu" aria-label="Open Home Assistant menu" type="button">☰</button>\n          <div id="summary" class="summary">Loading generated switch configuration…</div>\n          <button id="refresh" title="Refresh dashboard" aria-label="Refresh dashboard">Refresh</button>\n          <span id="version" class="version">v${PANEL_VERSION}</span>\n        </div>\n'''
new_header = '''        <div id="native-header" class="native-header">\n          <div id="shortcut-row" class="shortcut-row"></div>\n          <div id="compact-head" class="compact-head">\n            <button id="menu-toggle" class="menu-toggle" title="Open Home Assistant menu" aria-label="Open Home Assistant menu" type="button">☰</button>\n            <div id="summary" class="summary">Loading generated switch configuration…</div>\n            <button id="refresh" title="Refresh dashboard" aria-label="Refresh dashboard">Refresh</button>\n            <span id="version" class="version">v${PANEL_VERSION}</span>\n          </div>\n        </div>\n'''
if old_header not in text:
    raise SystemExit("native panel header markup marker missing")
text = text.replace(old_header, new_header, 1)

old_apply = '''  _applyDashboardHeaderVisibility(result) {\n    const configured = result?.show_dashboard_header ?? this.panel?.config?.show_dashboard_header;\n    this._showDashboardHeader = configured !== false;\n    const header = this.shadowRoot.getElementById("compact-head");\n    if (header) header.classList.toggle("header-hidden", !this._showDashboardHeader);\n  }\n'''
new_apply = '''  _applyDashboardHeaderVisibility(result) {\n    const legacyConfigured = result?.show_dashboard_header ?? this.panel?.config?.show_dashboard_header;\n    const incoming = result?.native_header || this.panel?.config?.native_header || {};\n    this._nativeHeader = {\n      enabled: incoming.enabled ?? (legacyConfigured !== false),\n      show_summary: incoming.show_summary !== false,\n      show_refresh: incoming.show_refresh !== false,\n      show_version: incoming.show_version !== false,\n      order: Array.isArray(incoming.order) ? incoming.order.map(String) : [],\n      shortcuts: incoming.shortcuts && typeof incoming.shortcuts === "object" ? { ...incoming.shortcuts } : {}\n    };\n    this._showDashboardHeader = this._nativeHeader.enabled !== false;\n    const wholeHeader = this.shadowRoot.getElementById("native-header");\n    if (wholeHeader) wholeHeader.hidden = !this._showDashboardHeader;\n    const summary = this.shadowRoot.getElementById("summary");\n    const refresh = this.shadowRoot.getElementById("refresh");\n    const version = this.shadowRoot.getElementById("version");\n    if (summary) summary.hidden = this._nativeHeader.show_summary === false;\n    if (refresh) refresh.hidden = this._nativeHeader.show_refresh === false;\n    if (version) version.hidden = this._nativeHeader.show_version === false;\n    this._lastNativeHeaderSignature = JSON.stringify(this._nativeHeader);\n    this._renderShortcuts();\n  }\n\n  _shortcutDefinitions() {\n    return {\n      hub: { label: "Switch Vision Hub", app: "discovery", path: "/app/switch_vision_discovery" },\n      switch_vision_settings: { label: "Switch Vision Settings", path: "/config/integrations/integration/switch_vision" },\n      discovery_settings: { label: "Discovery Settings", app: "discovery", path: "/config/app/switch_vision_discovery/config" },\n      installer: { label: "Switch Vision Installer", app: "installer", path: "/app/switch_vision_installer" },\n      installer_settings: { label: "Installer Settings", app: "installer", path: "/config/app/switch_vision_installer/config" },\n      snmp2mqtt_settings: { label: "SNMP2MQTT Settings", app: "snmp2mqtt", path: "/config/app/switch_vision_snmp2mqtt/config" },\n      unifi2mqtt_settings: { label: "UniFi2MQTT Settings", app: "unifi2mqtt", path: "/config/app/switch_vision_unifi2mqtt/config" }\n    };\n  }\n\n  _navigate(path) {\n    this.dispatchEvent(new CustomEvent("hass-navigate", {\n      bubbles: true, composed: true, detail: { navigate: path }\n    }));\n  }\n\n  async _refreshShortcutAvailability() {\n    if (!this._hass) return;\n    const slugs = {\n      discovery: "switch_vision_discovery",\n      installer: "switch_vision_installer",\n      snmp2mqtt: "switch_vision_snmp2mqtt",\n      unifi2mqtt: "switch_vision_unifi2mqtt"\n    };\n    const next = { discovery: false, installer: false, snmp2mqtt: false, unifi2mqtt: false };\n    await Promise.all(Object.entries(slugs).map(async ([key, slug]) => {\n      try {\n        await this._hass.callWS({ type: "supervisor/api", endpoint: `/addons/${slug}/info`, method: "get" });\n        next[key] = true;\n      } catch (error) {\n        next[key] = false;\n      }\n    }));\n    this._shortcutAvailability = next;\n    this._renderShortcuts();\n  }\n\n  _renderShortcuts() {\n    const root = this.shadowRoot.getElementById("shortcut-row");\n    if (!root) return;\n    root.replaceChildren();\n    if (!this._showDashboardHeader) { root.hidden = true; return; }\n    const defs = this._shortcutDefinitions();\n    const enabled = this._nativeHeader.shortcuts || {};\n    const order = Array.isArray(this._nativeHeader.order) && this._nativeHeader.order.length\n      ? this._nativeHeader.order\n      : Object.keys(defs);\n    const rendered = [];\n    for (const id of order) {\n      const def = defs[id];\n      if (!def || enabled[id] === false) continue;\n      const installed = !def.app || this._shortcutAvailability[def.app] === true;\n      if (!installed) continue;\n      const button = document.createElement("button");\n      button.type = "button";\n      button.className = `shortcut${this._customizingShortcuts ? " customizing" : ""}`;\n      button.dataset.shortcutId = id;\n      button.textContent = def.label;\n      button.title = this._customizingShortcuts ? "Drag to reorder" : def.label;\n      button.draggable = this._customizingShortcuts;\n      button.addEventListener("click", (event) => {\n        if (this._customizingShortcuts) { event.preventDefault(); return; }\n        this._navigate(def.path);\n      });\n      button.addEventListener("dragstart", () => { this._draggedShortcutId = id; button.classList.add("dragging"); });\n      button.addEventListener("dragend", () => { this._draggedShortcutId = null; button.classList.remove("dragging"); });\n      button.addEventListener("dragover", (event) => {\n        if (!this._customizingShortcuts || !this._draggedShortcutId || this._draggedShortcutId === id) return;\n        event.preventDefault();\n        const dragged = root.querySelector(`[data-shortcut-id="${this._draggedShortcutId}"]`);\n        if (dragged && dragged !== button) root.insertBefore(dragged, button);\n      });\n      root.appendChild(button);\n      rendered.push(id);\n    }\n    if (rendered.length) {\n      const tools = document.createElement("span");\n      tools.className = "shortcut-tools";\n      if (this._customizingShortcuts) {\n        const hint = document.createElement("span");\n        hint.className = "shortcut-hint";\n        hint.textContent = "Drag shortcuts, then Done";\n        tools.appendChild(hint);\n      }\n      const customize = document.createElement("button");\n      customize.type = "button";\n      customize.className = "secondary";\n      customize.textContent = this._customizingShortcuts ? "Done" : "Customize";\n      customize.addEventListener("click", () => this._toggleShortcutCustomization());\n      tools.appendChild(customize);\n      root.appendChild(tools);\n    }\n    root.hidden = rendered.length === 0;\n  }\n\n  async _toggleShortcutCustomization() {\n    if (!this._customizingShortcuts) {\n      this._customizingShortcuts = true;\n      this._renderShortcuts();\n      return;\n    }\n    const root = this.shadowRoot.getElementById("shortcut-row");\n    const visibleOrder = root ? [...root.querySelectorAll("button.shortcut")].map(button => button.dataset.shortcutId).filter(Boolean) : [];\n    const fullOrder = Array.isArray(this._nativeHeader.order) ? [...this._nativeHeader.order] : [];\n    const visibleSet = new Set(visibleOrder);\n    const mergedOrder = [...visibleOrder, ...fullOrder.filter(id => !visibleSet.has(id))];\n    try {\n      const result = await this._hass.callWS({ type: "switch_vision/set_native_header_shortcut_order", order: mergedOrder });\n      this._nativeHeader.order = Array.isArray(result?.order) ? result.order : mergedOrder;\n    } catch (error) {\n      console.warn("Switch Vision could not save shortcut order", error);\n    } finally {\n      this._customizingShortcuts = false;\n      this._renderShortcuts();\n    }\n  }\n'''
if old_apply not in text:
    raise SystemExit("_applyDashboardHeaderVisibility marker missing")
text = text.replace(old_apply, new_apply, 1)

# Refresh app availability without blocking card rendering.
text = text.replace(
    '      this._applyDashboardHeaderVisibility(result);\n      cardsRoot.classList.toggle("headers-hidden", result?.show_card_headers === false);\n',
    '      this._applyDashboardHeaderVisibility(result);\n      void this._refreshShortcutAvailability();\n      cardsRoot.classList.toggle("headers-hidden", result?.show_card_headers === false);\n',
    1,
)

# Detect live header-option changes during the normal 5s poll.
old_check = '''      const showCalibrationButtons = result && result.show_calibration_buttons !== false;\n      const optionChanged = this._lastShowCalibrationButtons !== null && showCalibrationButtons !== this._lastShowCalibrationButtons;\n      if (!this._loaded || optionChanged || (modified && this._lastModified && modified !== this._lastModified) || (modified && !this._lastModified)) {\n'''
new_check = '''      const showCalibrationButtons = result && result.show_calibration_buttons !== false;\n      const headerSignature = JSON.stringify(result?.native_header || {});\n      const optionChanged = (this._lastShowCalibrationButtons !== null && showCalibrationButtons !== this._lastShowCalibrationButtons)\n        || (this._lastNativeHeaderSignature !== null && headerSignature !== this._lastNativeHeaderSignature);\n      if (!this._loaded || optionChanged || (modified && this._lastModified && modified !== this._lastModified) || (modified && !this._lastModified)) {\n'''
if old_check not in text:
    raise SystemExit("native panel poll option marker missing")
text = text.replace(old_check, new_check, 1)
text = text.replace(
    '      manual_yaml_fallback: true\n',
    '      manual_yaml_fallback: true,\n      native_header: result.native_header || this._nativeHeader\n',
    1,
)
write(panel, text)

# ---------------------------------------------------------------------------
# Strings / translations.
# ---------------------------------------------------------------------------
for path in (COMP / "strings.json", COMP / "translations/en.json"):
    data = json.loads(read(path))
    init = data["options"]["step"]["init"]
    init["description"] = (
        "Configure Switch Vision sidebar visibility, the Native dashboard shortcut header, "
        "shared card presentation, Activity LEDs, Discovery, and Installer presentation."
    )
    sections = init["sections"]
    sections["sidebar"] = {
        "name": "Sidebar",
        "description": "Central visibility controls for every installed Switch Vision sidebar-capable panel. Not-installed apps remain visible here as read-only status rows.",
        "data": {
            "show_all_switch_vision_sidebar_items": "Show all Switch Vision sidebar items",
            "show_panel_in_sidebar": "Native Switch Vision",
            "show_lovelace_dashboard_in_sidebar": "Switch Vision Dashboard",
            "show_hub_in_sidebar": "Switch Vision Hub",
            "show_installer_in_sidebar": "Switch Vision Installer",
            "sidebar_hub_not_installed": "Switch Vision Hub — Not installed",
            "sidebar_installer_not_installed": "Switch Vision Installer — Not installed",
        },
        "data_description": {
            "show_all_switch_vision_sidebar_items": "Master switch. Turning this off hides all Switch Vision-managed sidebar entries while preserving the individual choices below.",
            "show_panel_in_sidebar": "Show or hide the automatic Native Switch Vision panel at /switch-vision.",
            "show_lovelace_dashboard_in_sidebar": "Show or hide Home Assistant dashboards created with the Switch Vision Community dashboard strategy.",
            "show_hub_in_sidebar": "Show or hide the Switch Vision Hub ingress panel supplied by Discovery.",
            "show_installer_in_sidebar": "Show or hide the Switch Vision Installer ingress panel.",
            "sidebar_hub_not_installed": "Install Switch Vision Discovery to enable this sidebar item.",
            "sidebar_installer_not_installed": "Install Switch Vision Installer to enable this sidebar item.",
        },
    }
    sections["native_header"] = {
        "name": "Native Dashboard Header",
        "description": "Choose what appears above the Native Switch Vision dashboard. Enabled shortcuts can be dragged into any order directly on the dashboard using Customize.",
        "data": {
            "show_dashboard_header": "Enable Native Dashboard Header",
            "native_header_show_summary": "Show status summary",
            "native_header_show_refresh": "Show Refresh button",
            "native_header_show_version": "Show version badge",
            "native_header_shortcut_switch_vision_settings": "Shortcut: Switch Vision Settings",
            "native_header_shortcut_hub": "Shortcut: Switch Vision Hub",
            "native_header_shortcut_discovery_settings": "Shortcut: Discovery Settings",
            "native_header_shortcut_installer": "Shortcut: Switch Vision Installer",
            "native_header_shortcut_installer_settings": "Shortcut: Installer Settings",
            "native_header_shortcut_snmp2mqtt_settings": "Shortcut: SNMP2MQTT Settings",
            "native_header_shortcut_unifi2mqtt_settings": "Shortcut: UniFi2MQTT Settings",
            "shortcut_discovery_not_installed": "Switch Vision Hub / Discovery Settings — Not installed",
            "shortcut_installer_not_installed": "Switch Vision Installer / Installer Settings — Not installed",
            "shortcut_snmp2mqtt_not_installed": "SNMP2MQTT Settings — Not installed",
            "shortcut_unifi2mqtt_not_installed": "UniFi2MQTT Settings — Not installed",
        },
        "data_description": {
            "show_dashboard_header": "Master switch for the entire Native dashboard header, including shortcuts and the summary row.",
            "native_header_show_summary": "Show switch count and last-generated status in the Native dashboard header.",
            "native_header_show_refresh": "Show the manual dashboard Refresh control.",
            "native_header_show_version": "Show the current Switch Vision Core version badge.",
            "native_header_shortcut_switch_vision_settings": "Open Settings → Integrations → Switch Vision.",
            "native_header_shortcut_hub": "Open Switch Vision Hub directly.",
            "native_header_shortcut_discovery_settings": "Open the Discovery app Configuration page.",
            "native_header_shortcut_installer": "Open Switch Vision Installer directly.",
            "native_header_shortcut_installer_settings": "Open the Installer app Configuration page.",
            "native_header_shortcut_snmp2mqtt_settings": "Open the SNMP2MQTT app Configuration page.",
            "native_header_shortcut_unifi2mqtt_settings": "Open the UniFi2MQTT app Configuration page.",
            "shortcut_discovery_not_installed": "Install Switch Vision Discovery to enable these shortcuts.",
            "shortcut_installer_not_installed": "Install Switch Vision Installer to enable these shortcuts.",
            "shortcut_snmp2mqtt_not_installed": "Install Switch Vision SNMP2MQTT to enable this shortcut.",
            "shortcut_unifi2mqtt_not_installed": "Install Switch Vision UniFi2MQTT to enable this shortcut.",
        },
    }
    sections["dashboard"] = {
        "name": "Dashboard Cards",
        "description": "Shared switch-card presentation controls.",
        "data": {
            "show_calibration_buttons": "Show calibration buttons on switch cards",
            "show_card_headers": "Show card headers",
        },
        "data_description": {
            "show_calibration_buttons": "Show or hide the on-card Calibration button on the automatic generated Switch Vision dashboard.",
            "show_card_headers": "Show or hide the complete header row on every Switch Vision card, including custom YAML cards.",
        },
    }
    # Reorder sections for the intended UI flow.
    init["sections"] = {
        "sidebar": sections["sidebar"],
        "native_header": sections["native_header"],
        "dashboard": sections["dashboard"],
        "activity_leds": sections["activity_leds"],
        "discovery": sections["discovery"],
        "installer": sections["installer"],
    }
    write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------------
# Release notes and permanent regression.
# ---------------------------------------------------------------------------
changelog = ROOT / "CHANGELOG.md"
entry = '''## v2.4.4 — Central sidebar and Native dashboard shortcuts\n\n- Adds a dedicated Switch Vision Integration **Sidebar** section controlling the Native panel, Community dashboard, Switch Vision Hub, and Switch Vision Installer from one place.\n- Uses Home Assistant Supervisor's supported `ingress_panel` option for Hub/Installer visibility; absent apps remain visible in settings as read-only **Not installed** rows.\n- Expands the Native dashboard header with configurable shortcuts to Hub, Switch Vision settings, Discovery settings, Installer, Installer settings, SNMP2MQTT settings, and UniFi2MQTT settings.\n- Adds per-shortcut enable/disable controls, installation-aware availability, drag-to-reorder customization on the Native dashboard, and independent summary/Refresh/version visibility controls.\n- Preserves the existing whole-header master switch and makes the shortcut row horizontally scrollable on narrow/mobile layouts.\n- Keeps card telemetry, calibration, Discovery generation, Activity LED behavior, and device mappings unchanged.\n\n'''
current = read(changelog)
if not current.startswith("## v2.4.4"):
    write(changelog, entry + current)

release_notes = ROOT / "RELEASE_NOTES.md"
write(release_notes, '''# Switch Vision Core v2.4.4 — Central sidebar and Native dashboard shortcuts\n\n- Centralizes all Switch Vision-managed sidebar visibility under Settings → Integrations → Switch Vision → Configure.\n- Controls Native Switch Vision, Switch Vision Dashboard, Switch Vision Hub, and Switch Vision Installer from one Sidebar section.\n- Shows absent sidebar-capable apps as read-only **Not installed** entries instead of silently omitting them.\n- Adds a configurable Native dashboard shortcut header with per-shortcut enable/disable, installation-aware shortcuts, drag-to-reorder customization, and independent summary / Refresh / version controls.\n- Uses Home Assistant Supervisor's supported ingress-panel API and current `/config/app/<slug>/config` app settings routes.\n- Does not change switch telemetry, calibration geometry, supported-device mappings, Discovery generation, or Activity LED behavior.\n\nAfter updating Core through Switch Vision Installer, restart Home Assistant Core when requested and hard-refresh the browser so the new integration options and Native panel JavaScript are loaded.\n''')

test = ROOT / "tests/test_sidebar_header_contracts.py"
write(test, '''from pathlib import Path\n\nROOT = Path(__file__).resolve().parents[1]\nINIT = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text(encoding="utf-8")\nFLOW = (ROOT / "src/custom_components/switch_vision/config_flow.py").read_text(encoding="utf-8")\nPANEL = (ROOT / "src/custom_components/switch_vision/switch-vision-panel.js").read_text(encoding="utf-8")\nSTRINGS = (ROOT / "src/custom_components/switch_vision/strings.json").read_text(encoding="utf-8")\n\nfor marker in (\n    'CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS',\n    'CONF_SHOW_HUB_IN_SIDEBAR',\n    'CONF_SHOW_INSTALLER_IN_SIDEBAR',\n    'AddonsOptions(ingress_panel=bool(show_in_sidebar))',\n    'switch_vision/set_native_header_shortcut_order',\n    'DATA_NATIVE_HEADER_SETTINGS',\n):\n    assert marker in INIT, marker\n\nfor marker in (\n    'sidebar_hub_not_installed',\n    'sidebar_installer_not_installed',\n    'shortcut_snmp2mqtt_not_installed',\n    'read_only',\n    'vol.Required("native_header")',\n):\n    assert marker in FLOW, marker\n\nfor marker in (\n    'Switch Vision Hub',\n    '/app/switch_vision_discovery',\n    '/config/app/switch_vision_discovery/config',\n    '/config/app/switch_vision_installer/config',\n    '/config/app/switch_vision_snmp2mqtt/config',\n    '/config/app/switch_vision_unifi2mqtt/config',\n    'Drag shortcuts, then Done',\n    'set_native_header_shortcut_order',\n    'overflow-x:auto',\n):\n    assert marker in PANEL, marker\n\nassert 'Not installed' in STRINGS\nprint('Core 2.4.4 sidebar/header contracts: PASS')\n''')

print("Prepared Switch Vision Core v2.4.4 sidebar/header feature")
