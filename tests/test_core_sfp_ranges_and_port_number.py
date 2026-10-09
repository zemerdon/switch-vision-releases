#!/usr/bin/env python3
"""Behavioral Core regression for optical ranges and calibrated status labels."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/js/switch-vision.js"


def function(source, name):
    start = source.index("function " + name + "(")
    end = source.find("\nfunction ", start + 8)
    return source[start:end if end >= 0 else len(source)]


class SfpRangePortNumberTests(unittest.TestCase):
    def test_real_javascript_behavior(self):
        source = SOURCE.read_text(encoding="utf-8")
        names = (
            "sfpPortNumber", "calibrationSfpAliasMap",
            "parseCalibrationCustomPortSelection", "sfpLogicalPort",
            "sfpVisibleLabel", "selectedPortStatusLabel",
            "normalStatusPanelRowType", "fieldListFromValue",
            "normaliseStatusPanelFieldOrder", "ensureStatusPanelFieldState",
            "statusPanelFieldSelection",
        )
        defs = source.split("const STATUS_PANEL_ROW_DEFS = {", 1)[1].split("\n};", 1)[0]
        harness = "\n".join([f"const STATUS_PANEL_ROW_DEFS = {{{defs}\n}};",
                              *(function(source, name) for name in names)]) + """
function uiFromCalibration(cal){return cal.ui;}
const assert=(ok, message)=>{if(!ok)throw new Error(message)};
const cal = {
  ports:{'1':{},'2':{},'3':{},'12':{}},
  sfp:{G1:{},G2:{},'G3/TE3':{},G4:{}}
};
const parse = (s) => parseCalibrationCustomPortSelection(s, cal);
let result = parse('sfp1-sfp4');
assert(result.sfpKeys.join(',') === 'G1,G2,G3/TE3,G4','SFP range not expanded');
assert(result.portKeys.length === 0 && result.invalid.length === 0,'SFP range classification');
assert(parse('sfp4-sfp1').sfpKeys.length === 4,'reverse SFP range');
assert(parse('SFP+1-SFP+4').sfpKeys.length === 4,'SFP+ range');
assert(parse('g1-g4').sfpKeys.length === 4,'G range alias');
assert(parse('1-3').portKeys.join(',') === '1,2,3','RJ45 range must be unchanged');
assert(parse('sfp1-sfp5').missing.includes('sfp5'),'must flag nonexisting SFP');
assert(parse('sfp1-te4').invalid.length === 1,'mixed-prefix SFP range rejected');
assert(parse('sfp1-sfp9000').invalid.length === 1,'unbounded range rejected');
assert(parse('sfp1,sfp3').sfpKeys.join(',') === 'G1,G3/TE3','individual selection');
assert(selectedPortStatusLabel({},cal,{type:'port',id:12}) === '12','RJ45 default');
cal.ports['12'].display_name = 'Server Uplink';
assert(selectedPortStatusLabel({},cal,{type:'port',id:12}) === 'Server Uplink','RJ45 custom');
assert(selectedPortStatusLabel({},cal,{type:'sfp',id:1}) === 'G1','SFP default');
cal.sfp.G1.display_name = 'Fiber Uplink';
assert(selectedPortStatusLabel({},cal,{type:'sfp',id:1}) === 'Fiber Uplink','SFP custom');
delete cal.sfp.G1.display_name;
assert(selectedPortStatusLabel({sfp_logical_port_map:[25]},cal,{type:'sfp',id:1}) === '25','mapped SFP label');
let legacy = {field_order:{port:['vlan','link'],sfp:['vlan','link']},hidden_fields:{port:[],sfp:[]}};
ensureStatusPanelFieldState(legacy);
assert(legacy.hidden_fields.port.includes('number'),'legacy RJ45 visibility changed');
assert(legacy.hidden_fields.sfp.includes('number'),'legacy SFP visibility changed');
legacy.hidden_fields.port = legacy.hidden_fields.port.filter(x=>x!=='number');
ensureStatusPanelFieldState(legacy);
assert(!legacy.hidden_fields.port.includes('number'),'explicit Show must persist');
assert(STATUS_PANEL_ROW_DEFS.port.labels.number === 'PORT ID','dropdown label');
assert(STATUS_PANEL_ROW_DEFS.sfp.labels.number === 'PORT ID','SFP label');
assert(STATUS_PANEL_ROW_DEFS.port.defaults.includes('role'), 'RJ45 ROLE missing from dropdown');
assert(STATUS_PANEL_ROW_DEFS.sfp.defaults.includes('role'), 'SFP ROLE missing from dropdown');
assert(legacy.field_order.port[0] === 'role', 'legacy RJ45 role position not preserved');
assert(legacy.field_order.sfp[0] === 'role', 'legacy SFP role position not preserved');
const display = {ui:{
  status_panel:legacy,
  status_panel_2:{
    field_order:{port:['link','role','number'],sfp:['link','role','number']},
    hidden_fields:{port:['role'],sfp:['role']}
  }
}};
let selected = statusPanelFieldSelection({}, 'port', display, 1);
assert(selected.includes('role'), 'RJ45 role not shown by default');
assert(selected[0] === 'role', 'RJ45 role not first for legacy');
display.ui.status_panel.hidden_fields.port.push('role');
selected = statusPanelFieldSelection({}, 'port', display, 1);
assert(!selected.includes('role'), 'RJ45 ROLE Show/Hide does not apply');
assert(!statusPanelFieldSelection({}, 'sfp', display, 2).includes('role'), 'SFP Status Box 2 hide ignored');
display.ui.status_panel_2.hidden_fields.sfp = [];
selected = statusPanelFieldSelection({}, 'sfp', display, 2);
assert(selected.includes('role'), 'SFP Status Box 2 Show ignored');
assert(selected.indexOf('role') > selected.indexOf('link'), 'SFP field reordering ignored');
assert(!statusPanelFieldSelection({}, 'port', display, 2).includes('role'), 'Status Box 2 RJ45 hide ignored');
console.log('SFP_RANGES_AND_PORT_NUMBER=PASS');
"""
        result = subprocess.run(["node", "-e", harness], cwd=ROOT, text=True,
                                capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rendering_and_controls_have_port_number_field(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(source.count("number: selectedPortStatusLabel(config, cal, selected)"), 2)
        self.assertIn('data-cv-field="port-status-row-field"', source)
        self.assertIn('field === "number" || field === "role" || field === "link"', source)
        self.assertIn("panel.field_order.sfp = [...order]", source)
        self.assertNotIn('if (values.role !== "—" && !fields.includes("role"))', source)
        self.assertIn('data-cv-action="port-status-row-toggle"', source)


if __name__ == "__main__":
    unittest.main()
