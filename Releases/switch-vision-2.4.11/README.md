# Switch Vision Releases

![Switch Vision](https://switch-vision.zemerdon.com/icon_pack/release.png)

This repository is the official public **Switch Vision Core/dashboard release channel** for Home Assistant.

Switch Vision is now composed of independently versioned components. The Core/dashboard release published here is installed and managed alongside the separate Discovery, SNMP2MQTT, UniFi2MQTT, and Installer projects.

---

## Current public Core release

### Switch Vision v2.4.11

**v2.4.11** is the current tested public Switch Vision Core/dashboard release.

This release adds Calibration LED Test Mode, a full Calibration Profile Manager in the Switch Vision Hub, and a runtime Refresh Faceplate action that reloads updated faceplate image bytes without renaming the file or changing calibration profile identity.

Component versions validated when Core v2.2.2 was released:

```text
Switch Vision Core/dashboard    2.2.2
Switch Vision Discovery         2.1.13
Switch Vision SNMP2MQTT app     0.9.8
Switch Vision UniFi2MQTT        2.0.41
Switch Vision Installer         2.1.19
```

These versions are a historical compatibility baseline for the Core v2.2.2 release, not a live component-version list.

Switch Vision components have independent version lines and may receive newer compatible releases without requiring a Core version change. Use Switch Vision Installer for current installed/latest component status.

---

## Recommended installation

The recommended deployment path is **Switch Vision Installer**:

https://github.com/zemerdon/switch-vision-installer

The Installer manages the Core/dashboard files and the separately versioned Switch Vision apps. It also provides component status, updates, backups, restore actions, and dependency-aware Update All handling.

After a Core file update, restart Home Assistant Core when the Installer requests it.

---

## Downloads

Latest public release:

https://github.com/zemerdon/switch-vision-releases/releases/latest

All releases:

https://github.com/zemerdon/switch-vision-releases/releases

For v2.2.2 the authoritative attached release files are:

```text
switch-vision-2.2.2.zip
Switch_Vision_v2.2.2_source.zip
Switch_Vision_v2.2.2_SHA256SUMS.txt
```

### v2.2.2 SHA-256

```text
61241576b143ea7370b43f1940e3c5069c8ff7465038e33779e7170765f84d20  switch-vision-2.2.2.zip
0318e91091b100ea709fd7e89ecd9f989a4dfd06d42f161bc76c13fe9cb46daf  Switch_Vision_v2.2.2_source.zip
```

For **v2.2.2**, use the explicitly attached `Switch_Vision_v2.2.2_source.zip` as the authoritative public source package. GitHub's automatically generated **Source code (zip)** and **Source code (tar.gz)** entries are repository-tag snapshots and are not the authoritative v2.2.2 Switch Vision source package.

---

## Component repositories

- Core/dashboard public releases: https://github.com/zemerdon/switch-vision-releases
- Switch Vision Discovery: https://github.com/zemerdon/switch-vision-discovery
- Switch Vision SNMP2MQTT core: https://github.com/zemerdon/switch-vision-snmp2mqtt
- Switch Vision SNMP2MQTT Home Assistant app: https://github.com/zemerdon/switch-vision-snmp2mqtt-addon
- Switch Vision UniFi2MQTT: https://github.com/zemerdon/switch-vision-unifi2mqtt
- Switch Vision Installer: https://github.com/zemerdon/switch-vision-installer

The v2.2.2 public Core source is distributed as the explicit source archive attached to the v2.2.2 GitHub Release.

---

## Normal workflow

```text
Install / update through Switch Vision Installer
→ Restart Home Assistant Core when requested
→ Configure switches in Switch Vision Discovery
→ Run Discovery
→ Discovery generates dashboard and SNMP2MQTT configuration
→ Open Switch Vision from the Home Assistant sidebar
```

Discovery and SNMP2MQTT are separate Home Assistant apps and are not bundled inside the Core release ZIP.

UniFi2MQTT is optional and is only required for users using the read-only UniFi Network Integration API path.

---

## Activity LEDs in v2.2

Switch Vision Core v2.2 measures activity relative to negotiated link speed rather than using one fixed byte-rate threshold for every port.

Activity LED controls include:

- Low / Normal / High / Custom sensitivity presets
- configurable Medium and Fast utilisation thresholds
- Slow / Medium / Fast blink periods
- activity hold time
- hysteresis
- safe fallback when negotiated speed is unavailable

Settings are available under:

```text
Switch Vision Core → Options → Activity LEDs
```

---

## v2.2.2 hotfix

v2.2.2 corrects C3650 factory-profile Status Box value coordinates that could cause these fields to disappear after a reset:

```text
MODEL
IP
CPU
TEMP
POE
```

`UPTIME` was unaffected. The correction was applied to the primary C3650 factory profile and the corresponding legacy / Status Box 2 definitions.

---

## Supported devices

Switch Vision support is tracked by **exact model identifier**. The current supported-device registry is shipped with the Core release and Discovery.

The authoritative community index is maintained on the Switch Vision forum:

https://switch-vision.zemerdon.com/viewtopic.php?t=74

Unsupported or experimental hardware can be submitted through **Support My Switch** in Discovery.

---

## Documentation and support

Switch Vision forum:

https://switch-vision.zemerdon.com

Useful forum sections include installation, configuration reference, supported devices, Support My Switch, troubleshooting, releases, and advanced custom-dashboard guidance.

Support email:

```text
switch-vision@zemerdon.com
```

---

For the Core tag/source/artifact trust model, see [RELEASE_PROVENANCE.md](RELEASE_PROVENANCE.md).

## Release integrity policy

For future Core releases the intended release sequence is:

```text
Prepare and validate exact release source
→ build install package from that source
→ verify install/source parity and versions
→ calculate SHA-256 digests
→ commit the exact public release-source state
→ tag that exact commit
→ publish install ZIP, explicit source ZIP, checksum file, and release notes
```

A release should not be considered complete until its explicit attached artifacts and checksums are published and verified.

---

## Licence and distribution

No open-source licence is currently included with Switch Vision. Unless a release states otherwise, copyright is retained by the project owner.

Official packages are distributed through the Switch Vision project repositories. Modified builds must not be represented as official Switch Vision releases.
