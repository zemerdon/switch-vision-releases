"""Switch Vision calibration profile storage integration."""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import math
import os
from pathlib import Path
from typing import Any

import voluptuous as vol
import yaml

from aiohasupervisor import SupervisorError, SupervisorNotFoundError
from aiohasupervisor.models import AddonsOptions

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.service import async_register_admin_service
from homeassistant.helpers.storage import Store
from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.lovelace.const import (
    CONF_ICON,
    CONF_REQUIRE_ADMIN,
    CONF_RESOURCE_TYPE_WS,
    CONF_SHOW_IN_SIDEBAR,
    CONF_TITLE,
    DEFAULT_ICON,
    DOMAIN as LOVELACE_DOMAIN,
    EVENT_LOVELACE_UPDATED,
    LOVELACE_DATA,
    MODE_STORAGE,
    ConfigNotFound,
)
from homeassistant.components.lovelace.dashboard import DashboardsCollection
from homeassistant.components.frontend import async_panel_exists, async_remove_panel
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.hassio.const import DATA_ADDONS_LIST
from homeassistant.components.hassio.handler import get_supervisor_client

_LOGGER = logging.getLogger(__name__)

DOMAIN = "switch_vision"
STORAGE_KEY = "switch_vision_calibrations"
STORAGE_VERSION = 1
STORAGE_PATH = f".storage/{STORAGE_KEY}"
EVENT_CALIBRATION_UPDATED = "switch_vision_calibration_updated"
EVENT_UI_SETTINGS_UPDATED = "switch_vision_ui_settings_updated"

NATIVE_HEADER_SHORTCUT_IDS = (
    "hub",
    "maintenance",
    "switch_vision_settings",
    "discovery_settings",
    "installer",
    "installer_settings",
    "snmp2mqtt_settings",
    "unifi2mqtt_settings",
)

SAVE_SCHEMA = vol.Schema(
    {
        vol.Required("profile"): vol.All(str, vol.Length(min=1)),
        vol.Required("calibration"): object,
        # Native-panel cards bootstrap from a stable switch-scoped profile.
        # Mirroring is explicit so custom/manual YAML cards never inherit it.
        vol.Optional("mirror_to_base", default=False): bool,
    }
)

DELETE_SCHEMA = vol.Schema(
    {
        vol.Required("profile"): vol.All(str, vol.Length(min=1)),
    }
)

RESET_SCHEMA = vol.Schema(
    {
        vol.Required("scope"): vol.In(["switch", "namespace", "native", "custom", "all"]),
        vol.Optional("base_profile"): vol.All(str, vol.Length(min=1)),
        vol.Optional("scope_prefix"): vol.All(str, vol.In(["native_", "custom_"])),
    }
)

UI_DENSITY_SCHEMA = vol.Schema(
    {
        vol.Required("density"): vol.In(["comfortable", "compact", "dense"]),
    }
)

GET_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/get_calibration",
    vol.Required("profile"): vol.All(str, vol.Length(min=1)),
    vol.Optional("exact", default=False): bool,
}

LIST_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/list_calibrations",
}

LIST_ASSETS_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/list_assets",
}

DASHBOARD_PANEL_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/get_dashboard_panel",
    vol.Optional("refresh", default=False): bool,
}

UI_SETTINGS_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/get_ui_settings",
}

CORE_SETTINGS_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/get_settings",
}

SET_CORE_SETTINGS_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/set_settings",
    vol.Optional("settings", default={}): object,
    vol.Optional("reset_to_defaults", default=False): bool,
}

APP_STATES_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/get_app_states",
}

SET_NATIVE_HEADER_ORDER_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/set_native_header_shortcut_order",
    vol.Required("order"): [vol.In(NATIVE_HEADER_SHORTCUT_IDS)],
    vol.Optional("shortcuts"): {vol.In(NATIVE_HEADER_SHORTCUT_IDS): bool},
}

UNIFI_DEVICE_WS_SCHEMA = {
    vol.Required("type"): "switch_vision/get_unifi_device",
    vol.Required("device_id"): vol.All(str, vol.Length(min=1, max=128)),
}

PANEL_URL_PATH = "switch-vision"
PANEL_VERSION = "2.6.23"
PANEL_JS_PATH = "/api/switch_vision/switch-vision-panel.js"
PANEL_JS_URL = f"{PANEL_JS_PATH}?v={PANEL_VERSION}"
ICONSET_JS_PATH = "/api/switch_vision/switch-vision-iconset.js"
ICONSET_JS_URL = f"{ICONSET_JS_PATH}?v={PANEL_VERSION}"
CARD_JS_PATH = "/api/switch_vision/switch-vision-card.js"
CARD_JS_URL = f"{CARD_JS_PATH}?v={PANEL_VERSION}"
DASHBOARD_STRATEGY_JS_PATH = "/api/switch_vision/switch-vision-dashboard-strategy.js"
DASHBOARD_STRATEGY_JS_URL = f"{DASHBOARD_STRATEGY_JS_PATH}?v={PANEL_VERSION}"
DEFAULT_DASHBOARD_CONFIG_PATH = "/share/switch_vision/generated-dashboard-card.yaml"
UNIFI_DEVICES_PATH = Path("/share/switch_vision/unifi/devices.json")
MAX_UNIFI_SNAPSHOT_BYTES = 4 * 1024 * 1024
MAX_GENERATED_DASHBOARD_BYTES = 4 * 1024 * 1024
CONF_SHOW_PANEL_IN_SIDEBAR = "show_panel_in_sidebar"
CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR = "show_lovelace_dashboard_in_sidebar"
CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS = "show_all_switch_vision_sidebar_items"
CONF_SHOW_HUB_IN_SIDEBAR = "show_hub_in_sidebar"
CONF_SHOW_INSTALLER_IN_SIDEBAR = "show_installer_in_sidebar"
CONF_NATIVE_HEADER_SHOW_SUMMARY = "native_header_show_summary"
CONF_NATIVE_HEADER_SHOW_REFRESH = "native_header_show_refresh"
CONF_NATIVE_HEADER_SHOW_VERSION = "native_header_show_version"
CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS = "native_header_shortcut_switch_vision_settings"
CONF_NATIVE_HEADER_SHORTCUT_HUB = "native_header_shortcut_hub"
CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE = "native_header_shortcut_maintenance"
CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS = "native_header_shortcut_discovery_settings"
CONF_NATIVE_HEADER_SHORTCUT_INSTALLER = "native_header_shortcut_installer"
CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS = "native_header_shortcut_installer_settings"
CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS = "native_header_shortcut_snmp2mqtt_settings"
CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS = "native_header_shortcut_unifi2mqtt_settings"
CONF_NATIVE_HEADER_SHORTCUT_ORDER = "native_header_shortcut_order"

DISCOVERY_APP_SLUG = "switch_vision_discovery"
INSTALLER_APP_SLUG = "switch_vision_installer"
SNMP2MQTT_APP_SLUG = "switch_vision_snmp2mqtt"
UNIFI2MQTT_APP_SLUG = "switch_vision_unifi2mqtt"

NATIVE_HEADER_SHORTCUT_OPTION_KEYS = {
    "hub": CONF_NATIVE_HEADER_SHORTCUT_HUB,
    "maintenance": CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE,
    "switch_vision_settings": CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS,
    "discovery_settings": CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS,
    "installer": CONF_NATIVE_HEADER_SHORTCUT_INSTALLER,
    "installer_settings": CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS,
    "snmp2mqtt_settings": CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS,
    "unifi2mqtt_settings": CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS,
}

CONF_SHOW_UNIFI_INTEGRATION = "show_unifi_integration"
CONF_SHOW_CALIBRATION_BUTTONS = "show_calibration_buttons"
CONF_SHOW_DASHBOARD_HEADER = "show_dashboard_header"
CONF_SHOW_CARD_HEADERS = "show_card_headers"
CONF_DISCOVERY_UI_DENSITY = "discovery_ui_density"
CONF_DISCOVERY_TEXT_SIZE = "discovery_text_size"
CONF_DISCOVERY_CONTENT_WIDTH = "discovery_content_width"
CONF_INSTALLER_UI_DENSITY = "installer_ui_density"
CONF_INSTALLER_TEXT_SIZE = "installer_text_size"
CONF_INSTALLER_CONTENT_WIDTH = "installer_content_width"

UI_TEXT_SIZE_MIN_PX = 10
UI_TEXT_SIZE_MAX_PX = 20
UI_TEXT_SIZE_DEFAULT_PX = 16
UI_TEXT_SIZE_LEGACY = {"normal": 16, "small": 14}


def normalise_ui_text_size(value: Any) -> int:
    """Return a safe explicit 10-20 px UI body font size.

    Core 2.6.2 and earlier stored the labels ``normal`` and ``small``. Keep
    those installations valid while the Hub and native fallback move to an
    explicit pixel contract. Invalid/stale values fail back to the 16 px
    factory default rather than leaking an unusable class into an app UI.
    """
    if isinstance(value, bool):
        return UI_TEXT_SIZE_DEFAULT_PX
    if isinstance(value, str):
        text = value.strip().lower()
        if text in UI_TEXT_SIZE_LEGACY:
            return UI_TEXT_SIZE_LEGACY[text]
        if text.endswith("px"):
            text = text[:-2].strip()
        if not text.isdigit():
            return UI_TEXT_SIZE_DEFAULT_PX
        pixels = int(text)
    elif isinstance(value, int):
        pixels = value
    else:
        return UI_TEXT_SIZE_DEFAULT_PX
    if UI_TEXT_SIZE_MIN_PX <= pixels <= UI_TEXT_SIZE_MAX_PX:
        return pixels
    return UI_TEXT_SIZE_DEFAULT_PX


CONF_ACTIVITY_LED_SENSITIVITY_PRESET = "activity_led_sensitivity_preset"
CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT = "activity_slow_max_utilization_pct"
CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT = "activity_medium_max_utilization_pct"
CONF_ACTIVITY_SLOW_PERIOD_MS = "activity_slow_period_ms"
CONF_ACTIVITY_MEDIUM_PERIOD_MS = "activity_medium_period_ms"
CONF_ACTIVITY_FAST_PERIOD_MS = "activity_fast_period_ms"
CONF_ACTIVITY_HOLD_SECONDS = "activity_hold_seconds"
CONF_ACTIVITY_HYSTERESIS_PCT = "activity_hysteresis_pct"

ACTIVITY_LED_PRESETS = {
    "low": {"slow_max_utilization_pct": 1.0, "medium_max_utilization_pct": 10.0},
    "normal": {"slow_max_utilization_pct": 0.10, "medium_max_utilization_pct": 1.0},
    "high": {"slow_max_utilization_pct": 0.02, "medium_max_utilization_pct": 0.25},
}

DEFAULT_OPTIONS = {
    CONF_SHOW_PANEL_IN_SIDEBAR: True,
    CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR: True,
    CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS: True,
    CONF_SHOW_HUB_IN_SIDEBAR: True,
    CONF_SHOW_INSTALLER_IN_SIDEBAR: True,
    CONF_NATIVE_HEADER_SHOW_SUMMARY: True,
    CONF_NATIVE_HEADER_SHOW_REFRESH: True,
    CONF_NATIVE_HEADER_SHOW_VERSION: True,
    CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS: True,
    CONF_NATIVE_HEADER_SHORTCUT_HUB: True,
    CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE: True,
    CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS: True,
    CONF_NATIVE_HEADER_SHORTCUT_INSTALLER: True,
    CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS: True,
    CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS: True,
    CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS: True,
    CONF_NATIVE_HEADER_SHORTCUT_ORDER: list(NATIVE_HEADER_SHORTCUT_IDS),
    CONF_SHOW_UNIFI_INTEGRATION: True,
    CONF_SHOW_CALIBRATION_BUTTONS: True,
    CONF_SHOW_DASHBOARD_HEADER: True,
    CONF_SHOW_CARD_HEADERS: True,
    CONF_DISCOVERY_UI_DENSITY: "dense",
    CONF_DISCOVERY_TEXT_SIZE: 12,
    CONF_DISCOVERY_CONTENT_WIDTH: "full",
    CONF_INSTALLER_UI_DENSITY: "comfortable",
    CONF_INSTALLER_TEXT_SIZE: 12,
    CONF_INSTALLER_CONTENT_WIDTH: "wide",
    CONF_ACTIVITY_LED_SENSITIVITY_PRESET: "normal",
    CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT: 0.10,
    CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT: 1.0,
    CONF_ACTIVITY_SLOW_PERIOD_MS: 500,
    CONF_ACTIVITY_MEDIUM_PERIOD_MS: 250,
    CONF_ACTIVITY_FAST_PERIOD_MS: 120,
    CONF_ACTIVITY_HOLD_SECONDS: 12.0,
    CONF_ACTIVITY_HYSTERESIS_PCT: 20.0,
}

UI_PREFERENCES_PATH = Path("/share/switch_vision/ui-preferences.json")
DATA_CONFIG = "config"
DATA_SHOW_CALIBRATION_BUTTONS = "show_calibration_buttons"
DATA_SHOW_DASHBOARD_HEADER = "show_dashboard_header"
DATA_SHOW_CARD_HEADERS = "show_card_headers"
DATA_ACTIVITY_LED_SETTINGS = "activity_led_settings"
DATA_NATIVE_HEADER_SETTINGS = "native_header_settings"
DATA_CALIBRATION_STORAGE_LOCK = "calibration_storage_lock"
DATA_LOVELACE_SIDEBAR_LOCK = "lovelace_sidebar_lock"

ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
ASSET_KINDS = ("logos", "faceplates")

MAX_PROFILE_NAME_LENGTH = 128
MAX_CALIBRATION_BYTES = 2 * 1024 * 1024
MAX_CALIBRATION_PORTS = 512
MAX_CALIBRATION_UPLINKS = 128
MAX_CALIBRATION_STATUS_LEDS = 128
MAX_CALIBRATION_DIMENSION = 16384
MAX_CALIBRATION_PIXELS = 64 * 1024 * 1024
MAX_ASSET_FILENAME_LENGTH = 255
FACEPLATE_DEFAULT = "__default__"
FACEPLATE_NONE = "__none__"  # Legacy migration sentinel; never preserved as an active faceplate state.


async def _ensure_dashboard_strategy_lovelace_resource(hass: HomeAssistant) -> bool:
    """Ensure the dashboard strategy is a real Lovelace module resource.

    Home Assistant's Community dashboard picker can discover metadata from any
    frontend-loaded script, but its strategy loader resolves custom strategy
    elements from Lovelace resources. Keep one Switch Vision-managed module
    resource current so the picker and loader use the same file/version.
    """
    lovelace_data = hass.data.get(LOVELACE_DATA)
    if lovelace_data is None:
        _LOGGER.warning(
            "Switch Vision dashboard strategy resource was not registered because "
            "Lovelace is not available"
        )
        return False

    if getattr(lovelace_data, "resource_mode", None) != MODE_STORAGE:
        _LOGGER.warning(
            "Switch Vision Community dashboard requires the strategy resource %s. "
            "Lovelace resources are in YAML mode, so add it as a module resource manually.",
            DASHBOARD_STRATEGY_JS_URL,
        )
        return False

    resources = lovelace_data.resources
    # ResourceStorageCollection lazily loads its storage document. async_get_info
    # is its public async loading path and is harmless if already loaded.
    await resources.async_get_info()
    items = list(resources.async_items() or [])
    matching = [
        item
        for item in items
        if str(item.get("url") or "").split("?", 1)[0] == DASHBOARD_STRATEGY_JS_PATH
    ]

    if not matching:
        await resources.async_create_item(
            {
                CONF_RESOURCE_TYPE_WS: "module",
                "url": DASHBOARD_STRATEGY_JS_URL,
            }
        )
        _LOGGER.info("Registered Switch Vision dashboard strategy Lovelace resource")
        return True

    primary = matching[0]
    updates: dict[str, Any] = {}
    if primary.get("type") != "module":
        updates[CONF_RESOURCE_TYPE_WS] = "module"
    if primary.get("url") != DASHBOARD_STRATEGY_JS_URL:
        updates["url"] = DASHBOARD_STRATEGY_JS_URL
    if updates:
        await resources.async_update_item(str(primary["id"]), updates)
        _LOGGER.info("Updated Switch Vision dashboard strategy Lovelace resource")

    # Previous test builds or manual troubleshooting may have created duplicate
    # entries for the same served path. Keep exactly one to avoid loading the
    # strategy bootstrap multiple times on every dashboard visit.
    for duplicate in matching[1:]:
        duplicate_id = duplicate.get("id")
        if duplicate_id:
            await resources.async_delete_item(str(duplicate_id))
            _LOGGER.info("Removed duplicate Switch Vision dashboard strategy resource")

    return True


_SWITCH_VISION_DASHBOARD_STRATEGY_TYPES = frozenset(
    {"custom:switch-vision", "switch-vision"}
)


def _is_switch_vision_lovelace_strategy(config: Any) -> bool:
    """Return True when a Lovelace config is a Switch Vision dashboard strategy."""
    if not isinstance(config, dict):
        return False
    strategy = config.get("strategy")
    return (
        isinstance(strategy, dict)
        and str(strategy.get("type") or "") in _SWITCH_VISION_DASHBOARD_STRATEGY_TYPES
    )


async def _sync_switch_vision_lovelace_dashboard_sidebar(
    hass: HomeAssistant, show_in_sidebar: bool
) -> int:
    """Persist and apply sidebar visibility to Switch Vision Lovelace dashboards."""
    lovelace_data = hass.data.get(LOVELACE_DATA)
    if lovelace_data is None:
        return 0

    lock = hass.data.setdefault(DOMAIN, {}).setdefault(
        DATA_LOVELACE_SIDEBAR_LOCK, asyncio.Lock()
    )

    async with lock:
        matches: list[tuple[str, Any, dict[str, Any]]] = []

        for url_path, dashboard_config in list(lovelace_data.dashboards.items()):
            if (
                not url_path
                or getattr(dashboard_config, "mode", None) != MODE_STORAGE
                or not isinstance(getattr(dashboard_config, "config", None), dict)
            ):
                continue

            metadata = dict(dashboard_config.config)
            dashboard_id = str(metadata.get("id") or "").strip()
            if not dashboard_id:
                continue

            try:
                saved_config = await dashboard_config.async_load(False)
            except ConfigNotFound:
                continue

            if _is_switch_vision_lovelace_strategy(saved_config):
                matches.append((str(url_path), dashboard_config, metadata))

        if not matches:
            return 0

        dashboards = DashboardsCollection(hass)
        await dashboards.async_load()
        changed = False

        for url_path, dashboard_config, metadata in matches:
            dashboard_id = str(metadata["id"])
            stored_item = dashboards.data.get(dashboard_id)
            if not isinstance(stored_item, dict):
                _LOGGER.warning(
                    "Switch Vision Lovelace dashboard %s is missing from dashboard storage",
                    url_path,
                )
                continue

            if bool(stored_item.get(CONF_SHOW_IN_SIDEBAR, True)) != bool(show_in_sidebar):
                updated = await dashboards.async_update_item(
                    dashboard_id,
                    {CONF_SHOW_IN_SIDEBAR: bool(show_in_sidebar)},
                )
                changed = True
            else:
                updated = stored_item

            # Mirror Home Assistant's own Lovelace dashboard panel update so the
            # sidebar changes immediately instead of requiring another restart.
            dashboard_config.config = dict(updated)
            frontend.async_register_built_in_panel(
                hass,
                component_name=LOVELACE_DOMAIN,
                sidebar_title=str(updated.get(CONF_TITLE) or "Switch Vision"),
                sidebar_icon=updated.get(CONF_ICON, DEFAULT_ICON),
                frontend_url_path=url_path,
                config={"mode": MODE_STORAGE},
                require_admin=bool(updated.get(CONF_REQUIRE_ADMIN, False)),
                update=True,
                show_in_sidebar=bool(show_in_sidebar),
            )

        if changed:
            # Persist immediately instead of waiting for the collection save delay.
            await dashboards.store.async_save({"items": dashboards.async_items()})

        return len(matches)


def _addon_slug_value(addon: Any) -> str:
    """Extract an installed Supervisor app slug from model or dict data."""
    if isinstance(addon, dict):
        return str(addon.get("slug") or "").strip()
    return str(getattr(addon, "slug", "") or "").strip()


def _resolve_switch_vision_app_slug(hass: HomeAssistant, base_slug: str) -> str:
    """Resolve a repository-prefixed installed slug from Supervisor's live list."""
    installed = hass.data.get(DATA_ADDONS_LIST) or []
    slugs = [slug for slug in (_addon_slug_value(addon) for addon in installed) if slug]
    if base_slug in slugs:
        return base_slug
    suffix = f"_{base_slug}"
    matches = sorted({slug for slug in slugs if slug.endswith(suffix)}, key=lambda value: (len(value), value))
    if matches:
        if len(matches) > 1:
            _LOGGER.warning("Multiple installed Supervisor apps match %s; using %s", base_slug, matches[0])
        return matches[0]
    return base_slug


async def async_switch_vision_app_states(hass: HomeAssistant) -> dict[str, dict[str, Any]]:
    """Return safe installed/ingress state for Switch Vision managed apps."""
    specs = {
        "discovery": DISCOVERY_APP_SLUG,
        "installer": INSTALLER_APP_SLUG,
        "snmp2mqtt": SNMP2MQTT_APP_SLUG,
        "unifi2mqtt": UNIFI2MQTT_APP_SLUG,
    }
    states: dict[str, dict[str, Any]] = {}
    try:
        client = get_supervisor_client(hass)
    except (KeyError, RuntimeError):
        client = None

    for key, base_slug in specs.items():
        slug = _resolve_switch_vision_app_slug(hass, base_slug)
        state = {
            "base_slug": base_slug,
            "slug": slug,
            "installed": False,
            "ingress": False,
            "ingress_panel": False,
            "available": False,
            "panel_path": f"/{slug}",
            "config_path": f"/config/app/{slug}/config",
        }
        states[key] = state
        if client is None:
            continue
        try:
            info = await client.addons.addon_info(slug)
        except SupervisorNotFoundError:
            continue
        except SupervisorError as err:
            _LOGGER.debug("Could not read Switch Vision app %s state: %s", slug, err)
            continue
        state.update(
            {
                "installed": True,
                "ingress": bool(getattr(info, "ingress", False)),
                "ingress_panel": bool(getattr(info, "ingress_panel", False)),
                "available": bool(getattr(info, "available", True)),
                "state": str(getattr(getattr(info, "state", None), "value", getattr(info, "state", "")) or ""),
            }
        )
    return states


async def _sync_switch_vision_app_ingress_panel(
    hass: HomeAssistant, slug: str, show_in_sidebar: bool
) -> bool:
    """Apply one supported Supervisor ingress-panel preference if installed."""
    slug = _resolve_switch_vision_app_slug(hass, slug)
    try:
        client = get_supervisor_client(hass)
        info = await client.addons.addon_info(slug)
    except (KeyError, RuntimeError, SupervisorNotFoundError):
        return False
    except SupervisorError as err:
        _LOGGER.warning("Could not read %s ingress-panel state: %s", slug, err)
        return False

    if not bool(getattr(info, "ingress", False)):
        return False
    if bool(getattr(info, "ingress_panel", False)) == bool(show_in_sidebar):
        return True

    try:
        await client.addons.set_addon_options(
            slug, AddonsOptions(ingress_panel=bool(show_in_sidebar))
        )
    except SupervisorError as err:
        _LOGGER.warning("Could not update %s ingress-panel state: %s", slug, err)
        return False
    return True


def _native_header_settings(entry: ConfigEntry) -> dict[str, Any]:
    """Return the ordered Native dashboard shortcut/header configuration."""
    raw_order = entry.options.get(
        CONF_NATIVE_HEADER_SHORTCUT_ORDER,
        DEFAULT_OPTIONS[CONF_NATIVE_HEADER_SHORTCUT_ORDER],
    )
    order = []
    for shortcut_id in raw_order if isinstance(raw_order, list) else []:
        shortcut = str(shortcut_id)
        if shortcut in NATIVE_HEADER_SHORTCUT_IDS and shortcut not in order:
            order.append(shortcut)
    order.extend(shortcut for shortcut in NATIVE_HEADER_SHORTCUT_IDS if shortcut not in order)
    return {
        "enabled": bool(entry.options.get(CONF_SHOW_DASHBOARD_HEADER, DEFAULT_OPTIONS[CONF_SHOW_DASHBOARD_HEADER])),
        "show_summary": bool(entry.options.get(CONF_NATIVE_HEADER_SHOW_SUMMARY, DEFAULT_OPTIONS[CONF_NATIVE_HEADER_SHOW_SUMMARY])),
        "show_refresh": bool(entry.options.get(CONF_NATIVE_HEADER_SHOW_REFRESH, DEFAULT_OPTIONS[CONF_NATIVE_HEADER_SHOW_REFRESH])),
        "show_version": bool(entry.options.get(CONF_NATIVE_HEADER_SHOW_VERSION, DEFAULT_OPTIONS[CONF_NATIVE_HEADER_SHOW_VERSION])),
        "order": order,
        "shortcuts": {
            "switch_vision_settings": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS, True)),
            "hub": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_HUB, True)),
            "discovery_settings": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS, True)),
            "installer": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_INSTALLER, True)),
            "installer_settings": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS, True)),
            "snmp2mqtt_settings": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS, True)),
            "unifi2mqtt_settings": bool(entry.options.get(CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS, True)),
        },
    }


def _activity_led_settings(entry: ConfigEntry) -> dict[str, Any]:
    """Return integration-wide Activity LED settings consumed by every card."""
    return {
        "sensitivity_preset": str(
            entry.options.get(
                CONF_ACTIVITY_LED_SENSITIVITY_PRESET,
                DEFAULT_OPTIONS[CONF_ACTIVITY_LED_SENSITIVITY_PRESET],
            )
        ),
        "slow_max_utilization_pct": float(
            entry.options.get(
                CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT,
                DEFAULT_OPTIONS[CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT],
            )
        ),
        "medium_max_utilization_pct": float(
            entry.options.get(
                CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT,
                DEFAULT_OPTIONS[CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT],
            )
        ),
        "slow_period_ms": int(
            entry.options.get(
                CONF_ACTIVITY_SLOW_PERIOD_MS,
                DEFAULT_OPTIONS[CONF_ACTIVITY_SLOW_PERIOD_MS],
            )
        ),
        "medium_period_ms": int(
            entry.options.get(
                CONF_ACTIVITY_MEDIUM_PERIOD_MS,
                DEFAULT_OPTIONS[CONF_ACTIVITY_MEDIUM_PERIOD_MS],
            )
        ),
        "fast_period_ms": int(
            entry.options.get(
                CONF_ACTIVITY_FAST_PERIOD_MS,
                DEFAULT_OPTIONS[CONF_ACTIVITY_FAST_PERIOD_MS],
            )
        ),
        "hold_seconds": float(
            entry.options.get(
                CONF_ACTIVITY_HOLD_SECONDS,
                DEFAULT_OPTIONS[CONF_ACTIVITY_HOLD_SECONDS],
            )
        ),
        "hysteresis_pct": float(
            entry.options.get(
                CONF_ACTIVITY_HYSTERESIS_PCT,
                DEFAULT_OPTIONS[CONF_ACTIVITY_HYSTERESIS_PCT],
            )
        ),
    }



CORE_SETTINGS_GROUP_KEYS = {
    "sidebar": (
        CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS,
        CONF_SHOW_PANEL_IN_SIDEBAR,
        CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR,
        CONF_SHOW_HUB_IN_SIDEBAR,
        CONF_SHOW_INSTALLER_IN_SIDEBAR,
    ),
    "native_header": (
        CONF_SHOW_DASHBOARD_HEADER,
        CONF_NATIVE_HEADER_SHOW_SUMMARY,
        CONF_NATIVE_HEADER_SHOW_REFRESH,
        CONF_NATIVE_HEADER_SHOW_VERSION,
        CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS,
        CONF_NATIVE_HEADER_SHORTCUT_HUB,
        CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE,
        CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS,
        CONF_NATIVE_HEADER_SHORTCUT_INSTALLER,
        CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS,
        CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS,
        CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS,
        CONF_NATIVE_HEADER_SHORTCUT_ORDER,
    ),
    "dashboard": (
        CONF_SHOW_CALIBRATION_BUTTONS,
        CONF_SHOW_CARD_HEADERS,
    ),
    "activity_leds": (
        CONF_ACTIVITY_LED_SENSITIVITY_PRESET,
        CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT,
        CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT,
        CONF_ACTIVITY_SLOW_PERIOD_MS,
        CONF_ACTIVITY_MEDIUM_PERIOD_MS,
        CONF_ACTIVITY_FAST_PERIOD_MS,
        CONF_ACTIVITY_HOLD_SECONDS,
        CONF_ACTIVITY_HYSTERESIS_PCT,
    ),
    "discovery": (
        CONF_DISCOVERY_UI_DENSITY,
        CONF_DISCOVERY_TEXT_SIZE,
        CONF_DISCOVERY_CONTENT_WIDTH,
        CONF_SHOW_UNIFI_INTEGRATION,
    ),
    "installer": (
        CONF_INSTALLER_UI_DENSITY,
        CONF_INSTALLER_TEXT_SIZE,
        CONF_INSTALLER_CONTENT_WIDTH,
    ),
}

CORE_SETTINGS_BOOL_KEYS = frozenset(
    {
        CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS,
        CONF_SHOW_PANEL_IN_SIDEBAR,
        CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR,
        CONF_SHOW_HUB_IN_SIDEBAR,
        CONF_SHOW_INSTALLER_IN_SIDEBAR,
        CONF_SHOW_DASHBOARD_HEADER,
        CONF_NATIVE_HEADER_SHOW_SUMMARY,
        CONF_NATIVE_HEADER_SHOW_REFRESH,
        CONF_NATIVE_HEADER_SHOW_VERSION,
        CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS,
        CONF_NATIVE_HEADER_SHORTCUT_HUB,
        CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE,
        CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS,
        CONF_NATIVE_HEADER_SHORTCUT_INSTALLER,
        CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS,
        CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS,
        CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS,
        CONF_SHOW_CALIBRATION_BUTTONS,
        CONF_SHOW_CARD_HEADERS,
        CONF_SHOW_UNIFI_INTEGRATION,
    }
)

CORE_SETTINGS_ENUMS = {
    CONF_ACTIVITY_LED_SENSITIVITY_PRESET: frozenset((*ACTIVITY_LED_PRESETS, "custom")),
    CONF_DISCOVERY_UI_DENSITY: frozenset(("comfortable", "compact", "dense")),
    CONF_DISCOVERY_CONTENT_WIDTH: frozenset(("standard", "wide", "full")),
    CONF_INSTALLER_UI_DENSITY: frozenset(("comfortable", "compact", "dense")),
    CONF_INSTALLER_CONTENT_WIDTH: frozenset(("standard", "wide", "full")),
}

CORE_SETTINGS_FLOAT_RANGES = {
    CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT: (0.001, 100.0),
    CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT: (0.001, 100.0),
    CONF_ACTIVITY_HOLD_SECONDS: (1.0, 120.0),
    CONF_ACTIVITY_HYSTERESIS_PCT: (0.0, 50.0),
}

CORE_SETTINGS_INT_RANGES = {
    CONF_ACTIVITY_SLOW_PERIOD_MS: (120, 2000),
    CONF_ACTIVITY_MEDIUM_PERIOD_MS: (120, 2000),
    CONF_ACTIVITY_FAST_PERIOD_MS: (120, 2000),
    CONF_DISCOVERY_TEXT_SIZE: (UI_TEXT_SIZE_MIN_PX, UI_TEXT_SIZE_MAX_PX),
    CONF_INSTALLER_TEXT_SIZE: (UI_TEXT_SIZE_MIN_PX, UI_TEXT_SIZE_MAX_PX),
}


def _canonical_native_header_order(value: Any) -> list[str]:
    """Return a complete, duplicate-free Native shortcut order."""
    if not isinstance(value, list):
        raise vol.Invalid("native_header_shortcut_order must be a list")
    order: list[str] = []
    for item in value:
        if not isinstance(item, str) or item not in NATIVE_HEADER_SHORTCUT_IDS:
            raise vol.Invalid("native_header_shortcut_order contains an unsupported shortcut")
        if item in order:
            raise vol.Invalid("native_header_shortcut_order contains a duplicate shortcut")
        order.append(item)
    order.extend(item for item in NATIVE_HEADER_SHORTCUT_IDS if item not in order)
    return order


def _core_settings_groups(
    options: dict[str, Any],
    app_states: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Return every normal Core option grouped for the Hub settings surface."""
    app_states = app_states or {}
    values = {
        key: options.get(key, DEFAULT_OPTIONS[key])
        for keys in CORE_SETTINGS_GROUP_KEYS.values()
        for key in keys
    }
    for key in (CONF_DISCOVERY_TEXT_SIZE, CONF_INSTALLER_TEXT_SIZE):
        values[key] = normalise_ui_text_size(values[key])

    # Existing installations may predate the explicit Hub/Installer sidebar
    # options. Preserve the current Supervisor ingress-panel state in that case,
    # matching the native Home Assistant Configure flow.
    if CONF_SHOW_HUB_IN_SIDEBAR not in options and app_states:
        values[CONF_SHOW_HUB_IN_SIDEBAR] = bool(
            app_states.get("discovery", {}).get(
                "ingress_panel", DEFAULT_OPTIONS[CONF_SHOW_HUB_IN_SIDEBAR]
            )
        )
    if CONF_SHOW_INSTALLER_IN_SIDEBAR not in options and app_states:
        values[CONF_SHOW_INSTALLER_IN_SIDEBAR] = bool(
            app_states.get("installer", {}).get(
                "ingress_panel", DEFAULT_OPTIONS[CONF_SHOW_INSTALLER_IN_SIDEBAR]
            )
        )

    raw_order = values[CONF_NATIVE_HEADER_SHORTCUT_ORDER]
    if not isinstance(raw_order, list):
        raw_order = list(DEFAULT_OPTIONS[CONF_NATIVE_HEADER_SHORTCUT_ORDER])
    order: list[str] = []
    for item in raw_order:
        item = str(item)
        if item in NATIVE_HEADER_SHORTCUT_IDS and item not in order:
            order.append(item)
    order.extend(item for item in NATIVE_HEADER_SHORTCUT_IDS if item not in order)
    values[CONF_NATIVE_HEADER_SHORTCUT_ORDER] = order

    return {
        group: {key: values[key] for key in keys}
        for group, keys in CORE_SETTINGS_GROUP_KEYS.items()
    }


async def _core_settings_payload(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return the complete browser-safe Core settings contract for the Hub."""
    app_states = await async_switch_vision_app_states(hass)
    return {
        "schema_version": 1,
        "settings": _core_settings_groups(dict(entry.options), app_states),
        "defaults": _core_settings_groups(dict(DEFAULT_OPTIONS)),
        "apps": {
            key: {
                "installed": bool(state.get("installed", False)),
                "available": bool(state.get("available", False)),
                "ingress": bool(state.get("ingress", False)),
            }
            for key, state in app_states.items()
        },
    }


def _normalise_core_settings_update(
    current_options: dict[str, Any], requested: Any
) -> dict[str, Any]:
    """Strictly validate one partial Hub Core settings update."""
    if not isinstance(requested, dict):
        raise vol.Invalid("settings must be an object")

    allowed_groups = set(CORE_SETTINGS_GROUP_KEYS)
    unknown_groups = sorted(set(requested) - allowed_groups)
    if unknown_groups:
        raise vol.Invalid(f"Unknown Core settings group: {unknown_groups[0]}")

    updated = dict(current_options)
    for group, group_values in requested.items():
        if not isinstance(group_values, dict):
            raise vol.Invalid(f"Core settings group {group} must be an object")
        allowed_keys = set(CORE_SETTINGS_GROUP_KEYS[group])
        unknown_keys = sorted(set(group_values) - allowed_keys)
        if unknown_keys:
            raise vol.Invalid(f"Unknown Core setting: {unknown_keys[0]}")

        for key, value in group_values.items():
            if key == CONF_NATIVE_HEADER_SHORTCUT_ORDER:
                updated[key] = _canonical_native_header_order(value)
                continue

            if key in CORE_SETTINGS_BOOL_KEYS:
                if type(value) is not bool:
                    raise vol.Invalid(f"{key} must be true or false")
                updated[key] = value
                continue

            allowed_values = CORE_SETTINGS_ENUMS.get(key)
            if allowed_values is not None:
                if not isinstance(value, str) or value not in allowed_values:
                    raise vol.Invalid(f"{key} has an unsupported value")
                updated[key] = value
                continue

            float_range = CORE_SETTINGS_FLOAT_RANGES.get(key)
            if float_range is not None:
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise vol.Invalid(f"{key} must be a number")
                number = float(value)
                if not math.isfinite(number):
                    raise vol.Invalid(f"{key} must be finite")
                minimum, maximum = float_range
                if not minimum <= number <= maximum:
                    raise vol.Invalid(
                        f"{key} must be between {minimum} and {maximum}"
                    )
                updated[key] = number
                continue

            int_range = CORE_SETTINGS_INT_RANGES.get(key)
            if int_range is not None:
                if isinstance(value, bool) or not isinstance(value, int):
                    raise vol.Invalid(f"{key} must be a whole number")
                minimum, maximum = int_range
                if not minimum <= value <= maximum:
                    raise vol.Invalid(
                        f"{key} must be between {minimum} and {maximum}"
                    )
                updated[key] = value
                continue

            raise vol.Invalid(f"Unknown Core setting: {key}")

    def option(key: str) -> Any:
        return updated.get(key, DEFAULT_OPTIONS[key])

    if option(CONF_ACTIVITY_LED_SENSITIVITY_PRESET) == "custom":
        slow_max = float(option(CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT))
        medium_max = float(option(CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT))
        if slow_max >= medium_max:
            raise vol.Invalid(
                "Custom Activity LED slow utilization must be below medium utilization"
            )

    slow_period = int(option(CONF_ACTIVITY_SLOW_PERIOD_MS))
    medium_period = int(option(CONF_ACTIVITY_MEDIUM_PERIOD_MS))
    fast_period = int(option(CONF_ACTIVITY_FAST_PERIOD_MS))
    if not (fast_period <= medium_period <= slow_period):
        raise vol.Invalid(
            "Activity LED periods must satisfy fast_period <= medium_period <= slow_period"
        )

    return updated


def _ui_preferences(entry: ConfigEntry) -> dict[str, Any]:
    """Build the shared Discovery and Installer UI preference document."""
    return {
        "schema_version": 1,
        "core": {
            "activity_leds": _activity_led_settings(entry),
        },
        "discovery": {
            "density": entry.options.get(CONF_DISCOVERY_UI_DENSITY, "comfortable"),
            "text_size": normalise_ui_text_size(
                entry.options.get(CONF_DISCOVERY_TEXT_SIZE, UI_TEXT_SIZE_DEFAULT_PX)
            ),
            "content_width": entry.options.get(CONF_DISCOVERY_CONTENT_WIDTH, "standard"),
            "show_unifi_integration": bool(entry.options.get(CONF_SHOW_UNIFI_INTEGRATION, True)),
        },
        "installer": {
            "density": entry.options.get(CONF_INSTALLER_UI_DENSITY, "comfortable"),
            "text_size": normalise_ui_text_size(
                entry.options.get(CONF_INSTALLER_TEXT_SIZE, UI_TEXT_SIZE_DEFAULT_PX)
            ),
            "content_width": entry.options.get(CONF_INSTALLER_CONTENT_WIDTH, "standard"),
        },
    }


def _write_ui_preferences(preferences: dict[str, Any]) -> None:
    """Atomically write shared UI preferences for local apps."""
    UI_PREFERENCES_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = UI_PREFERENCES_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(preferences, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, UI_PREFERENCES_PATH)


def _normalise_profile(value: str) -> str:
    """Trim a profile name while allowing optional empty metadata values."""
    return str(value or "").strip()


PROTECTED_FACTORY_PROFILES = {
    "default_cisco_48_port",
    "cisco_2960x_24p",
    "cisco_2960s_48p",
    "cisco_3560cg_8pc",
}


def _is_protected_factory_profile(value: Any) -> bool:
    return _normalise_profile(value) in PROTECTED_FACTORY_PROFILES


def _validate_profile_name(value: Any) -> str:
    """Return one safe, non-empty profile name."""
    profile = _normalise_profile(value)
    if not profile:
        raise vol.Invalid("profile name is required")
    if len(profile) > MAX_PROFILE_NAME_LENGTH:
        raise vol.Invalid(
            f"profile name must be {MAX_PROFILE_NAME_LENGTH} characters or fewer"
        )
    if profile in {".", ".."}:
        raise vol.Invalid("profile name is not valid")
    forbidden = set('/\\<>\"\'&')
    if any((not character.isprintable()) or character in forbidden for character in profile):
        raise vol.Invalid(
            "profile name contains an unsupported control, path, or markup character"
        )
    return profile


def _normalise_calibration(value: Any) -> dict[str, Any]:
    """Accept a JSON object or JSON string and return a dict."""
    if isinstance(value, str):
        if len(value.encode("utf-8")) > MAX_CALIBRATION_BYTES:
            raise vol.Invalid(
                f"calibration payload exceeds {MAX_CALIBRATION_BYTES} bytes"
            )
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as err:
            raise vol.Invalid(f"calibration is not valid JSON: {err.msg}") from err
    else:
        parsed = value
    if not isinstance(parsed, dict):
        raise vol.Invalid("calibration must be a JSON object or JSON object string")
    return parsed


def _safe_asset_filename(value: Any, *, allow_special: bool = True) -> str:
    """Validate a stored asset filename without requiring the file to exist yet."""
    filename = str(value or "").strip()
    if allow_special and filename in {FACEPLATE_DEFAULT, FACEPLATE_NONE}:
        return filename
    if not filename:
        return ""
    if len(filename) > MAX_ASSET_FILENAME_LENGTH:
        raise vol.Invalid("asset filename is too long")
    if filename != Path(filename).name or filename in {".", ".."}:
        raise vol.Invalid("asset filename must not contain a path")
    if any(not character.isprintable() for character in filename):
        raise vol.Invalid("asset filename contains a control character")
    return filename


def _normalise_visible_faceplate(calibration: dict[str, Any]) -> bool:
    """Migrate hidden/none faceplate states to the visible recommended default."""
    ui = calibration.get("ui")
    if not isinstance(ui, dict):
        return False
    faceplate = ui.get("faceplate")
    if not isinstance(faceplate, dict):
        return False

    raw_file = str(faceplate.get("file") or FACEPLATE_DEFAULT).strip()
    source = str(faceplate.get("source") or "").strip().lower()
    hidden = raw_file == FACEPLATE_NONE or source == "none" or faceplate.get("show") is False
    if not hidden:
        return False

    faceplate["show"] = True
    faceplate["file"] = FACEPLATE_DEFAULT
    faceplate["source"] = "default"
    return True


def _finite_number(value: Any, label: str) -> float:
    """Return a finite numeric value or raise a user-facing validation error."""
    try:
        number = float(value)
    except (TypeError, ValueError) as err:
        raise vol.Invalid(f"{label} must be a number") from err
    if not math.isfinite(number):
        raise vol.Invalid(f"{label} must be finite")
    return number


def _validate_pair(
    value: Any,
    label: str,
    *,
    width: float,
    height: float,
    size: bool = False,
) -> None:
    """Validate one [x, y] coordinate or [width, height] size pair."""
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise vol.Invalid(f"{label} must contain exactly two numbers")
    first = _finite_number(value[0], f"{label}[0]")
    second = _finite_number(value[1], f"{label}[1]")
    if size:
        maximum = MAX_CALIBRATION_DIMENSION * 2
        if first <= 0 or second <= 0:
            raise vol.Invalid(f"{label} dimensions must be positive")
        if first > maximum or second > maximum:
            raise vol.Invalid(f"{label} dimensions are unreasonably large")
        return

    # Calibration elements may intentionally sit slightly outside the artwork,
    # but values many canvases away are almost certainly corrupt imports.
    if not (-width <= first <= width * 2):
        raise vol.Invalid(f"{label} x coordinate is outside the safe canvas range")
    if not (-height <= second <= height * 2):
        raise vol.Invalid(f"{label} y coordinate is outside the safe canvas range")


def _validate_calibration(profile: str, calibration: dict[str, Any]) -> dict[str, Any]:
    """Validate a calibration before it is saved or returned to a browser."""
    profile = _validate_profile_name(profile)
    try:
        encoded = json.dumps(
            calibration,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as err:
        raise vol.Invalid(f"calibration is not JSON-safe: {err}") from err
    if len(encoded) > MAX_CALIBRATION_BYTES:
        raise vol.Invalid(
            f"calibration payload exceeds {MAX_CALIBRATION_BYTES} bytes"
        )

    schema_version = calibration.get("schema_version")
    if schema_version not in (None, 0, 1, "1", 2, "2"):
        raise vol.Invalid("unsupported calibration schema_version")

    image = calibration.get("image")
    ports = calibration.get("ports")
    uplinks = calibration.get("sfp")
    status_leds = calibration.get("status_leds")
    if not isinstance(image, dict):
        raise vol.Invalid("calibration image must be an object")
    if not isinstance(ports, dict):
        raise vol.Invalid("calibration ports must be an object")
    if not isinstance(uplinks, dict):
        raise vol.Invalid("calibration sfp must be an object")
    if not isinstance(status_leds, dict):
        raise vol.Invalid("calibration status_leds must be an object")

    width = _finite_number(image.get("width"), "image width")
    height = _finite_number(image.get("height"), "image height")
    if width <= 0 or height <= 0:
        raise vol.Invalid("image width and height must be positive")
    if width > MAX_CALIBRATION_DIMENSION or height > MAX_CALIBRATION_DIMENSION:
        raise vol.Invalid("image dimensions exceed the supported canvas limit")
    if width * height > MAX_CALIBRATION_PIXELS:
        raise vol.Invalid("image canvas contains too many pixels")
    image_file = str(image.get("file") or "").strip()
    if image_file:
        # Bundled profiles use faceplates/name.ext; custom selections use name.ext.
        if image_file.startswith("faceplates/"):
            _safe_asset_filename(image_file.split("/", 1)[1], allow_special=False)
        else:
            _safe_asset_filename(image_file, allow_special=False)

    if len(ports) > MAX_CALIBRATION_PORTS:
        raise vol.Invalid(
            f"calibration contains more than {MAX_CALIBRATION_PORTS} RJ45 ports"
        )
    if not ports and not uplinks:
        raise vol.Invalid("calibration must contain at least one RJ45 or optical port")
    if len(uplinks) > MAX_CALIBRATION_UPLINKS:
        raise vol.Invalid(
            f"calibration contains more than {MAX_CALIBRATION_UPLINKS} uplinks"
        )
    if len(status_leds) > MAX_CALIBRATION_STATUS_LEDS:
        raise vol.Invalid(
            f"calibration contains more than {MAX_CALIBRATION_STATUS_LEDS} status LEDs"
        )

    for key, port in ports.items():
        if not isinstance(port, dict):
            raise vol.Invalid(f"port {key} must be an object")
        for part in ("center", "number", "led_left", "led_right"):
            _validate_pair(
                port.get(part), f"port {key} {part}", width=width, height=height
            )
        _validate_pair(
            port.get("hitbox"),
            f"port {key} hitbox",
            width=width,
            height=height,
            size=True,
        )
        for part in ("led_left_size", "led_right_size"):
            if part in port:
                _validate_pair(
                    port.get(part),
                    f"port {key} {part}",
                    width=width,
                    height=height,
                    size=True,
                )

    for key, uplink in uplinks.items():
        if not isinstance(uplink, dict):
            raise vol.Invalid(f"uplink {key} must be an object")
        _validate_pair(
            uplink.get("center"), f"uplink {key} center", width=width, height=height
        )
        if "label" in uplink:
            _validate_pair(
                uplink.get("label"), f"uplink {key} label", width=width, height=height
            )
        if "hitbox" in uplink:
            _validate_pair(
                uplink.get("hitbox"),
                f"uplink {key} hitbox",
                width=width,
                height=height,
                size=True,
            )

    for key, point in status_leds.items():
        if str(key).upper() == "MODE":
            continue
        _validate_pair(
            point, f"status LED {key}", width=width, height=height
        )

    for metadata_key in ("profile_name", "base_profile_name"):
        metadata_value = str(calibration.get(metadata_key) or "").strip()
        if metadata_value:
            _validate_profile_name(metadata_value)
    stored_profile = str(calibration.get("profile_name") or "").strip()
    if stored_profile and stored_profile != profile:
        raise vol.Invalid("calibration profile_name does not match the target profile")

    ui = calibration.get("ui")
    if ui is not None and not isinstance(ui, dict):
        raise vol.Invalid("calibration ui must be an object")
    if isinstance(ui, dict):
        faceplate = ui.get("faceplate")
        if faceplate is not None and not isinstance(faceplate, dict):
            raise vol.Invalid("ui.faceplate must be an object")
        if isinstance(faceplate, dict):
            file_value = str(faceplate.get("file") or FACEPLATE_DEFAULT).strip()
            _safe_asset_filename(file_value, allow_special=True)
            if "show" in faceplate and not isinstance(faceplate.get("show"), bool):
                raise vol.Invalid("ui.faceplate.show must be true or false")
            fit = str(faceplate.get("fit") or "fill").strip().lower()
            if fit not in {"fill", "contain", "cover"}:
                raise vol.Invalid("ui.faceplate.fit must be fill, contain, or cover")
            opacity = _finite_number(faceplate.get("opacity", 1), "ui.faceplate.opacity")
            if not 0 <= opacity <= 1:
                raise vol.Invalid("ui.faceplate.opacity must be between 0 and 1")

        for box_name in (
            "logo",
            "calibration_button",
            "status_panel",
            "status_panel_2",
        ):
            box = ui.get(box_name)
            if box is None:
                continue
            if not isinstance(box, dict):
                raise vol.Invalid(f"ui.{box_name} must be an object")
            if box_name == "logo" and box.get("file"):
                _safe_asset_filename(box.get("file"), allow_special=False)
            for coordinate in ("x", "y"):
                if coordinate in box:
                    number = _finite_number(
                        box.get(coordinate), f"ui.{box_name}.{coordinate}"
                    )
                    maximum = width if coordinate == "x" else height
                    if not (-maximum <= number <= maximum * 2):
                        raise vol.Invalid(
                            f"ui.{box_name}.{coordinate} is outside the safe canvas range"
                        )
            for dimension in ("width", "height"):
                if dimension in box:
                    number = _finite_number(
                        box.get(dimension), f"ui.{box_name}.{dimension}"
                    )
                    if number <= 0 or number > MAX_CALIBRATION_DIMENSION * 2:
                        raise vol.Invalid(
                            f"ui.{box_name}.{dimension} must be a reasonable positive number"
                        )
            fields = box.get("fields")
            if fields is not None:
                if not isinstance(fields, dict):
                    raise vol.Invalid(f"ui.{box_name}.fields must be an object")
                for field_name, point in fields.items():
                    _validate_pair(
                        point,
                        f"ui.{box_name}.fields.{field_name}",
                        width=width,
                        height=height,
                    )

    for text_key in ("model", "profile", "generated_by", "faceplate_file"):
        text_value = str(calibration.get(text_key) or "")
        if len(text_value) > 512:
            raise vol.Invalid(f"{text_key} is too long")
    if calibration.get("faceplate_file"):
        _safe_asset_filename(calibration.get("faceplate_file"), allow_special=True)

    return calibration


_PROFILE_MIRROR_METADATA = {
    "profile_name",
    "profile_scope",
    "base_profile_name",
    "mirrored_from_profile",
}


def _calibration_content(calibration: dict[str, Any]) -> dict[str, Any]:
    """Return calibration content without profile/mirroring metadata."""
    return {
        key: value
        for key, value in calibration.items()
        if key not in _PROFILE_MIRROR_METADATA
    }


def _is_mirrored_base_profile(
    base_calibration: Any,
    source_calibration: Any,
    base_profile: str,
    source_profile: str,
) -> bool:
    """Return true when a base profile is the mirror of a faceplate profile."""
    if not isinstance(base_calibration, dict) or not isinstance(source_calibration, dict):
        return False

    mirrored_from = _normalise_profile(base_calibration.get("mirrored_from_profile", ""))
    if mirrored_from:
        return mirrored_from == source_profile

    # v1.9.29 and earlier mirrors did not include mirrored_from_profile. They can
    # still be identified safely because the backend copied the source payload
    # verbatim and changed only the profile-scope metadata below.
    if _normalise_profile(base_calibration.get("profile_name", "")) != base_profile:
        return False
    if _normalise_profile(base_calibration.get("base_profile_name", "")) != base_profile:
        return False
    if _normalise_profile(source_calibration.get("base_profile_name", "")) != base_profile:
        return False
    return _calibration_content(base_calibration) == _calibration_content(source_calibration)


def _migrate_legacy_faceplate_mirrors(data: dict[str, Any]) -> bool:
    """Replace legacy whole-calibration base mirrors with active-profile pointers."""
    profiles = data.setdefault("profiles", {})
    active_profiles = data.setdefault("active_profiles", {})
    changed = False

    if not isinstance(profiles, dict):
        data["profiles"] = profiles = {}
        changed = True
    if not isinstance(active_profiles, dict):
        data["active_profiles"] = active_profiles = {}
        changed = True

    for base_profile, base_calibration in list(profiles.items()):
        if "__faceplate__" in base_profile or not isinstance(base_calibration, dict):
            continue
        prefix = f"{base_profile}__faceplate__"
        candidates = [
            (name, calibration)
            for name, calibration in profiles.items()
            if name.startswith(prefix) and isinstance(calibration, dict)
        ]
        mirrored_from = _normalise_profile(base_calibration.get("mirrored_from_profile", ""))
        ordered = sorted(candidates, key=lambda item: item[0] != mirrored_from)
        source_profile = next((
            name
            for name, source_calibration in ordered
            if _is_mirrored_base_profile(
                base_calibration, source_calibration, base_profile, name
            )
        ), "")
        if not source_profile:
            continue

        active_profiles[base_profile] = source_profile
        # The legacy base object is a byte-for-byte faceplate calibration copy,
        # not an independent default-faceplate profile. Keeping it is precisely
        # what leaked Status Box/layout state between faceplates.
        profiles.pop(base_profile, None)
        changed = True

    # Drop stale/unsafe pointers rather than allowing one switch namespace to
    # resolve another switch's calibration profile.
    for base_profile, active_profile in list(active_profiles.items()):
        base = _normalise_profile(base_profile)
        active = _normalise_profile(active_profile)
        if (
            not base
            or not active
            or active not in profiles
            or not active.startswith(f"{base}__faceplate__")
        ):
            active_profiles.pop(base_profile, None)
            changed = True

    return changed


def _read_unifi_device_snapshot(path: Path, device_id: str) -> dict[str, Any]:
    """Return one normalized UniFi2MQTT device from the shared snapshot."""
    try:
        stat = path.stat()
    except OSError as err:
        return {"exists": False, "device": None, "error": f"UniFi2MQTT snapshot is unavailable: {err}"}
    if stat.st_size > MAX_UNIFI_SNAPSHOT_BYTES:
        return {"exists": True, "device": None, "error": "UniFi2MQTT snapshot exceeds the Switch Vision safety limit."}
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as err:
        return {"exists": True, "device": None, "error": f"UniFi2MQTT snapshot could not be read: {err}"}
    if not isinstance(document, dict) or not isinstance(document.get("devices"), list):
        return {"exists": True, "device": None, "error": "UniFi2MQTT snapshot schema is invalid."}
    wanted = str(device_id).strip()
    for raw in document["devices"]:
        if not isinstance(raw, dict) or str(raw.get("id") or "").strip() != wanted:
            continue
        # Return only the normalized bridge payload. The authenticated Home
        # Assistant websocket already scopes access to the current HA user.
        return {
            "exists": True,
            "device": raw,
            "schema_version": document.get("schema_version"),
            "product": document.get("product"),
            "bridge_version": document.get("version"),
            "generated_at": document.get("generated_at"),
        }
    return {"exists": True, "device": None, "error": "Requested UniFi device was not found in the current snapshot."}


def _extract_dashboard_cards(document: Any) -> list[dict[str, Any]]:
    """Extract Switch Vision card configs from generated dashboard YAML."""
    cards: list[dict[str, Any]] = []

    def visit(value: Any) -> None:
        if isinstance(value, list):
            for item in value:
                visit(item)
            return
        if not isinstance(value, dict):
            return
        if value.get("type") == "custom:switch-vision-3650":
            cards.append(dict(value))
            return
        for key in ("views", "sections", "cards"):
            if key in value:
                visit(value[key])

    visit(document)
    return cards


def _dashboard_file_payload(
    path: Path,
    show_calibration_buttons: bool = True,
    show_dashboard_header: bool = True,
    show_card_headers: bool = True,
) -> dict[str, Any]:
    """Read the generated review YAML without modifying it."""
    if not path.is_file():
        return {
            "exists": False,
            "path": str(path),
            "cards": [],
            "card_count": 0,
            "message": "Run Discovery with dashboard-card generation enabled, then refresh the Switch Vision panel.",
            "warnings": ["Manual generated dashboard YAML remains available as the fallback workflow."],
        }
    try:
        initial_stat = path.stat()
    except OSError as err:
        return {
            "exists": path.exists(),
            "path": str(path),
            "cards": [],
            "card_count": 0,
            "message": f"Generated dashboard YAML metadata could not be read: {err}",
            "warnings": ["The source file was not changed."],
        }
    if initial_stat.st_size > MAX_GENERATED_DASHBOARD_BYTES:
        return {
            "exists": True,
            "path": str(path),
            "cards": [],
            "card_count": 0,
            "message": "Generated dashboard YAML exceeds the Switch Vision safety limit.",
            "warnings": [
                f"Maximum allowed size is {MAX_GENERATED_DASHBOARD_BYTES} bytes.",
                "The source file was not changed.",
            ],
        }
    try:
        text = path.read_text(encoding="utf-8")
        document = yaml.safe_load(text)
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as err:
        return {
            "exists": path.exists(),
            "path": str(path),
            "cards": [],
            "card_count": 0,
            "message": f"Generated dashboard YAML could not be read or parsed: {err}",
            "warnings": ["The source file was not changed."],
        }
    cards = _extract_dashboard_cards(document)
    for card in cards:
        card["calibration_button"] = bool(show_calibration_buttons)

        # Card-header visibility is a single integration-wide preference.
        # Per-card flags from v1.9.56-v1.9.61 are deliberately ignored and
        # removed so native and custom dashboards have one source of truth.
        card["show_card_header"] = bool(show_card_headers)
        card.pop("show_card_header_information", None)
        card.pop("show_card_metadata", None)

        # The native sidebar must keep the active calibration/faceplate selection
        # scoped to one discovered switch. Discovery's generated YAML carries a
        # model/factory calibration profile so manual YAML dashboards can opt into
        # shared geometry, but using that shared name directly in the native panel
        # causes every matching model to inherit one switch's selected faceplate.
        # Use the stable per-card switch/member key for native-panel persistence;
        # exact-model reconciliation still supplies the recommended factory geometry.
        native_switch_key = str(
            card.get("selected_switch") or card.get("member") or ""
        ).strip()
        if native_switch_key:
            # Keep calibration_profile as the read-only factory/template profile.
            # The frontend derives writable storage as native_<switch key>.
            card["switch_vision_native_panel"] = True
    try:
        modified = path.stat().st_mtime
        stat_warning: list[str] = []
    except OSError as err:
        # The file may be replaced between read and stat while Discovery writes it.
        # Keep the successfully parsed cards and report the metadata race instead of
        # failing the entire native-panel websocket request.
        modified = None
        stat_warning = [f"Generated dashboard metadata could not be read: {err}"]
    return {
        "exists": True,
        "path": str(path),
        "runtime_version": PANEL_VERSION,
        "asset_revision": PANEL_VERSION,
        "modified": modified,
        "cards": cards,
        "card_count": len(cards),
        "warnings": stat_warning + ([] if cards else ["No custom:switch-vision-3650 cards were found in the generated file."]),
        "show_calibration_buttons": bool(show_calibration_buttons),
        "show_dashboard_header": bool(show_dashboard_header),
        "show_card_headers": bool(show_card_headers),
    }


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up Switch Vision services."""
    store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
    domain_data = hass.data.setdefault(DOMAIN, {})
    storage_lock = domain_data.get(DATA_CALIBRATION_STORAGE_LOCK)
    if storage_lock is None:
        storage_lock = asyncio.Lock()
        domain_data[DATA_CALIBRATION_STORAGE_LOCK] = storage_lock

    domain_config = config.get(DOMAIN, {}) if isinstance(config, dict) else {}
    configured_dashboard_path = domain_config.get("dashboard_config_path") if isinstance(domain_config, dict) else None
    dashboard_path = Path(str(configured_dashboard_path or DEFAULT_DASHBOARD_CONFIG_PATH))
    domain_data[DATA_CONFIG] = {"dashboard_config_path": str(dashboard_path)}

    async def _load() -> dict[str, Any]:
        data = await store.async_load()
        if not isinstance(data, dict):
            return {"profiles": {}, "active_profiles": {}}
        profiles = data.get("profiles")
        if not isinstance(profiles, dict):
            data["profiles"] = {}
        active_profiles = data.get("active_profiles")
        if not isinstance(active_profiles, dict):
            data["active_profiles"] = {}
        if _migrate_legacy_faceplate_mirrors(data):
            await store.async_save(data)
            _LOGGER.info("Migrated legacy Switch Vision faceplate calibration mirrors to isolated active-profile pointers")
        return data

    async def _save(data: dict[str, Any]) -> None:
        await store.async_save(data)

    def _asset_root() -> Path:
        return Path(hass.config.path("www", "switch-vision"))

    def _list_assets() -> dict[str, Any]:
        root = _asset_root()
        result: dict[str, Any] = {"root": "/config/www/switch-vision"}
        warnings: list[str] = []
        for kind in ASSET_KINDS:
            folder = root / kind
            files: list[str] = []
            try:
                folder.mkdir(parents=True, exist_ok=True)
                files = sorted(
                    path.name
                    for path in folder.iterdir()
                    if path.is_file()
                    and path.suffix.lower() in ASSET_EXTENSIONS
                    and path.name == Path(path.name).name
                    and not path.name.startswith(".")
                )
            except OSError as err:
                # Asset folders are optional. A permissions or transient filesystem
                # problem must not prevent the integration or native panel loading.
                warnings.append(f"Could not access {folder}: {err}")
            result[kind] = files
            result[f"{kind}_path"] = f"/config/www/switch-vision/{kind}"
        result["extensions"] = sorted(ASSET_EXTENSIONS)
        result["warnings"] = warnings
        return result

    def _fingerprint_faceplates() -> dict[str, dict[str, Any]]:
        """Return SHA-256 metadata for locally installed faceplate assets."""
        folder = _asset_root() / "faceplates"
        fingerprints: dict[str, dict[str, Any]] = {}

        try:
            paths = sorted(
                path
                for path in folder.iterdir()
                if path.is_file()
                and path.suffix.lower() in ASSET_EXTENSIONS
                and path.name == Path(path.name).name
                and not path.name.startswith(".")
            )
        except OSError:
            return fingerprints

        for path in paths:
            try:
                stat = path.stat()
                digest = hashlib.sha256()

                with path.open("rb") as handle:
                    while chunk := handle.read(1024 * 1024):
                        digest.update(chunk)

                fingerprints[path.name] = {
                    "sha256": digest.hexdigest(),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                }
            except OSError:
                # One unreadable asset must not make the whole manager fail.
                continue

        return fingerprints

    async def handle_save(call: ServiceCall) -> None:
        profile = _validate_profile_name(call.data["profile"])
        if _is_protected_factory_profile(profile):
            raise vol.Invalid("factory calibration profiles are read-only")
        calibration = dict(_normalise_calibration(call.data["calibration"]))
        _normalise_visible_faceplate(calibration)
        # mirrored_from_profile is legacy backend-owned metadata and must never
        # be trusted from a browser/imported payload.
        calibration.pop("mirrored_from_profile", None)
        _validate_calibration(profile, calibration)
        activate_for_base = bool(call.data.get("mirror_to_base", False))
        base_profile = _normalise_profile(calibration.get("base_profile_name", ""))
        if activate_for_base and _is_protected_factory_profile(base_profile):
            raise vol.Invalid("factory calibration profiles cannot be active-profile destinations")
        if activate_for_base and (not base_profile or not profile.startswith(f"{base_profile}__faceplate__")):
            raise vol.Invalid("active faceplate profile does not belong to the supplied base profile")

        active_profile_changed = False
        async with storage_lock:
            data = await _load()
            profiles = data.setdefault("profiles", {})
            active_profiles = data.setdefault("active_profiles", {})
            profiles[profile] = calibration

            if activate_for_base and base_profile and base_profile != profile:
                previous = active_profiles.get(base_profile)
                active_profiles[base_profile] = profile
                active_profile_changed = previous != profile
            elif base_profile and base_profile == profile:
                # Saving the default/recommended faceplate makes the independent
                # base profile active again; no faceplate-specific state is copied.
                active_profile_changed = active_profiles.pop(base_profile, None) is not None

            await _save(data)

        changed_profiles = [profile]
        hass.bus.async_fire(
            EVENT_CALIBRATION_UPDATED,
            {
                "profile": profile,
                "profiles_changed": changed_profiles,
                "base_profile_name": base_profile if active_profile_changed or activate_for_base else "",
                "active_profile": profile if activate_for_base else "",
                "active_profile_changed": active_profile_changed,
                "action": "saved",
                # Retain this field for old frontends/event consumers, but v2.1.4
                # no longer mirrors calibration content into the base profile.
                "mirror_to_base": False,
            },
        )
        _LOGGER.info(
            "Saved Switch Vision calibration profile %s%s",
            profile,
            f" (active for {base_profile})" if activate_for_base else "",
        )

    async def handle_delete(call: ServiceCall) -> None:
        profile = _validate_profile_name(call.data["profile"])
        base_profile = ""
        active_profile_removed = False
        changed_profiles: list[str] = []

        async with storage_lock:
            data = await _load()
            profiles = data.setdefault("profiles", {})
            active_profiles = data.setdefault("active_profiles", {})

            if _is_protected_factory_profile(profile):
                raise vol.Invalid(
                    "factory calibration profiles are protected from deletion"
                )

            active_targets = {
                _normalise_profile(active_profile)
                for active_profile in active_profiles.values()
                if _normalise_profile(active_profile)
            }

            if profile in active_profiles or profile in active_targets:
                raise vol.Invalid(
                    "active calibration profiles are protected from deletion"
                )

            deleted_calibration = profiles.pop(profile, None)
            existed = deleted_calibration is not None
            if existed:
                changed_profiles.append(profile)

            if isinstance(deleted_calibration, dict):
                base_profile = _normalise_profile(
                    deleted_calibration.get("base_profile_name", "")
                )
            if not base_profile and profile in active_profiles:
                base_profile = profile

            if base_profile and active_profiles.get(base_profile) == profile:
                active_profiles.pop(base_profile, None)
                active_profile_removed = True
            elif profile in active_profiles:
                active_profiles.pop(profile, None)
                base_profile = profile
                active_profile_removed = True

            await _save(data)

        hass.bus.async_fire(
            EVENT_CALIBRATION_UPDATED,
            {
                "profile": profile,
                "profiles_changed": changed_profiles,
                "base_profile_name": base_profile if active_profile_removed else "",
                "action": "deleted",
                "existed": existed,
                "active_profile_removed": active_profile_removed,
            },
        )
        _LOGGER.info(
            "Deleted Switch Vision calibration profile %s",
            profile,
        )

    async def handle_reset(call: ServiceCall) -> None:
        scope = str(call.data["scope"]).strip().lower()
        base_profile = _normalise_profile(call.data.get("base_profile", ""))
        scope_prefix = str(call.data.get("scope_prefix", "")).strip()
        # v1.9.54 accepts explicit native/custom scopes as well as the
        # v1.9.52-v1.9.53 namespace + scope_prefix form. This keeps older
        # frontends compatible while making the service contract unambiguous.
        if scope in {"native", "custom"}:
            scope_prefix = f"{scope}_"
            scope = "namespace"
        if base_profile:
            base_profile = _validate_profile_name(base_profile)

        async with storage_lock:
            data = await _load()
            profiles = data.setdefault("profiles", {})

            active_profiles = data.setdefault("active_profiles", {})
            if scope == "all":
                matching = list(profiles)
                profiles.clear()
                active_profiles.clear()
                event_profile = "*"
            elif scope == "namespace":
                if scope_prefix not in {"native_", "custom_"}:
                    raise vol.Invalid("scope_prefix must be native_ or custom_ when scope is namespace")
                matching = [name for name in list(profiles) if name.startswith(scope_prefix)]
                for name in matching:
                    profiles.pop(name, None)
                for name in list(active_profiles):
                    if name.startswith(scope_prefix):
                        active_profiles.pop(name, None)
                event_profile = scope_prefix
            else:
                if not base_profile:
                    raise vol.Invalid("base_profile is required when scope is switch")
                prefix = f"{base_profile}__faceplate__"
                matching = [
                    name for name in list(profiles)
                    if name == base_profile or name.startswith(prefix)
                ]
                for name in matching:
                    profiles.pop(name, None)
                active_profiles.pop(base_profile, None)
                event_profile = base_profile

            await _save(data)

        removed = len(matching)
        hass.bus.async_fire(
            EVENT_CALIBRATION_UPDATED,
            {
                "profile": event_profile,
                "profiles_changed": matching,
                "base_profile_name": base_profile if scope == "switch" else "",
                "scope_prefix": scope_prefix if scope == "namespace" else "",
                "action": "reset_scope" if scope == "namespace" else f"reset_{scope}",
                "removed": removed,
            },
        )
        _LOGGER.info(
            "Reset Switch Vision calibration profiles scope=%s base_profile=%s removed=%s",
            scope,
            base_profile or "*",
            removed,
        )

    async def handle_reload(call: ServiceCall) -> None:
        hass.bus.async_fire(
            EVENT_CALIBRATION_UPDATED,
            {"profile": "*", "action": "reload"},
        )

    async def handle_set_ui_density(call: ServiceCall) -> None:
        """Update Discovery management-UI density without touching dashboards."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise RuntimeError("Switch Vision integration entry is not available.")
        entry = entries[0]
        options = dict(entry.options)
        options[CONF_DISCOVERY_UI_DENSITY] = str(call.data["density"])
        hass.config_entries.async_update_entry(entry, options=options)
        await hass.async_add_executor_job(_write_ui_preferences, _ui_preferences(entry))

    @websocket_api.websocket_command(GET_WS_SCHEMA)
    @websocket_api.async_response
    async def websocket_get_calibration(hass: HomeAssistant, connection, msg):
        """Return one saved Switch Vision calibration profile."""
        requested_profile = _validate_profile_name(msg["profile"])
        resolved_profile = requested_profile
        active_profile = ""
        exact_profile = bool(msg.get("exact", False))
        async with storage_lock:
            data = await _load()
            profiles = data.setdefault("profiles", {})
            active_profiles = data.setdefault("active_profiles", {})

            # A stable switch base profile now stores its own calibration only.
            # The currently selected custom faceplate is a separate pointer, so
            # loading it cannot overwrite default-faceplate Status Box/layout data.
            candidate = "" if exact_profile else _normalise_profile(active_profiles.get(requested_profile, ""))
            if candidate:
                if candidate in profiles and candidate.startswith(f"{requested_profile}__faceplate__"):
                    resolved_profile = candidate
                    active_profile = candidate
                else:
                    active_profiles.pop(requested_profile, None)
                    await _save(data)

            calibration = profiles.get(resolved_profile)
            if isinstance(calibration, dict) and _normalise_visible_faceplate(calibration):
                # Persist the migration so a v1.9.35/legacy hidden state cannot
                # return after another browser refresh or Home Assistant restart.
                await _save(data)

        invalid = False
        validation_error = ""
        if calibration is not None:
            try:
                _validate_calibration(resolved_profile, calibration)
            except vol.Invalid as err:
                invalid = True
                validation_error = str(err)
                _LOGGER.error(
                    "Rejected invalid stored Switch Vision calibration %s: %s",
                    resolved_profile,
                    validation_error,
                )
                calibration = None

        connection.send_result(
            msg["id"],
            {
                "profile": resolved_profile,
                "requested_profile": requested_profile,
                "active_profile": active_profile,
                "exists": calibration is not None,
                "invalid": invalid,
                "validation_error": validation_error,
                "calibration": calibration,
                "source": (
                    "invalid saved profile rejected; using current card config / baked defaults"
                    if invalid
                    else (
                        "Home Assistant storage"
                        if calibration is not None
                        else "current card config / baked defaults"
                    )
                ),
                "storage_key": STORAGE_KEY,
                "storage_path": STORAGE_PATH,
                "profile_path": f"{STORAGE_PATH} → profiles.{resolved_profile}",
            },
        )

    @websocket_api.websocket_command(LIST_WS_SCHEMA)
    @websocket_api.async_response
    async def websocket_list_calibrations(hass: HomeAssistant, connection, msg):
        """Return saved calibration profiles plus safe Hub management metadata."""
        async with storage_lock:
            data = await _load()
            stored_profiles = data.setdefault("profiles", {})
            active_profiles = dict(data.setdefault("active_profiles", {}))
            profiles = sorted(stored_profiles.keys())

            items = []
            for profile in profiles:
                calibration = stored_profiles.get(profile)
                if not isinstance(calibration, dict):
                    calibration = {}

                marker = "__faceplate__"
                faceplate_profile = marker in profile

                base_profile = _normalise_profile(
                    calibration.get("base_profile_name", "")
                )
                if not base_profile:
                    base_profile = (
                        profile.split(marker, 1)[0]
                        if faceplate_profile
                        else profile
                    )

                stored_scope = str(
                    calibration.get("profile_scope") or ""
                ).strip().lower()

                if stored_scope in {"native", "custom"}:
                    scope = stored_scope
                elif base_profile.startswith("native_"):
                    scope = "native"
                elif base_profile.startswith("custom_"):
                    scope = "custom"
                elif _is_protected_factory_profile(base_profile):
                    scope = "factory"
                else:
                    scope = "other"

                ui = calibration.get("ui")
                ui = ui if isinstance(ui, dict) else {}

                faceplate_ui = ui.get("faceplate")
                faceplate_ui = (
                    faceplate_ui
                    if isinstance(faceplate_ui, dict)
                    else {}
                )

                raw_faceplate = str(
                    faceplate_ui.get("file")
                    or calibration.get("faceplate_file")
                    or FACEPLATE_DEFAULT
                ).strip()

                faceplate_source = str(
                    faceplate_ui.get("source") or ""
                ).strip().lower()

                faceplate = raw_faceplate
                if faceplate.startswith("faceplates/"):
                    faceplate = faceplate.split("/", 1)[1]

                active_pointer = _normalise_profile(
                    active_profiles.get(base_profile, "")
                )

                active = (
                    active_pointer == profile
                    if active_pointer
                    else profile == base_profile
                )

                items.append(
                    {
                        "profile": profile,
                        "base_profile": base_profile,
                        "scope": scope,
                        "faceplate_profile": faceplate_profile,
                        "faceplate": faceplate,
                        "faceplate_source": faceplate_source,
                        "active": active,
                        "model": str(calibration.get("model") or ""),
                        "port_count": len(
                            calibration.get("ports")
                            if isinstance(calibration.get("ports"), dict)
                            else {}
                        ),
                        "sfp_count": len(
                            calibration.get("sfp")
                            if isinstance(calibration.get("sfp"), dict)
                            else {}
                        ),
                    }
                )

        assets = await hass.async_add_executor_job(_list_assets)
        fingerprints = await hass.async_add_executor_job(_fingerprint_faceplates)
        available_faceplates = set(assets.get("faceplates") or [])

        fingerprint_groups: dict[str, list[str]] = {}
        for filename, metadata in fingerprints.items():
            digest = str(metadata.get("sha256") or "")
            if digest:
                fingerprint_groups.setdefault(digest, []).append(filename)

        duplicate_faceplate_groups = [
            {
                "sha256": digest,
                "files": sorted(filenames),
            }
            for digest, filenames in sorted(fingerprint_groups.items())
            if len(filenames) > 1
        ]

        for item in items:
            faceplate = str(item.get("faceplate") or "").strip()

            if faceplate in {"", FACEPLATE_DEFAULT, FACEPLATE_NONE}:
                exists = True
            else:
                exists = faceplate in available_faceplates

            item["faceplate_exists"] = exists
            item["stale"] = bool(
                item["faceplate_profile"]
                and faceplate not in {"", FACEPLATE_DEFAULT, FACEPLATE_NONE}
                and not exists
            )

            fingerprint = fingerprints.get(faceplate, {})
            digest = str(fingerprint.get("sha256") or "")
            duplicates = sorted(fingerprint_groups.get(digest, [])) if digest else []

            item["faceplate_sha256"] = digest
            item["faceplate_size"] = fingerprint.get("size")
            item["faceplate_modified"] = fingerprint.get("modified")
            item["duplicate_faceplate_content"] = len(duplicates) > 1
            item["duplicate_faceplates"] = duplicates if len(duplicates) > 1 else []

        connection.send_result(
            msg["id"],
            {
                "profiles": profiles,
                "items": items,
                "active_profiles": active_profiles,
                "duplicate_faceplate_groups": duplicate_faceplate_groups,
                "storage_key": STORAGE_KEY,
                "storage_path": STORAGE_PATH,
            },
        )

    @websocket_api.websocket_command(LIST_ASSETS_WS_SCHEMA)
    @websocket_api.async_response
    async def websocket_list_assets(hass: HomeAssistant, connection, msg):
        """Return safe logo and faceplate filenames from the Switch Vision folders."""
        assets = await hass.async_add_executor_job(_list_assets)
        connection.send_result(msg["id"], assets)

    @websocket_api.websocket_command(DASHBOARD_PANEL_WS_SCHEMA)
    @websocket_api.async_response
    async def websocket_get_dashboard_panel(hass: HomeAssistant, connection, msg):
        """Return generated card configuration for the native Switch Vision panel."""
        show_calibration_buttons = hass.data.setdefault(DOMAIN, {}).get(DATA_SHOW_CALIBRATION_BUTTONS, True)
        show_dashboard_header = hass.data.setdefault(DOMAIN, {}).get(DATA_SHOW_DASHBOARD_HEADER, True)
        show_card_headers = hass.data.setdefault(DOMAIN, {}).get(DATA_SHOW_CARD_HEADERS, True)
        payload = await hass.async_add_executor_job(
            _dashboard_file_payload,
            dashboard_path,
            bool(show_calibration_buttons),
            bool(show_dashboard_header),
            bool(show_card_headers),
        )
        payload["native_header"] = dict(
            hass.data.setdefault(DOMAIN, {}).get(
                DATA_NATIVE_HEADER_SETTINGS,
                {
                    "enabled": bool(show_dashboard_header),
                    "show_summary": True,
                    "show_refresh": True,
                    "show_version": True,
                    "order": list(NATIVE_HEADER_SHORTCUT_IDS),
                    "shortcuts": {shortcut: True for shortcut in NATIVE_HEADER_SHORTCUT_IDS},
                },
            )
        )
        connection.send_result(msg["id"], payload)

    @websocket_api.websocket_command(UNIFI_DEVICE_WS_SCHEMA)
    @websocket_api.async_response
    async def websocket_get_unifi_device(hass: HomeAssistant, connection, msg):
        """Return one live normalized UniFi device from UniFi2MQTT."""
        result = await hass.async_add_executor_job(
            _read_unifi_device_snapshot, UNIFI_DEVICES_PATH, str(msg["device_id"])
        )
        connection.send_result(msg["id"], result)

    @websocket_api.websocket_command(APP_STATES_WS_SCHEMA)
    @websocket_api.async_response
    async def websocket_get_app_states(hass: HomeAssistant, connection, msg):
        """Return sanitized Switch Vision app availability to the Native panel."""
        raw_states = await async_switch_vision_app_states(hass)
        apps = {}
        for key, state in raw_states.items():
            apps[key] = {
                "installed": bool(state.get("installed", False)),
                "ingress": bool(state.get("ingress", False)),
                "available": bool(state.get("available", False)),
                "slug": str(state.get("slug") or ""),
                "panel_path": str(state.get("panel_path") or ""),
                "config_path": str(state.get("config_path") or ""),
            }
        connection.send_result(msg["id"], {"apps": apps})

    @websocket_api.websocket_command(UI_SETTINGS_WS_SCHEMA)
    @websocket_api.async_response
    async def websocket_get_ui_settings(hass: HomeAssistant, connection, msg):
        """Return integration-wide card presentation settings to all card types."""
        domain_state = hass.data.setdefault(DOMAIN, {})
        connection.send_result(
            msg["id"],
            {
                "show_card_headers": bool(domain_state.get(DATA_SHOW_CARD_HEADERS, True)),
                "activity_leds": dict(
                    domain_state.get(
                        DATA_ACTIVITY_LED_SETTINGS,
                        {
                            "sensitivity_preset": DEFAULT_OPTIONS[CONF_ACTIVITY_LED_SENSITIVITY_PRESET],
                            "slow_max_utilization_pct": DEFAULT_OPTIONS[CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT],
                            "medium_max_utilization_pct": DEFAULT_OPTIONS[CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT],
                            "slow_period_ms": DEFAULT_OPTIONS[CONF_ACTIVITY_SLOW_PERIOD_MS],
                            "medium_period_ms": DEFAULT_OPTIONS[CONF_ACTIVITY_MEDIUM_PERIOD_MS],
                            "fast_period_ms": DEFAULT_OPTIONS[CONF_ACTIVITY_FAST_PERIOD_MS],
                            "hold_seconds": DEFAULT_OPTIONS[CONF_ACTIVITY_HOLD_SECONDS],
                            "hysteresis_pct": DEFAULT_OPTIONS[CONF_ACTIVITY_HYSTERESIS_PCT],
                        },
                    )
                ),
            },
        )


    @websocket_api.websocket_command(CORE_SETTINGS_WS_SCHEMA)
    @websocket_api.require_admin
    @websocket_api.async_response
    async def websocket_get_core_settings(hass: HomeAssistant, connection, msg):
        """Return all normal Core settings to the authenticated Hub."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            connection.send_error(
                msg["id"],
                "not_configured",
                "Switch Vision integration is not configured",
            )
            return
        connection.send_result(
            msg["id"], await _core_settings_payload(hass, entries[0])
        )

    @websocket_api.websocket_command(SET_CORE_SETTINGS_WS_SCHEMA)
    @websocket_api.require_admin
    @websocket_api.async_response
    async def websocket_set_core_settings(hass: HomeAssistant, connection, msg):
        """Persist validated Hub Core settings in the existing config entry."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            connection.send_error(
                msg["id"],
                "not_configured",
                "Switch Vision integration is not configured",
            )
            return
        entry = entries[0]
        reset_to_defaults = bool(msg.get("reset_to_defaults", False))
        try:
            if reset_to_defaults:
                options = dict(DEFAULT_OPTIONS)
            else:
                options = _normalise_core_settings_update(
                    dict(entry.options), msg.get("settings", {})
                )
        except vol.Invalid as err:
            connection.send_error(
                msg["id"], "invalid_settings", str(err)
            )
            return

        hass.config_entries.async_update_entry(entry, options=options)
        payload = await _core_settings_payload(hass, entry)
        payload["saved"] = True
        payload["reset_to_defaults"] = reset_to_defaults
        connection.send_result(msg["id"], payload)

    # Create the public asset folders during integration setup so users can copy
    # files into them immediately, even before opening Calibration. Directory
    # scanning and folder creation are blocking filesystem operations, so keep
    # them off Home Assistant's event loop.
    await hass.async_add_executor_job(_list_assets)

    websocket_api.async_register_command(hass, websocket_get_calibration)
    websocket_api.async_register_command(hass, websocket_list_calibrations)
    websocket_api.async_register_command(hass, websocket_list_assets)
    websocket_api.async_register_command(hass, websocket_get_dashboard_panel)
    websocket_api.async_register_command(hass, websocket_get_unifi_device)

    @websocket_api.websocket_command(SET_NATIVE_HEADER_ORDER_WS_SCHEMA)
    @websocket_api.require_admin
    @websocket_api.async_response
    async def websocket_set_native_header_shortcut_order(hass: HomeAssistant, connection, msg):
        """Persist Native dashboard shortcut visibility and ordering."""
        requested = [str(value) for value in msg.get("order", [])]
        order = []
        for shortcut in requested:
            if shortcut in NATIVE_HEADER_SHORTCUT_IDS and shortcut not in order:
                order.append(shortcut)
        order.extend(shortcut for shortcut in NATIVE_HEADER_SHORTCUT_IDS if shortcut not in order)

        requested_shortcuts = msg.get("shortcuts")
        requested_shortcuts = requested_shortcuts if isinstance(requested_shortcuts, dict) else {}

        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            connection.send_error(msg["id"], "not_configured", "Switch Vision integration is not configured")
            return
        entry = entries[0]
        options = dict(entry.options)
        options[CONF_NATIVE_HEADER_SHORTCUT_ORDER] = order
        for shortcut_id, enabled in requested_shortcuts.items():
            option_key = NATIVE_HEADER_SHORTCUT_OPTION_KEYS.get(str(shortcut_id))
            if option_key:
                options[option_key] = bool(enabled)
        hass.config_entries.async_update_entry(entry, options=options)
        native_header = _native_header_settings(entry)
        hass.data.setdefault(DOMAIN, {})[DATA_NATIVE_HEADER_SETTINGS] = native_header
        hass.bus.async_fire(EVENT_UI_SETTINGS_UPDATED)
        connection.send_result(
            msg["id"],
            {"order": native_header["order"], "shortcuts": native_header["shortcuts"]},
        )

    websocket_api.async_register_command(hass, websocket_get_app_states)
    websocket_api.async_register_command(hass, websocket_get_ui_settings)
    websocket_api.async_register_command(hass, websocket_get_core_settings)
    websocket_api.async_register_command(hass, websocket_set_core_settings)
    websocket_api.async_register_command(hass, websocket_set_native_header_shortcut_order)

    panel_file = Path(__file__).with_name("switch-vision-panel.js")
    iconset_file = Path(__file__).with_name("switch-vision-iconset.js")
    card_file = Path(__file__).with_name("switch-vision-card.js")
    dashboard_strategy_file = Path(__file__).with_name("switch-vision-dashboard-strategy.js")
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(PANEL_JS_PATH, str(panel_file), cache_headers=False),
            StaticPathConfig(ICONSET_JS_PATH, str(iconset_file), cache_headers=False),
            StaticPathConfig(CARD_JS_PATH, str(card_file), cache_headers=False),
            StaticPathConfig(DASHBOARD_STRATEGY_JS_PATH, str(dashboard_strategy_file), cache_headers=False),
        ]
    )
    frontend.add_extra_js_url(hass, ICONSET_JS_URL)
    # Home Assistant custom dashboard strategies must be loaded as Lovelace
    # resources. Register/update our module resource in storage mode. Keep the
    # existing panel registration completely independent as the stable fallback.
    strategy_resource_ready = await _ensure_dashboard_strategy_lovelace_resource(hass)
    if not strategy_resource_ready:
        # YAML-resource installs cannot be mutated safely by an integration. The
        # global load preserves backwards visibility while the log explains the
        # required manual module-resource entry.
        frontend.add_extra_js_url(hass, DASHBOARD_STRATEGY_JS_URL)

    # Create a config entry automatically for existing YAML-based installs so the
    # integration gains a normal Configure/options screen without requiring users
    # to remove their current configuration.
    if not hass.config_entries.async_entries(DOMAIN):
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "import"},
                data={"dashboard_config_path": str(dashboard_path)},
            )
        )

    async_register_admin_service(hass, DOMAIN, "save_calibration", handle_save, schema=SAVE_SCHEMA)
    async_register_admin_service(hass, DOMAIN, "delete_calibration", handle_delete, schema=DELETE_SCHEMA)
    async_register_admin_service(hass, DOMAIN, "reset_calibrations", handle_reset, schema=RESET_SCHEMA)
    async_register_admin_service(hass, DOMAIN, "reload_calibrations", handle_reload)
    async_register_admin_service(hass, DOMAIN, "set_ui_density", handle_set_ui_density, schema=UI_DENSITY_SCHEMA)

    return True

async def _apply_entry_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Apply presentation/sidebar options without reloading the integration.

    Home Assistant ingress panels owned by other apps must not be disturbed when
    Switch Vision presentation options change. Keep the Native panel registered
    and update it in-place instead of removing/re-registering it.
    """
    stored_config = hass.data.setdefault(DOMAIN, {}).get(DATA_CONFIG, {})
    dashboard_path = Path(
        str(
            entry.data.get("dashboard_config_path")
            or stored_config.get("dashboard_config_path")
            or DEFAULT_DASHBOARD_CONFIG_PATH
        )
    )
    sidebar_master = bool(
        entry.options.get(
            CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS,
            DEFAULT_OPTIONS[CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS],
        )
    )
    show_in_sidebar = sidebar_master and bool(
        entry.options.get(CONF_SHOW_PANEL_IN_SIDEBAR, DEFAULT_OPTIONS[CONF_SHOW_PANEL_IN_SIDEBAR])
    )
    show_lovelace_in_sidebar = sidebar_master and bool(
        entry.options.get(CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR, DEFAULT_OPTIONS[CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR])
    )
    app_states = await async_switch_vision_app_states(hass)
    hub_preference = (
        bool(entry.options[CONF_SHOW_HUB_IN_SIDEBAR])
        if CONF_SHOW_HUB_IN_SIDEBAR in entry.options
        else bool(app_states.get("discovery", {}).get("ingress_panel", True))
    )
    installer_preference = (
        bool(entry.options[CONF_SHOW_INSTALLER_IN_SIDEBAR])
        if CONF_SHOW_INSTALLER_IN_SIDEBAR in entry.options
        else bool(app_states.get("installer", {}).get("ingress_panel", True))
    )
    show_hub_in_sidebar = sidebar_master and hub_preference
    show_installer_in_sidebar = sidebar_master and installer_preference
    show_calibration_buttons = bool(
        entry.options.get(CONF_SHOW_CALIBRATION_BUTTONS, DEFAULT_OPTIONS[CONF_SHOW_CALIBRATION_BUTTONS])
    )
    show_dashboard_header = bool(
        entry.options.get(CONF_SHOW_DASHBOARD_HEADER, DEFAULT_OPTIONS[CONF_SHOW_DASHBOARD_HEADER])
    )
    show_card_headers = bool(entry.options.get(CONF_SHOW_CARD_HEADERS, DEFAULT_OPTIONS[CONF_SHOW_CARD_HEADERS]))
    activity_led_settings = _activity_led_settings(entry)
    native_header_settings = _native_header_settings(entry)

    domain_state = hass.data.setdefault(DOMAIN, {})
    domain_state[DATA_SHOW_CALIBRATION_BUTTONS] = show_calibration_buttons
    domain_state[DATA_SHOW_DASHBOARD_HEADER] = show_dashboard_header
    domain_state[DATA_SHOW_CARD_HEADERS] = show_card_headers
    domain_state[DATA_ACTIVITY_LED_SETTINGS] = activity_led_settings
    domain_state[DATA_NATIVE_HEADER_SETTINGS] = native_header_settings
    hass.bus.async_fire(
        EVENT_UI_SETTINGS_UPDATED,
        {
            "show_card_headers": show_card_headers,
            "activity_leds": activity_led_settings,
            "native_header": native_header_settings,
        },
    )

    try:
        await hass.async_add_executor_job(_write_ui_preferences, _ui_preferences(entry))
    except OSError as err:
        # Shared UI preferences improve consistency with local apps, but failure
        # to write /share must not stop the integration/sidebar update.
        _LOGGER.warning("Could not write Switch Vision UI preferences: %s", err)

    panel_runtime_config = {
        "automatic_dashboard": True,
        "version": PANEL_VERSION,
        "generated_dashboard_path": str(dashboard_path),
        "manual_yaml_fallback": True,
        "show_in_sidebar": show_in_sidebar,
        "runtime_version": PANEL_VERSION,
        "asset_revision": PANEL_VERSION,
        "show_calibration_buttons": show_calibration_buttons,
        "show_dashboard_header": show_dashboard_header,
        "show_card_headers": show_card_headers,
        "native_header": native_header_settings,
    }

    # Register once if missing (normal initial setup/recovery). On option changes
    # the panel already exists and is updated in-place below; do not remove it.
    if not async_panel_exists(hass, PANEL_URL_PATH):
        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=PANEL_URL_PATH,
            webcomponent_name="switch-vision-panel",
            sidebar_title="Switch Vision",
            sidebar_icon="switch-vision:logo",
            module_url=PANEL_JS_URL,
            config=panel_runtime_config,
        )

    # panel_custom.async_register_panel() does not expose show_in_sidebar. Update
    # the existing panel record in-place so Native visibility changes without a
    # config-entry reload or a transient global sidebar panel-list rebuild.
    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="Switch Vision",
        sidebar_icon="switch-vision:logo",
        frontend_url_path=PANEL_URL_PATH,
        config={
            **panel_runtime_config,
            "_panel_custom": {
                "name": "switch-vision-panel",
                "embed_iframe": False,
                "trust_external": False,
                "module_url": PANEL_JS_URL,
            },
        },
        require_admin=False,
        update=True,
        show_in_sidebar=show_in_sidebar,
    )

    try:
        await _sync_switch_vision_lovelace_dashboard_sidebar(
            hass, show_lovelace_in_sidebar
        )
    except (OSError, ValueError, TypeError) as err:
        _LOGGER.warning(
            "Could not update Switch Vision Lovelace dashboard sidebar visibility: %s",
            err,
        )

    await _sync_switch_vision_app_ingress_panel(
        hass, DISCOVERY_APP_SLUG, show_hub_in_sidebar
    )
    await _sync_switch_vision_app_ingress_panel(
        hass, INSTALLER_APP_SLUG, show_installer_in_sidebar
    )


async def _async_entry_options_updated(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Apply changed Switch Vision options live without reloading."""
    await _apply_entry_options(hass, entry)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Switch Vision config entry and presentation options."""
    await _apply_entry_options(hass, entry)

    # Presentation options are intentionally live-updated. Using
    # OptionsFlowWithReload here used to remove/re-register the Native panel and
    # could make unrelated ingress sidebar icons disappear when both Switch
    # Vision dashboard entries were hidden.
    entry.async_on_unload(entry.add_update_listener(_async_entry_options_updated))

    async def _handle_lovelace_updated(_event) -> None:
        # Read the current option each time; the config entry is no longer
        # reloaded merely to apply a presentation change.
        try:
            sidebar_master = bool(
                entry.options.get(
                    CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS,
                    DEFAULT_OPTIONS[CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS],
                )
            )
            lovelace_preference = bool(
                entry.options.get(
                    CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR,
                    DEFAULT_OPTIONS[CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR],
                )
            )
            await _sync_switch_vision_lovelace_dashboard_sidebar(
                hass, sidebar_master and lovelace_preference
            )
        except (OSError, ValueError, TypeError) as err:
            _LOGGER.warning(
                "Could not apply Switch Vision Lovelace sidebar preference: %s",
                err,
            )

    entry.async_on_unload(
        hass.bus.async_listen(EVENT_LOVELACE_UPDATED, _handle_lovelace_updated)
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the Switch Vision config entry."""
    if async_panel_exists(hass, PANEL_URL_PATH):
        async_remove_panel(hass, PANEL_URL_PATH)
    return True
