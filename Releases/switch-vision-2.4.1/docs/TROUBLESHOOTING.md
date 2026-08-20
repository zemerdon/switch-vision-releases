# Troubleshooting

## Switch Vision sidebar entry is missing

The custom-component directory must be exactly:

```text
/config/custom_components/switch_vision/
```

Files such as `__init__.py`, `manifest.json`, and `config_flow.py` must be directly inside it.

Then:

1. confirm Switch Vision appears under **Settings → Devices & services**;
2. restart Home Assistant Core;
3. open **Switch Vision → Configure**;
4. confirm **Show automatic Native Switch Vision panel in sidebar** is enabled;
5. hard-refresh or test in an Incognito window.

New installations do not require `switch_vision:` in `configuration.yaml`.

## The panel or card still shows an older version

The panel shell and card module use the main Switch Vision version; the separately versioned Discovery app can legitimately report a different version.

1. Replace the complete current-release custom component.
2. Replace `/config/www/switch-vision/`.
3. Restart Home Assistant Core.
4. Hard-refresh or clear browser site data.
5. Confirm the panel header version.

For Discovery, use the repository-managed app update shown by Home Assistant/Installer. Do not replace Discovery files from the main Switch Vision ZIP. Confirm the independent Discovery version in Discovery Diagnostics or a new Support My Switch contribution.

## Generated dashboard does not update

Check that:

- Discovery completed successfully;
- `/share/switch_vision/generated-dashboard-card.yaml` exists and has a newer modified time;
- the panel header shows the expected generation time;
- the browser tab is visible;
- **Refresh** performs an immediate check.

Current releases keep existing cards visible if a refresh fails. A failure message should state that the existing dashboard remains active.

## Duplicate calibration updates or progressive slowdown

Current cards unsubscribe from calibration events when removed from the page. If duplicate updates remain:

1. confirm the panel and card are on the current release;
2. close duplicate browser tabs;
3. hard-refresh;
4. navigate away and back;
5. capture browser console errors if the problem returns.

## Discovery Web UI only updates after refresh

Confirm the repository-managed Discovery app is on its current published version rather than assuming it matches the main Switch Vision version.

Expected behaviour:

- one-second polling while active;
- five-second polling while idle;
- pause while the tab is hidden;
- immediate update when returning to the tab;
- elapsed time visibly ticking every second.

## Old SNMP devices still appear after switching to UniFi API only

Current releases do not reuse stored SNMP walks unless `parse_all_walks` is explicitly enabled. Open **Switch Vision Hub → Discovery → SNMP cleanup** and select **Reset SNMP Discovery Data**, then run Discovery again. The reset preserves UniFi API data/settings while clearing saved SNMP walks, capability caches, generated SNMP files, the mixed generated card, and identifiable retained SNMP2MQTT Home Assistant discovery entries.

If retained MQTT cleanup reports a warning, verify the MQTT integration and Switch Vision SNMP2MQTT app are available, then use the normal Home Assistant MQTT tooling to remove any remaining retired discovery topics.

## SNMP2MQTT did not start or restart

Open Discovery Debug output and check the final handoff result.

Common causes:

- generated YAML was not updated by the current run;
- YAML validation failed;
- Switch Vision SNMP2MQTT is not installed;
- generated-YAML import is disabled;
- the installed Discovery repository version or Supervisor permissions are stale;
- Supervisor authorization is unavailable.

The Discovery app configuration must include:

```yaml
hassio_api: true
hassio_role: manager
```

A handoff warning does not invalidate otherwise successful Discovery output.

## Discovery cannot start after an upgrade

Older switch rows may lack `switch_model`. Current releases resolve missing or blank values to **Auto-detect**.

If Home Assistant reports an option error, open the app configuration, save each row with **Auto-detect**, then update/reinstall the repository-managed Discovery app if Home Assistant offers a newer build.

## Discovery reports a switch timeout

Default timing is:

```text
Timeout: 3 seconds
Retries: 1
```

Verify the switch address, UDP/161 reachability, read-only SNMP community, ACLs, and routing between Home Assistant and the switch.

## A recognised model shows the wrong port or uplink count

1. Confirm Discovery detected the exact SKU shown in `SUPPORTED_DEVICES.md`.
2. Confirm the panel/card module is current.
3. Use **Reset Current Switch** and check the model-specific default.
4. Use **Reset All Switches** only when every saved calibration should be removed.
5. Refresh and restart Home Assistant to verify persistence.

Reset All should restore each loaded switch independently. A Cisco 2960S/2960X 48-port profile must not become a generic 48-port/4-uplink layout, and a 24-port 2960X must remain 24-port/4-uplink.

## Custom ports reappear after saving

A successfully saved profile is authoritative, including deliberately added or removed visual ports. Confirm:

- the footer reports the expected saved profile;
- **Done** completed without validation errors;
- the card is loading the same stable switch profile;
- the browser is not using an older card module.

Do not use Reset Current Switch or Reset All when the custom topology should be retained.

## Rectangle LED resizing changes the port box

Current releases store Link/Speed and Activity rectangle dimensions separately from the RJ45 hitbox.

Confirm the current card version, select the LED part rather than Port Box, and verify the footer W/H values. Older frontend code can make the W/H buttons target the port hitbox, so hard-refresh after upgrading.

## A custom faceplate is blank or missing

A faceplate cannot be hidden. Missing, invalid, blank, or legacy `__none__` selections should fall back to the model-recommended visible artwork.

Check:

- the custom file exists in `/config/www/switch-vision/faceplates/`;
- the filename contains no path traversal or unsupported characters;
- the asset list was refreshed;
- the browser cache was refreshed.

Keep filenames stable because changing the filename creates a new faceplate-specific profile namespace.

## Calibration import is rejected

The validation message identifies the unsafe value. Common causes include:

- width or height is zero/negative;
- a coordinate is non-finite or far outside the canvas;
- the profile name contains `/` or another unsafe character;
- an asset path contains directories or traversal;
- the payload exceeds the size limit;
- the element count is unreasonable.

A rejected import does not replace the active profile.

## Simultaneous saves lose a different switch's changes

Current releases serialize calibration storage transactions. Confirm both browser sessions use the current frontend and integration versions. Save different changes to two switches, refresh, and restart Home Assistant. Both should survive.

If the issue returns, capture the profile names and timestamps from both sessions without deleting `.storage/switch_vision_calibrations`.

## Support My Switch reports REVIEW REQUIRED

Open the generated `BUNDLE_QUALITY.txt` and `SANITIZATION_REPORT.txt`.

A bundle is blocked when a file is unsupported, oversized, unreadable, unwritable, a symbolic link, or another special file. The file is excluded from the temporary archive and represented by a privacy-safe identifier.

Remove or correct the source file under `/share/switch_vision/`, create a new contribution, and confirm the result returns to PASS or PASS WITH PRIVACY WARNINGS. Do not share a blocked bundle without review.

## Manual dashboard shows Configuration error

The native panel does not require Layout Card. For a generated manual layout:

1. open **Settings → Dashboards → Resources**;
2. remove stale or duplicate Layout Card resources;
3. register `/hacsfiles/lovelace-layout-card/layout-card.js` as a JavaScript Module;
4. register the current versioned Switch Vision card resource;
5. reload the browser.

## Sensors were not created

- Confirm `generated-snmp2mqtt.yaml` contains the expected target and sensors.
- Confirm SNMP2MQTT imports that generated file.
- Check the Discovery handoff result.
- Check SNMP2MQTT logs for YAML, OID, MQTT, or connection errors.
- Confirm the sensor prefix matches the dashboard card.

A later poll cannot create an entity that is absent from the generated configuration.

## Identity fields show a dash

Model, serial, and system description are generated only when the required OIDs are present in the walk evidence. Missing optional identity data displays as `—` without breaking the card.

## PoE shows an incorrect budget

Switch Vision normalises platform-specific PoE units. Generate a fresh targeted walk and confirm the standard POWER-ETHERNET-MIB branch is present.

## Home Assistant reports blocking filesystem calls

Current asset directory creation and scanning are executed outside the Home Assistant event loop. Confirm the integration is current. If a blocking warning remains, capture the complete traceback and submit it with a Support My Switch package.


### Two Switch Vision sidebar entries

- **Show automatic Native Switch Vision panel in sidebar** controls the original `/switch-vision` panel.
- **Show Switch Vision Lovelace dashboard in sidebar** controls dashboards created from the Switch Vision Community dashboard strategy.

The Lovelace dashboard is identified by its saved strategy, not by its title or URL.
