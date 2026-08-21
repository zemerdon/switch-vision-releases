# Switch Vision Core v2.4.4 — Central sidebar and Native dashboard shortcuts

- Centralizes all Switch Vision-managed sidebar visibility under Settings → Integrations → Switch Vision → Configure.
- Controls Native Switch Vision, Switch Vision Dashboard, Switch Vision Hub, and Switch Vision Installer from one Sidebar section.
- Shows absent sidebar-capable apps as read-only **Not installed** entries instead of silently omitting them.
- Adds a configurable Native dashboard shortcut header with per-shortcut enable/disable, installation-aware shortcuts, drag-to-reorder customization, and independent summary / Refresh / version controls.
- Uses Home Assistant Supervisor's supported ingress-panel API and current `/config/app/<slug>/config` app settings routes.
- Does not change switch telemetry, calibration geometry, supported-device mappings, Discovery generation, or Activity LED behavior.

After updating Core through Switch Vision Installer, restart Home Assistant Core when requested and hard-refresh the browser so the new integration options and Native panel JavaScript are loaded.
