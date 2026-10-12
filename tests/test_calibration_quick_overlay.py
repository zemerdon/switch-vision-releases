#!/usr/bin/env python3
"""SFP/rSFP selection visuals are driven by real front/rear geometry keys."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "src/js/switch-vision.js").read_text(encoding="utf-8")


def between(start: str, end: str) -> str:
    return JS[JS.index(start):JS.index(end, JS.index(start))]


class QuickOverlayTest(unittest.TestCase):
    def test_entire_sfp_rsfp_and_parity_activate_yellow_hitboxes(self):
        fragments = "\n".join((
            between("function normalCalibrationTarget(config) {", "function targetLabelForConfig("),
            between("function getEditableCalibrationTarget(cal, config) {", "function movePoint("),
            between("function calibrationOverlayPartActive(editable,", "function calibrationControlBoxFromRenderedElement("),
        ))
        harness = r"""
const assert=require("node:assert/strict");
const SV_PROFILE_MAX_UPLINKS=1024;
const rearSfpOrdinal=k=>{const match=String(k).match(/^rSFP([1-9][0-9]*)$/i);return match?Number(match[1]):0};
const sfpPortNumber=k=>rearSfpOrdinal(k)?1000000+rearSfpOrdinal(k):Number((String(k).match(/\d+/g)||["0"]).at(-1));
const calibrationTarget=c=>String(c?.calibration_target||"") === "sfps" ? "sfps" : ({type:"port",id:1});
const ensureCalibrationUi=_=>{};
const sortedCalibrationSfpKeys=cal=>Object.keys(cal.sfp).sort();
const sortedCalibrationPortKeys=cal=>Object.keys(cal.ports||{}).sort();
const calibrationSelectedSfpKeys=()=>[];
const calibrationSelectedPortKeys=()=>[];
const calibrationSfpKeysByParity=(cal,parity)=>sortedCalibrationSfpKeys(cal).filter(k=>!rearSfpOrdinal(k)).filter(k=>!["odd","even"].includes(parity)||sfpPortNumber(k)%2===(parity==="odd"?1:0));
const calibrationPortKeysByParity=(cal,parity)=>sortedCalibrationPortKeys(cal).filter(k=>!["odd","even"].includes(parity)||Number(k)%2===(parity==="odd"?1:0));
const portLedSizeKey=p=>["led_left","led_right"].includes(p)?p+"_size":null;
const defaultPortLedRectangleSize=()=>[8,8];
const sfpLedRectangleSize=()=>[8,8];
const sfpEntryForTarget=(cal,id)=>Object.entries(cal.sfp).map(([key,item])=>({key,item})).find(e=>sfpPortNumber(e.key)===Number(id));
const statusKeyForTarget=()=>null;
const normaliseStatusFieldGroupPart=p=>p;
""" + fragments + r"""
const cal={sfp:Object.fromEntries(["SFP1","SFP2","SFP3","SFP4","rSFP1","rSFP2","rSFP3","rSFP4"].map(k=>[k,{center:[20,30],hitbox:[12,18],label:[20,30],led_left:[18,30],led_right:[22,30]}])),ports:{}};
function check(target,part,expect) {
 const config={calibration_target:target,calibration_part:part};
 const editable=getEditableCalibrationTarget(cal,config);
 assert.equal(editable.type,"sfps",target);
 assert.deepEqual(editable.keys,expect,target);
 const active=Object.keys(cal.sfp).filter(k=>calibrationOverlayPartActive(editable,"sfp",k,"center"));
 assert.deepEqual(active,expect,target+" yellow center hitbox");
 if(part==="entire") {
  for(const k of expect)for(const p of ["led_left","led_right","label"]) {
   assert.equal(calibrationOverlayPartActive(editable,"sfp",k,p),true,target+" "+p);
  }
 }
 return editable;
}
check("sfps","entire",["SFP1","SFP2","SFP3","SFP4"]);
check("rear_sfps","entire",["rSFP1","rSFP2","rSFP3","rSFP4"]);
check("sfps_odd_entire","entire",["SFP1","SFP3"]);
check("sfps_even_entire","entire",["SFP2","SFP4"]);
check("rsfps_odd_entire","entire",["rSFP1","rSFP3"]);
check("rsfps_even_entire","entire",["rSFP2","rSFP4"]);
const target=normalCalibrationTarget({calibration_target:"rsfps_odd_labels",calibration_part:"label"});
assert.equal(target.parity,"odd");assert.equal(target.part,"label");
const e=getEditableCalibrationTarget(cal,{calibration_target:"rsfps_odd_labels",calibration_part:"label"});
assert.deepEqual(e.keys,["rSFP1","rSFP3"]);
assert.equal(calibrationOverlayPartActive(e,"sfp","rSFP1","label"),true);
assert.equal(calibrationOverlayPartActive(e,"sfp","SFP1","label"),false);
console.log("SFP_RSFP_YELLOW_SELECTION_PASS");
"""
        p = subprocess.run(["node", "-e", harness], cwd=ROOT, capture_output=True, text=True, timeout=15)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("SFP_RSFP_YELLOW_SELECTION_PASS", p.stdout)


if __name__ == "__main__":
    unittest.main()
