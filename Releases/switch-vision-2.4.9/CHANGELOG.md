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

## v2.4.7 — Audit hardening

- Strengthen admin-only mutation controls and exact-model visual safeguards.
- Preserve validated physical layouts without publishing contributor/tester identities.

## v2.4.6 — UniFi dark alternative faceplate

- Add a manually selectable dark UniFi faceplate with the same factory calibration geometry as the standard UniFi 24+2 visual.

## v2.4.5 — Native dashboard shortcut editor hotfix

- Fix Native dashboard shortcut navigation and simplify shortcut ordering/customization controls.

## v2.4.4 — Central sidebar and Native dashboard shortcuts

- Add centralized Switch Vision sidebar controls and Native-dashboard shortcuts.

## v2.4.3 — Huawei faceplate reset hotfix

- Restore neutral Huawei S5720/S5735 factory visual assignments.

## v2.4.2 — Hardware validation safeguards

- Promote real-hardware-tested exact models while preserving model-specific physical semantics and speed limits.

## v2.4.1 — Registry synchronization

- Synchronize additional exact-model knowledge into Core without changing support status.

## v2.4.0 — UniFi visual family

- Add the dedicated UniFi / Ubiquiti faceplate family and authoritative factory calibration.

## Earlier releases

Earlier detailed changelog entries have been consolidated from the public changelog as part of the Switch Vision public-attribution privacy policy. Public changelog and release-note text must not contain contributor/tester identities, submission identifiers, contribution package names, or submission filenames unless explicitly approved by the project owner.
