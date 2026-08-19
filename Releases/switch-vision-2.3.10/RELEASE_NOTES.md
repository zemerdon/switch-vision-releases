# Switch Vision Core v2.3.10 — Calibration profile management and test tools

Switch Vision Core v2.3.10 expands the Calibration workflow with safer profile management, easier LED positioning, and a proper faceplate refresh path.

## Calibration LED Test Mode

Calibration now includes a transient LED Test Mode.

While enabled, calibratable Status, RJ45 link/activity, and SFP/uplink link/activity LEDs are shown continuously lit so their positions are easy to see and adjust.

Test Mode is calibration-only and does not change live switch state, saved calibration data, or the calibration dirty state.

## Calibration Profile Manager

The Switch Vision Hub now includes a dedicated Calibration Profiles view.

Profiles show their scope, active state, model, RJ45 and SFP/uplink counts, faceplate identity, stale state, and faceplate SHA-256 fingerprint information.

The manager can identify:

- active and unused profiles
- missing-faceplate/stale profiles
- identical faceplate image content stored under different filenames
- factory profiles that must remain protected

Active and factory profiles are protected from deletion in both the frontend and backend.

The Hub also provides:

- Select Stale
- Clean Stale Profiles
- multi-select deletion
- individual deletion
- Copy Profile
- Export Profile
- Import Into Profile

Copy and Import preserve the destination profile identity and faceplate rather than allowing source data to silently redirect the destination.

Import also preserves destination management and stack data and rejects incompatible model transfers.

No duplicate or stale profile is automatically merged or deleted.

## Refresh Faceplate

Calibration now includes Refresh Faceplate.

If a faceplate PNG is replaced while keeping the same filename, Refresh Faceplate adds a temporary runtime cache-buster and reloads the current image bytes.

This avoids the previous workaround of renaming a faceplate file merely to bypass browser caching.

Refresh Faceplate does not:

- change the faceplate filename
- change the calibration profile key
- mark Calibration dirty
- save a profile
- change the active-profile pointer

## Upgrade note

Switch Vision Core v2.3.10 changes the Home Assistant custom integration files.

After updating Core through Switch Vision Installer, restart Home Assistant Core when prompted.
