#!/usr/bin/env python3
"""Regression for configurable read-only optical diagnostics in the existing status box."""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "js" / "switch-vision.js"


class OpticalPortStatusFieldConfigurationTests(unittest.TestCase):
    def test_existing_field_state_dell_transition_and_separate_boxes(self):
        js = r'''
const fs = require("fs");
const vm = require("vm");
const assert = require("assert");
const source = fs.readFileSync(process.argv[1], "utf8");
const a = source.indexOf("const SFP_OPTICAL_FIELDS = Object.freeze(");
const b = source.indexOf("function switchSummaryDetails(hass, config, cal, panelNumber = 1)", a);
assert(a >= 0 && b > a);
const sandbox = {
  assert,
  calibration: {},
  uiFromCalibration: (cal) => cal.ui
};
vm.runInNewContext(source.slice(a,b) + String.raw`
const opticIds = [...SFP_OPTICAL_FIELDS];
assert.strictEqual(opticIds.length, 9);
const profile = (key) => ({
  field_order: {
    port: ["role","vlan","desc","link","rx","tx","number","port_db"],
    sfp: ["role","vlan","desc","link","rx","tx","number","port_db"]
  },
  hidden_fields: {port: ["number"], sfp: ["number"]},
  key
});
const cal = {ui:{status_panel:profile("box1"),status_panel_2:profile("box2")}};
const dell = {switch_model:"N2128PX-ON"};
statusPanelFieldSelection(dell,"port",cal,1);
const copperBefore = JSON.stringify(cal.ui.status_panel.field_order.port);
const portHiddenBefore = JSON.stringify(cal.ui.status_panel.hidden_fields.port);
let initial = statusPanelFieldSelection(dell,"sfp",cal,1);
assert(!initial.includes("tx_power"), "legacy optical fields must not silently appear");
assert(opticIds.every((field) => cal.ui.status_panel.hidden_fields.sfp.includes(field)));
assert.strictEqual(cal.ui.status_panel.optical_rows_customized, undefined);
prepareSfpStatusFieldEdit(dell,cal,cal.ui.status_panel,1);
assert.strictEqual(cal.ui.status_panel.optical_rows_customized,true);
const visible = statusPanelFieldSelection(dell,"sfp",cal,1);
assert(visible.includes("optic_status") && visible.includes("temperature") && visible.includes("tx_power"));
assert(visible.includes("media_type") && visible.includes("transceiver_part"));
assert.strictEqual(JSON.stringify(cal.ui.status_panel.field_order.port),copperBefore);
assert.strictEqual(JSON.stringify(cal.ui.status_panel.hidden_fields.port),portHiddenBefore);
assert.strictEqual(cal.ui.status_panel_2.optical_rows_customized,undefined);
const hidden = cal.ui.status_panel.hidden_fields.sfp;
hidden.push("tx_power");
assert(!statusPanelFieldSelection(dell,"sfp",cal,1).includes("tx_power"));
let order = cal.ui.status_panel.field_order.sfp;
order.splice(order.indexOf("rx_power"),1);
order.unshift("rx_power");
assert.strictEqual(statusPanelFieldSelection(dell,"sfp",cal,1)[0],"rx_power");
assert.strictEqual(statusPanelFieldSelection(dell,"port",cal,1)[0],"role");
// Simulate real saved calibration storage and restoration without altering defaults.
const reloaded = JSON.parse(JSON.stringify(cal));
assert.strictEqual(reloaded.ui.status_panel.optical_rows_customized,true);
assert.strictEqual(statusPanelFieldSelection(dell,"sfp",reloaded,1)[0],"rx_power");
assert(!statusPanelFieldSelection(dell,"sfp",reloaded,1).includes("tx_power"));
assert.strictEqual(JSON.stringify(reloaded.ui.status_panel.field_order.port),copperBefore);
const originalBox1 = JSON.stringify(cal.ui.status_panel);
prepareSfpStatusFieldEdit(dell,cal,cal.ui.status_panel_2,2);
assert.strictEqual(JSON.stringify(cal.ui.status_panel),originalBox1);
assert(statusPanelFieldSelection(dell,"sfp",cal,2).includes("tx_power"));
const generic = {ui:{status_panel:profile("generic")}};
statusPanelFieldSelection({switch_model:"OTHER"},"sfp",generic,1);
prepareSfpStatusFieldEdit({switch_model:"OTHER"},generic,generic.ui.status_panel,1);
assert(!statusPanelFieldSelection({},"sfp",generic,1).includes("rx_power"));
generic.ui.status_panel.hidden_fields.sfp =
  generic.ui.status_panel.hidden_fields.sfp.filter((field) => field !== "rx_power");
assert(statusPanelFieldSelection({},"sfp",generic,1).includes("rx_power"));
`,sandbox);
'''
        result = subprocess.run(
            ["node", "-e", js, str(SOURCE)],
            text=True, capture_output=True, cwd=ROOT, timeout=20
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_independent_port_calibration_controls_and_legacy_rendering(self):
        s = SOURCE.read_text(encoding="utf-8")
        self.assertIn('data-cv-field="port-status-row-type"', s)
        self.assertIn('this._portStatusRowTypes?.[panelNumber] === "sfp" ? "sfp" : "port"', s)
        self.assertIn('Port Status Box ${panelNumber} Output', s)
        self.assertIn('const panelNumber = Number(button.getAttribute("data-cv-panel"));', s)
        self.assertIn('data-cv-field="port-status-output"', s)
        self.assertIn('<option value="both"', s)
        self.assertIn('cv-cal-port-output-row${enabled ? "" : " is-inactive"}', s)
        self.assertIn('panel.field_order[rowType] = order;', s)
        self.assertIn('panel.hidden_fields[rowType] = [...hidden]', s)
        self.assertIn('optics.available && isDellN2128OpticalModel(config)', s)
        self.assertIn('optical_rows_customized !== true', s)
        self.assertIn('SFP_OPTICAL_FIELDS.includes(field) || values[field] !== "—"', s)
        self.assertNotIn('panel.field_order.sfp = [...order];', s)
        self.assertNotIn('panel.hidden_fields.sfp = [...nextHidden];', s)
        self.assertEqual(s, (ROOT / "src/custom_components/switch_vision/switch-vision-card.js").read_text(encoding="utf-8"))

    def test_dell_optical_sensor_names_and_two_distinct_ports(self):
        js = r'''
const fs=require("fs"),vm=require("vm"),assert=require("assert");
const s=fs.readFileSync(process.argv[1],"utf8");
const a=s.indexOf("function selectedSfpOpticalDetails(");
const b=s.indexOf("\nfunction selectedSfpDetails(",a);
assert(a>0&&b>a);
const ctx={
 rearSfpOrdinalFromPort:()=>0,
 normalizeEntityPrefix:()=>"dell",
 configuredEntity:()=>null,
 firstEntityValue:(h,ids)=>ids.map(id=>h.states[id]?.state).find(Boolean),
 firstEntityDisplayValue:(h,ids)=>ids.map(id=>{
   const state=h.states[id];return state ? state.state+(state.attributes?.unit_of_measurement?" "+state.attributes.unit_of_measurement:"") : null;
 }).find(Boolean)
};
const fn=vm.runInNewContext(s.slice(a,b)+";selectedSfpOpticalDetails",ctx);
const states={
 "sensor.dell_sfp_10g_1_temperature":{state:"28.4",attributes:{unit_of_measurement:"°C"}},
 "sensor.dell_sfp_10g_1_tx_optical_power":{state:"-3.125",attributes:{unit_of_measurement:"dBm"}},
 "sensor.dell_sfp_10g_1_media_type":{state:"10GBase-LR"},
 "sensor.dell_sfp_10g_1_transceiver_vendor":{state:"SAMPLE-OPTICS-A"},
 "sensor.dell_sfp_10g_2_temperature":{state:"31.6",attributes:{unit_of_measurement:"°C"}},
 "sensor.dell_sfp_10g_2_rx_optical_power":{state:"-8.250",attributes:{unit_of_measurement:"dBm"}},
 "sensor.dell_sfp_10g_2_media_type":{state:"10GBase-SR"},
 "sensor.dell_sfp_10g_2_transceiver_vendor":{state:"SAMPLE-OPTICS-B"}
};
const a1=fn({states},{},1),a2=fn({states},{},2),none=fn({states},{},3);
assert.equal(a1.temperature,"28.4 °C");
assert.equal(a1.tx_power,"-3.125 dBm");
assert.equal(a1.media_type,"10GBase-LR");
assert.equal(a2.rx_power,"-8.250 dBm");
assert.equal(a2.media_type,"10GBase-SR");
assert.equal(a2.transceiver_vendor,"SAMPLE-OPTICS-B");
const oneG=fn({states:{"sensor.dell_sfp_1g_3_media_type":{state:"1000Base-LX"}}},{},3);
const uplink=fn({states:{"sensor.dell_uplink_4_rx_optical_power":{state:"-3.8",attributes:{unit_of_measurement:"dBm"}}}},{},4);
assert.equal(oneG.media_type,"1000Base-LX");
assert.equal(uplink.rx_power,"-3.8 dBm");
assert.equal(none.available,false);
assert.equal(none.tx_power,"—");
'''
        result = subprocess.run(
            ["node", "-e", js, str(SOURCE)],
            text=True, capture_output=True, cwd=ROOT, timeout=20
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
