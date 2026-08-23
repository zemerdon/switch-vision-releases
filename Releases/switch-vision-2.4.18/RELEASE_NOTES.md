# Switch Vision Core v2.4.18

Core 2.4.18 adds dedicated small-device UniFi faceplates and factory calibration geometry for the existing `UCG Ultra` and `USW Ultra` exact-model contracts.

`UCG Ultra` now uses the new five-RJ45 UniFi faceplate with its calibrated five-port geometry. `USW Ultra` now uses the new eight-RJ45 UniFi faceplate with its calibrated eight-port geometry. Their verified API/hardware contracts remain unchanged: the UCG Ultra retains four 1G RJ45 ports plus one 2.5G-capable RJ45 port with no PoE output, while the USW Ultra retains eight 1G RJ45 ports with PoE output capability on ports 1–7 only.

Both models remain Experimental. The new artwork and geometry are now the exact-model defaults, but rendered alignment on the contributed real hardware still requires community confirmation before any support-status promotion.

This release changes the Switch Vision Home Assistant custom component/frontend card because the new factory calibrations are embedded into the generated card source. It does not change UniFi polling, telemetry, API port ordering, maximum-speed contracts, PoE semantics, or per-port traffic availability.
