# Switch Vision Core v2.3.1 — Calibration flexibility update

Switch Vision Core v2.3.1 expands the interactive calibration workspace for faster model-specific faceplate creation, including the first UniFi faceplate calibration work in the v2.3 release line.

Custom port selection now supports both RJ45 port numbers/ranges and case-insensitive SFP/uplink aliases such as `g1` and `te2`. Selected uplink groups can be positioned, resized, and calibrated independently rather than requiring all SFP ports to be edited together.

Every RJ45 and SFP/uplink visual port can now carry an optional display-name override. The display name affects presentation only; the underlying port identity and telemetry mapping remain unchanged.

Port-label presentation gains shared Normal/Bold control plus independent RJ45 and SFP/uplink font sizing up to 50 px. Status LED and Status Box font-size controls also extend to 50 px.

The calibration workspace now opens with Assets first and expanded, Selection collapsed, Position & Size expanded, and the remaining sections collapsed. Reset section layout restores this default arrangement.

The release preserves existing Discovery, SNMP2MQTT, UniFi2MQTT, entity, telemetry, Activity LED 2.0, dashboard, faceplate, and calibration-profile behaviour outside these calibration-tool improvements.
