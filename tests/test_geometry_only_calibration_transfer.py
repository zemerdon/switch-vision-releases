#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "src" / "js" / "switch-vision.js"


def main() -> None:
    frontend = FRONTEND.read_text(encoding="utf-8")
    for marker in (
        'const SV_GEOMETRY_TRANSFER_TYPE = "switch-vision-geometry-profile-v1";',
        'const SV_FACEPLATE_TRANSFER_TYPE = "switch-vision-faceplate-profile-v2";',
        'data-cv-action="download-geometry"',
        'data-cv-action="import-geometry"',
        "data-cv-geometry-file",
        "geometryTransferExportData(",
        "geometryTransferImportSource(",
        "applyGeometryTransferData(",
        "Imported geometry from Switch Vision Faceplate Profile v2",
    ):
        assert marker in frontend, marker

    start = frontend.index('const SV_GEOMETRY_TRANSFER_TYPE = "switch-vision-geometry-profile-v1";')
    end = frontend.index("\nfunction jsonPayloadByteLength", start)
    helper_block = frontend[start:end]

    node = shutil.which("node")
    assert node, "Node.js is required for the geometry transfer behavior regression"

    prefix = r'''
"use strict";
const SV_VERSION = "regression";
function clonePlainData(value) {
  if (value === undefined) return undefined;
  return JSON.parse(JSON.stringify(value));
}
function cloneCalibrationData(value) {
  return ensureCalibrationUi(clonePlainData(value));
}
function ensureCalibrationUi(cal) {
  cal.image = cal.image || {};
  cal.ports = cal.ports || {};
  cal.sfp = cal.sfp || {};
  cal.status_leds = cal.status_leds || {};
  cal.ui = cal.ui || {};
  for (const key of ["logo", "faceplate", "status_panel", "status_panel_2", "calibration_button"]) {
    cal.ui[key] = cal.ui[key] && typeof cal.ui[key] === "object" ? cal.ui[key] : {};
  }
  return cal;
}
function validateImportedCalibration(raw, currentCal = null) {
  const errors = [];
  const warnings = [];
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return { valid: false, errors: ["The imported file must contain one JSON object."], warnings, calibration: null, summary: null };
  }
  for (const key of ["image", "ports", "sfp", "status_leds", "ui"]) {
    if (!raw[key] || typeof raw[key] !== "object" || Array.isArray(raw[key])) errors.push(`Missing or invalid ${key}.`);
  }
  const width = Number(raw.image?.width || 0);
  const height = Number(raw.image?.height || 0);
  if (!(width > 0 && height > 0)) errors.push("Invalid image dimensions.");
  if (errors.length) return { valid: false, errors, warnings, calibration: null, summary: null };
  return {
    valid: true,
    errors,
    warnings,
    calibration: ensureCalibrationUi(cloneCalibrationData(raw)),
    summary: {
      model: String(raw.model || "model"),
      width,
      height,
      portCount: Object.keys(raw.ports || {}).length,
      sfpCount: Object.keys(raw.sfp || {}).length,
      statusCount: Object.keys(raw.status_leds || {}).length
    }
  };
}
'''
    suffix = r'''
const current = {
  model: "MODEL-A",
  image: {file: "target-background.png", master: "target-master", width: 2048, height: 448},
  ports: {
    "1": {
      center: [10, 20], number: [10, 5], led_left: [8, 15], led_right: [12, 15],
      hitbox: [30, 40], led_left_size: [5, 6], led_right_size: [7, 8],
      display_name: "Keep me", number_show: false
    }
  },
  sfp: {
    "G1": {center: [100, 20], label: [100, 5], hitbox: [40, 20], display_name: "Keep SFP", label_show: false}
  },
  status_leds: {STAT: [200, 20]},
  ui: {
    logo: {show: false, file: "target-logo.svg", source: "custom", x: 1, y: 2, width: 30, height: 40},
    faceplate: {show: true, file: "target-faceplate.png", source: "custom", fit: "contain", opacity: 0.7},
    status_panel: {show: false, x: 3, y: 4, width: 300, height: 100, font_size: 19, fields: {row1_key: [10, 10]}},
    status_panel_2: {show: true, x: 5, y: 6, width: 200, height: 90, font_size: 17, fields: {row1_value: [20, 10]}},
    calibration_button: {show: false, x: 7, y: 8, width: 90, height: 25, anchor: "top_right"}
  },
  stack: {enabled: true},
  management: {switch_ip: "192.0.2.1"},
  profile: "target-profile"
};

const malicious = {
  transfer_type: SV_GEOMETRY_TRANSFER_TYPE,
  schema_version: 1,
  geometry: {
    image: {width: 1024, height: 224, file: "foreign-background.png", master: "foreign-master"},
    ports: {
      "1": {
        center: [110, 120], number: [110, 105], led_left: [108, 115], led_right: [112, 115],
        hitbox: [31, 41], led_left_size: [9, 10], led_right_size: [11, 12],
        display_name: "FOREIGN", number_show: true
      }
    },
    sfp: {
      "G1": {center: [300, 120], label: [300, 105], hitbox: [41, 21], file: "foreign-sfp.png", label_show: true}
    },
    status_leds: {STAT: [400, 120]},
    ui: {
      logo: {x: 21, y: 22, width: 31, height: 41, file: "foreign-logo.svg", source: "default", show: true},
      faceplate: {file: "foreign-faceplate.png", source: "default", fit: "cover", opacity: 1},
      status_panel: {x: 23, y: 24, width: 301, height: 101, font_size: 99, show: true, fields: {row1_key: [30, 30]}},
      status_panel_2: {x: 25, y: 26, width: 201, height: 91, font_size: 98, show: false, fields: {row1_value: [40, 30]}},
      calibration_button: {x: 27, y: 28, width: 91, height: 26, anchor: "bottom_left", show: true}
    }
  }
};

const result = applyGeometryTransferData(current, malicious);
if (!result.valid) throw new Error(JSON.stringify(result.errors));
const applied = result.calibration;

const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const assert = (condition, message) => { if (!condition) throw new Error(message); };

assert(applied.image.file === current.image.file, "image.file changed");
assert(applied.image.master === current.image.master, "image.master changed");
assert(applied.ui.faceplate.file === current.ui.faceplate.file, "faceplate file changed");
assert(applied.ui.faceplate.source === current.ui.faceplate.source, "faceplate source changed");
assert(applied.ui.logo.file === current.ui.logo.file, "logo file changed");
assert(applied.ui.logo.source === current.ui.logo.source, "logo source changed");
assert(applied.ui.faceplate.fit === current.ui.faceplate.fit, "faceplate fit changed");
assert(applied.ui.faceplate.opacity === current.ui.faceplate.opacity, "faceplate opacity changed");
assert(applied.ui.logo.show === current.ui.logo.show, "logo visibility changed");
assert(applied.ui.status_panel.show === current.ui.status_panel.show, "status panel visibility changed");
assert(applied.ui.status_panel.font_size === current.ui.status_panel.font_size, "status panel style changed");
assert(applied.ports["1"].display_name === "Keep me", "port display name changed");
assert(applied.ports["1"].number_show === false, "port number visibility changed");
assert(applied.sfp.G1.display_name === "Keep SFP", "SFP display name changed");
assert(applied.sfp.G1.label_show === false, "SFP label visibility changed");

assert(same(applied.ports["1"].center, [110, 120]), "port geometry not applied");
assert(same(applied.sfp.G1.center, [300, 120]), "SFP geometry not applied");
assert(same(applied.status_leds.STAT, [400, 120]), "status LED geometry not applied");
assert(applied.ui.logo.x === 21 && applied.ui.logo.y === 22, "logo geometry not applied");
assert(applied.ui.status_panel.x === 23 && same(applied.ui.status_panel.fields.row1_key, [30, 30]), "status panel geometry not applied");
assert(applied.ui.calibration_button.anchor === "bottom_left", "button anchor geometry not applied");
assert(applied.image.width === 1024 && applied.image.height === 224, "canvas geometry not applied");

const exported = geometryTransferExportData(current, {
  scope: "custom",
  baseProfile: "custom_sw1",
  profile: "custom_sw1__faceplate__target-faceplate.png"
});
assert(exported.transfer_type === SV_GEOMETRY_TRANSFER_TYPE, "wrong transfer type");
assert(!("file" in exported.geometry.image), "export leaked image.file");
assert(!("master" in exported.geometry.image), "export leaked image.master");
assert(!("file" in exported.geometry.ui.logo), "export leaked logo.file");
assert(!("source" in exported.geometry.ui.logo), "export leaked logo.source");
assert(!("faceplate" in exported.geometry.ui), "export included faceplate artwork block");
assert(exported.geometry.image.width === 2048 && exported.geometry.image.height === 448, "strict-mode export lost canvas dimensions");
assert(same(exported.geometry.status_leds.STAT, [200, 20]), "strict-mode export corrupted status LED coordinates");
assert(!("ui" in exported.geometry.ui.status_panel.fields), "geometry export polluted status-panel fields with calibration UI data");
assert(!("stack" in exported.geometry.ui.status_panel.fields), "geometry export polluted status-panel fields with calibration stack data");
assert(!("management" in exported.geometry.ui.status_panel.fields), "geometry export polluted status-panel fields with calibration management data");

const roundTrip = applyGeometryTransferData(current, exported);
assert(roundTrip.valid === true, "exported geometry could not be imported back into the same calibration");
assert(same(roundTrip.calibration.ui.faceplate, current.ui.faceplate), "geometry round-trip polluted or changed faceplate presentation");
assert(same(roundTrip.calibration.status_leds.STAT, [200, 20]), "geometry round-trip polluted status LED coordinates");
assert(Object.keys(roundTrip.calibration.status_leds.STAT).every((key) => key === "0" || key === "1"), "geometry round-trip added non-coordinate properties to a status LED");

const mismatch = cloneCalibrationData(malicious);
mismatch.geometry.ports["2"] = cloneCalibrationData(mismatch.geometry.ports["1"]);
const rejected = applyGeometryTransferData(current, mismatch);
assert(rejected.valid === false, "topology mismatch was accepted");


const legacyFaceplate = clonePlainData(current);
legacyFaceplate.schema_version = 2;
legacyFaceplate.transfer_type = SV_FACEPLATE_TRANSFER_TYPE;
legacyFaceplate.generated_by = "Switch Vision v2.6.8";
legacyFaceplate.source_scope = "custom";
legacyFaceplate.source_profile = "legacy-profile";
legacyFaceplate.source_base_profile = "legacy-base";
legacyFaceplate.required_faceplate = "legacy-faceplate.png";
legacyFaceplate.image = {
  ...legacyFaceplate.image,
  width: 1024,
  height: 224,
  file: "foreign-background.png",
  master: "foreign-master"
};
legacyFaceplate.ports["1"] = { ...legacyFaceplate.ports["1"], ...clonePlainData(malicious.geometry.ports["1"]) };
legacyFaceplate.sfp.G1 = { ...legacyFaceplate.sfp.G1, ...clonePlainData(malicious.geometry.sfp.G1) };
legacyFaceplate.status_leds = clonePlainData(malicious.geometry.status_leds);
legacyFaceplate.ui.logo = { ...legacyFaceplate.ui.logo, ...clonePlainData(malicious.geometry.ui.logo) };
legacyFaceplate.ui.faceplate = { ...legacyFaceplate.ui.faceplate, ...clonePlainData(malicious.geometry.ui.faceplate) };
legacyFaceplate.ui.status_panel = { ...legacyFaceplate.ui.status_panel, ...clonePlainData(malicious.geometry.ui.status_panel) };
legacyFaceplate.ui.status_panel_2 = { ...legacyFaceplate.ui.status_panel_2, ...clonePlainData(malicious.geometry.ui.status_panel_2) };
legacyFaceplate.ui.calibration_button = { ...legacyFaceplate.ui.calibration_button, ...clonePlainData(malicious.geometry.ui.calibration_button) };
legacyFaceplate.management = {switch_ip: "203.0.113.9"};
legacyFaceplate.stack = {enabled: false, members: {}};
legacyFaceplate.profile = "foreign-profile";

const legacyResult = applyGeometryTransferData(current, legacyFaceplate);
if (!legacyResult.valid) throw new Error(JSON.stringify(legacyResult.errors));
const legacyApplied = legacyResult.calibration;
assert(legacyResult.summary?.sourceTransferType === SV_FACEPLATE_TRANSFER_TYPE, "Faceplate Profile v2 source type not reported");
assert(legacyResult.summary?.convertedFromFaceplateProfileV2 === true, "Faceplate Profile v2 conversion marker missing");
assert(legacyApplied.image.width === 1024 && legacyApplied.image.height === 224, "Faceplate Profile v2 canvas geometry not applied");
assert(same(legacyApplied.ports["1"].center, [110, 120]), "Faceplate Profile v2 port geometry not applied");
assert(same(legacyApplied.sfp.G1.center, [300, 120]), "Faceplate Profile v2 SFP geometry not applied");
assert(same(legacyApplied.status_leds.STAT, [400, 120]), "Faceplate Profile v2 status LED geometry not applied");
assert(legacyApplied.ui.logo.x === 21 && legacyApplied.ui.logo.y === 22, "Faceplate Profile v2 logo geometry not applied");
assert(legacyApplied.ui.status_panel.x === 23 && same(legacyApplied.ui.status_panel.fields.row1_key, [30, 30]), "Faceplate Profile v2 status panel geometry not applied");
assert(legacyApplied.ui.status_panel_2.x === 25 && same(legacyApplied.ui.status_panel_2.fields.row1_value, [40, 30]), "Faceplate Profile v2 second status panel geometry not applied");
assert(legacyApplied.ui.calibration_button.anchor === "bottom_left", "Faceplate Profile v2 calibration button geometry not applied");

assert(legacyApplied.image.file === current.image.file && legacyApplied.image.master === current.image.master, "Faceplate Profile v2 changed image identity");
assert(legacyApplied.management.switch_ip === current.management.switch_ip, "Faceplate Profile v2 changed management IP");
assert(same(legacyApplied.stack, current.stack), "Faceplate Profile v2 changed stack configuration");
assert(legacyApplied.profile === current.profile, "Faceplate Profile v2 changed profile destination");
assert(same(legacyApplied.ui.faceplate, current.ui.faceplate), "Faceplate Profile v2 changed faceplate appearance/source");
assert(legacyApplied.ui.logo.file === current.ui.logo.file && legacyApplied.ui.logo.source === current.ui.logo.source && legacyApplied.ui.logo.show === current.ui.logo.show, "Faceplate Profile v2 changed logo appearance/source");
assert(legacyApplied.ui.status_panel.show === current.ui.status_panel.show && legacyApplied.ui.status_panel.font_size === current.ui.status_panel.font_size, "Faceplate Profile v2 changed status panel appearance");
assert(legacyApplied.ports["1"].display_name === current.ports["1"].display_name && legacyApplied.ports["1"].number_show === current.ports["1"].number_show, "Faceplate Profile v2 changed port non-geometry configuration");
assert(legacyApplied.sfp.G1.display_name === current.sfp.G1.display_name && legacyApplied.sfp.G1.label_show === current.sfp.G1.label_show, "Faceplate Profile v2 changed SFP non-geometry configuration");

const nativeSourceResult = applyGeometryTransferData(current, exported);
assert(nativeSourceResult.valid === true, "native geometry transfer behavior regressed");
assert(nativeSourceResult.summary?.sourceTransferType === SV_GEOMETRY_TRANSFER_TYPE, "native geometry source type changed");
assert(nativeSourceResult.summary?.convertedFromFaceplateProfileV2 === false, "native geometry was incorrectly marked converted");

const unknownTransfer = clonePlainData(legacyFaceplate);
unknownTransfer.transfer_type = "unknown-transfer-type";
const unknownTransferResult = applyGeometryTransferData(current, unknownTransfer);
assert(unknownTransferResult.valid === false, "unknown transfer_type was accepted");

const wrongFaceplateSchema = clonePlainData(legacyFaceplate);
wrongFaceplateSchema.schema_version = 3;
const wrongFaceplateSchemaResult = applyGeometryTransferData(current, wrongFaceplateSchema);
assert(wrongFaceplateSchemaResult.valid === false, "unsupported Faceplate Profile schema was accepted");
assert(wrongFaceplateSchemaResult.errors.some((value) => String(value).includes("schema_version")), "unsupported Faceplate Profile schema did not report schema_version");

const malformedFaceplate = clonePlainData(legacyFaceplate);
delete malformedFaceplate.ports;
const malformedFaceplateResult = applyGeometryTransferData(current, malformedFaceplate);
assert(malformedFaceplateResult.valid === false, "malformed Faceplate Profile v2 was accepted");

console.log("Core geometry-only calibration transfer: PASS");
'''

    script = prefix + helper_block + suffix
    with tempfile.TemporaryDirectory() as td:
        script_path = Path(td) / "geometry-transfer-regression.js"
        script_path.write_text(script, encoding="utf-8")
        result = subprocess.run(
            [node, str(script_path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    assert "Core geometry-only calibration transfer: PASS" in result.stdout
    print("Core geometry-only calibration transfer: PASS")


if __name__ == "__main__":
    main()
