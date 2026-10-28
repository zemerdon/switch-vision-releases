"""Exercise real card reconnect/profile-load methods after a missed Hub event.

No Home Assistant network calls are made. A fake server responds with the
persisted approved stock pin and the exact new factory Calibration saved by Core.
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
 validateImportedCalibration:raw=>({valid:true,calibration:raw}),
 cloneCalibrationData:value=>structuredClone(value),
 exactModelVisualRecommendation:()=>null,
 factoryMigrationForStoredCalibration:()=>null,
 console:{error(){},debug(){}}
});
const currentSha='b'.repeat(64);
const oldSha='a'.repeat(64);
const persistedFactory={
  schema:'switch-vision-interactive-calibration-v1',
  profile_name:'native_SW3',
  image:{file:'faceplates/model.png',width:6000,height:900},
  ports:{'1':{center:[123,456]}},sfp:{SFP1:{center:[789,456]}},
  status_leds:{SYSTEM:[400,40]},
  ui:{faceplate:{file:'__default__',source:'default',show:true}}
};
async function checkReconnect({alreadyLoaded,previousConnection}) {
 let wsCalls=0;
 const card=new Card();
 card.isConnected=true;
 card.config={switch_vision_native_panel:true,calibration_profile_auto_load:true};
 card._hass={connection:{},callWS:async request=>{
   wsCalls++; assert.equal(request.type,'switch_vision/get_calibration');
   assert.equal(request.profile,'native_SW3');
   assert.equal(request.stock_faceplate,'model.png');
   return {exists:true,calibration:persistedFactory,
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
 card.baseCalibrationData=()=>({});
 card.detectedExactModel=()=>'';
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
 assert.equal(card._profileCalibration?.image?.width,6000,'reconnected card must load Core-saved factory');
 assert.equal(card._profileCalibration?.ports?.['1']?.center?.[0],123,'must load new port geometry');
 assert.equal(card._profileCalibration?.ui?.faceplate?.file,'__default__','must use approved stock selection');
 assert.equal(card._stockArtworkChoice.sha256,currentSha,'must use approved server SHA');
 assert.equal(card._profileLoadInfo.exists,true,'approved factory remains durably saved');
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
