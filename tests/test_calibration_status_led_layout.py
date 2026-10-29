from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"
MIRROR = ROOT / "src" / "js" / "switch-vision.js"
CALIBRATION = ROOT / "src" / "calibration"

FACTORY_PROFILES_WITH_VISIBLE_STATUS_LEDS = (
    "faceplate-c3560cg-8pc-s.json",
    "faceplate-stock-24rj45-2sfp.json",
    "faceplate-stock-24rj45-4sfp.json",
    "faceplate-submarine-48rj45-4sfp.json",
)


class CalibrationStatusLedLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = CARD.read_text(encoding="utf-8")

    def test_card_sources_remain_exact_mirrors(self) -> None:
        self.assertEqual(CARD.read_bytes(), MIRROR.read_bytes())

    def test_led_shapes_follow_thickness_in_one_responsive_row(self) -> None:
        start = self.source.index('<details class="cv-cal-section" data-cv-section="labels-leds"')
        end = self.source.index('data-cv-section="status-boxes"', start)
        section = self.source[start:end]
        self.assertLess(section.index('cv-cal-status-led-visibility'), section.index('cv-cal-port-led-shape'))
        self.assertLess(section.index('cv-cal-port-led-shape'), section.index('cv-cal-led-outline-row'))
        self.assertLess(section.index('cv-cal-led-outline-row'), section.index('cv-cal-port-label-style'))
        outline = section[section.index('cv-cal-led-outline-row'):section.index('cv-cal-port-label-style')]
        self.assertLess(outline.index('data-cv-field="led-outline-thickness"'), outline.index('${selectedPortLedControls}'))
        self.assertNotIn('Off by default.', section)
        self.assertNotIn('portPresentationControls', self.source)
        for marker in ('>Link LED Shape', 'data-cv-field="link-led-shape"',
                       '>Activity LED Shape', 'data-cv-field="activity-led-shape"',
                       '>PoE LED Shape', 'data-cv-field="poe-led-shape"'):
            self.assertIn(marker, self.source)

        css = (ROOT / 'src' / 'css' / 'switch-vision.css').read_text(encoding='utf-8')
        self.assertIn('.cv-cal-led-outline-row > .cv-cal-led-shape-label', css)
        self.assertNotIn('.cv-cal-led-outline-row{overflow-x:auto', css)

    def test_factory_defaults_follow_authoritative_status_led_visibility(self) -> None:
        self.assertIn(
            'status_leds: { hidden: [], text_color: "#eef7ff"',
            self.source,
        )
        self.assertNotIn(
            'statusLedVisibilityExplicit = Array.isArray(cal.ui?.status_leds?.hidden);',
            self.source,
        )
        self.assertIn(
            'cal.ui.status_leds.hidden = [...new Set((Array.isArray(cal.ui.status_leds.hidden) ? cal.ui.status_leds.hidden : []).map((name) => String(name)))];',
            self.source,
        )

        for name in FACTORY_PROFILES_WITH_VISIBLE_STATUS_LEDS:
            profile = json.loads((CALIBRATION / name).read_text(encoding="utf-8"))
            self.assertEqual(
                profile["ui"]["status_leds"]["hidden"],
                [],
                f"{name} must retain its factory Status LED presentation",
            )

        # This owner-supplied stock revision deliberately hides the seven
        # factory indicators. Preserve the supplied selection byte-for-byte.
        for suffix in ("2sfp", "4sfp"):
            stock = json.loads(
                (CALIBRATION / f"faceplate-stock-48rj45-{suffix}.json").read_text(encoding="utf-8")
            )
            owner = json.loads(
                (CALIBRATION / f"geometry-stock-48rj45-{suffix}-compact.json").read_text(
                    encoding="utf-8"
                )
            )["geometry"]
            self.assertEqual(
                stock["ui"]["status_leds"]["hidden"], owner["ui"]["status_leds"]["hidden"]
            )
            self.assertEqual(
                set(stock["ui"]["status_leds"]["hidden"]), set(stock["status_leds"])
            )

    def test_new_calibration_session_starts_with_all_status_leds_removed(self) -> None:
        helper_start = self.source.index("function applyNewCalibrationStatusLedDefaults")
        helper_end = self.source.index("let activeCalibrationUiRenderPass", helper_start)
        helper = self.source[helper_start:helper_end]
        self.assertIn("next.ui.status_leds.added = [];", helper)
        self.assertNotIn("next.ui.status_leds.hidden = [];", helper)
        self.assertIn("delete next.ui.status_leds.membership_edited;", helper)

        opening = self.source[
            self.source.index("attachCalibrationButtonHandler()"):
            self.source.index("      this.config = {", self.source.index("attachCalibrationButtonHandler()"))
        ]
        self.assertIn("info.exists !== true", opening)
        self.assertIn("info.invalid !== true", opening)
        self.assertIn("!this._profileLoadError", opening)
        self.assertIn(
            "if (openingNewCalibration) applyNewCalibrationStatusLedDefaults(this._calibrationWorking);",
            opening,
        )
        self.assertIn("applyNewCalibrationStatusLedDefaults(starter);", self.source)
        self.assertIn("return applyNewCalibrationStatusLedDefaults(next);", self.source)

        picker = self.source[
            self.source.index("const statusLedNames = calibrationStatusLedNames(cal);"):
            self.source.index("const customFontValue", self.source.index("const statusLedNames = calibrationStatusLedNames(cal);"))
        ]
        self.assertIn("const statusLedOptionsHtml", picker)
        self.assertIn(' (removed)', picker)
        for marker in (
            'data-cv-field="status-led-selected"',
            'data-cv-action="show-status-led"',
            'data-cv-action="hide-status-led"',
            'data-cv-action="add-status-led"',
            'data-cv-action="remove-status-led"',
        ):
            self.assertIn(marker, self.source)
        self.assertNotIn('data-cv-status-led=', self.source)

    def test_existing_saved_status_led_visibility_and_membership_remain_authoritative(self) -> None:
        opening = self.source[
            self.source.index("attachCalibrationButtonHandler()"):
            self.source.index("      this.config = {", self.source.index("attachCalibrationButtonHandler()"))
        ]
        self.assertIn("const openingNewCalibration = Boolean(", opening)
        self.assertNotIn("applyNewCalibrationStatusLedDefaults(this._profileCalibration)", opening)

        ensure = self.source[
            self.source.index("function ensureCalibrationUi(cal)"):
            self.source.index("function calibrationStatusLedNames", self.source.index("function ensureCalibrationUi(cal)"))
        ]
        self.assertIn("Array.isArray(cal.ui.status_leds.hidden) ? cal.ui.status_leds.hidden : []", ensure)
        self.assertIn("if (Array.isArray(cal.ui.status_leds.added))", ensure)
        self.assertIn("delete cal.ui.status_leds.added;", ensure)

        helper = self.source[
            self.source.index("function calibrationStatusLedIsAdded"):
            self.source.index("function setCalibrationStatusLedAdded")
        ]
        self.assertIn("if (!Array.isArray(added)) return true;", helper)
        self.assertIn("Saved legacy profiles retain their original LEDs", helper)

    def test_show_hide_all_buttons_follow_status_led_text_colour(self) -> None:
        start = self.source.index('<details class="cv-cal-section" data-cv-section="labels-leds"')
        end = self.source.index('data-cv-section="status-boxes"', start)
        html = self.source[start:end]
        colour = html.index('customColourControlsHtml("status-led-text-color"')
        show = html.index('data-cv-action="show-all-status-leds"')
        hide = html.index('data-cv-action="hide-all-status-leds"')
        port = html.index('cv-cal-port-led-shape')
        self.assertLess(colour, show)
        self.assertLess(show, hide)
        self.assertLess(hide, port)
        self.assertIn('Object.keys(cal.status_leds || {}).length ? "" : "disabled"', html)
        self.assertNotIn('data-cv-action="show-all-status-leds"', self.source[:start])

    def test_dropdown_membership_and_visibility_are_independent_and_reversible(self) -> None:
        helper = self.source[
            self.source.index("function calibrationStatusLedNames"):
            self.source.index("let activeCalibrationUiRenderPass")
        ]
        js = "const ensureCalibrationUi = (cal) => cal;\n" + helper + """
const assert = require("assert");
const old = {
  status_leds: { MODE:[1,2], STAT:[3,4], PoE:[5,6] },
  ui: { status_leds: { hidden:["PoE"], text_color:"#ff00ff", font_size:17 } },
  ports: { "1":{ center:[10,20] } }
};
const originalPorts = JSON.stringify(old.ports);
assert.strictEqual(calibrationStatusLedIsAdded(old, "STAT"), true);
assert.strictEqual(calibrationStatusLedIsAdded(old, "PoE"), true);
setAllCalibrationStatusLedsVisible(old, false);
assert.deepStrictEqual(old.ui.status_leds.hidden, ["MODE", "STAT", "PoE"]);
setAllCalibrationStatusLedsVisible(old, true);
assert.deepStrictEqual(old.ui.status_leds.hidden, []);
assert.strictEqual(old.ui.status_leds.text_color, "#ff00ff");
assert.strictEqual(JSON.stringify(old.ports), originalPorts);
assert.strictEqual("added" in old.ui.status_leds, false);

const fresh = JSON.parse(JSON.stringify(old));
applyNewCalibrationStatusLedDefaults(fresh);
assert.deepStrictEqual(fresh.ui.status_leds.added, []);
assert.deepStrictEqual(fresh.ui.status_leds.hidden, []);
assert.strictEqual(calibrationStatusLedIsAdded(fresh, "STAT"), false);
assert.strictEqual(setCalibrationStatusLedVisible(fresh, "STAT", true), false);
assert.strictEqual(setCalibrationStatusLedAdded(fresh, "STAT", true), true);
assert.deepStrictEqual(fresh.ui.status_leds.added, ["STAT"]);
assert.deepStrictEqual(fresh.ui.status_leds.hidden, []);
assert.strictEqual(setCalibrationStatusLedVisible(fresh, "STAT", false), true);
assert.deepStrictEqual(fresh.ui.status_leds.hidden, ["STAT"]);
setAllCalibrationStatusLedsVisible(fresh, true);
assert.deepStrictEqual(fresh.ui.status_leds.added, ["STAT"]);
assert.deepStrictEqual(fresh.ui.status_leds.hidden, []);
assert.strictEqual(setCalibrationStatusLedAdded(fresh, "STAT", false), true);
assert.deepStrictEqual(fresh.ui.status_leds.added, []);
assert.deepStrictEqual(fresh.status_leds.STAT, [3,4]);
assert.strictEqual(setCalibrationStatusLedAdded(fresh, "MISSING", true), false);
assert.strictEqual(JSON.stringify(fresh.ports), originalPorts);
"""
        result = subprocess.run(["node", "-e", js], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_stock_faceplates_survive_empty_editor_and_legacy_auto_hidden_profiles(self) -> None:
        helper = self.source[
            self.source.index("function calibrationStatusLedNames"):
            self.source.index("let activeCalibrationUiRenderPass")
        ]
        renderer = self.source[
            self.source.index("function statusLedIsHidden"):
            self.source.index("function drawPanel", self.source.index("function statusLedIsHidden"))
        ]
        js = "const ensureCalibrationUi = (cal) => cal;\nconst uiFromCalibration = (cal) => cal.ui;\nconst faceplateFactoryCalibrationForFile = () => ({ ui: { status_leds: { hidden: [] } } });\n" + helper + renderer + """
const assert = require("assert");
const profile = {
  status_leds: { MODE:[1,2], STAT:[3,4], PoE:[5,6] },
  ui: { status_leds: { hidden: [] } }
};
for (const name of Object.keys(profile.status_leds)) {
  assert.strictEqual(statusLedIsHidden(profile, name), false);
}
applyNewCalibrationStatusLedDefaults(profile);
assert.deepStrictEqual(profile.ui.status_leds.added, []);
assert.deepStrictEqual(profile.ui.status_leds.hidden, []);
for (const name of Object.keys(profile.status_leds)) {
  assert.strictEqual(statusLedIsHidden(profile, name), false);
}

// A starter automatically saved by 2.8.16–2.8.18 must still display stock LEDs.
const oldStarter = structuredClone(profile);
oldStarter.ui.status_leds.hidden = ["MODE", "STAT", "PoE"];
for (const name of Object.keys(oldStarter.status_leds)) {
  assert.strictEqual(statusLedIsHidden(oldStarter, name), false);
}
assert.deepStrictEqual(oldStarter.ui.status_leds.hidden, ["MODE", "STAT", "PoE"]);

// Pre-existing explicit visibility choices remain effective.
const oldCustom = structuredClone(profile);
delete oldCustom.ui.status_leds.added;
oldCustom.ui.status_leds.hidden = ["PoE"];
assert.strictEqual(statusLedIsHidden(oldCustom, "STAT"), false);
assert.strictEqual(statusLedIsHidden(oldCustom, "PoE"), true);

// Existing profiles with deliberately added LEDs retain their membership.
oldCustom.ui.status_leds.added = ["STAT"];
assert.strictEqual(statusLedIsHidden(oldCustom, "STAT"), false);
assert.strictEqual(statusLedIsHidden(oldCustom, "PoE"), true);
assert.strictEqual(statusLedIsHidden(oldCustom, "MODE"), false);

// New deliberate Add/Hide/Remove actions explicitly override the stock view.
setCalibrationStatusLedAdded(profile, "STAT", true);
assert.strictEqual(profile.ui.status_leds.membership_edited, true);
assert.strictEqual(statusLedIsHidden(profile, "STAT"), false);
assert.strictEqual(statusLedIsHidden(profile, "PoE"), true);
assert.strictEqual(statusLedIsHidden(profile, "MODE"), false);
setCalibrationStatusLedVisible(profile, "STAT", false);
assert.strictEqual(statusLedIsHidden(profile, "STAT"), true);
setCalibrationStatusLedVisible(profile, "STAT", true);
assert.strictEqual(statusLedIsHidden(profile, "STAT"), false);
setCalibrationStatusLedAdded(profile, "STAT", false);
assert.strictEqual(statusLedIsHidden(profile, "STAT"), true);
assert.strictEqual(statusLedIsHidden(profile, "MODE"), false);
applyNewCalibrationStatusLedDefaults(profile);
assert.strictEqual("membership_edited" in profile.ui.status_leds, false);
assert.strictEqual(statusLedIsHidden(profile, "STAT"), false);
"""
        result = subprocess.run(["node", "-e", js], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("if (statusLedIsHidden(calibration, name)) continue;", self.source)

    def test_all_bundled_faceplates_honour_factory_led_visibility(self) -> None:
        # Exercise actual authored JSON: the old stock-only regression missed
        # the deliberately hidden LEDs on dedicated model faceplates.
        factories = {}
        cases = []
        for path in sorted(CALIBRATION.glob("faceplate-*.json")):
            factory = json.loads(path.read_text(encoding="utf-8"))
            filename = Path(factory["image"]["file"]).name
            names = list(factory.get("status_leds", {}))
            hidden = list(factory.get("ui", {}).get("status_leds", {}).get("hidden", []))
            factories[filename] = {"ui": {"status_leds": {"hidden": hidden}}}
            cases.append({"file": filename, "names": names, "hidden": hidden})
        self.assertGreaterEqual(len(cases), 27)
        self.assertTrue(any(case["hidden"] for case in cases))
        self.assertTrue(any(case["names"] and not case["hidden"] for case in cases))

        helper = self.source[
            self.source.index("function calibrationStatusLedNames"):
            self.source.index("let activeCalibrationUiRenderPass")
        ]
        renderer = self.source[
            self.source.index("function statusLedIsHidden"):
            self.source.index("function drawPanel", self.source.index("function statusLedIsHidden"))
        ]
        js = (
            "const ensureCalibrationUi = (cal) => cal;\n"
            "const uiFromCalibration = (cal) => cal.ui;\n"
            "const factories = " + json.dumps(factories) + ";\n"
            "const cases = " + json.dumps(cases) + ";\n"
            "const faceplateFactoryCalibrationForFile = (file) => "
            "factories[String(file || '').split('/').pop()] || null;\n"
            + helper + renderer + """
const assert = require("assert");
for (const fixture of cases) {
  const coordinates = Object.fromEntries(fixture.names.map((name) => [name, [10, 20]]));
  const expectedHidden = new Set(fixture.hidden.map((name) => name.toUpperCase()));
  const factory = {
    image: { file: "faceplates/" + fixture.file },
    status_leds: coordinates,
    ui: { status_leds: { hidden: [...fixture.hidden] } }
  };

  // Opening Calibration must keep each faceplate's authored visibility.
  applyNewCalibrationStatusLedDefaults(factory);
  assert.deepStrictEqual(factory.ui.status_leds.added, []);
  assert.deepStrictEqual(factory.ui.status_leds.hidden, fixture.hidden, fixture.file);
  for (const name of fixture.names) {
    assert.strictEqual(statusLedIsHidden(factory, name),
      expectedHidden.has(name.toUpperCase()), "new: " + fixture.file + " " + name);
  }

  // Repair already-saved 2.8.19 starters whose hidden array was cleared.
  const clearedStarter = structuredClone(factory);
  clearedStarter.ui.status_leds.hidden = [];
  for (const name of fixture.names) {
    assert.strictEqual(statusLedIsHidden(clearedStarter, name),
      expectedHidden.has(name.toUpperCase()), "2.8.19: " + fixture.file + " " + name);
  }

  // Repair older auto-hidden starters without hiding the intended stock LEDs.
  const oldStarter = structuredClone(factory);
  oldStarter.ui.status_leds.hidden = [...fixture.names];
  for (const name of fixture.names) {
    assert.strictEqual(statusLedIsHidden(oldStarter, name),
      expectedHidden.has(name.toUpperCase()), "2.8.16: " + fixture.file + " " + name);
  }

  // Deliberate saved visibility overrides must remain authoritative.
  const explicitVisible = structuredClone(factory);
  delete explicitVisible.ui.status_leds.added;
  explicitVisible.ui.status_leds.hidden = [];
  for (const name of fixture.names) {
    assert.strictEqual(statusLedIsHidden(explicitVisible, name), false,
      "saved show: " + fixture.file + " " + name);
  }
  const explicitHidden = structuredClone(factory);
  delete explicitHidden.ui.status_leds.added;
  explicitHidden.ui.status_leds.hidden = [...fixture.names];
  for (const name of fixture.names) {
    assert.strictEqual(statusLedIsHidden(explicitHidden, name), true,
      "saved hide: " + fixture.file + " " + name);
  }

  // A deliberate Add must override even a factory-hidden indicator.
  if (fixture.names.length) {
    const edited = structuredClone(factory);
    const selected = fixture.names[0];
    assert.strictEqual(setCalibrationStatusLedAdded(edited, selected, true), true);
    assert.strictEqual(statusLedIsHidden(edited, selected), false,
      "manual add: " + fixture.file);
    for (const name of fixture.names.slice(1)) {
      assert.strictEqual(statusLedIsHidden(edited, name), true,
        "manual membership: " + fixture.file + " " + name);
    }
  }
}
// Unknown/custom artwork has no stock authority: do not auto-revive an
// explicitly hidden LED under the old starter signature.
const unknown = {
  image: { file: "faceplates/custom-owner.png" },
  status_leds: { STAT: [10, 20] },
  ui: { status_leds: { added: [], hidden: ["STAT"] } }
};
assert.strictEqual(statusLedIsHidden(unknown, "STAT"), true);
"""
        )
        result = subprocess.run(["node", "-e", js], text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_live_chassis_leds_do_not_invent_green_telemetry(self) -> None:
        start = self.source.index("function statusLedClass(")
        end = self.source.index("const portActivityState", start)
        js = self.source[start:end] + """
const assert = require("assert");
for (const name of ["MODE", "STAT", "SYST", "ACTV", "DUPLX", "SPEED"]) {
  assert.strictEqual(statusLedClass(name, false), "cv-led-off", name);
}
assert.strictEqual(statusLedClass("STAT", true), "cv-led-green");
assert.strictEqual(statusLedClass("PoE", false, { poeActive: true }), "cv-led-poe");
assert.strictEqual(statusLedClass("PoE", false), "cv-led-off");
assert.strictEqual(statusLedClass("STACK", false, { stackActive: true }), "cv-led-blue");
assert.strictEqual(statusLedClass("STACK", false), "cv-led-off");
"""
        result = subprocess.run(["node", "-e", js], text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_status_box_border_and_field_controls_start_on_second_track(self) -> None:
        start = self.source.index('data-cv-section="status-boxes"')
        end = self.source.index('data-cv-section="switch-stack"', start)
        section = self.source[start:end]
        self.assertEqual(section.count("cv-cal-status-combined-row"), 4)
        self.assertEqual(section.count("cv-cal-status-border-row"), 2)
        self.assertIn("Box 1 border", section)
        self.assertIn("Box 2 border", section)
        first = section[section.index('>Status Box 1</span>'):section.index('>Status Box 2</span>')]
        second = section[section.index('>Status Box 2</span>'):section.index('cv-cal-dual-port-status-outputs')]
        self.assertNotIn('Status Box 1 style', section)
        self.assertNotIn('Status Box 2 style', section)
        self.assertLess(first.index('data-cv-field="status-box-color-show"'), first.index('cv-cal-status-border-row'))
        self.assertLess(first.index('cv-cal-status-border-row'), first.index('data-cv-field="status-border-show"'))
        self.assertIn('data-cv-field="status-row-field"', first)
        self.assertIn('data-cv-action="status-row-toggle"', first)
        self.assertLess(second.index('data-cv-field="status2-box-color-show"'), second.index('cv-cal-status-border-row'))
        self.assertLess(second.index('cv-cal-status-border-row'), second.index('data-cv-field="status2-border-show"'))
        self.assertIn('data-cv-field="status2-row-field"', second)
        self.assertIn('data-cv-action="status2-row-toggle"', second)
        self.assertNotIn('class="cv-cal-tools-row cv-cal-status-row"', first)
        self.assertNotIn('class="cv-cal-tools-row cv-cal-status-row"', second)

        css = (ROOT / "src" / "css" / "switch-vision.css").read_text(encoding="utf-8")
        track = css[css.index(".cv-cal-status-combined-row{"):css.index(".cv-cal-inline-separator{")]
        self.assertIn("flex-wrap:nowrap", track)
        self.assertIn("overflow-x:auto", track)

    def test_all_calibration_move_controls_have_accessible_arrow_labels(self) -> None:
        section = self.source
        for action in ("status-row", "status2-row", "port-status-row"):
            for direction, symbol in (("up", "↑"), ("down", "↓")):
                self.assertIn(f'data-cv-action="{action}-{direction}"', section)
                self.assertIn(f'aria-label="Move {direction}"', section)
                self.assertIn(f'>{symbol}</button>', section)
        self.assertNotIn('>Move up</button>', section)
        self.assertNotIn('>Move down</button>', section)

    def test_port_status_output_picker_precedes_connector_in_details_row(self) -> None:
        start = self.source.index("const portStatusOutputPickerHtml")
        end = self.source.index("const status1TitleOptions", start)
        block = self.source[start:end]
        self.assertLess(block.index('data-cv-field="port-status-output"'), block.index('data-cv-field="port-status-row-type"'))
        self.assertIn("panelNumber === 1 ? portStatusOutputPickerHtml", block)
        self.assertIn("cv-cal-port-output-details", block)
        self.assertIn('data-cv-panel="${panelNumber}" ${disabled}', block)
        section = self.source[self.source.index('data-cv-section="status-boxes"'):
                              self.source.index('data-cv-section="switch-stack"')]
        self.assertNotIn('<span class="cv-cal-quick-label">Port Status Box Output</span>', section)

    def test_port_label_visibility_is_first_on_label_style_row(self) -> None:
        start = self.source.index('class="cv-cal-port-label-style"') if 'class="cv-cal-port-label-style"' in self.source else self.source.index("cv-cal-port-label-style")
        section = self.source[start:self.source.index('data-cv-field="port-number-font-size"', start)]
        self.assertLess(section.index("${selectedNumberLabelVisibilityControls}"), section.index("${portLabelStyleControl}"))
        self.assertIn('cv-cal-port-label-target', self.source)
        css = (ROOT / 'src' / 'css' / 'switch-vision.css').read_text(encoding='utf-8')
        target_style = css[css.index('.cv-cal-port-label-style > .cv-cal-port-label-target'):]
        self.assertIn('flex: 0 0 auto', target_style)
        self.assertIn('min-width: 0', target_style)

    def test_port_status_output_groups_follow_one_another_without_expanding_gap(self) -> None:
        css = (ROOT / 'src' / 'css' / 'switch-vision.css').read_text(encoding='utf-8')
        start = css.index('.cv-cal-dual-port-status-outputs > .cv-cal-status-row{')
        block = css[start:css.index('}', start)]
        self.assertIn('flex:0 1 auto', block)
        self.assertIn('max-width:100%', block)
        self.assertNotIn('flex:1 1', block)



if __name__ == "__main__":
    unittest.main()
