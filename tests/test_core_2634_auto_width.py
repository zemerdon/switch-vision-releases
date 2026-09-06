from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JS=(ROOT/"src/js/switch-vision.js").read_text()
INIT=(ROOT/"src/custom_components/switch_vision/__init__.py").read_text()
FLOW=(ROOT/"src/custom_components/switch_vision/config_flow.py").read_text()
def test_auto_width_default_and_original_responsive_behaviour():
 assert 'FACEPLATE_WIDTH_MODES = ("auto", "800", "1024", "custom")' in INIT
 assert 'CONF_FACEPLATE_WIDTH_MODE: "auto"' in INIT
 assert 'effective = None if mode == "auto"' in INIT
 assert '"auto":"Auto (fit dashboard)"' in FLOW
 assert 'faceplateMaxWidth = this._globalFaceplateWidthMode === "auto" ? 2048' in JS
 assert 'style="width:100%;max-width:${faceplateMaxWidth}px;margin-inline:auto"' in JS
 assert 'auto width' in JS and 'native 2048 × 448' in JS
