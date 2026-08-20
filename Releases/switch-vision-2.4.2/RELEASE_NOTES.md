# Switch Vision Core v2.4.2 — Hardware validation safeguards

- Promotes `WS-C2960X-24TS-L`, `WS-C3560CG-8PC-S`, `SG500X-24`, `S5735-L8P4X-A1`, and `S5720-12TP-LI-AC` to **Community Validated** from existing real-hardware evidence.
- Preserves `WS-C3560CG-8PC-S` Gi0/9 and Gi0/10 dual-purpose combo-uplink semantics.
- Records the Huawei `S5720-12TP-LI-AC` physical layout as 8 RJ45 + 4 physical 1G SFP cages; Discovery v2.1.27 owns the matching 1G speed-cap safeguard.
- Keeps all 28 exact-model records aligned with Discovery and gives every known Ubiquiti model an explicit non-Cisco faceplate/profile assignment based on its real API geometry.
- Adds permanent Core regression coverage proving 2500 Mbps renders as `2.5G`, never `3G`.
- Makes the HAOS/manual Lovelace resource cache-buster a mandatory release contract: `/local/switch-vision/js/switch-vision.js?v=<version>` must match the Core release.
- Keeps MQTT topics, saved calibrations, Activity LED behaviour, and TEST MODE behaviour unchanged.

After updating Core through Switch Vision Installer, restart Home Assistant Core when prompted and hard-refresh the browser. If a manual Lovelace resource is configured, ensure its `?v=` suffix is `2.4.2`.
