# Switch Vision Core v2.3.11 — Calibration Profile Manager relocation

Switch Vision Core v2.3.11 cleans up the Switch Vision Core Hub by moving Calibration Profile management into the Switch Vision Discovery Hub.

## Core Hub cleanup

The Core Hub is once again focused on the native Switch Vision dashboard.

The temporary Dashboard / Calibration Profiles selector introduced in v2.3.10 has been removed.

Calibration Profiles are now managed from:

**Switch Vision Discovery Hub → Calibration Profiles**

This keeps switch discovery, setup, device management, and calibration-profile management together in one management interface.

## Calibration backend remains in Core

Only the Profile Manager frontend has moved.

Switch Vision Core continues to own the authoritative calibration storage and API.

The existing Core calibration interfaces remain available, including:

- calibration profile listing
- calibration profile retrieval
- save calibration
- delete calibration
- active-profile protection
- factory-profile protection
- stale and duplicate-faceplate metadata

Switch Vision Discovery v2.1.25 uses these existing Core interfaces rather than reading or modifying Home Assistant `.storage` files directly.

No calibration profiles are migrated, renamed, deleted, or recreated by this update.

## Existing v2.3.10 calibration tools remain

The v2.3.10 calibration features remain available, including:

- Calibration LED Test Mode
- Refresh Faceplate
- faceplate-aware calibration profile identity
- active and factory profile protection

## Upgrade note

Switch Vision Core v2.3.11 changes the Home Assistant custom integration files.

After updating Core through Switch Vision Installer, restart Home Assistant Core when prompted.

For Calibration Profile management, use Switch Vision Discovery v2.1.25 or later.
