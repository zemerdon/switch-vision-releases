#!/usr/bin/env python3
"""Source-executed two-box Port Status Output behavior and compatibility."""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/js/switch-vision.js"


class DualPortStatusOutputTests(unittest.TestCase):
    def test_independent_dropdown_render_actions_and_legacy_routing(self):
        js = r"""
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync(process.argv[1], "utf8");
const between = (start, end) => {
  const a=source.indexOf(start), b=source.indexOf(end,a+start.length);
  assert(a>=0 && b>a, "missing Core implementation boundary "+start);
  return source.slice(a,b);
};

// Execute the actual saved-profile routing helpers, not copies of their logic.
const helpers = between("function portStatusOutputSelection(", "function statusPanelFieldSelection(");
const context={calibration:{},selectedInterface:()=>({type:"port"})};
const route=vm.runInNewContext(helpers+";({portStatusOutputSelection,statusPanelDisplaysSelectedPort,statusPanelRowTypeForConfig})", context);
// Legacy single-box saved profiles keep their explicitly saved route.
for(const [destination,p1,p2] of [["status_box_1",true,false],["status_box_2",false,true],["both",true,true]]){
  const profile={ui:{port_status_output:destination}};
  assert.equal(route.statusPanelDisplaysSelectedPort(profile,1),p1);
  assert.equal(route.statusPanelDisplaysSelectedPort(profile,2),p2);
  assert.equal(route.statusPanelRowTypeForConfig({},1,profile),p1?"port":"switch");
  assert.equal(route.statusPanelRowTypeForConfig({},2,profile),p2?"port":"switch");
}
// 2.8.12 and 2.8.13 had a split flag; do not silently drop their Both choice.
const legacyDual={ui:{port_status_output:"status_box_2",port_status_dual_output:true}};
assert.equal(route.portStatusOutputSelection(legacyDual),"both");
assert.equal(route.statusPanelRowTypeForConfig({},1,legacyDual),"port");
assert.equal(route.statusPanelRowTypeForConfig({},2,legacyDual),"port");
const legacySingle={ui:{port_status_output:"status_box_2",port_status_dual_output:false}};
assert.equal(route.portStatusOutputSelection(legacySingle),"status_box_2");
assert.equal(route.portStatusOutputSelection({ui:{}}),"both");
assert(source.includes("cal.ui.port_status_output = portStatusOutputSelection(cal);"));
assert(source.includes("delete cal.ui.port_status_dual_output;"));

const defs={
  port:{defaults:["role","vlan","link"],labels:{role:"Role",vlan:"VLAN",link:"Link"}},
  sfp:{defaults:["role","temperature","rx_power"],labels:{role:"Role",temperature:"Temperature",rx_power:"RX Power"}}
};
const panel=()=>({field_order:{port:["role","vlan","link"],sfp:["role","temperature","rx_power"]},
  hidden_fields:{port:[],sfp:[]}});
const cal={ui:{port_status_output:"status_box_2",port_status_dual_output:false,
  status_panel:panel(),status_panel_2:panel()}};
const normalise=(value)=>Array.isArray(value)?[...value]:[];
const fields=value=>Array.isArray(value)?[...value]:null;
const editor={config:{port_status_1_selected_field:"vlan",port_status_2_selected_field:"role"},
  _portStatusRowTypes:{1:"port",2:"port"},renderCount:0,dirtyCount:0,
  render(){this.renderCount++;},markCalibrationDirty(){this.dirtyCount++;}};
const markup = between("    const portStatusRowControlsHtml = [1, 2].map(", "    const status1TitleOptions =");
const build=new Function("statusUi","status2Ui","STATUS_PANEL_ROW_DEFS",
  "normaliseStatusPanelFieldOrder","fieldListFromValue","juniperModeOption",
  "isDellN2128OpticalModel","SFP_OPTICAL_FIELDS","htmlEscape","outputSelection",
  markup+";return portStatusRowControlsHtml;");
const renderControls=(mode)=>{
  cal.ui.port_status_output=mode;
  return build.call(editor,cal.ui.status_panel,cal.ui.status_panel_2,defs,normalise,fields,
    false,()=>false,[],x=>String(x),route.portStatusOutputSelection(cal));
};
const html=renderControls("status_box_2");
assert(html.includes("Port Status Box 1 Output"));
assert(html.includes("Port Status Box 2 Output"));
assert(!html.includes("Port Status Output"));
const rowFlags=(value)=>[...value.matchAll(/cv-cal-port-output-row(?: is-inactive)?" aria-disabled="(true|false)"/g)].map(x=>x[1]);
assert.deepEqual(rowFlags(html),["true","false"]);
assert.equal((html.match(/ disabled(?=>)/g)||[]).length,5,"inactive box has two disabled dropdowns and three disabled buttons");
assert.deepEqual(rowFlags(renderControls("status_box_1")),["false","true"]);
assert.deepEqual(rowFlags(renderControls("both")),["false","false"]);
assert.equal((renderControls("both").match(/ disabled(?=>)/g)||[]).length,0);
cal.ui.port_status_output="status_box_2";
assert.equal((html.match(/data-cv-field="port-status-row-type"/g)||[]).length,2);
assert.equal((html.match(/data-cv-field="port-status-row-field"/g)||[]).length,2);
assert.equal((html.match(/data-cv-action="port-status-row-toggle"/g)||[]).length,2);
assert(html.includes('data-cv-panel="1"') && html.includes('data-cv-panel="2"'));

const actionCode = between(
  '        if (["port-status-row-up", "port-status-row-down", "port-status-row-toggle"].includes(action)) {',
  '        if (["status-row-up", "status-row-down", "status-row-toggle"].includes(action)) {');
const action = new Function("action","button","cal","statusPanelDisplaysSelectedPort",
  "ensureCalibrationUi","ensureStatusPanelFieldState",
  "STATUS_PANEL_ROW_DEFS","normaliseStatusPanelFieldOrder","fieldListFromValue",
  "prepareSfpStatusFieldEdit",
  "return (async function(){"+actionCode+"}).call(this)");
const run=async (name,n)=>{
  await action.call(editor,name,{getAttribute:()=>String(n)},cal,
    route.statusPanelDisplaysSelectedPort,x=>x,x=>x,defs,
    normalise,fields,(_config,_cal,p)=>{p.optical_rows_customized=true;});
};
(async()=>{
  await run("port-status-row-toggle",1);
  assert.deepEqual(cal.ui.status_panel.hidden_fields.port,[],"disabled Box 1 action cannot mutate fields");
  assert.equal(editor.dirtyCount,0);
  cal.ui.port_status_output="both";
  await run("port-status-row-toggle",1);
  assert.deepEqual(cal.ui.status_panel.hidden_fields.port,["vlan"]);
  assert.deepEqual(cal.ui.status_panel_2.hidden_fields.port,[]);
  await run("port-status-row-down",2);
  assert.deepEqual(cal.ui.status_panel_2.field_order.port,["vlan","role","link"]);
  assert.deepEqual(cal.ui.status_panel.field_order.port,["role","vlan","link"]);
  editor._portStatusRowTypes[2]="sfp";
  editor.config.port_status_2_selected_field="temperature";
  await run("port-status-row-toggle",2);
  assert(cal.ui.status_panel_2.hidden_fields.sfp.includes("temperature"));
  assert.deepEqual(cal.ui.status_panel.hidden_fields.sfp,[]);
  const saved=JSON.parse(JSON.stringify(cal));
  assert(saved.ui.status_panel.hidden_fields.port.includes("vlan"));
  assert(saved.ui.status_panel_2.hidden_fields.sfp.includes("temperature"));
  assert.equal(saved.ui.port_status_output,"both");
  assert.equal(route.statusPanelDisplaysSelectedPort(saved,1),true);
  assert.equal(route.statusPanelDisplaysSelectedPort(saved,2),true);
  cal.ui.port_status_output="status_box_1";
  await run("port-status-row-toggle",2);
  assert.equal(editor.dirtyCount,3,"disabled Box 2 action must remain inert");
  assert.equal(editor.renderCount,3);
  assert.equal(editor.dirtyCount,3);
  assert.equal(editor.renderCount,3);
  console.log("Independent Core Port Status Output contract: PASS");
})().catch(e=>{console.error(e);process.exitCode=1;});
"""
        result = subprocess.run(
            ["node", "-e", js, str(SOURCE)],
            capture_output=True, text=True, cwd=ROOT, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn("contract: PASS", result.stdout)

    def test_two_output_rows_share_responsive_horizontal_layout(self):
        source = SOURCE.read_text(encoding="utf-8")
        css = (ROOT / "src/css/switch-vision.css").read_text(encoding="utf-8")
        # The two existing rows are grouped under one shared layout wrapper,
        # not duplicated controls or coupled per-box configuration.
        self.assertIn(
            '<div class="cv-cal-dual-port-status-outputs">\n'
            '        ${portStatusRowControlsHtml}\n'
            '      </div>', source,
        )
        self.assertIn(
            '.cv-cal-dual-port-status-outputs{\n'
            '  display:flex;\n'
            '  flex-wrap:wrap;', css,
        )
        self.assertIn(
            '.cv-cal-dual-port-status-outputs > .cv-cal-status-row{\n'
            '  flex:1 1 540px;\n'
            '  min-width:0;', css,
        )
        self.assertEqual(source.count('data-cv-panel="${panelNumber}"'), 5)
        self.assertIn('data-cv-field="port-status-output"', source)
        for value in ("status_box_1", "status_box_2", "both"):
            self.assertIn(f'<option value="{value}"', source)
        self.assertIn('cv-cal-port-output-row${enabled ? "" : " is-inactive"}', source)
        self.assertIn('aria-disabled="${!enabled}"', source)
        self.assertIn('data-cv-field="port-status-row-field" data-cv-panel="${panelNumber}" ${disabled}', source)
        self.assertIn('data-cv-action="port-status-row-toggle" data-cv-panel="${panelNumber}" ${disabled}', source)
        self.assertIn('trigger.disabled = select.disabled;', source)
        self.assertEqual(source.count('!statusPanelDisplaysSelectedPort(cal, panelNumber)) return;'), 3)
        self.assertIn('.cv-cal-dual-port-status-outputs > .cv-cal-port-output-row.is-inactive{', css)


if __name__ == "__main__":
    unittest.main()
