# Switch Vision Releases

![Switch Vision](https://switch-vision.zemerdon.com/icon_pack/release.png)

**Switch Vision** is a Home Assistant network-switch visualisation platform. It discovers supported switches, generates SNMP2MQTT and dashboard configuration, and presents ports, activity, VLANs, PoE, health information, stack members, and selected-port details through an interactive dashboard.

This repository contains the **official public release packages** for Switch Vision.

---

## Current Public Release

### Switch Vision v1.9.39

Switch Vision v1.9.39 is the current tested public-release baseline.

It includes:

- Native Home Assistant sidebar dashboard
- Automatic exact-model switch discovery
- Generated SNMP2MQTT configuration
- Automatic dashboard-card generation
- Port link, speed, traffic, VLAN, trunk, and PoE presentation
- CPU, temperature, uptime, and system-health monitoring
- Stack-member support
- Selected-port information
- Two configurable switch status boxes
- Visual faceplate and calibration tools
- Independent Link/Speed and Activity LED geometry
- Per-status LED visibility controls
- Model-aware reset actions
- Safe concurrent calibration-profile storage
- Support My Switch contribution bundles with privacy processing
- Diagnostics and central links to related Switch Vision tools
- Public-release packaging, checksums, and updated documentation

The next protected Gold baseline is planned as **Switch Vision v2.0.0**, after the final featured faceplate set, approved default positions, and complete regression testing are finished.

---

## Download

Download the latest installable release from GitHub Releases:

[Download the latest Switch Vision release](https://github.com/zemerdon/switch-vision-releases/releases/latest)

Browse all published releases:

[View all Switch Vision releases](https://github.com/zemerdon/switch-vision-releases/releases)

---

## Installation

A current Switch Vision release contains these main installation folders:

```text
local_apps/switch_vision_discovery/
custom_components/switch_vision/
www/switch-vision/
```

Install them as follows:

```text
local_apps/switch_vision_discovery/  -> /addons/local/switch_vision_discovery/
custom_components/switch_vision/     -> /config/custom_components/switch_vision/
www/switch-vision/                   -> /config/www/switch-vision/
```

After replacing the Discovery app files, reload the Home Assistant app store and **rebuild** the Switch Vision Discovery app before starting it again.

Switch Vision also requires the separate SNMP2MQTT app:

[Switch Vision SNMP2MQTT app](https://github.com/zemerdon/switch-vision-snmp2mqtt-addon)

The Switch Vision Installer can simplify installation, updates, backups, restoration, and repair:

[Switch Vision Installer](https://github.com/zemerdon/switch-vision-installer)

### Installation guides

- [Easy Setup and Installation](https://switch-vision.zemerdon.com/viewtopic.php?t=44)
- [Clean Installation — Advanced](https://switch-vision.zemerdon.com/viewtopic.php?t=56)
- [Upgrade and Browser Cache Guide](https://switch-vision.zemerdon.com/viewtopic.php?t=57)

---

## Supported Hardware

Switch Vision support is tracked by **exact model identifier**. Similar-looking models can expose different uplinks, stack layouts, PoE capabilities, and SNMP data.

### Registered and validated models

- Cisco `WS-C3650-48PD-E`
- Cisco `WS-C3650-48PD-L`
- Cisco `WS-C2960X-24TS-L`
- Cisco `WS-C2960X-48FPD-L`
- Cisco `WS-C2960S-48FPD-L`
- Cisco `WS-C3560CG-8PC-S`

### Experimental support

- Juniper `EX3300-48P`
- Additional Cisco models undergoing community validation

Experimental devices may already provide working discovery, ports, telemetry, VLAN, or PoE information while still requiring validation of uplinks, stacking, optics, sensors, or exact faceplate geometry.

[Open the Supported Devices Index](https://switch-vision.zemerdon.com/viewtopic.php?t=74)

---

## Main Features

### Automatic Discovery

Switch Vision Discovery can:

- Query switches using SNMP
- Detect exact models and physical interfaces
- Identify switch and stack-member details
- Map RJ45 ports and uplinks
- Collect VLAN, trunk, PoE, and capability information
- Generate SNMP2MQTT configuration
- Generate native-dashboard card configuration
- Create diagnostics and privacy-processed contribution bundles

Generated files are stored under:

```text
/share/switch_vision/
```

Important generated files include:

```text
/share/switch_vision/generated-dashboard-card.yaml
/share/switch_vision/generated-snmp2mqtt.yaml
```

### Native Home Assistant Dashboard

The Switch Vision integration provides:

- Automatic switch cards in the Home Assistant sidebar
- Sidebar show and hide controls
- Automatic generated-dashboard loading
- Built-in resource loading for the native panel
- Calibration access from each switch card
- Atomic dashboard refreshes that preserve working cards if a refresh fails
- Cross-browser calibration updates
- Runtime version reporting and frontend cache handling

Custom YAML dashboards remain supported. They require the Switch Vision Lovelace resource and any additional dashboard resources used by the YAML, such as Layout Card.

### Port Visualisation

Switch Vision can display:

- Port link state
- Link speed
- Transmit and receive activity
- Interface descriptions
- VLAN membership
- Access and trunk state
- Duplex information
- PoE state and usage
- Stack-member association
- Selected-port details

VLAN information can be presented as:

```text
VLAN 10
VLANS 1, 10, 30
VLAN TRUNK
```

### Calibration and Faceplates

The calibration tool supports:

- Port positioning and sizing
- Adding and removing ports for custom layouts
- Link/Speed LED positioning, sizing, and circle or rectangle shapes
- Activity LED positioning, sizing, and circle or rectangle shapes
- Port labels and numbering
- Faceplate selection with a visible model-aware fallback
- Logo selection and visibility
- Individual status LED visibility
- Status Box 1
- Status Box 2
- Selected Port Status Box
- Independent field-label and value positioning
- Stack-member presentation
- Reset Current Faceplate
- Reset Current Switch
- Reset All Switches
- Profile import, export, validation, and safe storage

Recognised models receive their registered profile automatically. Unknown models receive a visible fallback profile that can be customised until an official or community profile becomes available.

Calibration changes do not alter SNMP credentials, Discovery settings, Home Assistant entities, or generated SNMP2MQTT configuration.

---

## Support My Switch

Unsupported and experimental devices can be submitted through the Switch Vision contribution workflow.

Contribution bundles can include:

- Targeted SNMP walks
- Device fingerprints
- Capability reports
- Discovery logs
- Generated configuration
- Privacy-audit information
- Device-registry matching results

The privacy processor inspects and sanitises contribution files before they are marked ready to share. Unsupported, unreadable, oversized, or otherwise uninspected files force **REVIEW REQUIRED** and are excluded from the prepared contribution archive.

Do not post raw SNMP walks or unreviewed contribution bundles publicly.

[Open Support My Switch](https://switch-vision.zemerdon.com/viewtopic.php?t=72)

---

## Release Files

A typical public release contains:

```text
switch-vision-X.Y.Z.zip
Switch_Vision_vX.Y.Z_source.zip
Switch_Vision_vX.Y.Z_SHA256SUMS.txt
Switch_Vision_vX.Y.Z_GitHub_Release_Notes.md
```

- `switch-vision-X.Y.Z.zip` is the normal installable package.
- `Switch_Vision_vX.Y.Z_source.zip` contains the corresponding public source package.
- The checksum file is used to verify archive integrity.
- The release-notes file contains the GitHub-ready release summary.

---

## Verify a Download

Release checksums are published with each release.

### Linux

```bash
sha256sum switch-vision-X.Y.Z.zip
sha256sum Switch_Vision_vX.Y.Z_source.zip
```

### Windows PowerShell

```powershell
Get-FileHash .\switch-vision-X.Y.Z.zip -Algorithm SHA256
Get-FileHash .\Switch_Vision_vX.Y.Z_source.zip -Algorithm SHA256
```

Compare the result with the checksum file attached to the GitHub Release.

---

## Updating

Do not merge files from different Switch Vision releases.

Follow the update scope published with each release. Depending on what changed, an update may require:

- Replacing the custom component
- Replacing frontend assets
- Restarting Home Assistant Core
- Replacing and rebuilding Switch Vision Discovery
- Running Discovery again
- Restarting Switch Vision SNMP2MQTT
- Performing a browser hard refresh

Preserve these locations unless the release notes explicitly instruct otherwise:

```text
/config/.storage/switch_vision_calibrations
/share/switch_vision/
```

Back up custom assets before replacing the frontend folder:

```text
/config/www/switch-vision/faceplates/
/config/www/switch-vision/logos/
```

[Open the Upgrade and Browser Cache Guide](https://switch-vision.zemerdon.com/viewtopic.php?t=57)

---

## Documentation

- [Switch Vision Community Forum](https://switch-vision.zemerdon.com)
- [Easy Setup and Installation](https://switch-vision.zemerdon.com/viewtopic.php?t=44)
- [Clean Installation — Advanced](https://switch-vision.zemerdon.com/viewtopic.php?t=56)
- [Automatic Dashboard and Sidebar](https://switch-vision.zemerdon.com/viewtopic.php?t=47)
- [Configuration Field Reference](https://switch-vision.zemerdon.com/viewtopic.php?t=70)
- [Supported Devices Index](https://switch-vision.zemerdon.com/viewtopic.php?t=74)
- [Support My Switch](https://switch-vision.zemerdon.com/viewtopic.php?t=72)

---

## Support

For installation help, bug reports, supported-device questions, or contribution guidance:

- Forum: [Switch Vision Community](https://switch-vision.zemerdon.com)
- Email: `switch-vision@zemerdon.com`
- Main project issues: [zemerdon/switch-vision issues](https://github.com/zemerdon/switch-vision/issues)

---

## Project Repositories

- Main project and public source: [zemerdon/switch-vision](https://github.com/zemerdon/switch-vision)
- Public releases: [zemerdon/switch-vision-releases](https://github.com/zemerdon/switch-vision-releases)
- Switch Vision Installer: [zemerdon/switch-vision-installer](https://github.com/zemerdon/switch-vision-installer)
- SNMP2MQTT app: [zemerdon/switch-vision-snmp2mqtt-addon](https://github.com/zemerdon/switch-vision-snmp2mqtt-addon)

---

## Release Channel

Switch Vision uses tested public releases and protected **Gold** baselines.

Public and Gold releases are validated against:

- Build and archive integrity
- Runtime and source version consistency
- Supported-device registry generation
- Home Assistant integration behaviour
- Native-sidebar and custom-YAML rendering
- Calibration save, reset, import, and profile isolation
- Model-aware default profiles
- Discovery output
- Support My Switch contribution workflow
- Privacy-report generation
- Package hygiene and checksum verification

The current tested public baseline is:

```text
Switch Vision v1.9.39
```

The next planned protected Gold baseline is:

```text
Switch Vision v2.0.0 Gold
```

---

## Licence and Distribution

No open-source licence is currently included with Switch Vision. Unless a release states otherwise, copyright is retained by the project owner.

Official packages are distributed through the Switch Vision project repositories. Modified builds must not be represented as official Switch Vision releases.

---

<p align="center">
  <strong>Switch Vision</strong><br>
  Network switch visibility for Home Assistant
</p>
