# Contributing to Switch Vision

Contributions are welcome in two main forms: real-hardware evidence and source-code improvements.

## New switch models and hardware validation

Use **Switch Vision Discovery → Support My Switch**. This workflow collects the evidence needed to identify a device, review interface mappings, generate an experimental profile, and validate existing support.

Before sharing a bundle:

- enable the privacy masks appropriate for the installation;
- review the generated ZIP and reports;
- do not share a bundle marked **REVIEW REQUIRED** until the reason is understood;
- describe what works, what is incorrect, and any unusual stack or uplink behaviour.

Nothing is sent automatically. Clean contributions can be prepared for:

```text
switch-vision@zemerdon.com
```

## Code changes

Keep pull requests focused and describe:

- the problem being solved;
- the affected Switch Vision component;
- how the change was tested;
- expected behaviour before and after the change;
- any Home Assistant restart, Discovery rebuild, or migration requirement.

Do not mix unrelated feature work with storage, calibration, Discovery, or packaging fixes.

## Source requirements

- Use LF line endings.
- Do not commit `__pycache__`, `.pyc`, `.pyo`, `.pytest_cache`, temporary files, PSD files, or built source archives.
- Keep `src/js/switch-vision.js` and `src/custom_components/switch_vision/switch-vision-card.js` synchronised through the build process.
- Preserve historical changelog entries; only add a new entry at the top.
- Update current documentation when behaviour changes.
- Build an exact version with `python3 build.py -v <version>`.

## Hardware support status

A contribution does not automatically make a model Confirmed. Switch Vision uses the progression:

1. Detected
2. Experimental
3. Community Validated
4. Confirmed Supported

Validation may be recorded separately for exact-model detection, RJ45 mapping, PoE, system sensors, uplinks, and stack behaviour.
