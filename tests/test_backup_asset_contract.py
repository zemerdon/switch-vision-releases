from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).parents[1]
SOURCE = (ROOT / "src/custom_components/switch_vision/__init__.py").read_text(encoding="utf-8")


def test_backup_asset_api_is_narrow_admin_only_and_integrity_checked():
    assert '"switch_vision/get_backup_asset"' in SOURCE
    assert '"switch_vision/put_backup_asset"' in SOURCE
    assert SOURCE.count("@websocket_api.require_admin") >= 3
    assert "MAX_BACKUP_ASSET_BYTES = 16 * 1024 * 1024" in SOURCE
    assert 'result["backup_api"] = 2 if stock_assets is not None else 1' in SOURCE
    assert 'result[f"custom_{kind}"] = custom_files' in SOURCE
    assert 'STOCK_ASSET_MANIFEST_PATH = Path(__file__).with_name("stock-assets.json")' in SOURCE
    assert 'if digest != expected:' in SOURCE
    assert "selected_name != Path(selected_name).name" in SOURCE
    assert "Path(selected_name).suffix.lower() not in ASSET_EXTENSIONS" in SOURCE
    assert "base64.b64decode(text.encode(\"ascii\"), validate=True)" in SOURCE
    assert "hashlib.sha256(data).hexdigest()" in SOURCE
    assert "Switch Vision backup asset SHA-256 does not match the manifest." in SOURCE
    assert "os.replace(temporary, path)" in SOURCE


def test_backup_asset_commands_are_registered():
    assert "websocket_api.async_register_command(hass, websocket_get_backup_asset)" in SOURCE
    assert "websocket_api.async_register_command(hass, websocket_put_backup_asset)" in SOURCE


def test_stock_asset_manifest_exactly_matches_release_owned_visuals():
    manifest_path = ROOT / "src/custom_components/switch_vision/stock-assets.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["schema"] == "switch-vision-stock-assets-v1"
    expected = {}
    for kind in ("logos", "faceplates"):
        rows = {}
        for path in sorted((ROOT / "src" / kind).iterdir()):
            if path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
                rows[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        expected[kind] = rows
    assert payload["assets"] == expected
