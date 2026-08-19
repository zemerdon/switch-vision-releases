# Switch Vision Core v2.3.6 — Neutral stock visual profiles

Switch Vision Core v2.3.6 introduces neutral stock factory calibration profiles so supported switches no longer need to inherit calibration identities belonging to unrelated hardware models.

The bundled stock visual families are now represented by dedicated neutral profiles:

- `stock_24rj45_2sfp`
- `stock_24rj45_4sfp`
- `stock_48rj45_2sfp`
- `stock_48rj45_4sfp`

For models without a dedicated visual, Switch Vision selects the stock 24-port family for devices with 24 or fewer RJ45 ports and the stock 48-port family for devices with more than 24 RJ45 ports. The closest bundled two-SFP or four-SFP variant is selected from the modelled uplink count.

This corrects fallback visual selection for SG500X-24, Huawei S5720/S5735, Zyxel XS1930-10, and generic-fallback UniFi models.

The dedicated Cisco Catalyst 3560-C profile and `c3560cg-8pc-s.png` faceplate are now reserved exclusively for the exact `WS-C3560CG-8PC-S` model. Existing model-specific Cisco Catalyst profiles and the validated Juniper EX3300 visual remain unchanged.

Physical discovered port counts and vendor-specific physical-port mappings are not changed by this release.

## Important upgrade note

Switch Vision preserves existing saved calibration profiles during an update.

If an affected existing switch continues to display its previous fallback faceplate or geometry after updating to v2.3.6:

1. Open **Switch Vision Calibration** for that switch.
2. Select **Reset Current Switch**.
3. Confirm the reset.

**Reset Current Switch removes the saved faceplate-specific calibration for that switch and replaces it with the current recommended factory visual and calibration profile. The replacement is saved automatically.**

This also replaces custom calibration positions, sizing, faceplate selection, and other saved calibration adjustments for that switch. Record any custom adjustments you want to recreate before resetting.

New switches, and existing switches without a saved calibration profile, use the corrected factory visual automatically.

Build-time validation also prevents the dedicated 3560CG profile or faceplate from being assigned to another model.
