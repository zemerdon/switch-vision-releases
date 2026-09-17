from pathlib import Path

SOURCE = (Path(__file__).parents[1] / "src/custom_components/switch_vision/__init__.py").read_text(encoding="utf-8")


def test_backup_asset_api_is_narrow_admin_only_and_integrity_checked():
    assert '"switch_vision/get_backup_asset"' in SOURCE
    assert '"switch_vision/put_backup_asset"' in SOURCE
    assert SOURCE.count("@websocket_api.require_admin") >= 3
    assert "MAX_BACKUP_ASSET_BYTES = 16 * 1024 * 1024" in SOURCE
    assert 'result["backup_api"] = 1' in SOURCE
    assert "selected_name != Path(selected_name).name" in SOURCE
    assert "Path(selected_name).suffix.lower() not in ASSET_EXTENSIONS" in SOURCE
    assert "base64.b64decode(text.encode(\"ascii\"), validate=True)" in SOURCE
    assert "hashlib.sha256(data).hexdigest()" in SOURCE
    assert "Switch Vision backup asset SHA-256 does not match the manifest." in SOURCE
    assert "os.replace(temporary, path)" in SOURCE


def test_backup_asset_commands_are_registered():
    assert "websocket_api.async_register_command(hass, websocket_get_backup_asset)" in SOURCE
    assert "websocket_api.async_register_command(hass, websocket_put_backup_asset)" in SOURCE
