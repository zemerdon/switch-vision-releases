# Field reference

## Switch Vision integration options

Open **Settings → Devices & services → Switch Vision → Configure**.

| Option | Default | Behaviour |
|---|---:|---|
| `show_panel_in_sidebar` — Show automatic Native Switch Vision panel in sidebar | On | Shows or hides the original automatic Native Switch Vision panel. The panel remains available at `/switch-vision` when hidden. |
| `show_lovelace_dashboard_in_sidebar` — Show Switch Vision Lovelace dashboard in sidebar | On | Shows or hides user-created dashboards that use the Switch Vision Community dashboard strategy. This is independent of the automatic Native panel. |
| `show_calibration_buttons` — Show calibration buttons on switch cards | On | Shows or hides the on-card Calibration button in the automatic native dashboard. Manual YAML cards remain controlled by their own `calibration_button` setting. |
| `show_dashboard_header` | On | Shows or hides the generated dashboard header. |
| `show_card_headers` | On | Shows or hides generated card headers. |
| `discovery_ui_density`, `discovery_text_size`, `discovery_content_width` | Comfortable / Normal / Standard | Controls the Switch Vision Hub/Discovery presentation. |
| `installer_ui_density`, `installer_text_size`, `installer_content_width` | Comfortable / Normal / Standard | Controls the Switch Vision Installer presentation. |

### Hub / Discovery management theme

The top-right **Theme** selector is a browser-local management UI preference. It is intentionally separate from dashboard/card presentation and offers:

- **Switch Vision** — current dark Switch Vision appearance and the default.
- **Cisco Classic** — graphite/steel management palette inspired by classic Cisco switching hardware.
- **Cisco Nexus** — dark data-centre management palette inspired by Nexus hardware.
- **UniFi** — clean light/aluminium/blue management palette inspired by UniFi hardware.

The selector affects only the Switch Vision Hub and its Discovery, Devices, Diagnostics, Support My Switch, Configuration, and UniFi2MQTT Settings views. It does **not** affect Native, Lovelace, or Custom Switch Vision dashboards, switch cards, faceplates, LEDs, port rendering, or Calibration visuals.

Discovery UI Density remains controlled by the existing `discovery_ui_density` integration option; the Hub no longer duplicates that control in its top bar.

## Discovery app fields

### Core paths

| Field | What it does |
|---|---|
| `input_path` | Fallback path to one SNMP walk file when structured switch folders are not used. |
| `snmpwalks_dir` | Root directory containing per-switch walk folders. |
| `report_path` | Main human-readable Discovery report. |
| `last_run_summary_path` | Short latest-run summary. |
| `generated_yaml_path` | Generated SNMP2MQTT YAML imported by the separate SNMP2MQTT app. |
| `generated_card_path` | Generated card YAML consumed by the native panel and retained for manual use. |
| `snmp_log_path` | SNMP walk command, timing, and result log. |

### Run controls

| Field | What it does |
|---|---|
| `run_snmp_walks` | Performs live SNMP walks before parsing when enabled. When disabled, stored walks are not reused unless `parse_all_walks` is explicitly enabled. |
| `enable_switch_list` | Enables the structured `switches` list. |
| `parse_all_walks` | Explicit offline/stored-walk import mode. When enabled, parses all valid walk files under the walk root; when disabled, only walk files created by the current run are parsed. |
| `generate_snmp2mqtt` | Generates SNMP2MQTT YAML and enables the post-run app handoff. |
| `clean_output_before_walk` | Removes old files from each target folder before writing a fresh walk. |
| `minimum_valid_walk_lines` | Treats smaller walks as failed or incomplete. |
| `snmp_timeout` | Seconds to wait for one SNMP request. |
| `snmp_retries` | Retry attempts after a timeout. |

### Switch identity

- **Switch Name (Used internally only)** is the stable machine-facing target ID, such as `SW5` or `CORE_A`. Keep it unique. It links walk folders, stack mappings, generated profiles, and report sections.
- **Display name** is optional human-facing text used for generated card titles. It does not control folder or profile identity.

### `switches` list

| Field | What it does |
|---|---|
| `switch_name` | Stable internal target ID. |
| `display_name` | Optional friendly generated-card title. |
| `switch_host` | Management IP address or resolvable hostname. |
| `sensor_prefix` | Prefix used for generated Home Assistant entities. |
| `snmp_community` | SNMP v2c read-only community; masked in normal output. |
| `walk_mode` | `targeted` requests useful known branches; `full` walks the complete accessible tree. |
| `switch_model` | `auto` uses exact-model detection. Selecting a registered model enables experimental compatibility override mode while retaining the real detected SKU. |

### `stack_member_prefixes` list

| Field | What it does |
|---|---|
| `switch_name` | Parent target ID from `switches[].switch_name`. |
| `member` | Numeric stack member index. |
| `display_name` | Optional friendly title for this member. |
| `sensor_prefix` | Entity prefix dedicated to this member. |

### CSV/fallback fields

| Field | What it does |
|---|---|
| `targets_csv` | Optional CSV target mapping used by advanced or import workflows. Standard CSV quoting is required for values containing commas. |

## UniFi2MQTT app fields

A newly installed UniFi2MQTT app requires both `site_id` and `api_key` before it can start. Saving valid settings in the Hub starts a stopped app or restarts an already running app.

These fields can be edited from **Switch Vision Hub → UniFi2MQTT Settings** or from the Home Assistant App configuration fallback. Secret fields are never read back into the Hub; leaving them blank preserves the current stored value.

| Field | What it does |
|---|---|
| `controller_url` | Base URL of the local UniFi Network controller. |
| `site_id` | Required UniFi Network site ID used by the site-scoped Integration API requests. |
| `api_key` | Required read-only UniFi Integration API key. Stored by Supervisor and never returned to the Hub; a blank Hub field preserves an existing key. |
| `verify_ssl` | Enables TLS certificate verification for the controller connection. |
| `poll_interval` | UniFi API polling interval in seconds, 10–300. |
| `mqtt_host` | MQTT broker hostname or address. |
| `mqtt_port` | MQTT broker port. |
| `mqtt_username` | Optional MQTT username. |
| `mqtt_password` | Optional MQTT password. Stored by Supervisor and masked in the Hub; a blank Hub field preserves it. Use Home Assistant App Configuration if you need to clear an existing password. |
| `mqtt_topic_prefix` | Root retained topic prefix used by UniFi2MQTT. |
| `mqtt_discovery_prefix` | Home Assistant MQTT Discovery prefix. |

## Native panel behaviour

The native panel reads:

```text
/share/switch_vision/generated-dashboard-card.yaml
```

It checks for source updates while visible, refreshes on focus, and supports an immediate Refresh action. New cards are prepared before the current dashboard is replaced. Failed refreshes leave the existing cards active.

## Dashboard card fields

### Identity and data mapping

| Field | What it does |
|---|---|
| `type` | Must be `custom:switch-vision-3650`. |
| `title` | Card title text. HTML-sensitive characters are escaped. |
| `member` | Friendly switch or stack-member name. |
| `selected_switch` | Generated entity group used by the card. |
| `discovery_selected_switch` | Discovery target identity associated with the card. |
| `switch_model` | Exact model used for registry mapping and model-aware visual defaults. |
| `model_override` | Marks an experimental manual compatibility override. |
| `detected_switch_model` | Preserves the real detected SKU when an override is active. |
| `calibration_profile` | Stable saved profile name. |
| `calibration_profile_load` | Enables saved-profile loading. |
| `calibration_profile_auto_load` | Loads the saved profile when the card starts. |
| `status_entity_prefix` | Entity prefix before the port number. |
| `status_entity_suffix` | Entity suffix after the port number, normally `_status`. |
| `switch_ip` | Optional management address shown in Status Box 1. |
| `management_ip` | Legacy alias/fallback for `switch_ip`. |

### Stack fields

| Field | What it does |
|---|---|
| `stack_enabled` | Enables stack-specific display and uptime behaviour. |
| `stack_id` | Optional stack identifier. |
| `stack_member_number` | Numeric member index. |
| `stack_uptime_mode` | Selects standalone or inherited stack uptime. |
| `stack_uptime_source` | Entity supplying inherited stack uptime. |
| `stack_member_uptime_source` | Optional member-specific uptime source. |

### Display controls

| Field | What it does |
|---|---|
| `demo` | Uses demonstration data instead of normal live entities. |
| `calibration_button` | Shows or hides the on-card Calibration button. |
| `show_labels` | Shows or hides port labels. |
| `show_numbers` | Shows or hides port numbers. |
| `show_legend` | Shows or hides the card legend. |
| `show_port_leds` | Shows or hides Link/Speed and Activity LED overlays. |
| `show_status_leds` | Shows or hides chassis/status LED overlays. |
| `show_status_panel` | Shows or hides Status Box 1. |
| `faceplate_file` | `__default__` for the exact-model recommendation or a safe custom filename. |
| `faceplate_show` | Legacy/manual compatibility field. `false` no longer hides the faceplate and resolves to the visible model recommendation. |
| `unknown_is_up` | Treats unknown status values as up when enabled. Normally leave disabled. |
| `status_up_values` | Custom entity states treated as up. |
| `status_down_values` | Custom entity states treated as down. |

### Activity LEDs and traffic timing

Switch Vision Core v2.2.0 calculates Activity LED intensity from measured **RX + TX throughput divided by negotiated link speed**. Normal mode defaults to Medium activity at `0.10%` utilisation and Fast activity at `1.00%`. These settings are normally changed in **Settings → Integrations → Switch Vision → Configure → Activity LEDs** and apply across Native, Community-strategy, and custom cards.

| Field | What it does |
|---|---|
| `activity_led_sensitivity_preset` | `low`, `normal`, `high`, or `custom`. Presets select the Medium/Fast utilisation boundaries. |
| `activity_slow_max_utilization_pct` | Custom-mode boundary where Slow ends and Medium begins. Factory custom value is `0.10`. |
| `activity_medium_max_utilization_pct` | Custom-mode boundary where Medium ends and Fast begins. Factory custom value is `1.0`. |
| `activity_slow_period_ms` | Slow blink period. v2.2 factory default is `500`. |
| `activity_medium_period_ms` | Medium blink period. v2.2 factory default is `250`. |
| `activity_fast_period_ms` | Fast blink period. v2.2 factory default is `120`. |
| `activity_hold_seconds` | Holds the last detected activity between traffic samples. Factory default is `12` seconds for the current 10-second traffic cadence. |
| `activity_hysteresis_pct` | Buffer around Medium/Fast boundaries to prevent rapid band changes near a threshold. Factory default is `20`. |
| `traffic_poll_seconds` | Expected traffic polling interval when supplied by generated/manual configuration. |
| `activity_poll_seconds` | Optional separate activity interval retained for compatibility. |
| `activity_window_ms` | Legacy/default activity-render window used when an explicit hold is unavailable. |
| `activity_decay_ms` | Legacy/default decay time used when an explicit hold is unavailable. |
| `traffic_rate_stale_ms` | Legacy compatibility field; traffic rates follow actual counter sensor update timestamps and are retained between samples. |
| `traffic_scan_interval` | Frontend traffic-entity scan interval. |

Preset boundaries are: **Low** = Medium at `1%`, Fast at `10%`; **Normal** = Medium at `0.10%`, Fast at `1%`; **High** = Medium at `0.02%`, Fast at `0.25%`. Custom uses the two percentage fields above. The global Switch Vision Core settings are authoritative during normal integrated operation; card/YAML values remain useful as fallback behaviour if the Core UI-settings service is unavailable.

### Status boxes

Status Box 1 is the primary switch summary. Status Box 2 is an independent secondary summary. The selected-port Status Box has its own field ordering and visibility.

Common switch fields include model, vendor, IP, CPU, temperature, PoE, uptime, OS, firmware, serial, stack, fans, and PSU.

Port and uplink fields include VLAN, MODE, description, link, RX, and TX. MODE is an optional Juniper-only row and remains hidden by default. Cisco cards retain the established VLAN, description, link, RX, and TX presentation.

Each status box supports independent position, size, fonts, colours, border, field ordering, visibility, and per-field offsets.

### Logo controls

| Field | What it does |
|---|---|
| `logo_show` | Shows or hides the configured logo. |
| `logo_file` | Logo asset filename/path. |
| `logo_x`, `logo_y` | Logo position. |
| `logo_width`, `logo_height` | Logo dimensions. |

## Interactive calibration

### Selection and movement fields

| Field | What it does |
|---|---|
| `calibration_mode` | Enables interactive calibration mode. |
| `calibration_target` | Selects ports, uplinks, status LEDs, logo, status boxes, or other groups. |
| `calibration_item` | Selects one item in the current target. |
| `calibration_part` | Selects the port box, number, Link/Speed LED, Activity LED, or other sub-part. |
| `calibration_step` | Movement and resize increment. |
| `calibration_show_hitboxes` | Shows clickable port hitboxes. |
| `calibration_show_labels` | Shows calibration labels. |
| `calibration_show_led_rings` | Shows LED guide rings. |

### Saved profile geometry

Each RJ45 port can contain:

| Profile field | Purpose |
|---|---|
| `center` | RJ45 visual centre. |
| `number` | Port-number label position. |
| `number_show` | Shows or hides that individual RJ45 port number. Missing values default to shown. |
| `hitbox` | RJ45 clickable width and height. |
| `led_left` | Link/Speed LED position. |
| `led_left_size` | Independent Link/Speed rectangle width and height. |
| `led_right` | Activity LED position. |
| `led_right_size` | Independent Activity rectangle width and height. |

`ui.port_led_shape` is `circle` or `rectangle`. Circle mode retains the normal radius. Rectangle mode uses the independent LED size fields and never resizes the RJ45 hitbox.

Profile-wide LED colour overrides are optional:

| Profile field | Purpose |
|---|---|
| `ui.link_led_color` | Overrides the illuminated Link LED colour across every RJ45 and SFP/uplink port. When omitted, factory speed-based Link colours are retained. |
| `ui.activity_led_color` | Overrides the illuminated Activity LED colour across every RJ45 and SFP/uplink port. When omitted, the existing Activity LED colour behaviour is retained. |

The Calibration colour-picker **Reset** action removes these overrides and restores factory LED colours. Off LEDs remain off, and the colour controls do not alter link state, activity detection, blink timing, LED geometry, or per-port visibility.

Status LED label styling is stored under `ui.status_leds`:

| Profile field | Purpose |
|---|---|
| `text_color` | Status LED label text colour. |
| `font_family` | Font stack used for Status LED labels. Older profiles default to the established Arial-family appearance. |
| `font_size` | Status LED label size in pixels. Older profiles default to `16.5`. |
| `font_weight` | Status LED label weight. `900`/bold is the backward-compatible default; Calibration provides a Bold toggle. |
| `hidden` | List of status LED names hidden for this profile. |

Calibration custom-colour controls use an inline picker with draggable saturation/value, hue, brightness, live preview, HEX entry, Reset, and Done. The same picker is used for Link LEDs, Activity LEDs, Status LED labels, RJ45 numbers, uplink labels, and Status Box custom colours.

Each SFP/uplink entry can also contain optional `led_left`, `led_right`, `led_left_size`, and `led_right_size` fields. Profiles that omit them retain the legacy fixed LED offsets from the SFP centre. Selecting or moving an SFP LED in Calibration materialises the optional coordinates for that profile. `label_show` controls the visibility of an individual SFP/uplink label and defaults to shown when omitted. The **Port Numbers** quick selection includes both RJ45 port numbers and SFP/uplink labels.

### Calibration actions

- **Save Profile** — validate and save without closing.
- **Done** — validate, save, and close.
- **Cancel** — discard unsaved working changes.
- **Reset Current Faceplate** — restore bundled defaults for the selected faceplate when available, otherwise model factory geometry, while retaining the selected custom faceplate image.
- **Reset Current Switch** — delete that switch's faceplate-specific calibrations and restore the exact-model profile and recommended faceplate.
- **Reset All Switches** — clear all saved Switch Vision calibrations and restore every loaded card to its own model-aware defaults.

There is no separate Apply Recommended Setup action. Exact-model Discovery and reset operations are the model-profile authorities.

## Calibration services

| Service | What it does |
|---|---|
| `switch_vision.save_calibration` | Validates and saves/replaces a named profile. Native faceplate saves can atomically mirror to the stable switch profile. |
| `switch_vision.delete_calibration` | Deletes a named profile and its active native-panel mirror when applicable. |
| `switch_vision.reset_calibrations` | Resets one switch or all saved Switch Vision calibrations. |
| `switch_vision.reload_calibrations` | Fires a reload event so open cards refresh saved data. |
| `switch_vision.set_ui_density` | Updates the Hub/Discovery management UI density used by the top-right density icon. Dashboard presentation is not affected. |

Save, delete, reset, and profile-read operations use one integration-level asynchronous lock.

## Faceplate-specific profile resolution

1. **Default / recommended** uses the exact-model registry faceplate and the stable switch/member profile.
2. A custom faceplate uses a derived profile name combining the base profile with a stable filename token.
3. When no custom-faceplate profile exists, Switch Vision clones the current switch geometry as a starter.
4. Renaming a faceplate creates a new namespace, so stable filenames are recommended.
5. A missing custom image displays the model-recommended artwork instead of a blank faceplate.

Calibration exports include `profile_scope`, `base_profile_name`, and `faceplate_file`.

The active faceplate state is either:

- `__default__` — exact-model recommended visible faceplate;
- a safe custom filename.

Legacy `__none__`, hidden, blank, invalid, or missing values migrate to `__default__`.

## Profile validation

Imported, saved, and loaded profiles are rejected safely when they contain:

- unsafe or excessively long profile names;
- payloads over the supported size limit;
- non-finite JSON values;
- missing or excessive visual elements;
- zero, negative, or unreasonable dimensions;
- coordinates far outside the canvas;
- unsafe asset paths;
- unsupported canvas dimensions;
- a stored profile name that does not match its storage key.

## Display naming

- `display_name` supplies the generated card title.
- The retired standalone faceplate-label system is not part of the current workflow.
## Card header display

### Global **Show card headers** option

Configured from **Settings → Devices & services → Switch Vision → Configure**. It shows or hides the complete header row on every Switch Vision card, including native and custom YAML dashboards. Per-card header visibility keys from earlier releases are ignored.

### `card_header_title`

Optional custom card heading. Leave blank to retain the automatic title generated from the card title and stable switch/member key. The title remains stored when headers are hidden and appears again when the global option is enabled.

```yaml
card_header_title: Garage Core Switch
```
