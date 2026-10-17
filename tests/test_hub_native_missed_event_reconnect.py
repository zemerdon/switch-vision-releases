"""Exercise real card reconnect/profile-load methods after a missed Hub event.

No Home Assistant network calls are made. A fake server responds with the
persisted approved stock pin and no old Calibration, as Core's approval stores.
"""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"src/js/switch-vision.js"
node=r"""
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const js=fs.readFileSync(process.argv[1],'utf8');
function section(start,end) {
 const a=js.indexOf(start),b=js.indexOf(end,a+start.length);
 assert(a>0 && b>a,'missing source method '+start);
 return js.slice(a,b);
}
const parts=[
  section('  connectedCallback() {','\n  disconnectedCallback() {'),
  section('  invalidateProfileLoad() {','\n  applyLoadedCalibrationToWorking('),
  section('  async _requestCalibrationProfile(', '\n  async createStarterCalibrationProfile('),
  section('  maybeLoadCalibrationProfile(', '\n  calibrationUpdateAppliesToThisCard('),
];
const Card=vm.runInNewContext('class Card {\n'+parts.join('\n')+'\n}\nCard',{
 window:{addEventListener(){}},
 calibrationControlsEnabled:()=>false,
 stableCalibrationSwitchKey:()=> 'SW3',
 console:{error(){},debug(){}}
});
const currentSha='b'.repeat(64);
const oldSha='a'.repeat(64);
async function checkReconnect({alreadyLoaded,previousConnection}) {
 let wsCalls=0;
 const card=new Card();
 card.isConnected=true;
 card.config={switch_vision_native_panel:true,calibration_profile_auto_load:true};
 card._hass={connection:{},callWS:async request=>{
   wsCalls++; assert.equal(request.type,'switch_vision/get_calibration');
   assert.equal(request.profile,'native_SW3');
   assert.equal(request.stock_faceplate,'model.png');
   return {exists:false,calibration:null,
      stock_artwork:{filename:'model.png',path:'faceplates/model.png',sha256:currentSha}};
 }};
 card._profileLoadGeneration=0;
 card._profileLoadRequested=alreadyLoaded?'native_SW3':null;
 card._profileLoadedProfile=alreadyLoaded?'native_SW3':null;
 card._profileLoadInfo=alreadyLoaded?{exists:true,profile:'native_SW3'}:null;
 card._profileCalibration=alreadyLoaded?{image:{file:'faceplates/model.png'},user_topology_authoritative:true}:null;
 card._stockArtworkBase='native_SW3';
 card._stockArtworkChoice={filename:'model.png',sha256:oldSha};
 card._calibrationDirty=false;
 card.calibrationProfileName=()=> 'native_SW3';
 card.baseCalibrationProfileName=()=> 'native_SW3';
 card.recommendedFaceplateFilename=()=> 'model.png';
 card.render=()=>{};
 card.subscribeCalibrationUpdates=()=>{};
 card.subscribeUiSettingsUpdates=()=>{};
 card.maybeLoadGlobalUiSettings=()=>{};
 card.ensureUnifiRefreshTimer=()=>{};
 card.maybeLoadUnifiDevice=()=>{};
 card.scheduleLiveVisualRefresh=()=>{};
 card.stopActivityAnimation=()=>{};
 card.canLoadCalibrationProfile=()=>true;
 card.connectedCallback();
 await new Promise(setImmediate);
 assert.equal(wsCalls,1,'reconnected card must re-query server after missed approval');
 assert.equal(card._profileCalibration,null,'reconnected card must not retain deleted Calibration');
 assert.equal(card._stockArtworkChoice.sha256,currentSha,'must use approved server SHA');
 assert.equal(card._profileLoadInfo.exists,false,'removed profile remains absent');
 card.maybeLoadCalibrationProfile();
 await new Promise(setImmediate);
 assert.equal(wsCalls,1,'ordinary attached updates must not repeat the profile query');
}
(async()=>{
 await checkReconnect({alreadyLoaded:false});
 await checkReconnect({alreadyLoaded:true});
 console.log('Native post-approval missed-event reconnect contract: PASS');
})().catch(err=>{console.error(err);process.exitCode=1});
"""
result=subprocess.run(["node","-e",node,str(SOURCE)],text=True,capture_output=True,timeout=30)
assert result.returncode==0, result.stdout+result.stderr
print(result.stdout.strip())
