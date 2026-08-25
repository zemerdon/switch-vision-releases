# Switch Vision Core v2.6.5

Core 2.6.5 corrects the factory faceplate geometry for Port 3 on the Cisco WS-C3560CG-8PC-S. The owner-supplied calibrated defaults move the Port 3 center to **[786, 329]** and restore its hitbox to **[84, 76]**, preventing the undersized/misplaced selectable region from falling through to switch-level information.

All other 3560CG faceplate geometry and presentation values remain unchanged. A permanent regression now locks the corrected Port 3 position and size. No connector, PoE, polling, telemetry, support-status, privacy or unrelated model contracts change.

---

# Previous release: Switch Vision Core v2.6.4

Core 2.6.4 makes the owner-approved Hub presentation values the authoritative Core factory/reset defaults: Discovery **Dense / 12 px / Full** and Installer **Comfortable / 12 px / Wide**. Existing saved user choices remain unchanged; these values apply to new/default state and explicit Core reset-to-defaults behavior.

Core remains the single owner of these preferences. Discovery and Installer continue to consume the shared persisted `ui-preferences.json` contract rather than defining separate local defaults. The selectable 10–20 px text-size range and legacy `normal`/`small` migration remain intact. Permanent regression coverage protects all six factory values.

This is a presentation-default change only. No switch mapping, physical geometry, connector, PoE, polling, telemetry, maximum-capability, support-status or privacy contracts change.

---

# Previous release: Switch Vision Core v2.6.3

Core 2.6.3 replaces the old Discovery/Installer **Normal / Small** appearance choice with an explicit **10–20 px** body-font setting in one-pixel steps. Existing installations remain valid: `normal` is read as 16 px and `small` as 14 px until the user next saves the setting.

The Hub and Home Assistant Configure fallback use the same range, and the shared UI-preferences document now publishes the normalized numeric value for Discovery and Installer consumers. A behavioral regression exercises every accepted pixel size plus the legacy migration and invalid-value fallback.

This is an appearance-settings contract change only. No switch mapping, physical geometry, connector, PoE, polling, telemetry, maximum-capability, support-status or privacy contracts change.
