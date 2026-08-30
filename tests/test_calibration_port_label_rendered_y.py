#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "src" / "js" / "switch-vision.js"
COMPONENT = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"


def main() -> None:
    frontend = FRONTEND.read_text(encoding="utf-8")
    component = COMPONENT.read_text(encoding="utf-8")
    assert frontend == component, "canonical JS and HA component card JS differ"

    required = (
        "function portNumberRenderOffset(portNumber, layout = null)",
        "const numberY = ny + portNumberRenderOffset(n, layout);",
        "Number(point[1]) + portNumberRenderOffset(portNumber)",
        "const setPortNumberPoint = (portNumber, point) => {",
        "point[1] = rounded(yValue - portNumberRenderOffset(portNumber));",
        "setPortNumberPoint(key, port?.number)",
        "setPortNumberPoint(key, port.number)",
        "setPortNumberPoint(editable.key, editable.item?.number)",
    )
    for marker in required:
        assert marker in frontend, marker

    forbidden = (
        "const numberY = ny + (n % 2 === 1 ? layout.ports.odd : layout.ports.even);",
        "for (const port of Object.values(cal.ports || {})) changed = setPoint(port?.number) || changed;",
    )
    for marker in forbidden:
        assert marker not in frontend, marker

    target_y = 100
    odd_stored = target_y - 7
    even_stored = target_y - (-7)
    assert odd_stored + 7 == target_y
    assert even_stored - 7 == target_y

    print("Core 2.6.22 RJ45 rendered-Y coordinate contract: PASS")


if __name__ == "__main__":
    main()
