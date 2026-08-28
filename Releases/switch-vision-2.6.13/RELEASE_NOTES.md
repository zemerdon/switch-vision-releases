# Switch Vision Core v2.6.13

Core 2.6.13 adds first-class SFP/uplink object management to the Calibration Port Manager. Calibration authors can now add SFP objects directly, duplicate the selected RJ45 or SFP object without changing its type, and edit the stored SFP key used to identify each logical uplink.

New SFP objects use canonical `SFP<n>` keys while existing legacy keys such as `G1`, `TE1` and `G3/TE3` remain supported. Exact key duplicates and ambiguous logical-number aliases are rejected, so keys such as `SFP1` and `TE1` cannot silently describe the same logical uplink in one calibration profile. The same collision check is enforced when calibration profiles are imported or saved.

Permanent Core regression coverage locks the Port Manager controls, canonical/runtime card parity, legacy alias handling and bundled-profile logical-SFP uniqueness. This release changes Calibration frontend/runtime files only; it does not change switch detection, physical hardware mappings, polling, telemetry, PoE, support status or existing factory geometry.

---

# Previous release: Switch Vision Core v2.6.12

Core 2.6.12 supersedes 2.6.11 as the current installable Core build after a public-attribution privacy correction. All public contributor attribution remains anonymous; private Evidence Vault provenance is unchanged and remains authoritative.

The MikroTik CRS328-24P-4S+RM support contract remains Experimental and otherwise unchanged: the same 24 RJ45 + four SFP+ physical contract, the same Discovery 2.3.21 field-evidence baseline, and the same pending live SFP+, PoE/environment presentation and rendered-alignment checks. Discovery 2.3.22 continues to own MikroTik detection/mapping and narrow telemetry acquisition.

This release does not introduce a new Core mapper, polling path, telemetry implementation, geometry change or support-status promotion.

---

# Previous release: Switch Vision Core v2.6.11

Core 2.6.11 promotes the first MikroTik exact-model support record into the stable Core device registry: **CRS328-24P-4S+RM**, remaining **Experimental** while current-build field validation is incomplete.

Privacy-processed real-hardware evidence from Discovery 2.3.21 confirms the local RouterOS identity `CRS328-24P-4S+`, 24 physical `ether1`–`ether24` RJ45 ports, and four `sfp-sfpplus1`–`sfp-sfpplus4` SFP+ cages. The marketed `CRS328-24P-4S+RM` name is used only as the exact registry SKU. The four SFP+ cages were empty in the capture; live optical behaviour, Switch Vision PoE/environment presentation, and rendered alignment remain pending.

This is a support-metadata promotion. It does not add a new Core hardware mapper, polling path or telemetry implementation; Discovery 2.3.22 owns the MikroTik detection/mapping and narrow telemetry acquisition. Core's neutral 24-RJ45 + 4-SFP visual remains a temporary fallback. Permanent registry regression coverage locks the exact topology, Experimental boundary and field-tested Discovery version while public contributor attribution remains anonymous.

---

# Previous release: Switch Vision Core v2.6.10

Core 2.6.10 tidies the Calibration **Faceplate** selector so every bundled faceplate has a clear human-readable name instead of exposing asset filenames. Stock layouts stay vendor-neutral, while dedicated Cisco, Dell, submarine and UniFi artwork is identified directly.

This is a presentation-only change. The underlying option values remain the exact existing faceplate filenames, so saved calibration profiles, existing installs and custom asset references continue to resolve unchanged. Unknown user-supplied files still receive the existing automatic readable fallback label.

Permanent regression coverage locks the friendly-label catalogue, keeps the two shipped card-source mirrors byte-identical, proves option values remain filenames, and preserves the custom-file fallback path. No device mapping, geometry, polling, telemetry or support-status behavior changes.

---

# Previous release: Switch Vision Core v2.6.9

Core 2.6.9 promotes Cisco SG500X-24, Huawei S5720-12TP-LI-AC, and Huawei S5735-L8P4X-A1 to **Community Validated** after the remaining applicable real-hardware checks were completed. The completed evidence covers physical mapping, port selection, link/activity and speed presentation, optical positions, applicable PoE and sensor/status information, and rendered alignment.

The field confirmation was performed on Core 2.6.7 and is recorded as such. Core 2.6.8 changed these models' support metadata and validation contract only; it did not change their runtime port mapping, connector ordering, polling or speed behavior. The SG500X promotion does not expand separately unvalidated stack-specific, VLAN-presentation or sustained-traffic scope.

All existing exact-model topology and connector contracts remain unchanged, including the S5720's eight RJ45 plus four 1G SFP positions and the S5735's eight RJ45 plus four 10G SFP+ positions. Permanent regression coverage locks both the promotions and those existing physical contracts.

---

# Previous release: Switch Vision Core v2.6.8

Core 2.6.8 corrects three support-status records whose Community Validated label was stronger than their complete recorded validation evidence. Cisco SG500X-24, Huawei S5720-12TP-LI-AC, and Huawei S5735-L8P4X-A1 return to **Experimental** until the remaining applicable checklist items are completed.

This does not discard their real-hardware validation. The release preserves confirmed physical mapping, optical-position and link/speed evidence, including the S5720's corrected 1G SFP presentation and the S5735's four 10G SFP+ positions. Outstanding sensor, PoE, stack and/or rendered-alignment checks remain explicitly pending where applicable.

The canonical Community Validated definition is tightened to match the project contract, and permanent regression coverage prevents these partially validated models from being promoted again without completing the required evidence. Runtime polling, Discovery selection, port ordering and hardware mapping behavior are otherwise unchanged.

---

# Previous release: Switch Vision Core v2.6.7

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
