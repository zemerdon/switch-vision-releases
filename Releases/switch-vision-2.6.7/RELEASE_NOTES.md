# Switch Vision Core v2.6.7

Core 2.6.7 fixes a status-panel telemetry bug found by the Functional Integrity Audit. When fan or power-supply telemetry is missing, unavailable or unknown, Switch Vision now displays an unknown value (`—`) instead of synthesizing a healthy `OK` state.

Real fan and PSU entity values continue to pass through unchanged. A permanent regression protects both missing-telemetry behavior and the existing entity-candidate paths.

The same Functional Integrity Audit also found two device-support records whose Community Validated label contradicted their own still-pending live-validation fields. WS-C2960X-24TS-L and WS-C3560CG-8PC-S return to Experimental until those checks are completed. Their hardware mapping, geometry, connector and polling contracts are unchanged; this corrects support metadata rather than removing device functionality.

---

# Previous release: Switch Vision Core v2.6.6

Core 2.6.6 normalizes bundled faceplate rendering to each artwork file's real native canvas while preserving the current on-screen appearance. A permanent audit records native PNG dimensions and the exact legacy-to-native transform for every factory faceplate before migration. Legacy/custom saved profiles remain on the 2048 × 448 compatibility path unless explicitly marked as normalized.

The migration rejects negative or out-of-canvas interactive faceplate factory geometry while preserving hardware mapping, connector, PoE, polling, telemetry and support-status contracts. Native factory geometry is converted back to the legacy 2048 × 448 overlay only at render time so the visible switch layout remains unchanged.

---

# Previous release: Switch Vision Core v2.6.5

Core 2.6.5 adds the dedicated `dell-28-rj45-2sfp.png` faceplate and owner-calibrated factory presentation for the Dell N2128PX-ON. The artwork is deliberately Dell-only and is guarded so it cannot be assigned to non-Dell hardware or to Dell models above **28 RJ45 ports / 2 uplinks**. The N2128PX-ON remains **Experimental**; artwork and calibration do not promote hardware support status.

Legacy Dell submission-identifying evidence text is replaced with neutral community-hardware wording so no private contribution identifier is published. The owner-approved Dell status-panel geometry is preserved exactly. Core's factory validator now supports a narrow, explicit per-profile opt-in for rows that the existing runtime bounds safety rule intentionally suppresses; profiles without that opt-in remain strict. The release also corrects the Cisco WS-C3560CG-8PC-S Port 3 factory center to **[786, 329]** and hitbox to **[84, 76]**. Permanent regressions lock the Dell scope boundary, the Dell-only validation opt-in and the corrected 3560CG geometry.

No connector, PoE, polling, telemetry, support-status, privacy or unrelated model contracts change.

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
