# Installing Switch Vision

These instructions describe the current clean-install workflow. Use `UPGRADING.md` for an existing installation.

## 1. Requirements

Confirm the prerequisites in `REQUIREMENTS.md`, including:

- Home Assistant OS or Supervised installation with Supervisor/App support;
- access to `/config` and `/share`;
- read-only SNMP v2c access to each switch.

## 2. Recommended installation: Switch Vision Installer

Add the official Installer repository:

```text
https://github.com/zemerdon/switch-vision-installer
```

This is the only repository end users need to add manually. Install and start **Switch Vision Installer**, then install the current Switch Vision release from its Web UI.

The Installer:

- validates the public Switch Vision release package;
- creates and validates a recovery backup;
- installs or updates the main custom component and dashboard assets;
- registers and installs/updates repository-backed Switch Vision Discovery;
- registers and installs/updates repository-backed Switch Vision SNMP2MQTT;
- registers optional UniFi2MQTT when required;
- preserves/restores supporting-app Supervisor options without restoring local app source trees.

Discovery, SNMP2MQTT, and UniFi2MQTT version independently from the main Switch Vision release.

## 3. Manual main-runtime fallback

The installable Switch Vision ZIP contains the main integration/dashboard runtime only. It does **not** contain supporting-app source trees.

Extract:

```text
switch-vision-<version>/
```

Do not combine files from multiple releases.

### 3.1 Install the custom component

Copy:

```text
custom_components/switch_vision/
```

to:

```text
/config/custom_components/switch_vision/
```

The files must be directly inside that directory. Do not create a nested `switch_vision/switch_vision/` path.

Restart Home Assistant Core, then add the integration through:

```text
Settings → Devices & services → Add Integration → Switch Vision
```

New installations do not require `switch_vision:` in `configuration.yaml`.

### 3.2 Install dashboard assets

Create or replace:

```text
/config/www/switch-vision/
```

with these release folders:

```text
calibration/
css/
faceplates/
js/
layouts/
logos/
```

The native panel loads its own versioned resources automatically.

A manual/custom YAML dashboard must register the Switch Vision card as a **JavaScript Module**:

```text
/local/switch-vision/js/switch-vision.js?v=<version>
```

Generated manual layouts using Layout Card also require:

```text
/hacsfiles/lovelace-layout-card/layout-card.js
```

Neither manual resource is required by the native sidebar panel.

### 3.3 Supporting apps

Even when installing the main runtime manually, use the **Switch Vision Installer repository** to register/install Discovery, SNMP2MQTT, and optional UniFi2MQTT. Do not copy old `local_apps/` folders from historical Switch Vision releases.

UniFi2MQTT is configured from **Switch Vision Hub → UniFi2MQTT Settings**. A successful poll writes:

```text
/share/switch_vision/unifi/devices.json
```

Discovery consumes that normalized snapshot and can generate cards for exact registered UniFi models. Keep SNMP2MQTT available for per-port RX/TX traffic where the current UniFi API does not expose suitable counters.

## 4. Switch Vision SNMP2MQTT handoff

The Installer manages Switch Vision SNMP2MQTT. Generated-YAML import uses:

```text
/share/switch_vision/generated-snmp2mqtt.yaml
```

Do not maintain a second active copied YAML file. The generated file is the authoritative Discovery handoff.

## 5. Configure Discovery

Open:

```text
Settings → Apps → Switch Vision Discovery → Configuration
```

For each target configure:

- **Switch Name (Used internally only)** — stable unique internal ID;
- display name — optional friendly card title;
- management IP address or hostname;
- sensor prefix;
- read-only SNMP community;
- targeted or full walk mode;
- **Switch Model** — normally **Auto-detect**.

For a stack, configure the parent target once and add a separate member number, display name, and sensor prefix for each member.

A previous Discovery configuration can be restored through **Discovery → Configuration → Import Configuration**. Store exports securely because they may contain management addresses and SNMP community strings.

## 6. Run Discovery

Open the Discovery Web UI and select **Run Discovery**.

The normal flow is:

```text
Validating configured switches
→ Running SNMP walks
→ Identifying exact models and interfaces
→ Generating SNMP2MQTT YAML
→ Generating dashboard card YAML
→ Starting or restarting Switch Vision SNMP2MQTT
→ Complete
```

Discovery generates:

```text
/share/switch_vision/generated-snmp2mqtt.yaml
/share/switch_vision/generated-dashboard-card.yaml
```

Use **Show Debug** for detailed command, parser, registry, file, and Supervisor information.

## 7. Open the native dashboard

Select **Switch Vision** from the Home Assistant sidebar.

The panel automatically reads the generated dashboard YAML and creates the switch cards. It keeps the current dashboard visible if a refresh fails and replaces cards only after the next complete set is ready.

To hide or show the sidebar shortcut or the native-card Calibration buttons, open:

```text
Settings → Devices & services → Switch Vision → Configure
```

## 8. Model profiles and calibration

Registered exact models automatically receive their mapped profile and recommended visible faceplate. Unknown models receive a visible generic fallback that can be customised.

Custom faceplates belong in:

```text
/config/www/switch-vision/faceplates/
```

Custom logos belong in:

```text
/config/www/switch-vision/logos/
```

To use a custom faceplate:

1. copy the PNG into the faceplates directory;
2. open the switch card and select **Calibrate**;
3. refresh the asset list;
4. choose the custom image;
5. adjust ports, LEDs, uplinks, labels, logo, and status boxes;
6. select **Done** to validate, save, and close.

The available faceplate choices are **Default / recommended** and named custom images. A faceplate cannot be hidden. Missing or invalid custom artwork falls back to the visible model recommendation.

Each faceplate retains independent geometry. Keep custom filenames stable so their saved profile namespaces remain stable.

## Manual dashboard fallback

The generated card YAML remains available at:

```text
/share/switch_vision/generated-dashboard-card.yaml
```

It can be copied into an existing Lovelace dashboard. Manual cards remain supported, but the native sidebar workflow is recommended.
