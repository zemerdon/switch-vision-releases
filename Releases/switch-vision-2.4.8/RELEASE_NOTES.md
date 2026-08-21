# Switch Vision Core v2.4.8

Core 2.4.8 fixes SFP status-panel speed presentation. Generic SFP links now use the existing negotiated/current-speed resolver instead of assuming every active non-UniFi uplink is 10G.

This fixes Huawei S5720 1G SFP uplinks showing **10G Full** even though Discovery and SNMP telemetry correctly report 1G. Existing 10G SFP+, UniFi, link-down, traffic, Activity LED, calibration geometry, Discovery handoff, device mapping, and saved calibration behaviour are unchanged.
