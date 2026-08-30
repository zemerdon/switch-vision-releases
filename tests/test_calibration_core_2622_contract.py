#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "src" / "js" / "switch-vision.js"
COMPONENT = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"


def main() -> int:
    source = CANONICAL.read_text(encoding="utf-8")
    component = COMPONENT.read_text(encoding="utf-8")
    assert source == component, "canonical and Home Assistant card JavaScript must remain byte-identical"

    required = [
        'const SV_VERSION = "2.6.22";',
        'const SV_GEOMETRY_RENDER_COORDINATE_SPACE = "switch-vision-render-2048x448-v1";',
        'calibrationRenderSpaceData(cloneCalibrationData(cal || {}))',
        'schema_version: 2,',
        'coordinate_space: SV_GEOMETRY_RENDER_COORDINATE_SPACE',
        'ports: clonePlainData(source.ports || {}),',
        'sfp: clonePlainData(source.sfp || {}),',
        'status_leds: clonePlainData(source.status_leds || {}),',
        'ui: geometryUi',
        'function geometryTransferLegacyRenderSpace(geometry)',
        'function geometryTransferPresentationV2(currentCal, geometry)',
        'if (![1, 2].includes(geometrySchemaVersion))',
        'geometry = geometryTransferLegacyRenderSpace(geometry);',
        'next = geometryTransferPresentationV2(current, geometry);',
        'presentationTransferred: geometrySchemaVersion >= 2',
        'function portNumberRenderOffset(portNumber, layout = null)',
        'Number(point[1]) + portNumberRenderOffset(portNumber)',
        'const setPortNumberPoint = (portNumber, point) => {',
        'point[1] = rounded(yValue - portNumberRenderOffset(portNumber));',
        'setPortNumberPoint(key, port?.number)',
        'setPortNumberPoint(editable.key, editable.item?.number)',
        'ny + portNumberRenderOffset(n, layout)',
    ]
    for marker in required:
        assert marker in source, f"missing v2.6.22 Calibration contract marker: {marker}"

    forbidden = [
        'Unsupported geometry schema_version; this release supports version 1.',
        'Status LED geometry does not match the current calibration topology.',
        'ports: geometryTransferEntryMap(source.ports),',
        'sfp: geometryTransferEntryMap(source.sfp),',
        'applied.ui.logo.file = current.ui?.logo?.file;',
        'applied.ui.logo.source = current.ui?.logo?.source;',
        'const numberY = ny + (n % 2 === 1 ? layout.ports.odd : layout.ports.even);',
        'for (const port of Object.values(cal.ports || {})) changed = setPoint(port?.number) || changed;',
    ]
    for marker in forbidden:
        assert marker not in source, f"legacy v2.6.21 behavior remains: {marker}"

    target_y = 100
    odd_stored = target_y - 7
    even_stored = target_y - (-7)
    assert odd_stored + 7 == target_y
    assert even_stored - 7 == target_y

    print("Switch Vision v2.6.22 Calibration transfer/label regression: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
