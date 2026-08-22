# Switch Vision Core v2.4.13

Core 2.4.13 fixes two dashboard UI regressions observed on a community-validated Zyxel XS1930-10.

Rendered ports now remain selectable when a saved or custom calibration contains the port centre but omits an explicit hitbox. Switch Vision derives the normal visual hitbox for the rendered socket rather than allowing the click to fall through to the switch-summary background handler. Blank interface descriptions continue to display as `DESC —` while the port remains selected.

The native dashboard Advanced diagnostics block now uses an explicit light foreground on its fixed dark background, keeping diagnostic text readable under Home Assistant themes whose primary text colour is dark.

No device mapping, telemetry, faceplate geometry, Discovery, SNMP2MQTT, or UniFi2MQTT behaviour changes are included in this corrective release.
