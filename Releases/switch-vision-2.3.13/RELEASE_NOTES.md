# Switch Vision Core v2.3.13 — Bottom-right Calibration controls

Switch Vision Core v2.3.13 polishes the persistent Calibration LED Test Mode controls introduced in v2.3.12.

## Cleaner bottom-right placement

The stock **Calibrate** control now sits in the lower-right faceplate control area instead of covering the upper-right screw/hardware detail.

When Calibration LED Test Mode is active, **TEST MODE** is displayed directly beneath Calibrate as a full-size matching control.

The two controls now form a clean vertical stack:

- Calibrate: 138 × 34
- TEST MODE: 138 × 34
- 4 px spacing between the controls

Existing profiles that still use the previous stock Calibrate coordinates are automatically moved to the new stock position. Profiles with genuinely customised Calibrate coordinates are left unchanged.

## Behaviour unchanged

This release does not change Test Mode logic introduced in v2.3.12:

- Done saves and closes Calibration while Test Mode remains active
- reopening Calibration preserves Test Mode
- Cancel closes Calibration and turns Test Mode off
- forced Status, RJ45, and SFP/uplink LED states remain unchanged

No Discovery, physical-port mapping, faceplate assignment, telemetry, calibration geometry, or Activity LED tuning behaviour is changed.

## Upgrade note

Switch Vision Core v2.3.13 changes the Home Assistant custom integration/card files and versioned frontend resources.

After updating Core through Switch Vision Installer, restart Home Assistant Core when prompted.
