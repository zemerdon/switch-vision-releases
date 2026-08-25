# Switch Vision Core v2.6.2

Core 2.6.2 fixes **Export Geometry** in the calibration tool.

The geometry-only transfer serializer was using the full calibration normalizer to clone primitive values such as canvas width/height and coordinate arrays. Switch Vision frontend code runs as a Home Assistant ES module, where strict-mode assignment to those primitive values throws. The click handler was present, but the exception occurred before the browser download was created, making the button appear to do nothing.

Geometry-only serialization and application now use plain-data cloning for canvas dimensions, coordinates, hitboxes/sizes, status-panel field positions, status LEDs and the preserved faceplate presentation object. Full calibration normalization remains limited to complete calibration objects.

The permanent geometry-transfer regression now runs in strict mode, verifies a real geometry export payload, checks that geometry substructures cannot acquire unrelated calibration UI/stack/management data, and proves that an exported geometry profile can be imported back into the same calibration without changing artwork or presentation identity.

No switch mapping, physical port geometry values, connector, PoE, polling, telemetry, maximum-capability, support-status, Hub/Discovery/SNMP2MQTT runtime or privacy contracts change in Core 2.6.2.
