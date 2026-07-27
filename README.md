# Switch Vision Releases

![Switch Vision](https://switch-vision.zemerdon.com/icon_pack/release.png)

**Switch Vision** is a Home Assistant network-switch visualisation platform that discovers supported switches, generates SNMP2MQTT configuration, and creates an interactive dashboard showing ports, activity, VLANs, PoE, system health, stack members, and selected-port details.

This repository contains the **public installable release packages** for Switch Vision.

---

## Current Gold Release

### Switch Vision v1.8.0 Gold

Switch Vision v1.8.0 is the current stable and protected Gold baseline.

It includes:

- Native Home Assistant sidebar dashboard
- Automatic switch discovery
- Generated SNMP2MQTT configuration
- Automatic dashboard-card generation
- Port status and traffic activity
- VLAN and trunk presentation
- PoE, CPU, temperature, and uptime monitoring
- Switch stack-member support
- Two independent switch status boxes
- Dedicated selected-port status information
- Visual calibration tools
- Support My Switch contribution bundles
- Exact-model device registry
- Confirmed Cisco support and experimental Juniper support

---

## Download

Download the latest installable release from GitHub Releases:

[Download the latest Switch Vision release](https://github.com/zemerdon/switch-vision-releases/releases/latest)

Browse all published releases:

[View all Switch Vision releases](https://github.com/zemerdon/switch-vision-releases/releases)

---

## Installation

A Switch Vision release contains three main installation folders:

```text
addons/switch_vision_discovery/
custom_components/switch_vision/
www/switch-vision/
```

Copy them to:

```text
/addons/switch_vision_discovery/
/config/custom_components/switch_vision/
/config/www/switch-vision/
```

Switch Vision also requires the separate SNMP2MQTT add-on:

[Switch Vision SNMP2MQTT add-on](https://github.com/zemerdon/switch-vision-snmp2mqtt-addon)

### Installation guides

- [Easy Setup and Installation](https://switch-vision.zemerdon.com/viewtopic.php?t=44)
- [Clean Installation — Advanced](https://switch-vision.zemerdon.com/viewtopic.php?t=56)
- [Upgrade and Browser Cache Guide](https://switch-vision.zemerdon.com/viewtopic.php?t=57)

---

## Supported Hardware

Switch Vision support is tracked by **exact model identifier**.

### Confirmed supported

- Cisco `WS-C3650-48PD-E`
- Cisco `WS-C3650-48PD-L`

### Experimental

- Cisco `WS-C2960X-48FPD-L`
- Cisco `WS-C2960X-24PS-L`
- Cisco `WS-C2960S-48FPD-L`
- Juniper `EX3300-48P`

Experimental devices may have working discovery, ports, telemetry, VLANs, or PoE support while still requiring uplink, stacking, optical, or hardware validation.

[Open the Supported Devices Index](https://switch-vision.zemerdon.com/viewtopic.php?t=74)

---

## Main Features

### Automatic Discovery

Switch Vision Discovery can:

- Query switches using SNMP
- Detect exact models and interfaces
- Identify stack members
- Map physical ports
- Collect VLAN and PoE information
- Generate SNMP2MQTT configuration
- Generate dashboard-card configuration
- Create diagnostic and contribution bundles

### Native Home Assistant Dashboard

The Switch Vision integration provides:

- Automatic switch cards
- Sidebar show and hide controls
- Calibration-button controls
- Runtime version reporting
- Automatic generated-dashboard loading
- Frontend cache and version handling

### Port Visualisation

Switch Vision can display:

- Port link state
- Transmit and receive activity
- Interface descriptions
- VLAN membership
- Access and trunk state
- Speed and duplex
- PoE state
- Stack-member association
- Selected-port details

VLAN information is shown as:

```text
VLAN 10
VLANS 1, 10, 30
VLAN TRUNK
```

### Calibration

The calibration tool supports:

- Port positioning and sizing
- LED positioning
- Port labels and numbering
- Faceplate selection
- Logo selection
- Status Box 1
- Status Box 2
- Port Status Box
- Individual field-label and value positioning
- Stack-member presentation
- Reset target
- Reset all

Calibration changes do not alter SNMP, Discovery, entity, or generated-YAML settings.

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

Do not post raw SNMP walks or contribution bundles publicly.

[Open Support My Switch](https://switch-vision.zemerdon.com/viewtopic.php?t=72)

---

## Release Files

A typical public release contains:

```text
switch-vision-X.Y.Z.zip
SHA256SUMS.txt
CHANGELOG.md
```

The installable ZIP is the normal user-facing package.

Private development source archives are not distributed from this repository unless explicitly published.

---

## Verify a Download

Release checksums are published with each release.

### Linux

```bash
sha256sum switch-vision-X.Y.Z.zip
```

### Windows PowerShell

```powershell
Get-FileHash .\switch-vision-X.Y.Z.zip -Algorithm SHA256
```

Compare the result with the checksum published in the GitHub Release.

---

## Updating

Do not merge files from different Switch Vision releases.

Follow the update scope published with each release. An update may require:

- Replacing the custom component
- Restarting Home Assistant Core
- Replacing and rebuilding Switch Vision Discovery
- Replacing frontend assets
- Running Discovery again
- Restarting Switch Vision SNMP2MQTT
- Performing a browser hard refresh

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

---

## Project Repositories

- Public releases: [zemerdon/switch-vision-releases](https://github.com/zemerdon/switch-vision-releases)
- SNMP2MQTT add-on: [zemerdon/switch-vision-snmp2mqtt-addon](https://github.com/zemerdon/switch-vision-snmp2mqtt-addon)

---

## Release Channel

Switch Vision uses a protected **Gold** baseline.

Gold releases are validated against:

- Build and archive integrity
- Runtime and source version consistency
- Supported-device registry generation
- Home Assistant integration behaviour
- Discovery output
- Dashboard rendering
- Contribution workflow
- Privacy-report generation
- Python cache and test artefact exclusion

The current Gold baseline is:

```text
Switch Vision v1.8.0 Gold
```

---

## Licence and Distribution

Switch Vision release packages are provided for installation and use through the official Switch Vision project.

Do not redistribute modified packages as official Switch Vision releases.

---

<p align="center">
  <strong>Switch Vision</strong><br>
  Network switch visibility for Home Assistant
</p>
