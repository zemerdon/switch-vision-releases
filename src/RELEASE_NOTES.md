# Switch Vision Core v2.4.3 — Huawei faceplate reset hotfix

- Restores `S5720-12TP-LI-AC` and `S5735-L8P4X-A1` to the neutral `stock_24rj45_4sfp` factory calibration profile.
- Restores `faceplates/24rj45-4sfp.png` as the matching default/recommended faceplate for both Huawei 8 RJ45 + 4 SFP models.
- Fixes Reset Current Faceplate/model-aware reset falling back to Cisco 48-port factory geometry and moving LEDs away from shipped card defaults.
- Adds a permanent regression so these exact Huawei models cannot silently return to `default_cisco_48_port`.
- Preserves physical mappings, S5720 1G SFP speed safeguards, telemetry, Activity LEDs and TEST MODE behavior.

After updating Core through Switch Vision Installer, restart Home Assistant Core when requested and hard-refresh the browser. Existing saved custom calibrations remain preserved until the user chooses a reset.
