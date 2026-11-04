"""Reset/Hub visual operations must verify persisted artwork, geometry and LEDs."""
from pathlib import Path
import json
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/js/switch-vision.js"


class VisualOperationReadbackTests(unittest.TestCase):
    def test_readback_convergence_and_fail_closed_cases(self):
        source = SOURCE.read_text(encoding="utf-8")
        start = source.index("  async verifySavedVisualOperation(")
        end = source.index("  async refreshApprovedStockArtwork() {", start)
        method = source[start:end]
        js = (
            'const assert=require("node:assert/strict");\n'
            + 'const method=' + json.dumps(method) + ';\n'
            + r"""
const SV_VERSION = '2.8.42';
const stableCalibrationSwitchKey = () => true;
const canonicalFaceplateFilename = value => String(value || '').split('/').pop();
const stableCalibrationJson = value => JSON.stringify(value);
const uiFromCalibration = cal => cal?.ui || {};
const Card = eval('class Card {'+method+'} ; Card');
const base = {
  image:{file:'faceplates/latest.png'},
  ports:{'1':{center:[100,130]}},
  sfp:{G1:{center:[330,110]}},
  status_leds:{SYST:[30,40]},
  ui:{status_leds:{hidden:['SYST'],added:[],membership_edited:false}}
};
const sha = 'a'.repeat(64);
const stock = {filename:'latest.png',path:'faceplates/latest.png',
  sha256:sha,geometry_sha256:'b'.repeat(64)};
const clone = value => structuredClone(value);
function card(result) {
  const instance = new Card();
  instance.config = {};
  instance.baseCalibrationProfileName=()=> 'native_SW3';
  instance.recommendedFaceplateFilename=()=> 'latest.png';
  instance._hass={callWS: async args => {
    assert.equal(args.profile,'native_SW3');
    assert.equal(args.exact,true);
    assert.equal(args.stock_faceplate,'latest.png');
    return result;
  }};
  return instance;
}
(async() => {
  const valid = card({exists:true,calibration:clone(base),stock_artwork:clone(stock)});
  assert.equal(await valid.verifySavedVisualOperation('reset_switch',base,'native_SW3',
    {requireLatestStock:true}),true);
  assert.equal(valid._lastVisualOperation.stage,'saved_state_verified');
  assert.equal(valid._lastVisualOperation.ok,true);
  assert.equal(valid._lastVisualOperation.artwork_sha256,sha);
  assert.equal(await valid.verifySavedVisualOperation('hub_approval',base,'native_SW3',
    {approvedSha:sha}),true);
  for (const [expectedStage,change,options] of [
    ['saved_profile_missing', result => {result.exists=false;}, {}],
    ['artwork_mismatch', result => {result.calibration.image.file='faceplates/other.png';},{}],
    ['saved_ports_mismatch', result => {result.calibration.ports['1'].center=[1,1];},{}],
    ['saved_sfp_mismatch', result => {result.calibration.sfp.G1.center=[7,7];},{}],
    ['saved_status_leds_mismatch', result => {result.calibration.status_leds.SYST=[12,44];},{}],
    ['saved_led_membership_mismatch', result => {result.calibration.ui.status_leds.hidden=[];},{}],
    ['stock_selection_mismatch', result => {result.stock_artwork.path='faceplate-history/old/latest.png';},{requireLatestStock:true}],
    ['approved_revision_mismatch', result => {result.stock_artwork.sha256='f'.repeat(64);},{approvedSha:sha}],
  ]) {
    const result={exists:true,calibration:clone(base),stock_artwork:clone(stock)};
    change(result);
    const instance=card(result);
    await assert.rejects(
      instance.verifySavedVisualOperation('reset_switch',base,'native_SW3',options),
      new RegExp('\\['+expectedStage+'\\]')
    );
    assert.equal(instance._lastVisualOperation.ok,false);
    assert.equal(instance._lastVisualOperation.stage,expectedStage);
  }
  const offline=card(null);
  offline._hass.callWS=async()=>{throw Error('private transport detail');};
  await assert.rejects(offline.verifySavedVisualOperation('reset_all',base,'native_SW3'),
    /readback_unavailable/);
  assert.equal(offline._lastVisualOperation.stage,'readback_unavailable');
  assert.equal(JSON.stringify(offline._lastVisualOperation).includes('private transport detail'),false);
  assert.equal(base.image.file,'faceplates/latest.png');
  console.log('Visual operation saved-state readback and mismatch regression: PASS');
})().catch(e => {console.error(e); process.exitCode=1;});
"""
        )
        result = subprocess.run(
            ["node", "-e", js], text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
