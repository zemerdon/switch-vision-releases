# Switch Vision Core v2.6.26

Core 2.6.26 fixes an RJ45 Calibration Port Manager regression when an entire port is duplicated or moved. The duplicated number label is already centred on the new port geometry, but the RJ45 Entire port selection and movement paths omitted that label, so subsequent nudges or Direct X/Y moves could leave the number behind while the port box and LEDs moved.

RJ45 number labels are now members of the Entire port overlay and move with the port centre and both LEDs in individual, grouped and direct-coordinate operations. SFP/uplink behaviour is unchanged because its whole-port path already carried the label correctly. Permanent regression coverage now locks the RJ45 label membership and movement contract.

---

# Previous release: Switch Vision Core v2.6.25

Core 2.6.25 adds three owner-calibrated UniFi faceplates and moves only exact matching device layouts away from their previous artwork. The five registered 24-RJ45 + 2-optical UniFi switches now use the new inline 24+2 faceplate and calibration profile. Devices with different physical port counts keep their existing fallback or dedicated visuals.

US XG 16 now has an exact 4-RJ45 + 12-SFP+ faceplate and dashboard calibration. Its authoritative optical-first UniFi API mapping remains unchanged: API ports 1-12 are the SFP+ positions and API ports 13-16 are the four RJ45 positions. Its support status remains Detected while live rendered alignment is still awaiting community confirmation.

The new 24-RJ45 + 4-optical UniFi faceplate is bundled and selectable but is deliberately not assigned as a device default until an exact matching UniFi topology is registered and validated. The historical UniFi 24+2 calibration profile remains resolvable for existing stored selections. Permanent regression coverage verifies the new geometry, labels and topology-safe assignments.

---

# Previous release: Switch Vision Core v2.6.24

Core 2.6.24 fixes native UniFi faceplate/calibration isolation when multiple devices are managed by the same controller. Previous releases derived the persistent calibration base only from the controller-scoped `selected_switch` value, so different devices could share one active faceplate pointer even though their faceplate-specific profiles were distinct.

UniFi calibration bases now retain the controller scope and add a deterministic opaque token derived from that card's `unifi_device_id`. The raw device ID is not written into the calibration profile name. This keeps UCG Fiber, USW Pro XG 8 PoE and other same-controller devices independent without changing UniFi telemetry IDs, MQTT/controller routing, or non-UniFi calibration behaviour.

Existing legacy controller-wide child profiles remain stored, but an ambiguous shared active selection is not automatically migrated to a device. This deliberately avoids assigning a previously shared faceplate to the wrong switch. A newly saved or selected faceplate is persisted under the new device-specific calibration base.

---

# Previous release: Switch Vision Core v2.6.23

Core 2.6.23 adds a display-only SFP/uplink label suffix control to Calibration. The Port labels row now includes an SFP suffix box and Apply action. Enter text such as `SFP`, `UPLINK` or `FIBRE` to render default uplink labels as the logical uplink number plus that suffix; leave the box blank and apply it to show only the number.

The setting is stored as presentation data in the calibration profile. Existing explicit per-port display names remain authoritative and are not rewritten. Logical SFP/uplink keys, telemetry mappings, Home Assistant entities, numbering and geometry are unchanged. Newly added or duplicated SFP/uplink ports have no copied custom display name, so they automatically use the configured profile suffix.

Profiles that have never applied this setting retain their existing factory/vendor label behaviour. This keeps current saved profiles backward-compatible while allowing an explicit suffix choice to override only the visible default label presentation.

---

# Previous release: Switch Vision Core v2.6.22

Core 2.6.22 fixes two Calibration portability/coordinate defects. Geometry Export now serializes the same fixed 2048 × 448 render-space consumed by the dashboard instead of leaking profile-native canvas coordinates. Geometry v2 carries the complete calibrated visual presentation — port/uplink sizing and labels, LED geometry, logo selection/placement, status boxes, fonts, colours and visibility — while preserving only the destination faceplate/background artwork and switch/runtime identity such as profile, stack and management state.

Geometry Import accepts both the new schema v2 and legacy schema v1. The destination calibration is normalized to render-space before merge, compatible differing RJ45/SFP counts remain supported, and v1 imports retain their geometry-only compatibility with a warning to re-export under 2.6.22 when full render-space presentation portability is required.

Direct Y for RJ45 number labels now means the actual visible Y coordinate. The existing odd/even row compensation remains in storage/rendering for compatibility with saved profiles, but Direct Y subtracts that compensation before storage and the coordinate readout reports rendered coordinates. Setting all RJ45 labels to Y=100 therefore renders every selected number at Y=100.

---

# Previous release: Switch Vision Core v2.6.21

Core 2.6.21 tightens Calibration selection behavior without changing hardware mappings or saved geometry contracts. Custom SFP/uplink selections now preserve `Entire port`; newly added or duplicated RJ45/SFP objects select their whole port immediately, and cloned labels start centred on the new port box rather than inheriting the source label offset.

Calibration now starts each session with Assets collapsed, while manual section expansion remains session-local. Odd/Even Quick Selection covers SFP/uplinks as well as RJ45, including whole ports, link LEDs, activity LEDs and labels; SFP parity is derived from the logical uplink number, so aliases such as `G3/TE3` are treated as uplink 3.

Selecting an individual RJ45 or SFP/uplink in the Target menu now updates the matching Custom Ports value immediately. Grouped and quick-selection targets likewise expose their resolved set, keeping Target and Custom Ports synchronized for subsequent editing.

---

# Previous release: Switch Vision Core v2.6.20

Core 2.6.20 improves Calibration portability in two places. SFP/uplink targets now expose `Entire port`, so moving a selected uplink moves its port box, link/speed LED, activity LED and label together while preserving their relative layout. Nudge and Direct X/Y use the same grouped delta; individual SFP parts remain separately editable, and Direct W/H continues to resize only the SFP hitbox.

Geometry Import no longer requires the imported RJ45 and SFP/uplink key sets to exactly equal the current calibration topology. Matching imported keys replace their geometry, additional imported ports are added, and current ports omitted from the transfer remain in place. This allows a layout such as 24 RJ45 + 4 SFP to be imported into a 24 RJ45 + 2 SFP working profile and then trimmed explicitly with Port Manager.

The relaxed port-count rule does not relax other safety boundaries. Status LED topology still has to match, the merged result still passes normal calibration validation and SFP logical-key collision checks, completely portless profiles remain invalid, and Geometry Import still cannot replace artwork, asset identity, profile destination, styling or switch configuration.

---

# Previous release: Switch Vision Core v2.6.19

Core 2.6.19 fixes the remaining Calibration Port Manager restriction that prevented removal of the final visual RJ45 port. That restriction also existed in profile validation, which meant an optical-only switch could not be represented without retaining a fake copper port.

Calibration now allows the RJ45 geometry set to become empty when SFP/uplink geometry remains. Deleting the last RJ45 automatically moves selection to the first remaining SFP/uplink, while a temporarily empty editor falls back to the safe `all` target rather than producing `port:undefined`. The matching SFP deletion fallback is hardened as well.

Saving/importing still rejects a profile containing no RJ45 and no SFP/uplink positions at all. Adding RJ45 after the copper set is empty remains supported and restarts at port 1 using the existing starter geometry. Permanent regression coverage locks these zero-RJ45 and selection-safety contracts.

---

# Previous release: Switch Vision Core v2.6.18

Core 2.6.18 fixes a Calibration Port Manager rendering defect exposed when duplicating an SFP/uplink (and equivalently an RJ45 port) beyond the live card's configured physical port count. The duplicate calibration object already contained the copied center, hitbox, label and LED geometry, but the SVG renderer applied the normal live-hardware count gate and skipped drawing the new port. That left the editable label/hitbox path visible while the actual port box, link LED and activity LED were missing.

Calibration now renders the complete editable calibration geometry regardless of the live card's physical-count cap. The bypass exists only while Calibration is active; normal dashboard rendering continues to obey `port_count` / `sfp_port_count` and therefore still reflects registry/configured physical hardware exactly. Existing Port labels controls, per-port and per-SFP Display name editing, SFP key management, telemetry and hardware mapping remain unchanged.

Permanent regression coverage locks this boundary for both RJ45 and SFP duplicates.

---

# Previous release: Switch Vision Core v2.6.17

Core 2.6.17 adds nine bundled vendor logo assets for Dell and Zyxel switches. The new transparent PNGs are shipped under `logos/` and become available automatically in Calibration's existing Logo selector alongside custom logo files.

The bundled Dell choices are Black, Blue, Modern and White. The bundled Zyxel choices are 2019, Black, Networks, Pre 2016 and White. Existing automatic filename-to-display-label handling provides readable picker names without introducing a separate hard-coded logo catalogue.

This release does not change switch detection, physical topology, calibration geometry, polling, telemetry, PoE, support status or logo placement behavior. The existing package path already copies the complete source `logos/` tree into the installable Core release.

---

# Previous release: Switch Vision Core v2.6.16

Core 2.6.16 makes Calibration → Import Geometry backward compatible with full Switch Vision Faceplate Profile v2 exports while preserving the strict geometry-only contract. Native `switch-vision-geometry-profile-v1` / schema 1 files continue through the existing path unchanged. Recognised `switch-vision-faceplate-profile-v2` / schema 2 files are first validated as Faceplate Profiles, reduced through the existing geometry exporter allow-list, and then consumed by the same geometry validator/applicator.

The compatibility adapter imports only coordinate-space dimensions, permitted RJ45/SFP geometry, status LED positions, logo box geometry, both status-panel boxes plus their field coordinates, and calibration-button box/anchor geometry. Management IP, stack/member configuration, profile identity/destination, faceplate artwork/source/fit/opacity, colours, fonts, visibility flags, status-panel styling and other non-geometry configuration remain owned by the current target profile and cannot be overwritten through Import Geometry.

Unknown transfer types remain fail-closed, unsupported Faceplate Profile schema versions are rejected, malformed Faceplate Profile v2 inputs must pass the existing calibration validator before conversion, and permanent regression coverage locks native-v1 behavior plus v2.6.8-style Faceplate Profile compatibility and non-geometry isolation.

---

# Previous release: Switch Vision Core v2.6.15

Core 2.6.15 updates the bundled factory port geometry for the light and dark UniFi 24-RJ45 + 2-SFP faceplates from newly calibrated defaults. The change is limited to RJ45 port geometry: corrected left-LED placement on ports 5, 6 and 7 and exact 4 x 3 port LED sizes across all 24 RJ45 positions.

SFP geometry, status LEDs, status panels, logo, calibration button, colours, fonts, stack/management defaults, device topology, polling, telemetry and support status are unchanged.

---

# Previous release: Switch Vision Core v2.6.14

Core 2.6.14 fixes a generic multi-uplink traffic binding gap in the dashboard runtime. Clean `sensor.<member>_uplink_<n>_rx_bytes` and `_tx_bytes` entities are now valid fallbacks for every logical SFP/uplink number instead of only uplinks 1 and 2.

This restores traffic-rate and activity-LED sampling on four-uplink hardware such as the HP J8693A when Discovery emits generic `uplink_3` and `uplink_4` byte counters. Existing `sfp_10g` and `sfp_1g` candidates remain preferred, legacy Cisco-style candidates remain available, and the UniFi per-port-traffic guard is unchanged. Negotiated-speed lookup required no fix because it already accepts generic `uplink_<n>_speed_mbps/bps` telemetry for arbitrary uplink numbers.

Permanent Core regression coverage locks generic RX/TX byte-counter binding across uplinks 1–4 and proves that both traffic-rate reporting and activity detection continue to share the same resolver. This release does not change physical topology, STATUS mapping, polling cadence, activity timing/sensitivity/hold behavior, PoE, support status or factory geometry.

---

# Previous release: Switch Vision Core v2.6.13


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
