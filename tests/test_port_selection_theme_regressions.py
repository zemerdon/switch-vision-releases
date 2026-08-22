from pathlib import Path

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
