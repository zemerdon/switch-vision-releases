#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "src/custom_components/switch_vision"
INIT = COMP / "__init__.py"
FLOW = COMP / "config_flow.py"
PANEL = COMP / "switch-vision-panel.js"
TEST = ROOT / "tests/test_sidebar_header_contracts.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


def replace_once(path: Path, old: str, new: str) -> None:
    text = read(path)
    if old not in text:
        raise SystemExit(f"Expected finalization marker missing in {path}: {old[:140]!r}")
    write(path, text.replace(old, new, 1))


# ---------------------------------------------------------------------------
# Backend import safety and sanitized app-state WebSocket.
# ---------------------------------------------------------------------------
text = read(INIT)
shortcut_block = '''NATIVE_HEADER_SHORTCUT_IDS = (\n    "hub",\n    "switch_vision_settings",\n    "discovery_settings",\n    "installer",\n    "installer_settings",\n    "snmp2mqtt_settings",\n    "unifi2mqtt_settings",\n)\n'''
if text.count(shortcut_block) != 1:
    raise SystemExit("Expected exactly one NATIVE_HEADER_SHORTCUT_IDS definition")
text = text.replace(shortcut_block, "", 1)
event_marker = 'EVENT_UI_SETTINGS_UPDATED = "switch_vision_ui_settings_updated"\n'
if event_marker not in text:
    raise SystemExit("Core event marker missing")
text = text.replace(event_marker, event_marker + "\n" + shortcut_block, 1)

ui_schema = '''UI_SETTINGS_WS_SCHEMA = {\n    vol.Required("type"): "switch_vision/get_ui_settings",\n}\n'''
app_schema = '''UI_SETTINGS_WS_SCHEMA = {\n    vol.Required("type"): "switch_vision/get_ui_settings",\n}\n\nAPP_STATES_WS_SCHEMA = {\n    vol.Required("type"): "switch_vision/get_app_states",\n}\n'''
if app_schema not in text:
    if ui_schema not in text:
        raise SystemExit("UI settings WebSocket schema marker missing")
    text = text.replace(ui_schema, app_schema, 1)

ui_handler_marker = '''    @websocket_api.websocket_command(UI_SETTINGS_WS_SCHEMA)\n    @websocket_api.async_response\n    async def websocket_get_ui_settings(hass: HomeAssistant, connection, msg):\n'''
app_handler = '''    @websocket_api.websocket_command(APP_STATES_WS_SCHEMA)\n    @websocket_api.async_response\n    async def websocket_get_app_states(hass: HomeAssistant, connection, msg):\n        """Return sanitized Switch Vision app availability to the Native panel."""\n        raw_states = await async_switch_vision_app_states(hass)\n        apps = {}\n        for key, state in raw_states.items():\n            apps[key] = {\n                "installed": bool(state.get("installed", False)),\n                "ingress": bool(state.get("ingress", False)),\n                "available": bool(state.get("available", False)),\n            }\n        connection.send_result(msg["id"], {"apps": apps})\n\n'''
if app_handler not in text:
    if ui_handler_marker not in text:
        raise SystemExit("UI settings WebSocket handler marker missing")
    text = text.replace(ui_handler_marker, app_handler + ui_handler_marker, 1)

register_marker = '    websocket_api.async_register_command(hass, websocket_get_ui_settings)\n'
register_app = '    websocket_api.async_register_command(hass, websocket_get_app_states)\n'
if register_app not in text:
    if register_marker not in text:
        raise SystemExit("UI settings registration marker missing")
    text = text.replace(register_marker, register_app + register_marker, 1)

# The master sidebar toggle remains authoritative when Home Assistant emits a
# later Lovelace dashboard-update event.
old_listener = '''            await _sync_switch_vision_lovelace_dashboard_sidebar(\n                hass,\n                bool(\n                    entry.options.get(\n                        CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR, True\n                    )\n                ),\n            )\n'''
new_listener = '''            sidebar_master = bool(\n                entry.options.get(\n                    CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS,\n                    DEFAULT_OPTIONS[CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS],\n                )\n            )\n            lovelace_preference = bool(\n                entry.options.get(\n                    CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR,\n                    DEFAULT_OPTIONS[CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR],\n                )\n            )\n            await _sync_switch_vision_lovelace_dashboard_sidebar(\n                hass, sidebar_master and lovelace_preference\n            )\n'''
if old_listener not in text:
    raise SystemExit("Lovelace update-listener marker missing")
text = text.replace(old_listener, new_listener, 1)
write(INIT, text)

# ---------------------------------------------------------------------------
# Never persist display-only Not installed selector values.
# ---------------------------------------------------------------------------
replace_once(
    FLOW,
    '''                for group in ("sidebar", "native_header", "dashboard", "activity_leds", "discovery", "installer"):\n                    saved.update(dict(user_input.get(group) or {}))\n                saved.pop(CONF_RESET_TO_DEFAULTS, None)\n                return self.async_create_entry(data=saved)\n''',
    '''                for group in ("sidebar", "native_header", "dashboard", "activity_leds", "discovery", "installer"):\n                    saved.update(dict(user_input.get(group) or {}))\n                for synthetic_key in (\n                    "sidebar_hub_not_installed",\n                    "sidebar_installer_not_installed",\n                    "shortcut_discovery_not_installed",\n                    "shortcut_installer_not_installed",\n                    "shortcut_snmp2mqtt_not_installed",\n                    "shortcut_unifi2mqtt_not_installed",\n                ):\n                    saved.pop(synthetic_key, None)\n                saved.pop(CONF_RESET_TO_DEFAULTS, None)\n                return self.async_create_entry(data=saved)\n''',
)

# ---------------------------------------------------------------------------
# Native panel: one Core WebSocket for app availability; robust drag ordering.
# ---------------------------------------------------------------------------
replace_once(
    PANEL,
    '''  async _refreshShortcutAvailability() {\n    if (!this._hass) return;\n    const slugs = {\n      discovery: "switch_vision_discovery",\n      installer: "switch_vision_installer",\n      snmp2mqtt: "switch_vision_snmp2mqtt",\n      unifi2mqtt: "switch_vision_unifi2mqtt"\n    };\n    const next = { discovery: false, installer: false, snmp2mqtt: false, unifi2mqtt: false };\n    await Promise.all(Object.entries(slugs).map(async ([key, slug]) => {\n      try {\n        await this._hass.callWS({ type: "supervisor/api", endpoint: `/addons/${slug}/info`, method: "get" });\n        next[key] = true;\n      } catch (error) {\n        next[key] = false;\n      }\n    }));\n    this._shortcutAvailability = next;\n    this._renderShortcuts();\n  }\n''',
    '''  async _refreshShortcutAvailability() {\n    if (!this._hass) return;\n    const next = { discovery: false, installer: false, snmp2mqtt: false, unifi2mqtt: false };\n    try {\n      const result = await this._hass.callWS({ type: "switch_vision/get_app_states" });\n      const apps = result?.apps && typeof result.apps === "object" ? result.apps : {};\n      for (const key of Object.keys(next)) next[key] = apps[key]?.installed === true;\n    } catch (error) {\n      console.warn("Switch Vision could not read app availability", error);\n    }\n    this._shortcutAvailability = next;\n    this._renderShortcuts();\n  }\n''',
)
replace_once(
    PANEL,
    '''      button.addEventListener("dragover", (event) => {\n        if (!this._customizingShortcuts || !this._draggedShortcutId || this._draggedShortcutId === id) return;\n        event.preventDefault();\n        const dragged = root.querySelector(`[data-shortcut-id="${this._draggedShortcutId}"]`);\n        if (dragged && dragged !== button) root.insertBefore(dragged, button);\n      });\n''',
    '''      button.addEventListener("dragover", (event) => {\n        if (!this._customizingShortcuts || !this._draggedShortcutId || this._draggedShortcutId === id) return;\n        event.preventDefault();\n        const dragged = root.querySelector(`[data-shortcut-id="${this._draggedShortcutId}"]`);\n        if (!dragged || dragged === button) return;\n        const rect = button.getBoundingClientRect();\n        const before = event.clientX < rect.left + rect.width / 2;\n        root.insertBefore(dragged, before ? button : button.nextSibling);\n      });\n''',
)

# Safety: Native panel must never depend on direct Supervisor browser calls.
panel_text = read(PANEL)
if 'type: "supervisor/api"' in panel_text:
    raise SystemExit("Direct Supervisor browser API call remains in Native panel")

# ---------------------------------------------------------------------------
# Permanent regressions for the final safety pass.
# ---------------------------------------------------------------------------
test_text = read(TEST)
addition = '''\n# Final 2.4.4 safety contracts.\nassert INIT.index("NATIVE_HEADER_SHORTCUT_IDS = (") < INIT.index("SET_NATIVE_HEADER_ORDER_WS_SCHEMA = {")\nassert 'switch_vision/get_app_states' in INIT\nassert 'websocket_get_app_states' in INIT\nassert 'sidebar_master and lovelace_preference' in INIT\nassert 'saved.pop(synthetic_key, None)' in FLOW\nassert 'switch_vision/get_app_states' in PANEL\nassert 'type: "supervisor/api"' not in PANEL\nassert 'event.clientX < rect.left + rect.width / 2' in PANEL\n'''
if addition not in test_text:
    test_text = test_text.replace(
        "assert 'Not installed' in STRINGS\n",
        "assert 'Not installed' in STRINGS\n" + addition,
        1,
    )
    write(TEST, test_text)

print("Finalized Switch Vision Core v2.4.4 sidebar/header safety contracts")
