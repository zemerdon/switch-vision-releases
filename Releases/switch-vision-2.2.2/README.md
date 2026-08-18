# Switch Vision

Switch Vision is a Home Assistant platform for discovering managed network switches, generating SNMP2MQTT configuration, and displaying live switch activity on an interactive front-panel dashboard.

## Current release

- **Latest release:** v2.2.2
- **Release status:** **Support / compatibility release**
- **Gold baseline:** **v2.0.0 Gold**
- **Primary workflow:** Discovery-generated Home Assistant Lovelace dashboard; Native and Custom paths remain supported fallbacks
- **Manual dashboard YAML:** Supported as a permanent fallback
- **SNMP:** Read-only SNMP v2c

v2.0.0 is the protected Gold baseline, promoted directly from the final v1.9.97 pre-Gold codebase. It preserves the proven feature set and locks the current Installer, Discovery, native-dashboard, Calibration, faceplate, diagnostics, and support workflows as the stable 2.0 foundation.

## What Switch Vision includes

- Repository-managed Switch Vision Discovery app with a persistent Web UI
- Optional repository-managed Switch Vision UniFi2MQTT app for read-only UniFi Integration API telemetry
- Native Home Assistant **Switch Vision** sidebar dashboard
- Switch Vision Lovelace card for native and manual dashboards
- Home Assistant custom integration for the panel, calibration storage, asset browsing, and settings
- Exact-model supported-device registry
- Model-aware visual profiles and faceplates
- Faceplate-specific calibration profiles
- Calibration import, export, reset, and validation tools
- Support My Switch contribution workflow with privacy processing
- Diagnostics, installation, upgrade, troubleshooting, and development documentation

The Switch Vision SNMP2MQTT app is maintained separately. In the recommended installation path, the Switch Vision Installer installs and manages it for the user.

### Optional UniFi API bridge

Switch Vision supports the separately versioned **Switch Vision UniFi2MQTT** app. It is a read-only bridge for the official UniFi Network Integration API and is deliberately separate from the proven SNMP2MQTT path. Its source is maintained in its own public repository and is not bundled inside the main Switch Vision release ZIP.

UniFi2MQTT can publish model, firmware, online state, per-port link/speed/connector/PoE data, CPU, memory, uptime, and uplink rates through MQTT Discovery when the controller exposes those fields. Current live API samples do not expose per-port RX/TX traffic in the latest-statistics endpoint, so SNMP2MQTT remains the current source for per-port traffic counters. Discovery consumes the normalized UniFi snapshot and automatically generates Switch Vision cards for exact registered models; SNMP2MQTT remains the current source for per-port traffic counters when required.

The UniFi bridge requires a controller URL, site ID, read-only API key, and MQTT connection details as required by the local broker configuration. Its normalized local snapshot is written to `/share/switch_vision/unifi/devices.json`; Support My Switch privacy processing masks UniFi device names and stable IDs before packaging.

UniFi2MQTT is independently versioned and is configured from **Switch Vision Hub → UniFi2MQTT Settings**. The Hub can install the app when available, save its Home Assistant Supervisor options, and start/restart it without exposing stored secrets back to the browser. End users only need to add the Switch Vision Installer repository manually; the Installer remains the deployment layer while the Hub owns ongoing UniFi configuration.

## Normal workflow

```text
Install Switch Vision
→ Configure switches in Discovery
→ Run Discovery
→ Discovery identifies the exact model and generates configuration
→ Switch Vision starts or restarts SNMP2MQTT
→ Open Switch Vision from the Home Assistant sidebar
```

## Quick start

1. Add the **Switch Vision Installer** repository to Home Assistant: `https://github.com/zemerdon/switch-vision-installer`. This is the only repository end users need to add manually.
2. Install the **current Switch Vision release** through the Installer. The Installer manages the main Switch Vision files and registers/installs the separately versioned Discovery and SNMP2MQTT apps; UniFi2MQTT remains optional. v2.0.0 remains the protected Gold baseline. Core, Discovery, Installer, SNMP2MQTT, and UniFi2MQTT now advance on independent version lines.
3. Restart Home Assistant Core when requested and add the **Switch Vision** integration under **Settings → Devices & services**.
4. Open **Switch Vision Discovery**, add each switch, and leave **Switch Model** set to **Auto-detect** unless an explicit compatibility override is required.
5. Run Discovery.
6. Open **Switch Vision** from the Home Assistant sidebar.
7. Use **Calibrate** only when a visual adjustment is needed.

The generated custom dashboard YAML remains available for advanced users. No dashboard YAML copying is required for the normal v2.2.2 workflow.

For manual installation or an existing installation, use `docs/INSTALLATION.md` and `docs/UPGRADING.md` without merging files from different releases.

## Automatic native dashboard

The `switch_vision` integration registers a native Home Assistant panel named **Switch Vision**. It reads:

```text
/share/switch_vision/generated-dashboard-card.yaml
```

The native panel:

- loads its own frontend resources automatically;
- does not require a manually created Lovelace dashboard;
- does not write to Lovelace storage;
- does not modify unrelated dashboards;
- checks for updated generated card YAML while visible;
- builds replacement cards before swapping the visible dashboard;
- keeps the existing dashboard active when a refresh fails;
- cleans up event listeners when cards leave the page;
- uses versioned frontend URLs to reduce stale browser caching.

The generated YAML remains available as a manual fallback.

## Optional sidebar and calibration-button visibility

Open:

```text
Settings → Devices & services → Switch Vision → Configure
```

The integration can independently:

- show or hide the Switch Vision sidebar shortcut;
- show or hide Calibration buttons on cards in the automatic native dashboard.

Hiding the sidebar shortcut does not disable the panel URL, manual cards, Discovery, stored calibrations, or SNMP2MQTT. The Discovery app has its own separate **Show in sidebar** setting.

## Model detection and visual profiles

Discovery preserves the exact detected hardware SKU. Registered exact models with dashboard support enabled receive their mapped interface layout, calibration profile, and recommended visible faceplate. Some Experimental entries are intentionally detection/API-telemetry only until their dashboard path is validated.

The current bundled faceplates are:

```text
faceplates/24rj45-2sfp.png
faceplates/24rj45-4sfp.png
faceplates/48rj45-2sfp.png
faceplates/48rj45-4sfp.png
faceplates/c3560cg-8pc-s.png
faceplates/submarine-48rj45-4sfp.png
```

Examples of model-aware defaults include:

- Cisco 3650 48-port models → 48 RJ45 / 4 uplinks
- Cisco 2960S and supported 2960X 48-port models → 48 RJ45 / 2 uplinks
- Cisco 2960X 24-port models → 24 RJ45 / 4 uplinks
- Cisco WS-C3560CG-8PC-S → dedicated `c3560cg-8pc-s.png` faceplate with its bundled faceplate-specific defaults

An unknown or unregistered model receives a visible generic fallback. The user may calibrate that fallback or use a custom faceplate until a registered model profile becomes available. Existing user-saved topology remains authoritative and is not silently rebuilt to a factory port count.

A registered model may be selected manually as an experimental compatibility override. Reports retain the detected model, selected override, and effective mapping model. An override does not change the detected hardware's official support status.

See `docs/SUPPORTED_DEVICES.md` for the authoritative exact-model list.

## Faceplates and calibration

Switch Vision always keeps visible switch artwork. The faceplate selector provides:

- **Default / recommended** — resolves the bundled faceplate assigned to the exact model;
- a named custom faceplate — uses that image and its own calibration namespace.

Legacy hidden, blank, invalid, or `__none__` states migrate to the model-recommended visible faceplate. If a selected custom image is missing, Switch Vision displays the recommended faceplate instead of a blank switch.

Install custom assets in:

```text
/config/www/switch-vision/logos/
/config/www/switch-vision/faceplates/
```

Each custom faceplate receives its own saved geometry. Keep filenames stable because the filename is part of the faceplate-specific profile identity.

Calibration supports:

- adding or removing visual RJ45 ports and uplinks;
- moving and resizing ports, labels, uplinks, status LEDs, logos, status boxes, and the Calibration button;
- independent Link/Speed and Activity LED rectangle dimensions;
- Circle or Rectangle port LED shapes while chassis/status LEDs remain circular;
- per-status-LED visibility;
- safe profile import and export;
- atomic cross-browser profile saves;
- independent switch and faceplate profiles.

The principal actions are:

- **Save Profile** — validate and save without closing;
- **Done** — validate, save, and close;
- **Reset Current Faceplate** — restore bundled defaults for the selected faceplate when available, otherwise model factory geometry, while retaining the selected faceplate image;
- **Reset Current Switch** — remove that switch's saved faceplate-specific profiles and restore its exact-model defaults;
- **Reset All Switches** — clear saved Switch Vision calibrations and restore each loaded switch to its own model-aware defaults.

There is no separate **Apply Recommended Setup** action. Automatic exact-model detection and the reset actions are the authoritative model-profile paths.

## Calibration profile safety

Saved and imported profiles are checked for:

- safe profile names and asset filenames;
- supported canvas dimensions;
- positive, finite geometry values;
- reasonable coordinate ranges and element counts;
- payload size limits;
- matching stored profile identity.

Save, delete, reset, and profile-read operations share one asynchronous storage lock so simultaneous browser sessions do not overwrite unrelated profiles.

Calibration data is stored under Home Assistant `.storage`. Do not delete `.storage/switch_vision_calibrations` during a normal upgrade.

## Discovery Web UI

The Discovery app starts in **Idle / Ready** and keeps its Web UI available before, during, and after a run.

Main pages:

- **Discovery** — run and monitor Discovery;
- **Devices** — view detected hardware and generated state;
- **Support My Switch** — create a privacy-processed contribution package;
- **Diagnostics** — inspect installation and generated outputs;
- **Configuration** — export or import portable Discovery configuration.

Discovery writes:

```text
/share/switch_vision/generated-snmp2mqtt.yaml
/share/switch_vision/generated-dashboard-card.yaml
```

The Discovery Web UI shows **Generated Card YAML** directly above **Generated SNMP2MQTT YAML**, with validation, preview, copy, and download actions. The dashboard file remains review/copy only and is never installed automatically.

After a successful run, Discovery validates the generated SNMP2MQTT YAML, locates the installed Switch Vision SNMP2MQTT app dynamically through Supervisor, and starts or restarts it. A handoff warning does not invalidate an otherwise successful Discovery run.

## Portable Discovery configuration

Use **Discovery → Configuration → Export Configuration** to back up the configured switches, stack mappings, and Discovery settings. The export may contain management addresses and SNMP community strings, so store it securely.

Use **Import Configuration** on a fresh installation before editing the app options manually.


## Home Assistant community dashboard

On Home Assistant 2026.5 or newer, Switch Vision also registers a **Switch Vision** community dashboard strategy. After the integration is loaded:

1. Open **Settings → Dashboards**.
2. Select **Add dashboard**.
3. Choose **Switch Vision** under **Community dashboards**.
4. Create the dashboard and choose whether it appears in the sidebar.

This creates a genuine Home Assistant Lovelace dashboard and therefore allows Home Assistant's normal default-dashboard selection to target Switch Vision. The existing Native Switch Vision custom panel remains available as a separate fallback and is not removed or converted automatically.

## Manual dashboard fallback

The native dashboard is recommended, but this file remains available:

```text
/share/switch_vision/generated-dashboard-card.yaml
```

A manual/custom YAML dashboard requires the Switch Vision card resource:

```text
/local/switch-vision/js/switch-vision.js?v=2.2.2
```

Generated layouts that use Layout Card also require this HACS JavaScript Module:

```text
/hacsfiles/lovelace-layout-card/layout-card.js
```

Neither manual resource is required by the native Switch Vision sidebar panel.

## Support My Switch

Support My Switch creates a contribution package from a temporary copy of `/share/switch_vision/`. The live data folder is not modified.

Credentials are always removed. Optional controls can mask management IP addresses, MAC addresses, hostnames, VLAN names, and interface descriptions.

Every included file must be inspectable by the privacy processor. Unsupported binary files, oversized files, unreadable files, symbolic links, and special files are excluded from the temporary archive and force **REVIEW REQUIRED**. Their original names and paths are replaced by privacy-safe identifiers in `SANITIZATION_REPORT.txt`.

A fully inspected bundle can produce a ZIP, prepared `.eml`, and local action page. A **REVIEW REQUIRED** bundle produces the reviewable ZIP but withholds prepared send actions. Nothing is sent automatically.

Support email:

```text
switch-vision@zemerdon.com
```

Community forum:

```text
https://switch-vision.zemerdon.com
```

Public release repository:

```text
https://github.com/zemerdon/switch-vision-releases
```

## Hardware support levels

- **Detected** — hardware identity was recognised.
- **Experimental** — generated support exists but validation is incomplete.
- **Community Validated** — a contributor has successfully tested the implementation.
- **Confirmed Supported** — support has strong repeatable validation.

Real-hardware uplink operation is confirmed for the exact registered `WS-C2960X-48FPD-L`, `WS-C2960S-48FPD-L`, and standalone `EX3300-48P` models. The registered Cisco 2960X 24-port and Cisco 3560-C models remain Experimental pending model-specific validation. Juniper Virtual Chassis remains outside the confirmed scope.

## Documentation

- `RELEASE_NOTES.md`
- `docs/REQUIREMENTS.md`
- `docs/INSTALLATION.md`
- `docs/UPGRADING.md`
- `docs/DISCOVERY_WORKFLOW.md`
- `docs/FIELD_REFERENCE.md`
- `docs/TROUBLESHOOTING.md`
- `docs/SUPPORT_MY_SWITCH.md`
- `docs/SUPPORTED_DEVICES.md`
- `docs/BUILDING.md`
- `CONTRIBUTING.md`
- `SECURITY.md`

## Card header controls

Use the global **Show card headers** integration option to show or hide the complete header row on every native and custom YAML card. Discovery still supports an optional per-switch **Card header title**.

## Management UI themes

Switch Vision Hub includes a browser-local top-right theme selector with Switch Vision, Cisco Classic, Cisco Nexus, and UniFi palettes. Discovery UI Density remains controlled by the existing Switch Vision integration setting. Themes affect management pages only; Native, Lovelace, and Custom dashboards and switch-card rendering are intentionally unchanged.

## Support the project

Switch Vision is free and community-driven. If you find it useful and would like to support continued development, you can sponsor the project through GitHub Sponsors:

https://github.com/sponsors/zemerdon

