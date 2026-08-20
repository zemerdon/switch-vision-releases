# Switch Vision Core v2.4.1 — Discovery model promotion

- Promotes all 11 exact models currently known by Discovery but missing from Core into the Core supported-device index.
- Promoted models: `N2128PX-ON`, `US 48 PoE 500W`, `US 8 60W`, `USW Flex`, `USW Flex 2.5G 8 PoE`, `USW Flex Mini`, `USW Pro 24`, `USW-16-PoE`, `USW-24-PoE`, `USW-Lite-8-PoE`, `UniFi Dream Machine PRO SE`.
- Preserves each model's existing Discovery support status, validation evidence, port geometry, mapping profile and visual recommendation; Experimental models remain Experimental.
- Makes explicit per-model registry visuals authoritative instead of forcing every Ubiquiti model into one 24-port faceplate family.
- Keeps the dedicated v2.4.0 UniFi 24 RJ45 / 2 SFP faceplate for the exact models that currently recommend it, while preserving Discovery's existing stock/model geometry for other UniFi hardware.
- Does not change SNMP/UniFi telemetry protocols, MQTT topics, saved calibrations, or TEST MODE behaviour.

After updating Core through Switch Vision Installer, restart Home Assistant Core when prompted and hard-refresh the browser.
