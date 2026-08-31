## v2.6.25 — Calibrated UniFi faceplates

- Bundle three owner-calibrated UniFi faceplates for 24 RJ45 + 2 optical, 24 RJ45 + 4 optical, and 4 RJ45 + 12 SFP+ layouts.
- Move the five exact registered UniFi 24+2 models from the older 24+2 artwork to the new inline calibrated default.
- Enable the exact US XG 16 4-RJ45 + 12-SFP+ dashboard visual while preserving its optical-first UniFi API port map and Detected support status.
- Keep the new UniFi 24+4 faceplate bundled and resolvable but unassigned until an exact matching UniFi topology is registered and validated.
- Preserve the historical UniFi 24+2 profile so existing stored selections continue to resolve.
- Add a permanent topology guard so the new faceplates cannot be assigned to mismatched device layouts.

## v2.6.24 — UniFi faceplate profile isolation

- Scope native UniFi calibration/faceplate profiles to the individual device as well as the controller namespace.
- Prevent two different UniFi devices on one controller from sharing the same active faceplate pointer.
- Derive only an opaque deterministic device token for calibration storage; never place the raw UniFi device ID in profile names.
- Preserve existing SNMP/custom-card switch-scoped calibration behaviour and leave UniFi telemetry/controller routing unchanged.
- Keep ambiguous legacy controller-wide faceplate selections out of automatic migration so a previous shared pointer cannot be assigned to the wrong device.
- Add permanent regression coverage using two synthetic UniFi devices on one controller.

## v2.6.23 — Custom SFP/uplink label suffix

- Add a Calibration SFP/uplink suffix field beside the existing port-label controls.
- Apply a custom suffix to default SFP/uplink display labels, or leave the suffix blank to show only the logical uplink number.
- Preserve explicit per-port display names and keep logical SFP keys, telemetry mappings, entities, numbering and geometry unchanged.
- Make newly added or duplicated SFP/uplink ports inherit the profile-level display suffix automatically.
- Preserve legacy/factory label behaviour until a suffix setting is explicitly applied to the calibration profile.
- Add permanent regression coverage for the display-only suffix contract.

## v2.6.22 — Render-space Geometry Transfer and absolute label Y

- Export Geometry schema v2 from the dashboard's fixed 2048 × 448 render-space so native/high-resolution faceplate coordinates do not leak into another switch profile.
- Transfer the complete calibrated visual presentation with Geometry v2 — ports/uplinks, labels, LED geometry, logo selection/placement, status boxes, fonts, colours and visibility — while preserving only destination faceplate/background artwork and switch/runtime identity.
- Keep Geometry schema v1 import compatibility and normalize the destination to render-space before merge; retain compatible differing RJ45/SFP visual counts.
- Make RJ45 number-label Direct Y use the actual visible coordinate while preserving the legacy odd/even render compensation for existing saved profiles.
- Report RJ45 number-label coordinates in rendered space so grouped labels aligned to one Y retain a common Direct Y readout.
- Add permanent regression coverage for Geometry v2/render-space and absolute label-Y behavior.

## v2.6.21 — Calibration selection consistency

- Preserve `Entire port` when Custom Ports resolves to SFP/uplink targets instead of translating it to SFP center.
- Select `Entire port` after Add RJ45, Add SFP or Duplicate selected, and immediately populate the matching Custom Ports value.
- Reset newly added/duplicated RJ45 number labels and SFP labels to the centre of the new port box.
- Start Assets collapsed for each new Calibration session while keeping manual section state session-local.
- Extend Odd/Even Quick Selection to SFP/uplinks for whole ports, link LEDs, activity LEDs and labels, using the logical SFP/uplink number for aliases such as `G3/TE3`.
- Keep Target and Custom Ports synchronized for individual, grouped and quick RJ45/SFP selections.
- Add permanent regression coverage for the v2.6.21 Calibration selection contract.

## v2.6.20 — Calibration SFP grouping and portable geometry import

- Add `Entire port` to individual and grouped SFP/uplink Calibration targets.
- Move an SFP/uplink port box, link/speed LED, activity LED and label by one shared delta when `Entire port` is selected, including nudge and Direct X/Y controls.
- Keep SFP/uplink subparts independently editable and keep Direct W/H / resize behavior scoped to the selected SFP hitbox, matching the existing RJ45 whole-port size contract.
- Make the All SFP quick-selection target use the same whole-port movement semantics.
- Allow Geometry Import to merge RJ45 and SFP/uplink geometry across profiles with different visual port counts: matching keys update, imported extras are added, and current entries omitted by the import are retained for explicit Port Manager cleanup.
- Keep status LED topology matching strict and preserve final profile validation, including SFP logical-key collision checks and rejection of completely portless profiles.
- Preserve Geometry Import's geometry-only boundary: artwork, asset identity, profile destination, styling and switch configuration remain owned by the current target profile.
- Add permanent regression coverage for SFP whole-port movement and cross-count geometry import.

## v2.6.19 — Calibration zero-RJ45 / optical-only profiles

- Allow Calibration Port Manager to remove the final visual RJ45 port instead of forcing one fake copper position to remain.
- Permit saved calibration profiles with zero RJ45 positions when one or more SFP/uplink positions exist, enabling genuine optical-only layouts.
- After deleting the final RJ45 port, move the editor selection to the first remaining SFP/uplink; if no visual ports remain temporarily, fall back safely to the all-elements target instead of `port:undefined`.
- Apply the same safe empty-selection fallback when the final SFP/uplink is removed.
- Preserve the guard against saving a completely portless profile: at least one RJ45 or SFP/uplink position must exist at save/import validation time.
- Keep Add RJ45 recovery from an empty copper set: numbering restarts at 1 and the existing default starter geometry is used.
- Add permanent regression coverage for final-RJ45 deletion, SFP-only profile validation and empty-selection safety.

## v2.6.18 — Calibration duplicated-port rendering

- Fix Calibration Port Manager duplicates whose logical RJ45/SFP number exceeds the live card's configured physical port count.
- While Calibration is active, render the complete editable calibration geometry so duplicated RJ45/SFP ports include the port box, link LED, activity LED and label.
- Keep normal/live dashboard rendering strictly capped by the configured/registry physical port counts; calibration-only visual capacity does not create fake live hardware.
- Preserve the current Port labels controls, per-port/SFP display-name editing, SFP key management, polling, telemetry and hardware topology contracts.
- Add permanent regression coverage locking the calibration-only count bypass for both RJ45 and SFP rendering.

## v2.6.17 — Dell and Zyxel bundled logos

- Add four bundled Dell logo PNGs: Black, Blue, Modern and White.
- Add five bundled Zyxel logo PNGs: 2019, Black, Networks, Pre 2016 and White.
- Reuse Calibration's existing folder-driven logo discovery and automatic readable filename labels; no new logo-picker code path is introduced.
- Keep custom logo files, logo placement/calibration behavior and existing default-logo handling unchanged.
- Keep switch detection, hardware mapping, geometry, polling, telemetry, PoE and support-status contracts unchanged.

## v2.6.16 — Geometry Import Faceplate Profile v2 compatibility

- Keep native `switch-vision-geometry-profile-v1` / schema 1 Geometry Import behavior unchanged.
- Accept only the explicitly recognised legacy/full `switch-vision-faceplate-profile-v2` / schema 2 format as the additional source type.
- Validate Faceplate Profile v2 input first, reduce it through the existing geometry exporter allow-list, then feed the resulting native geometry transfer through the existing validator/applicator.
- Import only image coordinate dimensions, permitted RJ45/SFP geometry, status LED positions, logo geometry, status-panel geometry/fields and calibration-button geometry/anchor.
- Preserve target management, stack/member settings, profile identity, selected faceplate/artwork source, fit/opacity, colours, fonts, visibility flags, status-panel styling and all other non-geometry configuration.
- Keep unknown transfer types, unsupported Faceplate Profile schema versions and malformed v2 profiles fail-closed.
- Add permanent Node-backed regression coverage for v2.6.8-style Faceplate Profile import, native-v1 compatibility and non-geometry isolation.

## v2.6.15 — UniFi 24-port factory geometry

- Update both bundled UniFi 24-RJ45 + 2-SFP factory profiles from the newly calibrated RJ45 port geometry.
- Correct left-LED placement on RJ45 ports 5, 6 and 7.
- Normalize all 24 RJ45 left/right LED sizes to exact 4 x 3 geometry.
- Leave SFP geometry, status LEDs, UI/status-panel settings, topology, polling, telemetry and support status unchanged.

## v2.6.14 — Multi-uplink activity binding

- Extend the clean generic `sensor.<member>_uplink_<n>_{rx,tx}_bytes` fallback from uplinks 1–2 to every logical SFP/uplink number.
- Preserve `sfp_10g` and `sfp_1g` as the preferred clean candidates and preserve existing legacy Cisco-style fallbacks.
- Restore traffic-rate and activity-LED binding for four-uplink hardware such as the HP J8693A when Discovery emits generic `uplink_3` / `uplink_4` byte counters.
- Keep negotiated-speed binding unchanged; `sfpSpeedMbps()` already accepts generic `uplink_<n>_speed_mbps/bps` telemetry for arbitrary uplink numbers.
- Add permanent Core regressions across uplinks 1–4, RX/TX directions, the shared activity/rate call chain, and the existing UniFi per-port-traffic guard.
- No physical topology, STATUS binding, polling cadence, activity timing/sensitivity/hold, PoE, support-status or factory-geometry contracts change.

## v2.6.13 — Calibration SFP port manager

- Add separate **Add RJ45** and **Add SFP** actions to Calibration's Port Manager.
- Make **Duplicate selected** preserve the selected object type, including exact-geometry SFP duplication.
- Add editable SFP/uplink keys while preserving existing legacy aliases such as `G1` and `G3/TE3`.
- Allocate newly created SFP objects with canonical `SFP<n>` keys using the next logical uplink number.
- Reject exact SFP-key duplicates and logical-number collisions such as `SFP1` + `TE1`, including profile import/save validation.
- Add permanent regression coverage for Port Manager controls, source parity, legacy key parsing and bundled calibration SFP identity uniqueness.
- No switch detection, physical mapping, polling, telemetry, PoE, support-status or factory-geometry contracts change.

## v2.6.12 — Attribution privacy and release-integrity supersession

- Supersede Core 2.6.11 as the current installable build without changing the MikroTik Experimental hardware contract.
- Keep all public contributor attribution anonymous; private evidence provenance remains separate and authoritative.
- Preserve the same Discovery 2.3.21 field-evidence baseline and pending validation boundaries.
- No hardware mapping, polling, telemetry, geometry or support-status behavior changes.

## v2.6.11 — MikroTik CRS328 Experimental registry promotion

- Add exact-model **MikroTik CRS328-24P-4S+RM** to the stable Core supported-device registry as Experimental.
- Preserve the observed RouterOS identity `CRS328-24P-4S+` while treating `CRS328-24P-4S+RM` as the marketed exact registry SKU only.
- Record the contribution-confirmed physical contract: 24 `ether` RJ45 ports plus four `sfp-sfpplus` 10G SFP+ cages; `bridge` and `lo` remain non-physical.
- Record the actual field-tested component baseline as Discovery 2.3.21; Core 2.6.11 is registry promotion, not a new hardware-validation claim.
- Preserve pending boundaries for live SFP+ behaviour, Switch Vision PoE/environment presentation and rendered alignment.
- Use the existing neutral 24-RJ45 + 4-SFP fallback visual pending MikroTik-specific alignment confirmation.
- Keep contributor attribution anonymous in public release metadata.
- Add permanent Core registry regression coverage; no new Core mapper, polling or telemetry implementation is introduced.

## v2.6.10 — Calibration faceplate selector cleanup

- Replace filename-derived Calibration faceplate dropdown text with concise, human-readable names for every bundled stock, Cisco, Dell, submarine and UniFi faceplate.
- Keep each option value and saved calibration/profile filename unchanged, so existing configurations and custom profiles remain backward compatible.
- Preserve automatic readable fallback labels for user-supplied/custom faceplate files that are not part of the bundled catalogue.
- Add permanent regression coverage for shipped labels, source-mirror parity, filename-valued options and custom-file fallback behavior.
- No switch detection, device mapping, calibration geometry, polling, telemetry, support-status or privacy contracts change.

## v2.6.9 — Community validation evidence completion

- Promote Cisco SG500X-24, Huawei S5720-12TP-LI-AC, and Huawei S5735-L8P4X-A1 from Experimental to Community Validated after the remaining applicable real-hardware checklist items were confirmed.
- Preserve all existing exact-model port counts, connector types, mapping profiles, uplink ordering, speed semantics and fallback-faceplate geometry.
- Record the field-validation baseline accurately as Core 2.6.7; Core 2.6.8 changed support metadata/contracts only and did not alter these models' runtime mapping or polling behaviour.
- Keep SG500X stack-specific operation, VLAN presentation and sustained-traffic testing separately unvalidated rather than expanding the Community Validated scope beyond the evidence.
- Add a permanent registry regression locking the three promotions while also protecting their existing physical mapping and connector contracts.
- No polling, Discovery selection, port ordering, telemetry synthesis or runtime hardware mapping behavior changes.

## v2.6.8 — Support-status evidence alignment

- Correct SG500X-24, Huawei S5720-12TP-LI-AC, and Huawei S5735-L8P4X-A1 from Community Validated back to Experimental because their complete Community Validated checklists are not yet recorded.
- Preserve the real-hardware mapping, optical-position and link/speed validation already confirmed for those exact models; unresolved sensor, PoE, stack and/or rendered-alignment checks remain pending as applicable.
- Clarify the canonical Community Validated definition so physical mapping, port selection, LEDs, link/speed, PoE, optical positions, sensors and rendered alignment must all be validated where applicable.
- Correct stale Huawei fallback-faceplate wording and record the S5735-L8P4X-A1 uplinks as four confirmed 10G SFP+ physical positions.
- Add a permanent registry regression preventing partial hardware validation from overstating support status.
- No polling, discovery selection, port ordering, telemetry synthesis or runtime hardware mapping behavior changes.

## v2.6.7 — Functional integrity fixes

- Fix the status panel so absent, unknown or unavailable fan and PSU telemetry displays `—` instead of a synthesized healthy `OK` state.
- Preserve real fan/PSU entity values and existing candidate resolution unchanged.
- Correct WS-C2960X-24TS-L and WS-C3560CG-8PC-S from Community Validated back to Experimental because their own live-validation records still contain pending/candidate checks.
- Preserve both models' existing hardware mapping, geometry, dual-personality semantics and polling behavior.
- Add permanent regressions for missing-telemetry truthfulness and these support-status evidence boundaries.

## v2.6.6 — Faceplate native-canvas normalization

- Audit every bundled factory faceplate against the PNG's real native dimensions and the legacy 2048 × 448 overlay coordinate space.
- Normalize affected factory profiles and rendering so native artwork, interactive geometry and text preserve their existing on-screen appearance without negative/out-of-canvas compensation coordinates.
- Keep legacy/custom saved calibration profiles on the existing 2048 × 448 compatibility path unless they explicitly opt into the normalized native-image coordinate space.
- Add permanent coordinate-space regressions before merge; no hardware mapping, connector, PoE, polling, telemetry or support-status contracts change.

## v2.6.5 — Dell faceplate and Cisco 3560CG factory geometry

- Add the dedicated `dell-28-rj45-2sfp.png` faceplate and owner-calibrated factory profile for the Dell N2128PX-ON while keeping the model **Experimental**.
- Keep the Dell artwork vendor-scoped: it may only be assigned to Dell models with **28 or fewer RJ45 ports** and **2 or fewer uplinks**; it is not a generic Switch Vision fallback.
- Replace legacy Dell submission-identifying evidence text with neutral community-hardware wording; no private contribution identifier is published.
- Preserve the owner-approved Dell status-panel geometry exactly. Factory validation now requires an explicit profile-level opt-in when rows are intentionally suppressed by the runtime bounds safety rule, so all other factory profiles remain strict.
- Correct the bundled `c3560cg-8pc-s.png` Port 3 factory calibration to the owner-supplied center **[786, 329]** and hitbox **[84, 76]**.
- Add permanent regressions for the Dell faceplate/vendor/topology boundary, the Dell-only status-panel opt-in, and corrected 3560CG Port 3 geometry.
- No connector, PoE, polling, telemetry, support-status, privacy or unrelated model contract changes.

## v2.6.4 — Hub presentation factory defaults

- Make the owner-approved Hub presentation values the Core factory/reset defaults: Discovery **Dense / 12 px / Full** and Installer **Comfortable / 12 px / Wide**.
- Keep Core as the single authoritative owner of these preferences so Discovery and Installer consume the same persisted `ui-preferences.json` values instead of inventing local defaults.
- Preserve the full 10–20 px selectable range, legacy text-size migration, existing saved user choices and all unrelated Core settings.
- Add permanent regression coverage for all six factory presentation defaults.
- No hardware mapping, port geometry, connector, PoE, polling, telemetry, support-status or privacy contract changes.

## v2.6.3 — Explicit 10–20 px app text sizing

- Replace the legacy Discovery/Installer **Normal / Small** text-size options with explicit **10–20 px** choices in 1 px steps.
- Preserve upgrades without invalid saved state: legacy `normal` resolves to **16 px** and legacy `small` resolves to **14 px** until the setting is next saved.
- Publish only normalized numeric font sizes to the shared `ui-preferences.json` contract consumed by Discovery and Installer.
- Validate Hub writes and the native Home Assistant Configure fallback against the same 10–20 px range.
- Add behavioral regression coverage for the complete range, legacy migration and invalid-value fallback.
- No hardware mapping, port geometry, connector, PoE, polling, telemetry, support-status or privacy contract changes.

## v2.6.2 — Geometry export strict-mode fix

- Fix **Export Geometry** in the calibration tool. The geometry-only serializer was incorrectly using the full calibration normalizer to clone primitive canvas dimensions, coordinate arrays and field maps; Home Assistant loads the card as an ES module, so strict-mode assignment to primitive values could throw before the JSON download was created.
- Use plain-data cloning for geometry-only substructures while keeping full calibration normalization only for complete calibration objects.
- Prevent geometry export/import from polluting status-panel field maps, status-LED coordinate arrays or the preserved faceplate presentation object with unrelated calibration `ui`, `stack` or `management` properties.
- Strengthen the permanent geometry-transfer regression to execute under strict-mode semantics, verify canvas/status geometry export, reject substructure pollution and prove same-profile export/import round-trip behaviour.
- No hardware mapping, port geometry values, connector, PoE, polling, telemetry, maximum-capability, support-status, Hub/Discovery/SNMP2MQTT runtime or privacy contract changes.

## v2.6.1 — Hub-managed Core settings

- Add authenticated admin WebSocket contracts for the Switch Vision Hub to read and save every normal Core option while preserving the existing Home Assistant config-entry options as the single source of truth.
- Cover sidebar/navigation, Native header visibility and shortcut order, dashboard presentation, Activity LED controls, Discovery appearance and Installer appearance in one grouped browser-safe contract.
- Validate Hub writes against the same enums/ranges and Activity LED ordering rules used by the native Configure workflow; reject unknown groups/keys and preserve unrelated saved options.
- Keep Home Assistant **Integrations → Switch Vision → Configure** available and synchronized as a fallback/recovery surface.
- Add a permanent regression covering the complete Hub/Core settings contract.
- No hardware mapping, connector, PoE, polling, telemetry, maximum-capability, support-status, Discovery/SNMP2MQTT runtime or privacy contract changes.

## v2.6.0 — Geometry-only calibration profiles

- Add separate **Export Geometry** and **Import Geometry** actions alongside the existing full faceplate-profile workflow.
- Geometry transfers copy only canvas dimensions, port/uplink/status-LED coordinates and hitbox/size data, plus positional geometry for the logo, status panels/fields and calibration button.
- Apply imported geometry onto the current destination calibration while preserving faceplate/background artwork, logo asset/source, styles, visibility, labels, stack, management and destination profile identity.
- Require exact RJ45, SFP/uplink and status-LED key-set parity before geometry can be applied, preventing geometry transfer from becoming a topology or hardware-mapping transplant.
- Add an executable permanent regression proving hand-edited foreign artwork/source identifiers cannot cross the geometry-only import boundary.
- No hardware mapping, connector, PoE, telemetry, polling, maximum-capability, support-status, Discovery/UniFi2MQTT or privacy contract changes.

## v2.5.1 — Exact-model factory UI defaults

- Fix first-load exact-model calibration resolution so cards with no persisted user profile keep the exact model factory UI defaults instead of overlaying the baked generic logo/status/button layout after factory geometry is selected.
- Preserve user-saved logo/status-panel/button placement, stack, management and faceplate choices when a real persisted calibration profile exists and exact-model geometry reconciliation is required.
- Add permanent regression coverage for the UCG Ultra and USW Ultra factory UI defaults and the persisted-profile preservation gate.
- Preserve switch mapping, port geometry, connector type, PoE, polling, telemetry, maximum-capability, support-status, Discovery/UniFi2MQTT handoff and privacy contracts.

## v2.5.0 — Maintenance Hub

- Add a first-class **Maintenance** shortcut to the Native Switch Vision dashboard header.
- Open Discovery 2.2.0's Maintenance Hub directly with `?view=maintenance`, keeping MQTT repair logic and destructive safeguards in Discovery rather than duplicating them in Core.
- Make the Maintenance shortcut installation-aware, configurable and reorderable alongside the existing Native dashboard shortcuts.
- Add a permanent Core regression covering the shortcut ID, settings option, translation parity and exact Maintenance destination.
- No switch mapping, geometry, polling, telemetry, PoE, connector, hardware capability, support-status or privacy contract changes.

## v2.4.20 — HAOS dashboard startup and calibration-v2 compatibility

- Fix the small UniFi factory calibration contract by adding explicit empty `status_leds` objects without inventing device LEDs.
- Accept calibration schema version 2 in the authenticated Core calibration validator.
- Bound Community-dashboard runtime-version lookup to one second and fall back to the versioned frontend resource when Home Assistant's WebSocket is congested during startup.
- Add permanent regressions for the v2 factory-profile contract and bounded dashboard bootstrap.
- Preserve the authoritative 2.4.19 UniFi PNG payloads/hashes, hardware mappings, PoE semantics, telemetry, privacy metadata, geometry and Experimental support status.

## v2.4.19 — Correct UniFi small-switch faceplate payloads

- Replace the incorrectly shipped small UniFi faceplate PNG payloads with the authoritative `unifi-5rj45.png` and `unifi-8rj45.png` artwork.
- Preserve the existing canonical filenames, UCG Ultra / USW Ultra model mappings, factory calibration geometry, hardware contracts and Experimental support status.
- Add permanent exact byte-size, PNG-signature and SHA-256 regressions for both authoritative faceplates.
- No polling, telemetry, API ordering, connector, PoE, maximum-speed, privacy, geometry or support-status change.

## v2.4.18 — UniFi small-device faceplates

- Add dedicated five-RJ45 and eight-RJ45 UniFi faceplates with factory calibration geometry.
- Map `UCG Ultra` to `faceplates/unifi-5rj45.png` / `default_unifi_5_rj45` and `USW Ultra` to `faceplates/unifi-8rj45.png` / `default_unifi_8_rj45`.
- Preserve the existing Experimental support status and verified UniFi API hardware contracts; rendered alignment remains pending community confirmation.
- Add permanent regression coverage for the new visual defaults, geometry, privacy-clean factory profiles and generated-registry parity.

## v2.4.17 — Default faceplate profile restoration

- Fix Calibration → Faceplate → Default / recommended so an explicit Default selection loads the independent switch base profile instead of following the currently active custom-faceplate pointer back into that faceplate.
- Add an exact-profile option to the authenticated `switch_vision/get_calibration` websocket command; normal card/profile loads keep the existing active-faceplate behaviour.
- Add a permanent regression covering the backend pointer bypass and frontend Default-selection contract.
- No switch mapping, port geometry, SNMP/UniFi polling, telemetry, LED sensitivity, support status, or device capability changes.

## v2.4.16 — UniFi support-status and privacy synchronization

- Promote `UCG Ultra`, `US 16 PoE 150W`, and `USW Ultra` from Detected to Experimental after corroborating real-hardware UniFi API evidence; keep `USW Pro Max 24` Experimental.
- Synchronize Core public support evidence with Discovery using neutral community-hardware wording and no private Support My Switch submission identifiers.
- Activate the permanent public-attribution privacy regression under the repository's direct-test CI runner and extend sanitization/regression coverage to structured public metadata keys.
- Preserve every existing port count, connector type, PoE mask, API/interface ordering, mapping profile, faceplate/calibration contract, validation field, and maximum-speed contract.
- No dashboard telemetry, port-selection, LED, SNMP, UniFi API, or other runtime behaviour changes.

## v2.4.15 — UniFi-native status telemetry

- Make the primary status panel data-source aware for UniFi API cards so it presents telemetry the Integration API actually exposes instead of defaulting to SNMP-only blank rows.
- Surface normalized management IP, memory utilization and aggregate uplink RX/TX rate in the UniFi switch summary when available.
- Derive switch-level PoE availability/activity from real UniFi port metadata and show connector type, maximum physical speed, PoE state and PoE standard in selected-port details.
- Keep temperature, VLAN/description and per-port RX/TX absent when the current UniFi API path does not expose them; no synthetic telemetry is introduced.
- Preserve existing SNMP status-panel behavior and explicit field configuration; `unifi_native_status_fields: false` restores the generic UniFi row-selection path.
- Add permanent regressions for the UniFi-native field contract, management-IP fallback, PoE presentation and preserved per-port-traffic boundary.

## v2.4.14 — UDM Pro Max and USW Pro XG 24 PoE exact contracts

- Add Experimental exact-model UniFi API support for `UDM Pro Max` using the community-validated 8 × 1G RJ45 + 1 × 2.5G RJ45 + 2 × 10G SFP+ physical contract with no PoE output.
- Add Experimental exact-model support for `USW Pro XG 24 PoE` as 8 × 2.5G RJ45 + 16 × 10G RJ45 + 2 × 25G SFP28, with 802.3bt Type 4 PoE capability reported on all 24 copper ports.
- Preserve maximum connector capability separately from negotiated link speed, including observed 10G-capable copper links at 100M/1G and 25G SFP28 links at 10G.
- Preserve the UniFi API boundary where port detail is available but per-port traffic is not; no synthetic per-port traffic is introduced.
- Reuse truthful generic socket geometry while keeping dedicated model artwork/rendered alignment validation pending.
- Keep both models Experimental until real-hardware dashboard alignment, port selection, PoE presentation and optical-position validation are completed.
- Public release metadata remains anonymous and contains no private contribution identifiers, package names, filenames or contributor identities.
- Add permanent regression coverage for exact port ordering, SFP28 capability, PoE semantics, firmware evidence, generated-registry parity and public attribution privacy.

## v2.4.13 — Port selection and native diagnostics theme fixes

- Keep rendered ports clickable when a saved/custom calibration has a port `center` but no explicit `hitbox`; derive the normal visual hitbox instead of allowing the click to fall through to switch summary.
- Preserve blank interface descriptions as a selected-port state (`DESC —`) rather than confusing missing description data with selection failure.
- Give the native dashboard Advanced diagnostics block an explicit light foreground on its fixed dark background so it remains readable under dark-text Home Assistant themes.
- Add permanent regression coverage for calibration hitbox fallback and native diagnostics contrast.
- No device mapping, telemetry, faceplate geometry, Discovery, SNMP2MQTT, or UniFi2MQTT behaviour changes.


## v2.4.12 — Catalyst 3750 48-port hardware contract

- Add Experimental exact-model handling for the community-observed `WS-C3750-48P` platform string.
- Preserve the non-G Catalyst 3750 physical contract as 48 × 10/100 FastEthernet PoE access ports plus 4 × 1G SFP uplinks; do not mislabel the copper ports as Gigabit-capable.
- Reuse the truthful 48-RJ45 + 4-SFP socket geometry while keeping live overlay/uplink/stack validation pending.
- Keep the public registry anonymous and omit private submission identifiers and filenames.
- Add permanent regression coverage for model identity, port counts, FastEthernet semantics, visual defaults, and attribution privacy.

## v2.4.11 — Public attribution privacy policy

- Remove contributor and tester identities from public changelog and release-note history unless explicitly approved by the project owner.
- Remove submission identifiers, contribution package names, and submission filenames from public release/history text and structured public contributor metadata.
- Use neutral **Community contributor** wording while preserving technical validation facts.
- Add permanent privacy regression coverage preventing non-approved public attribution from returning.
- No telemetry, device mapping, faceplate, calibration, or runtime behaviour changes.

## v2.4.10 — UniFi exact-model hardware contracts

- Add exact-model UniFi API contracts for `UCG Ultra`, `US 16 PoE 150W`, `USW Pro Max 24`, and `USW Ultra` from community-provided real-hardware validation.
- Validate `USW Pro Max 24` as 16 × 1G RJ45 + 8 × 2.5G-capable RJ45 + 2 × 10G SFP+ with no PoE, using the existing truthful UniFi 24+2 visual geometry.
- Validate `US 16 PoE 150W` as 16 × 1G PoE-capable RJ45 + 2 × 1G SFP and `USW Ultra` as eight 1G RJ45 with PoE output capability on ports 1–7 only.
- Validate `UCG Ultra` as four 1G RJ45 + one 2.5G-capable RJ45 integrated-switch ports with no PoE output, without hard-coding WAN/LAN role by physical position.
- Keep UCG Ultra, US 16 PoE 150W and USW Ultra exact visuals pending rather than claiming inaccurate small-device artwork.
- Preserve the UniFi API capability boundary: port detail is available but per-port traffic is not, so no synthetic per-port traffic data is introduced.
- Public release history intentionally omits contributor/tester identities, submission identifiers, contribution package names, and submission filenames.

## v2.4.9 — UniFi exact-model API mapping

- Add a backward-compatible explicit UniFi visual-port → API-port mapping contract while preserving the legacy sequential/offset path when no explicit map is present.
- Add exact-model support for `US 48` using the verified 48 × 1G RJ45 + 2 × 10G SFP+ + 2 × 1G SFP geometry and existing truthful 48+4 visual.
- Add detected hardware contracts for `US XG 16` (12 × 10G SFP+ followed by 4 × 10G RJ45) and `USW Pro Aggregation` (28 × 10G SFP+ + 4 × 25G SFP28) without inventing unverified dashboard faceplates.
- Keep maximum port capability separate from current negotiated speed, including 10G-capable RJ45 links negotiating at 1G and 25G-capable SFP28 links negotiating at 10G.
- Preserve community-provided validation for related UniFi and Zyxel models without publishing contributor identities or submission references.
- Add permanent regressions for explicit/legacy UniFi mappings, optical-only calibration, speed presentation, exact-model registry contracts, and preserved Zyxel defaults.

## v2.4.8 — SFP negotiated-speed status labels

- Replace the generic SFP status-panel 10G fallback with the existing live SFP speed resolver.
- Huawei S5720 1G SFP uplinks now display 1G instead of 10G when negotiated/current speed telemetry reports 1000 Mbps.
- Preserve UniFi, 10G SFP+, link-down, traffic, Activity LED, calibration, Discovery handoff, and device-mapping behaviour.
- Add permanent regression coverage preventing a hard-coded 10G SFP status fallback from returning.

## v2.4.7 — Audit hardening

- Register calibration and Switch Vision UI mutation services with Home Assistant's admin-only service helper.
- Add permanent regression coverage proving those mutation services cannot regress to ordinary service registration.
- Align Zyxel XS1930-10 visual defaults with its validated physical 8-RJ45 + 2-SFP+ layout using the compact 8+2 calibration/faceplate fallback.
- Keep exact-model visual ownership explicit and preserve device telemetry/mapping behaviour.

## v2.4.6 — UniFi dark alternative faceplate

- Add `unifi-24-rj45-2sfp-dark.png` as a manually selectable alternative UniFi faceplate.
- Use the factory calibration geometry/defaults of `unifi-24p-rj45-2sfp.png`.
- Keep the dark artwork manual-only with no exact-model mapping or default replacement.

## v2.4.5 — Native dashboard shortcut editor hotfix

- Fix Native dashboard shortcut navigation using Home Assistant's current navigation contract.
- Resolve repository-prefixed Supervisor app slugs so installed Switch Vision apps are not incorrectly shown as **Not installed**.
- Replace drag-and-drop shortcut ordering with explicit show/hide and Up/Down controls.

## v2.4.4 — Central sidebar and Native dashboard shortcuts

- Add centralized sidebar controls for the Native panel, Community dashboard, Switch Vision Hub, and Switch Vision Installer.
- Add configurable Native-dashboard shortcuts for Switch Vision management surfaces.
- Preserve telemetry, calibration geometry, Discovery generation, Activity LED behaviour, and device mappings.

## v2.4.3 — Huawei faceplate reset hotfix

- Restore Huawei S5720/S5735 neutral 24 RJ45 / 4 SFP factory visual assignments.
- Ensure reset operations return those models to the neutral stock visual instead of Cisco geometry.

## v2.4.2 — Hardware validation safeguards

- Promote real-hardware-tested exact models while preserving model-specific physical semantics.
- Align Ubiquiti exact-model visual/profile metadata with Discovery's verified API geometry assignments.
- Preserve Huawei S5720 8 RJ45 + 4 physical 1G SFP layout metadata and 1G physical-cage speed capping.
- Add permanent 2.5G display and HAOS/manual resource-version regressions.

## v2.4.1 — Registry synchronization

- Promote additional Discovery exact-model entries into the Core supported-device index without changing their support status.
- Preserve exact-model evidence, geometry, mapping profiles and visual recommendations.

## v2.4.0 — UniFi visual family

- Add the dedicated `unifi-24p-rj45-2sfp.png` UniFi / Ubiquiti faceplate and authoritative factory calibration.
- Make UniFi / Ubiquiti an explicit visual family instead of a generic stock fallback.
- Preserve existing saved/custom calibrations while refreshed defaults apply on reset.

## Earlier releases

Earlier detailed changelog entries have been consolidated from the public changelog as part of the Switch Vision public-attribution privacy policy. Public changelog and release-note text must not contain contributor/tester identities, submission identifiers, contribution package names, or submission filenames unless explicitly approved by the project owner.
