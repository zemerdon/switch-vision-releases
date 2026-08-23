# Switch Vision Core v2.4.17

Core 2.4.17 fixes the Calibration faceplate selector so choosing **Default / recommended** reliably returns to the switch's independent base calibration profile.

Previously, the base-profile load followed the saved active custom-faceplate pointer, which could immediately restore the faceplate the user was trying to leave. The websocket contract now supports an exact base-profile read used only for an explicit Default selection; normal profile loads continue to follow the active faceplate as before.

This release changes the Switch Vision Home Assistant custom component and frontend card. It does not change switch mappings, hardware geometry, polling, telemetry, support status, or device capability data.
