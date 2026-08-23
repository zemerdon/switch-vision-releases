# Switch Vision Core v2.4.15

Core 2.4.15 makes the dashboard status panels data-source aware for UniFi API devices.

The main UniFi switch summary now prioritizes telemetry the official Integration API actually provides: model, management IP when supplied by UniFi2MQTT 2.0.49 or newer, CPU, memory, uptime, real PoE capability/active-port summary where applicable, and live aggregate uplink RX/TX rate where PoE is not available.

Selected UniFi ports now show negotiated link speed, maximum physical capability, connector/media type, and real PoE state/standard when the API provides it. Switch Vision no longer wastes the default UniFi port panel on VLAN, description, or per-port RX/TX rows that the current Integration API path cannot populate. Temperature and per-port traffic remain absent rather than being synthesized.

SNMP-backed cards keep their existing status-panel behavior unchanged. Explicit card-level status-field configuration is respected, and `unifi_native_status_fields: false` restores the generic field-selection path for UniFi cards.
