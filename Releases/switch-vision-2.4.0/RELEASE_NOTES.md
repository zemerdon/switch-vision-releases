# Switch Vision Core v2.4.0 — UniFi faceplates and refreshed 24-port defaults

- Adds the dedicated `unifi-24p-rj45-2sfp.png` faceplate and matching factory calibration baseline.
- Makes the UniFi faceplate the shipped default artwork for all current UniFi / Ubiquiti model mappings.
- Updates the factory calibration defaults for Stock 24 RJ45 / 2 SFP.
- Updates the factory calibration defaults for Stock 24 RJ45 / 4 SFP.
- Preserves existing saved/custom faceplate calibrations during upgrade.
- Existing switches that should adopt the new v2.4.0 defaults can open Calibration and reset/reload the faceplate to its current default.
- Keeps the v2.3.16 browser-geometry TEST MODE no-overlap behaviour unchanged.

After updating Core through Switch Vision Installer, restart Home Assistant Core when prompted and hard-refresh the browser.
