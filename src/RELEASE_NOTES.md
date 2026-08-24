# Switch Vision Core v2.5.1

Core 2.5.1 is a visual-default hotfix for the v2.5.0 Gold line.

Fresh/generated exact-model cards that do not yet have a persisted calibration profile now keep the complete exact-model factory UI defaults when Core reconciles them from the baked generic fallback. Previously the factory port geometry was selected correctly, but generic fallback logo/status/button placement could be copied over the model-specific factory UI.

When a real persisted calibration profile exists, Core continues to preserve the user's saved logo/status-panel/button placement, stack, management and faceplate choices while applying any required exact-model geometry reconciliation.

Permanent regression coverage locks the UCG Ultra and USW Ultra factory-default contract and the persisted-profile preservation gate.

No switch mapping, physical port geometry, connector type, PoE, polling, telemetry, maximum-capability, support-status, Discovery/UniFi2MQTT handoff or privacy contracts change in Core 2.5.1.
