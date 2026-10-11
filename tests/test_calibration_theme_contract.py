#!/usr/bin/env python3
"""Calibration-only dual-viewport theme contract and safety regressions."""
import ast
import json
import subprocess
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "src/custom_components/switch_vision/__init__.py"
CARD = ROOT / "src/js/switch-vision.js"


class CalibrationThemeContracts(unittest.TestCase):
    def test_backend_rejects_invalid_styles_without_touching_profiles(self):
        tree = ast.parse(BACKEND.read_text())
        allowed = ("CALIBRATION_THEME_SECTIONS", "CALIBRATION_THEME_FIELDS", "CALIBRATION_THEME_FIELD_LIMITS")
        exprs = [n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in allowed for t in n.targets)]
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_normalise_calibration_theme")
        class Vol:
            Invalid = ValueError
        namespace = {"vol": Vol, "Any": Any}
        exec(compile(ast.Module(body=exprs + [fn], type_ignores=[]), str(BACKEND), "exec"), namespace)
        norm = namespace["_normalise_calibration_theme"]
        theme = {"desktop":{"global":{"font_size":13,"font_weight":"bold","padding_horizontal":8,"padding_vertical":2,"gap":5},"assets":{"font_size":11,"font_weight":"regular","padding":3}},
                 "mobile":{"dropdown_open":{"font_size":14,"row_height":40,"max_height":300}}}
        self.assertEqual(norm(theme), theme)
        self.assertEqual(norm({}), {"desktop":{}, "mobile":{}})
        for invalid in (
            {"desktop":{"assets":{"font_size":999}}},
            {"desktop":{"assets":{"font_size":True}}},
            {"desktop":{"assets":{"font_weight":"900!important"}}},
            {"desktop":{"unknown":{"font_size":11}}},
            {"tablet":{}}, {"mobile":{"assets":{"geometry":[1,2]}}},
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                norm(invalid)
        text = BACKEND.read_text()
        self.assertIn('CONF_CALIBRATION_THEME = "calibration_theme"', text)
        self.assertIn('"calibration_theme": (CONF_CALIBRATION_THEME,)', text)
        self.assertIn('domain_state[CONF_CALIBRATION_THEME]', text)
        self.assertNotIn("calibration_theme", (ROOT / "src/calibration/calibration.json").read_text() if (ROOT / "src/calibration/calibration.json").exists() else "")

    def test_css_only_targets_editor_and_switches_at_mobile_breakpoint(self):
        src = CARD.read_text()
        start = src.index('const SV_CALIBRATION_MOBILE_MEDIA = ')
        end = src.index('const SV_CALIBRATION_TRANSIENT_CONFIG_KEYS', start)
        fragment = src[start:end]
        js = ("const assert=require('node:assert/strict');\n" + fragment +
              "\nconst css=calibrationThemeCss({desktop:{assets:{font_size:11,font_weight:'bold',padding_horizontal:8,padding_vertical:2},dropdown_open:{row_height:32,max_height:350}},mobile:{assets:{font_size:14},dropdown_open:{row_height:42}}});" +
              "\nassert.match(css,/@media \\(min-width:761px\\)/);assert.match(css,/@media \\(max-width:760px\\)/);" +
              "\nassert.match(css,/font-size:11px!important/);assert.match(css,/font-size:14px!important/);" +
              "\nassert.match(css,/min-height:42px!important/);" +
              "\nassert.match(css,/padding-inline:8px!important/);assert.match(css,/padding-block:2px!important/);" +
              "\nassert.doesNotMatch(css,/\\.cv-stage|\\.cv-svg|\\.cv-faceplate-canvas/);" +
              "\nassert.deepEqual(normalizeCalibrationTheme({mobile:{assets:{font_size:999,padding:5}}}).mobile.assets,{padding:5});")
        proc = subprocess.run(["node", "-e", js], cwd=ROOT, text=True, capture_output=True, timeout=20)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertIn('calibrationControlsEnabled(this.config) ?', src)
        self.assertIn("calibration_theme: event?.data?.calibration_theme", src)
        self.assertIn('select.dispatchEvent(new Event("change", { bubbles: true }))', src)


    def test_global_controls_override_legacy_sections_only_in_calibration(self):
        source = CARD.read_text()
        start = source.index("const SV_CALIBRATION_MOBILE_MEDIA = ")
        end = source.index("const SV_CALIBRATION_TRANSIENT_CONFIG_KEYS", start)
        fragment = source[start:end]
        script = ("const assert=require('node:assert/strict');" + fragment +
                  "\nconst stored={desktop:{assets:{font_size:11,padding:6,font_weight:'regular'},global:{font_size:13,font_weight:'bold',padding_horizontal:7,padding_vertical:3,gap:5},dropdown_open:{row_height:42}},mobile:{global:{font_size:15,padding_horizontal:4,padding_vertical:2,gap:2}}};" +
                  "\nassert.deepEqual(normalizeCalibrationTheme(stored),stored);" +
                  "\nconst css=calibrationThemeCss(stored);" +
                  "\nassert.match(css,/font-size:13px!important/);assert.match(css,/font-size:15px!important/);" +
                  "\nassert.doesNotMatch(css,/font-size:11px!important/);assert.doesNotMatch(css,/padding:6px!important/);" +
                  "\nassert.match(css,/padding-inline:7px!important/);assert.match(css,/padding-block:3px!important/);" +
                  "\nassert.match(css,/\\.cv-cal-tools \\.cv-cal-tools-row button/);" +
                  "\nassert.match(css,/\\.cv-cal-option-menu-item/);" +
                  "\nassert.match(css,/min-height:42px!important/);" +
                  "\nassert.doesNotMatch(css,/\\.cv-faceplate-canvas|\\.cv-stage|\\.cv-svg/);" +
                  "\nassert.equal(normalizeCalibrationTheme({desktop:{global:{font_size:999}}}).desktop.global,undefined);")
        result = subprocess.run(["node", "-e", script], cwd=ROOT, text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
