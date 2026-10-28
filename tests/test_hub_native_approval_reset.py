"""Native Hub artwork approval completes the existing factory-reset save, once.

The browser-side test executes the actual Switch Vision card event handler with
minimal fake Home Assistant services. Nothing is written to live HAOS.
"""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
frontend = root / "src/js/switch-vision.js"
backend = (root / "src/custom_components/switch_vision/__init__.py").read_text()
assert '"stock_artwork_approved": base.startswith("native_")' in backend
assert '"approved_sha256": revision["sha256"]' in backend

node = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const js=fs.readFileSync(process.argv[1],'utf8');
const start=js.indexOf('  async handleCalibrationUpdateEvent(event) {');
const end=js.indexOf('\n  scheduleCalibrationSubscriptionRetry()',start);
assert(start>0&&end>start);
const Card=vm.runInNewContext('class Card {'+js.slice(start,end)+'}\nCard',{
  calibrationControlsEnabled:()=>false,
  cloneCalibrationData:structuredClone,
  console:{error(){}}
});
const approved='a'.repeat(64);
function fixture(base='native_SW3',pinSha=approved) {
  const card=new Card(),trace=[];
  card.config={}; card._calibrationWorking={old:true};
  card._profileCalibration={old:true};
  card.calibrationUpdateAppliesToThisCard=()=>({
    applies:base==='native_SW3', profile:base, baseProfile:base,
    changedProfiles:[],mine:base,myBase:base
  });
  card.invalidateProfileLoad=()=>trace.push('invalidate');
  card.refreshApprovedStockArtwork=async()=>{
    trace.push('refresh');
    card._stockArtworkChoice={sha256:pinSha};
  };
  card.factoryCalibrationForCurrentSwitch=opts=>{
    trace.push('factory');
    assert.equal(opts.preserveFaceplate,false);
    return {ui:{faceplate:{file:'default'}},geometry:'factory'};
  };
  card.clearLoadedCalibrationState=next=>{
    trace.push('clear');
    if (next) assert.equal(next.geometry,'factory');
    card._profileCalibration=null;
  };
  card.saveCalibrationProfile=()=>{throw Error('client must not rewrite approved Core factory')};
  card.render=()=>trace.push('render');
  card.loadCalibrationProfile=async(force,opts)=>{
    trace.push('load');
    assert.equal(force,true);
    assert.equal(opts.applyToWorking,false);
    card._profileCalibration={geometry:'verified Core factory'};
    return {exists:true};
  };
  card.setCalibrationSaveStatus=()=>trace.push('error-status');
  card.resetSavedCalibrations=()=>{throw Error('must NOT launch a second reset')};
  return {card,trace};
}
const event={data:{profile:'native_SW3',base_profile_name:'native_SW3',
  action:'reset_switch',stock_artwork_approved:true,approved_sha256:approved}};
(async()=>{
  const f=fixture();
  await f.card.handleCalibrationUpdateEvent(event);
  assert.deepEqual(f.trace,['invalidate','refresh','clear','load','render']);
  assert.equal(f.card._profileCalibration.geometry,'verified Core factory');
  assert.equal(f.card._calibrationDirty,false);

  // A changed SHA cannot silently persist a different faceplate.
  const mismatch=fixture('native_SW3','b'.repeat(64));
  await mismatch.card.handleCalibrationUpdateEvent(event);
  assert.equal(mismatch.trace.includes('factory'),false);
  assert.equal(mismatch.trace.includes('error-status'),true);
  assert.equal(mismatch.trace.includes('load'),true);

  // Custom is independent and does not receive Native approval events.
  const custom=fixture('custom_SW3');
  await custom.card.handleCalibrationUpdateEvent(event);
  assert.deepEqual(custom.trace,[]);

  // Existing ordinary Reset Current Switch event keeps its previous path.
  const legacy=fixture();
  await legacy.card.handleCalibrationUpdateEvent({data:{
    profile:'native_SW3',action:'reset_switch'}});
  assert.equal(legacy.trace.includes('refresh'),false);
  assert.equal(legacy.trace.includes('save:native_SW3'),false);
  assert.equal(legacy.trace.includes('load'),true);
  console.log('Core Native Hub artwork approval reset and scope contract: PASS');
})().catch(e=>{console.error(e);process.exitCode=1});
"""
res = subprocess.run(["node", "-e", node, str(frontend)], capture_output=True, text=True)
assert res.returncode == 0, res.stdout + res.stderr
print(res.stdout.strip())
