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
const helpers = between("function portStatusOutputPanel(", "function statusPanelFieldSelection(");
const context={calibration:{},uiFromCalibration:cal=>cal.ui,selectedInterface:()=>({type:"port"})};
const route=vm.runInNewContext(helpers+";({portStatusOutputPanel,statusPanelDisplaysSelectedPort,statusPanelRowTypeForConfig})", context);
const legacy={ui:{port_status_output:"status_box_2"}};
assert.equal(route.statusPanelDisplaysSelectedPort(legacy,1),false);
assert.equal(route.statusPanelDisplaysSelectedPort(legacy,2),true);
assert.equal(route.statusPanelRowTypeForConfig({},1,legacy),"switch");
assert.equal(route.statusPanelRowTypeForConfig({},2,legacy),"port");
const migrated=JSON.parse(JSON.stringify(legacy));
migrated.ui.port_status_dual_output=true;
assert.equal(route.statusPanelRowTypeForConfig({},1,migrated),"port");
assert.equal(route.statusPanelRowTypeForConfig({},2,migrated),"port");
assert.equal(route.portStatusOutputPanel(migrated),2,"migration must retain legacy setting");
assert(source.includes('cal.ui.port_status_dual_output = !Object.prototype.hasOwnProperty.call(cal.ui, "port_status_output");'));

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
  "isDellN2128OpticalModel","SFP_OPTICAL_FIELDS","htmlEscape",
  markup+";return portStatusRowControlsHtml;");
const html=build.call(editor,cal.ui.status_panel,cal.ui.status_panel_2,defs,normalise,fields,
  false,()=>false,[],x=>String(x));
assert(html.includes("Port Status Box 1 Output"));
assert(html.includes("Port Status Box 2 Output"));
assert(!html.includes("Port Status Output"));
assert.equal((html.match(/data-cv-field="port-status-row-type"/g)||[]).length,2);
assert.equal((html.match(/data-cv-field="port-status-row-field"/g)||[]).length,2);
assert.equal((html.match(/data-cv-action="port-status-row-toggle"/g)||[]).length,2);
assert(html.includes('data-cv-panel="1"') && html.includes('data-cv-panel="2"'));

const actionCode = between(
  '        if (["port-status-row-up", "port-status-row-down", "port-status-row-toggle"].includes(action)) {',
  '        if (["status-row-up", "status-row-down", "status-row-toggle"].includes(action)) {');
const action = new Function("action","button","cal","ensureCalibrationUi","ensureStatusPanelFieldState",
  "STATUS_PANEL_ROW_DEFS","normaliseStatusPanelFieldOrder","fieldListFromValue",
  "prepareSfpStatusFieldEdit",
  "return (async function(){"+actionCode+"}).call(this)");
const run=async (name,n)=>{
  await action.call(editor,name,{getAttribute:()=>String(n)},cal,x=>x,x=>x,defs,
    normalise,fields,(_config,_cal,p)=>{p.optical_rows_customized=true;});
};
(async()=>{
  await run("port-status-row-toggle",1);
  assert.equal(cal.ui.port_status_dual_output,true);
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
  assert(saved.ui.port_status_dual_output);
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


if __name__ == "__main__":
    unittest.main()
