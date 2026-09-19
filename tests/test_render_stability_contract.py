#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "src" / "js" / "switch-vision.js"
MIRROR = ROOT / "src" / "custom_components" / "switch_vision" / "switch-vision-card.js"


def find_chromium() -> Path | None:
    roots = [
        Path("/opt/switch-vision-runner/cache/stability-lab/playwright"),
        Path("/opt/switch-vision-release-lab/playwright-browsers"),
    ]
    candidates: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        candidates.extend(sorted(root.glob("chromium_headless_shell-*/chrome-linux/headless_shell"), reverse=True))
        candidates.extend(sorted(root.glob("chromium-*/chrome-linux/chrome"), reverse=True))
    return next((candidate for candidate in candidates if candidate.is_file()), None)


CHROMIUM = find_chromium()


class RenderStabilityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = CARD.read_text(encoding="utf-8")

    def test_card_sources_remain_exact_mirrors(self) -> None:
        self.assertEqual(CARD.read_bytes(), MIRROR.read_bytes())

    def test_faceplate_height_is_calibration_only(self) -> None:
        self.assertNotIn("config.faceplate_max_height", self.source)
        self.assertNotIn('data-cv-field="faceplate-max-height"', self.source)
        self.assertIn('data-cv-field="faceplate-height-preset"', self.source)
        self.assertIn('data-cv-field="faceplate-height-custom"', self.source)
        self.assertIn("const SV_FACEPLATE_MAX_HEIGHT_MIN_PX = 80;", self.source)
        self.assertIn("preserveFaceplateMaxHeight: true", self.source)
        self.assertIn("delete faceplate.max_height;", self.source)
        self.assertNotIn("faceplateWidthCapForHeight(", self.source)
        self.assertIn('const faceplateRenderMaxWidth = globalFaceplateMaxWidth;', self.source)
        self.assertIn('const faceplateSvgAspect = faceplateMaxHeight === null ? "xMidYMid meet" : "none";', self.source)

    def test_live_hass_path_is_relevance_gated_and_frame_coalesced(self) -> None:
        required = (
            "hasRelevantHassStateChange(previousHass, nextHass)",
            "trackedHassForRender(dependencies)",
            "scheduleLiveVisualRefresh(force = false)",
            "pendingLiveFrameCanAbsorbUpdate",
            "this._trackedEntityIds = dependencies;",
            "if (!this.isConnected) return;",
            "if (controlsActive) {",
            "this.cancelScheduledLiveRefresh();",
            "this.stopActivityAnimation();",
        )
        for marker in required:
            self.assertIn(marker, self.source)

    def test_activity_timer_updates_retained_leds_only(self) -> None:
        start = self.source.index("  scheduleActivityAnimationIfNeeded() {")
        end = self.source.index("\n  set hass(hass) {", start)
        block = self.source[start:end]
        self.assertIn("this.refreshActivityLeds();", block)
        self.assertNotIn("this.redrawSwitchSvg()", block)
        self.assertIn("cvActivityPort", self.source)
        self.assertIn("cvActivitySfp", self.source)
        self.assertIn("__activity_state_maps", self.source)

    def test_activity_visuals_are_irregular_independent_and_not_metronomic(self) -> None:
        required = (
            "function activityFlickerSeed(value)",
            "function nextActivityRandom(state)",
            "function activityFlickerDurationMs(config, level, state, on)",
            "function resetActivityFlicker(state, key, config, level, now, sampleUpdated = 0)",
            "function activityFlickerOn(config, state, key, level, now)",
            "return activityFlickerOn(config, state, key, displayLevel, now);",
        )
        for marker in required:
            self.assertIn(marker, self.source)
        self.assertNotIn("const phase = elapsed % period;", self.source)
        self.assertNotIn("dutyCycle(displayLevel)", self.source)

    def test_render_normalization_is_scoped_to_one_visual_pass(self) -> None:
        self.assertIn("function beginCalibrationUiRenderPass()", self.source)
        self.assertIn("const calibrationUiRenderPassCache = new WeakMap();", self.source)
        redraw_start = self.source.index("  redrawSwitchSvg(activeCalibration = null) {")
        redraw_end = self.source.index("\n  render() {", redraw_start)
        redraw = self.source[redraw_start:redraw_end]
        self.assertIn("const previousUiPass = beginCalibrationUiRenderPass();", redraw)
        self.assertIn("endCalibrationUiRenderPass(previousUiPass);", redraw)

    def test_ui_settings_subscription_is_single_flight_and_stale_safe(self) -> None:
        block_start = self.source.index("  unsubscribeUiSettingsUpdates() {")
        block_end = self.source.index("\n  maybeLoadGlobalUiSettings() {", block_start)
        block = self.source[block_start:block_end]
        self.assertIn("_uiSettingsEventSubscriptionRequested", block)
        self.assertIn("_uiSettingsEventSubscriptionToken", block)
        self.assertIn("!this.isConnected", block)
        self.assertIn("stale UI-settings unsubscription failed", block)

    def test_profile_load_is_single_flight_and_dirty_editor_safe(self) -> None:
        start = self.source.index("  async loadCalibrationProfile(force = false, options = {}) {")
        end = self.source.index("\n  async createStarterCalibrationProfile", start)
        block = self.source[start:end]
        self.assertIn("this._profileLoadPromiseKey === requestKey", block)
        self.assertIn("this._profileLoadPromise = task;", block)
        self.assertIn("editRevision", block)
        self.assertIn("this._calibrationDirty === true", block)
        self.assertIn("applyLoadedCalibrationToWorking", block)

    def test_delayed_editor_feedback_never_full_renders(self) -> None:
        start = self.source.index("  clearCalibrationSaveStatusSoon() {")
        end = self.source.index("\n  async saveCalibrationProfile", start)
        block = self.source[start:end]
        self.assertNotIn("this.render()", block)
        self.assertIn("this.syncCalibrationSaveStatus();", block)
        self.assertIn("data-cv-save-status", self.source)
        self.assertNotIn("setTimeout(() => this.render(), 900)", self.source)

    def test_continuous_colour_input_uses_visual_only_refresh(self) -> None:
        self.assertIn("scheduleCalibrationSvgRefresh(cal = null)", self.source)
        self.assertIn("{ syncPicker: false, visualOnly: true }", self.source)
        self.assertIn("{ visualOnly: true }", self.source)
        self.assertIn('input.addEventListener("input", (event) => commit(event, true));', self.source)

    @unittest.skipUnless(CHROMIUM is not None, "maintained Chromium runtime unavailable")
    def test_browser_runtime_regressions(self) -> None:
        source = self.source.replace("</script>", "<\\/script>")
        harness = r"""
window.requestAnimationFrame = (cb) => setTimeout(() => cb(performance.now()), 0);
window.cancelAnimationFrame = (id) => clearTimeout(id);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const entity = (value, when = Date.now()) => ({state:String(value), attributes:{}, last_updated:new Date(when).toISOString(), last_changed:new Date(when).toISOString()});
const defaultSettings = {show_card_headers:true, activity_leds:{}, faceplate_width:{mode:'auto', custom:800, effective:null}};
function immediateConnection() { return {subscribeEvents: () => Promise.resolve(() => {})}; }
function makeHass(states, connection = immediateConnection(), callWS = null) {
  return {states, connection, callWS: callWS || (async (msg) => msg.type === 'switch_vision/get_ui_settings' ? defaultSettings : (msg.type === 'switch_vision/list_assets' ? {logos:[], faceplates:[]} : {})), callService: async () => {}};
}
async function scenarioLiveGate() {
  const conn = immediateConnection(); let states = {}; let hass = makeHass(states, conn); const cards = [];
  for (let i = 1; i <= 10; i++) { const card = document.createElement('switch-vision-3650'); card.setConfig({member:`SW${i}`, selected_switch:`SW${i}`, calibration_profile_load:false, calibration_profile_auto_load:false, demo:false, port_count:48, sfp_port_count:4}); document.body.appendChild(card); card.hass = hass; cards.push(card); }
  await sleep(80);
  for (const card of cards) { card.__redraws = 0; const original = card.redrawSwitchSvg.bind(card); card.redrawSwitchSvg = (...args) => { card.__redraws++; return original(...args); }; }
  for (let n = 0; n < 20; n++) { states = {...states, [`sensor.unrelated_${n}`]: entity(n)}; hass = makeHass(states, conn); for (const card of cards) card.hass = hass; }
  await sleep(30); const unrelated = cards.map((card) => card.__redraws);
  states = {...states, 'sensor.sw5_port_1_speed_mbps': entity('1000')}; hass = makeHass(states, conn); for (const card of cards) card.hass = hass; await sleep(30);
  const relevant = cards.map((card) => card.__redraws);
  const beforeBurst = cards.map((card) => card.__redraws);
  for (let n = 0; n < 20; n++) { states = {...states, 'sensor.sw5_port_1_speed_mbps': entity(n % 2 ? '1000' : '100')}; hass = makeHass(states, conn); for (const card of cards) card.hass = hass; }
  await sleep(30);
  const burstDelta = cards.map((card, index) => card.__redraws - beforeBurst[index]);
  const timers = cards.map((card) => card._activityRenderTimer != null); cards.forEach((card) => card.remove()); return {unrelated, relevant, burstDelta, timers};
}
async function scenarioSubscriptions() {
  const pending = []; const calls = {ui:0, cal:0}; const active = {ui:0, cal:0};
  const conn = {subscribeEvents: (_cb, name) => { const kind = name === 'switch_vision_ui_settings_updated' ? 'ui' : 'cal'; calls[kind]++; return new Promise((resolve) => pending.push(() => { active[kind]++; resolve(() => { active[kind]--; }); })); }};
  const hass = makeHass({}, conn); const card = document.createElement('switch-vision-3650'); card.setConfig({member:'SW1', selected_switch:'SW1', calibration_profile_load:false, calibration_profile_auto_load:false}); document.body.appendChild(card);
  for (let i = 0; i < 12; i++) card.hass = hass; await sleep(10); const before = {...calls}; card.remove(); while (pending.length) pending.shift()(); await sleep(10); const late = {...active}; document.body.appendChild(card); card.hass = hass; await sleep(5); while (pending.length) pending.shift()(); await sleep(10); const reconnect = {...active}; card.remove(); await sleep(10); return {before, late, reconnect, final:{...active}};
}
async function scenarioProfileRace() {
  let calls = 0; let resolveProfile; const deferred = new Promise((resolve) => { resolveProfile = resolve; }); const conn = immediateConnection();
  const callWS = (msg) => { if (msg.type === 'switch_vision/get_calibration') { calls++; return deferred; } if (msg.type === 'switch_vision/get_ui_settings') return Promise.resolve(defaultSettings); if (msg.type === 'switch_vision/list_assets') return Promise.resolve({logos:[], faceplates:[]}); return Promise.resolve({}); };
  const hass = makeHass({}, conn, callWS); const card = document.createElement('switch-vision-3650'); card.setConfig({member:'SW1', selected_switch:'SW1', calibration_mode:true, calibration_controls:true, calibration_profile_load:true, calibration_profile_auto_load:true}); document.body.appendChild(card); for (let i = 0; i < 12; i++) card.hass = hass; await sleep(20);
  const profile = card.calibrationProfileName(); card._calibrationWorking.ui.link_led_color = '#abcdef'; card.markCalibrationDirty(); const stored = JSON.parse(JSON.stringify(calibration)); stored.ui.link_led_color = '#112233'; resolveProfile({profile, exists:true, source:'test', calibration:stored}); await sleep(40); const out = {calls, dirty:card._calibrationDirty, working:card._calibrationWorking?.ui?.link_led_color, stored:card._profileCalibration?.ui?.link_led_color}; card.remove(); return out;
}
async function scenarioCalibrationStability() {
  let states = {'sensor.sw1_port_1_speed_mbps': entity('1000')}; const conn = immediateConnection(); const card = document.createElement('switch-vision-3650'); card.setConfig({member:'SW1', selected_switch:'SW1', calibration_profile_load:false, calibration_profile_auto_load:false, calibration_mode:true, calibration_controls:true, port_count:48, sfp_port_count:4}); document.body.appendChild(card); card.hass = makeHass(states, conn); await sleep(40); const select = card.shadowRoot.querySelector('[data-cv-field="target"]'); let renders = 0, redraws = 0; const r = card.render.bind(card), d = card.redrawSwitchSvg.bind(card); card.render = (...args) => { renders++; return r(...args); }; card.redrawSwitchSvg = (...args) => { redraws++; return d(...args); }; states = {...states, 'sensor.sw1_port_1_speed_mbps': entity('100')}; card.hass = makeHass(states, conn); await sleep(20); const telemetry = {renders, redraws}; card.setCalibrationSaveStatus('Saved test', false); card.clearCalibrationSaveStatusSoon(); await sleep(2250); const same = select === card.shadowRoot.querySelector('[data-cv-field="target"]') && select?.isConnected; const status = card.shadowRoot.querySelector('[data-cv-save-status]'); const out = {telemetry, same, renders, redraws, statusHidden:status?.hidden === true}; card.remove(); return out;
}
async function scenarioActivity() {
  const now = Date.now(); let states = {'sensor.sw1_port_1_status':entity('up', now-10000),'sensor.sw1_port_1_speed_mbps':entity('1000', now-10000),'sensor.sw1_port_1_rx_bytes':entity('1000', now-10000),'sensor.sw1_port_1_tx_bytes':entity('1000', now-10000)}; const conn = immediateConnection(); const card = document.createElement('switch-vision-3650'); card.setConfig({member:'SW1', selected_switch:'SW1', calibration_profile_load:false, calibration_profile_auto_load:false, port_count:48, sfp_port_count:4, status_entity_prefix:'sensor.sw1_port_', status_entity_suffix:'_status', activity_hold_seconds:0.5, activity_animation_refresh_ms:100}); document.body.appendChild(card); card.hass = makeHass(states, conn); await sleep(40); let redraws = 0, ticks = 0; const r = card.redrawSwitchSvg.bind(card), a = card.refreshActivityLeds.bind(card); card.redrawSwitchSvg = (...args) => { redraws++; return r(...args); }; card.refreshActivityLeds = (...args) => { ticks++; return a(...args); }; states = {...states,'sensor.sw1_port_1_rx_bytes':entity('500000',now),'sensor.sw1_port_1_tx_bytes':entity('250000',now)}; card.hass = makeHass(states, conn); await sleep(160); const active = {redraws, ticks, timer:card._activityRenderTimer != null}; await sleep(700); const led = card.shadowRoot.querySelector('[data-cv-activity-port="1"]'); const expired = {redraws, ticks, timer:card._activityRenderTimer != null, cls:led?.getAttribute('class')}; card.remove(); return {active, expired};
}
function scenarioNaturalActivityPattern() {
  const originalNow = Date.now;
  let clock = 100000;
  Date.now = () => clock;
  try {
    const config = {
      activity_led_sensitivity_preset:'normal',
      activity_slow_period_ms:500,
      activity_medium_period_ms:250,
      activity_fast_period_ms:120,
      activity_hold_seconds:4,
      activity_hysteresis_pct:20,
    };
    const ceiling = 100000000;
    const summarize = (sequence) => {
      const toggles = [];
      let previous = sequence[0];
      for (let i = 1; i < sequence.length; i++) {
        if (sequence[i] !== previous) {
          toggles.push(i);
          previous = sequence[i];
        }
      }
      const gaps = [];
      for (let i = 1; i < toggles.length; i++) gaps.push(toggles[i] - toggles[i - 1]);
      return {
        on: sequence.filter(Boolean).length,
        transitions: toggles.length,
        uniqueGaps: [...new Set(gaps)].length,
        signature: sequence.map(v => v ? '1' : '0').join(''),
      };
    };
    const sample = (key, deltaBytes) => {
      const map = new Map();
      clock = 100000;
      const initialRx = {value:1000, updated:clock};
      const initialTx = {value:1000, updated:clock};
      updateActivityState(map, key, initialRx, initialTx, config, ceiling);
      clock += 1000;
      const activeRx = {value:1000 + deltaBytes, updated:clock};
      const activeTx = {value:1000, updated:clock};
      updateActivityState(map, key, activeRx, activeTx, config, ceiling);
      const started = clock;
      const sequence = [];
      for (let i = 0; i < 60; i++) {
        clock = started + (i * 50);
        sequence.push(updateActivityState(map, key, activeRx, activeTx, config, ceiling));
      }
      return summarize(sequence);
    };
    return {
      slow:sample('SW1:port:1',5000),
      medium:sample('SW1:port:2',50000),
      mediumPeer:sample('SW1:port:3',50000),
      fast:sample('SW1:port:4',200000),
    };
  } finally {
    Date.now = originalNow;
  }
}
async function scenarioColour() {
  const conn = immediateConnection(); const card = document.createElement('switch-vision-3650'); card.setConfig({member:'SW1', selected_switch:'SW1', calibration_profile_load:false, calibration_profile_auto_load:false, calibration_mode:true, calibration_controls:true, demo:true, port_count:48, sfp_port_count:4}); document.body.appendChild(card); card.hass = makeHass({}, conn); await sleep(40); let renders=0, redraws=0; const r=card.render.bind(card), d=card.redrawSwitchSvg.bind(card); card.render=(...args)=>{renders++;return r(...args)}; card.redrawSwitchSvg=(...args)=>{redraws++;return d(...args)}; const hue=card.shadowRoot.querySelector('[data-cv-colour-hue]'); const original=hue; for(let i=0;i<10;i++){hue.value=String(i*31);hue.dispatchEvent(new Event('input',{bubbles:true}));} const immediate={renders,redraws,same:original===card.shadowRoot.querySelector('[data-cv-colour-hue]')}; await sleep(25); const after={renders,redraws,same:original===card.shadowRoot.querySelector('[data-cv-colour-hue]'),dirty:card._calibrationDirty}; card.remove(); return {immediate,after};
}
async function scenarioFaceplateHeight() {
  const conn = immediateConnection();
  const makeCard = async (member) => {
    const card = document.createElement('switch-vision-3650');
    card.setConfig({member, selected_switch:member, calibration_profile_load:false, calibration_profile_auto_load:false, calibration_mode:true, calibration_controls:true, demo:true, port_count:48, sfp_port_count:4});
    document.body.appendChild(card);
    card.hass = makeHass({}, conn);
    await sleep(30);
    return card;
  };
  const choosePreset = async (card, preset) => {
    const select = card.shadowRoot.querySelector('[data-cv-field="faceplate-height-preset"]');
    select.value = preset;
    select.dispatchEvent(new Event('change', {bubbles:true}));
    await sleep(20);
  };
  const chooseCustom = async (card, height) => {
    const select = card.shadowRoot.querySelector('[data-cv-field="faceplate-height-preset"]');
    select.value = 'custom';
    select.dispatchEvent(new Event('change', {bubbles:true}));
    const customWrap = card.shadowRoot.querySelector('[data-cv-faceplate-height-custom]');
    const input = card.shadowRoot.querySelector('[data-cv-field="faceplate-height-custom"]');
    const visible = customWrap?.hidden === false;
    input.value = String(height);
    input.dispatchEvent(new Event('change', {bubbles:true}));
    await sleep(20);
    return visible;
  };
  const snapshot = (card) => ({
    maxHeight: card.resolvedFaceplateMaxHeight(card.calibrationData()),
    maxWidth: parseFloat(card.shadowRoot.querySelector('.cv-card')?.style.maxWidth || '0'),
    imageHeight: card.shadowRoot.querySelector('[data-cv-faceplate-image]')?.style.height || null,
    svgAspect: card.shadowRoot.querySelector('.cv-svg')?.getAttribute('preserveAspectRatio') || null,
    preset: card.shadowRoot.querySelector('[data-cv-field="faceplate-height-preset"]')?.value || null,
    customMin: card.shadowRoot.querySelector('[data-cv-field="faceplate-height-custom"]')?.min || null,
  });

  const automatic = await makeCard('SWHAUTO');
  const automaticSnapshot = snapshot(automatic);

  const compact = await makeCard('SWH115');
  await choosePreset(compact, 'compact');
  const compactSnapshot = snapshot(compact);

  const medium = await makeCard('SWH150');
  await choosePreset(medium, 'medium');
  const mediumSnapshot = snapshot(medium);

  const roomy = await makeCard('SWH200');
  await choosePreset(roomy, 'large');
  const roomySnapshot = snapshot(roomy);

  const custom = await makeCard('SWHCUSTOM');
  const customVisible = await chooseCustom(custom, 96);
  const customSnapshot = snapshot(custom);

  const customMinimum = await makeCard('SWHMIN');
  await chooseCustom(customMinimum, 40);
  const customMinimumSnapshot = snapshot(customMinimum);

  const result = {
    automatic:automaticSnapshot,
    compact:compactSnapshot,
    medium:mediumSnapshot,
    roomy:roomySnapshot,
    custom:{...customSnapshot, visible:customVisible},
    customMinimum:customMinimumSnapshot,
  };
  automatic.remove(); compact.remove(); medium.remove(); roomy.remove(); custom.remove(); customMinimum.remove();

  const configOnly = document.createElement('switch-vision-3650');
  configOnly.setConfig({member:'SWHYAML', selected_switch:'SWHYAML', faceplate_max_height:115, calibration_profile_load:false, calibration_profile_auto_load:false, demo:true, port_count:48, sfp_port_count:4});
  document.body.appendChild(configOnly);
  configOnly.hass = makeHass({}, conn);
  await sleep(30);
  result.configOnly = snapshot(configOnly);
  configOnly.remove();

  let savedPayload = null;
  const persistCard = document.createElement('switch-vision-3650');
  persistCard.setConfig({member:'SWHSTORE', selected_switch:'SWHSTORE', calibration_profile_load:false, calibration_profile_auto_load:false, calibration_mode:true, calibration_controls:true, demo:true, port_count:48, sfp_port_count:4});
  document.body.appendChild(persistCard);
  const persistHass = makeHass({}, conn);
  persistHass.callService = async (domain, service, data) => {
    if (domain === 'switch_vision' && service === 'save_calibration') {
      savedPayload = JSON.parse(JSON.stringify(data.calibration));
    }
  };
  persistCard.hass = persistHass;
  await sleep(30);
  await choosePreset(persistCard, 'medium');
  const savedProfile = await persistCard.saveCalibrationProfile(persistCard.calibrationData());
  result.persistenceSave = {
    profile:savedProfile,
    sent:savedPayload?.ui?.faceplate?.max_height ?? null,
    cached:persistCard._profileCalibration?.ui?.faceplate?.max_height ?? null,
  };
  persistCard.remove();

  const reloadCard = document.createElement('switch-vision-3650');
  reloadCard.setConfig({member:'SWHSTORE', selected_switch:'SWHSTORE', calibration_profile_load:true, calibration_profile_auto_load:false, demo:true, port_count:48, sfp_port_count:4});
  document.body.appendChild(reloadCard);
  const reloadCallWS = async (msg) => {
    if (msg.type === 'switch_vision/get_calibration') return {profile:msg.profile, exists:true, source:'test storage', calibration:JSON.parse(JSON.stringify(savedPayload))};
    if (msg.type === 'switch_vision/get_ui_settings') return defaultSettings;
    if (msg.type === 'switch_vision/list_assets') return {logos:[], faceplates:[]};
    return {};
  };
  reloadCard.hass = makeHass({}, conn, reloadCallWS);
  await reloadCard.loadCalibrationProfile(true, {applyToWorking:false});
  await sleep(20);
  result.persistenceLoad = {
    loaded:reloadCard._profileCalibration?.ui?.faceplate?.max_height ?? null,
    resolved:reloadCard.resolvedFaceplateMaxHeight(reloadCard._profileCalibration),
  };
  reloadCard.remove();

  return result;
}
(async () => { try { const result = {live:await scenarioLiveGate(), subscriptions:await scenarioSubscriptions(), profile:await scenarioProfileRace(), calibration:await scenarioCalibrationStability(), activity:await scenarioActivity(), naturalActivity:scenarioNaturalActivityPattern(), colour:await scenarioColour(), faceplateHeight:await scenarioFaceplateHeight()}; document.getElementById('result').textContent = JSON.stringify(result); } catch (err) { document.getElementById('result').textContent = JSON.stringify({error:String(err), stack:err?.stack||''}); } })();
"""
        document = '<!doctype html><html><body><pre id="result">pending</pre><script>' + source + '</script><script>' + harness + '</script></body></html>'
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as handle:
            handle.write(document)
            fixture = Path(handle.name)
        try:
            command = [str(CHROMIUM), "--headless", "--no-sandbox", "--disable-gpu", "--allow-file-access-from-files", "--virtual-time-budget=9000", "--dump-dom", fixture.as_uri()]
            result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90, check=False)
            self.assertEqual(result.returncode, 0, result.stderr[-2000:])
            match = re.search(r'<pre id="result">(.*?)</pre>', result.stdout, re.S)
            self.assertIsNotNone(match, result.stdout[-2000:])
            payload = json.loads(html.unescape(match.group(1)))
        finally:
            fixture.unlink(missing_ok=True)

        self.assertNotIn("error", payload, payload)
        self.assertEqual(payload["live"]["unrelated"], [0] * 10)
        self.assertEqual(payload["live"]["relevant"], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
        self.assertEqual(payload["live"]["burstDelta"], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
        self.assertEqual(payload["live"]["timers"], [False] * 10)
        self.assertEqual(payload["subscriptions"]["before"], {"ui": 1, "cal": 1})
        self.assertEqual(payload["subscriptions"]["late"], {"ui": 0, "cal": 0})
        self.assertEqual(payload["subscriptions"]["reconnect"], {"ui": 1, "cal": 1})
        self.assertEqual(payload["subscriptions"]["final"], {"ui": 0, "cal": 0})
        self.assertEqual(payload["profile"]["calls"], 1)
        self.assertTrue(payload["profile"]["dirty"])
        self.assertEqual(payload["profile"]["working"], "#abcdef")
        self.assertEqual(payload["profile"]["stored"], "#112233")
        self.assertEqual(payload["calibration"]["telemetry"], {"renders": 0, "redraws": 0})
        self.assertTrue(payload["calibration"]["same"])
        self.assertTrue(payload["calibration"]["statusHidden"])
        self.assertEqual(payload["activity"]["active"]["redraws"], 1)
        self.assertTrue(payload["activity"]["active"]["timer"])
        self.assertGreaterEqual(payload["activity"]["active"]["ticks"], 1)
        self.assertEqual(payload["activity"]["expired"]["redraws"], 1)
        self.assertFalse(payload["activity"]["expired"]["timer"])
        self.assertEqual(payload["activity"]["expired"]["cls"], "cv-led-off")
        self.assertGreater(payload["naturalActivity"]["medium"]["on"], payload["naturalActivity"]["slow"]["on"])
        self.assertGreater(payload["naturalActivity"]["fast"]["on"], payload["naturalActivity"]["medium"]["on"])
        self.assertGreaterEqual(payload["naturalActivity"]["medium"]["transitions"], 4)
        self.assertGreaterEqual(payload["naturalActivity"]["medium"]["uniqueGaps"], 2)
        self.assertNotEqual(payload["naturalActivity"]["medium"]["signature"], payload["naturalActivity"]["mediumPeer"]["signature"])
        self.assertEqual(payload["colour"]["immediate"]["renders"], 0)
        self.assertEqual(payload["colour"]["immediate"]["redraws"], 0)
        self.assertTrue(payload["colour"]["immediate"]["same"])
        self.assertEqual(payload["colour"]["after"]["renders"], 0)
        self.assertEqual(payload["colour"]["after"]["redraws"], 1)
        self.assertTrue(payload["colour"]["after"]["same"])
        self.assertTrue(payload["colour"]["after"]["dirty"])
        self.assertIsNone(payload["faceplateHeight"]["automatic"]["maxHeight"])
        self.assertEqual(payload["faceplateHeight"]["automatic"]["preset"], "auto")
        self.assertEqual(payload["faceplateHeight"]["compact"]["maxHeight"], 115)
        self.assertEqual(payload["faceplateHeight"]["compact"]["preset"], "compact")
        self.assertEqual(payload["faceplateHeight"]["medium"]["maxHeight"], 150)
        self.assertEqual(payload["faceplateHeight"]["medium"]["preset"], "medium")
        self.assertEqual(payload["faceplateHeight"]["roomy"]["maxHeight"], 200)
        self.assertEqual(payload["faceplateHeight"]["roomy"]["preset"], "large")
        self.assertEqual(payload["faceplateHeight"]["custom"]["maxHeight"], 96)
        self.assertEqual(payload["faceplateHeight"]["custom"]["preset"], "custom")
        self.assertTrue(payload["faceplateHeight"]["custom"]["visible"])
        self.assertEqual(payload["faceplateHeight"]["custom"]["customMin"], "80")
        self.assertEqual(payload["faceplateHeight"]["customMinimum"]["maxHeight"], 80)
        self.assertEqual(payload["faceplateHeight"]["customMinimum"]["preset"], "custom")
        self.assertEqual(payload["faceplateHeight"]["automatic"]["maxWidth"], payload["faceplateHeight"]["compact"]["maxWidth"])
        self.assertEqual(payload["faceplateHeight"]["automatic"]["maxWidth"], payload["faceplateHeight"]["medium"]["maxWidth"])
        self.assertEqual(payload["faceplateHeight"]["automatic"]["maxWidth"], payload["faceplateHeight"]["roomy"]["maxWidth"])
        self.assertEqual(payload["faceplateHeight"]["automatic"]["imageHeight"], "auto")
        self.assertEqual(payload["faceplateHeight"]["automatic"]["svgAspect"], "xMidYMid meet")
        self.assertEqual(payload["faceplateHeight"]["compact"]["imageHeight"], "115px")
        self.assertEqual(payload["faceplateHeight"]["medium"]["imageHeight"], "150px")
        self.assertEqual(payload["faceplateHeight"]["roomy"]["imageHeight"], "200px")
        self.assertEqual(payload["faceplateHeight"]["custom"]["imageHeight"], "96px")
        self.assertEqual(payload["faceplateHeight"]["customMinimum"]["imageHeight"], "80px")
        self.assertEqual(payload["faceplateHeight"]["compact"]["svgAspect"], "none")
        self.assertEqual(payload["faceplateHeight"]["medium"]["svgAspect"], "none")
        self.assertEqual(payload["faceplateHeight"]["roomy"]["svgAspect"], "none")
        self.assertIsNone(payload["faceplateHeight"]["configOnly"]["maxHeight"])
        self.assertEqual(payload["faceplateHeight"]["configOnly"]["maxWidth"], payload["faceplateHeight"]["automatic"]["maxWidth"])
        self.assertEqual(payload["faceplateHeight"]["configOnly"]["imageHeight"], "auto")
        self.assertEqual(payload["faceplateHeight"]["persistenceSave"]["sent"], 150)
        self.assertEqual(payload["faceplateHeight"]["persistenceSave"]["cached"], 150)
        self.assertEqual(payload["faceplateHeight"]["persistenceLoad"]["loaded"], 150)
        self.assertEqual(payload["faceplateHeight"]["persistenceLoad"]["resolved"], 150)


if __name__ == "__main__":
    unittest.main()
