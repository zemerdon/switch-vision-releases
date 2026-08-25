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
        'data-cv-action="download-geometry"',
        'data-cv-action="import-geometry"',
        "data-cv-geometry-file",
        "geometryTransferExportData(",
        "applyGeometryTransferData(",
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
  return {
    valid: true,
    errors: [],
    warnings: [],
    calibration: ensureCalibrationUi(cloneCalibrationData(raw)),
    summary: {
      model: String(raw.model || "model"),
      width: Number(raw.image?.width || 0),
      height: Number(raw.image?.height || 0),
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
