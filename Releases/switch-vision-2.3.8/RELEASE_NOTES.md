# Switch Vision Core v2.3.8 — Streamlined calibration colour controls

Switch Vision Core v2.3.8 simplifies the Calibration interface by removing redundant preset colour dropdowns from the Status Box styling controls.

Status Box 1 and Status Box 2 now use the existing colour-picker controls directly for:

- text colour
- box/background colour
- border colour

The colour pickers already provide direct colour selection and therefore make the older preset dropdown menus unnecessary.

This is a Calibration UI cleanup only.

Existing calibration properties and saved-profile values are unchanged. Existing profiles continue to use the same text, label, title, background, and border colour settings.

The release does not change:

- colour storage keys
- saved-profile compatibility
- factory calibration values
- reset/default behaviour
- port or uplink mappings
- Discovery
- faceplate selection
- Activity LED calculations

Other Calibration dropdowns that perform non-colour selections, such as fonts, targets, assets, LED shapes, fields, stack settings, and movement steps, remain unchanged.
