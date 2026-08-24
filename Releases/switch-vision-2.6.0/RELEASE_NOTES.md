# Switch Vision Core v2.6.0

Core 2.6.0 adds a separate geometry-only calibration transfer workflow without replacing or weakening the existing full faceplate-profile import/export path.

**Export Geometry** produces a versioned `switch-vision-geometry-profile-v1` payload containing only canvas dimensions, RJ45/SFP/status-LED coordinates and hitbox/size data, plus positional geometry for the logo, status panels/field coordinates and calibration button. **Import Geometry** applies that geometry onto the current destination calibration rather than replacing the calibration object.

The current destination keeps its faceplate/background artwork, logo asset/source, styles, visibility, labels, stack, management settings and profile identity. Geometry import also requires the same RJ45, SFP/uplink and status-LED key sets as the destination, so it cannot silently alter topology or hardware mapping.

A permanent executable regression injects foreign artwork/source identifiers into a hand-edited geometry payload and verifies that those identifiers cannot cross the geometry-only import boundary while legitimate geometry still applies.

No hardware mapping, connector, PoE, polling, telemetry, maximum-capability, support-status, Discovery/UniFi2MQTT or privacy contracts change in Core 2.6.0.
