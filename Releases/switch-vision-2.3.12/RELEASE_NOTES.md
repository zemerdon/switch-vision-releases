# Switch Vision Core v2.3.12 — Persistent Calibration LED Test Mode

Switch Vision Core v2.3.12 makes Calibration LED Test Mode useful after the calibration editor is closed, so a completed faceplate can be inspected without the calibration workspace covering it.

## Test Mode remains active after Done

When **Test Mode** is enabled and **Done** is selected:

- calibration changes are saved normally
- the calibration editor closes normally
- Test Mode remains active
- Status, RJ45, and SFP/uplink LEDs remain forced into their calibration test state

Test Mode is now independent of whether the calibration controls are open. Closing the editor no longer silently disables the forced LED display.

## Visible TEST MODE reminder

While Test Mode remains active, a small **TEST MODE** indicator is displayed directly beneath the normal **Calibrate** button.

This provides a persistent visual reminder that the faceplate is showing forced calibration LED states rather than normal live LED presentation.

## Returning to Calibration

Opening Calibration again while Test Mode is active preserves the active Test Mode state.

The existing **Test Mode** control can be used to switch the mode off normally.

Choosing **Cancel** continues to close Calibration and explicitly turns Test Mode off, providing a clear reset path.

## Compatibility

This update does not change:

- saved calibration profile geometry
- faceplate assignments
- switch discovery
- physical-port mappings
- live telemetry values
- Activity LED thresholds or timing

The change is limited to Calibration Test Mode session behaviour and its visible status indicator.

## Upgrade note

Switch Vision Core v2.3.12 changes the Home Assistant custom integration card files and versioned frontend resources.

After updating Core through Switch Vision Installer, restart Home Assistant Core when prompted.
