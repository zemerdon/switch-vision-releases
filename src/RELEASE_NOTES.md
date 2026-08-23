# Switch Vision Core v2.5.0

Core 2.5.0 introduces the user-facing Core integration for the new Switch Vision Maintenance Hub.

The Native Switch Vision dashboard header now includes a configurable **Maintenance** shortcut when Discovery is installed. It opens the Discovery 2.2.0 Hub directly at its Maintenance page using the supported `?view=maintenance` route.

The MQTT scan, ownership validation, preview, confirmation and repair operations remain owned by Discovery. Core does not duplicate broker access or destructive cleanup logic; it only exposes the installation-aware navigation and preference contract.

A permanent Core regression verifies the new shortcut ID, default option, settings field, translation parity and exact Maintenance destination.

No switch mapping, port geometry, polling, telemetry, PoE, connector, hardware capability, support-status or privacy contracts change in Core 2.5.0.
