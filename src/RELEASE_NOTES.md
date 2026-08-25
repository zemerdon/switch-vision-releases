# Switch Vision Core v2.6.1

Core 2.6.1 adds the authenticated settings contract used by the Switch Vision Hub. The Hub can now read and save every normal Core option without creating a second settings store: Home Assistant's existing Switch Vision config-entry options remain authoritative.

The grouped contract covers sidebar/navigation visibility, Native dashboard header controls and shortcut order, dashboard presentation, Activity LED sensitivity/threshold/timing controls, Discovery appearance and Installer appearance. Hub writes are admin-only, reject unknown settings, enforce the existing allowed values/ranges and Activity LED ordering rules, and preserve unrelated saved options.

Home Assistant **Integrations → Switch Vision → Configure** remains available as a synchronized fallback/recovery surface. This Core release provides the backend contract; the matching Hub release provides the user-facing settings page and Save workflow.

No switch mapping, port geometry, connector, PoE, polling, telemetry, maximum-capability, support-status, SNMP2MQTT/Discovery runtime or privacy contracts change in Core 2.6.1.
