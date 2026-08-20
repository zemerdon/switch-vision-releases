# Switch Vision Core v2.3.16 — No-overlap Test Mode placement

- Keeps Calibrate exactly where the profile places it.
- Measures the actual rendered Calibrate and TEST MODE controls in the browser.
- Prefers a true 30 px edge-to-edge gap below Calibrate.
- Falls back above, then left or right when the preferred position does not fit.
- Recalculates after faceplate image load and when the rendered faceplate resizes.
- Guarantees TEST MODE will not overlap Calibrate; in an impossibly small stage it hides the faceplate badge rather than overlap the control.
- Keeps all existing Test Mode persistence behaviour unchanged.

After updating Core through Switch Vision Installer, restart Home Assistant Core when prompted.
