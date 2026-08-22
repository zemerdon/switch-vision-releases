from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.4.13"


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement target, found {count}")
    write(path, text.replace(old, new, 1))


card = ROOT / "src/js/switch-vision.js"
replace_once(
    card,
    """const addHitbox = (type, id, item) => {\n      if (!item?.center || !item?.hitbox) return;\n\n      const [cx, cy] = item.center;\n      const [w, h] = visualHitboxSize(type, item.hitbox);""",
    """const addHitbox = (type, id, item) => {\n      if (!item?.center) return;\n\n      const fallbackHitbox = type === \"port\" ? [34, 56] : [94, 48];\n      const [cx, cy] = item.center;\n      const [w, h] = visualHitboxSize(type, item.hitbox || fallbackHitbox);""",
)

panel = ROOT / "src/custom_components/switch_vision/switch-vision-panel.js"
replace_once(
    panel,
    ".meta{font-family:monospace;white-space:pre-wrap;word-break:break-word;background:#0d1216;padding:12px;border-radius:8px;max-height:320px;overflow:auto}",
    ".meta{font-family:monospace;white-space:pre-wrap;word-break:break-word;background:#0d1216;color:#e8eef3;padding:12px;border-radius:8px;max-height:320px;overflow:auto}",
)

write(ROOT / "VERSION", VERSION + "\n")

release_notes = f"""# Switch Vision Core v{VERSION}

Core {VERSION} fixes two dashboard UI regressions observed on a community-validated Zyxel XS1930-10.

Rendered ports now remain selectable when a saved or custom calibration contains the port centre but omits an explicit hitbox. Switch Vision derives the normal visual hitbox for the rendered socket rather than allowing the click to fall through to the switch-summary background handler. Blank interface descriptions continue to display as `DESC —` while the port remains selected.

The native dashboard Advanced diagnostics block now uses an explicit light foreground on its fixed dark background, keeping diagnostic text readable under Home Assistant themes whose primary text colour is dark.

No device mapping, telemetry, faceplate geometry, Discovery, SNMP2MQTT, or UniFi2MQTT behaviour changes are included in this corrective release.
"""
write(ROOT / "RELEASE_NOTES.md", release_notes)
write(ROOT / "src/RELEASE_NOTES.md", release_notes)

entry = """## v2.4.13 — Port selection and native diagnostics theme fixes

- Keep rendered ports clickable when a saved/custom calibration has a port `center` but no explicit `hitbox`; derive the normal visual hitbox instead of allowing the click to fall through to switch summary.
- Preserve blank interface descriptions as a selected-port state (`DESC —`) rather than confusing missing description data with selection failure.
- Give the native dashboard Advanced diagnostics block an explicit light foreground on its fixed dark background so it remains readable under dark-text Home Assistant themes.
- Add permanent regression coverage for calibration hitbox fallback and native diagnostics contrast.
- No device mapping, telemetry, faceplate geometry, Discovery, SNMP2MQTT, or UniFi2MQTT behaviour changes.

"""
changelog_path = ROOT / "CHANGELOG.md"
changelog = changelog_path.read_text(encoding="utf-8")
if "## v2.4.13 — Port selection and native diagnostics theme fixes" in changelog:
    raise SystemExit("v2.4.13 changelog entry already exists")
changelog = entry + changelog
write(changelog_path, changelog)
write(ROOT / "src/CHANGELOG.md", changelog)

test = r'''from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD_SOURCE = ROOT / "src/js/switch-vision.js"
CARD_PACKAGED = ROOT / "src/custom_components/switch_vision/switch-vision-card.js"
PANEL = ROOT / "src/custom_components/switch_vision/switch-vision-panel.js"

OLD_GATE = "if (!item?.center || !item?.hitbox) return;"
NEW_GATE = "if (!item?.center) return;"
FALLBACK = 'const fallbackHitbox = type === "port" ? [34, 56] : [94, 48];'
USE_FALLBACK = "visualHitboxSize(type, item.hitbox || fallbackHitbox)"
OLD_META = ".meta{font-family:monospace;white-space:pre-wrap;word-break:break-word;background:#0d1216;padding:12px;border-radius:8px;max-height:320px;overflow:auto}"
NEW_META = ".meta{font-family:monospace;white-space:pre-wrap;word-break:break-word;background:#0d1216;color:#e8eef3;padding:12px;border-radius:8px;max-height:320px;overflow:auto}"


def check_card(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert NEW_GATE in text, path
    assert FALLBACK in text, path
    assert USE_FALLBACK in text, path
    assert OLD_GATE not in text, path


def main() -> None:
    check_card(CARD_SOURCE)
    check_card(CARD_PACKAGED)
    panel = PANEL.read_text(encoding="utf-8")
    assert NEW_META in panel
    assert OLD_META not in panel
    print("Port selection/theme regressions: PASS")


if __name__ == "__main__":
    main()
'''
write(ROOT / "tests/test_port_selection_theme_regressions.py", test)

subprocess.run(["python3", "build.py", "-v", VERSION], cwd=ROOT, check=True)

for generated in (
    ROOT / f"Releases/switch-vision-{VERSION}.zip",
    ROOT / f"Releases/switch-vision-{VERSION}.zip.sha256",
    ROOT / f"Switch_Vision_v{VERSION}_source.zip",
    ROOT / f"Switch_Vision_v{VERSION}_SHA256SUMS.txt",
):
    generated.unlink(missing_ok=True)

subprocess.run(["node", "--check", "src/js/switch-vision.js"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/custom_components/switch_vision/switch-vision-card.js"], cwd=ROOT, check=True)
subprocess.run(["node", "--check", "src/custom_components/switch_vision/switch-vision-panel.js"], cwd=ROOT, check=True)
subprocess.run(["python3", "tools/check_core_release_parity.py"], cwd=ROOT, check=True)

for path in sorted((ROOT / "tests").glob("test_*.py")):
    subprocess.run(["python3", str(path.relative_to(ROOT))], cwd=ROOT, check=True)

print("Core 2.4.13 preparation and regression suite: PASS")
