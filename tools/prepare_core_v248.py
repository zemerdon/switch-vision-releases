#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "js" / "switch-vision.js"
TEST = ROOT / "tests" / "test_speed_formatting.py"
CHANGELOG = ROOT / "CHANGELOG.md"
RELEASE_NOTES = ROOT / "RELEASE_NOTES.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.write_text(
        text.replace("\r\n", "\n").replace("\r", "\n"),
        encoding="utf-8",
        newline="\n",
    )


# The SFP status panel must use the same negotiated/current speed resolver that
# already drives SFP activity/rate behaviour. Never assume every active generic
# uplink is 10G.
card = read(CARD)
old = '''    link: (() => {
      const unifi = unifiSfpPort(config, n);
      if (unifi) return speedLabel(unifi.speed_mbps, up);
      return up ? "10G Full" : "Down";
    })()
'''
new = '''    link: speedLabel(sfpSpeedMbps(hass, config, n), up)
'''
count = card.count(old)
if count != 1:
    raise SystemExit(f"Expected exactly one hard-coded SFP 10G fallback, found {count}")
write(CARD, card.replace(old, new, 1))


# Permanent regression: selected SFP presentation must use negotiated speed and
# the resolver must continue accepting both 1G and 10G Switch Vision entity IDs.
test = read(TEST)
marker = '''    def test_fractional_gigabit_speed_is_not_rounded_up(self) -> None:
'''
if marker not in test:
    raise SystemExit("Speed-formatting test insertion marker missing")
regression = '''    def test_selected_sfp_link_uses_negotiated_speed(self) -> None:
        source = CARD.read_text(encoding="utf-8")
        selected = extract_js_function(
            source, "function selectedSfpDetails(hass, config, port)"
        )
        helper = extract_js_function(
            source, "function sfpSpeedMbps(hass, config, port)"
        )

        self.assertNotIn('10G Full', selected)
        self.assertIn(
            "link: speedLabel(sfpSpeedMbps(hass, config, n), up)",
            selected,
        )
        self.assertIn("_sfp_1g_", helper)
        self.assertIn("_sfp_10g_", helper)
        self.assertIn("_uplink_", helper)

'''
if "def test_selected_sfp_link_uses_negotiated_speed" not in test:
    test = test.replace(marker, regression + marker, 1)
write(TEST, test)


# Human-facing release metadata.
changelog = read(CHANGELOG)
entry = '''## v2.4.8 — SFP negotiated-speed status labels

- Replace the generic SFP status-panel 10G fallback with the existing live SFP speed resolver.
- Huawei S5720 1G SFP uplinks now display 1G instead of 10G when negotiated/current speed telemetry reports 1000 Mbps.
- Preserve UniFi, 10G SFP+, link-down, traffic, Activity LED, calibration, Discovery handoff, and device-mapping behaviour.
- Add permanent regression coverage preventing a hard-coded 10G SFP status fallback from returning.

'''
if not changelog.startswith("## v2.4.7"):
    raise SystemExit("Unexpected current changelog head; expected v2.4.7")
if "## v2.4.8" not in changelog:
    changelog = entry + changelog
write(CHANGELOG, changelog)

write(
    RELEASE_NOTES,
    '''# Switch Vision Core v2.4.8

Core 2.4.8 fixes SFP status-panel speed presentation. Generic SFP links now use the existing negotiated/current-speed resolver instead of assuming every active non-UniFi uplink is 10G.

This fixes Huawei S5720 1G SFP uplinks showing **10G Full** even though Discovery and SNMP telemetry correctly report 1G. Existing 10G SFP+, UniFi, link-down, traffic, Activity LED, calibration geometry, Discovery handoff, device mapping, and saved calibration behaviour are unchanged.
''',
)

print("Prepared Switch Vision Core v2.4.8 negotiated SFP speed fix")
