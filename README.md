# Switch Vision Releases

![Switch Vision](https://switch-vision.zemerdon.com/icon_pack/release.png)

**Switch Vision** is a Home Assistant-based network switch visualisation platform that discovers supported switches, generates SNMP2MQTT configuration, and creates an interactive dashboard showing ports, activity, VLANs, PoE, system health, stack members, and selected-port details.

This repository contains the **public installable release packages** for Switch Vision.

---

## Current Gold Release

### Switch Vision v1.8.0 Gold

Switch Vision v1.8.0 is the current stable and protected Gold baseline.

It includes:

- native Home Assistant sidebar dashboard
- automatic switch discovery
- generated SNMP2MQTT configuration
- automatic dashboard-card generation
- port status and traffic activity
- VLAN and trunk presentation
- PoE, CPU, temperature, and uptime monitoring
- switch stack-member support
- two independent switch status boxes
- dedicated selected-port status information
- visual calibration tools
- Support My Switch contribution bundles
- exact-model device registry
- Cisco and experimental Juniper support

---

## Download

Download the latest installable release from the GitHub Releases page:

[Download the latest Switch Vision release](https://github.com/zemerdon/switch-vision-releases/releases/latest)

For older versions, visit:

[All Switch Vision releases](https://github.com/zemerdon/switch-vision-releases/releases)

---

## Installation

Switch Vision is installed using three main components from the release package:

```text
addons/switch_vision_discovery/
custom_components/switch_vision/
www/switch-vision/
