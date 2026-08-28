"""Config and options flow for Switch Vision Core."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.data_entry_flow import section
from homeassistant.helpers import selector

from . import (
    ACTIVITY_LED_PRESETS,
    CONF_ACTIVITY_FAST_PERIOD_MS,
    CONF_ACTIVITY_HOLD_SECONDS,
    CONF_ACTIVITY_HYSTERESIS_PCT,
    CONF_ACTIVITY_LED_SENSITIVITY_PRESET,
    CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT,
    CONF_ACTIVITY_MEDIUM_PERIOD_MS,
    CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT,
    CONF_ACTIVITY_SLOW_PERIOD_MS,
    CONF_DISCOVERY_CONTENT_WIDTH,
    CONF_DISCOVERY_TEXT_SIZE,
    CONF_DISCOVERY_UI_DENSITY,
    CONF_INSTALLER_CONTENT_WIDTH,
    CONF_INSTALLER_TEXT_SIZE,
    CONF_INSTALLER_UI_DENSITY,
    CONF_SHOW_CALIBRATION_BUTTONS,
    CONF_SHOW_CARD_HEADERS,
    CONF_SHOW_DASHBOARD_HEADER,
    CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR,
    CONF_SHOW_PANEL_IN_SIDEBAR,
    CONF_SHOW_UNIFI_INTEGRATION,
    CONF_NATIVE_HEADER_SHORTCUT_DISCOVERY_SETTINGS,
    CONF_NATIVE_HEADER_SHORTCUT_HUB,
    CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE,
    CONF_NATIVE_HEADER_SHORTCUT_INSTALLER,
    CONF_NATIVE_HEADER_SHORTCUT_INSTALLER_SETTINGS,
    CONF_NATIVE_HEADER_SHORTCUT_SNMP2MQTT_SETTINGS,
    CONF_NATIVE_HEADER_SHORTCUT_SWITCH_VISION_SETTINGS,
    CONF_NATIVE_HEADER_SHORTCUT_UNIFI2MQTT_SETTINGS,
    CONF_NATIVE_HEADER_SHOW_REFRESH,
    CONF_NATIVE_HEADER_SHOW_SUMMARY,
    CONF_NATIVE_HEADER_SHOW_VERSION,
    CONF_SHOW_ALL_SWITCH_VISION_SIDEBAR_ITEMS,
    CONF_SHOW_HUB_IN_SIDEBAR,
    CONF_SHOW_INSTALLER_IN_SIDEBAR,
    async_switch_vision_app_states,
    DEFAULT_DASHBOARD_CONFIG_PATH,
    DEFAULT_OPTIONS,
    DOMAIN,
    UI_TEXT_SIZE_MAX_PX,
    UI_TEXT_SIZE_MIN_PX,
    normalise_ui_text_size,
)

CONF_RESET_TO_DEFAULTS = "reset_to_defaults"


class SwitchVisionConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create the single local Switch Vision Core integration entry."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up Switch Vision Core from the integrations page."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        if user_input is not None:
            return self.async_create_entry(
                title="Switch Vision",
                data={"dashboard_config_path": DEFAULT_DASHBOARD_CONFIG_PATH},
            )
        return self.async_show_form(step_id="user")

    async def async_step_import(
        self, import_data: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Import an existing YAML-based installation."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="Switch Vision",
            data={
                "dashboard_config_path": str(
                    (import_data or {}).get(
                        "dashboard_config_path", DEFAULT_DASHBOARD_CONFIG_PATH
                    )
                )
            },
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the Switch Vision Core options flow."""
        return SwitchVisionOptionsFlow()


class SwitchVisionOptionsFlow(OptionsFlow):
    """Manage Switch Vision Core settings."""

    def _value(self, key: str) -> Any:
        """Return one saved option, migrating legacy UI font labels in memory."""
        value = self.config_entry.options.get(key, DEFAULT_OPTIONS[key])
        if key in {CONF_DISCOVERY_TEXT_SIZE, CONF_INSTALLER_TEXT_SIZE}:
            return normalise_ui_text_size(value)
        return value

    async def _schema(self) -> vol.Schema:
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
                    default=(
                        bool(self.config_entry.options[CONF_SHOW_HUB_IN_SIDEBAR])
                        if CONF_SHOW_HUB_IN_SIDEBAR in self.config_entry.options
                        else bool(discovery.get("ingress_panel", True))
                    ),
                )
            ] = bool
        else:
            sidebar_fields[vol.Optional("sidebar_hub_not_installed", default=False)] = read_only_bool
        if installer.get("installed") and installer.get("ingress"):
            sidebar_fields[
                vol.Required(
                    CONF_SHOW_INSTALLER_IN_SIDEBAR,
                    default=(
                        bool(self.config_entry.options[CONF_SHOW_INSTALLER_IN_SIDEBAR])
                        if CONF_SHOW_INSTALLER_IN_SIDEBAR in self.config_entry.options
                        else bool(installer.get("ingress_panel", True))
                    ),
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
                    CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE,
                    default=self._value(CONF_NATIVE_HEADER_SHORTCUT_MAINTENANCE),
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
                            ): vol.In(
                                list(range(UI_TEXT_SIZE_MIN_PX, UI_TEXT_SIZE_MAX_PX + 1))
                            ),
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
                            ): vol.In(
                                list(range(UI_TEXT_SIZE_MIN_PX, UI_TEXT_SIZE_MAX_PX + 1))
                            ),
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

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show Switch Vision Core settings, including Activity LED 2.0 controls."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if user_input.get(CONF_RESET_TO_DEFAULTS):
                return self.async_create_entry(data=dict(DEFAULT_OPTIONS))

            activity = dict(user_input.get("activity_leds") or {})
            if (
                activity.get(CONF_ACTIVITY_LED_SENSITIVITY_PRESET) == "custom"
                and float(activity[CONF_ACTIVITY_SLOW_MAX_UTILIZATION_PCT])
                >= float(activity[CONF_ACTIVITY_MEDIUM_MAX_UTILIZATION_PCT])
            ):
                errors["base"] = "invalid_activity_thresholds"

            slow_period = int(activity[CONF_ACTIVITY_SLOW_PERIOD_MS])
            medium_period = int(activity[CONF_ACTIVITY_MEDIUM_PERIOD_MS])
            fast_period = int(activity[CONF_ACTIVITY_FAST_PERIOD_MS])
            if not (fast_period <= medium_period <= slow_period):
                errors["base"] = "invalid_activity_periods"

            if not errors:
                saved = dict(self.config_entry.options)
                for group in ("sidebar", "native_header", "dashboard", "activity_leds", "discovery", "installer"):
                    saved.update(dict(user_input.get(group) or {}))
                for synthetic_key in (
                    "sidebar_hub_not_installed",
                    "sidebar_installer_not_installed",
                    "shortcut_discovery_not_installed",
                    "shortcut_installer_not_installed",
                    "shortcut_snmp2mqtt_not_installed",
                    "shortcut_unifi2mqtt_not_installed",
                ):
                    saved.pop(synthetic_key, None)
                saved.pop(CONF_RESET_TO_DEFAULTS, None)
                return self.async_create_entry(data=saved)

        return self.async_show_form(
            step_id="init",
            data_schema=await self._schema(),
            errors=errors,
        )
