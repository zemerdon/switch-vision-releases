"""Config and options flow for Switch Vision Core."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.data_entry_flow import section

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
    DEFAULT_DASHBOARD_CONFIG_PATH,
    DEFAULT_OPTIONS,
    DOMAIN,
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
        """Return the saved option or the v2.2 factory default."""
        return self.config_entry.options.get(key, DEFAULT_OPTIONS[key])

    def _schema(self) -> vol.Schema:
        """Build the grouped Switch Vision Core settings form."""
        return vol.Schema(
            {
                vol.Required("dashboard"): section(
                    vol.Schema(
                        {
                            vol.Required(
                                CONF_SHOW_PANEL_IN_SIDEBAR,
                                default=self._value(CONF_SHOW_PANEL_IN_SIDEBAR),
                            ): bool,
                            vol.Required(
                                CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR,
                                default=self._value(CONF_SHOW_LOVELACE_DASHBOARD_IN_SIDEBAR),
                            ): bool,
                            vol.Required(
                                CONF_SHOW_CALIBRATION_BUTTONS,
                                default=self._value(CONF_SHOW_CALIBRATION_BUTTONS),
                            ): bool,
                            vol.Required(
                                CONF_SHOW_DASHBOARD_HEADER,
                                default=self._value(CONF_SHOW_DASHBOARD_HEADER),
                            ): bool,
                            vol.Required(
                                CONF_SHOW_CARD_HEADERS,
                                default=self._value(CONF_SHOW_CARD_HEADERS),
                            ): bool,
                        }
                    ),
                    {"collapsed": False},
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
                    {"collapsed": False},
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
                for group in ("dashboard", "activity_leds", "discovery", "installer"):
                    saved.update(dict(user_input.get(group) or {}))
                saved.pop(CONF_RESET_TO_DEFAULTS, None)
                return self.async_create_entry(data=saved)

        return self.async_show_form(
            step_id="init",
            data_schema=self._schema(),
            errors=errors,
        )
