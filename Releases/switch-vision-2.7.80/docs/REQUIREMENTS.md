# Requirements

## Home Assistant

- Home Assistant OS or Supervised installation with Home Assistant Apps/Supervisor support
- Access to `/config` and `/share`
- Permission to install the Switch Vision custom integration and the Switch Vision Installer app
- A current Home Assistant frontend and browser

The native Switch Vision dashboard does not require a manually created Lovelace dashboard or a manually registered Switch Vision resource.

## Switch Vision Installer and supporting apps

End users only need to add this repository manually:

```text
https://github.com/zemerdon/switch-vision-installer
```

The Installer registers and manages the separately versioned supporting apps:

- Switch Vision Discovery
- Switch Vision SNMP2MQTT
- optional Switch Vision UniFi2MQTT

Their source trees are not bundled inside the main Switch Vision release ZIP.

Switch Vision SNMP2MQTT consumes the generated configuration from:

```text
/share/switch_vision/generated-snmp2mqtt.yaml
```

Discovery validates this file and attempts to start or restart SNMP2MQTT after a successful run.

## Optional UniFi2MQTT bridge

For UniFi API support provide:

- a reachable UniFi Network controller URL;
- the UniFi site ID;
- a read-only Integration API key;
- MQTT host, port, username, and password as required by the broker.

The bridge uses read-only `GET` requests with the `X-API-KEY` header. Current UniFi API support supplies identity, port state/speed/connector/PoE, CPU, memory, uptime, and uplink rates where available. Discovery consumes `/share/switch_vision/unifi/devices.json` and auto-generates cards for exact registered models. Per-port RX/TX traffic remains on the SNMP2MQTT path until the API exposes suitable counters.

Configure UniFi2MQTT from **Switch Vision Hub → UniFi2MQTT Settings**. The Home Assistant App configuration remains the fallback.

## Network and switch access

- Managed switch reachable from Home Assistant
- SNMP v2c enabled with a read-only community
- UDP port 161 permitted between Home Assistant and the switch
- Stable management IP address or resolvable hostname

Use a dedicated read-only SNMP community. Do not reuse administrative credentials.

## Supervisor access

Discovery requires Supervisor API access to locate and control the supporting apps. The published Discovery repository supplies its own required app permissions; the main Switch Vision ZIP does not ship or override Discovery app source.

## Manual dashboard fallback dependencies

Only manual/custom YAML dashboards need the Switch Vision card resource:

```text
/local/switch-vision/js/switch-vision.js?v=<version>
```

Only generated manual layouts using Layout Card need the HACS resource:

```text
/hacsfiles/lovelace-layout-card/layout-card.js
```

The native sidebar panel uses neither manually registered resource.

## Browser support and caching

Use a current desktop or mobile browser. Switch Vision uses versioned panel and card module URLs, but a browser may retain old frontend code after an upgrade.

After replacing the custom component or dashboard assets:

1. restart Home Assistant Core when the custom component changed;
2. hard-refresh the browser;
3. clear site data or test in an Incognito window if an old version remains visible.

## Storage and backup

Preserve these paths during normal upgrades:

```text
/share/switch_vision/
/config/.storage/switch_vision_calibrations
```

Back up custom assets before replacing `/config/www/switch-vision/`:

```text
/config/www/switch-vision/faceplates/
/config/www/switch-vision/logos/
```
