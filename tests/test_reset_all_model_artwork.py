"""Reset All must rebase every loaded Native model onto its latest factory faceplate."""
from pathlib import Path
import json
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/js/switch-vision.js"


class ResetAllLatestModelArtworkTests(unittest.TestCase):
    def test_loaded_native_cards_rebase_old_faceplates_individually(self):
        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("  async applyModelAwareResetAll() {")
        end = source.index("  async refreshApprovedStockArtwork() {", start)
        method = source[start:end]
        script = (
            'const assert = require("node:assert/strict");\n'
            + "const method = " + json.dumps(method) + ";\n"
            + """
const cloneCalibrationData = structuredClone;
const calibrationControlsEnabled = () => false;
const TestCard = eval('class TestCard {' + method + '} ; TestCard');
const compact = '48rj45-4sfp-compact.png';
const old = '48rj45-4sfp.png';
const optical = 'cisco-3850-12xs.png';
const state = {
  native_SW1: compact,
  native_SW2: optical,
  native_SW3: old,
  native_SW4: old,
  custom_SW5: old,
};
const resets = [];
function card(base) {
  const instance = new TestCard();
  instance._base = base;
  instance.baseCalibrationProfileName = () => base;
  instance.recommendedFaceplateFilename = () => base === 'native_SW2' ? optical : compact;
  instance.factoryCalibrationForCurrentSwitch = () => ({
    profile: 'stock_48rj45_4sfp_compact',
    image: { file: 'faceplates/' + instance.recommendedFaceplateFilename() },
    ports: { 1: { center: [321, 123] } },
  });
  instance.resetSavedCalibrations = async (scope) => {
    resets.push([base, scope]);
    if (scope !== 'switch') throw Error('Expected exactly one model-specific reset');
    state[base] = instance.recommendedFaceplateFilename();
  };
  instance.clearLoadedCalibrationState = (next) => { instance._calibrationWorking = next; };
  instance.render = () => {};
  instance.saveCalibrationProfile = async (cal, profile) => {
    assert.equal(state[base], instance.recommendedFaceplateFilename(), 'Save must follow a verified model-specific pin reset');
    instance._saved = structuredClone(cal);
    return profile;
  };
  instance.refreshApprovedStockArtwork = async () => {
    instance._stockArtworkChoice = { filename: state[base] };
  };
  instance.setCalibrationSaveStatus = (message, failed) => {
    instance._status = { message, failed };
  };
  return instance;
}
(async () => {
  const cards = ['native_SW1', 'native_SW2', 'native_SW3', 'native_SW4'].map(card);
  const success = await Promise.all(cards.map((instance) => instance.applyModelAwareResetAll()));
  assert.deepEqual(success, [true, true, true, true]);
  assert.deepEqual(resets, [
    ['native_SW1', 'switch'], ['native_SW2', 'switch'],
    ['native_SW3', 'switch'], ['native_SW4', 'switch']
  ]);
  for (const instance of cards) {
    const expected = instance.recommendedFaceplateFilename();
    assert.equal(state[instance._base], expected);
    assert.equal(instance._stockArtworkChoice.filename, expected);
    assert.equal(instance._saved.image.file, 'faceplates/' + expected);
    assert.deepEqual(instance._saved.ports['1'].center, [321, 123]);
  }
  assert.equal(state.custom_SW5, old, 'Native Reset All must not affect Custom');
})().catch((err) => { console.error(err); process.exitCode = 1; });
"""
        )
        result = subprocess.run(
            ["node", "-e", script], text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_reset_all_directly_reaches_mounted_neighbors_without_events(self):
        source = SOURCE.read_text(encoding="utf-8")
        start = source.index('        if (action === "reset-all-switches") {')
        end = source.index('        if (action === "load-profile") {', start)
        block = source[start:end]
        script = (
            'const assert = require("node:assert/strict");\n'
            + 'const block = ' + json.dumps(block) + ';\n'
            + """
const state = {native_SW1:'compact',native_SW3:'old',native_SW4:'old',custom_SW5:'old'};
const SV_MOUNTED_CALIBRATION_CARDS = new Set();
const calls = [];
function card(base) {
  const item = {
    config:{}, _hass:{}, isConnected:true,
    _lastModelAwareResetAllAppliedAt:0,
    baseCalibrationProfileName:()=>base,
    factoryCalibrationForCurrentSwitch:()=>({model:'verified'}),
    showConfirmation: async()=>true,
    resetSavedCalibrations:async(scope)=>{calls.push([base,scope]);},
    applyModelAwareResetAll:async()=>{
      calls.push([base,'switch']);
      state[base]='compact';
      item._lastModelAwareResetAllAppliedAt=Date.now();
      return true;
    },
    setCalibrationSaveStatus:(message,failed)=>{item.status={message,failed};},
    render:()=>{},
    clearCalibrationSaveStatusSoon:()=>{},
  };
  SV_MOUNTED_CALIBRATION_CARDS.add(item);
  return item;
}
const sw1=card('native_SW1');
card('native_SW3'); card('native_SW4'); card('custom_SW5');
(async()=>{
  const run = eval('(async function(){const action="reset-all-switches"; const currentScope="Native";'+block+'})');
  await run.call(sw1);
  assert.deepEqual(calls, [
    ['native_SW1','namespace'],
    ['native_SW1','switch'],['native_SW3','switch'],['native_SW4','switch'],
  ]);
  assert.equal(state.native_SW3,'compact');
  assert.equal(state.native_SW4,'compact');
  assert.equal(state.custom_SW5,'old');
  assert.equal(sw1.status.failed,false);
  for (const candidate of SV_MOUNTED_CALIBRATION_CARDS) {
    candidate._lastModelAwareResetAllAppliedAt=0;
  }
  const failed = [...SV_MOUNTED_CALIBRATION_CARDS].find(item =>
    item.baseCalibrationProfileName()==='native_SW4');
  failed.applyModelAwareResetAll=async()=>false;
  await run.call(sw1);
  assert.equal(sw1.status.failed,true, 'A failed neighboring card cannot yield success');
})().catch(err=>{console.error(err);process.exitCode=1;});
"""
        )
        result = subprocess.run(["node", "-e", script], text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
