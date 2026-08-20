# Changelog

## v2.3.14 — Test Mode control spacing

- Restores the stock Calibrate button to its original top-right position.
- Places TEST MODE 10 px below Calibrate with the same width, height and alignment.
- Corrects exact v2.3.13 stock button positions while preserving customised Calibrate placements.
- Keeps all v2.3.12 Test Mode persistence behaviour unchanged.
- Changes the Home Assistant custom integration/card files; restart Home Assistant Core after updating.

## v2.3.13 — Bottom-right Calibration controls

- Moves the stock Calibrate control to the lower-right faceplate control area so the upper-right screw/hardware remains visible.
- Displays persistent TEST MODE directly beneath Calibrate using the same 138 × 34 control size and a 4 px gap.
- Reuses the normal Calibrate control styling so the two controls read as one intentional vertical control stack.
- Automatically relocates profiles still using the previous exact stock Calibrate coordinates while preserving genuinely customised positions.
- Keeps all v2.3.12 persistent Test Mode behaviour unchanged.
- Does not change Discovery, physical-port mappings, faceplate assignments, telemetry, calibration geometry, or Activity LED tuning.
- Changes the Home Assistant custom integration/card files; restart Home Assistant Core after updating.

## v2.3.12 — Persistent Calibration LED Test Mode

- Keeps Calibration LED Test Mode active after **Done** closes and saves the calibration editor.
- Decouples Test Mode from the open calibration-controls state so forced Status, RJ45, and SFP/uplink LEDs remain visible for clean faceplate inspection.
- Adds a small **TEST MODE** indicator directly beneath the normal Calibrate button while Test Mode remains active.
- Preserves Test Mode when Calibration is reopened.
- Keeps **Cancel** as the explicit path that closes Calibration and turns Test Mode off.
- Does not change saved calibration geometry, faceplate assignments, Discovery, physical-port mappings, live telemetry, or Activity LED tuning.
- Changes the Home Assistant custom integration/card files; restart Home Assistant Core after updating.

## v2.3.11 — Calibration Profile Manager relocation

- Moves Calibration Profile management out of the Core Hub and into Switch Vision Discovery Hub v2.1.25.
- Removes the temporary Dashboard / Calibration Profiles selector from the Core Hub.
- Restores the Core Hub to its normal dashboard-focused layout.
- Retains Core ownership of calibration profile storage, WebSocket commands, save/delete services, active-profile protection, and factory-profile protection.
- Requires no calibration-profile migration, rename, deletion, or recreation.
- Preserves Calibration LED Test Mode and Refresh Faceplate introduced in v2.3.10.
- Changes the Home Assistant custom integration files; restart Home Assistant Core after updating.


## v2.3.10 — Calibration profile management and test tools

- Adds Calibration LED Test Mode, forcing Status, RJ45, and SFP/uplink LEDs visibly on while Calibration is open without changing live state, saved calibration, or dirty state.
- Adds a first-class Calibration Profiles manager to the Switch Vision Hub.
- Shows profile scope, active/unused state, model, RJ45/SFP counts, faceplate identity, stale/missing-faceplate state, and SHA-256 faceplate fingerprints.
- Detects identical faceplate image content stored under different filenames without automatically merging or deleting profiles.
- Protects active and factory calibration profiles from deletion in both the Hub UI and backend service.
- Adds multi-select deletion, Select Stale, and Clean Stale Profiles with explicit confirmation and protected-profile filtering.
- Adds Copy Profile between compatible profiles while preserving the destination faceplate identity and active-profile pointer.
- Adds Export Profile and destination-driven Import Into Profile using the Switch Vision faceplate-profile transfer format.
- Import preserves destination faceplate, profile identity, management data, and stack data, and rejects unsafe factory/stale destinations and model mismatches.
- Adds Refresh Faceplate in Calibration to bypass browser image caching for an overwritten faceplate file without changing the filename or creating a new calibration profile.
- Keeps the canonical card source and Home Assistant card copy byte-identical.
- Does not change Discovery, physical-port mappings, or existing saved-profile keys.

## v2.3.9 — Quick Selection populates Custom Ports

- RJ45 Calibration Quick Selection now populates the Custom Ports field with the exact resolved visual-port set.
- Applies to All RJ45, RJ45 Link/Activity, and Odd/Even port, LED, and number selections.
- Uses only RJ45 ports that actually exist in the active calibration profile.
- Keeps the original Quick Selection target active while making the resolved list visible and editable.
- Non-RJ45 Quick Selections leave Custom Ports unchanged.
- Does not change port mappings, Discovery, faceplate assignments, or saved-profile compatibility.

## v2.3.8 — Streamlined calibration colour controls

- Removes the redundant preset colour dropdowns from Status Box 1 and Status Box 2 in Calibration.
- Keeps the existing colour-picker controls for text, box/background, and border colours.
- Preserves the existing calibration property names, saved-profile values, factory defaults, and reset behaviour.
- Leaves all non-colour Calibration dropdowns unchanged.
- Does not change Discovery, physical-port mappings, faceplate selection, or Activity LED behaviour.


## v2.3.7 — Accurate multi-gigabit speed labels

- Corrects the generic human-readable port-speed formatter so 2.5 Gbit/s links display as `2.5G` instead of being rounded to `3G`.
- Preserves meaningful standard Ethernet rates including 10M, 100M, 1G, 2.5G, 5G, 10G, 25G, 40G, and 100G.
- Keeps link-speed presentation separate from the numeric speed values used for activity and utilisation calculations.
- Applies the correction generically rather than using a Dell- or vendor-specific display workaround.
- Does not change physical-port mappings, Discovery classification, faceplate selection, or calibration data.

## v2.3.6 — Neutral stock visual profiles

- Adds neutral factory calibration profiles for the four bundled stock faceplate families:
  - `stock_24rj45_2sfp`
  - `stock_24rj45_4sfp`
  - `stock_48rj45_2sfp`
  - `stock_48rj45_4sfp`
- Uses the stock 24-port family for devices with 24 or fewer RJ45 ports and the stock 48-port family for devices with more than 24 RJ45 ports when a dedicated model-specific profile is not available.
- Uses the two-SFP stock variant for devices with up to two uplinks and the four-SFP stock variant for devices with three or four uplinks.
- Corrects fallback visual selection for SG500X-24, Huawei S5720/S5735, Zyxel XS1930-10, and generic-fallback UniFi models.
- Reserves the dedicated `cisco_3560cg_8pc` calibration and `c3560cg-8pc-s.png` faceplate exclusively for the exact `WS-C3560CG-8PC-S` model.
- Preserves existing model-specific Cisco Catalyst and validated Juniper EX3300 visual profiles.
- Adds build-time regression checks for stock-profile policy and dedicated 3560CG visual isolation.
- Does not change discovered physical port counts or vendor-specific physical-port mappings.

### Important upgrade note

Existing saved calibration profiles are preserved during upgrade and are not silently overwritten.

If an affected switch continues to display its previous fallback faceplate or geometry after updating to v2.3.6:

1. Open **Switch Vision Calibration** for that switch.
2. Select **Reset Current Switch**.
3. Confirm the reset.

**Reset Current Switch removes the saved faceplate-specific calibration for that switch and replaces it with the current recommended factory visual and calibration profile. The replacement is saved automatically.**

This also replaces any custom calibration positions, sizing, faceplate selection, or other saved calibration adjustments for that switch. Note any custom adjustments you want to recreate before resetting.

New switches, and switches without a saved calibration profile, use the corrected factory visual automatically.

## v2.3.5 — Calibration selection highlight correctness

- Refactors the yellow Calibration selection overlay to use the same canonical editable target as movement, positioning, and sizing operations.
- Corrects RJ45 Port box, Entire Port, Link, Activity, and Number highlighting.
- Corrects grouped All, Odd, Even, and Custom RJ45 highlight behaviour.
- Adds yellow calibration rings for RJ45 number targets.
- Corrects combined Port Numbers highlighting across RJ45 numbers and SFP/uplink labels.
- Keeps SFP/uplink centre, link, activity, and label highlighting part-aware.
- Keeps Status Box 1 and Status Box 2 field highlighting aligned with All fields, All labels, and All values selections.
- Preserves positional calibration outlines for selected hidden UI objects.
- Adds whole-box Visible controls for Status Box 1 and Status Box 2.
- Preserves saved Status Box 1 visibility instead of allowing the card default to overwrite it.
- Does not change the underlying calibration selection, movement, sizing, or saved target identity semantics.

## v2.3.4 — Status field group quick selection

- Adds **All labels** and **All values** quick-selection controls for Status Box 1.
- Adds **All labels** and **All values** quick-selection controls for Status Box 2.
- Keeps each Status Box group together with Box and All fields controls.
- Moves Logo and Calibration button back to the general Quick select row.
- Group label operations affect only `row*_key` coordinates.
- Group value operations affect only `row*_value` coordinates.
- Existing All fields operations continue to affect the complete Status Box field set.
- Group-aware nudge, direct X/Y positioning, overlay highlighting, and reset handling are included.
- Preserves existing calibration profile data and stable field identities.

## v2.3.3 — Calibration Selection layout cleanup

- Moves **RJ45 key** and **Renumber** onto a dedicated row beneath the main Target / Port manager controls.
- Moves **Display name**, **Set name**, and **Reset name** onto that same dedicated row.
- Keeps **Remove port** with the main Port manager controls.
- Moves **Logo** and **Calibration button** quick-selection actions to immediately follow the Even-port controls.
- Reduces unnecessary wrapping and horizontal scrolling in the Calibration Selection workspace.
- Preserves all v2.3.2 calibration behaviour, port identity, telemetry mappings, logo assets, and profile data unchanged.

## v2.3.2 — UniFi logo refresh

- Refreshes the bundled `unifi-2005.png` artwork.
- Refreshes the bundled `unifi-2013.png` artwork.
- Removes the obsolete `unifi-2023.png` raster asset.
- Retains `unifi-2023.svg` as the current vector UniFi artwork.
- Keeps the existing `ubiquiti-networks.png` asset unchanged.
- Preserves all Core v2.3.1 calibration flexibility behaviour unchanged.

## v2.3.1 — Calibration flexibility update

- Reorders the interactive calibration workspace so **Assets** appears first and opens by default, **Selection** starts collapsed, and **Position & Size** remains open for faster faceplate work.
- Makes **Reset section layout** restore the new default section order and expanded/collapsed state.
- Extends **Custom ports** selection to SFP/SFP+ uplinks using case-insensitive aliases such as `g1`, `te2`, `sfp1`, and `uplink2`, while retaining numeric RJ45 lists and ranges.
- Adds selected-SFP group operations so position, size, labels, link LEDs, and activity LEDs can be calibrated on an arbitrary subset of uplinks instead of only all uplinks.
- Adds optional per-port display-name overrides for both RJ45 and SFP/uplink ports without changing the underlying port key, entity mapping, or telemetry identity.
- Adds **Set name** and **Reset name** actions and exposes saved display names in the calibration target selector and overlay.
- Adds a shared **Normal / Bold** presentation control for all RJ45 and SFP/uplink labels.
- Adds independent RJ45 and SFP/uplink label font sizing with a maximum of **50 px**.
- Extends Status LED and Status Box font-size calibration controls to **50 px**.
- Keeps existing default geometry, colours, telemetry behaviour, profile storage, Discovery integration, Activity LED 2.0 behaviour, and switch mappings unchanged.

## v2.3.0 — UniFi presentation baseline

- Establishes the Switch Vision Core v2.3 release line for expanded UniFi presentation work.
- Adds bundled UniFi and Ubiquiti logo assets for model-specific presentation and calibration use.
- Normalizes Cisco logo filenames to the consistent `cisco-<variant>` naming scheme.
- Migrates existing bundled Cisco logo references to the normalized asset names.
- Preserves existing Discovery, SNMP2MQTT, entity, calibration, faceplate, dashboard, Activity LED 2.0, and C3650 Status Box behaviour.


## v2.2.2 — C3650 Status Box emergency hotfix

- Corrects stale Cisco 3650 factory Status Box value-column coordinates that caused MODEL, IP, CPU, TEMP, and POE rows to be clipped after a factory reset.
- Corrects the same stale value-column offsets in the legacy C3650 profile and Status Box 2 factory coordinates.
- Adds build-time bounds validation across every bundled calibration and faceplate profile so enabled factory status rows cannot ship outside their calibrated panel.
- Carries forward all Core v2.2.1 hardening and Activity LED 2.0 behaviour unchanged.

## v2.2.1 — Core hardening hotfix

- Removes environment-specific management and stack state from the bundled Cisco 3650 factory calibration.
- Regenerates and validates the primary frontend C3650 factory calibration from the authoritative JSON profile so factory state cannot drift into the card bundle.
- Adds build-time factory-calibration privacy validation for management addresses, hostnames, credentials, instance identifiers, and site-specific stack members.
- Requires an explicit `-v/--version` for every Core build; implicit patch increments and `--bump` release builds are no longer allowed.
- Keeps independently-versioned Discovery examples unversioned instead of relabelling them with the Core release number.
- Corrects live-dashboard example text so it matches the enabled Calibration-button setting.
- Clarifies that Core, Discovery, Installer, SNMP2MQTT, and UniFi2MQTT advance on independent version lines.
- Adds a 4 MiB safety cap before the native dashboard reads/parses generated dashboard YAML.
- Carries forward Activity LED 2.0 behaviour from v2.2.0 unchanged.

## v2.2.0 — Activity LED 2.0

- Promotes switch-port activity animation to a first-class Switch Vision Core setting instead of relying on hard-coded tuning.
- Keeps the existing RX + TX throughput calculation relative to negotiated link speed, but replaces the old 1% / 20% activity bands with configurable sensitivity presets and Custom thresholds.
- Adds **Low**, **Normal**, **High**, and **Custom** Activity LED sensitivity modes. Normal defaults to Medium at 0.10% link utilisation and Fast at 1.00%.
- Changes the default blink periods to 500 ms Slow, 250 ms Medium, and 120 ms Fast so normal network activity remains visibly alive.
- Adds configurable activity hold and threshold hysteresis; hysteresis reduces Slow/Medium/Fast band chatter near utilisation boundaries.
- Makes Activity LED settings integration-wide for Native, Community-strategy, and custom Switch Vision cards while preserving card/YAML values as the fallback if global settings are unavailable.
- Groups Switch Vision Core Options into Dashboard, Activity LEDs, Switch Vision Discovery, and Switch Vision Installer sections.
- Adds **Reset all Switch Vision Core settings to defaults** to the Options flow.
- Publishes Activity LED settings through the existing Switch Vision UI-settings websocket/event path and shared UI-preferences document for supported management interfaces.

## v2.1.5 — Zyxel XS1930-10 exact-model entry

- Adds an Experimental exact-model registry entry for **Zyxel XS1930-10** from the sanitized community Support My Switch evidence set.
- Adds card-side exact-model recognition for `XS1930-10` text so model-aware visual defaults can resolve when the model string is exposed.
- Uses the existing compact **8 RJ45 + 2 SFP** visual/profile as the closest temporary fallback until a Zyxel-specific faceplate is supplied.
- Aligns with Switch Vision Discovery v2.1.7, which adds the corresponding exact-model discovery, port mapping, PVID, traffic, CPU, memory, fan, and temperature support.
- Keeps the Zyxel model **Experimental** until the contributor completes post-update live validation on the real switch.

## v2.1.4 — Faceplate calibration isolation

- Stops faceplate-specific saves from mirroring the entire calibration into the base switch profile.
- Keeps Status Box, layout, and faceplate-specific calibration data independent between faceplates.
- Stores the active faceplate selection separately without copying calibration content.
- Prevents a new or unsaved faceplate from inheriting the previously active faceplate layout.
- Adds migration handling for older mirrored faceplate state and regression coverage for profile isolation.
- Carries forward the v2.1.3 removal of obsolete Status Box fields `MEM`, `UP RX`, and `UP TX`.

## v2.1.3 — Status Box field cleanup

- Removes the unused `MEM`, `UP RX`, and `UP TX` rows from the configurable switch Status Box field list.
- Keeps normal port/SFP `RX` and `TX` rows unchanged.
- Preserves existing memory and uplink RX/TX telemetry plumbing for future/non-Status-Box use.
- Adds a build-time regression guard preventing the retired rows from returning to the Status Box selector.

## v2.1.2 — Repository-managed package cleanup

- Removes bundled Switch Vision Discovery and UniFi2MQTT local-app source trees from the main Switch Vision release and private source package.
- Keeps Discovery, SNMP2MQTT, and optional UniFi2MQTT independently versioned and managed through the Switch Vision Installer.
- Removes main-build version propagation, hardening checks, self-tests, and registry synchronization that belonged to the separate Discovery/UniFi repositories.
- Retains main-owned UniFi card/backend validation for normalized `/share/switch_vision/unifi/devices.json` consumption and dynamic port geometry.
- Updates installation, upgrade, requirements, troubleshooting, and build documentation for the Installer-only repository architecture.
- Replaces public Home Assistant documentation/issue links that pointed at the private main source repository.
- Adds archive validation that fails if `local_apps/` source is reintroduced into the main release or private source ZIP.
- Separates the publishable release SHA-256 file from the private checksum ledger so private source archive metadata is not exposed in public release assets.

## v2.1.1

- Keeps the UniFi2MQTT Settings card visible in Switch Vision Hub by default.
- Greys out the UniFi2MQTT card when the app is not installed and explains why in a hover tooltip.
- Uses an amber needs-setup state when UniFi2MQTT is installed but controller/API configuration is incomplete.
- Uses an amber warning state when UniFi2MQTT is configured but not running.
- Adds a live `Show UniFi2MQTT integration` option under Settings → Integrations → Switch Vision; disabling it removes the UniFi section from the Hub.
- Preserves the v2.1.0 Hub-owned UniFi configuration flow and Installer-owned install/recovery split.


## v2.1.0 — UniFi Hub integration public baseline

- Promotes the Switch Vision Hub UniFi2MQTT management path as the public 2.1 baseline.
- Adds a dedicated **UniFi2MQTT Settings** page in Switch Vision Hub for controller URL, Site ID, API key, SSL verification, polling interval, MQTT connection details, and MQTT topic prefixes.
- Preserves stored API keys and MQTT passwords without reading secret values back into the browser; blank secret fields keep the existing saved value.
- Lets the Hub install UniFi2MQTT when it is available but not yet installed, then save configuration and start or restart the app through Home Assistant Supervisor.
- Shows UniFi2MQTT installation/runtime state, controller configuration readiness, snapshot availability, and normalized device count in the Hub.
- Integrates normalized UniFi devices into the existing Devices and Diagnostics views and keeps UniFi Support My Switch data privacy-processed.
- Keeps SNMP/SNMP2MQTT support unchanged and keeps UniFi support optional.
- Establishes the Switch Vision Installer as the single repository end users need to add manually; UniFi2MQTT configuration belongs in Switch Vision Hub rather than the Installer.
- Carries forward all v2.0.36 sidebar live-update and stability fixes.

## v2.0.36 — Sidebar live-update fix

- Fixes the Switch Vision Installer ingress/sidebar icon disappearing when both Native and Lovelace Switch Vision sidebar entries are hidden.
- Replaces presentation-option full integration reloads with Home Assistant config-entry update listeners.
- Updates Native and Lovelace sidebar visibility in-place without removing/re-registering the Native panel.
- Keeps unrelated Home Assistant ingress/sidebar entries untouched while Switch Vision presentation options change.
- Adds build-time regression guards preventing presentation options from returning to full-reload behavior.

## v2.0.35 — Management theme simplification

- Simplifies the Hub theme selector to four focused choices: Switch Vision, Cisco Classic, Cisco Nexus, and UniFi.
- Removes the Light, Cisco Catalyst, and System themes.
- Removes the Hub compact/density button; Discovery UI Density remains controlled by the existing Switch Vision integration setting.
- Keeps all theme styling isolated from Native, Lovelace, and Custom dashboards and switch-card rendering.
- Hardens generated SNMP2MQTT YAML validation against empty/malformed targets and sensors.
- Preserves the previous UniFi device snapshot entry when a single device detail/statistics refresh fails transiently.

## v2.0.34 — SNMP retirement / UniFi-only discovery fix

- Stops Discovery from silently reusing historical SNMP walks when the current run did not create them; stored walks are now parsed only with explicit `parse_all_walks`.
- Rebuilds the SNMP capability cache from the current source set so removed SNMP devices do not linger in Devices/Diagnostics.
- Decouples dashboard-card generation from SNMP2MQTT generation so UniFi API-only runs generate fresh cards with zero SNMP inputs.
- Removes stale generated SNMP2MQTT YAML when a run has no active SNMP source and stops the generated-YAML SNMP2MQTT bridge when that file is retired by Discovery.
- Adds **Reset SNMP Discovery Data** in the Hub to stop SNMP2MQTT, retire identifiable retained Home Assistant MQTT Discovery entries, clear saved SNMP walks/capabilities/generated SNMP files, and preserve UniFi data/settings.
- Records exact generated SNMP2MQTT discovery topics (no credentials) so full or partial SNMP retirement can remove stale Home Assistant entities even after the active YAML is replaced/removed.
- Adds regression/self-test coverage for SNMP2MQTT retirement topic generation and UniFi-only source isolation.

## v2.0.33 — Management UI themes

- Adds a top-right management UI theme selector to Switch Vision Hub and all Discovery views.
- Adds seven choices: Switch Vision, Light, Cisco Classic, Cisco Catalyst, Cisco Nexus, UniFi, and System.
- Keeps the existing Switch Vision appearance as the default and stores theme choice per browser.
- Adds a top-right density icon tied to the existing Discovery UI Density preference.
- Lets the density icon toggle Comfortable/Compact while keeping the normal integration setting authoritative.
- Automatically reflects Compact/Dense state when Discovery UI Density changes elsewhere.
- Adds shared colour variables so Hub, Devices, Diagnostics, Support My Switch, Configuration, and UniFi2MQTT Settings change consistently.
- Keeps Native, Lovelace, Custom Switch Vision, switch cards, faceplates, ports, LEDs, and Calibration visuals completely outside the theme system.
- Adds build-time regression checks preventing management-theme code from leaking into dashboard runtimes.

## v2.0.32 — Support-path polish

- Honors an explicit `sfp_port_count: 0`, so universal fallback visuals do not draw fake SFP ports on copper-only switches.
- Uses live SFP negotiated speed for link-speed colour, including Huawei 1G SFP fallbacks and UniFi API SFP ports.

- Marks first-time UniFi Site ID/API key values as mandatory in the Home Assistant App schema.
- Starts UniFi2MQTT after a successful Hub save when the app is stopped; running instances are restarted.

- Requires a non-empty UniFi site ID and a first-time API key before Hub save/restart.
- Keeps blank secret fields as preserve-on-update and documents the Home Assistant App fallback for clearing an optional MQTT password.
- Removes stale registry/documentation statements that contradicted current UniFi card generation and fallback visuals.

- Adds UniFi2MQTT configuration, status, and install handling to Switch Vision Hub.
- Preserves UniFi API/MQTT secrets without exposing existing values to the Hub browser.
- Uses the generic 48-RJ45 + 4-SFP visual as the universal temporary UniFi fallback.
- Enables generated cards for the remaining registered UniFi geometries, including USW Lite 16 PoE and UDM Pro.
- Synchronizes manual SNMP model overrides with the authoritative registry and adds regression checks.
- Updates stale UniFi/integration documentation.
- No unrelated feature additions.

## v2.0.31 — Huawei SNMP compatibility

- Adds `ifDescr` fallback for switches that omit IF-MIB `ifName`.
- Adds Experimental `S5720-12TP-LI-AC` 8-RJ45 + 4-SFP mapping support.
- Adds walk-aware 32-bit traffic-counter and `ifSpeed` fallbacks.
- Adds 1G SFP entity-name support to the card.
- Uses the generic 48-RJ45 + 4-SFP visual as the temporary Huawei fallback.
- Normalizes CR/trailing whitespace in SNMP identity values.
- Support/compatibility only; no new product features.

## v2.0.30 — UniFi contribution/privacy audit hardening

- Masks UniFi card IDs/names in Support My Switch dashboard YAML.
- Adds residual checks for leaked UniFi dashboard identity fields.
- Includes sanitized UniFi devices in contribution summaries and fingerprints.
- Makes diagnostics source-aware for UniFi API devices.
- Cleans up outdated generated-dashboard visual wording.
- No live card rendering or SNMP behavior changes.

## v2.0.29 — UniFi Discovery/card integration

- Imports normalized UniFi2MQTT devices into Discovery and generated dashboard cards.
- Adds live authenticated UniFi card data through the Switch Vision integration.
- Drives link/speed/PoE/system data from the UniFi snapshot while keeping per-port traffic disabled when unavailable.
- Keeps devices with missing generic visual profiles visible but does not generate incorrect cards for them.
- Existing SNMP/SNMP2MQTT paths remain unchanged.

## v2.0.28 — UDM Pro + live UniFi validation

- Adds Experimental `UDM Pro` gateway/switch-hybrid registry/profile support.
- Records live UniFi2MQTT validation for the existing UniFi switch models.
- Adds API model-pattern variants for `USW Enterprise 8 PoE` and `USW Pro 24 PoE`.
- Suppresses nominal/stale `speedMbps` values when a UniFi port is DOWN.
- Keeps PoE state independent from Ethernet link state.
- No SNMP2MQTT, card, calibration, polling, or sidebar behavior changes.

## v2.0.27 — Independent sidebar controls

- Adds separate sidebar visibility controls for the automatic Native panel and the Lovelace/Community dashboard.
- Identifies Switch Vision Lovelace dashboards by strategy, so renaming them is safe.
- Applies the saved Lovelace preference to dashboards created after setup.
- No Discovery, SNMP2MQTT, UniFi2MQTT, card, calibration, polling, or registry changes.

## v2.0.26 — Sidebar visibility hotfix

- Fixes hiding of the original automatic Native Switch Vision panel.
- Uses Home Assistant's actual `show_in_sidebar` panel flag.
- Clarifies that the integration option controls only the automatic/native panel.
- User-created Switch Vision dashboards retain their own Home Assistant sidebar setting.
- No runtime data, Discovery, SNMP2MQTT, UniFi2MQTT, calibration, card, or registry changes.

## v2.0.25 — Dashboard strategy resource hotfix

- Registers the Switch Vision Community dashboard strategy as a Lovelace `module` resource, matching Home Assistant's required custom-strategy loading path.
- Automatically updates the versioned strategy resource and removes duplicate stale entries in Lovelace storage mode.
- Retains the existing Native panel and Custom dashboard fallback unchanged.
- No device registry, Discovery, SNMP2MQTT, UniFi2MQTT, polling, calibration, or card behavior changes.

## v2.0.24 — Native dashboard strategy hotfix

- Fixes Home Assistant timing out while loading the Switch Vision Community dashboard strategy.
- Registers current and legacy strategy tags and makes duplicate resource evaluation safe.
- Adds build-time regression coverage for dashboard strategy registration.
- No runtime switch-data paths changed.

## v2.0.23 — Home Assistant dashboard strategy

- Registers Switch Vision in Home Assistant 2026.5+ Community dashboards.
- Adds a real Lovelace dashboard path that can be selected as the Home Assistant default dashboard.
- Reuses the existing Native Switch Vision renderer/polling path instead of duplicating card-generation logic.
- Retains the current custom sidebar panel and generated YAML dashboard as independent fallbacks.
- Adds a versioned panel alias for safe frontend upgrades in long-lived browser sessions.
- Adds build-time version validation for the dashboard strategy resource.
- No Discovery, SNMP2MQTT, UniFi2MQTT, calibration, registry, or existing card behavior changes.

## v2.0.22 — Audit / stability

- Audits the complete v2.0.21 package and fixes issues without broad architectural changes.
- Fixes UniFi2MQTT Paho 1.x/2.x constructor compatibility.
- Flushes queued retained MQTT publications before UniFi2MQTT disconnect.
- Adds UniFi2MQTT build-time version propagation, hardening validation, and offline self-test coverage.
- Marks UniFi automatic dashboard support as pending while preserving Experimental exact-model/API telemetry support.
- Adds authoritative Discovery/SNMP2MQTT parser support for Cisco `SG500X-24` 24 RJ45 + 4 10G interface names.
- Completes Huawei `S5735-L8P4X-A1` 8 RJ45 + 4 XGigabitEthernet uplink generation with correct Huawei metadata.
- Adds SG500X capability-classifier regression coverage.
- Aligns Discovery import validation with shipped SG500X/S5735 model overrides.
- Masks UniFi snapshot device names and stable IDs in Support My Switch contribution bundles.
- Adds experimental UniFi2MQTT setup/limitations documentation.
- No existing Confirmed support status is changed.

## v2.0.21 — Huawei S5735-L8P4X-A1 contribution

- Adds Experimental exact-model registry entry for `S5735-L8P4X-A1` from `SV-2026-000010`.
- Adds profile `huawei-s5735-l8p4x-a1`.
- Maps `GigabitEthernet0/0/1-8` as eight copper ports.
- Maps `XGigabitEthernet0/0/1-4` as four high-speed uplink candidates.
- Classifies Huawei `XGigabitEthernet` interfaces as physical `sfp_plus` interfaces.
- Adds a Huawei interface-classification regression test.
- Leaves PoE telemetry, sensors and final visual validation pending.

## v2.0.20 — First UniFi Integration API bridge

- Adds experimental `local_apps/switch_vision_unifi2mqtt`.
- Uses read-only UniFi Integration API `X-API-KEY` authentication.
- Publishes MQTT Discovery/state for model, online state, port state/speed/connector/PoE, CPU, memory, uptime and uplink rates.
- Writes normalized `/share/switch_vision/unifi/devices.json`.
- Adds Experimental registry entries for `USW Pro XG 8 PoE` and `USW Lite 16 PoE`.
- Validates normalization against supplied sanitized live API samples.
- Leaves SNMP2MQTT unchanged and retains SNMP for per-port RX/TX.

## v2.0.19 — Ubiquiti contribution registry expansion

- Adds Experimental exact-model entry for `USW-Enterprise-8-PoE` from contribution SV-2026-000013.
- Adds candidate mapping for `tw1`-`tw8` and `te1`-`te2`.
- Adds Experimental exact-model entry for `USW-Pro-24-PoE`.
- Adds candidate mapping for `0/1`-`0/24` plus candidate uplinks `0/25`-`0/26`.
- Extends the Ubiquiti vendor identity pack to recognize `USW-` and `UniFi Switch` sysDescr strings.
- Improves exact-model lookup for descriptive firmware suffixes such as commas after the exact SKU.
- Leaves UDM-Pro and generic Linux-based UniFi devices unregistered as switch profiles pending stronger evidence.
- No existing supported-device status is promoted or changed.

## v2.0.18 — Contribution registry expansion

- Adds Experimental exact-model registry entry for Cisco `SG500X-24` from contribution SV-2026-000006.
- Adds candidate SG500X profile for `gi1/1`–`gi1/24` and `te1/1`–`te1/4`.
- Adds Experimental exact-model registry entry for Huawei `S5720-12TP-LI-AC` from contribution SV-2026-000006.
- Records Huawei `GigabitEthernet0/0/1`–`GigabitEthernet0/0/12` interface evidence while leaving media/uplink classification pending.
- Improves exact-model registry lookup for verbose vendor sysDescr strings.
- No existing supported-device status is promoted or changed.

## v2.0.17 — GitHub Sponsors UI placement update

- Removes the Sponsors link from Support My Switch.
- Adds a compact Sponsor chip with heart icon to the Switch Vision Hub page.
- No Discovery runtime, generated YAML, polling, activity LED, card, calibration, or installer behaviour changes.

## v2.0.16 — GitHub Sponsors link fix

- Fixes the Support My Switch Sponsors link being emitted as the literal `{GITHUB_SPONSORS_URL}` placeholder.
- Uses the official absolute Sponsors URL directly so Home Assistant Ingress does not treat it as a local path.
- No runtime Discovery, generated-output, polling, activity LED, card, calibration, or installer changes.

## v2.0.15 — GitHub Sponsors integration

- Adds `.github/FUNDING.yml` for the `zemerdon` GitHub Sponsors profile.
- Adds a short Support the project section to README.
- Adds a discreet GitHub Sponsors link to Support My Switch.
- No Discovery runtime, generated YAML, polling, activity LED, card, calibration, or installer behaviour changes.

## v2.0.14 — Generated YAML section style alignment

- Makes Generated Card YAML and Generated SNMP2MQTT YAML use the same rounded boxed container style.
- Aligns border, padding, background, spacing, summary width, and right-side chevrons.
- Presentation-only change; no Discovery runtime or generated-output changes.

## v2.0.13 — Generated YAML arrow alignment

- Aligns the collapse/expand arrows for Generated Card YAML and Generated SNMP2MQTT YAML.
- Normalizes summary-row width and box sizing so both right-side chevrons share the same effective right edge.
- Presentation-only change; no Discovery runtime or generated-output changes.

## v2.0.12 — Utilization-based activity LEDs

- Changes port activity classification from raw byte-delta logarithmic scaling to real port-utilization bands.
- Slow activity is below 1% utilization.
- Medium activity is 1% to below 20% utilization.
- Fast activity is 20% utilization and above.
- Retains the 750 ms / 350 ms / 180 ms slow/medium/fast blink periods.
- Uses measured sample timing and port speed for activity classification.
- Uses the existing 10 Gb/s ceiling for SFP activity.
- Reduces generated `activity_hold_seconds` from 30 seconds to 12 seconds for the 10-second traffic polling cadence.
- No Discovery switch detection, generated sensor naming, calibration, or installer behaviour changes.

## v2.0.11 — Generated YAML header polish

- Moves the collapse/expand arrows for Generated Card YAML and Generated SNMP2MQTT YAML to the far right of each section header.
- Keeps section collapse/expand behaviour unchanged.
- No Discovery runtime, generated YAML, SNMP polling, card, calibration, or installer logic changes.

## v2.0.10 — Polling cadence and editor cleanup

- Changes generated RX/TX traffic polling from 30 seconds to 10 seconds.
- Changes generated link/status polling to 30 seconds.
- Keeps VLAN/trunk polling at 30 seconds.
- Keeps slow system/interface polling at 300 seconds.
- Removes the temporary nested-editor Save reminder from Add/Edit Switch and Add/Edit Stack Member.
- Retains the v2.0.7 Stop Discovery control, v2.0.6 traffic-rate sanity guard, and v2.0.5 fresh-install Discovery defaults.

## v2.0.9 — Discovery editor Save reminder spacing

- Separates the two-step Save reminder from the final field help text with a blank line.
- Applies the same presentation to Add/Edit Switch and Add/Edit Stack Member.
- No Discovery runtime or generated-output behaviour is changed.
- Retains the v2.0.7 Stop Discovery control, v2.0.6 traffic-rate sanity guard, and v2.0.5 fresh-install Discovery defaults.

## v2.0.8 — Discovery editor Save reminder

- Restores the two-step Home Assistant Save reminder at the bottom of the Add/Edit Switch editor.
- Restores the same reminder at the bottom of the Add/Edit Stack Member editor.
- Places the reminder in the final field description so it remains visible inside the nested editor itself.
- No Discovery runtime or generated-output behaviour is changed.
- Retains the v2.0.7 Stop Discovery control, v2.0.6 traffic-rate sanity guard, and v2.0.5 fresh-install Discovery defaults.

## v2.0.7 — Stop Discovery control

- Adds a Stop Discovery button beside Run Discovery.
- Stops only the active Discovery job; it does not stop or uninstall the Discovery app.
- Uses process-group termination so active SNMP walk child processes stop with the Discovery job.
- Preserves already-generated files and skips the post-run SNMP2MQTT restart when a run is stopped.
- Adds explicit Stopping and Stopped UI states.
- Retains the v2.0.6 traffic-rate sanity guard and v2.0.5 fresh-install Discovery defaults.

## v2.0.6 — Traffic-rate sanity guard

- Rejects impossible RX/TX rate samples that exceed the selected interface's physical link speed.
- Retains the last valid traffic rate when Home Assistant counter timestamps produce an impossible spike.
- Keeps genuine fresh zero-delta samples at `0 B/s`.
- Retains the v2.0.5 fresh-install Discovery defaults.

## v2.0.5 — Fresh-install Discovery defaults

- Fresh Discovery installs now enable `run_snmp_walks` by default.
- Fresh Discovery installs now enable `generate_snmp2mqtt` by default.
- Fresh Discovery installs now enable `generate_support_my_switch_bundle` by default.
- Existing saved Discovery options are preserved; these are package defaults for new installs only.
- Retains the v2.0.4 RX/TX traffic-rate sample-timing fix.

## v2.0.4 — Traffic-rate sample timing fix

- RX/TX rate calculation now keys off the underlying Home Assistant counter entity update timestamps instead of card redraw time.
- Retains the last calculated traffic rate between SNMP samples instead of forcing `0 B/s` after a frontend stale timeout.
- A fresh counter sample with zero byte delta now produces a genuine `0 B/s`.
- Retains the v2.0.2 Calibration colour-picker overflow fix and v2.0.3 Native generated-dashboard fix.
- Fresh Discovery installs now enable `run_snmp_walks` by default.
- Fresh Discovery installs now enable `generate_snmp2mqtt` by default.
- Fresh Discovery installs now enable `generate_support_my_switch_bundle` by default.
- Existing saved Discovery options are preserved; these are package defaults for new installs only.

# Switch Vision Changelog

## v2.0.3 — Native generated-dashboard card fix

- Fixed Discovery-generated Native dashboard YAML containing the dashboard shell but no Switch Vision cards when member rows were processed.
- Added the missing `member_header_title` jq helper used by generated stack/member card rows.
- Member header titles now use the member-specific value when present and otherwise fall back to the parent switch header title.
- Retains the v2.0.2 Calibration colour-picker overflow fix.
- No SNMP polling, sensor mapping, saved-profile format, reset behaviour, faceplate geometry, Custom dashboard behaviour, or broader Discovery workflow is intentionally changed.

## v2.0.2 — Calibration colour picker overflow fix

- Fixed the Calibration colour picker being clipped by its open section container and appearing underneath the following section.
- Open Calibration sections now use visible overflow so the existing colour popover can extend outside the section boundary.
- Collapsed sections keep the existing clipped rounded-container behaviour.
- UI/CSS-only maintenance change; Calibration logic, saved profiles, reset paths, Discovery, sensors, faceplate geometry, and backend runtime behaviour are unchanged.

## v2.0.1 — Reset All Switches hotfix

- Fixed a frontend regression that prevented **Reset All Switches** from running in both Native and Custom calibration scopes.
- The shared Calibration action handler now defines the active scope before it is used by the Reset All confirmation and status messages.
- The existing scope-isolated backend reset, reset event, and model-aware factory rebuild paths are unchanged.
- No calibration schema, saved-profile format, faceplate defaults, geometry, Discovery, sensors, generated YAML, mappings, or dashboard behaviour changed.

## v2.0.0 Gold — Gold Master / Stable

- Promoted the final v1.9.97 pre-Gold codebase to **Switch Vision v2.0.0 Gold** with no additional runtime feature changes.
- Established v2.0.0 as the new protected and authoritative Gold baseline for future 2.x maintenance.
- Locked the current Installer-led setup path, Discovery workflow, native Home Assistant dashboard, advanced custom-YAML path, Calibration workspace, faceplate defaults, diagnostics, import/export, and Support My Switch workflow.
- Confirmed the normal new-user path as **Installer → Discovery → native Switch Vision dashboard**, with SNMP2MQTT managed by the Installer and manual/custom YAML retained for advanced users.
- Retained all v1.9.97 calibration, faceplate, profile, sensor, Discovery, generated-YAML, and dashboard behaviour unchanged during the Gold promotion.

## v1.9.97 — c3560cg faceplate factory defaults

- Added factory calibration defaults for the bundled `c3560cg-8pc-s.png` faceplate from the newly supplied calibrated faceplate profile.
- Preserved the supplied port, uplink, Status LED, status-box, logo, font, visibility, colour, LED-size, and calibration-button geometry.
- Removed switch-specific export identity, stack membership, management IP, and transfer metadata before bundling the profile as a reusable faceplate default.
- The change is faceplate-specific: model detection, supported-device mappings, sensors, Discovery, generated YAML, and saved user profiles are unchanged.

## v1.9.96 — compact calibration update events

- Removed full calibration objects from the `switch_vision_calibration_updated` Home Assistant event payload.
- Calibration save events now carry only the small routing metadata needed by listening cards, preventing 48-port profiles from exceeding Home Assistant Recorder's 32 KiB event-data limit.
- Listening cards keep the existing compatibility path for older payload-bearing events and otherwise reload the saved profile through the existing Switch Vision websocket API.
- Save Profile, native/custom profile mirroring, cross-card refresh, calibration schema, geometry, Discovery, sensors, generated YAML, faceplates, and dashboard behaviour are unchanged.

## v1.9.95 — Calibration compact geometry row

- Restored the **Status LEDs** Quick Selection shortcut and placed it with the other status controls before the RJ45 shortcuts.
- Quick Selection now reads: **Logo → Status Box 1 → Status Box 1 fields → Status Box 2 → Status Box 2 fields → Status LEDs → All RJ45 → RJ45 Link → RJ45 Activity → All SFP → SFP Link → SFP Activity → Port Numbers → Calibration button**.
- Compacted **Position & Size** into one desktop row: Nudge, size controls, Step, direct X/Y/W/H, Apply, and the target summary now share the same line when space allows.
- Narrower screens still wrap the controls responsively.
- No calibration target IDs, saved-profile data, geometry behaviour, Discovery, sensors, generated YAML, faceplate defaults, or dashboard behaviour changed.

## v1.9.94 — Calibration Quick Selection cleanup

- Renamed and reordered Calibration Quick Selection shortcuts for clearer RJ45/SFP terminology and a more natural left-to-right workflow.
- Quick Selection now reads: **Logo → Status Box 1 → Status Box 1 fields → Status Box 2 → Status Box 2 fields → All RJ45 → RJ45 Link → RJ45 Activity → All SFP → SFP Link → SFP Activity → Port Numbers → Calibration button**.
- Removed the redundant **Status LEDs** quick shortcut from the Quick Selection row; Status LEDs remain fully available from the Calibration Target selector.
- Updated the matching aggregate Target labels without changing any target IDs, saved calibration data, geometry, or behaviour.
- No Discovery, sensor, generated YAML, faceplate, profile schema, or dashboard behaviour changes.

## v1.9.93

- Added drag handles to the seven Calibration workspace sections so users can arrange the editor around long calibration jobs.
- Calibration section order is remembered as a browser UI preference and is never written into calibration profiles.
- Added keyboard Arrow Up / Arrow Down reordering from each drag handle.
- Added **Reset section layout** to restore the v1.9.92 workflow order.
- Kept the sticky Save/reset bar fixed and unchanged.
- No calibration schema, profile storage, rendering, Discovery, sensors, generated YAML, faceplate defaults, or dashboard behaviour changes.

## v1.9.92 — Calibration usability cleanup

- Reorganised Calibration around the normal workflow: **Selection → Position & Size → optional appearance/settings sections → profile actions**.
- Merged the old Calibration Target and Quick Selection panels into one **Selection** section and made Selection and Position & Size open by default.
- Split the oversized Appearance panel into focused **Assets**, **Labels & LEDs**, **Status Boxes**, and **Switch & Stack** sections.
- Compacted common controls, shortened quick-selection labels, and placed direct X/Y/W/H editing on its own compact row.
- Preserved every existing Calibration action and field; no profile schema, saved-profile behaviour, geometry, faceplate defaults, LED logic, Discovery, sensors, generated YAML, model mappings, or dashboard rendering changed.

## v1.9.91 — global port LED colours

- Added profile-wide **Link LED colour** and **Activity LED colour** controls to Calibration using the existing Switch Vision colour picker.
- A selected Link colour applies to every RJ45 and SFP/uplink Link LED; a selected Activity colour applies to every RJ45 and SFP/uplink Activity LED.
- Existing profiles remain visually unchanged until a colour override is selected: factory Link LEDs retain their speed-based colours and Activity LEDs retain their existing behaviour.
- Resetting either LED colour restores factory behaviour rather than forcing a new colour into older profiles.
- LED state, activity timing, geometry, Discovery, sensors, generated YAML, model mappings, and dashboard layout are unchanged.

## v1.9.90 — changelog ownership cleanup

- Removed the release-history/changelog browser from the Switch Vision Discovery Hub.
- Removed Discovery's generated changelog-history JSON, API endpoint, browser controls, and build-time history generation.
- Release changelog browsing now belongs exclusively to the Switch Vision Installer.
- No changes to Discovery execution, Calibration, faceplates, profiles, sensors, generated YAML, model mappings, or dashboard rendering.

## v1.9.89 — Pre-2.0 stability audit hardening

- Remove unused Home Assistant `/config` access from the Discovery app.
- Migrate Discovery from deprecated `build.yaml` handling to a Dockerfile-only Home Assistant Alpine 3.22 build.
- Add a one-time migration that removes the retired `show_card_header` saved option.
- Constrain clean-before-walk deletion to the canonical `/share/switch_vision/snmpwalks` tree, including symlink-aware path resolution.
- Strengthen Discovery configuration import validation for paths, booleans, numeric limits, switch rows, stack rows, and model choices.
- Correct WS-C3560CG-8PC-S visual metadata to its dedicated 2048×329 faceplate and preserve the legacy faceplate as an optional fallback.
- Improve Calibration failure guidance to point to the browser console as well as Home Assistant logs.
- Add Discovery vendor/interface self-test and device-visual registry consistency to the build release gates.
- Refresh pre-2.0 stability documentation.

## v1.9.88 — changelog navigation

- Added a compact changelog browser to the Switch Vision Hub with simple left and right arrows to move through release history one version at a time.
- The current release opens by default; the left arrow moves to older entries and the right arrow returns toward newer entries.
- Added build-time generation of the Hub changelog history from the authoritative `CHANGELOG.md`, so future release entries are included automatically.
- Contains no changes to Calibration, faceplate defaults, profiles, Discovery execution, sensors, generated YAML, model mappings, or dashboard rendering.

## v1.9.87 — persistent Calibration colour picker

- Removed custom Calibration colour pickers from enclosing HTML `label` elements so browser label activation cannot close the picker while it is being used.
- The picker now remains open during saturation/value dragging, hue and brightness changes, HEX editing, and Reset.
- The picker closes only with Done, Escape, or a click outside the picker.
- Applied the fix to Status LED text, RJ45 port numbers, uplink labels, and both Status Box text/background/border colour controls.
- Added a regression check preventing custom colour pickers from being nested inside HTML labels again.

## v1.9.86 — Status LED text styling and inline colour picker

- Added independent Status LED label Font, Font size, Bold, and Text colour controls in Calibration.
- Preserved older-profile appearance with backward-compatible defaults matching the established Status LED text style.
- Replaced browser-native colour inputs with a persistent Switch Vision inline colour picker for Calibration custom-colour controls.
- Added draggable saturation/value, hue and brightness controls, live switch preview, editable HEX input, Reset, Done, outside-click close, and Escape close behaviour.
- Applied the shared picker to Status LED text, RJ45 numbers, uplink labels, and Status Box text/background/border colours.

## v1.9.85 — native faceplate reset correction

- Rebuilt the reset change from the v1.9.82 baseline rather than stacking the v1.9.83/v1.9.84 runtime attempts.
- Fixed calibration identity copying so scalar profile identifiers and nested identity data are deep-copied without being passed through whole-profile normalisation.
- **Reset Current Faceplate** now resolves the faceplate from the calibration currently displayed in the editor, so native and custom scopes use the same bundled faceplate-specific defaults.
- Future bundled faceplates automatically participate when a matching `calibration/faceplate-*.json` factory profile is present; model defaults remain the fallback when no faceplate-specific defaults exist.
- Retained build-time synchronization and validation of embedded faceplate defaults against the authoritative calibration JSON files to prevent stale native/card copies.
- No calibration geometry, profile schema, model mappings, Discovery behaviour, sensors, generated YAML, or dashboard layout changed.
## v1.9.82 — SFP label visibility

- Added per-SFP/uplink `label_show` visibility with backward-compatible shown-by-default behaviour.
- Added Show/Hide controls for individual and grouped SFP labels in Calibration.
- Expanded **All numbers** Quick Selection to include both RJ45 port numbers and SFP/uplink labels for movement, direct coordinates, and visibility.
- Preserved existing profile compatibility and made no changes to Discovery, sensors, generated YAML, faceplate mappings, or dashboard layout.

## v1.9.81 — bundled black Cisco logo

- Added `cisco-black-logo.png` to the bundled logo assets for optional selection in Calibration.
- Preserved the supplied 2048 × 2048 transparent PNG unchanged.
- No default logo, model mapping, calibration geometry, profile behaviour, Discovery, sensors, generated YAML, or dashboard rendering changed.

## v1.9.80 — calibration label colours

- Added a Calibration colour control for status LED label text.
- Added a separate Calibration colour control for RJ45 port numbers.
- Kept the existing uplink-label colour control independent, with backward-compatible fallbacks for older profiles.
- Contains no intentional changes to calibration geometry, profile selection, faceplate defaults, Discovery, sensors, generated YAML, or dashboard layout.

## v1.9.79 — direct width and height controls

- Added direct W and H pixel fields beside the existing X and Y controls in Calibration.
- Single targets show their current size; grouped targets show a shared size or `Mixed` when dimensions differ.
- Users may apply only W, only H, or both while leaving blank values unchanged.
- Supports RJ45 and SFP boxes, RJ45 and SFP LEDs, logos, status boxes, and the calibration button.
- Contains no profile-schema, faceplate-default, Discovery, sensor, generated-YAML, or dashboard-rendering changes.

## v1.9.78 — Calibration selection and coordinate controls

- Custom ports now automatically reflects the active single-port or multi-port RJ45 selection, making it easy to remove or add individual ports before reselecting.
- Added optional direct X and Y coordinate inputs to Position and Size.
- A single axis can be applied while leaving the other unchanged, or both axes can be applied together.
- Direct coordinates work with individual targets and existing grouped selections without changing the established selection model.
- No profile format, faceplate defaults, Discovery, sensors, generated YAML, or dashboard rendering changes.

## v1.9.77 — Calibration step-control placement

- Moved the pixel-step selector from **Calibration Target** to the end of **Position and Size**, immediately after `H+`.
- Keeps target selection focused on the selected item and groups the step size with movement and resizing controls.
- Contains no changes to calibration geometry, profiles, faceplate defaults, imports/exports, Discovery, sensors, generated YAML, or dashboard rendering.

## v1.9.76 — static calibration selection

- Changed selected Calibration targets from flashing yellow to a continuous static yellow highlight.
- Removed the calibration-only blink clock, blink interval defaults, and time-dependent active-state checks.
- Live switch port and SFP activity LED blinking remains unchanged and separate from Calibration selection highlighting.
- Contains no changes to calibration coordinates, profile storage, imports/exports, faceplate defaults, Discovery, sensors, generated YAML, or dashboard layout.

## v1.9.75 — SFP LED calibration controls

- Added independent **Link/speed LED** and **Activity LED** Calibration parts for individual SFP/uplink ports.
- Added matching aggregate targets for all SFP link/speed LEDs and all SFP activity LEDs.
- Added optional SFP `led_left`, `led_right`, `led_left_size`, and `led_right_size` profile fields with legacy fixed-offset fallback for older profiles.
- Included SFP LED geometry in normal profile save, export/import, faceplate defaults, target reset, movement, resize, and calibration guide-ring behaviour.
- Existing profiles without SFP LED coordinates retain their previous visual positions.

## v1.9.74 — submarine SFP label correction

- Updated the bundled `submarine-48rj45-4sfp.png` faceplate defaults with the corrected SFP label positions from the latest exported Calibration profile.
- Changed only the G1, G2, G3/TE3, and G4/TE4 label coordinates.
- All RJ45 coordinates, SFP centers and hitboxes, LEDs, status panels, logo, calibration button, model mappings, and runtime behaviour remain unchanged.

## v1.9.73 — submarine faceplate defaults

- Added factory faceplate-selection defaults for `submarine-48rj45-4sfp.png` from the exported Calibration profile.
- Selecting the submarine faceplate now starts from its supplied 48-port, four-uplink, LED, label, status-panel, logo, and calibration-button geometry when no saved faceplate profile exists.
- **Reset Current Faceplate** and individual calibration target resets now restore the submarine faceplate's own defaults while preserving the selected faceplate.
- Removed switch-specific IP, stack-member, and profile-transfer metadata from the bundled factory defaults.
- The standard 48-port model calibration, Discovery mappings, model-default faceplates, and the current calibration Save confirmation remain unchanged.

## v1.9.72 — configuration reminder placement

- Removed the Save-twice warning from the Card header title help text, where Home Assistant collapsed it into the preceding sentence.
- Moved the reminder to the Switches and Stack Members section descriptions so it remains clear without crowding the final field.
- No Discovery execution, device mapping, faceplate, calibration, sensor, YAML generation, or dashboard behaviour was changed.

## v1.9.71 — dedicated 3560CG faceplate

- Bundled `c3560cg-8pc-s.png` at its native 2048 × 329 dimensions.
- Made the new artwork the default faceplate for `WS-C3560CG-8PC-S`.
- Updated the model calibration profile to reference the native slim canvas while preserving its editable calibration data for final user calibration.
- Retained `24rj45-2sfp.png` as an optional fallback faceplate.
- Contains no intentional changes to Discovery execution, sensors, generated YAML, dashboards, or other device profiles.

## v1.9.70 — bundled submarine faceplate

- Added `submarine-48rj45-4sfp.png` as a bundled alternative faceplate asset.
- This is an optional bundled faceplate only; no runtime logic, device mappings, calibration behaviour, or dashboard behaviour was changed.

## v1.9.69 — 3560-C manual model selection

- Added `WS-C3560CG-8PC-S` to the Discovery manual switch-model dropdown.
- The model was already registered for automatic detection, profile mapping, and experimental device support; this change only makes the same registered model selectable as a manual override.
- Contains no intentional changes to Discovery processing, profiles, sensors, calibration, dashboards, or faceplates.

## v1.9.68 — Hub wording and reminder spacing

- Updated the Hub wording to **Show detected devices & status**, **Detailed device(s) information**, and **Logging level**.
- Removed unsupported literal HTML/Markdown from the add/edit reminder descriptions.
- Added two preserved spacer lines above the warning reminder and kept warning symbols at both ends.
- Contains no intentional changes to Discovery execution, generated files, profiles, sensors, calibration, resets, dashboards, or faceplates.

## v1.9.67 — Switch Vision Hub cleanup

- Renamed the Discovery landing page to **Switch Vision Hub** and removed its introductory subtitle.
- Simplified the landing-page cards and wording for Discovery, Devices, Support My Switch, detected-device information, and configuration import/export.
- Removed duplicate Dashboard & Calibration and Installer launch cards because both already have dedicated Home Assistant sidebar entries.
- Renamed and simplified the Switch Vision, Discovery, and SNMP2MQTT settings cards.
- Contains no intentional changes to Discovery execution, generated files, profiles, sensors, calibration, resets, dashboards, or faceplates.

## v1.9.66 — Final UI polish

- Changed the add/edit Save reminder to a larger warning-triangle line with extra spacing and a matching trailing warning symbol.
- Made **Generated SNMP2MQTT YAML** a collapsible section matching **Generated Card YAML**.
- Contains no intentional changes to Discovery generation, profiles, sensors, calibration, resets, dashboards, or faceplates.

## v1.9.65 — Final stability audit

- Made optional logo and faceplate folder failures non-fatal so filesystem permission or transient storage problems cannot prevent the integration or native panel loading.
- Made generated-dashboard metadata races non-fatal; successfully parsed cards remain available if the file is replaced between reading and metadata lookup.
- Made shared UI-preference write failures log a warning instead of aborting integration setup.
- Added build-time README resource-version synchronisation and refreshed stale current-release documentation.
- Fixed checksum manifests to reference the release ZIP in its actual `Releases/` path, allowing direct `sha256sum -c` verification from the source root.
- Re-ran Python, JavaScript, shell, JSON, YAML, archive, version-propagation, and reproducible-build validation without changing established feature behaviour.

## v1.9.63 — Generated Card YAML preview

- Added a collapsible **Generated Card YAML** section above **Generated SNMP2MQTT YAML** in the Discovery Web UI.
- Added generated-card status, YAML validation, preview, copy-to-clipboard, and download actions.
- The preview refreshes after Discovery and reports missing or invalid output instead of showing stale content.
- Separated the add/edit reminder from the card-title example with a clearer yellow-square warning line.
- Contains no intentional changes to Discovery generation, calibration, profile storage, imports, resets, sensors, or dashboard rendering.

## v1.9.62 — Global card-header control

- Replaced per-switch card-header visibility with one global **Show card headers** integration option.
- Applied the setting to native and custom YAML cards through a shared runtime UI-settings service.
- Removed the per-switch Discovery field while retaining custom card-header titles.
- Ignored retired per-card header flags to prevent conflicting sources of truth.

## v1.9.61 — Discovery header-save fix

- Fixed Discovery preserving an explicit `show_card_header: false`; jq no longer treats boolean `false` as missing during fallback or row serialisation.
- Applied the same explicit-boolean handling to parent switches and individual stack members.
- Added the reminder **“Remember: click Save again on the next page.”** at the bottom of the add/edit switch and stack-member forms.
- Contains no intentional changes to calibration, scoped storage, import/export, reset behaviour, sensors, or native/custom isolation.

## v1.9.60

- Fixed native card-header visibility after upgrades by using a release-specific native card renderer, preventing an older custom element retained by Home Assistant SPA navigation from overriding the current setting.
- Canonicalised `show_card_header` in the backend with strict precedence over retired aliases, including an explicit `false`.
- Kept manual YAML on the stable `custom:switch-vision-3650` element while isolating native-panel renderer upgrades.

## v1.9.59 — Full audit fixes

- Fixed Discovery stack-card generation so secondary members always inherit uptime from the configured member 1 sensor when a valid stack is present.
- Hardened generated dashboard YAML by quoting user/configuration strings and normalising control characters in generated rows.
- Cleaned duplicated and out-of-order recent changelog entries.
- Verified calibration JSON normalisation already performs a single parse and retained that safe implementation unchanged.
- Contains no intentional changes to scoped profile storage, import/export, reset behaviour, calibration geometry, sensor mappings, or switch identity.

## v1.9.58 — Header controls

- Replaced the partial metadata toggle with per-card **Show card header**, which hides or shows the complete title/metadata row without leaving a gap.
- Added global native-panel **Show dashboard header** integration option while preserving the mobile menu button when hidden.
- Kept legacy card-header keys as compatibility aliases.

## v1.9.57 — Card header title type fix

- Fixed generated cards showing `true • SWx` when the optional card header title was blank.
- Discovery preserves empty fields while generating dashboard cards, preventing boolean settings from shifting into title fields.
- Boolean and legacy string values of `true` or `false` are treated as an empty custom header title and fall back to the normal card title.

## v1.9.56 — Discovery card-header controls

- Added per-switch card-header visibility and optional custom header title.
- Added concise practical examples to useful Discovery fields.
- Preserved compatibility with the earlier `show_card_header_information` and `show_card_metadata` keys.

## v1.9.55 — Native mobile navigation

- Added a mobile-only Home Assistant menu button to the native Switch Vision panel using the standard `hass-toggle-menu` event.

## v1.9.54 — Scoped Reset All backend fix

- Added backend validation and handling for explicit `native` and `custom` reset scopes.
- Reset All from one dashboard scope no longer clears the opposite scope.

## v1.9.53 — Reset controls and confirmation dialogs

- Moved **Reset All Switches** beside the current reset actions and styled it purple.
- Replaced small browser prompts with larger responsive Switch Vision confirmation dialogs.

## v1.9.52 — Scoped Reset All

- Scoped Reset All to the dashboard namespace that launched it.

## v1.9.51 — Reset action layout

- Moved **Reset Current Switch** beside **Reset Current Faceplate**.
- Styled faceplate reset orange and current-switch reset red.

## v1.9.50 — Scoped profile import/export

- Restored faceplate profile import/export on the proven `native_SWx` / `custom_SWx` storage model.
- Imports target only the card scope that launched them and cannot write to factory profiles.
- Native and custom YAML scopes remain independent through save, refresh, restart, and cross-device use.

## v1.9.49 — Scoped profile storage

- Added deterministic writable namespaces `native_SWx` and `custom_SWx`.
- Native and custom YAML cards for the same physical switch no longer share calibration records.
- Factory profiles remain read-only templates.

## v1.9.48 — Import persistence test

- Reworked imported profile persistence on the earlier unscoped design. Superseded by the scoped storage introduced in v1.9.49.

## v1.9.47 — Import safety test

- Added factory-profile protection and switch-specific import targeting. Superseded by the scoped storage introduced in v1.9.49.

## v1.9.46 — Retired importer persistence attempt

- Retired due to unsafe shared-profile behaviour. Upgrade to v1.9.50 or later before using profile import/export.

## v1.9.45 — Retired importer persistence attempt

- Retired due to unsafe shared-profile behaviour. Upgrade to v1.9.50 or later before using profile import/export.

## v1.9.44 — Initial faceplate profile transfer

- Introduced faceplate profile import/export. Its original save-destination model was replaced by scoped storage in v1.9.49-v1.9.50.

## v1.9.43 — Calibration workflow baseline

- Added larger calibration movement steps, Entire port default targeting, and per-port number visibility.

## v1.9.42 — Colour controls

- Added contextual colour pickers for existing colour-enabled calibration elements while preserving operational LED colours.

## v1.9.41 — Discovery and Support UI theme

- Unified Discovery and Support My Switch styling with the Switch Vision dark navy application theme.

## v1.9.40 — Compact calibration header

- Reduced the calibration header to Switch, Model, Faceplate, and Profile while retaining state and geometry in the sticky footer.

## v1.9.39 — Discovery navigation polish

- Simplified home tiles and added consistent neutral, hover, and keyboard-focus states.

## v1.9.38 — Public release documentation and packaging

- Rebuilt public documentation and packaging around the tested v1.9.37 runtime baseline.

## v1.9.37 — Automatic profile-selection cleanup

- Removes the user-facing **Apply Recommended Setup** action and its duplicate temporary-profile path.
- Removes the obsolete recommendation/compatibility row from Interactive Calibration.
- Keeps exact-model detection authoritative for initial profile selection, missing-profile recovery, **Reset Current Switch**, and **Reset All Switches**.
- Keeps unknown or unregistered switches on a visible fallback profile that users can freely customise until an official or custom profile is available.
- Leaves faceplate selection, calibration persistence, Discovery, sensors, and Support My Switch behaviour unchanged.

## v1.9.36 — Always-visible faceplate correction

- Removes **None** from the faceplate selector; valid choices are now **Default / recommended** or a named custom faceplate.
- Migrates legacy hidden, `__none__`, blank, or invalid faceplate states to the exact model's recommended visible artwork.
- Falls back to the recommended faceplate when a selected custom image is missing or fails to load.
- Preserves logo hiding as a separate supported option.
- Retains all v1.9.35 calibration-profile validation and title escaping.

## v1.9.35 — Faceplate states and calibration profile validation

- Separates **None**, **Default / recommended**, and explicit custom faceplate selections.
- Makes **None** render no faceplate image and resolves **Default / recommended** from each switch's exact model or factory profile.
- Migrates legacy `show: false` plus `__default__` profiles to the intended recommended-faceplate state while preserving explicit `__none__` selections.
- Validates imported, saved, and loaded calibration profiles for payload size, profile names, finite coordinates, positive dimensions, canvas bounds, element counts, asset filenames, and JSON safety.
- Rejects invalid stored profiles safely and falls back to the current card/factory calibration instead of rendering corrupt data.
- Escapes card titles before inserting them into the frontend DOM.
- Adds executable backend and browser-side regression coverage without changing Discovery, sensors, Support My Switch, or calibration storage transactions.

## v1.9.34 — Frontend listener and native-panel resilience

- Releases calibration event subscriptions when cards leave the page and re-establishes one clean subscription when they reconnect.
- Prevents duplicate subscriptions across repeated Home Assistant state updates and connection replacements.
- Retries transient event-subscription failures with bounded backoff and safely releases subscriptions that complete after a card has already disconnected.
- Builds a complete native-sidebar replacement dashboard away from the visible panel before committing it.
- Keeps the current working switch cards visible when a refresh, module import, or generated card configuration fails.
- Preserves the rendered panel across normal disconnect/reconnect cycles and ignores stale asynchronous refresh results.
- Adds executable frontend lifecycle and atomic-refresh regression coverage without changing calibration, Discovery, sensors, or support-bundle behaviour.

## v1.9.33 — Support bundle privacy-processing safety

- Prevents Support My Switch bundles from reporting PASS when any file could not be fully inspected or sanitized.
- Excludes unsupported binary, oversized, unreadable, unwritable, symbolic-link, and special-file entries from the temporary archive copy.
- Records privacy-safe file identifiers, reasons, suffixes, sizes, and exclusion counts without exposing original filenames or paths.
- Marks incomplete bundles **REVIEW REQUIRED**, sets `ready_to_send` to false, and withholds prepared `.eml` and send actions.
- Keeps clean, fully inspected bundles on the existing PASS or PASS WITH PRIVACY WARNINGS workflow.
- Aligns sanitizer, bundle, manifest, text-report, Web UI, and email-gating behaviour at processing version 9.

## v1.9.32 — Reset All persistence correction

- Fixes Reset All calculating the correct model layout but leaving it only in temporary editor state.
- Every loaded native or custom YAML card now saves its own model-aware factory default to its stable base profile after the global store is cleared.
- Keeps the correct default authoritative while Calibration is closed and across refresh/restart.
- Retains the safe no-generic-fallback behaviour when model context is temporarily unavailable.

## v1.9.31 — Model-aware Reset All defaults

- Fixes **Reset All Switches** rebuilding 2960S, 2960X, and 3560-C cards with the generic 48-port/4-SFP layout.
- Resolves each card from its exact model first, then its already-loaded factory profile when exact-model sensor context is temporarily unavailable.
- Restores 2960S/2960X 48-port models to 48 RJ45 / 2 SFP, 2960X 24-port models to 24 RJ45 / 4 SFP, and keeps all other registered model defaults intact.
- Defers a global reset rather than displaying the wrong generic geometry when no model-aware context is available yet.
- Leaves **Reset Current Switch**, calibration storage transactions, rectangle LED geometry, Discovery, and sensors unchanged.

## v1.9.30 — Calibration storage transaction safety

- Serializes calibration save, delete, reset, and profile-read operations through one integration-level asynchronous lock.
- Saves a native faceplate-specific profile and its switch-scoped base mirror in one atomic storage transaction.
- Records which faceplate profile supplied each mirrored base profile and safely recognises equivalent legacy v1.9.29 mirrors.
- Removes an active mirrored base profile when its source faceplate profile is deleted, preventing stale native-panel calibration data.
- Reports every profile changed by a transaction and supplies the correct per-profile calibration payload to other open dashboards.
- Clears deleted calibration data from frontend memory before reloading fallback/default geometry.
- Adds storage-safety regression checks without changing calibration controls, rendering, Discovery, or sensor behaviour.

## v1.9.29 — Independent rectangle LED geometry

- Gives every RJ45 Link/Speed and Activity rectangle its own saved width and height.
- Prevents rectangle LED W/H controls from resizing the RJ45 port hitbox.
- Keeps Link/Speed and Activity rectangle dimensions independent for individual, selected, odd/even, and all-port targets.
- Migrates older calibration profiles in memory with dimensions matching the previous fixed rectangle appearance.
- Preserves Circle rendering and accepts older imported profiles that do not contain rectangle-size fields.
- Validates optional rectangle-size fields when importing profiles and displays their true W/H values in the calibration footer.

## v1.9.28 — Code hygiene and regression hardening

- Consolidates native-sidebar calibration persistence into one atomic save call while keeping custom YAML profiles isolated.
- Adds explicit native-only base-profile mirroring instead of unconditional backend mirroring.
- Fixes the build system so historical changelog versions are never rewritten during packaging.
- Keeps the root and source README/CHANGELOG copies synchronised from one authoritative document set.
- Excludes Gold-only documents and development artefacts from non-Gold source archives.
- Adds maintenance regression checks for per-switch profile isolation, custom topology persistence, source synchronisation, archive hygiene, and historical changelog preservation.
- Refreshes current installation/build guidance without changing runtime rendering, Discovery, sensor, faceplate, or calibration behaviour.

## v1.9.27

- Preserves deliberately added or removed visual RJ45 and uplink ports after **Save Profile** or **Done**.
- Treats a user-saved calibration topology as authoritative instead of rebuilding it to the exact-model factory port count.
- Keeps exact-model reconciliation only for missing, starter, or legacy profiles that have not been explicitly saved by the user.

## v1.9.26

- Fixes a native-sidebar calibration load race that could replace a newly selected custom faceplate with the starter/default profile when **Done** was clicked.
- Waits for the saved switch profile (and optional starter profile) to finish loading before opening Calibration.
- Shows a brief **Loading…** state while the per-switch calibration profile is prepared.
- Leaves custom/manual YAML dashboard profile behaviour unchanged.

## v1.9.25

- Fixes native-sidebar custom faceplates being overwritten by generated card defaults after **Done**.
- Treats a saved switch calibration profile as authoritative for faceplate selection in the native panel.
- Keeps explicit `faceplate_file` and `faceplate_show` overrides unchanged for manual/custom YAML dashboards.

## v1.9.24

- Fixes native-sidebar custom faceplates not persisting after **Done**.
- Mirrors native-panel faceplate-specific saves back to the stable per-switch base profile used to bootstrap each card.
- Keeps manual/custom YAML dashboard save behaviour unchanged.

## v1.9.23

- Isolates native-sidebar faceplate and calibration persistence per discovered switch.
- Prevents one switch's selected faceplate from propagating to other cards that share the same model/factory profile.
- Leaves generated custom YAML dashboard profile behaviour unchanged.

## v1.9.22

- Improves the Support My Switch home-page descriptions with clearer, action-focused guidance.
- Clarifies the purpose of Discovery, Devices, contribution bundles, Diagnostics, Configuration, and linked Switch Vision tools.
- Updates the central-tools introduction to better reflect the page as the main navigation hub.

## v1.9.21 Experimental

- Adds a per-profile Port LED Shape selector for Link/Speed and Activity LEDs.
- Supports Circle and Rectangle port LED rendering while keeping all status LEDs circular.
- Existing profiles remain compatible and default to Circle.

## v1.9.20 Experimental

- Restores the known-good v1.9.15 calibration behaviour and excludes the abandoned cross-device live-preview implementation.
- Adds a live selected-target geometry readout beside the calibration save state in the sticky footer.
- The footer readout updates with the selected target, part, X, Y, width, and height as calibration controls move or resize it.

## v1.9.15 Experimental

- Updates Quick Selection complete-port movement to include the port box and link/activity LEDs while leaving port-number labels in place.
- Keeps port-number labels independently selectable through the Part control and dedicated number-selection buttons.

## v1.9.14 Experimental

- Places Calibration Target and Port manager controls on one responsive row.
- Makes Quick Selection port buttons select and move the complete port group, including the port box, link/activity LEDs, and number label.
## v1.9.13 Experimental

- Renames the status-box font controls from **Status font** to **Font** for cleaner column alignment.
- Removes the reserved calibration workspace footer gap so the sticky action bar follows the content directly.
- Keeps normal scrolling when expanded calibration sections exceed the available viewport.

## v1.9.12 Experimental

- Aligns calibration labels, inputs, selectors, and action buttons into cleaner rows.
- Places Switch IP and stack controls on one coordinated Switch / Stack row.
- Removes excess spacing beneath collapsed or short calibration sections.
- Keeps responsive wrapping for narrower screens.

## v1.9.11 Experimental

- Polishes the Interactive Calibration workspace with a clearer switch/model/faceplate/profile header.
- Adds an always-visible unsaved/saved state indicator.
- Adds a sticky Save Profile, Cancel, and Reset Current Faceplate action bar.
- Moves import, export, reload, and broader reset tools into a collapsible advanced section.
- Adds confirmation before Done saves and closes a modified calibration session.
- Leaves calibration geometry, storage, Discovery, and dashboard behavior unchanged.


## v1.9.10

- Fixed Support My Switch app links so public releases do not depend on instance-specific Home Assistant repository hashes.
- Discovery settings now use the stable local app route.
- SNMP2MQTT settings and Switch Vision Installer links are resolved dynamically from the installed Supervisor app list.
- Added a clear message when a linked app is not installed or cannot be resolved.

## v1.9.9

- Expanded the Support My Switch main page into the central Switch Vision launch point.
- Added direct links to Dashboard & Calibration, Integration Settings, Discovery App Settings, SNMP2MQTT Settings, and the Switch Vision Installer.
- Retained the existing Discovery, Devices, Support My Switch, Diagnostics, and Configuration workflows.

## v1.9.8

- Fixed Diagnostics falsely warning that generated SNMP2MQTT/dashboard YAML was older when files were produced moments apart during the same Discovery run.
- Stale-file warnings now require a meaningful age difference and show the compared timestamps.
- Fixed the faceplate PoE LED so it honours the configured `poe_used_entity`/`poe_used_mw_entity` and correctly handles watt, milliwatt, and kilowatt units.
- Retained the existing WS-C3560CG-8PC-S mapping of Gi0/1-Gi0/8 as RJ45 and Gi0/9-Gi0/10 as G1/G2 uplinks.

## v1.9.7

- Fixed Discovery-generated dashboard cards to use the exact-model calibration profile from the supported-device registry.
- `WS-C2960X-24TS-L` now defaults to the bundled 24-port / 4-SFP profile.
- `WS-C3560CG-8PC-S` now defaults to the temporary 24-port / 2-SFP visual profile instead of the generic 48-port profile.

## v1.9.6 — Calibration reset controls

- Added **Reset Current Faceplate** to restore the active faceplate's saved geometry, status LEDs, logo, calibration button, and status panels to the switch model defaults while keeping the selected faceplate image.
- Added **Reset Current Switch** to remove every saved faceplate-specific calibration for the active switch and restore its recommended model defaults.
- Added **Reset All Switches** to clear every saved Switch Vision calibration across all dashboards, protected by a two-step confirmation.
- Added backend reset handling and cross-client reset events so other open dashboards return to defaults immediately.

## v1.9.5 — Cross-device calibration synchronisation

- Fixed custom faceplates and calibration changes not appearing on phones, fresh browsers, or Incognito sessions.
- The faceplate-specific calibration is now mirrored to the switch base profile as the shared active selection.
- Calibration update events now carry the saved calibration and base-profile identity so other clients update immediately.

## v1.9.4 — Per-status-LED visibility

- Added independent visibility controls for every status LED in Interactive Calibration.
- Unticking STAT, SYST, DUPLX, ACTV, SPEED, STACK, or PoE now hides only that LED for the active calibration profile.
- Per-LED visibility is saved with faceplate-specific and switch-default calibration profiles.
- Existing profiles remain fully compatible and keep all status LEDs visible by default.

## v1.9.3

- Fixed custom faceplates reverting to the exact-model default after clicking **Done** in Calibration.
- Exact-model reconciliation now preserves the saved faceplate while continuing to enforce compatible port and uplink geometry.

## v1.9.2 — Custom faceplate persistence fix

- Preserved the user-selected faceplate when closing the visual card editor with Done.
- Updated exact-model profile reconciliation so authoritative port and uplink geometry no longer forces the model's default faceplate.
- Custom faceplates now remain selected after the card configuration is saved and reloaded.

## v1.9.1 — Home Assistant event-loop filesystem fix

- Moved Switch Vision logo and faceplate directory creation/scanning off Home Assistant's asyncio event loop.
- Updated both integration startup and the asset-list WebSocket command to use `hass.async_add_executor_job`.
- Removes the `Detected blocking call to scandir` warning without changing asset discovery or calibration behaviour.

## v1.9.0 — Dynamic faceplate-specific calibration profiles

- Added automatic calibration namespaces for every faceplate, keyed by the active switch profile and faceplate filename.
- Changing faceplates now loads that faceplate's saved geometry or creates a starter profile from the current switch geometry when no profile exists.
- Port boxes, port labels, link/speed LEDs, activity LEDs, SFP/uplink positions, status panels, logos, and calibration-button geometry can now be calibrated independently for each faceplate.
- The default faceplate continues to use the existing switch calibration profile, preserving compatibility with all saved v1.8.x profiles.
- Added a clear Calibration header showing the switch profile, active faceplate, and whether the profile scope is Switch default or Faceplate-specific.
- Calibration exports now record the base profile, profile scope, and faceplate filename.
- New community faceplates work without code changes: copy the image into the faceplates folder, select it, then calibrate and save.

## v1.8.29 — Discovery typography polish

- Reduced the Discovery web interface typography globally for a cleaner, less oversized presentation.
- Added shared font-size and line-height variables so future UI tuning remains consistent across pages.
- Reduced page headings, section headings, body text, helper text, status values, and navigation-card labels while preserving readability.
- Contains no switch-rendering, discovery-engine, sensor-generation, or device-support changes.

## v1.8.27 — Installer and clean-update validation release

- Rebuilt the current v1.8.26 code and documentation baseline as v1.8.27 for end-to-end Installer v1.9.3 testing.
- Provides a real version change so the installer can verify automatic Discovery stop, rebuild, restart, and installed-version confirmation.
- Carries forward the current confirmed support status for Cisco 2960S/2960X 48-port models and standalone Juniper EX3300.
- Contains no functional switch-rendering changes beyond the version bump and synchronized release metadata.

## v1.8.26 — Hardware support status refresh

- Promoted `WS-C2960X-48FPD-L` to Confirmed after real-hardware validation of both 10G SFP+ uplinks, link state, activity, and traffic operation.
- Promoted `WS-C2960S-48FPD-L` to Confirmed after real-hardware validation of both 10G SFP+ uplinks, link state, activity, and traffic operation.
- Promoted standalone `EX3300-48P` to Confirmed after real-hardware validation of its SFP/SFP+ uplink path, link state, activity, and 64-bit traffic counters.
- Kept Juniper Virtual Chassis outside the confirmed support scope pending dedicated validation.
- Retained the Juniper native-VLAN plus optional MODE presentation workaround for clear ACCESS/TRUNK display.
- Kept the registered Cisco 2960X 24-port and Cisco 3560-C models Experimental pending model-specific live validation.

# v1.8.25

- Started Experimental Cisco Catalyst 2960X support for `WS-C2960X-24TS-L` from Support My Switch contribution `SV-2026-000001`.
- Added exact model recognition and the dedicated `cisco-2960x-24ts-24p-4sfp` Discovery profile.
- Mapped 24 RJ45 interfaces and four Gigabit SFP uplinks using the existing `24rj45-4sfp.png` faceplate and `cisco_2960x_24p` calibration geometry.
- Enabled stack-aware Discovery for the contributed three-member layout.
- Added status, VLAN, description, link, speed, duplex, and traffic/activity generation through the standard Catalyst 2960X sensor path.
- Marked the model Experimental pending contributor validation of member mapping, uplinks, VLAN/trunk display, and live activity.


## v1.8.26

### Discovery configuration export and import

- Added a Configuration page to the Switch Vision Discovery web interface.
- Added one-click export of the configured switch list, stack-member mappings, and Discovery settings.
- Added validated JSON import for restoring Discovery configuration on a fresh Home Assistant installation.
- Import preserves Support My Switch privacy and contributor preferences.
- Creates `/data/options.before-import.json` before replacing Discovery settings.
- Export files include switch addresses and SNMP community strings and must be stored securely.

## v1.8.24

- Started Experimental Cisco Catalyst 3560-C support for `WS-C3560CG-8PC-S` from Support My Switch contribution `SV-2026-000001`.
- Added exact sysObjectID recognition for `1.3.6.1.4.1.9.1.1317` and a dedicated `cisco-3560cg-8pc-8p-2dual` Discovery mapping profile.
- Mapped `Gi0/1` through `Gi0/8` to eight front-panel access ports and `Gi0/9` through `Gi0/10` to two dual-purpose uplink positions.
- Added a temporary `cisco_3560cg_8pc` calibration profile using the bundled `24rj45-2sfp.png` faceplate until a dedicated 3560-C faceplate is supplied.
- Added walk-aware status, activity, traffic, VLAN, alias, speed and PoE generation for the 3560-C two-component interface naming format.
- Kept the model Experimental pending contributor confirmation of live port activity, uplink media behaviour, VLAN display and PoE telemetry.

## v1.8.23

- Fixed Cisco SFP/uplink VLAN presentation so an active trunk displays `TRUNK` instead of its numeric native/PVID VLAN.
- Kept Juniper VLAN presentation unchanged: the VLAN row continues to show the native VLAN while optional MODE shows `TRUNK` or `ACCESS`.
- Preserved numeric VLAN display for Cisco access ports.

## v1.8.22

- Added `MODE` as an optional selected-interface status field for Juniper switches only.
- Kept the default selected-interface layout as `VLAN`, `DESC`, `LINK`, `RX`, `TX`, with `MODE` hidden by default.
- Calibration can now show `MODE` and hide `DESC`, producing the useful Juniper layout `VLAN`, `MODE`, `LINK`, `RX`, `TX`.
- Unified the Interface Status Box visibility and ordering controls across Juniper RJ45 and SFP/uplink selections.
- Cisco selected-interface panels continue to omit `MODE`.

## v1.8.20

- Bound selected SFP/uplink status panels to the new Juniper EX VLAN Mode and Native VLAN entities generated by Discovery.
- SFP status rows now show `VLAN` and `MODE` directly, with Juniper entities such as `sensor.<switch>_sfp_10g_<n>_native_vlan` and `sensor.<switch>_sfp_10g_<n>_vlan_mode` resolved automatically.
- Preserved existing Cisco VLAN/trunk fallbacks and SFP link/traffic display.

## v1.8.16

- Fixed saved SFP/uplink label coordinates so G1/G2 label positions persist after Save Profile, Done, profile reload, and dashboard reload.
- Preserved compatible older saved calibrations that predate the factory-profile metadata field instead of replacing them with factory geometry.
- Added the factory profile identifier to saved/exported calibration data and validation for optional SFP label and hitbox coordinates.
- Confirmed Save Profile saves without closing, while Done validates, saves, and exits calibration mode.
- Reduced fonts strictly within the Calibration tool UI by 1 px; rendered switch labels and dashboard text are unchanged.

## v1.8.15

- Added independent calibration targets for SFP/uplink labels so their visible text can be moved separately from the SFP port box.
- Renamed the RJ45 calibration part from `Ports`/`Hitbox centre` to `Port box`.
- Added `Entire Port` selection, moving the port box, link/speed LED, and activity LED together while resizing only the port box.
- Made the Calibration `Position and Size` section expanded by default.

## v1.8.14

- Corrected exact-model faceplate resolution for Cisco Catalyst 2960S and 2960X devices.
- WS-C2960S-48FPD-L and WS-C2960X-48FPD-L now enforce the 48 RJ45 / 2 SFP faceplate and two-uplink calibration geometry.
- WS-C2960X-24PS-L now enforces the 24 RJ45 / 4 SFP faceplate and matching calibration geometry.
- Exact switch models can now be detected from Home Assistant model sensors when the card configuration does not include the model explicitly.
- Renamed faceplate dropdown labels to clear generic port/uplink descriptions for all four bundled layouts.
- Saved profiles with obsolete faceplate or uplink geometry are resolved to the authoritative exact-model factory layout while preserving user status-box, logo, stack and management settings.

# Switch Vision v1.8.11

- Migrated the packaged Discovery source and release folder from `addons/` to `local_apps/`.
- Updated active installation, requirements, troubleshooting, building, workflow, and field-reference documentation to Home Assistant app terminology.
- Updated new installation paths from `/addons/switch_vision_discovery/` to `/local_apps/switch_vision_discovery/`.
- Documented the Samba share migration from `addons`/`addon_configs` to `local_apps`/`app_configs`, while noting the temporary legacy aliases.
- Kept the existing Supervisor `/addons` API routes unchanged because they are API endpoints rather than filesystem or Samba paths.
- Added app-named release-manifest fields while retaining legacy add-on field names for compatibility.

## v1.8.9

- Added model-specific calibration geometry for Cisco WS-C2960X-24PS-L with 24 RJ45 ports and four Gigabit SFP uplinks.
- Added model-specific calibration geometry for Cisco WS-C2960S-48FPD-L with 48 RJ45 ports and two 10G SFP+ uplinks.
- Connected both exact models to their bundled faceplates and factory calibration profiles.
- Removed the confirmation prompt when removing a visual RJ45 port or uplink in Calibration.

## 1.8.5

## v1.8.5

- Replaced the bundled faceplate set with the single `faceplates/switch-vision-default-faceplate.png` asset and made it the default for shipped profiles and exact-model recommendations.
- Removed the previous `sv-dark.png` and `sv-light.png` bundled faceplates.
- Replaced `logos/1996-cisco-logo.svg` with the supplied updated artwork.

- Fixed multi-device Discovery report isolation and added exact WS-C3560CG model recognition so one walk cannot inherit another device's model/profile result.
- Corrected Support My Switch manifest file counts to include the complete archive payload, including generated metadata.
- Added `PASS WITH PRIVACY WARNINGS` when interface descriptions or VLAN labels remain visible because their masking options were disabled.


- Allow individual SFP/uplink targets to be removed in interactive calibration.

# Switch Vision Changelog

## v1.9.67 — Switch Vision Hub cleanup

- Renamed the Discovery landing page to **Switch Vision Hub** and removed its introductory subtitle.
- Simplified the landing-page cards and wording for Discovery, Devices, Support My Switch, detected-device information, and configuration import/export.
- Removed duplicate Dashboard & Calibration and Installer launch cards because both already have dedicated Home Assistant sidebar entries.
- Renamed and simplified the Switch Vision, Discovery, and SNMP2MQTT settings cards.
- Contains no intentional changes to Discovery execution, generated files, profiles, sensors, calibration, resets, dashboards, or faceplates.

## v1.9.66 — Final UI polish

- Changed the add/edit Save reminder to a larger warning-triangle line with extra spacing and a matching trailing warning symbol.
- Made **Generated SNMP2MQTT YAML** a collapsible section matching **Generated Card YAML**.
- Contains no intentional changes to Discovery generation, profiles, sensors, calibration, resets, dashboards, or faceplates.

## v1.9.65 — Final stability audit

- Made optional logo and faceplate folder failures non-fatal so filesystem permission or transient storage problems cannot prevent the integration or native panel loading.
- Made generated-dashboard metadata races non-fatal; successfully parsed cards remain available if the file is replaced between reading and metadata lookup.
- Made shared UI-preference write failures log a warning instead of aborting integration setup.
- Added build-time README resource-version synchronisation and refreshed stale current-release documentation.
- Fixed checksum manifests to reference the release ZIP in its actual `Releases/` path, allowing direct `sha256sum -c` verification from the source root.
- Re-ran Python, JavaScript, shell, JSON, YAML, archive, version-propagation, and reproducible-build validation without changing established feature behaviour.

## v1.8.2

- Fixed Juniper EX3300 model recognition in the frontend by reading the Discovery-generated `switch_model` field.
- Juniper EX3300 uplink overlays now render as `TE1`, `TE2`, `TE3`, and `TE4` instead of the generic Cisco labels.
- Discovery-generated cards now include an explicit SFP status entity template so TE uplink link LEDs bind directly to `sensor.<prefix>_sfp_10g_<port>_status`.
- Retained all existing Cisco uplink labels and legacy entity fallbacks.
- Update scope: replace the custom component and Discovery add-on, rebuild/reinstall Discovery, restart Home Assistant Core and Discovery, then run Discovery again.

## v1.8.1

- Added Juniper EX3300-48P physical uplink polling for `xe-0/1/0` through `xe-0/1/3`, with `ge-0/1/N` accepted as the 1G alternate name for the same cages.
- Mapped Juniper uplinks to Switch Vision SFP entities as TE1 through TE4, including link status and 64-bit RX/TX traffic counters.
- Added Juniper-specific faceplate labels `TE1`, `TE2`, `TE3`, and `TE4` while retaining Cisco uplink labels for Cisco models.
- Promoted EX3300-48P uplink validation to confirmed from real-hardware TE1 / `xe-0/1/0` 10G link evidence. Virtual Chassis validation remains pending, so the model remains Experimental overall.
- Update scope: replace the custom component and Discovery add-on, rebuild/reinstall Discovery, restart Home Assistant Core and Discovery, then run Discovery again.

## v1.8.0 Gold

- Promoted the fully validated v1.7.53 codebase to the new **Gold / Stable** baseline as v1.8.0.
- Updated all runtime versions, manifests, examples, installation paths, supported-device outputs, Gold documents, and current-release documentation.
- Locked in the final status-box layout: independent Status Box 1, Status Box 2, and Port Status Box controls; title-free rows; IntelOne 16 px bold defaults; and VENDOR/UPTIME defaults for Status Box 2.
- Locked in Juniper EX3300-48P exact-model registry matching, copper-port mapping, PoE/system telemetry, and per-port static Q-BRIDGE VLAN membership display.
- Locked in Support My Switch registry enrichment and explicit privacy-audit enforcement metadata.
- Retained Cisco Catalyst 3650 exact models as Confirmed; Cisco 2960S/2960X and Juniper EX3300-48P remain Experimental pending outstanding uplink or Virtual Chassis validation.
- Confirmed `CHANGELOG.md` as the sole version-history document; historical `RELEASE_NOTES*` files remain excluded.
- Gold update scope: perform a clean complete replacement of the release components, rebuild/reinstall Discovery, restart Home Assistant Core, run Discovery, and refresh the browser.

## 1.7.53

- Cleaned up Support My Switch privacy metadata so disabled legacy residual-audit fields are emitted as `null` rather than misleading zero values.
- Updated the contribution report generator to read authoritative `audit_categories` metadata.
- Increased the sanitization report schema to version 7 and added regression coverage.

## v1.7.52

- Fixed Support My Switch registry enrichment by synchronising the authoritative supported-device registry into the Discovery add-on at build time.
- Juniper `Juniper EX3300-48P` contribution records now resolve to `EX3300-48P` with `registry_match: true` and Experimental metadata.
- Added explicit JSON audit metadata for disabled privacy categories using `enforced: false` and `remaining: null`.
- Bumped the sanitization report schema to version 6.

## v1.7.51

- Unified Juniper model normalisation across Discovery, diagnostics and Support My Switch contribution summaries, so `Juniper EX3300-48P` matches the exact `EX3300-48P` experimental registry entry.
- Contribution bundles now re-enrich privacy-processed capability files with the shared supported-device registry lookup before generating device summaries.
- Privacy reports now state `not enforced - masking disabled` for categories whose masking option was disabled instead of incorrectly reporting zero remaining values.
- Added `build.py --bump patch|minor|major` while retaining explicit `-v/--version` builds.
- Removed accumulated historical `RELEASE_NOTES*` files; version history is maintained in `CHANGELOG.md`.
- Update scope: replace `/addons/switch_vision_discovery/`, rebuild/reinstall the local add-on, and restart Discovery. Home Assistant Core and SNMP2MQTT do not need restarting.

## v1.7.49

- Moved the shared status value column 10 px further left in Status Box 1, Status Box 2, and the Port Status Box.
- Preserved box geometry, label positions, row spacing, and individual field calibration offsets.
- Update scope: replace `/config/custom_components/switch_vision/`, restart Home Assistant Core, then refresh the browser.

## v1.7.48

- Moved the shared status value column another 5 px left for Status Box 1, Status Box 2 and the Port Status Box.
- Fixed fresh/default profiles so Status Box 2 visibly defaults to VENDOR and UPTIME.
- Fixed Reset All so Status Box 2 restores VENDOR and UPTIME in that order.
- Update scope: replace `/config/custom_components/switch_vision/`, restart Home Assistant Core, then refresh the browser.

## v1.7.47

- Added a dedicated **Port Status Box** field-control row beneath Status Box 2, so selecting a port no longer replaces the Status Box 1 field controls.
- Removed the obsolete MODE item from port status fields and legacy MODE entries are ignored.
- Status Box 2 now defaults to VENDOR and UPTIME, in that order.
- Moved the shared status-field value column 40 px further left for Status Box 1, Status Box 2 and selected-port details.
- Update scope: replace `/config/custom_components/switch_vision/`, restart Home Assistant Core, then refresh the browser.

## 1.7.46

- Fixed Reset All so both status boxes explicitly clear legacy row offsets.
- Restored the canonical 88 px label-to-value column spacing.
- Reset defaults are Custom / IntelOne, 16 px and bold.

## v1.7.45

- Set the default font for both status boxes to Custom / IntelOne, 16 px, bold.
- Standardised the default label-to-value column spacing at 88 px from label start to value start.
- Existing saved profiles retain their font settings and individual field offsets.
- Reset All now restores the new shared status-box defaults.

## 1.7.44

- Moved the shared status-box value column further left to reduce the label-to-value gap in both Status Box 1 and Status Box 2.
- Preserved box geometry, outer padding, row spacing, truncation behaviour and independent field calibration offsets.

### Update Scope

Replace:

- `/config/custom_components/switch_vision/`

Then restart Home Assistant Core and refresh the browser. Discovery and SNMP2MQTT do not need restarting.

## 1.7.43

- Removed the confirmation prompt from Reset all; the visual reset now runs immediately.
- Reduced the horizontal gap between status-field labels and values in both Status Box 1 and Status Box 2.
- Preserved box geometry, outer padding, vertical layout, field ordering and independent field calibration offsets.

### Update Scope

Replace:

- `/config/custom_components/switch_vision/`

Then restart Home Assistant Core and refresh the browser. Discovery and SNMP2MQTT do not need restarting.

## 1.7.42

- Fixed Status Box 1 row rendering and field-target alignment.
- Added sixth-row status-field targets.
- Restored Reset all with confirmation and visual-only scope.

## v1.7.41

- Fixed Status Box 2 field calibration targets so label/value markers align with the rendered text.
- Status Box 2 field X/Y nudges now move the live text, not only the calibration overlay.
- Status Box 1 and Status Box 2 field targets now use the same coordinate transform as the renderer.
- Removed the irrelevant `LED centre` part option from status-field targets; they now show `Field position`.
- Removed the deferred `Reset all` control and action.
- Added Reset target support for Status Box 2 field groups and individual fields.
- Removed legacy title points from both status-box field maps while preserving compatibility with older profiles.
- MODE remains excluded from calibration targets and exports.

### Update Scope

Replace:

- `/config/custom_components/switch_vision/`

Then restart Home Assistant Core and refresh the browser. Discovery and SNMP2MQTT do not need restarting.

## v1.7.40

- Added the 1984, 1996, and 2016 Cisco SVG logo variants to the bundled logo library.
- Confirmed obsolete Status Box 1/2 title targets and the MODE calibration target remain excluded.
- Existing saved legacy title or MODE offsets remain harmlessly ignored.

### Update Scope

Replace the logo folder only:

- `/config/www/switch-vision/logos/`

Then refresh the browser. No Home Assistant Core, Discovery, or SNMP2MQTT restart is required.

## v1.7.39

- Added the Q-BRIDGE static VLAN table (`1.3.6.1.2.1.17.7.1.4.3`) to targeted SNMP walks.
- Juniper VLAN membership is now decoded for every mapped port using bridge-port → ifIndex → physical-interface correlation.
- Juniper ports render one VLAN as `VLAN n`, multiple memberships as `VLANS n, n, ...`, and fall back to `VLAN TRUNK` when trunking is known but membership is unavailable.
- Removed obsolete Status Box 1 and Status Box 2 title calibration targets. Legacy saved title offsets remain harmlessly ignored.
- MODE remains excluded from status LED calibration targets and export data.

### Update Scope

Replace both:

- `/addons/switch_vision_discovery/`
- `/config/custom_components/switch_vision/`

Then rebuild/reinstall and restart Discovery, restart Home Assistant Core, run Discovery again, and refresh the browser. SNMP2MQTT does not need restarting unless regenerated configuration changes are applied.

## 1.7.38

- Fixed Juniper EX3300-48P supported-device registry matching when Discovery reports the vendor-prefixed model name `Juniper EX3300-48P`.
- Kept the authoritative exact model entry as `EX3300-48P` while normalising the vendor prefix during registry lookup.
- The Juniper contribution now reports `registry_match: true`, the `juniper-ex3300-48p` mapping profile, and Experimental validation metadata.
- Update scope: replace `/addons/switch_vision_discovery/`, rebuild or reinstall the local add-on, and restart Discovery. Home Assistant Core and SNMP2MQTT do not need restarting.

## 1.7.37

- Added individual calibration targets for every Status Box 2 field, matching Status Box 1 target support.
- Added a separate Status Box 2 field target group and an All Status Box 2 fields quick-selection button.
- Status Box 2 field targets now show calibration rings and labels and can be nudged independently without moving or resizing the box.
- Preserved Status Box 1 behaviour, status-box dimensions, field visibility, ordering, and styling.
- Update scope: replace `/config/custom_components/switch_vision/`, restart Home Assistant Core, then refresh the browser.

## 1.7.36

- Moved Status Box 2 label and value content 10 px further left.
- Preserved Status Box 1 padding, calibrated box dimensions, vertical layout, and right edge.
- Update scope: replace `/config/custom_components/switch_vision/`, restart Home Assistant Core, then refresh the browser.

# Switch Vision Changelog

## v1.9.67 — Switch Vision Hub cleanup

- Renamed the Discovery landing page to **Switch Vision Hub** and removed its introductory subtitle.
- Simplified the landing-page cards and wording for Discovery, Devices, Support My Switch, detected-device information, and configuration import/export.
- Removed duplicate Dashboard & Calibration and Installer launch cards because both already have dedicated Home Assistant sidebar entries.
- Renamed and simplified the Switch Vision, Discovery, and SNMP2MQTT settings cards.
- Contains no intentional changes to Discovery execution, generated files, profiles, sensors, calibration, resets, dashboards, or faceplates.

## v1.9.66 — Final UI polish

- Changed the add/edit Save reminder to a larger warning-triangle line with extra spacing and a matching trailing warning symbol.
- Made **Generated SNMP2MQTT YAML** a collapsible section matching **Generated Card YAML**.
- Contains no intentional changes to Discovery generation, profiles, sensors, calibration, resets, dashboards, or faceplates.

## v1.9.65 — Final stability audit

- Made optional logo and faceplate folder failures non-fatal so filesystem permission or transient storage problems cannot prevent the integration or native panel loading.
- Made generated-dashboard metadata races non-fatal; successfully parsed cards remain available if the file is replaced between reading and metadata lookup.
- Made shared UI-preference write failures log a warning instead of aborting integration setup.
- Added build-time README resource-version synchronisation and refreshed stale current-release documentation.
- Fixed checksum manifests to reference the release ZIP in its actual `Releases/` path, allowing direct `sha256sum -c` verification from the source root.
- Re-ran Python, JavaScript, shell, JSON, YAML, archive, version-propagation, and reproducible-build validation without changing established feature behaviour.

## v1.7.35

- Reduced the left content buffer in Status Box 1 by 5px.
- Applied the same horizontal inset to Status Box 2 so both boxes share matching label and value column margins.
- Preserved calibrated box position, width, height, vertical layout, and right edge.
- Update scope: replace `/config/custom_components/switch_vision/`, restart Home Assistant Core, then refresh the browser.

## v1.7.34

- Removed automatic Status Box 2 height changes introduced in v1.7.33.
- Status Box 2 now always keeps its calibrated width and height.
- Showing, hiding, or reordering fields changes only the content inside the box.
- Rows that do not fit remain clipped by the existing in-box safety rules rather than resizing the panel.

## v1.7.33

- Tightened live Status Box 2 height so its padding and buffer better match Status Box 1.
- Old title-era box heights no longer leave oversized empty space around compact Status Box 2 content.
- Preserved saved calibration profiles while applying the compact height only at render time.

## v1.7.32

- Standardised the horizontal two-column layout for every field in Status Box 1 and Status Box 2.
- All field labels now share one fixed label column.
- All field values now share one fixed, left-aligned value column.
- Short values such as UPTIME no longer appear indented because of right-aligned text width.
- Hidden, reordered, switch, port, and SFP fields all use the same alignment rules.
- Preserved compatibility with existing saved calibration profiles.

## v1.7.31 Gold

- Standardised the vertical layout of every visible field in Status Box 1 and Status Box 2.
- Visible rows now use one compact, evenly spaced grid based on their displayed order.
- Hidden and reordered fields no longer leave uneven gaps.
- Preserved calibrated horizontal label/value positions and existing saved-profile compatibility.

## v1.7.30 Gold

- Designated v1.7.30 as the new **Gold / Stable** baseline.
- Added **Smoke** as a separate status-box background selection for Status Box 1 and Status Box 2.
- **Clear** remains fully transparent.
- **Smoke** restores the previous subtle dim using `rgba(0,0,0,.06)`.
- Existing saved profiles using the old subtle-dim value now appear as **Smoke** in calibration.
- Finalised title-free Status Box 1 and Status Box 2 rendering and calibration controls.
- Finalised blue STACK LED behaviour for every confirmed stack member, with no LED for standalone or unconfirmed stack state.
- Finalised dynamic Juniper EX3300-48P zero-based port mapping and VLAN membership display.
- Kept Cisco trunk presentation unchanged.
- Marked all non-Catalyst-3650 models **Experimental** pending SFP/uplink testing.
- Added Gold packaging validation that excludes `__pycache__/`, `*.pyc`, and `*.pyo`.

## v1.7.29

- Changed the **Clear** status-box colour to true transparency for Status Box 1 and Status Box 2.
- Existing profiles that used the previous `rgba(0,0,0,.06)` Clear value are rendered as fully transparent automatically.
- Border, text, and non-clear colour choices are unchanged.

## v1.7.28

- Removed the rendered title and divider from both Status Box 1 and Status Box 2.
- Shifted enabled rows upward in both boxes without rewriting saved calibration coordinates.
- Removed all title-specific calibration controls for both boxes: title source, title field, custom title, and title size.
- Preserved legacy title keys in saved profiles for backward compatibility; they are now ignored at runtime.

## v1.7.27

- Fixed the blue STACK LED so every confirmed stack member, including member 1, illuminates consistently.
- Discovery now emits `stack_enabled: true` for all cards in a confirmed multi-member stack.

## v1.7.26

- Moved the default Status Box 2 position 5 pixels to the right.
- Added a blue STACK LED for switches explicitly configured as stack members.
- Keeps the STACK LED off for standalone switches, unknown stack state, and unconfirmed membership.
- Preserved saved calibration-profile coordinates; the position change applies only to defaults and new profiles.

## v1.7.25

- Removed the rendered title and divider from Status Box 2.
- Shifted Status Box 2 values upward while preserving existing calibration profiles.
- Restored the Status Box 2 labels in the calibration tool.
- Left Status Box 1 and vendor-specific VLAN display unchanged.

## v1.7.24

- Juniper access ports display a single VLAN value.
- Juniper trunk ports display the complete discovered VLAN membership list under `VLANS`.
- Removed the separate Juniper port-mode and native-VLAN rows from selected-port presentation.
- Cisco `TRUNK` display remains unchanged.

## v1.7.23

Maintenance cleanup release.

- Made `src/js/switch-vision.js` the single authoritative card source and added byte-for-byte build validation for the custom-component copy.
- Synchronised source manifest version, release name, and cache-busting resource metadata.
- Replaced stale embedded calibration generator metadata with the live `SV_VERSION`.
- Added automated Juniper VLAN mode and release-integrity regression tests.
- Normalised changelog headings and release order.
- Preserved existing plural asset paths for backwards compatibility; no calibration-profile migration is required.

## v1.7.22

- Added dynamic Juniper trunk/access classification from Q-BRIDGE VLAN membership bitmaps.
- Port details now show MODE plus the accurate native VLAN.
- Removed redundant Status Box 2 calibration headings.
- Native panel card JavaScript is now served by the custom component to prevent stale frontend versions.

## v1.7.21

- Fixed Juniper logical-interface index parsing when `ifName` values contain a dot, such as `ge-0/0/42.0`.
- Dynamic BRIDGE-MIB/Q-BRIDGE-MIB joins now emit per-port VLAN/PVID sensors instead of resolving logical indexes as zero.
- Added generated-YAML diagnostics for logical interfaces, bridge mappings, PVID rows, and successful joins.

## v1.7.20

- Added `dot1dBasePortIfIndex` and `dot1qPvid` to targeted live SNMP walks so dynamic Juniper per-port VLAN sensors have the source tables required during generation.
- Replaced the hard-coded targeted-walk progress total with a count derived from the configured OID list.
- Keeps VLAN discovery dynamic; no interface-range names, port numbers, bridge indexes, or VLAN IDs are hard-coded.

## v1.7.19

- Added dynamic Juniper per-port VLAN/PVID generation through BRIDGE-MIB and Q-BRIDGE-MIB table correlation.
- VLAN discovery is independent of interface-range names and contains no fixed port, bridge-index, or VLAN mappings.

## v1.7.18

- Fixed Juniper zero-based port mapping in selected-port details so the entity offset is applied exactly once.
- Visual label 42 now resolves to `sensor.sw10_port_42_*` instead of the previous port 41/43 mismatch.
- Link, speed, VLAN, alias and selected-port summary now use the same resolved Juniper entity number as the LEDs and traffic counters.

## v1.7.17

- Fixed the frontend port-number overlay so `port_label_offset` is applied when labels are drawn.
- Juniper EX3300-48P now displays labels 0-47 while retaining zero-based entity mapping.

## v1.7.16

- Added Juniper EX3300-48P zero-based port-number overlays: calibrated slots 1–48 now display labels 0–47.
- Kept Juniper entity lookup aligned with the same zero-based numbering, so label, click target, status, activity, RX/TX and details all use the matching port.
- Cisco and other one-based models remain unchanged.

## v1.7.15

- Fixed Calibration failing to open after the v1.7.14 status-panel change.
- Status Box 2 is now strictly switch-summary only and no longer renders selected-port or selected-SFP details.
- Calibration sections start collapsed for each new Calibration session.
- Preserved Juniper visual ports 1–48 with zero-based entity lookup.

## v1.7.14

- Status Box 2 now remains a switch-summary box and no longer switches to port or SFP details when a front-panel interface is selected.
- Port and SFP selection details are displayed only in Status Box 1.
- Restored visible copper-port numbering to 1-48 for all 48-port faceplates.
- Juniper EX3300 cards retain `port_entity_offset: -1` for correct SNMP entity mapping without changing the displayed port labels.

## v1.7.13

- Fixed Status Box 2 rows being discarded when legacy value anchors sat a few pixels outside the compact box width.
- All Calibration tool sections now open collapsed at the start of every calibration session.
- Added a label mask for remapped port numbering so zero-based Juniper labels 0-47 replace the baked 1-48 faceplate numbers cleanly.
- Clarified Juniper link/activity placement by keeping entity, displayed label, selection and details mapping aligned.

## v1.7.9

- Fixed authoritative version propagation across all packaged runtime components and added strict mixed-version build validation.
- Added walk-aware Juniper EX3300-48P CPU, temperature, memory, fan and power-supply health discovery using `jnxOperatingTable`.
- Kept unsupported Juniper health values absent rather than generating invalid OIDs.

## v1.7.8

- Fixed zero-based Juniper port detail, traffic and activity lookups.
- Selected Juniper ports now show the correct faceplate number in the status panel.
- Added the optional bundled Juniper logo at `logos/juniper.svg`.


- Fixed Juniper EX3300-48P SNMP2MQTT generation so the 48 base `ge-0/0/N` interfaces create live port entities.
- Preserved zero-based labels 0 through 47 and excluded `.0` logical interfaces.
- Corrected generated device metadata from Cisco / unknown to Juniper / EX3300-48P.

## v1.7.7



## v1.7.6

- Corrected Juniper EX3300-48P copper-port numbering to match the physical zero-based labels 0 through 47.
- Added per-card port label and entity offsets so calibrated positions 1 through 48 map to Juniper interfaces ge-0/0/0 through ge-0/0/47.
- Port ge-0/0/42 now drives the faceplate position labelled 42.

# Changelog

## v1.7.5

### Added

- Added experimental Juniper EX3300-48P exact-model detection and front-panel mapping.
- Mapped ge-0/0/0 through ge-0/0/47 as 48 physical RJ45 ports.
- Deduplicated the four shared ge-0/1/N and xe-0/1/N uplink cages.
- Excluded logical unit, management, and VLAN interfaces from front-panel totals.

## v1.7.4

### Fixed

- Create the Discovery Web log directory and file before use.
- Prevent clean-install Discovery failures when `/share/switch_vision/discovery-web.log` does not yet exist.

# Switch Vision changelog

## v1.7.3

- Added local Home Assistant brand images using the bundled Switch Vision logo, removing the missing integration icon on Home Assistant 2026.3 and later.
- Added the supplied Switch Vision SVG as a dedicated custom sidebar icon.
- Unified native panel version reporting so the top-right badge reads the backend runtime version instead of stale v1.6.0 text.
- Added runtime and asset revision metadata to the native sidebar panel and its Advanced diagnostics.
- Updated the build process to patch frontend and backend panel version constants automatically in future releases.

## v1.7.1

- Made the Switch Vision logo the vendor-neutral default for new profiles.
- Moved bundled logos into `logos/` and retained Cisco as optional `logos/cisco.svg`.
- Removed the obsolete `images/` directory.
- Renamed bundled faceplates to `faceplates/sv-dark.png` and `faceplates/sv-light.png`.
- Updated calibration, layout, discovery registry, and runtime asset fallbacks to the new paths.
- Added standard-MIB sensor discovery for unfamiliar and non-Cisco switches.
- Added major-vendor discovery packs for Juniper, HPE/Aruba, Dell, Extreme Networks, Ruckus/Brocade, MikroTik, Ubiquiti, NETGEAR, and Huawei.
- Added vendor-specific symbolic sensor matching and enterprise-OID review candidates alongside the standard-MIB scanner.

## v1.6.0

- Added a Switch Vision integration option to show or hide Calibration buttons on all cards in the automatic generated dashboard.
- The option defaults to enabled and applies without rewriting generated YAML.
- Manual YAML cards continue to use their own `calibration_button` value.
- The native dashboard detects the option change and rebuilds its cards automatically.

## v1.5.5

- Compact one-line native dashboard header.
- Automatic generated-dashboard refresh when Discovery updates the YAML.
- Versioned frontend module URLs for reliable cache invalidation.
- Rewritten current documentation for the zero-copy native dashboard workflow.
- Documented automatic SNMP2MQTT handoff, sidebar visibility, live polling, dark faceplate defaults, cache recovery, and the manual YAML fallback.
- Removed obsolete active-file installation and normal-workflow copy/paste instructions from current documentation.

## v1.5.4

- Fixed Supervisor authorization for automatic SNMP2MQTT start/restart after Discovery.
- Added robust Supervisor token detection.
- Added a continuously ticking elapsed timer while Discovery is running.
- Preserved v1.5.3 live polling behaviour.

## v1.5.3

- Added automatic Discovery Web UI polling.
- Refreshes every second while Discovery or Support My Switch work is running.
- Refreshes every five seconds while idle.
- Pauses polling while the browser tab is hidden.
- Refreshes immediately when the tab becomes visible or receives focus.
- Keeps Discovery status, Debug output, Devices, Diagnostics, generated YAML status, and SNMP2MQTT results current without manual page refreshes.
- No parser, generator, native dashboard, calibration, custom-component, or SNMP2MQTT restart behaviour changes.

## v1.5.2 — Optional native sidebar dashboard

- Added a Switch Vision integration options screen under **Settings → Devices & services → Switch Vision → Configure**.
- Added **Show Switch Vision dashboard in sidebar**, enabled by default.
- Turning the option off hides only the dedicated native dashboard sidebar entry.
- Manual Lovelace cards, generated dashboard YAML, Calibration, Discovery, Diagnostics, Support My Switch and SNMP2MQTT remain available when the sidebar panel is hidden.
- Existing YAML-based installations automatically gain a Switch Vision config entry and retain their current calibration and generated-dashboard paths.
- Option changes reload the panel immediately without requiring another Home Assistant restart.

## v1.5.1 — Seamless SNMP2MQTT activation

- Added automatic start/restart of the Switch Vision SNMP2MQTT add-on after successful Discovery.
- Validate that the current Discovery run updated `generated-snmp2mqtt.yaml` before taking action.
- Discover the installed SNMP2MQTT add-on slug through the Supervisor API.
- Restart the add-on when already running, or start it when stopped.
- Report missing add-ons and Supervisor failures as warnings without failing Discovery.
- Added SNMP2MQTT action status to the minimal Discovery status window and Debug output.
- Kept the existing generated-YAML import option as the authoritative SNMP2MQTT configuration path.

## v1.5.0 — Automatic native dashboard

- Promoted the successful native Home Assistant sidebar dashboard to a major supported feature.
- Added zero-copy dashboard loading from Discovery's generated card configuration.
- Removed prototype/test wording and polished the panel for everyday use.
- Added a compact card count and last-generated timestamp.
- Moved technical source details and module reload controls under Advanced.
- Preserved generated dashboard YAML as the permanent manual fallback.
- Kept existing Lovelace cards, Discovery parsing and SNMP2MQTT behaviour unchanged.

## v1.4.17 — Experimental native dashboard prototype

- Added an experimental native Switch Vision sidebar panel registered by the custom component.
- The panel reads Discovery's generated dashboard-card YAML and renders live Switch Vision cards automatically.
- Preserved the manual generated-YAML workflow as an unchanged fallback.
- Added clear prototype/error states so a panel failure does not affect Discovery or manual cards.
- Simplified SNMP2MQTT generated-YAML controls to validation, preview and download only.
- Removed the duplicate active-file install/backup workflow introduced in v1.4.16.
- Home Assistant Core restart is required because `custom_components/switch_vision` changed.

## v1.4.16

- Added a safe **Use generated SNMP2MQTT YAML** workflow to the persistent Discovery Web UI.
- Added YAML preview, validation, download, manual install and restore actions.
- Added an optional setting to install valid generated YAML automatically after a successful Discovery run.
- Active YAML is installed to `/share/switch_vision/snmp2mqtt.yaml`.
- Existing active YAML is backed up before every replacement under `/share/switch_vision/backups/snmp2mqtt/`.
- Invalid, empty or hostless generated YAML is rejected before installation.
- Switch Vision does not automatically restart the SNMP2MQTT add-on.
- Discovery parsing, dashboard generation and supported-device behaviour are unchanged.

## v1.4.15

- Made Auto-detect the migration-safe default for existing and new switch rows.
- Added distinct Idle, Preparing, Running, Complete and Failed Discovery states.
- Prevented the guided workflow from looking active before real Discovery work starts.
- Renamed the first step to `Validating configured switches`.
- Kept parser, generator and compatibility-override behaviour unchanged.

## v1.4.14

- Added a per-switch **Switch Model** dropdown to Discovery configuration.
- Added Auto-detect plus exact registered model choices.
- Preserved detected, selected override, and effective model values separately.
- Added experimental compatibility warnings to reports and generated cards.
- Included override metadata in capability JSON, diagnostics, and Support My Switch summaries.
- Kept the real detected model authoritative for support status.

## v1.4.13

- Added default minimal and optional debug output modes to Discovery.
- Retained the requested technical stage names for SNMP walks and generated YAML.
- Made the graphite 48-port faceplate the default/recommended 3650 faceplate.
- Made Calibration **Done** validate and save the active profile automatically.

## v1.4.12

- Simplified the persistent Discovery Web UI around four clear destinations: Discovery, Devices, Support My Switch and Diagnostics.
- Added a clean landing page that shows only the current high-level status and primary actions.
- Added a guided six-step Discovery progress view while keeping raw log output inside an Advanced details section.
- Added a Devices results page with compact per-switch discovery, support, port and generated-configuration summaries.
- Moved detailed registry, validation, path and generated-file information behind Diagnostics or View Details.
- Kept the persistent idle/ready lifecycle, duplicate-run protection, parser behaviour and SNMP2MQTT/dashboard generation unchanged.

## v1.4.11

- Updated the generated dashboard-card YAML to include `switch_model` automatically.
- The exact SKU is read from each switch's generated capability JSON.
- Every generated member card in a stack receives the verified exact model.
- Recommended Setup now appears without manually editing generated card YAML.
- Left dashboard rendering, calibration behaviour, parsing, registry matching and SNMP2MQTT generation unchanged.

## v1.4.10

- Added exact-model faceplate and calibration recommendations.
- Added read-only compatibility checks in Interactive Calibration.
- Added a user-triggered Apply Recommended Setup action with no automatic overwrite.
- Marked 2960 visual assets as pending until model-specific faceplates/profiles are supplied.

## v1.4.9

- Fixed **Copy Diagnostics** in Home Assistant Ingress and HTTP browser contexts.
- Added a legacy clipboard fallback when `navigator.clipboard.writeText()` is unavailable or denied.
- Added clearer clipboard and diagnostics-download error reporting.
- Left Discovery, registry, dashboard and SNMP2MQTT behaviour unchanged.

## v1.4.8

- Added a read-only Diagnostics page to the persistent Discovery Web UI.
- Added installation and service checks for the Discovery add-on, exact-model registry, generated SNMP2MQTT YAML, generated dashboard YAML and contribution workflow.
- Added per-device diagnostics from capability JSON, including exact model, registry state, interface counts, mapping/calibration profiles and component-level validation.
- Added clear warning/error messages for missing registry data, missing or stale generated files and unavailable capability data.
- Added **Refresh Diagnostics**, **Copy Diagnostics**, **Download Diagnostics Report** and **Run Discovery** actions.
- Kept parser, registry matching and SNMP2MQTT generation behaviour unchanged.

## v1.4.7

- Changed the Discovery add-on into a persistent idle/ready service.
- The Home Assistant Ingress Web UI now starts immediately with the add-on and remains available between Discovery runs.
- Added a **Run Discovery** control and live Discovery status/log output to the Support My Switch Web UI.
- Discovery now runs as a child job without stopping or replacing the Web UI service.
- Changed the add-on boot setting to `auto` so **Open Web UI** remains available after Home Assistant starts.
- Kept the existing parser, registry lookup, contribution and SNMP2MQTT generation behaviour unchanged inside each Discovery run.

## v1.4.6

- Added downloadable calibration profile JSON files.
- Added profile JSON import with validation and preview.
- Added schema version 1 to exported and factory profiles.
- Added canvas, coordinate and component-count compatibility checks.
- Added safe save-as and overwrite confirmation for imported profiles.
- Kept Discovery, parser and SNMP2MQTT behaviour unchanged.

## v1.4.5

- Added a persistent **Back to Home Assistant** button to the main Support My Switch landing page.
- Kept the shorter **Back** behaviour on contribution progress and result views.
- Added safe browser-history and Home Assistant root fallbacks for Ingress navigation.
- No parser, SNMP2MQTT, dashboard JavaScript, or custom component behaviour changed.

## v1.4.3

- Connected the exact-model supported-device registry to Discovery as informational metadata.
- Added component-level validation fields for model detection, RJ45, PoE, system sensors, uplinks, and stack support.
- Added registry results to discovery reports, capability JSON, and Support My Switch summaries.
- Kept all 2960 variants experimental with uplink validation pending.
- Parser and SNMP2MQTT generator behaviour remain unchanged.

## v1.4.2

- Added exact experimental registry entries for `WS-C2960X-48FPD-L`, `WS-C2960X-24PS-L` and `WS-C2960S-48FPD-L` from real test-rack contributions.
- Revalidated exact confirmed entries for `WS-C3650-48PD-E` and `WS-C3650-48PD-L` using production and test-rack contributions.
- Fixed Discovery model selection so a complete `-E` or `-L` SKU is not overwritten by a shorter chassis model string.
- Updated Cisco vendor knowledge and regenerated supported-device documentation.

## v1.4.1

- Removed the generic `WS-C3650-48PD` supported-device entry.
- Added exact confirmed entries for `WS-C3650-48PD-L` and `WS-C3650-48PD-E`.
- Recorded the exact 48 RJ45 + 2 Gigabit SFP + 2 10G SFP+ front-panel layout.
- Recorded tested IOS version 16.12.14 for both exact models.
- Regenerated Markdown and phpBB supported-device documentation.

## v1.4.0

- Started the exact-model supported-device registry.
- Added confirmed support entry for `WS-C3650-48PD` only.
- Added four controlled support statuses: detected, experimental, community validated and confirmed.
- Added build-time registry validation that rejects aliases and duplicate exact models.
- Added generated Markdown and phpBB supported-device documents.
- Preserved v1.3.15 as the protected Gold baseline.

## v1.3.15

- Replaced the shipped optional dark faceplate with the cooler graphite version.
- Removed the bronze-tinted optional dark plate from the package.
- Kept the same optional faceplate filename, dropdown label and shared calibration profile.
- No calibration or custom component changes were required.

## v1.3.14

- Added `switch-master-dark.png` as the first shipped optional faceplate.
- Added the dropdown label `Switch Vision Cisco 48 Port — Dark`.
- Reused `default_cisco_48_port` because the optional faceplate geometry is unchanged.
- Kept the current default faceplate unchanged.
- Added friendly dropdown labels for known shipped faceplates.
- Added automatic readable labels for user-supplied faceplate and logo filenames.

## v1.3.13

- Updated `default_cisco_48_port` with the latest Status Box 1 and Status Box 2 positions.
- Moved Status Box 1 from Y 37 to Y 30.
- Moved Status Box 2 from Y 20 to Y 25.
- Updated embedded factory calibration metadata for the four-uplink layout.

## v1.3.12

- Added the new `default_cisco_48_port` factory calibration profile.
- Replaced the default faceplate with the new 2048 × 448 modular 48-port design.
- Updated all 48 RJ45 port, LED, number and hitbox coordinates.
- Updated four uplink hitboxes and seven status LED positions.
- Updated default logo, Status Box 1, Status Box 2 and calibration-button placement.
- Preserved the previous faceplate and calibration as legacy assets.
- Made Copy JSON copy directly to the clipboard.
- Added a legacy browser copy fallback for insecure or restricted clipboard contexts.
- Added clear clipboard success and failure messages.

## v1.3.11

- Added editable custom port selection with comma-separated ports and ranges.
- Added custom targets for ports, link LEDs, activity LEDs and port numbers.
- Added sorting, duplicate removal, validation and missing-port reporting.
- Unified calibration blinking for single, grouped, odd/even and custom selections.
- Added a calibration-button selection overlay.
- Fixed Status Box 1 and calibration-button target editability.

## v1.3.9

- Made Profile Controls permanently visible without a collapsible header.
- Merged Port Manager into Calibration Target below the target controls.
- Placed Odd and Even Quick Selection controls on one horizontal row.
- Added horizontal overflow handling for the parity row on narrow panels.
- Normalised the remaining Port Manager field and action names.

## v1.3.8

- Merged Port Manager into Calibration Target and placed its controls directly below the target controls.
- Placed odd and even Quick Selection controls on the same row.
- Made Profile Controls permanently visible and removed its collapsible section header.

## v1.3.7

- Reordered calibration sections to: Appearance, Calibration Target, Port Manager, Quick Selection, Position and Size, Profile Controls.
- Promoted the remaining Port Manager to the single primary Port Manager section.
- Reduced calibration-tool interface text by 2 px for a more compact layout.

## v1.3.6

- Reduced all calibration-tool text by 2 px for a more compact workspace.
- Reduced calibration section text, buttons, dropdowns, badges, profile-path text, JSON export text, the on-card Calibrate toggle, overlay title, and overlay labels.
- Preserved all control sizes, spacing, functionality, and saved calibration data.

## v1.3.5

- Removed the duplicate Port Manager from the top of the calibration panel.
- Kept the single Port Manager near the bottom of the panel.
- Preserved all Add Port, Duplicate Port, Rename Port, Remove Port, and live port-count functionality.
- Simplified the calibration workflow before creating the new default faceplate profile.

## v1.3.1

- Fixed the calibration editor repeatedly alternating between a saved profile and “No saved profile found” on new installations.
- When calibration is opened for a switch with no stored profile, Switch Vision now creates a starter profile from the current generated/default layout.
- Added `calibration_profile_auto_create` (default: `true`) so automatic starter-profile creation can be disabled when required.
- Added an in-flight creation guard to prevent duplicate profile saves while Home Assistant re-renders the card.

## v1.3.0

- Added the first dynamic Port Manager to interactive calibration.
- Port target selectors now follow the ports present in the active calibration profile rather than assuming 48 ports.
- Added Add Port, Duplicate Port, Rename Port, and Remove Port controls.
- Removing a port affects only the visual calibration profile and does not delete Home Assistant or SNMP2MQTT entities.
- Preserved the v1.2.26 Gold release folder unchanged.

# Changelog

## v1.2.25 — Support My Switch prepared email

- Generates a standard `.eml` message addressed to `switch-vision@zemerdon.com` with the contribution ZIP already attached.
- Generates a local action page with **Prepare Email**, **Download Archive**, and **Open Email Without Attachment** actions.
- Nothing is sent automatically and no mail credentials are stored.


## v1.2.24 — Launch documentation refresh

- Rewrote the main README and clean-install guide for the current Switch Vision workflow.
- Documented the required Layout Card resource and the mobile Configuration error recovery procedure.
- Added dedicated troubleshooting and Support My Switch guides.
- Updated support levels, forum and support-email references, status-box guidance, and clean-update instructions.
- Removed stale pre-1.0 version examples and obsolete faceplate-label wording from primary documentation.

## v1.2.26

- Added a Home Assistant Ingress web interface for Support My Switch.
- Added guided privacy and contributor-recognition controls.
- Added live contribution progress, bundle-quality results, and detected-hardware summaries.
- Added one-click Prepare Email, Download Archive, and email-without-attachment actions.
- Kept all sending manual; Switch Vision stores no email credentials.

## v1.2.22

- Removed the icon from the on-card Calibrate button.
- Centred the Calibrate and Done labels within the calibrated button bounds.

## v1.2.21

- Fixed Status Box 2 style controls updating a stale calibration object after UI defaults were merged.
- Border show/hide, border colour, font, sizing, text colour, and fill colour now update the live Status Box 2 profile and renderer immediately.
- Added a browser regression check covering border off, border on, colour changes, and font-size changes.

## v1.2.20

- Fixed Status Box 2 border controls by separating the rendered border from the panel background.
- Moved status-box calibration outlines 5 px outside the boxes so live border visibility and colour changes remain visible while selected.

## v1.2.19

- Fixed Status Box 2 border enable and border-colour controls by using the same profile-driven rendering path as Status Box 1.
- Clears stale Status Box 2 border overrides created by earlier calibration builds.

# Changelog

## v1.2.18

- Fixed Status Box 2 border re-enabling after it was hidden.
- Fixed live Status Box 2 border-colour updates by applying explicit SVG stroke attributes.

## v1.2.17

- Fixed Status Box 2 border visibility and border colour so the renderer uses the box's own saved settings directly.
- Simplified status-box border rendering to a single correctly coloured outline.
- Removed the duplicate Switch IP heading from the calibration panel.

## v1.2.16

- Moved the default Status Box 2 position down another 5 px.
- Fixed Status Box 2 live styling so font, sizing, colours, bold, fill and border controls are applied immediately even when card-level overrides exist.

## v1.2.15

- Moved the default Status Box 2 position down by 5 px, from Y 10 to Y 15.
- Moved the Status Box 2 style row directly above the Status Box 2 field controls.
- Simplified both status-box field selectors to the label **Field**.

## v1.2.14

- Added a dedicated **Status Box 1 style** label so both status-box styling rows use the same layout.
- Added a **Show JSON / Hide JSON** control to the calibration panel.
- The calibration JSON export is now collapsed by default to save vertical space; **Copy JSON** continues to work while it is hidden.

## v1.2.13

- Fixed the calibration controls failing to render after adding Status Box 2 styling.
- Defined the Status Box 2 bold-state value before the calibration panel template is built.
- Restored the calibration panel while retaining all Status Box 2 font and border controls.

## v1.2.12

- Added a dedicated Status Box 2 styling row with independent font, bold, font size, title size, text colour, and fill colour controls.
- Added border visibility and border colour controls for both Status Box 1 and Status Box 2.
- Status-box border settings are saved independently in calibration profiles.
- Reduced the default Status Box 2 height from 60 px to 55 px.

## v1.2.11

- Moved the default Status Box 2 position to the higher, slightly left-aligned placement used by the tested SW6 layout.
- Status Box 2 now defaults fully inside the faceplate frame above the right-side vents and clear of the Calibrate button.
- Existing saved calibration profiles keep their saved position; the new placement applies to new profiles and reset layouts.

## v1.2.10

- Removed the separate faceplate-label rendering, calibration target, controls, YAML generation, and active documentation.
- Status Box 2 is now the single configurable name/label area and defaults to the generated card title as its custom title.
- Moved the default Status Box 2 fully inside the faceplate frame and positioned it neatly above the right-side vents.
- Status Box 2 starts with all rows hidden so its custom title can be used as a clean switch label; users can reveal any status rows manually.
- Existing custom Status Box 2 titles remain editable and are saved in calibration profiles.

## v1.2.9

- Added independently configurable **Status Box 2**, using the same switch status fields as Status Box 1.
- Status Box 2 defaults to the faceplate label while Status Box 1 retains the existing switch fields.
- Changed the default Status Box 1 order to MODEL, IP, CPU, TEMP, POE, UPTIME, then the remaining fields.
- Added editable title sources for both status boxes: default title, status-field value, or a custom title. Selecting a title field does not automatically hide or reorder its normal row.
- Renamed the calibration controls to **Status Box 1 Field** and **Status Box 2 Field**.
- Removed Faceplate label and the individual identity-field buttons from Quick select.
- Renamed the calibration management-address input to **Switch IP**.

## v1.2.8

- Added the standard POWER-ETHERNET-MIB aggregate PoE branch (`1.3.6.1.2.1.105.1.3.1`) to targeted discovery walks.
- Catalyst 2960S devices that omit Cisco extended aggregate PoE totals can now generate PoE used and budget sensors without requiring a full walk.
- Built directly from the v1.2.7 baseline; no abandoned earlier v1.2.8 dashboard changes are included.
- Custom component changed: no.

## v1.2.7

- Added a standard POWER-ETHERNET-MIB fallback for aggregate PoE used and budget sensors when Cisco extended totals are absent.
- Catalyst 2960S devices such as WS-C2960S-48FPD-L now generate `PoE Used W` and `PoE Budget W` sensors and display `0 / 740 W` when no PoE power is in use.


- Fixed Discovery identity parsing so system description, model, and serial sensors are actually emitted into generated SNMP2MQTT YAML.
- Identity sensors now use each switch's existing `Slow System` poll group at 300 seconds and are created on the first poll after SNMP2MQTT restarts.
- ENTITY-MIB model and serial OIDs remain walk-aware and member-specific for supported Catalyst stacks.
- Custom component changed: no.

## v1.2.6



## v1.2.5

- Added generated identity sensors for model, serial number, and system description using exact OIDs found in each discovery walk.
- Generated dashboard cards now map the identity entities automatically.
- Vendor, OS, and firmware are derived from Cisco system-description data when dedicated entities are unavailable.
- Corrected Cisco 2960S/2960X aggregate PoE units to watts while preserving Catalyst 3650 milliwatt reporting.
- Card PoE formatting now respects entity units and safely handles legacy entities without unit metadata.
- Custom component changed: no.

## v1.2.4

- Centered the Calibration button label vertically and horizontally inside its calibrated target box.
- Applied border-box sizing and even internal spacing so the selection border no longer touches the label at the bottom or appears heavier above it.
- Custom component changed: no.

## v1.2.3

- Fixed Calibration button target parsing so arrow and size controls edit the visible button instead of falling through to a port target.
- Added Calibration button support to target labels and Reset target.

# Changelog

## v1.2.2

- Fixed the movable Calibration button so its 2048 × 448 calibration coordinates scale correctly with the displayed card size.
- Calibration button now appears at its default top-right position on newly generated cards.
- Status rows whose calibrated label or value positions fall outside the status box are no longer rendered.
- Prevents identity and telemetry text from overlapping ports or other faceplate elements.
- Custom component changed: no.

## v1.2.1

- Calibration button now defaults to visible when the card setting is omitted.
- Discovery-generated dashboard cards now explicitly include `calibration_button: true`.
- Bundled live and generated-card examples now show the calibration button by default.
- Custom component changed: no.

## v1.1.8

- Added separate custom logo and background folders.
- Added a safe Home Assistant WebSocket asset-listing API.
- Added Logo and Background dropdowns to interactive Calibration.
- Added Use card default, None, empty-folder guidance, and Refresh files controls.
- Added live background/logo preview and calibration-profile persistence.
- Custom component changed: yes.


- Masks Cisco local-hostname OID `1.3.6.1.4.1.9.2.1.3.0` in symbolic and numeric SNMP walk output.
- Adds the Cisco hostname OID to the final residual privacy audit.
- Advances the contribution bundle schema to version 8 and sanitization schema to version 5.

## v1.1.6 - Support My Switch Cisco local hostname privacy fix

- Masks plain-text `Cisco local hostname: <value>` fields in Discovery reports when hostname masking is enabled.
- Extends the final residual privacy audit to detect the same report field.
- Prevents contribution bundles from reporting a clean hostname audit while Cisco local hostnames remain.
- Advances the contribution bundle schema to version 7 and sanitization schema to version 4.

## v1.1.5 - Support My Switch contributor experience

- Added optional contributor recognition preferences: anonymous, first name, full name, GitHub username, or forum username.
- Added `EMAIL_TEMPLATE.txt` with the contribution ID, archive name, recognition preference, and tester-notes prompts.
- Added `BUNDLE_QUALITY.txt` and manifest quality fields driven by the final residual privacy audit.
- Added a clearer review receipt, privacy summary, and next-step instructions in the Discovery log.
- Kept the validated bundle engine and sanitization behaviour unchanged.

## v1.1.4 - Support My Switch report hostname privacy fix

- Masks bullet-style plain-text hostname fields such as `- sysName: switch.example.com` in Discovery reports.
- Extends the final residual audit to detect the same report-style hostname fields.
- Prevents a contribution archive from reporting a clean hostname audit while those values remain.
- Advances the Support My Switch bundle schema to version 5 and sanitization schema to version 3.

## v1.1.3 - Support My Switch privacy completion

- Sanitizes copied switch data before device summaries and fingerprints are generated.
- Adds a final privacy pass across bundle-root metadata to prevent reintroduced hostnames.
- Masks numeric and symbolic IF-MIB ifAlias values when interface-description masking is enabled.
- Masks VLAN labels consistently while preserving numeric VLAN IDs for analysis.
- Adds a final residual privacy audit and records any remaining enabled-category findings.
- Advances Support My Switch bundle schema to version 4.

## v1.1.2 - Support My Switch privacy engine

- Added privacy processing for contribution bundles using only a temporary copy.
- Credential-like values are always removed before archive creation.
- Added configurable masking for management IPs, MAC addresses, hostnames/domains, VLAN names, and interface descriptions.
- Added machine-readable and human-readable sanitization reports.
- Updated bundle manifest schema to version 3 with privacy selections and replacement counts.
- Live `/share/switch_vision/` data remains untouched.

# Switch Vision changelog

## v1.1.1 — Support My Switch bundle metadata and fingerprints

- Replaced development-stage wording with a user-facing Support My Switch workflow.
- Added a concise completion summary with contribution ID, archive size, file count, privacy state, and output path.
- Added `DEVICE_SUMMARY.json` from discovered capability sidecars.
- Added deterministic SHA-256 device fingerprints for grouping repeated contributions from the same hardware profile.
- Expanded `MANIFEST.json` to bundle schema version 2 with device counts and fingerprint references.
- Kept the live `/share/switch_vision` folder read-only and excluded prior contribution archives.
- Privacy sanitization remains a later test stage; generated bundles still require review before sharing.

## v1.0.0 — Gold Master

- Promoted the fully validated v0.9.21 codebase to the first Switch Vision Gold Master.
- Froze the v1.0 compatibility baseline for paths, domains, card fields, generated entities, calibration storage, and generated YAML headers.
- Recorded validated SNMP2MQTT core/add-on v0.9.3 as the Gold telemetry companion.
- Added Gold-only release documentation and explicit `build.py -v 1.0.0 --gold` validation.
- Confirmed all known Gold blockers closed through clean-install evidence on SW5–SW9.

## v0.9.21

- Capability sidecars now read the active Discovery runtime version instead of a hard-coded value.
- Capability interface totals use model-aware 24/48-port front-panel classification and exclude management interfaces.
- Multi-switch runs remove an obsolete empty `snmpwalks/live/` directory without deleting non-empty user data.
- Build validation now covers dynamic capability versioning, interface classification, and legacy-folder cleanup.

## v0.9.20

- Propagate the active release version into every per-switch capability sidecar.
- Align Catalyst 2960S/2960X capability counts with the authoritative front-panel mapping.
- Exclude the dedicated Gi0/0 management interface from physical-port totals.
- Classify 2960 front-panel uplinks above the 24/48-port RJ45 boundary as uplinks instead of RJ45 ports.
- Stop recreating the obsolete empty `snmpwalks/live/` directory during multi-switch discovery.
- Add build regressions for capability versioning, interface classification, and walk-folder cleanup.

## v0.9.18

- The build script now creates `Switch_Vision_v<version>_source.zip` automatically after every successful build.
- The generated source ZIP is placed in the project root for easy upload and contains source files at the archive root plus the matching extracted release.
- Removed the need for the optional `--source-zip` argument.
- Previous local source ZIPs are excluded from newly generated source archives.

## v0.9.17

- Removed obsolete generated `last_change_entity_prefix` and `last_change_entity_suffix` fields.
- Confirmed port activity is derived directly from RX/TX byte-counter deltas.
- Simplified generated dashboard cards by omitting redundant `demo: false` and `calibration_button: false` settings.
- Added release validation so nonexistent `_last_change` dependencies cannot return.

## v0.9.16

- Fixed stack-member status entity resolution with explicit CPU, temperature, and PoE entity mappings.
- Added explicit stack member numbers to generated cards and rejected malformed saved member values.
- Generated faceplate labels now remain authoritative unless the label text is explicitly edited in Calibration.
- Hid the PoE status row when used/budget entities are unavailable.
- Renamed the Discovery field label to **Switch Name (Used internally only)**.

# Changelog

## v0.9.15

- Made stack-member display names drive both generated card titles and default faceplate labels.
- Kept stable member IDs and calibration profile names separate from friendly display text.
- Added optional per-switch and per-stack-member `faceplate_label` overrides.
- Corrected generated stack member status text by preserving stable member keys such as `SW5` and `SW6`.

## v0.9.14

- Fixed switch-list walk-to-target resolution after per-switch folder persistence.
- Parent folders with spaces converted to underscores now match their configured switch names.
- Management IP, sensor prefix, community and display metadata are restored from the runtime switch map during parsing.
- Generated SNMP2MQTT YAML is no longer blocked by false `Management target: unknown` results.
- Removed the stale `v0.7.18` behaviour-authority wording from vendor reports.

## v0.9.13 — Per-switch output cleanup

- Removed creation of the legacy empty `snmpwalks/live/` folder during switch-list runs.
- Capability sidecars now use one stable file per switch: `capabilities/<switch_name>-capabilities.json`.
- Removed the ambiguous latest `capabilities.json` convenience copy.
- Updated Discovery report headings to show the walk root and per-switch folder mode.
- Non-Gold packages no longer include Gold-specific checklist material.
- Build output removes `__pycache__` directories and `.pyc` files.

## v0.9.12

- Removed the user-facing `folder_label` field; walk folders now derive only from sanitized `switch_name`.
- Spaces and unsafe characters in walk folder names are converted to underscores.
- Targeted walks are written directly to `/share/switch_vision/snmpwalks/<switch_name>/` and verified after each write.
- Added an optional `display_name` field for each stack member.
- Generated card titles and faceplate labels inherit stack-member display names when supplied.

## v0.9.11

- Fixed targeted multi-switch walks so each switch persists only in its own switch-name subfolder; removed the legacy shared-root copy that overwrote `live-targeted-snmpwalk.txt`.
- Made high-capacity RX/TX counters walk-aware so missing `ifHCInOctets`/`ifHCOutOctets` OIDs are not generated.
- Made PoE supply/status/used/budget sensors individually walk-aware.
- Made optional trunk-status and alias sensors walk-aware.
- Prevented standalone switch cards from receiving stack inheritance settings unless an explicit multi-member stack is configured.
- Corrected capability interface classification for abbreviated `Gi` names and refined 2960S identity from `sysDescr`.
- Propagated v0.9.11 into capability sidecars.

## v0.9.8

- Fixed targeted switch-list walks retaining the shared `snmpwalks/live` output path when optional folder fields were blank.
- Every switch now writes to `/share/switch_vision/snmpwalks/<switch-name>/live-targeted-snmpwalk.txt` by default.
- Added a build regression check for the per-switch targeted-walk fallback.

## v0.9.6

- Made switch-list `display_name` optional so blank friendly names save correctly.
- Removed legacy opening fields: `selected_switch`, `fallback_switch_host`, top-level `sensor_prefix`, and `fallback_snmp_community`.
- Clarified `switch_name` as the stable internal target ID and `display_name` as the optional friendly title.
- Renamed report headings to `Current target`, `Management IP`, and `Output folder`.

## v0.9.5

- Added optional Discovery `display_name` field for generated card titles.
- Generated cards now avoid duplicate `SW5 • SW5` titles by using `Switch Vision • SW5` when no display name is supplied.
- Added editable and movable **Faceplate label** calibration target above the right-hand vents.
- Discovery-generated cards set `faceplate_label` to the member/switch name.

# Switch Vision changelog

## v0.9.4

- Propagate the enforced build version into Discovery runtime-generated YAML and dashboard headers.
- Prefix per-walk capability sidecar filenames with the configured switch sensor prefix to prevent overwrites.
- Normalize simple `SW<number>` dashboard member/profile names to uppercase while preserving custom labels.
- Add build-time regression checks for all three fixes.

## v0.9.3

- Fixed calibration profile storage after the Switch Vision rename.
- The custom component now uses only `.storage/switch_vision_calibrations`.
- Clean-install release: no legacy Cisco Vision storage import or compatibility fallback is included.

## v0.9.1

- Fixed standalone switches with retained Cisco member numbering (for example `Gi2/0/1`) generating the next sensor prefix (`sw5`) instead of their configured prefix (`sw4`).
- Standalone devices now always use the configured `sensor_prefix`; stack member prefix arithmetic remains stack-only.

## v0.9.0 — Release Candidate

- Completed the project-wide Switch Vision naming cutover.
- Added vendor/OID knowledge and normalized interface capability sidecar output.
- Added the `switch_vision` Home Assistant integration domain.
- Added the `custom:switch-vision-3650` dashboard card type.
- Moved shared output paths to `/share/switch_vision/`.
- Added a reproducible, version-aware build script.
- Added exact and wildcard `-v/--version` build enforcement.
- Added automatic patch increment after every successful build.
- Rebuilt the release as one all-in-one Switch Vision folder.
- Kept SNMP2MQTT core/add-on packaging separate from the main project.
- Rewrote requirements, installation, workflow, field-reference, and example documentation.
- Removed stale Cisco Vision product naming while retaining Cisco where it identifies the hardware vendor or Cisco-specific MIB logic.

## Historical baseline

Cisco Vision v0.7.17 was the final Gold baseline before the project became Switch Vision. Historical release notes remain relevant only when reviewing old builds.

## v1.1.0 - Support My Switch Stage 1

- Added the first testable Support My Switch bundle engine.
- Added an add-on option to archive the complete `/share/switch_vision/` data folder.
- Generates sequential contribution IDs such as `SV-2026-000001`.
- Adds a manifest, contribution ID, README, and sanitization status report.
- Excludes the contributions output folder to prevent recursive archives.
- Never modifies the live Switch Vision data folder.
- Stage 1 bundles are intentionally unsanitized and must be reviewed before sharing.
