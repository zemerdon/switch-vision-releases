#!/usr/bin/env python3
"""Responsive Calibration option-menu and legacy event-handler regressions."""
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/js/switch-vision.js"
CSS = ROOT / "src/css/switch-vision.css"


class CompactPickerTest(unittest.TestCase):
    def test_visual_and_preservation_contract(self) -> None:
        css = CSS.read_text(encoding="utf-8")
        src = SOURCE.read_text(encoding="utf-8")
        for marker in (
            ".cv-cal-select-shell > select.cv-cal-select",
            "visibility: hidden;",
            "pointer-events: none;",
            ".cv-cal-select-shell > button.cv-cal-select-trigger",
            ".cv-cal-option-menu-item",
            "overflow-y: auto;",
            "min-height: 32px;",
            "font: 400 12px/17px",
        ):
            self.assertIn(marker, css)
        for marker in (
            'this.attachCompactCalibrationSelectMenus();',
            'this.attachCalibrationControlHandlers(activeCalibration);',
            'this._closeCompactCalibrationMenu?.();',
            'select.dispatchEvent(new Event("change", { bubbles: true }));',
            'if (child.tagName === "OPTGROUP")',
            'window.removeEventListener("pointerdown", onOutsidePointer, true);',
            'Math.min(openTheme.max_height || 320, available)',
            'const SV_CALIBRATION_MOBILE_MEDIA = "(max-width: 760px)";',
            'window.matchMedia?.(SV_CALIBRATION_MOBILE_MEDIA)',
            'this.attachCalibrationMobileViewportListener();',
            'media.addEventListener("change", handler)',
            'const openTheme = this._globalCalibrationTheme?.[mode ? "mobile" : "desktop"]?.dropdown_open || {};',
            'trigger.setAttribute("aria-expanded", "true");',
        ):
            self.assertIn(marker, src)

    def test_auto_width_fits_selected_trigger_and_preserves_manual_override(self) -> None:
        css = CSS.read_text(encoding="utf-8")
        src = SOURCE.read_text(encoding="utf-8")
        shell = css.split(".cv-cal-tools .cv-cal-select-shell {", 1)[1].split("}", 1)[0]
        native = css.split(".cv-cal-tools .cv-cal-select-shell > select.cv-cal-select {", 1)[1].split("}", 1)[0]
        trigger = css.split(".cv-cal-tools .cv-cal-select-shell > button.cv-cal-select-trigger {", 1)[1].split("}", 1)[0]
        target = css.split(".cv-cal-tools .cv-cal-target-select-shell > button.cv-cal-select-trigger {", 1)[1].split("}", 1)[0]
        self.assertIn("display: inline-flex;", shell)
        self.assertIn("position: absolute;", native)
        self.assertIn("width: 100%;", native)
        self.assertIn("position: relative;", trigger)
        self.assertIn("width: max-content;", trigger)
        self.assertIn("max-width: min(100%, 300px);", trigger)
        self.assertNotIn("inset: 0;", trigger)
        self.assertIn("max-width: min(100%, 185px);", target)
        self.assertIn('if (select.classList.contains("cv-cal-target-select")) shell.classList.add("cv-cal-target-select-shell");', src)
        self.assertIn('if (name === "dropdown_closed" && fields.width > 0)', src)
        self.assertIn('"width:" + fields.width + "px!important"', src)
        self.assertIn("max-width:100%!important", src)

    def test_option_choice_dispatches_change_and_closes(self) -> None:
        src = SOURCE.read_text(encoding="utf-8")
        a = src.index("  attachCompactCalibrationSelectMenus() {")
        b = src.index("  attachCalibrationControlHandlers(cal) {", a)
        method = src[a:b]
        js = r"""
const assert=require("node:assert/strict");
const events=new Map(), root={
  children:[],activeElement:null,querySelectorAll:()=>[select],
  appendChild(x){this.children.push(x);x.parent=this;return x;}
};
class El {
  constructor(tag){
    this.tagName=tag.toUpperCase();this.children=[];this.attr={};this.events={};
    this.style={};this.textContent="";this.disabled=false;
    this.classList={contains:()=>false,add:()=>{}};
    this.offsetTop=0;this.offsetHeight=32;this.clientHeight=160;this.scrollTop=0;
  }
  setAttribute(k,v){this.attr[k]=String(v);}
  getAttribute(k){return this.attr[k]??null;}
  removeAttribute(k){delete this.attr[k];}
  addEventListener(k,fn){(this.events[k]||=[]).push(fn);}
  dispatchEvent(e){for(const fn of this.events[e.type]||[])fn(e);}
  fire(type,extra={}){this.dispatchEvent({type,preventDefault(){},stopPropagation(){},...extra});}
  append(...nodes){for(const x of nodes){this.children.push(x);x.parent=this;}}
  appendChild(x){this.append(x);return x;}
  before(x){x.parent=this.parent;}
  remove(){this.removed=true;if(this.parent?.children)this.parent.children=this.parent.children.filter(x=>x!==this);}
  closest(){return{firstChild:{textContent:"Misc Targets"}};}
  focus(){root.activeElement=this;}
  getBoundingClientRect(){return{left:48,top:120,bottom:136,width:180};}
}
const opt=(v,t,s=false,d=false)=>Object.assign(new El("option"),{value:v,textContent:t,selected:s,disabled:d});
const select=new El("select");
select.value="";
select.selectedOptions=[opt("","Select Misc target",true,true)];
select.children=[select.selectedOptions[0],opt("logo","Logo"),
  Object.assign(new El("optgroup"),{label:"Status Box 1 fields",children:[opt("field","Row 1 label")]})];
const document={createElement:tag=>new El(tag)};
const window={
  innerWidth:360,innerHeight:700,
  matchMedia:()=>({get matches(){return window.innerWidth<=760;}}),
  addEventListener(k,fn){(events.get(k)||events.set(k,[]).get(k)).push(fn);},
  removeEventListener(k,fn){events.set(k,(events.get(k)||[]).filter(f=>f!==fn));},
  fire(k,e){for(const fn of events.get(k)||[])fn(e);}
};
const Card=new Function("window","document","Event","SV_CALIBRATION_MOBILE_MEDIA","return class {\n"+method+"\n}")(
  window,document,class Event{constructor(type,o){this.type=type;this.bubbles=o.bubbles;}},"(max-width: 760px)"
);
const card=new Card();card.shadowRoot=root;
let changes=0;select.addEventListener("change",()=>changes++);
card.attachCompactCalibrationSelectMenus();
const trigger=select.parent.children[0];
assert.equal(trigger.tagName,"BUTTON");
assert.equal(select.getAttribute("aria-hidden"),"true");
assert.equal(trigger.textContent,"Select Misc target");
trigger.fire("click");
let menu=root.children.at(-1);
assert.equal(menu.getAttribute("role"),"listbox");
assert.equal(menu.children.find(x=>x.textContent==="Select Misc target").disabled,true);
assert.ok(menu.children.some(x=>x.textContent==="Status Box 1 fields"));
menu.children.find(x=>x.textContent==="Logo").fire("click");
assert.equal(select.value,"logo");
assert.equal(changes,1);
assert.equal(menu.removed,true);
assert.equal(trigger.getAttribute("aria-expanded"),"false");
trigger.fire("click");
menu=root.children.at(-1);
menu.children.find(x=>x.textContent==="Logo").fire("click");
assert.equal(changes,1);
trigger.fire("click");
window.fire("keydown",{key:"Escape",preventDefault(){}});
assert.equal(trigger.getAttribute("aria-expanded"),"false");
trigger.fire("keydown",{key:"ArrowDown",preventDefault(){}});
assert.equal(trigger.getAttribute("aria-expanded"),"true");
window.fire("pointerdown",{composedPath:()=>[]});
assert.equal(trigger.getAttribute("aria-expanded"),"false");
assert.equal(card._closeCompactCalibrationMenu,null);
// Desktop uses the same popup owner so open menus are styleable on both screens.
window.innerWidth=1280;
const nativeSelect=new El("select");
nativeSelect.selectedOptions=[opt("one","One",true)];nativeSelect.children=[nativeSelect.selectedOptions[0]];
const desktop=new Card();desktop.shadowRoot={querySelectorAll:()=>[nativeSelect]};
desktop.attachCompactCalibrationSelectMenus();
assert.equal(nativeSelect.parent.children[0].tagName,"BUTTON");
assert.equal(nativeSelect.getAttribute("aria-hidden"),"true");
assert.equal(nativeSelect.tabIndex,-1);
console.log("Responsive calibration popup behavior: PASS");
"""
        proc = subprocess.run(
            ["node", "-e", "const method=" + json.dumps(method) + ";\n" + js],
            cwd=ROOT, capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)


if __name__ == "__main__":
    unittest.main()
