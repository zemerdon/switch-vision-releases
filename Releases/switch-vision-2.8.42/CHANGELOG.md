## v2.8.42 — Verify saved artwork, geometry and LEDs after visual operations

- Read back Core's persisted Calibration after Reset Current Faceplate, Reset Current Switch, Reset All and Hub-approved stock upgrades. Check the saved image, RJ45/SFP geometry, status LED positions and LED membership instead of reporting success from a save acknowledgement alone.
- Check the selected verified stock artwork on switch/namespace resets and the explicitly approved stock revision on Hub upgrades. Reject missing or mismatched saved state, and retain a compact per-card operation result with the failing stage for diagnosis.

## v2.8.41 — Keep Calibration manifest reads off the HA event loop

- Offload packaged stock-artwork manifest reads from Calibration save, selection and approval WebSocket operations to Home Assistant’s executor. Preserve exact stock SHA-256 checks, saved Calibration and existing artwork-selection rules.

## v2.8.40 — Keep original and compact 24-port stock faceplates separate

- Restore the original 24 RJ45 / 2 SFP and 24 RJ45 / 4 SFP artwork and factory Geometry under their established filenames, and add owner-calibrated 6000 × 750 Compact artwork with matching Geometry under distinct `-compact.png` filenames.
- Make the Compact variants the recommended default for compatible generic 24-port models while retaining Original as an explicit optional selection. Preserve historical artwork revisions and per-switch saved Calibration until the normal, explicit upgrade approval.

## v2.8.39 — New compact 24-port stock faceplate defaults

- Replace the default 24 RJ45 / 2 SFP and 24 RJ45 / 4 SFP artwork with the new owner-supplied 6000 × 750 compact faceplates and their individually calibrated port, optical and status LED Geometry. Both existing stock filenames, profiles and functional port counts remain unchanged.
- Preserve switch-scoped Calibration and approved historical artwork revisions until a deliberate faceplate upgrade. No model support claims or hardware capabilities are changed.

## v2.8.38 — Reset All restores each loaded switch's current factory artwork

- Fix Reset All retaining historical faceplate artwork on other loaded switches after the original and Compact 48/4 stock filenames were separated. Use each card's verified model-specific Reset Current Switch contract before saving its paired factory Geometry.
- Refresh all mounted cards in the selected Native or Custom scope even if their HA update events were missed, without touching the opposite scope or physical switches. Fail visibly if a mounted switch cannot complete its factory reset.

## v2.8.37 — Restore complete verified Core changelog history

- Restore previously omitted verified v0.9.0–v2.3.0 release entries from canonical local Git, while retaining full version attribution for major/minor roll-up presentation.
- Remove private contribution references from the recovered customer-facing history; preserve application behaviour, Calibration and existing public releases unchanged.

## v2.8.36 — Preserve faceplate-specific status LED identity

- Use the checksum-verified artwork revision's Geometry when drawing Native status LEDs, so historical compact artwork cannot inherit the LEDs of a newer faceplate that reused its filename.
- Show generic factory status LEDs only on the two original 48 RJ45 stock faceplates; hide unused placeholders on the remaining faceplates without preventing explicit owner Calibration.
- Add Native redraw and catalogue regression coverage for legacy pinned artwork, intentional factory LEDs and saved Calibration.

## v2.8.35 — Faceplate-driven status LED rendering

- Native SVG status LEDs now obey the actual displayed faceplate's stock Geometry. The compact 48 RJ45 / 4 SFP faceplate cannot inherit LEDs from a saved original-stock layout; explicitly edited LED membership on the same selected faceplate remains a supported Calibration override.
- Add executable red/green regression coverage for stale saved Geometry, actual Native SVG redraw wiring and the original/compact artwork distinction.

## v2.8.34 — Restore compact factory Status LED defaults in Native cards

- New Native cards now resolve the exact model's factory presentation even when their RJ45/SFP counts match the generic legacy 3650 template. Compact 48/4 cards keep the seven authored status indicators hidden.
- Preserve existing switch-scoped saved Calibration and approved historical faceplate pins, without automatically resetting user selections.

## v2.8.33 — Align 48/4 stock and compact model projection

- Synchronize Core's 67-model registry projection to Discovery's reviewed 48 RJ45 / 4 SFP faceplate defaults, retaining separate original and compact art/Geometry and the existing per-switch upgrade choices. No new physical-switch capabilities or changes to saved Calibration.

## v2.8.32 — Keep original and compact 48 RJ45 / 4 SFP faceplates separate

- Restore the original 6000 × 1325 stock 48 RJ45 / 4 SFP artwork and its original factory Geometry, while retaining the 6000 × 900 compact artwork and owner-calibrated Geometry as a separately named option.
- Keep compact recommended for existing compatible 48/4 models and offer original stock separately. Preserve saved switch Calibration and require explicit approval for any faceplate/Geometry replacement.

## v2.8.31 — Display observed Dell optical diagnostics

- Present existing read-only TX/RX optical power (dBm) and transceiver fields on Dell SFP Status Boxes when actual Home Assistant sensor readings are available, including Dell models other than the N2128PX-ON.
- Preserve explicit per-box Calibration Show/Hide choices, keep unavailable/N4032F readings absent, and retain the existing model-bounded Discovery OID collection. No new SNMP SET, optical inference or unsupported-device claim.

## v2.8.30 — Preserve saved stock faceplates across renamed defaults

- Preserve the SHA-verified original faceplate as the current selection on existing Native switches when a new model-specific default uses another filename; the new artwork and its paired factory Geometry remain an explicit Hub upgrade choice.
- Recover only incorrectly initialized, unapproved latest-artwork pins from verified saved stock bytes. Never replace an explicitly approved revision, alter a neighboring switch, or reset saved Calibration without confirmation.

## v2.8.29 — Separate original and compact 48 RJ45 / 2 SFP faceplates

- Restore the original 48rj45-2sfp artwork and factory Geometry as a selectable alternative. Register the owner-supplied 6000 × 900 compact artwork and its exact paired Geometry separately as 48rj45-2sfp-compact.
- Set compact as the default for the supported 48 RJ45 / 2 SFP model contracts without changing their physical port mappings. Preserve saved per-switch Calibration until a verified user-approved upgrade.

## v2.8.28 — Compact stock 48 RJ45 / 2 SFP faceplate

- Replace the default 48 RJ45 / 2 SFP stock artwork with the supplied 6000 × 900 compact PNG and matching factory Geometry. Preserve the source export's port, SFP, status LED and visual-control coordinates in native image space.
- Keep the established stock filename and model mappings. Existing switch-specific Calibration remains unchanged until the user approves the verified replacement through Hub.

## v2.8.27 — Complete verified Hub faceplate upgrades

- Validate the full Core Calibration profile before an approved stock revision can replace a switch's saved layout or SHA-pinned artwork. Reject incomplete historical factory geometry without changing the switch.
- Reload the saved verified factory for both Native upgrades and the switch-scoped Custom faceplate picker, including the editor's working layout. Strengthen missed-event reconnect and approval rejection regressions.

## v2.8.26 — Apply Hub-approved stock faceplate immediately

- On an approved Hub faceplate upgrade, atomically save the exact SHA-verified factory Calibration for that switch in Core alongside the pinned artwork selection. This completes the reset even if no Native dashboard card is open to receive the update event.
- Make Native reload the approved saved factory instead of reconstructing and writing potentially outdated fallback geometry in the browser. Keep other switches and custom faceplate profiles unchanged.

## v2.8.25 — Compact stock 48-port faceplate

- Replace the generic stock 48 × RJ45 / 4 × SFP artwork and its paired factory Calibration geometry with the owner-supplied compact design. Preserve exact port, SFP, LED and Status Box placements from the supplied export.
- Keep the existing stock filename and model mappings; new stock defaults use the updated SHA-paired artwork and factory geometry while saved per-switch Calibration remains unchanged until an explicit faceplate upgrade is accepted.

## v2.8.24 — Adjustable Status Box border thickness

- Add independent border thickness controls after Hide in Status Box 1 and Status Box 2 Calibration rows, matching LED outline adjustments (0.25–3.00 px in 0.25 px steps).
- Apply the saved border width directly to each box outline. Preserve the existing 1.5 px appearance in older profiles, keep settings when borders are hidden, and leave LED outline settings unchanged.

## v2.8.23 — Honour faceplate LEDs and refine Calibration tools

- Honour each faceplate's factory Status LED visibility in new, reset and older automatically saved Calibration profiles. Keep model-specific overlays hidden where intended, preserve deliberate user LED changes and geometry, and keep unverified chassis indicators off.
- Rename LED Test Mode to Test Mode 1 (force visible LEDs on), and add temporary Test Mode 2 (force visible Status/Link/Activity/PoE LEDs off); leaving test mode restores live readings without saving LED overrides.
- Unify bold coloured Calibration action buttons: Cancel first in red, Refresh green, faceplate/all reset red, current-switch reset pink, Save Profile blue, and two distinct orange test modes.
- Fix Status Box colour pickers hidden by horizontally scrolling controls. Preserve factory transparent box backgrounds and translucent borders when resetting either Status Box colour; leave unrelated colours and saved settings unchanged.
- Require pinned Chromium browser checks in release validation; verify the real picker layout, colour edits, reset and close actions, and both LED Test Mode buttons with zero skipped browser tests.

## v2.8.19 — Calibration controls and reliable faceplate Status LEDs

- Configure selected RJ45/SFP details independently in Port Status Box 1, Box 2 or Both, with per-box connector, field ordering and Show/Hide actions. Keep inactive boxes on their normal switch summary.
- Streamline Calibration with compact Status Box rows, accessible ↑/↓ field-order buttons, a Status LED dropdown with Show/Hide/Add/Remove, adjacent output controls and Port Label Show, and responsive Link/Activity/PoE LED Shape controls. New/factory-reset editors start with empty LED membership without suppressing the stock display.
- Restore original stock faceplate Status LEDs and recover previously auto-hidden starter profiles without rewriting saved Calibration. Deliberate LED edits remain effective; existing port indicators, custom geometry, other saved settings and telemetry are preserved.

## v2.8.18 — Compact Calibration control placement

- Remove redundant “style” from both Status Box headings, and align Port Status Box 2 Output immediately after Box 1’s Hide control when space permits.
- Keep Port Label Show directly beside its control name, remove the LED outline thickness hint, and flow Link, Activity and PoE LED Shape controls directly after Thickness with responsive wrapping and no forced horizontal scrollbar.
- Preserve all saved Calibration settings, status/port LED behaviour, routing and faceplates.

## v2.8.17 — Calibration status controls on two rows and arrow buttons

- Put each Status Box Border switch and border-colour picker at the start of a second horizontal row, followed by the existing field order and Show/Hide controls; keep each style row intact.
- Replace every Calibration Move up/down control for Status Box 1, Status Box 2 and Port Status outputs with ↑/↓ arrow buttons, retaining their actions and accessible labels.
- Preserve saved Calibration values, field order, visibility, colour, border state, and switch rendering.

## v2.8.16 — Calibration control layout and optional Status LEDs

- Keep Status Box 1 and Status Box 2 style and field controls on a single horizontal row each, with horizontal scrolling where the Calibration editor is narrower.
- Put Port Status Output first in the Port Status Box 1 Output controls, before Connector; put the selected Port Label Show/Hide controls first on the Port labels style row.
- Replace separate Status LED checkboxes with an LED selector and Show, Hide, Add and Remove actions. New or factory-reset calibration profiles start with every Status LED removed; manually adding one restores its existing calibrated position. Preserve Status LEDs, visibility and geometry in previously saved profiles.

## v2.8.15 — Port Status Box routing and Calibration improvements

- Configure RJ45/SFP port details independently in Port Status Box 1 and Box 2, including Connector, Field, Move up/down and Show/Hide. Port Status Output selects Box 1, Box 2 or Both; the other destination keeps its switch summary with inactive selected-port controls disabled.
- Display both output-control groups side by side on wide screens or stacked on narrow screens. Update the Calibration Part dropdown label immediately without applying a different target before Select.
- Preserve existing single- and dual-box saved profiles, custom field order, visibility, geometry and faceplates.

## v2.8.10 — Optional per-port PoE LED Calibration

- Add an independent per-RJ45 PoE LED shape, visibility, position and size in existing Calibration controls, without creating new quick-select options or changing saved/factory defaults.
- Light the LED only for confirmed active per-port delivery from mapped SNMP PoE status/positive measured power or fresh UniFi API port PoE state; keep unknown, inactive and unavailable telemetry off. Test Mode previews geometry without live readings.
- Preserve Link and Activity indicators, system-level PoE LEDs, existing faceplates and previous saved Calibration.

## v2.8.9 — Clear customer release history

- Remove development-stage labels from earlier changelog headings and correct obsolete release-status text.
- Keep all existing runtime, artwork, Calibration and telemetry functionality unchanged.

## v2.8.8 — Cisco 3560CG Compact default artwork

- Add owner-supplied native 2680 × 356 `c3560cg-8pc-s-compact.png` as the reviewed default artwork for exact Cisco WS-C3560CG-8PC-S; preserve the old `c3560cg-8pc-s.png` as a selectable original, with user-facing catalog text unchanged except for the new ` Compact` suffix.
- Translate owner Geometry Export v2 into native-image factory presentation while treating its SW1 / stock-48 export origin solely as capture metadata. Preserve eight fixed RJ45 plus two real dual-purpose copper/SFP logical positions; retain exact discovery mapping and Experimental evidence status.
- Use a separate Compact factory profile so the Zyxel XS1930-10 and legacy Cisco profiles keep their original faceplate. Do not reset saved per-switch Native or Custom Calibration, alter the standard card renderer, change existing models' assigned artwork, perform any public release or mutate the owner-supplied originals.

## v2.8.7 — Parallel read-only Supervisor app status

- Fetch Discovery, Installer, SNMP2MQTT and UniFi2MQTT app status concurrently when the Native management UI opens, rather than waiting for four independent Supervisor requests in sequence. Preserve app identity, sidebar navigation, missing-app handling and failure reporting; add source-executed concurrency and error regressions.

## v2.8.6 — Exact Calibration backup restoration

- Preserve imported stock SHA metadata exactly for trusted complete-backup restoration, rejecting unverifiable supplied hashes. Normal Calibration still uses the installed verified artwork SHA.

## v2.8.5 — Left and right Link/Activity LED triangles

- Add Triangle Left and Triangle Right to both Link LED Shape and Activity LED Shape Calibration dropdowns for RJ45 and SFP/uplink ports.
- Render horizontal arrowheads using existing per-port LED size and shape fields; preserve existing shapes, per-port persistence, grouped selection, colours, visibility and telemetry.
- Add source-executed regression for dropdown choices and directional SVG geometry. No user installation is performed by this source-level regression.

## v2.8.4 — SHA-deduplicate historical registry privacy scans

- Keep the Core public attribution/privacy check reading and hashing every supported-device registry across source and all bundled historical releases. Inspect byte-identical copies only once per parser format, without exempting changed, unsafe, malformed, or unexpected archived registries.
- Add failure-path tests proving all archive files are read, unsafe changed releases still fail, and YAML/JSON content is validated under its own parser contract. Source-bound before/after standalone scan measurements on `sv-dev` were 75.85s and 23.44s respectively; the improvement is not a hardware/end-to-end claim.
- Preserve deterministic Core build/version parity, release safety, existing historical assets and No owner Home Assistant installation is performed.

## v2.8.3 — Recover Native artwork after missed Hub events

- Force a server-side Calibration and approved-stock-artwork revalidation whenever a Native or Custom card reconnects, including after the Hub approval event occurred while its dashboard was unmounted.
- Drop a previously cached Calibration only after Core explicitly confirms that the saved profile no longer exists; keep unsaved editor changes intact, and preserve the approved exact-SHA image pin and normal Custom isolation.
- Add source-executed Node/JavaScript regression for cold mount and stale reattachment, verifying a single fetch per attachment and no repeated reads on ordinary card updates. No new Calibration system, owner HAOS installation, or public publication.

## v2.8.2 — Complete Hub-approved Native artwork reset

- On a verified, explicit Native Hub Upgrade Faceplate approval, complete Core's established Reset Current Switch factory Calibration save and re-read the exact SHA-pinned stock artwork. The backend's original approval remains the single authoritative switch-scoped mutation; no second reset service call or Calibration system is introduced.
- Reject mismatched approved SHA and avoid modifying the Custom scope. Preserve the existing manual Reset Current Switch event path and explicit per-switch approval, history and Calibration safeguards.
- Add regression coverage for Native factory save, rejected SHA, normal reset compatibility and Custom isolation.

## v2.8.1 — Cisco 3850-12XS stock faceplate artwork refresh

- Replace `cisco-3850-12xs.png` with the exact owner-provided 2680 × 356 RGBA PNG (SHA-256 `a8ebdc68ddbb38d22bbeaf9f69476b620aa06d494f425dc20baf519b05758028`), preserving the submitted original untouched.
- Keep the twelve SFP cage and port-label strip pixel-identical to the previous revision; leave its verified factory port/LED geometry and per-switch saved Calibration unchanged.
- Installer retains earlier SHA-addressed stock artwork for explicit Native-only Hub adoption after the coordinated update; no automatic Calibration reset or model topology change.

## v2.8.0 — Calibration action tooltips

- Add precise hover/focus descriptions to the seven Calibration action buttons: Test Mode, Cancel, Refresh Faceplate, Reset Current Faceplate, Reset Current Switch, Reset All Switches, and Save Profile.
- Distinguish refreshing pixels without touching settings, resetting Calibration while preserving a chosen faceplate, restoring the current switch to latest verified factory artwork, and resetting all saved switches strictly within the current Native/Custom dashboard scope with two confirmations.
- Keep all button handlers, confirmations, storage, reset semantics, artwork selection and per-switch Calibration unchanged. Use the existing HTML title tooltip pattern; no second tooltip/UI system.
- Apply the standing patch-99 version rollover: Core 2.7.99 → 2.8.0.

## v2.7.99 — Accept legacy SHA-pinned faceplate approvals

- Fix Hub Upgrade Faceplate rejecting an unchanged pre-versioned Cisco 3850-12XS artwork pin with `stale_choice`: Core now compares its saved filename and SHA, and only checks the expected version when a version was actually persisted.
- Keep explicit admin consent, verified target stock image/factory geometry, model-scoped visual Calibration reset and strict stale protection for versioned pins. No automatic reset, physical switch changes or unrelated profile mutation.
- Add regression for the real legacy 3850 SHA, changed selection SHA, wrong filename, missing pin and mismatched versioned revision.

## v2.7.98 — Cisco 3850-12XS owner artwork refresh

- Replace the stock `cisco-3850-12xs.png` with the owner's supplied 2680 × 356 revision (`bc34fc58e818014a3d1b031221e4aab87ae567654075f4f2011f695c23572d74`), preserving the exact image bytes including the test marking.
- Preserve all twelve factory SFP port/LED positions, model topology, the existing native-image factory geometry and saved per-switch Calibration.
- Allow the established Installer SHA-pair history and explicit Hub artwork approval flow to distinguish the prior artwork from this revision; no automatic reset, model promotion or public publication.

## v2.7.97 — Confirmed factory reset refreshes stock artwork

- A confirmed Reset Current Switch now replaces that switch's historical faceplate pin with the latest SHA-verified factory image and geometry. Reset All does the same only within the approved Native/Custom scope.
- Keep Current and routine saves remain unchanged. Unverified replacement pairs stop the reset before modifying persisted state, and the dashboard refreshes its cached artwork after a successful reset.

## v2.7.96 — Installer-owned SHA faceplate preservation

- Stop bundling historical `faceplates-old` archives; Core ships current stock PNGs and their factory geometry only.
- Read validated Installer-preserved SHA image/geometry pairs for per-switch selection, with legacy versioned archives supported only during migration.
- Preserve generic-stock selections when a model gains dedicated artwork and keep user-authored Calibration independent of stock revision changes.

## v2.7.95 — Reproducible Core source-archive packaging

- Package the faceplate revision builder with the exact source archive and load it reliably in clean extracted-source regressions.
- Keep all 2.7.94 bounded-revision, geometry, Calibration-isolation and archive-parity protections unchanged; 2.7.94 was not staged.

## v2.7.94 — Three distinct faceplate revisions

- Limit each shipped stock faceplate to its latest distinct PNG/factory geometry pair and two preceding distinct pairs, without new revisions on routine Core releases.
- Preserve per-switch older selected geometry when it rotates out of shipping and verify every generated archive member under exact release parity.
- Do not change user Calibration, topology, or opt-in faceplate selections.

## v2.7.93 — Versioned faceplates with paired factory geometry

- Bundle every verified historical faceplate and its matching factory port geometry from Core release history; retain current stock files and automatically derive past revisions when building.
- Expose exact Core-version/image/geometry revisions through the trusted Core assets API and permit per-switch selection of any verified revision without changing saved user Calibration.
- Render selected historical factory geometry only where no user-authored Calibration is active. Reject absent/tampered historical image/geometry pairs.

## v2.7.92 — Direct faceplate migration

- Reuse Installer's verified prior-artwork record for existing switches without a selection.
- Preserve saved artwork decisions and Calibration.

## v2.7.91 — Cisco 3850-12XS stock faceplate art refinement

- Replace the stock `cisco-3850-12xs.png` with the owner's latest verified 2680 × 356 PNG, retaining the exact filename and all twelve factory SFP positions.
- Advance the stock asset checksum to distinguish this image from the previous revision for the already-staged per-switch Keep Current / Upgrade Faceplate workflow.
- Leave model telemetry, geometry, saved Calibration profiles and admin actions unchanged.

## v2.7.90 — Opt-in faceplate artwork selection

- Persist one approved stock artwork SHA per switch and dashboard scope without relying on saved Calibration.
- Keep displaying verified archived older stock pixels when the canonical stock filename changes contents, or even when a model recommendation is renamed.
- Protect unapproved updates from being displayed until the artwork pin is resolved; reject missing/tampered history without substituting new pixels.
- Add admin-only exact-SHA artwork approval without resetting per-switch Calibration, preserving native geometry and saved adjustments.

## v2.7.89 — HP 3500yl optical refresh per-port cooldown

- Apply the existing 30-second rate limit to the exact selected physical optical port, not every port on the switch. Refreshing rear A1 does not delay a later rear A4 refresh after the first operation finishes.
- Preserve the single in-flight refresh lock per switch, admin-only explicit opt-in/write credentials, exact J8693A model and IF-index binding, live DOM(1) validation, fixed SNMP SET target/value, 30-second operation timeout and cooldown after stale/failed requests.
- Add offline per-port/host concurrency, retry, time-edge and trust-order regressions. Do not change physical port mappings, faceplates, factory Calibration or Discovery telemetry.

## v2.7.88 — Same-filename faceplate history support

- Record a server-verified stock image SHA-256 whenever a Calibration profile is saved, without changing its geometry, filename or visual mapping.
- Expose a previous artwork revision only when a retained historical PNG matches its expected SHA; support legacy pre-fingerprint profiles using the Installer's verified first retained stock version.
- Preserve all saved profiles unless the owner explicitly invokes Reset Current Switch; no renderer changes or automatic resets.

## v2.7.87 — Cisco Catalyst 3850-12XS artwork replacement

- Replace only the bundled `cisco-3850-12xs.png` artwork with the owner-provided 2680 × 356 PNG, preserving its source bytes and updating the stock-image SHA-256 fingerprint.
- Keep the existing factory Calibration JSON, all 12 SFP port/LED hitboxes, native-image coordinates, exact-model mapping, telemetry and saved user preferences unchanged. No renderer or geometry migration.

## v2.7.86 — Read-only Hub faceplate upgrade metadata

- Expose SHA-256 fingerprints of installed faceplate images and Core runtime version through the existing read-only asset listing after Home Assistant Core starts.
- Expose the stock image retained inside each saved Calibration profile so Hub can compare it with the latest reviewed model default without duplicating Calibration state.
- Preserve existing Reset Current Switch, saved Calibration, stock artwork, model mapping and native renderer behavior; Core does not automatically reset any profiles.

## v2.7.85 — Guarded HP 3500yl rear optical selection

- Resolve rear A1/A4 optical selections to their actual Discovery-observed physical IF-MIB indexes; never infer an optical module from stock artwork, stale Calibration labels or CX4/empty A2/A3 positions.
- Reuse the explicitly enabled, admin-only HP DOM refresh and RX/TX dBm presentation with exact dashboard-bound index and live interface identity checks before any existing fixed OID SNMP SET. No arbitrary writes, automatic polling or new credentials.
- Preserve rear status entities, front 45–48 combo-port behavior, faceplate geometry, native rendering and saved Calibration profiles.
- Coordinate with Discovery 3.0.55's observed rear-index metadata.

## v2.7.84 — Configurable SFP optical status rows

- Make SFP optical sensor rows individually configurable via the existing Port Status Box Show/Hide/Move controls, separate from RJ45 fields.
- Preserve the previous Dell N2128PX-ON optical display until the user edits SFP rows; retain saved calibration and independent status-box layouts.
- Keep missing telemetry unavailable; add no hover information, extra polling or SNMP writes.

## v2.7.83 — Rear optical status accuracy

- Display an unknown state instead of falsely reporting Down when rear optical status telemetry is absent or unavailable.
- Preserve confirmed Up/Down states, speed reporting, front shared-port mapping, supplied faceplate geometry and saved Calibration settings.

## v2.7.82 — HP 3500yl-48G exact default artwork

- Register the unmodified owner-provided 6000 × 1600 HP 3500yl-48G PNG and its unmodified geometry export; use geometry only, ignoring the SW1 test-profile metadata.
- Bind this dedicated native-image factory profile as the HP J8693A Switch 3500yl-48G default, with renderer round-trip and SHA-256 regressions guarding the 48 calibrated RJ45, four SFP and four rear SFP positions.
- Preserve the existing 44 fixed and 4 dual-personality logical port identities, optical/PoE telemetry contract, source renderer and other models without modifying saved user calibration.

## v2.7.81 — Cisco SG200-26 exact owner-supplied default faceplate

- Make `cisco-sg200-26.png` the exclusive Cisco SG200-26 default faceplate, replacing the generic stock visual for this exact model without affecting other models.
- Preserve owner-supplied PNG bytes and complete geometry JSON verbatim; carry all 26 RJ45 socket positions, two shared optical cage positions, seven status LEDs and calibrated UI fields into the dedicated factory profile without rescaling or moving coordinates.
- Keep the existing 24 fixed RJ45 + two dual-personality 1G RJ45/SFP logical interface telemetry and discovery contract unchanged; source checksum and coordinate-equality regressions protect owner geometry.

## v2.7.80 — Five Calibration selectors and visual selection restoration

- Split quick selections into five independent compact dropdowns: Status Box 1, Status Box 2, RJ45, SFP, and rSFP. Preserve each existing target/part choice and add rear-port Odd/Even Ports, Link LEDs, Activity LEDs, and Labels using existing rSFP geometry only.
- Restore yellow selected hitbox/LED/label feedback for entire SFP and rSFP groups and their Odd/Even or individual selections without changing saved Calibration data or hardware telemetry binding.
- Move Port Label Style immediately before the B bold button on the Port labels row; remove the redundant SFP-suffix hint.
- Use the user-facing name rSFP throughout Calibration while retaining legacy internal target identifiers for saved profile compatibility.
- Extend existing Quick Selection theme scope to include the five-dropdown row; existing dropdown typography, sizing and appearance settings remain authoritative, with no unnecessary extra fields.

## v2.7.79 — Compact Status Box dropdowns and rSFP control ordering

- Replace both Status Box quick-action button groups with two compact dropdowns preserving all 24 original target/part selections and existing odd/even RJ45/SFP semantics.
- Position Add rSFP after Add SFP and Remove All rSFP Ports after Remove All SFP Ports in the Port manager row.
- Order front SFP Targets and Part before rSFP Targets and Part; preserve their independent geometry, registry-owned mapping, and saved profiles.
- Place Card Height and Custom Height alongside the asset controls after folder-scan status.
- Remove the three redundant Calibration hints for Status LED visibility, link/activity colour scope, and Auto card height.

## v2.7.78 — Revert shared Calibration label-column alignment

- Undo the 2.7.77 fixed primary label-column layout and restore the proven 2.7.76 Calibration row spacing and first-control positions.
- Keep the earlier rSFP selector beside SFP, content-aware Auto dropdown sizing, Status Box quick-action grouping, and Port Label / LED Shape control refinements.
- Preserve user Calibration geometry, saved profiles, telemetry separation, and all other functionality.

## v2.7.77 — Shared Calibration label-column alignment

- Use the same first-control starting column as Status Boxes across Selection, Port Labels and LEDs, Position & Size, and other primary Calibration rows, with responsive stacking for narrow screens.
- Align Card Height, Port manager, Misc Targets, rear SFP actions, RJ45 key, quick selectors, and Port Label Style without widening nested controls or breaking SFP/rSFP adjacency.
- Preserve existing saved geometry, accessibility of the renamed first-column controls, and model-neutral rSFP/Discovery mapping contracts.

## v2.7.76 — Calibration selector sizing and aligned quick controls

- Put the independent rSFP Target beside the front SFP selector, keeping rear-port add/remove actions below without changing discovery/registry bindings or saved geometry.
- Make Closed Dropdown Auto fit the selected label plus arrow by removing the fixed target-picker cap and letting target groups wrap when necessary; preserve explicit pixel overrides.
- Align Odd/Even RJ45 quick actions under Status Box 1 and Odd/Even SFP actions under Status Box 2, including responsive stacking.
- Tighten Port Label / Show spacing and keep Link LED Shape and Activity LED Shape labels intact on one line. Retain existing selection, shape, save and persistence behaviour.

## v2.7.75 — Content-aware Calibration dropdown widths

- Add model-neutral rear SFP (rSFP) Calibration positions, targeting, geometry and LED/label editing independent of front uplinks. Preserve existing profiles and permit explicit observed bindings, without deriving telemetry from vendor or model names.
- Closed Dropdowns Control width Auto now fits the selected option text plus dropdown arrow, instead of using the longest available option.
- Make Auto content-aware for closed dropdown selected labels, open dropdown option menus, and numeric/text Calibration input widths, preserving explicit desktop/mobile pixel overrides and compact target-picker caps.
- Fix truncated Font and Port Status Output choices while keeping short Field choices compact. Restore Status Box 1 and Status Box 2 Quick Select groups side by side with aligned action columns and mobile stacking. Add an optional Custom Theme Calibration preview highlight colour role (#ff9f1c default), backward compatible with saved themes. No saved calibration geometry or normal dashboard changes.

## v2.7.74 — Calibration workspace polish and combined LED groups

- Align Status Box 1/2 Quick Select controls; separate Port manager; remove redundant Direct text, vertical separators, and obsolete faceplate tip.
- Expand X/Y/W/H entry fields and connect their widths to the existing Number Input Width Calibration Theme setting.
- Introduce independent Desktop/Mobile Hint Text font size and Regular/Bold weight for grey section descriptions and inline helpers.
- Add safe combined RJ45/SFP Link+Activity LED selection for position and size editing, preserving the existing individual link/activity controls via dropdowns; keep target/part dropdown changes immediate.
- Preserve existing saved profile geometry and normal dashboard behavior;

## v2.7.73 — Independent Calibration label and heading typography

- Separate field, group, subsection and section text size/weight from global control text in both Desktop and Mobile.
- Preserve existing settings and Core Calibration behavior; constrain generated style rules to the Calibration editor.

## v2.7.72 — Calibration Theme global sizing and density

- Add bounded Desktop/Mobile row, button and input heights, line height, button width, row and label spacing, and input width controls, with values below and above current defaults.
- Use minimum row heights to preserve mobile wrapping; leave stored switch Calibration profiles unchanged.

## v2.7.72 — Global Calibration editor density adjustments

- Add validated global Desktop/Mobile row-height, row-spacing, button/input minimum height, text line-height, label spacing, button minimum width, and text/number input width controls; preserve previous settings and independent open-menu option-height control.
- Support values above and below actual compact Core defaults, let mobile rows expand for wrapping, and scope changes to the Calibration editor only.

## v2.7.71 — Calibration Theme global settings

- Consolidate editor presentation into one global Desktop/Mobile preference group for shared typography, padding axes and spacing.
- Maintain backwards-compatible saved detailed settings with explicit global-property precedence, preserving special closed/open dropdown dimensions and normal Calibration functionality.

## v2.7.70 — Calibration Theme padding axes and exact-style preview

- Validate and apply separate horizontal and vertical padding in Calibration Theme for applicable controls, with backward compatibility for all-side padding and device-specific scope.
- Ship the unmodified Core Calibration stylesheet and theme-rule generator to the Local Hub preview under exact Core-source parity checks. No saved profile or faceplate changes.

## v2.7.69 — Calibration Theme desktop/mobile editor presentation

- Add validated Core settings for independent Calibration-editor Desktop and Mobile appearance, grouped by workspace/sections, assets/selection, labels/fields, buttons/inputs and dropdown closed/open states.
- Render safely bounded editor-only CSS, including configurable text weight, size, spacing, padding, dropdown dimensions, option row height and open-menu height. Use one accessible in-page dropdown on desktop/mobile while preserving the underlying native selection event contracts.
- Do not change faceplate geometry, saved Calibration profiles, normal dashboards or protected contributor data.

## v2.7.68 — Mobile-only compact Calibration dropdown menus

- Use the approved compact scrollable dropdown menus at mobile viewport widths (760px or less) only; restore native desktop select/dropdown behavior on wider viewports.
- Update picker presentation at breakpoint transitions while preserving the single shared Calibration engine, selected values, unsaved edits and stored profiles.
- Keep approved mobile menu appearance, 16px closed-control sizes, 11px regular white labels, Quick Links and all unrelated behavior unchanged.

## v2.7.67 — Compact in-page Calibration dropdown menus

- Replace Android's oversized native expanded select picker with a short scrollable in-page list (32px rows, 12px option text, maximum 320px height), retaining grouped options and disabled placeholders.
- Keep closed 16px selectors, 11px regular-weight white text, selected values, existing native-select change handlers, arrow styling and profile behavior unchanged.
- Add keyboard/outside-tap dismissal, menu cleanup across rerender/disconnect and focused option-selection regression coverage. Quick Links and all other Calibration functionality remain unchanged;

## v2.7.66 — 11px regular-weight white Calibration control text

- Reduce regular-weight white text in Calibration dropdowns and neutral/white buttons from 12px to 11px.
- Preserve 16px box heights, 12px line-height, all padding, widths and dropdown arrows; leave other text/colours unchanged.
- No Quick Links, geometry, saved profiles or behaviour changes.

## v2.7.65 — Regular-weight Calibration dropdown and white button text

- Remove bold from the white text in Calibration dropdowns and neutral/white buttons, including Misc Targets and Duplicate selected; retain normal 400 font weight.
- Leave the approved 16px control height, 12px text size, padding, widths and painted dropdown arrows unchanged.
- Retain bold field labels and B-format controls, coloured actions, Quick Links, saved calibration and behaviour;

## v2.7.64 — 16px Calibration controls and dropdown sizing

- Set Calibration blue dropdowns/buttons and grey inputs to 16px overall height with 12px text.
- Apply 2px horizontal and 1px vertical text padding within 1px borders; reserve dropdown arrow clearance and override legacy 24px minimums.
- Leave Quick Links, saved profiles, faceplate geometry and telemetry unchanged.

## v2.7.63 — 18px Calibration controls with 1px padding

- Reduce Calibration input, select, button and colour-swatch height from 20px to 18px.
- Set text padding to 1px on all sides, except required native dropdown arrow clearance; retain 10px text, 12px line-height and existing widths.
- Leave all Quick Links and calibration behaviour/profiles unchanged;

## v2.7.62 — Compact Calibration control height

- Reduce Calibration grey text/number/hex inputs, blue buttons and dropdowns from 24px to 20px with a 12px text line-height, retaining 10px text size and the 3px internal text padding.
- Bring colour-swatch height to 20px and preserve 18px of dropdown arrow-side clearance; leave horizontal widths untouched.
- Preserve all Quick Links, saved profiles, geometry and behaviour. Local staging only, no public publication.

## v2.7.61 — Tight 3px Calibration control spacing

- Use 3px padding between the text and outlines of Calibration grey inputs and blue controls, reserving the necessary right-hand clearance for native dropdown arrows.
- Reduce common numeric, hex, swatch, text-label, coordinate and target-dropdown widths by roughly 10–15% while retaining 24px-height controls.
- Preserve all Quick Selection links unchanged pending owner review, and preserve saved calibration profiles and faceplate behaviour.

## v2.7.60 — Compact Calibration targets and controls

- Split Calibration Target into three focused dropdowns: Misc Targets, RJ45 Targets and SFP Targets, retaining the existing single active selection, part handling and saved-profile schema.
- Compact editor controls to consistent input heights and reduced vertical padding; narrow numeric/hex boxes and colour swatches while retaining longer text-entry space where needed.
- No saved Calibration reset, forum write or mail action is performed.

## v2.7.59 — Optional LED outlines and bulk Status LED visibility

- Remove the default black SVG stroke from all rendered LED overlays, keeping their existing shapes, positions, fills and telemetry unchanged. In Calibration → Port Labels and LEDs, add optional per-profile LED outlines with colour and a bounded 0.25–3.00 thickness input in 0.25 increments; existing saved profiles default to off.
- Add Show All and Hide All immediately after the Status LED Text colour control. Both buttons use the existing per-profile status-LED hidden list, keep individual checkboxes functional, and do not change status LED styling or port calibration.
- Local-first candidate only; public Core remains v2.7.58 until separately authorized.

## v2.7.58 — HP 3500yl opt-in Port dB refresh

- Retire the generic optional Avaya ERS 3524GT-PWR+ faceplate assignment, retaining the sole reviewed Avaya PNG and factory profile without rewriting user-saved calibrations.
- Resolve the visible HP SFP click through Discovery's physical interface map before requesting optical refresh; do not dispatch a write from Calibration controls or copper port clicks.
- Require the live SNMP identity to contain both the 3500yl family and exact J8693A identifier before sending the fixed DOM refresh SET; a family-only match is insufficient.

- Add the Port dB status row to RJ45/uplink and SFP show/hide menus, retaining existing saved-field order and presenting fresh optical RX/TX dBm for the selected HP 3500yl optic only.
- Clicking a supported SFP invokes an administrator-only Home Assistant WebSocket action; the browser never receives stored SNMP write credentials or issues SNMP commands, while newly entered credentials are submitted to private Home Assistant storage.
- Implement a separate default-off SNMPv2c write credential in private Home Assistant storage. Bind the action to the generated HP J8693A 3500yl-48G device and physical optical interface, check live sysDescr/ifDescr and strictly DOM(1) before the single fixed SNMP SET, rate-limit requests, and confirm the updated timestamp before displaying new power.
- VCT/Other/unsupported diagnostic modes cannot send the SET. Read-only Discovery, unrelated models and normal interface polling remain unchanged.
- Local evaluation only until actual HP firmware DOM refresh and non-disruptive behaviour are independently field-validated.

## v2.7.57 — TP-Link JetStream experimental registry projection

- Project two reviewed Discovery exact-model candidates (TL-SG2428P and TL-SG2008P) into Core for consistent 24-RJ45/4-SFP and eight-RJ45 stock-visual assignments.
- Preserve the current native-image calibration renderer and all existing faceplates, while retaining unknown PoE telemetry/hardware-revision acceptance state.

## v2.7.56 — Avaya ERS 3524GT-PWR+ factory default

- Adopt the dedicated native-image `avaya-3524gt.png` and `avaya_3524gt` factory calibration as the exact-model default from Discovery, retaining the existing stock faceplate as an optional fallback.
- Preserve 24 physical copper sockets, four shared front SFP positions, IF-MIB combo mapping and existing renderer/calibration geometry; no new telemetry semantics or renderer replacement.

## v2.7.55 — Selectable Avaya 3524GT faceplate registration

- Register the owner-supplied 2925 × 323 Avaya ERS 3524GT-PWR+ artwork and its 24-RJ45/4-SFP calibration as a selectable bundled faceplate, without changing any model defaults or Discovery contracts.
- Convert the SW1 calibration workstation's render-space geometry to the new image's native coordinate space using the established native-image transformation; do not treat the SW1 Cisco factory identity as an Avaya binding.
- Retain the restored native-image renderer, existing combo-port semantics and other faceplate defaults; add registration, geometry and selection regression coverage.

## v2.7.54 — Selectable ROLE row in Port Status Box

- Move RJ45/SFP ROLE into the same Port Status Box field selector as PORT ID, with Show/Hide and Up/Down ordering, rather than unconditionally prepending a role row for uplinks.
- Preserve legacy visible uplink ROLE and its leading placement when loading saved profiles without ROLE in the stored field order; explicit hidden state and user-defined order remain authoritative afterward.
- Keep unknown roles suppressed, the two status boxes independent, existing UniFi/optical presentations and the Core 2.7.53 Port ID and SFP range features unchanged.

## v2.7.53 — Port ID status-field label

- Rename the optional RJ45/SFP Port Status Box field label from `PORT NUMBER` to `PORT ID` for a better visual fit.
- Preserve the existing internal `number` field key and the default-or-renamed port label behavior, along with the SFP range selection from 2.7.52.

## v2.7.52 — SFP calibration ranges and selectable Port Number status

- Support optical selection ranges such as `sfp1-sfp4`, `sfp+1-sfp+4` and existing SFP/uplink aliases, resolving only actual calibrated cages and reporting unavailable positions without inventing hardware.
- Add a Port Number field to the existing Port Status Box dropdown for RJ45 and SFP ports. Show the calibrated custom display name when set, otherwise the established faceplate port label; leave interface identities and telemetry mapping unchanged.
- Keep Port Number hidden until enabled so existing saved status-panel layouts remain visually unchanged, and preserve per-panel field ordering/visibility.
- Test parsing, naming, legacy-profile visibility and unchanged RJ45 range selection.

## v2.7.51 — Dell N4032F always renders all 26 optical positions

- Bypass stale/partial `sfp_port_count` visual capping only for the dedicated N4032F model/calibration profile, so SFP/QSFP positions 1–26 are always drawn.
- Keep normal count-driven rendering unchanged for Cisco 3650, Cisco 3850-12XS and every other model.
- Make N4032F positions 25–26 labels visible while preserving their supplied geometry, LED positions and 40G telemetry binding.
- Add Chromium regression coverage proving N4032F renders 26 positions with `sfp_port_count: 4` while Cisco 3850/3650 retain their existing count-capped behavior.

## v2.7.50 — Restore native-image calibration mapping

- Revert the local-only 2.7.49 fixed 2048 × 448 canvas experiment and restore the established faceplate renderer: image-defined canvas height, `height:auto`, and SVG `preserveAspectRatio="xMidYMid meet"`.
- Preserve the long-standing native-image calibration transform rather than changing the calibration workflow used by existing owner profiles.
- Keep the latest 1935 × 262 Dell N4032F artwork and project the owner-supplied 2048 × 448 geometry into that real native image canvas.
- Add a regression proving the Dell native-image projection maps SFP1–24 and QSFP25–26 to the same browser-space points as the legacy render-space geometry.
- Keep the native-resolution header reporting the active PNG dimensions.
- Retain the Cisco SG200-26 stock 24-RJ45 + 2-SFP visual correction and unchanged 26-interface contract.

## v2.7.49 — Stable 2048×448 faceplate render plane

- Fix the runtime image/SVG mismatch by giving the faceplate canvas a fixed 2048 × 448 aspect ratio and mapping both the faceplate image and SVG overlay to the same full canvas.
- Remove the SVG-only aspect-ratio transform so PNG native dimensions cannot make correct calibration coordinates appear larger, smaller or shifted.
- Keep the Dell N4032F owner geometry exactly in Switch Vision render space and separate its geometry coordinate contract from the active PNG's native-resolution metadata.
- Replace the Dell N4032F artwork with the latest owner-supplied 1935 × 262 dell-4032f.png while preserving SFP+ positions 1–24 and optional 40G QSFP positions 25–26 unchanged.
- Add permanent Chromium regression coverage proving that changing between 2172 × 724 and 1935 × 262 artwork does not move or resize the canvas, SVG overlay or mapped geometry.
- Retain the Cisco SG200-26 stock 24-RJ45 + 2-SFP correction and its unchanged 26-interface logical contract from the 2.7.48 candidate.

## v2.7.48 — Cisco SG200-26 stock 24+2 visual correction

- Project Discovery 3.0.23's corrected Cisco SG200-26 visual contract into Core's generated exact-model registry.
- Replace the SG200-26 oversized 48-RJ45 fallback with the existing `24rj45-2sfp.png` / `stock_24rj45_2sfp` stock presentation while preserving logical interfaces 25–26 through the existing SFP logical-port map.
- Add permanent regression coverage proving that the selected stock profile contains exactly 24 RJ45 geometry positions and two SFP cages for the SG200-26 presentation.

## v2.7.47 — Dell N4032F dedicated faceplate

- Add the dedicated Dell N4032F faceplate and owner-supplied 26-position optical geometry: SFP+ positions 1–24 plus optional 40G QSFP+ module positions 25–26.
- Preserve the exact supplied 2048 × 448 render geometry while storing the factory profile against the artwork's real 2172 × 724 native PNG canvas.
- Replace the generic N4032F UniFi optical fallback with the dedicated Dell faceplate/profile without changing its real-hardware 24-port base contract or optional QSFP parent-interface mapping.
- Prefer the corrected `qsfp_40g` entity namespace for positions 25–26 while retaining the earlier `rear_qsfp_40g` entity IDs as compatibility fallbacks for existing installations.
- Make the card header report the active faceplate image's actual native resolution instead of a fixed render-canvas value.
- Add permanent regression coverage for exact geometry round-trip, PNG dimensions, native-resolution display and N4032F QSFP entity binding.

## v2.7.46 — Generic VLAN membership presentation

- Render a discovered `allowed_vlans` / `vlans` membership list for any switch vendor when that trusted derived telemetry exists, instead of restricting multi-VLAN presentation to Juniper.
- Bind copper-port `native_vlan` and `vlan_mode` entities alongside the legacy VLAN/mode names so standards-based Q-BRIDGE native VLAN and ACCESS/TRUNK state are consumed consistently with existing SFP behavior.
- Preserve the established single native/access VLAN display when no membership list exists, and preserve Juniper's existing fallback behavior.
- Add a permanent behavioral regression covering a non-Juniper port with native VLAN 1 plus VLAN memberships 1,10,20 and a normal single-VLAN compatibility case.

## v2.7.45 — Persistent Test Mode activity isolation

- Keep persistent **Test Mode** active after **Done** exactly as before, so the saved faceplate remains available for unobstructed calibration inspection.
- While persistent Test Mode is active, suppress the independent live Activity LED animation/repaint loop so telemetry cannot flicker individual Activity LEDs or briefly repaint the whole Activity LED set.
- Resume normal live Activity LED animation automatically when Test Mode is explicitly turned off.
- Add source and maintained Chromium regression coverage that seeds live activity after **Done** and proves the Activity LED remains solid with no animation timer running.

## v2.7.44 — Persistent Test Mode full-topology rendering

- Keep every saved Calibration RJ45/SFP visual position rendered while persistent **Test Mode** is active after **Done**, even when the live switch's configured physical port counts are smaller than the custom faceplate topology.
- Preserve the normal live/runtime topology guard when Test Mode is off, so Switch Vision still never invents operational ports or telemetry outside the real configured switch contract.
- Add permanent source and Chromium coverage for the exact 4-SFP live-device / expanded saved-faceplate case that previously dropped extra Test Mode LEDs after Done.

## v2.7.43 — Calibration rendered-geometry and multi-port metadata corrections

- Make saved Link/Activity LED W/H calibration values affect Circle rendering as well as rectangle/triangle shapes, while preserving the stock default circle size when no custom size is saved.
- Allow **Supported speed** and **Port Role** to be edited for grouped RJ45/SFP selections, including all/odd/even/custom selections, with a **Mixed** state when selected ports differ.
- Preserve persistent Calibration Test Mode semantics: **Done** saves/closes while Test Mode stays active for unobstructed faceplate inspection, reopening Calibration keeps it active, and **Cancel** explicitly turns it off.
- Add source-level and maintained Chromium regressions that exercise resize -> rendered SVG geometry, grouped metadata mutation boundaries, and the complete Test Mode Done/reopen/Cancel lifecycle through the real Calibration UI.

## v2.7.42 — Calibration quick-label tooltip restoration

- Restore the explanatory hover text on the selected-port **Link LED** and **Activity LED** quick labels after the consolidated Calibration port-presentation-row refactor.
- Keep the existing Port Label → Link LED → Activity LED layout, visibility mutations, LED shape controls, saved calibration state and telemetry mappings unchanged.
- Add permanent regression coverage requiring all selected-port Port Label Style / Port Label / Link LED / Activity LED explanatory tooltips to remain present.

## v2.7.41 — Hardware contribution registry coordination

- Project Discovery's reviewed SG200-26 and UniFi Standard 24 / `USW-24-G2` exact-model contracts into Core's generated support registry.
- Add Core visual recommendations for SG200-26 using the safe oversized stock 48-RJ45 + 2-SFP canvas and for USW-24-G2 using the existing calibrated UniFi 24-RJ45 + 2-SFP inline faceplate.
- Carry refreshed USW-16-PoE, US 8 60W and USW Flex Mini support metadata from Discovery without changing their support states.
- Preserve all existing faceplate geometry, Calibration behavior and runtime telemetry resolution; this patch changes only generated exact-model registry/visual metadata and release versioning.

## v2.7.40 — Calibration-only Status LED default correction

- Restore factory calibration Status LED visibility and the stock faceplate presentation contract to their pre-2.7.37 behavior.
- Start Status LED checkboxes unticked only for a genuinely new Calibration editor working copy.
- Preserve every existing saved `ui.status_leds.hidden` list exactly, including an explicit empty list.
- Leave normal dashboard/runtime Status LED visibility, stock faceplate geometry/presentation, and the 2.7.37 layout unchanged.
- Add focused regression coverage for new-session defaults, saved-state authority, factory profile visibility, source mirror parity, and the stock presentation hash.

## v2.7.39 — Release-contract synchronization

- Carry forward Core 2.7.38 shared-SFP selected-status behavior and the 2.7.37 Calibration layout/default changes unchanged.
- Synchronize the stock 48-port factory presentation integrity lock with the intentional all-Status-LEDs-hidden default.
- No additional faceplate geometry, telemetry mapping, Calibration behavior, or management-theme behavior changes.

## v2.7.38 — Shared SFP selection telemetry consistency

- Keep a shared SFP/uplink selected as an SFP when dedicated SFP telemetry exists, so the selected-interface status panel uses the same authoritative telemetry as the rendered Link/Activity LEDs.
- Restore correct selected-port link state on the Avaya ERS 3524GT-PWR+ shared uplinks when dedicated `sfp_1g_*` entities disagree with the inactive copper-side logical-port entity.
- Preserve logical RJ45-port selection as the compatibility fallback for combo-port models that expose only shared access-port telemetry, including HP J9774A.
- Add permanent regression coverage for the dedicated-SFP click path and logical-port fallback.

## v2.7.37 — Calibration Port Labels/LED layout and Status LED defaults

- Put **Status LEDs** at the top of **Port Labels and LEDs**.
- Put **Port LEDs** directly below Status LEDs.
- Combine **Port Label Style**, selected **Port Label** Show/Hide, and selected Link/Activity LED shape + Show/Hide controls into one responsive Calibration row.
- Keep remaining port-label font size, bold, suffix, and colour controls below the compact presentation row.
- Make missing/default Status LED visibility hide every available chassis Status LED by default, while preserving any explicit saved `ui.status_leds.hidden` list.
- Update factory profiles that explicitly defaulted Status LEDs visible so their default checkbox state is fully unticked.
- Add regression coverage for section ordering, the single responsive presentation row, saved-visibility preservation, and factory Status LED defaults.

## v2.7.36 — Shared named custom management themes

- Add Core-owned `management_theme_selected` and `custom_themes` settings for the Switch Vision management UI.
- Validate up to 20 named custom themes with unique bounded ids/names and a complete 45-role `#rrggbb` colour palette.
- Project the selected theme and sanitized custom-theme library into shared UI preferences schema version 2 for Discovery / Hub and Installer.
- Preserve the four built-in theme identifiers while allowing `custom:<id>` selections only when the referenced saved theme exists.
- Keep management themes strictly separate from Native/Lovelace/Custom switch dashboards, faceplates, LEDs, port rendering, and Calibration.
- Add permanent validation for valid themes, malformed ids/names/colours, unknown roles, and invalid custom selections.

## v2.7.35 — Consolidate all Calibration Quick Select actions

- Move Port Labels, All Link LEDs, All Activity LEDs, RJ45 Link/Activity, and SFP Link/Activity quick targets back into **Selection** with the rest of Calibration's target shortcuts.
- Remove the duplicate Quick Select row from **Port Labels and LEDs** so that section contains presentation settings only.
- Preserve Port Label Style plus selected Port Label, Link LED, and Activity LED style/shape/visibility controls under **Port Labels and LEDs**.
- Add a permanent contract requiring every `data-cv-action="select-target"` control to live inside the Selection section.
- No calibration-data, telemetry, rendering, or per-interface LED-shape behavior changes.

## v2.7.34 — Per-port Link/Activity LED shapes and calibration layout

- Add independent per-interface `led_left_shape` and `led_right_shape` calibration fields for Link and Activity LEDs on RJ45 and SFP/uplink entries.
- Support Circle, Rectangle, Triangle Up, and Triangle Down, with the triangle variants rendered as tall, narrow arrowhead-style indicators.
- Keep legacy `ui.port_led_shape` only as a backward-compatible fallback for profiles that do not yet contain per-interface shape values.
- Add **All Link LEDs** and **All Activity LEDs** quick targets spanning both RJ45 and SFP/uplink ports, while preserving RJ45-only and SFP-only Link/Activity targets.
- Move Port Label Style, selected Port Label visibility, selected Link/Activity shape and visibility controls, and presentation quick targets into **Port Labels and LEDs**.
- Keep Selection focused on interface/geometry targeting rather than presentation styling.
- Persist the new shape fields through profile save/import and geometry transfer, with fail-closed validation for unsupported values.
- Add permanent regression coverage for shape rendering, persistence, cross-port targeting, UI section placement, source mirror parity, and existing label/LED behavior.

## v2.7.33 — Shared SFP telemetry preference repair

- Fix shared RJ45/SFP cage resolution so dedicated SFP telemetry is preferred when Discovery provides it, instead of stopping at the shared logical copper-port entities.
- Restore Avaya ERS 3524GT-PWR+ SFP link/status, speed, traffic, activity and selected-port telemetry for its four shared logical ports 21–24 while preserving one logical interface per combo position.
- Keep logical-port fallback unchanged for combo-port models that expose only the shared access-port telemetry, including the HP J9774A contract.
- Add permanent shared-SFP regressions covering dedicated 1G SFP telemetry, fallback behavior, activity and speed/detail resolution.
- No physical topology, model-support status, faceplate geometry or Calibration contract changes.

## v2.7.32 — Exact registry alignment and HP 2530-8G-PoEP contract

- Align Core's exact-model registry one-for-one with Discovery for all previously registered switches, including UCG Fiber and WS-C2960XR-48LPS-I, and remove stale support-confidence drift.
- Add the exact HP J9774A 2530-8G-PoEP Experimental contract from reviewed real-hardware evidence: eight fixed 1G PoE+ copper ports plus two dual-personality 1G RJ45/SFP logical ports.
- Use the existing stock 24-RJ45/2-SFP faceplate as the safe presentation fallback while limiting the generated card to ten active RJ45 positions and two SFP cages.
- Bind the two SFP cages back to logical ports 9 and 10 through the existing shared-cage mapping contract so link state, speed, traffic, activity and selected-port details remain one logical interface per combo position.
- Add permanent exact-model faceplate/logical-port regression coverage.

## v2.7.31 — Contributed Dell/Avaya operational bindings

- Add the exact Avaya ERS 3524GT-PWR+ Core registry/visual contract using the stock 24-RJ45/4-SFP faceplate, preserving 20 fixed copper ports plus four shared front combo positions.
- Add the exact Dell N4032F Experimental visual contract using the reviewed 32-position optical fallback: 24 front SFP+ positions plus two observed rear QSFP parent connectors at positions 25-26 when the expansion is present.
- Keep N4032F breakout lanes as logical child interfaces rather than inventing eight extra physical sockets; a base chassis without the rear module renders only 24 optical positions.
- Extend N4032F status/speed/traffic entity resolution so faceplate positions 25-26 consume the real 40G rear-QSFP entities.
- Add Dell N2128PX-ON selected-SFP optical diagnostics for the proven DDMI/transceiver entities while retaining its dedicated Dell 28-RJ45/2-SFP+ faceplate.
- Keep the HP 3500yl current front-panel visual unchanged; its separately observed rear A1-A4 module remains outside current faceplate geometry until dedicated presentation exists.
- Add permanent registry, faceplate-binding and optical-status regressions for these contracts.

## v2.7.30 — HP ProCurve 1810G-24 exact faceplate and factory calibration

- Add the exact HP ProCurve 1810G-24 faceplate as the default visual for the existing exact model contract.
- Add its owner-calibrated 24 × RJ45 + 2 × SFP factory geometry in the standard 2048 × 448 render coordinate space.
- Keep the stock 24RJ45+2SFP faceplate available as an optional fallback without changing the established physical/telemetry contract.

## v2.7.29 — Unified Port Label styles, per-port LED visibility and hardware-style activity flicker

- Supersede the unreleased 2.7.28 same-version local candidate so standard update detection installs the finalized source rather than treating an older 2.7.28 build as Latest.

- Add **Port Label Style** with Static, Activity, and Link speed modes for RJ45 and SFP/uplink labels.
- Keep Static as the backward-compatible default and preserve existing RJ45/SFP static label colours.
- Make Activity-style labels consume the same per-port activity decision as the Activity LED so both remain synchronized.
- Reuse the existing link-speed palette and custom link-LED colour override for Link speed mode.
- Normalize selected-port Calibration wording to **Port Label Style** followed by **Port Label** Show/Hide regardless of port type.
- Preserve existing type-specific visibility persistence internally for saved-profile compatibility.
- Keep **Port Label Style** and **Port Label** controls visible whenever an RJ45 or SFP/uplink port target is selected, regardless of the currently selected editable part.
- Add per-selected-port **Activity LED** Show/Hide and **Link LED** Show/Hide immediately after Port Label; persist those choices per port while retaining the existing profile-wide LED switches as master controls.
- Add explanatory tooltips for the selected-port Port Label Style, Port Label, Activity LED and Link LED controls without changing saved geometry or telemetry mappings.
- Cache visible activity targets after redraw and stop the activity timer completely when no Activity LED or Activity-style label is visible.
- Update LED-only and Activity-label-only modes only at their visible target; when both are visible, reuse one per-port activity decision.
- Tune heavy/Fast activity at the existing 120 ms factory setting to approximately **125–140 ms ON / 29–40 ms OFF**, about **6 flashes/sec** and roughly **80% ON duty**.
- Use a 25 ms internal activity render sample only while visible activity targets are active so the short Fast drop-outs remain perceptible.
- Add permanent regressions for persistence, RJ45/SFP parity, activity synchronization, Fast timing, hidden-work suppression, JavaScript mirror parity, and render stability.

## v2.7.27 — Public attribution privacy hardening

- Remove unapproved contributor/tester identities from current and carried public release history.
- Remove identity-specific names from public-source regression filenames, comments, output strings, and variable labels.
- Keep technical validation facts while using neutral community attribution unless zemerdon explicitly approves exact public credit.
- Strengthen release/publication privacy gates so carried historical release content is scanned fail-closed before publication.
- No telemetry, device mapping, faceplate, calibration, or runtime behaviour changes.

## v2.7.26 — Exact-model, combo-port and Cisco telemetry release

- Publish the exact WS-C3750X-48P-S Experimental contract and HP ProCurve 1810G-24 dual-personality contract already validated on local main.
- Preserve shared logical-port state/details between RJ45 and SFP hitboxes for dual-personality ports while keeping Calibration geometry independent.
- Complete 1G SFP VLAN/trunk/alias/description/name binding through the explicit entity-prefix contract.
- Aggregate real Cisco ENVMON fan/PSU state entities without inventing health when rows are absent.
- Show selected-port Cisco PoE state, class and power only when Discovery has an exact physical-port join; hide missing telemetry.
- Add permanent regression coverage for Cisco telemetry binding and fail-closed presentation.

## v2.7.25 — Dell visual-state metadata reconciliation

- Reconcile the Dell N2128PX-ON registry notes with the already-shipped dedicated 28 RJ45 + 2 SFP+ faceplate and owner-calibrated factory geometry.
- Record current-build field confirmation for Dell faceplate alignment and port-description presentation without changing its Experimental support status.
- Keep only the evidence-backed remaining promotion blockers: detailed per-port PoE presentation, system-sensor applicability, and VLAN/trunk semantics.
- Add a permanent regression that rejects stale generic-fallback or pending-Dell-calibration wording.

## v2.7.24 — Dedicated USW Flex Mini faceplate

- Add the owner-calibrated USW Flex Mini factory faceplate and dedicated usw_flex_mini calibration profile.
- Move only USW Flex Mini from the generic five-RJ45 UniFi presentation to the dedicated artwork while preserving the proven 5 × 1G RJ45 / no-uplink functional contract.
- Preserve the supplied five RJ45 hitboxes, LEDs, port numbers, status-box selection and UI geometry as presentation data; exact model capabilities remain registry-owned.
- Add permanent regression coverage for the supplied geometry round-trip and Flex Mini-only assignment.

## v2.7.23 — Compact UniFi exact-model faceplates

- Add owner-calibrated UniFi **16 RJ45 + 2 SFP**, **9 RJ45 + 2 SFP**, and **3 SFP+** factory faceplates.
- Replace oversized generic visuals for USW-16-PoE, US 16 PoE 150W, UDM Pro, UniFi Dream Machine PRO SE, UDM Pro Max, and USW WAN.
- Keep shared faceplate geometry role-neutral so exact-model WAN/LAN and speed semantics remain registry/runtime-owned; the existing UDM Pro RJ45 port 9 WAN default is preserved.
- Preserve the USW WAN rear RJ45 as real API port 4 while rendering only its three front 10G SFP+ cages.
- Add permanent geometry/model regressions for native-canvas integrity, exact assignments, role neutrality, and the USW WAN rear-port/front-panel split.

## v2.7.22 — Rendered calibration control target alignment

- Keep the on-card **Calibrate/Done** and **TEST MODE** controls exactly where they render today.
- Make Calibration target boxes derive from the controls' real rendered browser bounds through the SVG screen transform, so the blue targets stay directly over the controls on unusually wide or non-2048:448 faceplates.
- Preserve the TEST MODE target geometry even while the badge is inactive by retaining a hidden rendered marker at its real position.
- Add a permanent regression contract proving rendered-control synchronization occurs before the Calibration overlay is drawn.
## v2.7.21 — Calibrated port roles

- Add a persistent per-port **Port Role** selector beside **Supported Speed** in Calibration with Auto / Model default, LAN, WAN and Uplink choices.
- Preserve per-device role overrides in calibration metadata while Auto inherits exact-model registry role metadata.
- Expose known effective port roles in selected-port status details without treating UniFi uplink markers as implicit WAN classification.
- Add validated exact-model `port_roles` metadata and record UDM Pro physical RJ45 port 9 as WAN from owner calibration.
- Add permanent regression coverage for Calibration placement/persistence and embedded exact-model role metadata.
## v2.7.20 — Calibration font-size pixel controls

- Fix native-canvas Calibration font-size fields showing scaled storage values such as `38.0859375`, `39.55078125`, `46.875`, and `48.33984375` instead of their effective rendered pixel sizes.
- Show and edit font sizes consistently in the 2048×448 render space: stock native profiles now display familiar values such as RJ45 **13 px**, SFP/uplink **13.5 px**, Status LEDs **16.5 px**, and Status Boxes **16 px**.
- Convert edited render-space pixel values back into native-image storage units internally, preserving existing 6000×1325 calibration geometry without exposing that conversion to users.
- Scale native-profile font validation bounds with the faceplate coordinate ratio so valid rendered sizes above ~17 px are no longer accidentally clamped by the old raw-storage 50-unit ceiling.
- Fix Status Box 2 font-size editing so its profile value and temporary render override use the correct respective coordinate spaces.
- Add maintained Chromium coverage that verifies native stored values display as 13 / 13.5 / 16.5 / 16, edits round-trip through native storage, and render back at the exact requested pixel sizes.

## v2.7.19 — Card-height viewport sizing

- Rework Calibration **Card Height** so presets control the card viewport rather than resizing or vertically distorting the faceplate artwork.
- Keep the faceplate at its normal width and natural aspect ratio, keep the SVG overlay on the standard 2048×448 mapping, and center the full faceplate canvas behind the shorter/taller viewport.
- Use the existing stage overflow mask to crop only excess top/bottom content when the selected viewport is shorter than the natural faceplate render height.
- Keep the on-card Calibrate / Done control reachable in fixed-height mode with a viewport-relative placement, while Auto continues to use its saved calibrated position.
- Preserve the existing per-switch persistence contract, YAML isolation, 80–1024 px Custom bounds, and Compact 115 / Medium 150 / Large 200 presets.
- Extend maintained Chromium coverage to prove card width and faceplate image height stay unchanged while only the stage viewport height changes and the 150 px value still survives save/reload.

## v2.7.18 — Exact-height faceplate sizing

- Change Calibration **Faceplate Height** so it changes only the rendered height; the card keeps its normal width instead of shrinking proportionally.
- Vertically map the faceplate image and SVG overlay to the selected height so ports, LEDs, labels and calibration controls remain aligned at Compact 115 px, Medium 150 px, Large 200 px or Custom 80–1024 px.
- Keep **Auto** unchanged and preserve the existing global width behavior when no per-switch height is selected.
- Retain the 2.7.17 save/reload persistence repair so the selected height survives Save Profile / Done and later Home Assistant profile reloads.
- Add maintained Chromium checks proving every preset leaves card width unchanged, applies the exact requested image height, switches SVG mapping only for fixed-height mode, and persists 150 px end to end.

## v2.7.17 — Per-switch faceplate height calibration

- Add a Calibration-only **Faceplate Height** control saved with each switch/card profile; existing cards remain unchanged because **Auto** is the default.
- Add **Compact (115 px)**, **Medium (150 px)**, **Large (200 px)** and **Custom** presets, with Custom clamped to a hard 80–1024 px range.
- Preserve faceplate aspect ratio by translating the selected height limit into an effective maximum card width after the image dimensions are known, rather than stretching or squashing the artwork.
- Keep the setting out of Lovelace/YAML card configuration and out of transferable faceplate geometry/import payloads so it remains presentation state owned by the destination switch/card.
- Fix the pre-release save/reload path so the selected height does not revert to Auto after **Save Profile** or **Done**; normal stored calibration validation preserves `ui.faceplate.max_height`, while transferable faceplate/geometry imports continue to exclude it.
- Extend maintained browser regression coverage for Auto, every preset, Custom, the 80 px minimum clamp, ignored YAML attempts, and an end-to-end 150 px save/reload through mocked Home Assistant storage.

## v2.7.16 — Stock 48-port faceplate presentation repair

- Promote zemerdon's supplied calibrated `48rj45-4sfp` geometry to the stock factory default, including corrected RJ45 placement, explicit SFP label anchors, and the `G1`, `G2`, `G3/TE3`, `G4/TE4` visible uplink labels.
- Restore the standard 13 px RJ45 numbers, 13.5 px SFP labels, and 16.5 px status labels on both stock 48-port faceplates instead of allowing missing native-canvas presentation metadata to collapse those labels to the 8 px renderer minimum.
- Keep the stock `48rj45-2sfp` port geometry unchanged while adding only the missing explicit presentation metadata and label visibility contract.
- Add a permanent factory-geometry regression that proves the stock 48-port/4-SFP render-space geometry exactly matches the accepted owner-supplied geometry snapshot and both stock 48-port plates retain the standard label sizes.

## v2.7.15 — Calibration profile deletion bridge

- Add an admin-only Home Assistant WebSocket command for deleting one unused calibration profile so the Switch Vision Hub can use the same authenticated control path as its existing calibration reads.
- Reuse the existing protected deletion implementation for both the service and WebSocket contracts, preserving factory-profile and active-profile deletion safeguards.
- Return explicit deletion results to Hub callers so bulk profile cleanup can fail visibly instead of reporting success after an inaccessible service call.

## v2.7.14 — Faceplate geometry integrity and upgrade repair

- Make each shipped faceplate the primary authority for its factory/default geometry instead of allowing broad port-count/profile fallbacks to substitute another layout.
- Restore the USW Pro Max 24 to its original standard `unifi-24p-rj45-2sfp.png` / `unifi_24p_rj45_2sfp` visual contract.
- Add the missing `unifi_8_rj45_2sfp` and `unifi_32sfp` factory bindings and route legacy Cisco profile aliases to their current faceplate-native geometry.
- Automatically repair saved profiles only when their complete persisted presentation fingerprint exactly matches a reviewed obsolete factory default; preserve any genuinely user-adjusted calibration.
- Give the Native dashboard summary/version/menu header a fixed high-contrast foreground/background pair independent of custom Home Assistant theme token combinations.
- Add permanent all-faceplate/model geometry integrity coverage across the 17 shipped faceplates and dashboard-supported exact-model recommendations.

## v2.7.13 — Natural independent Activity LED flicker

- Replace the fixed repeating Activity LED metronome with deterministic irregular per-port flicker driven only by real RX + TX counter movement.
- Preserve Slow / Medium / Fast utilisation classification, sensitivity presets, custom thresholds, hysteresis and saved period settings; the three period values now control average flicker cadence rather than an exact repeating cycle.
- Keep light traffic as occasional short flashes, medium traffic as frequent irregular flicker, and heavy traffic as a dense mostly-on shimmer with short uneven drop-outs.
- Keep the link LED solid and authoritative, retain the existing poll cadence, and use Activity Hold only to keep the last real activity sample valid between slower telemetry updates.
- Add permanent browser/runtime regression coverage for irregular timing, independent per-port patterns, traffic-density ordering, retained-LED updates and clean expiry.

## v2.7.12 — Custom asset backup classification

- Package an exact SHA-256 manifest of release-owned logo and faceplate assets so Core can distinguish stock visuals from user data at runtime.
- Extend the narrow asset-list backup contract to advertise only truly custom logo/faceplate files to complete backups, avoiding repeated export of the full stock visual library.
- Treat a stock-named file whose content differs from the packaged stock SHA-256 as custom user data so local overrides are preserved.
- Fail the complete-backup capability back to the older API level if the stock manifest is missing or invalid; normal asset listing remains fail-soft.
- Preserve rendering, Calibration geometry, device support and credential handling unchanged.

## v2.7.11 — Portable backup asset bridge

- Add a narrow admin-only Home Assistant WebSocket bridge for exporting and restoring Switch Vision-owned custom logo and faceplate files used by complete configuration backups.
- Keep the bridge confined to `/config/www/switch-vision/{logos,faceplates}` with basename/extension validation, a 16 MiB per-file limit, SHA-256 integrity checks and atomic replacement.
- Advertise backup API capability through the existing asset-list contract so Discovery can fail closed rather than silently create or restore an incomplete whole-stack backup against an older Core.
- Preserve the existing renderer, faceplate geometry, Calibration presentation and dashboard behavior; no credential storage or broad `/config` filesystem access is introduced.

## v2.7.10 — Renderer and Calibration stability

- Gate Home Assistant updates by the entities each card actually consumes and coalesce relevant bursts to one visual commit per affected card/frame.
- Replace whole-SVG activity animation redraws with retained LED updates; idle and detached cards no longer run continuous activity redraw work.
- Pause telemetry rendering while Calibration is open, then resynchronize once from the newest Home Assistant state when Calibration closes.
- Single-flight UI-settings/profile subscriptions and profile loads, reject stale profile responses from overwriting dirty editor state, and clean timer/subscription lifecycle across disconnect/reconnect.
- Keep delayed status/copy housekeeping and continuous colour previews from rebuilding the complete Calibration editor or replacing active controls.
- Add permanent browser/runtime coverage for ten-card relevance/burst behavior, activity start/expiry, Calibration control identity, stale-load protection, detached staging and subscription cleanup.
- Preserve visible Live and Calibration SVG presentation; the accepted HAOS candidate showed the same visible output while eliminating the previous main-thread redraw storm.

## v2.7.9 — Exact-model faceplate mapping integrity

- Replace stale oversized visual fallbacks with already-shipped exact UniFi faceplates for `USW Flex`, `USW Flex Mini`, `USW-Lite-8-PoE`, `USW-Enterprise-8-PoE`, `USW Pro XG 8 PoE`, and `USW Pro HD 24 PoE`.
- Enable the existing owner-calibrated 32-position optical faceplate/profile for `USW Pro Aggregation`, preserving its authoritative 28 × SFP+ + 4 × SFP28 topology and API-port map.
- Enable the approved stock 24+2 canvas for `US 16 PoE 150W` while preserving its authoritative 16 RJ45 + 2 SFP physical counts; no nonexistent 16-port artwork is invented.
- Add permanent exact-model regressions that lock faceplate/profile pairs, preserve known-good compact UniFi mappings, and keep non-exact fallback models' physical counts authoritative.
- Keep support-confidence states unchanged; this release corrects presentation assignments only and does not promote hardware validation status.

## v2.7.8 — Hybrid UniFi telemetry and presentation integrity

- Add hybrid UniFi runtime binding so an SNMP-backed card can consume fresh UniFi API metadata without replacing SNMP link/activity/counter behavior.
- Reject stale retained UniFi telemetry using producer freshness metadata and show a bounded stale/unavailable warning instead of presenting old API values as live.
- Keep runtime entity/API mappings separate from presentation: stock faceplate/profile labels remain unchanged by telemetry mapping, with calibration remaining the supported presentation override.
- Preserve the existing full-width rendering contract and existing closest-fit faceplate assignments; no new faceplates or calibration workflow changes are introduced.

## v2.7.7 — Native Auto full-width correction

- Remove the native Switch Vision panel's fixed 1280 px page ceiling so **Auto** can use the full Home Assistant content width while the card itself retains its existing 2048 px native maximum.
- Preserve the explicit 800 px, 1024 px and Custom faceplate-width caps, centred card rendering, proportional calibration geometry and mobile responsiveness.
- Repair stale Core UI/UX regressions so they resolve the current release dynamically and assert the current Config Flow implementation instead of 2.6.34-era source formatting.
- Add permanent coverage preventing the native panel wrapper from reintroducing a fixed maximum width around Auto mode.

## v2.7.6 — UniFi 8-port visual mapping corrections

- Map exact `US-8-150W` to the already shipped owner-calibrated `unifi-8-rj45-2sfp.png` / `unifi_8_rj45_2sfp` visual, matching its proven 8 × RJ45 + 2 × 1G SFP physical contract without changing Experimental support confidence.
- Map exact `US 8 60W` to the already shipped `unifi-8rj45.png` / `default_unifi_8_rj45` visual, matching its proven eight-RJ45/no-uplink physical contract and preserving its ports 5-8 PoE evidence.
- Keep model-specific live rendered alignment pending for both mappings; the release removes oversized stock fallback visuals but does not claim Community Validated visual confidence.
- Add a permanent exact-model regression so these two models cannot fall back to a 24-port stock faceplate again.

## v2.7.5 — Shared management width and density scales

- Expand the shared Discovery/Installer **UI density** contract from three values to five: Spacious, Comfortable, Compact, Dense, and Ultra Dense.
- Expand the shared Discovery/Installer **content width** contract from Standard/Wide/Full to ten ordered positions from Standard through Full, preserving the existing `standard`, `wide`, and `full` values for upgrade compatibility.
- Keep the same values valid through Home Assistant options, Hub settings read/write, the shared preference file, and the `set_ui_density` service so Discovery and Installer consume one authoritative presentation contract.
- Add permanent Core regression coverage for both expanded scales without changing dashboard-card geometry, model metadata, calibration data, or device support state.

## v2.7.4 — Catalyst 3850 12XS Community Validated

- Promote `WS-C3850-12XS-E` from Experimental to **Community Validated** after three materially independent real-hardware capture sessions agree on the exact 12 × 10G SFP+ factory/no-module topology and current live rendered field confirmation passes.
- Record repeatable Cisco ENVMON temperature, fan and power-supply state evidence, while keeping RJ45, PoE and stack capabilities explicitly not applicable for this exact model.
- Mark the existing `cisco-3850-12xs.png` / `cisco_3850_12xs` visual recommendation as Community Validated without changing its owner-supplied 2048 × 448 geometry or physical-port contract.
- Extend the exact-model regression so the 3850 support and visual confidence cannot regress independently.

## v2.7.3 — US XG 16 Experimental evidence promotion

- Promote `US XG 16` from Detected to **Experimental** after corroborating independent real-hardware UniFi API evidence confirms its exact optical-first 12 × 10G SFP+ + 4 × 10G-capable RJ45 contract.
- Preserve the authoritative UniFi API map (ports 1-12 optical, 13-16 RJ45), no-PoE contract, owner-calibrated faceplate/profile, and all existing port/speed semantics.
- Keep the model's visual confidence **Detected** until model-specific live rendered alignment/behavior is confirmed; this support-status promotion does not claim Community Validated.
- Extend Core registry/faceplate regressions so support confidence and visual confidence cannot be accidentally collapsed into one status.

## v2.7.2 — Walk-backed model registry sync and 3850 Status Box 1 correction

- Restore the owner-supplied Cisco Catalyst 3850 12XS Status Box 1 horizontal geometry: render-space X returns from the accidental clamped `0` to `-337` while Y/width/height, all 12 SFP positions, LEDs, buttons and faceplate artwork remain unchanged.
- Add every exact real-hardware walk/API-backed model already present in the current Discovery registry but missing from Core, keeping those entries Experimental and preserving their existing topology/evidence/visual metadata.
- Add the walk-backed Zyxel GS1915-24EP exact model contract with 24 copper ports, zero optical uplinks and PoE capability; visual alignment remains Experimental and the oversized stock canvas cannot create phantom uplinks.
- Add permanent regressions for the 3850 Status Box 1 owner coordinate and Core retention of the walk-backed registry set.

## v2.7.1 — Field follow-up: live Test Mode and exact 3850 default

- Fix the live TEST MODE badge to render from the current working calibration instead of a nested calibration-button object, so its real position follows Calibration immediately.
- Add the exact Experimental `WS-C3850-12XS-E` Core visual recommendation: 0 RJ45 + 12 SFP, existing `cisco-3850-12xs.png` faceplate, and `cisco_3850_12xs` profile.
- Replace the incorrect 3850 factory geometry with the owner-supplied 2048 x 448 render geometry while preserving native-PNG storage, factory bounds and physical-topology authority.
- Strengthen permanent regressions so the 3850 cannot fall back to a generic 48-port visual and the live Test Mode path cannot regress to nested UI state.

## v2.7.0 — Test Mode position persistence and 3850 12XS coordination

- Make the Calibration Test Mode button a position-only target with both Direct X/Y and arrow/nudge movement while keeping resize and pointer-drag disabled.
- Render the live TEST MODE badge from the current working calibration so position changes apply immediately before save.
- Preserve Test Mode button position through calibration export, save/reload, reset and persisted fingerprints with permanent regressions.
- Carry the reviewed Cisco Catalyst 3850 12XS factory-geometry binding while preserving physical topology as the authority and coordinating exact device support with Discovery 2.4.0.

## v2.6.35 — Calibration state, target stability and 3850 12XS faceplate

- Make Save Profile reflect the actual persisted profile difference from the last loaded/saved baseline, including returning to clean when every change is reverted.
- Keep rapid Target/Part/Step and related editor selection stable across Home Assistant setConfig refreshes so the latest Calibration target remains selected.
- Make the Test Mode button visibly selectable as an arrow/nudge-only Calibration target, with no drag or direct coordinate/size editing.
- Add the calibrated Cisco Catalyst 3850 12XS faceplate and supplied 12-SFP / 7-status-LED factory geometry without inferring device support or live topology.
- Extend native-canvas normalization to Test Mode button geometry and the canonical faceplate catalog to the new 3850 12XS identity.
- Add permanent regressions for dirty-state change/revert semantics, target stability, Test Mode selection/nudge-only behavior, catalog identity, geometry and the no-phantom-topology boundary.

## v2.6.34 — Auto faceplate scaling

- Restored the original responsive card-sizing behaviour as the new Auto faceplate-width default.
- Preserved explicit 800 px, 1024 px and Custom maximum-width choices.
- Auto fills available Home Assistant width while never upscaling beyond the native 2048 px faceplate canvas.
- Clarified card header rendered sizing versus native artwork dimensions.

## v2.6.33 — Core UI/UX consistency batch

- Added persistent transparent Status Box background toggles without discarding selected colours.
- Added independent per-profile Link LED and Activity LED visibility controls.
- Added global 800 px / 1024 px / custom faceplate width settings with responsive proportional rendering.
- Normalized Calibration faceplate display names to explicit RJ45/SFP media counts.
- Fixed Test Mode button Target Entity arrow/nudge movement parity with the Calibration button.
- Allowed zero-port calibration profiles to save with a visible non-blocking warning.

## v2.6.32 — UniFi 32-port optical identity

- Correct the owner-calibrated UniFi optical faceplate identity from `unifi-28sfp` to canonical `unifi-32sfp`; its existing geometry already contains 28 × SFP+ plus four SFP28/TWE positions.
- Preserve the exact 32-position calibration geometry and `TWE1`–`TWE4` display mapping at optical positions 29–32.
- Keep one canonical physical faceplate/profile copy while resolving legacy `unifi-28sfp.png` and `unifi_28sfp` references to the new identity.
- Migrate legacy saved faceplate-specific calibration storage tokens to the canonical 32-port identity without discarding the legacy stored record.
- Extend permanent faceplate/catalog/legacy-compatibility regressions.

## v2.6.31 — Canonical faceplate catalog

- Add canonical machine-readable `src/faceplates/catalog.json` covering every shipped faceplate and its approved human-readable Calibration label.
- Render shipped Calibration faceplate labels from the catalog-backed mapping while preserving exact faceplate filenames as the runtime/profile identity.
- Make the Core build validate catalog schema/coverage and synchronize the catalog mapping into packaged runtime assets.
- Add product-owned deterministic release-check tooling with exactly pinned release-check dependencies.

## v2.6.30

- Added an independent persisted Calibration target for the TEST MODE status indicator.
- Compacted Calibration editor utility controls while preserving 24px form controls and faceplate geometry.

## v2.6.29 — UniFi faceplate factory defaults

- Bundle owner-calibrated `unifi-8-rj45-2sfp.png` and `unifi-28sfp.png` faceplates.
- Add exact faceplate-specific factory defaults for the 8-RJ45 + 2-SFP and 28-SFP + 4-TWE optical layouts.
- Preserve `TWE1`–`TWE4` display names for optical positions 29–32 on the 28SFP faceplate.
- Keep these defaults scoped to the exact faceplate filename; do not reassign existing exact-model recommendations.

## v2.6.28 — Supported speed selector persistence

- Fix the Calibration Supported speed change handler referencing an undefined `editable` variable.
- Resolve the current RJ45/SFP editable target at change time before writing `supported_speed`.
- Preserve the existing profile save/reload format, duplicate-port metadata inheritance and Unknown / Not specified backward-compatible default.
- Keep static supported-speed capability separate from live negotiated-speed telemetry and entity mapping.
- Add permanent regression coverage that requires the editable lookup before the speed metadata write.

## v2.6.27 — Calibration Port Manager workflow and port metadata

- Merge Assets into Selection and remove the standalone Assets Calibration section.
- Put Quick select before the Status Box quick-selection controls.
- Rename Labels & LEDs to Port Labels and LEDs, Interface Status Box to Port Status Box, and Switch & Stack to Switch and Stack Manual Override.
- Add 100 px and 200 px movement steps.
- Add Remove All RJ45 Ports and Remove All SFP Ports while preserving the central no-total-ports save/import validation contract.
- Add persistent per-RJ45/SFP Supported speed metadata with Unknown / Not specified as the backward-compatible default; new ports start unknown and duplicates retain source metadata.
- Add a per-profile Port Status Output selector for Status Box 1 or Status Box 2, defaulting existing profiles to Status Box 1.
- Make port-status row ordering/visibility edit the currently selected output box and route selected-port details only to that box.
- Preserve canonical/Home Assistant JavaScript parity and extend permanent Calibration regression coverage.

## v2.6.26 — RJ45 entire-port label movement

- Treat the RJ45 number label as part of `Entire port` in the Calibration selection overlay.
- Move the RJ45 number label with the port centre and LEDs for individual, grouped, nudge and Direct X/Y whole-port operations.
- Preserve the existing duplicate-port geometry contract: newly duplicated RJ45 labels start centred on the new port box.
- Leave SFP/uplink whole-port behaviour unchanged because its label movement path was already complete.
- Add permanent regression coverage for RJ45 label membership and whole-port movement.

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

## Earlier verified releases (v0.9.0–v2.3.0)

## v2.3.0

- Establishes the Switch Vision Core v2.3 release line for expanded UniFi presentation work.
- Adds bundled UniFi and Ubiquiti logo assets for model-specific presentation and calibration use.
- Normalizes Cisco logo filenames to the consistent `cisco-<variant>` naming scheme.
- Migrates existing bundled Cisco logo references to the normalized asset names.
- Preserves existing Discovery, SNMP2MQTT, entity, calibration, faceplate, dashboard, Activity LED 2.0, and C3650 Status Box behaviour.

## v2.2.2

- Corrects stale Cisco 3650 factory Status Box value-column coordinates that caused MODEL, IP, CPU, TEMP, and POE rows to be clipped after a factory reset.
- Corrects the same stale value-column offsets in the legacy C3650 profile and Status Box 2 factory coordinates.
- Adds build-time bounds validation across every bundled calibration and faceplate profile so enabled factory status rows cannot ship outside their calibrated panel.
- Carries forward all Core v2.2.1 hardening and Activity LED 2.0 behaviour unchanged.

## v2.2.1

- Removes environment-specific management and stack state from the bundled Cisco 3650 factory calibration.
- Regenerates and validates the primary frontend C3650 factory calibration from the authoritative JSON profile so factory state cannot drift into the card bundle.
- Adds build-time factory-calibration privacy validation for management addresses, hostnames, credentials, instance identifiers, and site-specific stack members.
- Requires an explicit `-v/--version` for every Core build; implicit patch increments and `--bump` release builds are no longer allowed.
- Keeps independently-versioned Discovery examples unversioned instead of relabelling them with the Core release number.
- Corrects live-dashboard example text so it matches the enabled Calibration-button setting.
- Clarifies that Core, Discovery, Installer, SNMP2MQTT, and UniFi2MQTT advance on independent version lines.
- Adds a 4 MiB safety cap before the native dashboard reads/parses generated dashboard YAML.
- Carries forward Activity LED 2.0 behaviour from v2.2.0 unchanged.

## v2.2.0

- Promotes switch-port activity animation to a first-class Switch Vision Core setting instead of relying on hard-coded tuning.
- Keeps the existing RX + TX throughput calculation relative to negotiated link speed, but replaces the old 1% / 20% activity bands with configurable sensitivity presets and Custom thresholds.
- Adds **Low**, **Normal**, **High**, and **Custom** Activity LED sensitivity modes. Normal defaults to Medium at 0.10% link utilisation and Fast at 1.00%.
- Changes the default blink periods to 500 ms Slow, 250 ms Medium, and 120 ms Fast so normal network activity remains visibly alive.
- Adds configurable activity hold and threshold hysteresis; hysteresis reduces Slow/Medium/Fast band chatter near utilisation boundaries.
- Makes Activity LED settings integration-wide for Native, Community-strategy, and custom Switch Vision cards while preserving card/YAML values as the fallback if global settings are unavailable.
- Groups Switch Vision Core Options into Dashboard, Activity LEDs, Switch Vision Discovery, and Switch Vision Installer sections.
- Adds **Reset all Switch Vision Core settings to defaults** to the Options flow.
- Publishes Activity LED settings through the existing Switch Vision UI-settings websocket/event path and shared UI-preferences document for supported management interfaces.

## v2.1.5

- Adds an Experimental exact-model registry entry for **Zyxel XS1930-10** from the sanitized community Support My Switch evidence set.
- Adds card-side exact-model recognition for `XS1930-10` text so model-aware visual defaults can resolve when the model string is exposed.
- Uses the existing compact **8 RJ45 + 2 SFP** visual/profile as the closest temporary fallback until a Zyxel-specific faceplate is supplied.
- Aligns with Switch Vision Discovery v2.1.7, which adds the corresponding exact-model discovery, port mapping, PVID, traffic, CPU, memory, fan, and temperature support.
- Keeps the Zyxel model **Experimental** until the contributor completes post-update live validation on the real switch.

## v2.1.4

- Stops faceplate-specific saves from mirroring the entire calibration into the base switch profile.
- Keeps Status Box, layout, and faceplate-specific calibration data independent between faceplates.
- Stores the active faceplate selection separately without copying calibration content.
- Prevents a new or unsaved faceplate from inheriting the previously active faceplate layout.
- Adds migration handling for older mirrored faceplate state and regression coverage for profile isolation.
- Carries forward the v2.1.3 removal of obsolete Status Box fields `MEM`, `UP RX`, and `UP TX`.

## v2.1.3

- Removes the unused `MEM`, `UP RX`, and `UP TX` rows from the configurable switch Status Box field list.
- Keeps normal port/SFP `RX` and `TX` rows unchanged.
- Preserves existing memory and uplink RX/TX telemetry plumbing for future/non-Status-Box use.
- Adds a build-time regression guard preventing the retired rows from returning to the Status Box selector.

## v2.1.2

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

## v2.1.0

- Promotes the Switch Vision Hub UniFi2MQTT management path as the public 2.1 baseline.
- Adds a dedicated **UniFi2MQTT Settings** page in Switch Vision Hub for controller URL, Site ID, API key, SSL verification, polling interval, MQTT connection details, and MQTT topic prefixes.
- Preserves stored API keys and MQTT passwords without reading secret values back into the browser; blank secret fields keep the existing saved value.
- Lets the Hub install UniFi2MQTT when it is available but not yet installed, then save configuration and start or restart the app through Home Assistant Supervisor.
- Shows UniFi2MQTT installation/runtime state, controller configuration readiness, snapshot availability, and normalized device count in the Hub.
- Integrates normalized UniFi devices into the existing Devices and Diagnostics views and keeps UniFi Support My Switch data privacy-processed.
- Keeps SNMP/SNMP2MQTT support unchanged and keeps UniFi support optional.
- Establishes the Switch Vision Installer as the single repository end users need to add manually; UniFi2MQTT configuration belongs in Switch Vision Hub rather than the Installer.
- Carries forward all v2.0.36 sidebar live-update and stability fixes.

## v2.0.36

- Fixes the Switch Vision Installer ingress/sidebar icon disappearing when both Native and Lovelace Switch Vision sidebar entries are hidden.
- Replaces presentation-option full integration reloads with Home Assistant config-entry update listeners.
- Updates Native and Lovelace sidebar visibility in-place without removing/re-registering the Native panel.
- Keeps unrelated Home Assistant ingress/sidebar entries untouched while Switch Vision presentation options change.
- Adds build-time regression guards preventing presentation options from returning to full-reload behavior.

## v2.0.35

- Simplifies the Hub theme selector to four focused choices: Switch Vision, Cisco Classic, Cisco Nexus, and UniFi.
- Removes the Light, Cisco Catalyst, and System themes.
- Removes the Hub compact/density button; Discovery UI Density remains controlled by the existing Switch Vision integration setting.
- Keeps all theme styling isolated from Native, Lovelace, and Custom dashboards and switch-card rendering.
- Hardens generated SNMP2MQTT YAML validation against empty/malformed targets and sensors.
- Preserves the previous UniFi device snapshot entry when a single device detail/statistics refresh fails transiently.

## v2.0.34

- Stops Discovery from silently reusing historical SNMP walks when the current run did not create them; stored walks are now parsed only with explicit `parse_all_walks`.
- Rebuilds the SNMP capability cache from the current source set so removed SNMP devices do not linger in Devices/Diagnostics.
- Decouples dashboard-card generation from SNMP2MQTT generation so UniFi API-only runs generate fresh cards with zero SNMP inputs.
- Removes stale generated SNMP2MQTT YAML when a run has no active SNMP source and stops the generated-YAML SNMP2MQTT bridge when that file is retired by Discovery.
- Adds **Reset SNMP Discovery Data** in the Hub to stop SNMP2MQTT, retire identifiable retained Home Assistant MQTT Discovery entries, clear saved SNMP walks/capabilities/generated SNMP files, and preserve UniFi data/settings.
- Records exact generated SNMP2MQTT discovery topics (no credentials) so full or partial SNMP retirement can remove stale Home Assistant entities even after the active YAML is replaced/removed.
- Adds regression/self-test coverage for SNMP2MQTT retirement topic generation and UniFi-only source isolation.

## v2.0.33

- Adds a top-right management UI theme selector to Switch Vision Hub and all Discovery views.
- Adds seven choices: Switch Vision, Light, Cisco Classic, Cisco Catalyst, Cisco Nexus, UniFi, and System.
- Keeps the existing Switch Vision appearance as the default and stores theme choice per browser.
- Adds a top-right density icon tied to the existing Discovery UI Density preference.
- Lets the density icon toggle Comfortable/Compact while keeping the normal integration setting authoritative.
- Automatically reflects Compact/Dense state when Discovery UI Density changes elsewhere.
- Adds shared colour variables so Hub, Devices, Diagnostics, Support My Switch, Configuration, and UniFi2MQTT Settings change consistently.
- Keeps Native, Lovelace, Custom Switch Vision, switch cards, faceplates, ports, LEDs, and Calibration visuals completely outside the theme system.
- Adds build-time regression checks preventing management-theme code from leaking into dashboard runtimes.

## v2.0.32

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

## v2.0.31

- Adds `ifDescr` fallback for switches that omit IF-MIB `ifName`.
- Adds Experimental `S5720-12TP-LI-AC` 8-RJ45 + 4-SFP mapping support.
- Adds walk-aware 32-bit traffic-counter and `ifSpeed` fallbacks.
- Adds 1G SFP entity-name support to the card.
- Uses the generic 48-RJ45 + 4-SFP visual as the temporary Huawei fallback.
- Normalizes CR/trailing whitespace in SNMP identity values.
- Support/compatibility only; no new product features.

## v2.0.30

- Masks UniFi card IDs/names in Support My Switch dashboard YAML.
- Adds residual checks for leaked UniFi dashboard identity fields.
- Includes sanitized UniFi devices in contribution summaries and fingerprints.
- Makes diagnostics source-aware for UniFi API devices.
- Cleans up outdated generated-dashboard visual wording.
- No live card rendering or SNMP behavior changes.

## v2.0.29

- Imports normalized UniFi2MQTT devices into Discovery and generated dashboard cards.
- Adds live authenticated UniFi card data through the Switch Vision integration.
- Drives link/speed/PoE/system data from the UniFi snapshot while keeping per-port traffic disabled when unavailable.
- Keeps devices with missing generic visual profiles visible but does not generate incorrect cards for them.
- Existing SNMP/SNMP2MQTT paths remain unchanged.

## v2.0.28

- Adds Experimental `UDM Pro` gateway/switch-hybrid registry/profile support.
- Records live UniFi2MQTT validation for the existing UniFi switch models.
- Adds API model-pattern variants for `USW Enterprise 8 PoE` and `USW Pro 24 PoE`.
- Suppresses nominal/stale `speedMbps` values when a UniFi port is DOWN.
- Keeps PoE state independent from Ethernet link state.
- No SNMP2MQTT, card, calibration, polling, or sidebar behavior changes.

## v2.0.27

- Adds separate sidebar visibility controls for the automatic Native panel and the Lovelace/Community dashboard.
- Identifies Switch Vision Lovelace dashboards by strategy, so renaming them is safe.
- Applies the saved Lovelace preference to dashboards created after setup.
- No Discovery, SNMP2MQTT, UniFi2MQTT, card, calibration, polling, or registry changes.

## v2.0.26

- Fixes hiding of the original automatic Native Switch Vision panel.
- Uses Home Assistant's actual `show_in_sidebar` panel flag.
- Clarifies that the integration option controls only the automatic/native panel.
- User-created Switch Vision dashboards retain their own Home Assistant sidebar setting.
- No runtime data, Discovery, SNMP2MQTT, UniFi2MQTT, calibration, card, or registry changes.

## v2.0.25

- Registers the Switch Vision Community dashboard strategy as a Lovelace `module` resource, matching Home Assistant's required custom-strategy loading path.
- Automatically updates the versioned strategy resource and removes duplicate stale entries in Lovelace storage mode.
- Retains the existing Native panel and Custom dashboard fallback unchanged.
- No device registry, Discovery, SNMP2MQTT, UniFi2MQTT, polling, calibration, or card behavior changes.

## v2.0.24

- Fixes Home Assistant timing out while loading the Switch Vision Community dashboard strategy.
- Registers current and legacy strategy tags and makes duplicate resource evaluation safe.
- Adds build-time regression coverage for dashboard strategy registration.
- No runtime switch-data paths changed.

## v2.0.23

- Registers Switch Vision in Home Assistant 2026.5+ Community dashboards.
- Adds a real Lovelace dashboard path that can be selected as the Home Assistant default dashboard.
- Reuses the existing Native Switch Vision renderer/polling path instead of duplicating card-generation logic.
- Retains the current custom sidebar panel and generated YAML dashboard as independent fallbacks.
- Adds a versioned panel alias for safe frontend upgrades in long-lived browser sessions.
- Adds build-time version validation for the dashboard strategy resource.
- No Discovery, SNMP2MQTT, UniFi2MQTT, calibration, registry, or existing card behavior changes.

## v2.0.22

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

## v2.0.21

- Adds Experimental exact-model registry entry for `S5735-L8P4X-A1` from `[contribution reference withheld]`.
- Adds profile `huawei-s5735-l8p4x-a1`.
- Maps `GigabitEthernet0/0/1-8` as eight copper ports.
- Maps `XGigabitEthernet0/0/1-4` as four high-speed uplink candidates.
- Classifies Huawei `XGigabitEthernet` interfaces as physical `sfp_plus` interfaces.
- Adds a Huawei interface-classification regression test.
- Leaves PoE telemetry, sensors and final visual validation pending.

## v2.0.20

- Adds experimental `local_apps/switch_vision_unifi2mqtt`.
- Uses read-only UniFi Integration API `X-API-KEY` authentication.
- Publishes MQTT Discovery/state for model, online state, port state/speed/connector/PoE, CPU, memory, uptime and uplink rates.
- Writes normalized `/share/switch_vision/unifi/devices.json`.
- Adds Experimental registry entries for `USW Pro XG 8 PoE` and `USW Lite 16 PoE`.
- Validates normalization against supplied sanitized live API samples.
- Leaves SNMP2MQTT unchanged and retains SNMP for per-port RX/TX.

## v2.0.19

- Adds Experimental exact-model entry for `USW-Enterprise-8-PoE` from contribution [contribution reference withheld].
- Adds candidate mapping for `tw1`-`tw8` and `te1`-`te2`.
- Adds Experimental exact-model entry for `USW-Pro-24-PoE`.
- Adds candidate mapping for `0/1`-`0/24` plus candidate uplinks `0/25`-`0/26`.
- Extends the Ubiquiti vendor identity pack to recognize `USW-` and `UniFi Switch` sysDescr strings.
- Improves exact-model lookup for descriptive firmware suffixes such as commas after the exact SKU.
- Leaves UDM-Pro and generic Linux-based UniFi devices unregistered as switch profiles pending stronger evidence.
- No existing supported-device status is promoted or changed.

## v2.0.18

- Adds Experimental exact-model registry entry for Cisco `SG500X-24` from contribution [contribution reference withheld].
- Adds candidate SG500X profile for `gi1/1`–`gi1/24` and `te1/1`–`te1/4`.
- Adds Experimental exact-model registry entry for Huawei `S5720-12TP-LI-AC` from contribution [contribution reference withheld].
- Records Huawei `GigabitEthernet0/0/1`–`GigabitEthernet0/0/12` interface evidence while leaving media/uplink classification pending.
- Improves exact-model registry lookup for verbose vendor sysDescr strings.
- No existing supported-device status is promoted or changed.

## v2.0.17

- Removes the Sponsors link from Support My Switch.
- Adds a compact Sponsor chip with heart icon to the Switch Vision Hub page.
- No Discovery runtime, generated YAML, polling, activity LED, card, calibration, or installer behaviour changes.

## v2.0.16

- Fixes the Support My Switch Sponsors link being emitted as the literal `{GITHUB_SPONSORS_URL}` placeholder.
- Uses the official absolute Sponsors URL directly so Home Assistant Ingress does not treat it as a local path.
- No runtime Discovery, generated-output, polling, activity LED, card, calibration, or installer changes.

## v2.0.15

- Adds `.github/FUNDING.yml` for the `zemerdon` GitHub Sponsors profile.
- Adds a short Support the project section to README.
- Adds a discreet GitHub Sponsors link to Support My Switch.
- No Discovery runtime, generated YAML, polling, activity LED, card, calibration, or installer behaviour changes.

## v2.0.14

- Makes Generated Card YAML and Generated SNMP2MQTT YAML use the same rounded boxed container style.
- Aligns border, padding, background, spacing, summary width, and right-side chevrons.
- Presentation-only change; no Discovery runtime or generated-output changes.

## v2.0.13

- Aligns the collapse/expand arrows for Generated Card YAML and Generated SNMP2MQTT YAML.
- Normalizes summary-row width and box sizing so both right-side chevrons share the same effective right edge.
- Presentation-only change; no Discovery runtime or generated-output changes.

## v2.0.12

- Changes port activity classification from raw byte-delta logarithmic scaling to real port-utilization bands.
- Slow activity is below 1% utilization.
- Medium activity is 1% to below 20% utilization.
- Fast activity is 20% utilization and above.
- Retains the 750 ms / 350 ms / 180 ms slow/medium/fast blink periods.
- Uses measured sample timing and port speed for activity classification.
- Uses the existing 10 Gb/s ceiling for SFP activity.
- Reduces generated `activity_hold_seconds` from 30 seconds to 12 seconds for the 10-second traffic polling cadence.
- No Discovery switch detection, generated sensor naming, calibration, or installer behaviour changes.

## v2.0.11

- Moves the collapse/expand arrows for Generated Card YAML and Generated SNMP2MQTT YAML to the far right of each section header.
- Keeps section collapse/expand behaviour unchanged.
- No Discovery runtime, generated YAML, SNMP polling, card, calibration, or installer logic changes.

## v2.0.10

- Changes generated RX/TX traffic polling from 30 seconds to 10 seconds.
- Changes generated link/status polling to 30 seconds.
- Keeps VLAN/trunk polling at 30 seconds.
- Keeps slow system/interface polling at 300 seconds.
- Removes the temporary nested-editor Save reminder from Add/Edit Switch and Add/Edit Stack Member.
- Retains the v2.0.7 Stop Discovery control, v2.0.6 traffic-rate sanity guard, and v2.0.5 fresh-install Discovery defaults.

## v2.0.9

- Separates the two-step Save reminder from the final field help text with a blank line.
- Applies the same presentation to Add/Edit Switch and Add/Edit Stack Member.
- No Discovery runtime or generated-output behaviour is changed.
- Retains the v2.0.7 Stop Discovery control, v2.0.6 traffic-rate sanity guard, and v2.0.5 fresh-install Discovery defaults.

## v2.0.8

- Restores the two-step Home Assistant Save reminder at the bottom of the Add/Edit Switch editor.
- Restores the same reminder at the bottom of the Add/Edit Stack Member editor.
- Places the reminder in the final field description so it remains visible inside the nested editor itself.
- No Discovery runtime or generated-output behaviour is changed.
- Retains the v2.0.7 Stop Discovery control, v2.0.6 traffic-rate sanity guard, and v2.0.5 fresh-install Discovery defaults.

## v2.0.7

- Adds a Stop Discovery button beside Run Discovery.
- Stops only the active Discovery job; it does not stop or uninstall the Discovery app.
- Uses process-group termination so active SNMP walk child processes stop with the Discovery job.
- Preserves already-generated files and skips the post-run SNMP2MQTT restart when a run is stopped.
- Adds explicit Stopping and Stopped UI states.
- Retains the v2.0.6 traffic-rate sanity guard and v2.0.5 fresh-install Discovery defaults.

## v2.0.6

- Rejects impossible RX/TX rate samples that exceed the selected interface's physical link speed.
- Retains the last valid traffic rate when Home Assistant counter timestamps produce an impossible spike.
- Keeps genuine fresh zero-delta samples at `0 B/s`.
- Retains the v2.0.5 fresh-install Discovery defaults.

## v2.0.5

- Fresh Discovery installs now enable `run_snmp_walks` by default.
- Fresh Discovery installs now enable `generate_snmp2mqtt` by default.
- Fresh Discovery installs now enable `generate_support_my_switch_bundle` by default.
- Existing saved Discovery options are preserved; these are package defaults for new installs only.
- Retains the v2.0.4 RX/TX traffic-rate sample-timing fix.

## v2.0.4

- RX/TX rate calculation now keys off the underlying Home Assistant counter entity update timestamps instead of card redraw time.
- Retains the last calculated traffic rate between SNMP samples instead of forcing `0 B/s` after a frontend stale timeout.
- A fresh counter sample with zero byte delta now produces a genuine `0 B/s`.
- Retains the v2.0.2 Calibration colour-picker overflow fix and v2.0.3 Native generated-dashboard fix.
- Fresh Discovery installs now enable `run_snmp_walks` by default.
- Fresh Discovery installs now enable `generate_snmp2mqtt` by default.
- Fresh Discovery installs now enable `generate_support_my_switch_bundle` by default.
- Existing saved Discovery options are preserved; these are package defaults for new installs only.

## v2.0.3

- Fixed Discovery-generated Native dashboard YAML containing the dashboard shell but no Switch Vision cards when member rows were processed.
- Added the missing `member_header_title` jq helper used by generated stack/member card rows.
- Member header titles now use the member-specific value when present and otherwise fall back to the parent switch header title.
- Retains the v2.0.2 Calibration colour-picker overflow fix.
- No SNMP polling, sensor mapping, saved-profile format, reset behaviour, faceplate geometry, Custom dashboard behaviour, or broader Discovery workflow is intentionally changed.

## v2.0.2

- Fixed the Calibration colour picker being clipped by its open section container and appearing underneath the following section.
- Open Calibration sections now use visible overflow so the existing colour popover can extend outside the section boundary.
- Collapsed sections keep the existing clipped rounded-container behaviour.
- UI/CSS-only maintenance change; Calibration logic, saved profiles, reset paths, Discovery, sensors, faceplate geometry, and backend runtime behaviour are unchanged.

## v2.0.1

- Fixed a frontend regression that prevented **Reset All Switches** from running in both Native and Custom calibration scopes.
- The shared Calibration action handler now defines the active scope before it is used by the Reset All confirmation and status messages.
- The existing scope-isolated backend reset, reset event, and model-aware factory rebuild paths are unchanged.
- No calibration schema, saved-profile format, faceplate defaults, geometry, Discovery, sensors, generated YAML, mappings, or dashboard behaviour changed.

## v2.0.0 — Gold Master / Stable

- Promoted the final v1.9.97 pre-Gold codebase to **Switch Vision v2.0.0 Gold** with no additional runtime feature changes.
- Established v2.0.0 as the new protected and authoritative Gold baseline for future 2.x maintenance.
- Locked the current Installer-led setup path, Discovery workflow, native Home Assistant dashboard, advanced custom-YAML path, Calibration workspace, faceplate defaults, diagnostics, import/export, and Support My Switch workflow.
- Confirmed the normal new-user path as **Installer → Discovery → native Switch Vision dashboard**, with SNMP2MQTT managed by the Installer and manual/custom YAML retained for advanced users.
- Retained all v1.9.97 calibration, faceplate, profile, sensor, Discovery, generated-YAML, and dashboard behaviour unchanged during the Gold promotion.

## v1.9.97

- Added factory calibration defaults for the bundled `c3560cg-8pc-s.png` faceplate from the newly supplied calibrated faceplate profile.
- Preserved the supplied port, uplink, Status LED, status-box, logo, font, visibility, colour, LED-size, and calibration-button geometry.
- Removed switch-specific export identity, stack membership, management IP, and transfer metadata before bundling the profile as a reusable faceplate default.
- The change is faceplate-specific: model detection, supported-device mappings, sensors, Discovery, generated YAML, and saved user profiles are unchanged.

## v1.9.96

- Removed full calibration objects from the `switch_vision_calibration_updated` Home Assistant event payload.
- Calibration save events now carry only the small routing metadata needed by listening cards, preventing 48-port profiles from exceeding Home Assistant Recorder's 32 KiB event-data limit.
- Listening cards keep the existing compatibility path for older payload-bearing events and otherwise reload the saved profile through the existing Switch Vision websocket API.
- Save Profile, native/custom profile mirroring, cross-card refresh, calibration schema, geometry, Discovery, sensors, generated YAML, faceplates, and dashboard behaviour are unchanged.

## v1.9.95

- Restored the **Status LEDs** Quick Selection shortcut and placed it with the other status controls before the RJ45 shortcuts.
- Quick Selection now reads: **Logo → Status Box 1 → Status Box 1 fields → Status Box 2 → Status Box 2 fields → Status LEDs → All RJ45 → RJ45 Link → RJ45 Activity → All SFP → SFP Link → SFP Activity → Port Numbers → Calibration button**.
- Compacted **Position & Size** into one desktop row: Nudge, size controls, Step, direct X/Y/W/H, Apply, and the target summary now share the same line when space allows.
- Narrower screens still wrap the controls responsively.
- No calibration target IDs, saved-profile data, geometry behaviour, Discovery, sensors, generated YAML, faceplate defaults, or dashboard behaviour changed.

## v1.9.94

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

## v1.9.92

- Reorganised Calibration around the normal workflow: **Selection → Position & Size → optional appearance/settings sections → profile actions**.
- Merged the old Calibration Target and Quick Selection panels into one **Selection** section and made Selection and Position & Size open by default.
- Split the oversized Appearance panel into focused **Assets**, **Labels & LEDs**, **Status Boxes**, and **Switch & Stack** sections.
- Compacted common controls, shortened quick-selection labels, and placed direct X/Y/W/H editing on its own compact row.
- Preserved every existing Calibration action and field; no profile schema, saved-profile behaviour, geometry, faceplate defaults, LED logic, Discovery, sensors, generated YAML, model mappings, or dashboard rendering changed.

## v1.9.91

- Added profile-wide **Link LED colour** and **Activity LED colour** controls to Calibration using the existing Switch Vision colour picker.
- A selected Link colour applies to every RJ45 and SFP/uplink Link LED; a selected Activity colour applies to every RJ45 and SFP/uplink Activity LED.
- Existing profiles remain visually unchanged until a colour override is selected: factory Link LEDs retain their speed-based colours and Activity LEDs retain their existing behaviour.
- Resetting either LED colour restores factory behaviour rather than forcing a new colour into older profiles.
- LED state, activity timing, geometry, Discovery, sensors, generated YAML, model mappings, and dashboard layout are unchanged.

## v1.9.90

- Removed the release-history/changelog browser from the Switch Vision Discovery Hub.
- Removed Discovery's generated changelog-history JSON, API endpoint, browser controls, and build-time history generation.
- Release changelog browsing now belongs exclusively to the Switch Vision Installer.
- No changes to Discovery execution, Calibration, faceplates, profiles, sensors, generated YAML, model mappings, or dashboard rendering.

## v1.9.89

- Remove unused Home Assistant `/config` access from the Discovery app.
- Migrate Discovery from deprecated `build.yaml` handling to a Dockerfile-only Home Assistant Alpine 3.22 build.
- Add a one-time migration that removes the retired `show_card_header` saved option.
- Constrain clean-before-walk deletion to the canonical `/share/switch_vision/snmpwalks` tree, including symlink-aware path resolution.
- Strengthen Discovery configuration import validation for paths, booleans, numeric limits, switch rows, stack rows, and model choices.
- Correct WS-C3560CG-8PC-S visual metadata to its dedicated 2048×329 faceplate and preserve the legacy faceplate as an optional fallback.
- Improve Calibration failure guidance to point to the browser console as well as Home Assistant logs.
- Add Discovery vendor/interface self-test and device-visual registry consistency to the build release gates.
- Refresh pre-2.0 stability documentation.

## v1.9.88

- Added a compact changelog browser to the Switch Vision Hub with simple left and right arrows to move through release history one version at a time.
- The current release opens by default; the left arrow moves to older entries and the right arrow returns toward newer entries.
- Added build-time generation of the Hub changelog history from the authoritative `CHANGELOG.md`, so future release entries are included automatically.
- Contains no changes to Calibration, faceplate defaults, profiles, Discovery execution, sensors, generated YAML, model mappings, or dashboard rendering.

## v1.9.87

- Removed custom Calibration colour pickers from enclosing HTML `label` elements so browser label activation cannot close the picker while it is being used.
- The picker now remains open during saturation/value dragging, hue and brightness changes, HEX editing, and Reset.
- The picker closes only with Done, Escape, or a click outside the picker.
- Applied the fix to Status LED text, RJ45 port numbers, uplink labels, and both Status Box text/background/border colour controls.
- Added a regression check preventing custom colour pickers from being nested inside HTML labels again.

## v1.9.86

- Added independent Status LED label Font, Font size, Bold, and Text colour controls in Calibration.
- Preserved older-profile appearance with backward-compatible defaults matching the established Status LED text style.
- Replaced browser-native colour inputs with a persistent Switch Vision inline colour picker for Calibration custom-colour controls.
- Added draggable saturation/value, hue and brightness controls, live switch preview, editable HEX input, Reset, Done, outside-click close, and Escape close behaviour.
- Applied the shared picker to Status LED text, RJ45 numbers, uplink labels, and Status Box text/background/border colours.

## v1.9.85

- Rebuilt the reset change from the v1.9.82 baseline rather than stacking the v1.9.83/v1.9.84 runtime attempts.
- Fixed calibration identity copying so scalar profile identifiers and nested identity data are deep-copied without being passed through whole-profile normalisation.
- **Reset Current Faceplate** now resolves the faceplate from the calibration currently displayed in the editor, so native and custom scopes use the same bundled faceplate-specific defaults.
- Future bundled faceplates automatically participate when a matching `calibration/faceplate-*.json` factory profile is present; model defaults remain the fallback when no faceplate-specific defaults exist.
- Retained build-time synchronization and validation of embedded faceplate defaults against the authoritative calibration JSON files to prevent stale native/card copies.
- No calibration geometry, profile schema, model mappings, Discovery behaviour, sensors, generated YAML, or dashboard layout changed.

## v1.9.82

- Added per-SFP/uplink `label_show` visibility with backward-compatible shown-by-default behaviour.
- Added Show/Hide controls for individual and grouped SFP labels in Calibration.
- Expanded **All numbers** Quick Selection to include both RJ45 port numbers and SFP/uplink labels for movement, direct coordinates, and visibility.
- Preserved existing profile compatibility and made no changes to Discovery, sensors, generated YAML, faceplate mappings, or dashboard layout.

## v1.9.81

- Added `cisco-black-logo.png` to the bundled logo assets for optional selection in Calibration.
- Preserved the supplied 2048 × 2048 transparent PNG unchanged.
- No default logo, model mapping, calibration geometry, profile behaviour, Discovery, sensors, generated YAML, or dashboard rendering changed.

## v1.9.80

- Added a Calibration colour control for status LED label text.
- Added a separate Calibration colour control for RJ45 port numbers.
- Kept the existing uplink-label colour control independent, with backward-compatible fallbacks for older profiles.
- Contains no intentional changes to calibration geometry, profile selection, faceplate defaults, Discovery, sensors, generated YAML, or dashboard layout.

## v1.9.79

- Added direct W and H pixel fields beside the existing X and Y controls in Calibration.
- Single targets show their current size; grouped targets show a shared size or `Mixed` when dimensions differ.
- Users may apply only W, only H, or both while leaving blank values unchanged.
- Supports RJ45 and SFP boxes, RJ45 and SFP LEDs, logos, status boxes, and the calibration button.
- Contains no profile-schema, faceplate-default, Discovery, sensor, generated-YAML, or dashboard-rendering changes.

## v1.9.78

- Custom ports now automatically reflects the active single-port or multi-port RJ45 selection, making it easy to remove or add individual ports before reselecting.
- Added optional direct X and Y coordinate inputs to Position and Size.
- A single axis can be applied while leaving the other unchanged, or both axes can be applied together.
- Direct coordinates work with individual targets and existing grouped selections without changing the established selection model.
- No profile format, faceplate defaults, Discovery, sensors, generated YAML, or dashboard rendering changes.

## v1.9.77

- Moved the pixel-step selector from **Calibration Target** to the end of **Position and Size**, immediately after `H+`.
- Keeps target selection focused on the selected item and groups the step size with movement and resizing controls.
- Contains no changes to calibration geometry, profiles, faceplate defaults, imports/exports, Discovery, sensors, generated YAML, or dashboard rendering.

## v1.9.76

- Changed selected Calibration targets from flashing yellow to a continuous static yellow highlight.
- Removed the calibration-only blink clock, blink interval defaults, and time-dependent active-state checks.
- Live switch port and SFP activity LED blinking remains unchanged and separate from Calibration selection highlighting.
- Contains no changes to calibration coordinates, profile storage, imports/exports, faceplate defaults, Discovery, sensors, generated YAML, or dashboard layout.

## v1.9.75

- Added independent **Link/speed LED** and **Activity LED** Calibration parts for individual SFP/uplink ports.
- Added matching aggregate targets for all SFP link/speed LEDs and all SFP activity LEDs.
- Added optional SFP `led_left`, `led_right`, `led_left_size`, and `led_right_size` profile fields with legacy fixed-offset fallback for older profiles.
- Included SFP LED geometry in normal profile save, export/import, faceplate defaults, target reset, movement, resize, and calibration guide-ring behaviour.
- Existing profiles without SFP LED coordinates retain their previous visual positions.

## v1.9.74

- Updated the bundled `submarine-48rj45-4sfp.png` faceplate defaults with the corrected SFP label positions from the latest exported Calibration profile.
- Changed only the G1, G2, G3/TE3, and G4/TE4 label coordinates.
- All RJ45 coordinates, SFP centers and hitboxes, LEDs, status panels, logo, calibration button, model mappings, and runtime behaviour remain unchanged.

## v1.9.73

- Added factory faceplate-selection defaults for `submarine-48rj45-4sfp.png` from the exported Calibration profile.
- Selecting the submarine faceplate now starts from its supplied 48-port, four-uplink, LED, label, status-panel, logo, and calibration-button geometry when no saved faceplate profile exists.
- **Reset Current Faceplate** and individual calibration target resets now restore the submarine faceplate's own defaults while preserving the selected faceplate.
- Removed switch-specific IP, stack-member, and profile-transfer metadata from the bundled factory defaults.
- The standard 48-port model calibration, Discovery mappings, model-default faceplates, and the current calibration Save confirmation remain unchanged.

## v1.9.72

- Removed the Save-twice warning from the Card header title help text, where Home Assistant collapsed it into the preceding sentence.
- Moved the reminder to the Switches and Stack Members section descriptions so it remains clear without crowding the final field.
- No Discovery execution, device mapping, faceplate, calibration, sensor, YAML generation, or dashboard behaviour was changed.

## v1.9.71

- Bundled `c3560cg-8pc-s.png` at its native 2048 × 329 dimensions.
- Made the new artwork the default faceplate for `WS-C3560CG-8PC-S`.
- Updated the model calibration profile to reference the native slim canvas while preserving its editable calibration data for final user calibration.
- Retained `24rj45-2sfp.png` as an optional fallback faceplate.
- Contains no intentional changes to Discovery execution, sensors, generated YAML, dashboards, or other device profiles.

## v1.9.70

- Added `submarine-48rj45-4sfp.png` as a bundled alternative faceplate asset.
- This is an optional bundled faceplate only; no runtime logic, device mappings, calibration behaviour, or dashboard behaviour was changed.

## v1.9.69

- Added `WS-C3560CG-8PC-S` to the Discovery manual switch-model dropdown.
- The model was already registered for automatic detection, profile mapping, and experimental device support; this change only makes the same registered model selectable as a manual override.
- Contains no intentional changes to Discovery processing, profiles, sensors, calibration, dashboards, or faceplates.

## v1.9.68

- Updated the Hub wording to **Show detected devices & status**, **Detailed device(s) information**, and **Logging level**.
- Removed unsupported literal HTML/Markdown from the add/edit reminder descriptions.
- Added two preserved spacer lines above the warning reminder and kept warning symbols at both ends.
- Contains no intentional changes to Discovery execution, generated files, profiles, sensors, calibration, resets, dashboards, or faceplates.

## v1.9.67

- Renamed the Discovery landing page to **Switch Vision Hub** and removed its introductory subtitle.
- Simplified the landing-page cards and wording for Discovery, Devices, Support My Switch, detected-device information, and configuration import/export.
- Removed duplicate Dashboard & Calibration and Installer launch cards because both already have dedicated Home Assistant sidebar entries.
- Renamed and simplified the Switch Vision, Discovery, and SNMP2MQTT settings cards.
- Contains no intentional changes to Discovery execution, generated files, profiles, sensors, calibration, resets, dashboards, or faceplates.

## v1.9.66

- Changed the add/edit Save reminder to a larger warning-triangle line with extra spacing and a matching trailing warning symbol.
- Made **Generated SNMP2MQTT YAML** a collapsible section matching **Generated Card YAML**.
- Contains no intentional changes to Discovery generation, profiles, sensors, calibration, resets, dashboards, or faceplates.

## v1.9.65

- Made optional logo and faceplate folder failures non-fatal so filesystem permission or transient storage problems cannot prevent the integration or native panel loading.
- Made generated-dashboard metadata races non-fatal; successfully parsed cards remain available if the file is replaced between reading and metadata lookup.
- Made shared UI-preference write failures log a warning instead of aborting integration setup.
- Added build-time README resource-version synchronisation and refreshed stale current-release documentation.
- Fixed checksum manifests to reference the release ZIP in its actual `Releases/` path, allowing direct `sha256sum -c` verification from the source root.
- Re-ran Python, JavaScript, shell, JSON, YAML, archive, version-propagation, and reproducible-build validation without changing established feature behaviour.

## v1.9.63

- Added a collapsible **Generated Card YAML** section above **Generated SNMP2MQTT YAML** in the Discovery Web UI.
- Added generated-card status, YAML validation, preview, copy-to-clipboard, and download actions.
- The preview refreshes after Discovery and reports missing or invalid output instead of showing stale content.
- Separated the add/edit reminder from the card-title example with a clearer yellow-square warning line.
- Contains no intentional changes to Discovery generation, calibration, profile storage, imports, resets, sensors, or dashboard rendering.

## v1.9.62

- Replaced per-switch card-header visibility with one global **Show card headers** integration option.
- Applied the setting to native and custom YAML cards through a shared runtime UI-settings service.
- Removed the per-switch Discovery field while retaining custom card-header titles.
- Ignored retired per-card header flags to prevent conflicting sources of truth.

## v1.9.61

- Fixed Discovery preserving an explicit `show_card_header: false`; jq no longer treats boolean `false` as missing during fallback or row serialisation.
- Applied the same explicit-boolean handling to parent switches and individual stack members.
- Added the reminder **“Remember: click Save again on the next page.”** at the bottom of the add/edit switch and stack-member forms.
- Contains no intentional changes to calibration, scoped storage, import/export, reset behaviour, sensors, or native/custom isolation.

## v1.9.60

- Fixed native card-header visibility after upgrades by using a release-specific native card renderer, preventing an older custom element retained by Home Assistant SPA navigation from overriding the current setting.
- Canonicalised `show_card_header` in the backend with strict precedence over retired aliases, including an explicit `false`.
- Kept manual YAML on the stable `custom:switch-vision-3650` element while isolating native-panel renderer upgrades.

## v1.9.59

- Fixed Discovery stack-card generation so secondary members always inherit uptime from the configured member 1 sensor when a valid stack is present.
- Hardened generated dashboard YAML by quoting user/configuration strings and normalising control characters in generated rows.
- Cleaned duplicated and out-of-order recent changelog entries.
- Verified calibration JSON normalisation already performs a single parse and retained that safe implementation unchanged.
- Contains no intentional changes to scoped profile storage, import/export, reset behaviour, calibration geometry, sensor mappings, or switch identity.

## v1.9.58

- Replaced the partial metadata toggle with per-card **Show card header**, which hides or shows the complete title/metadata row without leaving a gap.
- Added global native-panel **Show dashboard header** integration option while preserving the mobile menu button when hidden.
- Kept legacy card-header keys as compatibility aliases.

## v1.9.57

- Fixed generated cards showing `true • SWx` when the optional card header title was blank.
- Discovery preserves empty fields while generating dashboard cards, preventing boolean settings from shifting into title fields.
- Boolean and legacy string values of `true` or `false` are treated as an empty custom header title and fall back to the normal card title.

## v1.9.56

- Added per-switch card-header visibility and optional custom header title.
- Added concise practical examples to useful Discovery fields.
- Preserved compatibility with the earlier `show_card_header_information` and `show_card_metadata` keys.

## v1.9.55

- Added a mobile-only Home Assistant menu button to the native Switch Vision panel using the standard `hass-toggle-menu` event.

## v1.9.54

- Added backend validation and handling for explicit `native` and `custom` reset scopes.
- Reset All from one dashboard scope no longer clears the opposite scope.

## v1.9.53

- Moved **Reset All Switches** beside the current reset actions and styled it purple.
- Replaced small browser prompts with larger responsive Switch Vision confirmation dialogs.

## v1.9.52

- Scoped Reset All to the dashboard namespace that launched it.

## v1.9.51

- Moved **Reset Current Switch** beside **Reset Current Faceplate**.
- Styled faceplate reset orange and current-switch reset red.

## v1.9.50

- Restored faceplate profile import/export on the proven `native_SWx` / `custom_SWx` storage model.
- Imports target only the card scope that launched them and cannot write to factory profiles.
- Native and custom YAML scopes remain independent through save, refresh, restart, and cross-device use.

## v1.9.49

- Added deterministic writable namespaces `native_SWx` and `custom_SWx`.
- Native and custom YAML cards for the same physical switch no longer share calibration records.
- Factory profiles remain read-only templates.

## v1.9.48

- Reworked imported profile persistence on the earlier unscoped design. Superseded by the scoped storage introduced in v1.9.49.

## v1.9.47

- Added factory-profile protection and switch-specific import targeting. Superseded by the scoped storage introduced in v1.9.49.

## v1.9.46

- Retired due to unsafe shared-profile behaviour. Upgrade to v1.9.50 or later before using profile import/export.

## v1.9.45

- Retired due to unsafe shared-profile behaviour. Upgrade to v1.9.50 or later before using profile import/export.

## v1.9.44

- Introduced faceplate profile import/export. Its original save-destination model was replaced by scoped storage in v1.9.49-v1.9.50.

## v1.9.43

- Added larger calibration movement steps, Entire port default targeting, and per-port number visibility.

## v1.9.42

- Added contextual colour pickers for existing colour-enabled calibration elements while preserving operational LED colours.

## v1.9.41

- Unified Discovery and Support My Switch styling with the Switch Vision dark navy application theme.

## v1.9.40

- Reduced the calibration header to Switch, Model, Faceplate, and Profile while retaining state and geometry in the sticky footer.

## v1.9.39

- Simplified home tiles and added consistent neutral, hover, and keyboard-focus states.

## v1.9.38

- Rebuilt public documentation and packaging around the tested v1.9.37 runtime baseline.

## v1.9.37

- Removes the user-facing **Apply Recommended Setup** action and its duplicate temporary-profile path.
- Removes the obsolete recommendation/compatibility row from Interactive Calibration.
- Keeps exact-model detection authoritative for initial profile selection, missing-profile recovery, **Reset Current Switch**, and **Reset All Switches**.
- Keeps unknown or unregistered switches on a visible fallback profile that users can freely customise until an official or custom profile is available.
- Leaves faceplate selection, calibration persistence, Discovery, sensors, and Support My Switch behaviour unchanged.

## v1.9.36

- Removes **None** from the faceplate selector; valid choices are now **Default / recommended** or a named custom faceplate.
- Migrates legacy hidden, `__none__`, blank, or invalid faceplate states to the exact model's recommended visible artwork.
- Falls back to the recommended faceplate when a selected custom image is missing or fails to load.
- Preserves logo hiding as a separate supported option.
- Retains all v1.9.35 calibration-profile validation and title escaping.

## v1.9.35

- Separates **None**, **Default / recommended**, and explicit custom faceplate selections.
- Makes **None** render no faceplate image and resolves **Default / recommended** from each switch's exact model or factory profile.
- Migrates legacy `show: false` plus `__default__` profiles to the intended recommended-faceplate state while preserving explicit `__none__` selections.
- Validates imported, saved, and loaded calibration profiles for payload size, profile names, finite coordinates, positive dimensions, canvas bounds, element counts, asset filenames, and JSON safety.
- Rejects invalid stored profiles safely and falls back to the current card/factory calibration instead of rendering corrupt data.
- Escapes card titles before inserting them into the frontend DOM.
- Adds executable backend and browser-side regression coverage without changing Discovery, sensors, Support My Switch, or calibration storage transactions.

## v1.9.34

- Releases calibration event subscriptions when cards leave the page and re-establishes one clean subscription when they reconnect.
- Prevents duplicate subscriptions across repeated Home Assistant state updates and connection replacements.
- Retries transient event-subscription failures with bounded backoff and safely releases subscriptions that complete after a card has already disconnected.
- Builds a complete native-sidebar replacement dashboard away from the visible panel before committing it.
- Keeps the current working switch cards visible when a refresh, module import, or generated card configuration fails.
- Preserves the rendered panel across normal disconnect/reconnect cycles and ignores stale asynchronous refresh results.
- Adds executable frontend lifecycle and atomic-refresh regression coverage without changing calibration, Discovery, sensors, or support-bundle behaviour.

## v1.9.33

- Prevents Support My Switch bundles from reporting PASS when any file could not be fully inspected or sanitized.
- Excludes unsupported binary, oversized, unreadable, unwritable, symbolic-link, and special-file entries from the temporary archive copy.
- Records privacy-safe file identifiers, reasons, suffixes, sizes, and exclusion counts without exposing original filenames or paths.
- Marks incomplete bundles **REVIEW REQUIRED**, sets `ready_to_send` to false, and withholds prepared `.eml` and send actions.
- Keeps clean, fully inspected bundles on the existing PASS or PASS WITH PRIVACY WARNINGS workflow.
- Aligns sanitizer, bundle, manifest, text-report, Web UI, and email-gating behaviour at processing version 9.

## v1.9.32

- Fixes Reset All calculating the correct model layout but leaving it only in temporary editor state.
- Every loaded native or custom YAML card now saves its own model-aware factory default to its stable base profile after the global store is cleared.
- Keeps the correct default authoritative while Calibration is closed and across refresh/restart.
- Retains the safe no-generic-fallback behaviour when model context is temporarily unavailable.

## v1.9.31

- Fixes **Reset All Switches** rebuilding 2960S, 2960X, and 3560-C cards with the generic 48-port/4-SFP layout.
- Resolves each card from its exact model first, then its already-loaded factory profile when exact-model sensor context is temporarily unavailable.
- Restores 2960S/2960X 48-port models to 48 RJ45 / 2 SFP, 2960X 24-port models to 24 RJ45 / 4 SFP, and keeps all other registered model defaults intact.
- Defers a global reset rather than displaying the wrong generic geometry when no model-aware context is available yet.
- Leaves **Reset Current Switch**, calibration storage transactions, rectangle LED geometry, Discovery, and sensors unchanged.

## v1.9.30

- Serializes calibration save, delete, reset, and profile-read operations through one integration-level asynchronous lock.
- Saves a native faceplate-specific profile and its switch-scoped base mirror in one atomic storage transaction.
- Records which faceplate profile supplied each mirrored base profile and safely recognises equivalent legacy v1.9.29 mirrors.
- Removes an active mirrored base profile when its source faceplate profile is deleted, preventing stale native-panel calibration data.
- Reports every profile changed by a transaction and supplies the correct per-profile calibration payload to other open dashboards.
- Clears deleted calibration data from frontend memory before reloading fallback/default geometry.
- Adds storage-safety regression checks without changing calibration controls, rendering, Discovery, or sensor behaviour.

## v1.9.29

- Gives every RJ45 Link/Speed and Activity rectangle its own saved width and height.
- Prevents rectangle LED W/H controls from resizing the RJ45 port hitbox.
- Keeps Link/Speed and Activity rectangle dimensions independent for individual, selected, odd/even, and all-port targets.
- Migrates older calibration profiles in memory with dimensions matching the previous fixed rectangle appearance.
- Preserves Circle rendering and accepts older imported profiles that do not contain rectangle-size fields.
- Validates optional rectangle-size fields when importing profiles and displays their true W/H values in the calibration footer.

## v1.9.28

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

## v1.9.21

- Adds a per-profile Port LED Shape selector for Link/Speed and Activity LEDs.
- Supports Circle and Rectangle port LED rendering while keeping all status LEDs circular.
- Existing profiles remain compatible and default to Circle.

## v1.9.20

- Restores the known-good v1.9.15 calibration behaviour and excludes the abandoned cross-device live-preview implementation.
- Adds a live selected-target geometry readout beside the calibration save state in the sticky footer.
- The footer readout updates with the selected target, part, X, Y, width, and height as calibration controls move or resize it.

## v1.9.15

- Updates Quick Selection complete-port movement to include the port box and link/activity LEDs while leaving port-number labels in place.
- Keeps port-number labels independently selectable through the Part control and dedicated number-selection buttons.

## v1.9.14

- Places Calibration Target and Port manager controls on one responsive row.
- Makes Quick Selection port buttons select and move the complete port group, including the port box, link/activity LEDs, and number label.

## v1.9.13

- Renames the status-box font controls from **Status font** to **Font** for cleaner column alignment.
- Removes the reserved calibration workspace footer gap so the sticky action bar follows the content directly.
- Keeps normal scrolling when expanded calibration sections exceed the available viewport.

## v1.9.12

- Aligns calibration labels, inputs, selectors, and action buttons into cleaner rows.
- Places Switch IP and stack controls on one coordinated Switch / Stack row.
- Removes excess spacing beneath collapsed or short calibration sections.
- Keeps responsive wrapping for narrower screens.

## v1.9.11

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

## v1.9.6

- Added **Reset Current Faceplate** to restore the active faceplate's saved geometry, status LEDs, logo, calibration button, and status panels to the switch model defaults while keeping the selected faceplate image.
- Added **Reset Current Switch** to remove every saved faceplate-specific calibration for the active switch and restore its recommended model defaults.
- Added **Reset All Switches** to clear every saved Switch Vision calibration across all dashboards, protected by a two-step confirmation.
- Added backend reset handling and cross-client reset events so other open dashboards return to defaults immediately.

## v1.9.5

- Fixed custom faceplates and calibration changes not appearing on phones, fresh browsers, or Incognito sessions.
- The faceplate-specific calibration is now mirrored to the switch base profile as the shared active selection.
- Calibration update events now carry the saved calibration and base-profile identity so other clients update immediately.

## v1.9.4

- Added independent visibility controls for every status LED in Interactive Calibration.
- Unticking STAT, SYST, DUPLX, ACTV, SPEED, STACK, or PoE now hides only that LED for the active calibration profile.
- Per-LED visibility is saved with faceplate-specific and switch-default calibration profiles.
- Existing profiles remain fully compatible and keep all status LEDs visible by default.

## v1.9.3

- Fixed custom faceplates reverting to the exact-model default after clicking **Done** in Calibration.
- Exact-model reconciliation now preserves the saved faceplate while continuing to enforce compatible port and uplink geometry.

## v1.9.2

- Preserved the user-selected faceplate when closing the visual card editor with Done.
- Updated exact-model profile reconciliation so authoritative port and uplink geometry no longer forces the model's default faceplate.
- Custom faceplates now remain selected after the card configuration is saved and reloaded.

## v1.9.1

- Moved Switch Vision logo and faceplate directory creation/scanning off Home Assistant's asyncio event loop.
- Updated both integration startup and the asset-list WebSocket command to use `hass.async_add_executor_job`.
- Removes the `Detected blocking call to scandir` warning without changing asset discovery or calibration behaviour.

## v1.9.0

- Added automatic calibration namespaces for every faceplate, keyed by the active switch profile and faceplate filename.
- Changing faceplates now loads that faceplate's saved geometry or creates a starter profile from the current switch geometry when no profile exists.
- Port boxes, port labels, link/speed LEDs, activity LEDs, SFP/uplink positions, status panels, logos, and calibration-button geometry can now be calibrated independently for each faceplate.
- The default faceplate continues to use the existing switch calibration profile, preserving compatibility with all saved v1.8.x profiles.
- Added a clear Calibration header showing the switch profile, active faceplate, and whether the profile scope is Switch default or Faceplate-specific.
- Calibration exports now record the base profile, profile scope, and faceplate filename.
- New community faceplates work without code changes: copy the image into the faceplates folder, select it, then calibrate and save.

## v1.8.29

- Reduced the Discovery web interface typography globally for a cleaner, less oversized presentation.
- Added shared font-size and line-height variables so future UI tuning remains consistent across pages.
- Reduced page headings, section headings, body text, helper text, status values, and navigation-card labels while preserving readability.
- Contains no switch-rendering, discovery-engine, sensor-generation, or device-support changes.

## v1.8.27

- Rebuilt the current v1.8.26 code and documentation baseline as v1.8.27 for end-to-end Installer v1.9.3 testing.
- Provides a real version change so the installer can verify automatic Discovery stop, rebuild, restart, and installed-version confirmation.
- Carries forward the current confirmed support status for Cisco 2960S/2960X 48-port models and standalone Juniper EX3300.
- Contains no functional switch-rendering changes beyond the version bump and synchronized release metadata.

## v1.8.26

- Promoted `WS-C2960X-48FPD-L` to Confirmed after real-hardware validation of both 10G SFP+ uplinks, link state, activity, and traffic operation.
- Promoted `WS-C2960S-48FPD-L` to Confirmed after real-hardware validation of both 10G SFP+ uplinks, link state, activity, and traffic operation.
- Promoted standalone `EX3300-48P` to Confirmed after real-hardware validation of its SFP/SFP+ uplink path, link state, activity, and 64-bit traffic counters.
- Kept Juniper Virtual Chassis outside the confirmed support scope pending dedicated validation.
- Retained the Juniper native-VLAN plus optional MODE presentation workaround for clear ACCESS/TRUNK display.
- Kept the registered Cisco 2960X 24-port and Cisco 3560-C models Experimental pending model-specific live validation.
- Started Experimental Cisco Catalyst 2960X support for `WS-C2960X-24TS-L` from Support My Switch contribution `[contribution reference withheld]`.
- Added exact model recognition and the dedicated `cisco-2960x-24ts-24p-4sfp` Discovery profile.
- Mapped 24 RJ45 interfaces and four Gigabit SFP uplinks using the existing `24rj45-4sfp.png` faceplate and `cisco_2960x_24p` calibration geometry.
- Enabled stack-aware Discovery for the contributed three-member layout.
- Added status, VLAN, description, link, speed, duplex, and traffic/activity generation through the standard Catalyst 2960X sensor path.
- Marked the model Experimental pending contributor validation of member mapping, uplinks, VLAN/trunk display, and live activity.
- Added a Configuration page to the Switch Vision Discovery web interface.
- Added one-click export of the configured switch list, stack-member mappings, and Discovery settings.
- Added validated JSON import for restoring Discovery configuration on a fresh Home Assistant installation.
- Import preserves Support My Switch privacy and contributor preferences.
- Creates `/data/options.before-import.json` before replacing Discovery settings.
- Export files include switch addresses and SNMP community strings and must be stored securely.

## v1.8.24

- Started Experimental Cisco Catalyst 3560-C support for `WS-C3560CG-8PC-S` from Support My Switch contribution `[contribution reference withheld]`.
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

## v1.8.5

- Replaced the bundled faceplate set with the single `faceplates/switch-vision-default-faceplate.png` asset and made it the default for shipped profiles and exact-model recommendations.
- Removed the previous `sv-dark.png` and `sv-light.png` bundled faceplates.
- Replaced `logos/1996-cisco-logo.svg` with the supplied updated artwork.
- Fixed multi-device Discovery report isolation and added exact WS-C3560CG model recognition so one walk cannot inherit another device's model/profile result.
- Corrected Support My Switch manifest file counts to include the complete archive payload, including generated metadata.
- Added `PASS WITH PRIVACY WARNINGS` when interface descriptions or VLAN labels remain visible because their masking options were disabled.
- Allow individual SFP/uplink targets to be removed in interactive calibration.

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

## v1.8.0

- Promoted the fully validated v1.7.53 codebase to the new **Gold / Stable** baseline as v1.8.0.
- Updated all runtime versions, manifests, examples, installation paths, supported-device outputs, Gold documents, and current-release documentation.
- Locked in the final status-box layout: independent Status Box 1, Status Box 2, and Port Status Box controls; title-free rows; IntelOne 16 px bold defaults; and VENDOR/UPTIME defaults for Status Box 2.
- Locked in Juniper EX3300-48P exact-model registry matching, copper-port mapping, PoE/system telemetry, and per-port static Q-BRIDGE VLAN membership display.
- Locked in Support My Switch registry enrichment and explicit privacy-audit enforcement metadata.
- Retained Cisco Catalyst 3650 exact models as Confirmed; Cisco 2960S/2960X and Juniper EX3300-48P remain Experimental pending outstanding uplink or Virtual Chassis validation.
- Confirmed `CHANGELOG.md` as the sole version-history document; historical `RELEASE_NOTES*` files remain excluded.
- Gold update scope: perform a clean complete replacement of the release components, rebuild/reinstall Discovery, restart Home Assistant Core, run Discovery, and refresh the browser.

## v1.7.53

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

## v1.7.46

- Fixed Reset All so both status boxes explicitly clear legacy row offsets.
- Restored the canonical 88 px label-to-value column spacing.
- Reset defaults are Custom / IntelOne, 16 px and bold.

## v1.7.45

- Set the default font for both status boxes to Custom / IntelOne, 16 px, bold.
- Standardised the default label-to-value column spacing at 88 px from label start to value start.
- Existing saved profiles retain their font settings and individual field offsets.
- Reset All now restores the new shared status-box defaults.

## v1.7.44

- Moved the shared status-box value column further left to reduce the label-to-value gap in both Status Box 1 and Status Box 2.
- Preserved box geometry, outer padding, row spacing, truncation behaviour and independent field calibration offsets.
- `/config/custom_components/switch_vision/`

## v1.7.43

- Removed the confirmation prompt from Reset all; the visual reset now runs immediately.
- Reduced the horizontal gap between status-field labels and values in both Status Box 1 and Status Box 2.
- Preserved box geometry, outer padding, vertical layout, field ordering and independent field calibration offsets.
- `/config/custom_components/switch_vision/`

## v1.7.42

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
- `/config/custom_components/switch_vision/`

## v1.7.40

- Added the 1984, 1996, and 2016 Cisco SVG logo variants to the bundled logo library.
- Confirmed obsolete Status Box 1/2 title targets and the MODE calibration target remain excluded.
- Existing saved legacy title or MODE offsets remain harmlessly ignored.
- `/config/www/switch-vision/logos/`

## v1.7.39

- Added the Q-BRIDGE static VLAN table (`1.3.6.1.2.1.17.7.1.4.3`) to targeted SNMP walks.
- Juniper VLAN membership is now decoded for every mapped port using bridge-port → ifIndex → physical-interface correlation.
- Juniper ports render one VLAN as `VLAN n`, multiple memberships as `VLANS n, n, ...`, and fall back to `VLAN TRUNK` when trunking is known but membership is unavailable.
- Removed obsolete Status Box 1 and Status Box 2 title calibration targets. Legacy saved title offsets remain harmlessly ignored.
- MODE remains excluded from status LED calibration targets and export data.
- `/addons/switch_vision_discovery/`
- `/config/custom_components/switch_vision/`

## v1.7.38

- Fixed Juniper EX3300-48P supported-device registry matching when Discovery reports the vendor-prefixed model name `Juniper EX3300-48P`.
- Kept the authoritative exact model entry as `EX3300-48P` while normalising the vendor prefix during registry lookup.
- The Juniper contribution now reports `registry_match: true`, the `juniper-ex3300-48p` mapping profile, and Experimental validation metadata.
- Update scope: replace `/addons/switch_vision_discovery/`, rebuild or reinstall the local add-on, and restart Discovery. Home Assistant Core and SNMP2MQTT do not need restarting.

## v1.7.37

- Added individual calibration targets for every Status Box 2 field, matching Status Box 1 target support.
- Added a separate Status Box 2 field target group and an All Status Box 2 fields quick-selection button.
- Status Box 2 field targets now show calibration rings and labels and can be nudged independently without moving or resizing the box.
- Preserved Status Box 1 behaviour, status-box dimensions, field visibility, ordering, and styling.
- Update scope: replace `/config/custom_components/switch_vision/`, restart Home Assistant Core, then refresh the browser.

## v1.7.36

- Moved Status Box 2 label and value content 10 px further left.
- Preserved Status Box 1 padding, calibrated box dimensions, vertical layout, and right edge.
- Update scope: replace `/config/custom_components/switch_vision/`, restart Home Assistant Core, then refresh the browser.

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

## v1.7.31

- Standardised the vertical layout of every visible field in Status Box 1 and Status Box 2.
- Visible rows now use one compact, evenly spaced grid based on their displayed order.
- Hidden and reordered fields no longer leave uneven gaps.
- Preserved calibrated horizontal label/value positions and existing saved-profile compatibility.

## v1.7.30

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

## v1.7.6

- Corrected Juniper EX3300-48P copper-port numbering to match the physical zero-based labels 0 through 47.
- Added per-card port label and entity offsets so calibrated positions 1 through 48 map to Juniper interfaces ge-0/0/0 through ge-0/0/47.
- Port ge-0/0/42 now drives the faceplate position labelled 42.

## v1.7.5

- Added experimental Juniper EX3300-48P exact-model detection and front-panel mapping.
- Mapped ge-0/0/0 through ge-0/0/47 as 48 physical RJ45 ports.
- Deduplicated the four shared ge-0/1/N and xe-0/1/N uplink cages.
- Excluded logical unit, management, and VLAN interfaces from front-panel totals.

## v1.7.4

- Create the Discovery Web log directory and file before use.
- Prevent clean-install Discovery failures when `/share/switch_vision/discovery-web.log` does not yet exist.

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

## v1.5.2

- Added a Switch Vision integration options screen under **Settings → Devices & services → Switch Vision → Configure**.
- Added **Show Switch Vision dashboard in sidebar**, enabled by default.
- Turning the option off hides only the dedicated native dashboard sidebar entry.
- Manual Lovelace cards, generated dashboard YAML, Calibration, Discovery, Diagnostics, Support My Switch and SNMP2MQTT remain available when the sidebar panel is hidden.
- Existing YAML-based installations automatically gain a Switch Vision config entry and retain their current calibration and generated-dashboard paths.
- Option changes reload the panel immediately without requiring another Home Assistant restart.

## v1.5.1

- Added automatic start/restart of the Switch Vision SNMP2MQTT add-on after successful Discovery.
- Validate that the current Discovery run updated `generated-snmp2mqtt.yaml` before taking action.
- Discover the installed SNMP2MQTT add-on slug through the Supervisor API.
- Restart the add-on when already running, or start it when stopped.
- Report missing add-ons and Supervisor failures as warnings without failing Discovery.
- Added SNMP2MQTT action status to the minimal Discovery status window and Debug output.
- Kept the existing generated-YAML import option as the authoritative SNMP2MQTT configuration path.

## v1.5.0

- Promoted the successful native Home Assistant sidebar dashboard to a major supported feature.
- Added zero-copy dashboard loading from Discovery's generated card configuration.
- Removed prototype/test wording and polished the panel for everyday use.
- Added a compact card count and last-generated timestamp.
- Moved technical source details and module reload controls under Advanced.
- Preserved generated dashboard YAML as the permanent manual fallback.
- Kept existing Lovelace cards, Discovery parsing and SNMP2MQTT behaviour unchanged.

## v1.4.17

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

## v1.2.26

- Added a Home Assistant Ingress web interface for Support My Switch.
- Added guided privacy and contributor-recognition controls.
- Added live contribution progress, bundle-quality results, and detected-hardware summaries.
- Added one-click Prepare Email, Download Archive, and email-without-attachment actions.
- Kept all sending manual; Switch Vision stores no email credentials.

## v1.2.25

- Generates a standard `.eml` message addressed to `the Switch Vision support email address` with the contribution ZIP already attached.
- Generates a local action page with **Prepare Email**, **Download Archive**, and **Open Email Without Attachment** actions.
- Nothing is sent automatically and no mail credentials are stored.

## v1.2.24

- Rewrote the main README and clean-install guide for the current Switch Vision workflow.
- Documented the required Layout Card resource and the mobile Configuration error recovery procedure.
- Added dedicated troubleshooting and Support My Switch guides.
- Updated support levels, forum and support-email references, status-box guidance, and clean-update instructions.
- Removed stale pre-1.0 version examples and obsolete faceplate-label wording from primary documentation.

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

## v1.1.6

- Masks plain-text `Cisco local hostname: <value>` fields in Discovery reports when hostname masking is enabled.
- Extends the final residual privacy audit to detect the same report field.
- Prevents contribution bundles from reporting a clean hostname audit while Cisco local hostnames remain.
- Advances the contribution bundle schema to version 7 and sanitization schema to version 4.

## v1.1.5

- Added optional contributor recognition preferences: anonymous, first name, full name, GitHub username, or forum username.
- Added `EMAIL_TEMPLATE.txt` with the contribution ID, archive name, recognition preference, and tester-notes prompts.
- Added `BUNDLE_QUALITY.txt` and manifest quality fields driven by the final residual privacy audit.
- Added a clearer review receipt, privacy summary, and next-step instructions in the Discovery log.
- Kept the validated bundle engine and sanitization behaviour unchanged.

## v1.1.4

- Masks bullet-style plain-text hostname fields such as `- sysName: switch.example.com` in Discovery reports.
- Extends the final residual audit to detect the same report-style hostname fields.
- Prevents a contribution archive from reporting a clean hostname audit while those values remain.
- Advances the Support My Switch bundle schema to version 5 and sanitization schema to version 3.

## v1.1.3

- Sanitizes copied switch data before device summaries and fingerprints are generated.
- Adds a final privacy pass across bundle-root metadata to prevent reintroduced hostnames.
- Masks numeric and symbolic IF-MIB ifAlias values when interface-description masking is enabled.
- Masks VLAN labels consistently while preserving numeric VLAN IDs for analysis.
- Adds a final residual privacy audit and records any remaining enabled-category findings.
- Advances Support My Switch bundle schema to version 4.

## v1.1.2

- Added privacy processing for contribution bundles using only a temporary copy.
- Credential-like values are always removed before archive creation.
- Added configurable masking for management IPs, MAC addresses, hostnames/domains, VLAN names, and interface descriptions.
- Added machine-readable and human-readable sanitization reports.
- Updated bundle manifest schema to version 3 with privacy selections and replacement counts.
- Live `/share/switch_vision/` data remains untouched.

## v1.1.1

- Replaced development-stage wording with a user-facing Support My Switch workflow.
- Added a concise completion summary with contribution ID, archive size, file count, privacy state, and output path.
- Added `DEVICE_SUMMARY.json` from discovered capability sidecars.
- Added deterministic SHA-256 device fingerprints for grouping repeated contributions from the same hardware profile.
- Expanded `MANIFEST.json` to bundle schema version 2 with device counts and fingerprint references.
- Kept the live `/share/switch_vision` folder read-only and excluded prior contribution archives.
- Privacy sanitization remains a later test stage; generated bundles still require review before sharing.

## v1.1.0

- Added the first testable Support My Switch bundle engine.
- Added an add-on option to archive the complete `/share/switch_vision/` data folder.
- Generates sequential contribution IDs such as `[contribution reference withheld]`.
- Adds a manifest, contribution ID, README, and sanitization status report.
- Excludes the contributions output folder to prevent recursive archives.
- Never modifies the live Switch Vision data folder.
- Stage 1 bundles are intentionally unsanitized and must be reviewed before sharing.

## v1.0.0

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

## v0.9.13

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

## v0.9.0

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
