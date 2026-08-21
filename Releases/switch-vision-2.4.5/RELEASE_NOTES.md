# Switch Vision Core v2.4.5 — Native dashboard shortcut editor hotfix

- Fixes **Switch Vision Settings** and other Native dashboard shortcuts so they navigate through Home Assistant's supported SPA navigation contract.
- Detects repository-installed Switch Vision apps by their real Supervisor slug, including repository prefixes.
- Uses the real installed app slug for Hub, Installer, and app Configuration destinations.
- Replaces drag-and-drop customization with a clear checkbox + Up/Down shortcut editor.
- Customize changes are staged until **Done**; **Cancel** discards them.
- Customize is shown only to Home Assistant administrators.
- Does not change switch telemetry, calibration geometry, Discovery generation, supported-device mappings, or Activity LED behavior.

After updating Core through Switch Vision Installer, restart Home Assistant Core when requested and hard-refresh the browser so the new integration and Native panel JavaScript are loaded.
