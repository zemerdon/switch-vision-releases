# Switch Vision Core v2.2.2 — C3650 Status Box emergency hotfix

Switch Vision Core v2.2.2 fixes a factory-profile coordinate regression affecting Cisco 3650 Status Box rendering. After a factory calibration reset, the saved value-column offsets for MODEL, IP, CPU, TEMP, and POE could resolve beyond the right edge of Status Box 1, causing the renderer's safety guard to hide those rows while UPTIME remained visible.

The same stale coordinate pattern is corrected in the legacy C3650 profile and Status Box 2. A new build-time bounds validator now replays the frontend status-row positioning rules across every bundled factory calibration and faceplate profile and rejects any release where an enabled factory status row would render outside its panel.

No SNMP, Discovery, Activity LED 2.0, or enable/disable behaviour is changed by this hotfix.
