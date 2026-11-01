# Upgrading Switch Vision

Use one complete release as the source of truth. Do not merge individual files from different versions.

## Recommended: Switch Vision Installer

The Switch Vision Installer is the preferred upgrade path. It validates the public release, creates a recovery backup, and replaces only the required main Switch Vision component/dashboard files.

Discovery, SNMP2MQTT, and optional UniFi2MQTT are repository-managed apps with independent versions. The Installer registers/updates them through Home Assistant Supervisor rather than copying app source from the main release ZIP.

After the Installer completes:

1. confirm the installed Switch Vision version;
2. confirm Discovery/SNMP2MQTT app health;
3. restart Home Assistant Core if requested;
4. restart Discovery or SNMP2MQTT when the Installer explicitly requests it;
5. hard-refresh the browser;
6. run Discovery once when the supported-device registry or generated configuration changed.

## Manual upgrade matrix

| Changed component | Required action |
|---|---|
| `custom_components/switch_vision/` | Replace the complete folder and restart Home Assistant Core. |
| `www/switch-vision/` assets | Replace the complete folder, restore custom assets, then hard-refresh the browser. |
| Main supported-device registry / visual mappings | Replace the release files and run Discovery when new generated output is required. |
| Discovery/SNMP2MQTT/UniFi2MQTT app | Update the repository-managed app through Home Assistant/Installer; do not copy a main-release `local_apps/` folder. |
| Documentation only | No Home Assistant runtime action is required. |

## Preserve before replacing files

Back up custom files from:

```text
/config/www/switch-vision/faceplates/
/config/www/switch-vision/logos/
```

Do not delete during a normal upgrade:

```text
/share/switch_vision/
/config/.storage/switch_vision_calibrations
```

`/share/switch_vision/` contains generated YAML, walks, reports, configuration exports, diagnostics, contributions, and normalized UniFi snapshots. `.storage/switch_vision_calibrations` contains saved calibration profiles.

## Manual main-runtime upgrade

1. Back up custom faceplates and logos.
2. Replace `/config/custom_components/switch_vision/` with the release copy.
3. Replace `/config/www/switch-vision/` with the release assets.
4. Restore custom faceplates and logos.
5. Restart Home Assistant Core.
6. Hard-refresh the browser or test in an Incognito window.
7. Update repository-managed supporting apps independently if Home Assistant shows an update.
8. Run Discovery once when mappings, examples, or the supported-device registry changed.

## Verification

Confirm:

- the native panel shows the expected main Switch Vision version;
- Discovery is installed from its repository and reports its own expected version;
- existing switches retain their faceplates and saved geometry;
- Reset Current Switch restores the correct model-specific topology;
- Reset All Switches restores each model independently;
- generated SNMP2MQTT and dashboard YAML exist;
- custom/manual dashboards load the versioned Switch Vision card resource.


## Faceplate defaults updated in v2.4.0

Existing saved/custom faceplate calibrations are preserved during upgrade. To use the new v2.4.0 built-in defaults on an existing switch, open **Calibration** and choose **Reset Current Faceplate** to reload the current bundled/model default.

Updated defaults:

- **UniFi / Ubiquiti models** now default to `unifi-24p-rj45-2sfp.png`.
- **Stock 24 RJ45 / 4 SFP** calibration defaults were updated.
- **Stock 24 RJ45 / 2 SFP** calibration defaults were updated.

## Rollback

Keep the previous installable and private source ZIPs until the new version has passed normal-use testing.

To roll back the main runtime manually, replace the custom component and dashboard assets from one complete earlier release, then restart Home Assistant Core. Supporting apps remain independently versioned and should only be rolled back through their own repository/app mechanism. Do not delete `/share/switch_vision/` or saved calibration storage unless a release explicitly requires a data reset.
