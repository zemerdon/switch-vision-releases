# Supported Devices

This document is generated from `devices/supported_devices.yaml`.
Only exact model identifiers are listed. Support for one SKU does not imply support for nearby variants.

| Vendor | Family | Exact model | RJ45 | Uplinks | PoE | Stack | Recommended faceplate | Calibration profile | Uplink validation | Status | Last validated |
|---|---|---|---:|---:|---|---|---|---|---|---|---|
| Cisco | Catalyst 3650 | `WS-C3650-48PD-E` | 48 | 2 Gigabit SFP + 2 10G SFP+ | Yes | Yes | `faceplates/48rj45-4sfp.png` | `default_cisco_48_port` | Confirmed | Confirmed | v1.8.0 |
| Cisco | Catalyst 3650 | `WS-C3650-48PD-L` | 48 | 2 Gigabit SFP + 2 10G SFP+ | Yes | Yes | `faceplates/48rj45-4sfp.png` | `default_cisco_48_port` | Confirmed | Confirmed | v1.8.0 |
| Cisco | Catalyst 2960X | `WS-C2960X-48FPD-L` | 48 | 2 10G SFP+ | Yes | No | `faceplates/48rj45-2sfp.png` | `cisco_2960s_48p` | Confirmed | Confirmed | v1.8.26 |
| Cisco | Catalyst 2960X | `WS-C2960X-24PS-L` | 24 | 4 Gigabit SFP | Yes | No | `faceplates/24rj45-4sfp.png` | `cisco_2960x_24p` | Pending | Experimental | v1.8.0 |
| Cisco | Catalyst 2960X | `WS-C2960X-24TS-L` | 24 | 4 Gigabit SFP | No | Yes | `faceplates/24rj45-4sfp.png` | `cisco_2960x_24p` | Pending | Community Validated | v1.8.25 |
| Cisco | Catalyst 2960S | `WS-C2960S-48FPD-L` | 48 | 2 10G SFP+ | Yes | No | `faceplates/48rj45-2sfp.png` | `cisco_2960s_48p` | Confirmed | Confirmed | v1.8.26 |
| Cisco | Catalyst 3560-C | `WS-C3560CG-8PC-S` | 8 | 2 Gigabit SFP | Yes | No | `faceplates/c3560cg-8pc-s.png` | `cisco_3560cg_8pc` | Pending | Community Validated | v1.8.24 |
| Juniper | EX3300 | `EX3300-48P` | 48 | 4 Gigabit SFP + 4 10G SFP+ | Yes | No | `faceplates/48rj45-4sfp.png` | `default_cisco_48_port` | Confirmed | Confirmed | v1.8.26 |
| Cisco | Small Business SG500X | `SG500X-24` | 24 | 4 10G SFP+ | No | Yes | `faceplates/24rj45-4sfp.png` | `cisco_2960x_24p` | Candidate | Community Validated | v2.0.22 |
| Huawei | S5720 | `S5720-12TP-LI-AC` | 8 | 4 Gigabit SFP | No | No | `faceplates/24rj45-4sfp.png` | `stock_24rj45_4sfp` | Exact Model Profile Ports 9 12 1G Sfp Pending Live Card Validation | Community Validated | v2.0.31 |
| Zyxel | XS1930 | `XS1930-10` | 8 | 2 10G SFP+ | No | No | `faceplates/c3560cg-8pc-s.png` | `cisco_3560cg_8pc` | Contribution Confirmed Ifindex 9 10 Swp08 Swp09 | Experimental | v2.1.7 |
| Ubiquiti | UniFi Switch Enterprise | `USW-Enterprise-8-PoE` | 8 | 2 10G SFP+ | Yes | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Candidate Repeated Evidence | Experimental | v2.0.32 |
| Ubiquiti | UniFi Switch Pro | `USW-Pro-24-PoE` | 24 | 2 10G SFP+ | Yes | No | `faceplates/unifi-24p-rj45-2sfp.png` | `unifi_24p_rj45_2sfp` | Candidate Media Pending Validation | Experimental | v2.0.32 |
| Ubiquiti | UniFi Switch Lite | `USW Lite 16 PoE` | 16 | 0 none | Yes | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Not Applicable | Experimental | v2.0.32 |
| Ubiquiti | UniFi Switch Pro XG | `USW Pro XG 8 PoE` | 8 | 2 10G SFP+ | Yes | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Api Confirmed Connector And Speed | Experimental | v2.0.32 |
| Huawei | S5735-L | `S5735-L8P4X-A1` | 8 | 4 10G SFP+ | Yes | No | `faceplates/24rj45-4sfp.png` | `stock_24rj45_4sfp` | Candidate Repeated Interface Evidence | Community Validated | v2.0.31 |
| Ubiquiti | UniFi Dream Machine Pro | `UDM Pro` | 9 | 2 10G SFP+ | No | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Live Api Confirmed Connector And Speed | Experimental | v2.0.32 |
| Dell | Dell EMC Networking N2000 | `N2128PX-ON` | 28 | 2 10G SFP+ | Yes | Yes | `faceplates/48rj45-4sfp.png` | `default_cisco_48_port` | Contribution Confirmed Te Member 0 1 2 As 10G Sfp Plus | Experimental | v2.1.20 |
| Ubiquiti | UniFi Switch | `US 48 PoE 500W` | 48 | 2 Gigabit SFP + 2 10G SFP+ | Yes | No | `faceplates/48rj45-4sfp.png` | `stock_48rj45_4sfp` | Live Api Confirmed Connector And Speed | Experimental | v2.1.15 |
| Ubiquiti | UniFi Switch | `US 48` | 48 | 2 Gigabit SFP + 2 10G SFP+ | No | No | `faceplates/48rj45-4sfp.png` | `stock_48rj45_4sfp` | Live Api Confirmed Ports 49 50 10G Sfp Plus 51 52 1G Sfp | Experimental | v2.4.9 |
| Ubiquiti | UniFi Switch XG | `US XG 16` | 4 | 12 10G SFP+ | No | No | `Pending` | `Pending` | Live Api Confirmed Api Ports 1 12 10G Sfp Plus | Detected | v2.4.9 |
| Ubiquiti | UniFi Switch Pro Aggregation | `USW Pro Aggregation` | 0 | 28 10G SFP+ + 4 25G SFP28 | No | No | `Pending` | `Pending` | Live Api Confirmed 28X10G Sfp Plus 4X25G Sfp28 | Detected | v2.4.9 |
| Ubiquiti | UniFi Switch 8 60W | `US 8 60W` | 8 | 0 none | Yes | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Not Applicable | Experimental | v2.1.19 |
| Ubiquiti | UniFi Switch Flex | `USW Flex` | 5 | 0 none | Yes | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Live Api Confirmed Connector And Speed | Experimental | v2.1.16 |
| Ubiquiti | UniFi Switch Flex 2.5G 8 PoE | `USW Flex 2.5G 8 PoE` | 9 | 1 10G SFP+ | Yes | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Live Api Confirmed Connector And Speed | Experimental | v2.1.16 |
| Ubiquiti | UniFi Switch Flex Mini | `USW Flex Mini` | 5 | 0 none | No | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Not Applicable | Experimental | v2.1.19 |
| Ubiquiti | UniFi Switch Pro 24 | `USW Pro 24` | 24 | 2 10G SFP+ | No | No | `faceplates/unifi-24p-rj45-2sfp.png` | `unifi_24p_rj45_2sfp` | Live Api Confirmed Two 10G Sfp Plus | Experimental | v2.1.19 |
| Ubiquiti | UniFi Switch 16 PoE | `USW-16-PoE` | 16 | 2 Gigabit SFP | Yes | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Live Api Confirmed Connector And Speed | Experimental | v2.1.16 |
| Ubiquiti | UniFi Switch 24 PoE | `USW-24-PoE` | 24 | 2 Gigabit SFP | Yes | No | `faceplates/unifi-24p-rj45-2sfp.png` | `unifi_24p_rj45_2sfp` | Live Api Confirmed Connector And Speed | Experimental | v2.1.19 |
| Ubiquiti | UniFi Switch Lite 8 PoE | `USW-Lite-8-PoE` | 8 | 0 none | Yes | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Live Api Confirmed Connector And Speed | Experimental | v2.1.16 |
| Ubiquiti | UniFi Dream Machine Pro SE | `UniFi Dream Machine PRO SE` | 9 | 2 10G SFP+ | Yes | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Live Api Confirmed Ports 10 11 10G Sfp Plus | Experimental | v2.1.19 |
| Ubiquiti | UniFi Cloud Gateway Ultra | `UCG Ultra` | 5 | 0 none | No | No | `Pending` | `Pending` | Not Applicable | Detected | v2.4.10 |
| Ubiquiti | UniFi Switch 16 PoE 150W | `US 16 PoE 150W` | 16 | 2 Gigabit SFP | Yes | No | `Pending` | `Pending` | Live Api Confirmed Ports 17 18 1G Sfp | Detected | v2.4.10 |
| Ubiquiti | UniFi Switch Pro Max 24 | `USW Pro Max 24` | 24 | 2 10G SFP+ | No | No | `faceplates/unifi-24p-rj45-2sfp.png` | `unifi_24p_rj45_2sfp` | Live Api Confirmed Ports 25 26 10G Sfp Plus | Experimental | v2.4.10 |
| Ubiquiti | UniFi Switch Ultra | `USW Ultra` | 8 | 0 none | Yes | No | `Pending` | `Pending` | Not Applicable | Detected | v2.4.10 |
| Cisco | Catalyst 3750 | `WS-C3750-48P` | 48 | 4 Gigabit SFP | Yes | Yes | `faceplates/48rj45-4sfp.png` | `default_cisco_48_port` | Candidate Four 1G Sfp Pending Live Validation | Experimental | v2.4.12 |
| Ubiquiti | UniFi Dream Machine Pro Max | `UDM Pro Max` | 9 | 2 10G SFP+ | No | No | `faceplates/24rj45-2sfp.png` | `stock_24rj45_2sfp` | Community Api Ports 10 11 10G Sfp Plus Confirmed Pending Rendered Validation | Experimental | v2.4.14 |
| Ubiquiti | UniFi Switch Pro XG | `USW Pro XG 24 PoE` | 24 | 2 25G SFP28 | Yes | No | `faceplates/unifi-24p-rj45-2sfp.png` | `unifi_24p_rj45_2sfp` | Community Api Ports 25 26 25G Sfp28 Confirmed Pending Rendered Validation | Experimental | v2.4.14 |

## Status definitions

- **Detected:** Model identification works, but telemetry and layout are not validated.
- **Experimental:** A profile exists, but real-hardware validation is incomplete.
- **Community Validated:** A contributor has tested the model successfully on real hardware.
- **Confirmed:** Repeatably tested and treated as officially supported.

## Exact-model policy

Each hardware SKU receives its own entry. The registry does not use aliases to infer support for licence, uplink, PoE, regional, or revision variants.
