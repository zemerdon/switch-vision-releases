# Switch Vision Core v2.6.3

Core 2.6.3 replaces the old Discovery/Installer **Normal / Small** appearance choice with an explicit **10–20 px** body-font setting in one-pixel steps. Existing installations remain valid: `normal` is read as 16 px and `small` as 14 px until the user next saves the setting.

The Hub and Home Assistant Configure fallback use the same range, and the shared UI-preferences document now publishes the normalized numeric value for Discovery and Installer consumers. A behavioral regression exercises every accepted pixel size plus the legacy migration and invalid-value fallback.

This is an appearance-settings contract change only. No switch mapping, physical geometry, connector, PoE, polling, telemetry, maximum-capability, support-status or privacy contracts change.

---

# Previous release: Switch Vision Core v2.6.2

Core 2.6.2 fixes **Export Geometry** in the calibration tool.

The geometry-only transfer serializer was using the full calibration normalizer to clone primitive values such as canvas width/height and coordinate arrays. Switch Vision frontend code runs as a Home Assistant ES module, where strict-mode assignment to those primitive values throws. The click handler was present, but the exception occurred before the browser download was created, making the button appear to do nothing.

Geometry-only serialization and application now use plain-data cloning for canvas dimensions, coordinates, hitboxes/sizes, status-panel field positions, status LEDs and the preserved faceplate presentation object. Full calibration normalization remains limited to complete calibration objects.

The permanent geometry-transfer regression now runs in strict mode, verifies a real geometry export payload, checks that geometry substructures cannot acquire unrelated calibration UI/stack/management data, and proves that an exported geometry profile can be imported back into the same calibration without changing artwork or presentation identity.

No switch mapping, physical port geometry values, connector, PoE, polling, telemetry, maximum-capability, support-status, Hub/Discovery/SNMP2MQTT runtime or privacy contracts change in Core 2.6.2.
