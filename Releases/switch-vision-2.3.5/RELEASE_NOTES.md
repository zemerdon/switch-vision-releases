# Switch Vision Core v2.3.5 — Calibration selection highlight correctness

Switch Vision Core v2.3.5 focuses on making the Calibration workspace's yellow selection overlay accurately represent the target that is actually being edited.

The overlay now uses the same canonical editable-target resolution used by calibration movement, direct positioning, and sizing operations.

This corrects visual highlighting for:

- individual RJ45 port boxes
- Entire Port selections
- RJ45 link LEDs
- RJ45 activity LEDs
- RJ45 number labels
- All RJ45 groups
- Odd RJ45 groups
- Even RJ45 groups
- custom RJ45 groups
- SFP/uplink boxes
- SFP/uplink link LEDs
- SFP/uplink activity LEDs
- SFP/uplink labels
- combined Port Numbers
- individual and grouped status LEDs
- Status Box 1 fields, labels, and values
- Status Box 2 fields, labels, and values
- Logo
- Calibration button
- Status Box 1
- Status Box 2

The underlying calibration target-selection behaviour was not changed; this release aligns the yellow visual feedback with the target already being edited.

Status Box 1 and Status Box 2 also gain whole-box Visible controls in the Calibration workspace.

A targeted regression matrix covering 60 overlay selection cases passed before release.

Community testing and feedback remain welcome.
