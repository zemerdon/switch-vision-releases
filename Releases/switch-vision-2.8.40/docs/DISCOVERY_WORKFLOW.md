# Discovery workflow

Switch Vision Discovery performs read-only SNMP collection, identifies exact models and interfaces, generates configuration, and updates the native dashboard workflow.

## Persistent Web UI

Discovery starts in **Idle / Ready** and keeps the Web UI online. A run begins only when **Run Discovery** is selected. Duplicate runs are blocked.

## Main pages

- **Discovery** — guided run status and Debug output
- **Devices** — compact per-device results
- **Support My Switch** — privacy-processed contribution packages
- **Diagnostics** — installation, registry, file, and device checks
- **Configuration** — portable export and validated import of Discovery settings

The home page also provides dynamic links to related Switch Vision components when they are installed.

## Normal workflow

1. Validate configured switch rows.
2. Run targeted or full SNMP walks.
3. Identify exact models, interfaces, stacks, PoE, environmental data, and capabilities.
4. Match the exact-model supported-device registry.
5. Generate SNMP2MQTT YAML when SNMP data is active.
6. Generate dashboard card YAML from the active SNMP and/or UniFi API sources.
7. Validate newly generated SNMP2MQTT YAML when present.
8. Start/restart SNMP2MQTT when SNMP output is active, or stop the generated-YAML bridge when Discovery retires it.
9. Make the generated cards available to the native Switch Vision panel.

## Guided stage labels

```text
1. Validating configured switches
2. Running SNMP walks
3. Identifying exact models and interfaces
4. Generating SNMP2MQTT YAML
5. Generating dashboard card YAML
6. Complete
```

## Minimal and Debug views

Minimal mode shows the current stage, switch name, target, masked command, action, status, and elapsed time. It does not stream every returned OID.

**Show Debug** displays command execution, walk progress, parser activity, registry lookups, generated paths, warnings, return codes, and Supervisor responses. SNMP communities remain masked.

## Polling behaviour

The Web UI:

- polls every second while Discovery or Support My Switch is active;
- polls every five seconds while idle;
- pauses while the tab is hidden;
- refreshes immediately when the tab becomes visible or focused;
- advances the displayed elapsed timer locally every second during an active run.

## Switch identity and model selection

Every switch row defaults to:

```text
Switch Model: Auto-detect
```

Discovery retains the exact detected model. A registered model can be selected as an experimental compatibility override; reports then preserve the detected model, selected override, and effective mapping model.

A recognised exact model receives its registered mapping, calibration profile, and recommended visible faceplate automatically. There is no separate Apply Recommended action.

An unknown model receives a visible generic fallback and can be calibrated or assigned a custom faceplate. User-saved custom topology remains authoritative until the user resets the switch or chooses to adopt a later registered profile.

## SNMP source isolation

Discovery uses only SNMP walk files created by the current run. Historical walk files are ignored unless `parse_all_walks` is explicitly enabled for an offline/stored-walk import. This prevents deleted or disabled SNMP targets from returning through old files. The capability cache is rebuilt from the selected source set on every run.

UniFi2MQTT is an independent source. A run with no active SNMP source can still generate a fresh `generated-dashboard-card.yaml` containing only normalized UniFi API devices.

The Discovery page also provides **Reset SNMP Discovery Data**. It stops Switch Vision SNMP2MQTT, retires identifiable retained Home Assistant MQTT Discovery entries using the exact generated topic names Switch Vision recorded (no credentials), clears saved SNMP walks/capabilities/generated SNMP files, and leaves `/share/switch_vision/unifi/` plus UniFi2MQTT settings untouched. Run Discovery after the reset to rebuild the card from the currently enabled sources.

## Persistent walk folders

Each target uses a stable directory based on **Switch Name (Used internally only)**:

```text
/share/switch_vision/snmpwalks/<switch_name>/
```

Display names do not control folder names.

## Generated output

| Output | Purpose |
|---|---|
| `snmpwalk.log` | Walk commands, timing, warnings, and results. |
| `discovery-report.txt` | Human-readable hardware, registry, and capability report. |
| `last-discovery-run.txt` | Short latest-run summary. |
| `generated-snmp2mqtt.yaml` | Authoritative telemetry configuration imported by Switch Vision SNMP2MQTT. |
| `generated-dashboard-card.yaml` | Source for the native panel and manual Lovelace fallback. |
| `capabilities/*-capabilities.json` | Normalised per-switch capability and registry data. |

## SNMP2MQTT handoff

Discovery attempts the handoff only when the current run created a new valid `generated-snmp2mqtt.yaml`.

It then:

1. locates the installed Switch Vision SNMP2MQTT app dynamically;
2. restarts it when running;
3. starts it when stopped;
4. reports the result in normal and Debug status.

A missing app, unavailable Supervisor token, or failed Supervisor request produces a warning without changing the successful Discovery result.

## Automatic dashboard update

The native panel reads `generated-dashboard-card.yaml` through the custom integration. While visible, it checks for a newer source file and also responds to the panel Refresh action and browser focus changes.

Replacement cards are built before the visible dashboard is swapped. A failed refresh leaves the existing cards active rather than blanking the panel.

## Export and import

Use **Discovery → Configuration → Export Configuration** to create a portable JSON backup of the switch list, stack-member mappings, and Discovery settings. Store it securely because it may contain management addresses and SNMP community strings.

On a fresh installation, use **Import Configuration** before editing app options manually. The import creates `/data/options.before-import.json` and preserves current Support My Switch privacy and recognition settings.

## New-device support

Use Support My Switch for unknown models or incomplete mappings. Evidence can establish Detected or Experimental support, but real-hardware testing is required before promotion.

Confirmed support applies only to the exact SKUs listed in `SUPPORTED_DEVICES.md`. The registered Cisco 2960X 24-port and Cisco 3560-C models remain Experimental pending their own model-specific validation.
