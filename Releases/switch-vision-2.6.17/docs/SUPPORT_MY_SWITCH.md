# Support My Switch

Support My Switch is the preferred workflow for requesting support for new hardware and supplying diagnostic evidence.

## Open the web interface

1. Open **Switch Vision Discovery** from the Home Assistant sidebar, or open its app page and select **Open Web UI**.
2. Select **Support My Switch**.

The persistent Web UI remains available while the contribution is created.

## What it collects

A contribution package can include:

- full or targeted SNMP walks;
- Discovery reports and logs;
- generated SNMP2MQTT YAML;
- generated dashboard card YAML;
- device summaries and fingerprints;
- exact-model registry and validation information;
- model override metadata when used;
- privacy and bundle-quality reports;
- optional contributor recognition details.

## Privacy processing

The package is created from a temporary copy of `/share/switch_vision/`. The live folder is not modified.

Credentials are always removed. Optional controls can mask:

- management IP addresses;
- MAC addresses;
- hostnames;
- VLAN names;
- interface descriptions.

The Web UI warns when common identity masks are disabled. Full walks can expose network inventory information, so review every package before sharing it.

Every file in the temporary bundle copy must be inspectable. Unsupported binary files, oversized files, unreadable or unwritable files, symbolic links, and special files are excluded. Their original names and paths are not written to the report; Switch Vision records a privacy-safe identifier, suffix, size, and reason.

Any uninspectable file changes the bundle result to **REVIEW REQUIRED** and suppresses the prepared email and email-without-attachment actions.

## Bundle results

### PASS

All files were inspected and the privacy processor found no blocking condition.

### PASS WITH PRIVACY WARNINGS

All files were inspected, but the selected privacy options or detected content require additional user review. The normal prepared-email workflow remains available.

### REVIEW REQUIRED

At least one file could not be inspected or sanitised. The ZIP remains available for manual review, but prepared send actions are withheld.

Review:

```text
BUNDLE_QUALITY.txt
SANITIZATION_REPORT.txt
```

Do not share the archive until the review reason is understood.

## Submission process

1. Open **Support My Switch**.
2. Choose privacy and recognition options.
3. Select **Create contribution**.
4. Watch the live progress display.
5. Review the bundle-quality result and device cards.
6. For a PASS result, select **Prepare Email** to download the `.eml` message with the ZIP attached.
7. Open the message in the normal email application, review it, and press Send.

Nothing is transmitted automatically, and Switch Vision stores no email credentials.

Generated contribution files remain in:

```text
/share/switch_vision/contributions/
```

Send clean contributions to:

```text
switch-vision@zemerdon.com
```

## Validation process

A contribution supplies evidence but does not replace real-device testing.

1. **Detected** — Switch Vision recognises the device.
2. **Experimental** — generated support exists but validation is incomplete.
3. **Community Validated** — a contributor successfully tests the implementation.
4. **Confirmed Supported** — support has strong repeatable validation.

Validation can be recorded separately for exact-model detection, RJ45 mapping, PoE, system sensors, uplinks, and stack behaviour.
