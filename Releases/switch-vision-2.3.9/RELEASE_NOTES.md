# Switch Vision Core v2.3.9 — Quick Selection populates Custom Ports

Switch Vision Core v2.3.9 improves the Calibration Quick Selection workflow.

When an RJ45 Quick Selection resolves to a normal set of visual ports, the resolved port list is now also populated into the Custom Ports field.

This applies to:

- All RJ45
- RJ45 Link
- RJ45 Activity
- Odd ports
- Odd link LEDs
- Odd activity LEDs
- Odd numbers
- Even ports
- Even link LEDs
- Even activity LEDs
- Even numbers

The populated Custom Ports value contains only ports that actually exist in the active calibration profile.

The original Quick Selection remains active. Populating Custom Ports simply makes the resolved selection visible and provides an editable starting point for further calibration work.

Quick selections that do not resolve to normal RJ45 ports do not modify the Custom Ports field.

This release does not change port mappings, SFP/uplink mappings, Discovery, device profiles, faceplate assignments, calibration storage keys, saved-profile compatibility, or Activity LED behaviour.
