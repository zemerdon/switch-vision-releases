# Switch Vision Core v2.4.19

Core 2.4.19 corrects the two UniFi small-switch faceplate image payloads introduced in v2.4.18. The canonical filenames and factory calibration geometry remain unchanged.

`UCG Ultra` continues to use `faceplates/unifi-5rj45.png` with `default_unifi_5_rj45`, and `USW Ultra` continues to use `faceplates/unifi-8rj45.png` with `default_unifi_8_rj45`. The shipped PNG files are replaced byte-for-byte with the authoritative staged artwork and are now permanently guarded by exact file-size, PNG-signature, and SHA-256 regressions.

No UniFi hardware contract, port mapping, connector type, PoE semantics, maximum-speed capability, telemetry, API ordering, calibration geometry, privacy metadata, or support status changes in this corrective release. Both models remain Experimental and rendered alignment still requires community confirmation.
