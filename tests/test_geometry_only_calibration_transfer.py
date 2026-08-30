#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "src" / "js" / "switch-vision.js"
COMPONENT = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
VERSION = ROOT / "VERSION"


def main() -> None:
    frontend = FRONTEND.read_text(encoding="utf-8")
    component = COMPONENT.read_text(encoding="utf-8")
    assert frontend == component, "canonical JS and HA component card JS differ"

    version_text = VERSION.read_text(encoding="utf-8").strip()
    version = tuple(int(part) for part in version_text.split("."))
    assert version >= (2, 6, 22), f"geometry presentation transfer requires Core 2.6.22+, got {version_text}"
    assert f'const SV_VERSION = "{version_text}";' in frontend, "JavaScript version must match VERSION"

    required = (
        'const SV_GEOMETRY_TRANSFER_TYPE = "switch-vision-geometry-profile-v1";',
        'const SV_GEOMETRY_RENDER_COORDINATE_SPACE = "switch-vision-render-2048x448-v1";',
        'schema_version: 2,',
        'const source = ensureCalibrationUi(calibrationRenderSpaceData(cloneCalibrationData(cal || {})));',
        'const geometryUi = clonePlainData(source.ui || {});',
        'delete geometryUi.faceplate.file;',
        'delete geometryUi.faceplate.source;',
        'ports: clonePlainData(source.ports || {}),',
        'sfp: clonePlainData(source.sfp || {}),',
        'status_leds: clonePlainData(source.status_leds || {}),',
        'ui: geometryUi',
        'function geometryTransferLegacyRenderSpace(geometry)',
        'coordinate_space: SV_FACEPLATE_NATIVE_COORDINATE_SPACE',
        'function geometryTransferPresentationV2(currentCal, geometry)',
        'next.ports = clonePlainData(geometry.ports || {});',
        'next.sfp = clonePlainData(geometry.sfp || {});',
        'next.status_leds = clonePlainData(geometry.status_leds || {});',
        'next.ui = clonePlainData(geometry.ui || {});',
        'next.image.file = current.image?.file;',
        'next.image.master = current.image?.master;',
        'next.ui.faceplate.file = current.ui?.faceplate?.file;',
        'next.ui.faceplate.source = current.ui?.faceplate?.source;',
        'next.model = current.model;',
        'next.profile = current.profile;',
        'next.stack = clonePlainData(current.stack || {});',
        'next.management = clonePlainData(current.management || {});',
        'if (![1, 2].includes(geometrySchemaVersion))',
        'geometry = geometryTransferLegacyRenderSpace(geometry);',
        'next = geometryTransferPresentationV2(current, geometry);',
        'presentationTransferred: geometrySchemaVersion >= 2',
    )
    for marker in required:
        assert marker in frontend, marker

    forbidden = (
        'Status LED geometry does not match the current calibration topology.',
        'ports: geometryTransferEntryMap(source.ports),',
        'sfp: geometryTransferEntryMap(source.sfp),',
        'delete ui.faceplate;',
        'delete ui.logo.file;',
        'delete ui.logo.source;',
        'applied.ui.logo.file = current.ui?.logo?.file;',
        'applied.ui.logo.source = current.ui?.logo?.source;',
    )
    for marker in forbidden:
        assert marker not in frontend, marker

    export_start = frontend.index("function geometryTransferExportData")
    export_end = frontend.index("\nfunction geometryTransferImportSource", export_start)
    export_block = frontend[export_start:export_end]
    assert "geometryTransferEntryMap(source.ports)" not in export_block
    assert "geometryTransferEntryMap(source.sfp)" not in export_block
    assert "delete geometryUi.logo" not in export_block

    presentation_start = frontend.index("function geometryTransferPresentationV2(currentCal, geometry)")
    presentation_end = frontend.index("\nfunction applyGeometryTransferData", presentation_start)
    presentation = frontend[presentation_start:presentation_end]
    assert "next.ui.logo.file = current" not in presentation
    assert "next.ui.logo.source = current" not in presentation

    print("Core 2.6.22+ geometry presentation transfer contract: PASS")


if __name__ == "__main__":
    main()
