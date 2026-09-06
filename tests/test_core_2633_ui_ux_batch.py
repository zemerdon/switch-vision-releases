from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "src/js/switch-vision.js").read_text(encoding="utf-8")
INIT = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text(encoding="utf-8")
FLOW = (ROOT / "src/custom_components/switch_vision/config_flow.py").read_text(encoding="utf-8")

def test_test_mode_button_uses_existing_nudge_path():
    assert 'editable.type === "calibration_button" || editable.type === "test_mode_button"' in JS

def test_zero_port_profile_is_warning_not_error():
    assert 'warnings.push("No port positions configured.' in JS
    assert 'errors.push("The profile contains no RJ45 or SFP/uplink positions.")' not in JS
    assert 'calibration must contain at least one RJ45 or optical port' not in INIT

def test_status_background_and_led_visibility_are_persistent_profile_controls():
    for token in ("status-box-color-show", "status2-box-color-show", "show-link-leds", "show-activity-leds"):
        assert token in JS
    assert 'panel.background_show === false ? "transparent"' in JS
    assert 'ui?.show_link_leds === false' in JS
    assert 'ui?.show_activity_leds === false' in JS

def test_faceplate_width_is_global_core_setting():
    for token in ("CONF_FACEPLATE_WIDTH_MODE", "CONF_FACEPLATE_CUSTOM_WIDTH", "FACEPLATE_WIDTH_MODES"):
        assert token in INIT
        assert token in FLOW
    assert '"faceplate_width": _faceplate_width_settings(entry)' in INIT
    assert '"faceplate_width": faceplate_width_settings' in INIT
    assert '_globalFaceplateWidth' in JS

def test_faceplate_labels_are_explicit_media_counts():
    data = json.loads((ROOT / "src/faceplates/catalog.json").read_text(encoding="utf-8"))
    labels = {row["filename"]: row["display_name"] for row in data["faceplates"]}
    assert labels["unifi-32sfp.png"] == "UniFi · 28 × SFP+ · 4 × SFP28"
    assert labels["24rj45-4sfp.png"] == "24 × RJ45 · 4 × SFP"
