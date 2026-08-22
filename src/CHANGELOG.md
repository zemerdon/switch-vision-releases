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
