"""Prevent blocking stock-manifest file access on the Home Assistant event loop."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "custom_components"
    / "switch_vision"
    / "__init__.py"
)


class StockAssetManifestAsyncContractTests(unittest.TestCase):
    def test_calibration_async_handlers_load_manifest_in_executor(self) -> None:
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        expected = {
            "handle_save",
            "websocket_get_calibration",
            "websocket_approve_stock_artwork",
        }
        found: set[str] = set()
        for fn in ast.walk(tree):
            if not isinstance(fn, ast.AsyncFunctionDef) or fn.name not in expected:
                continue
            found.add(fn.name)
            calls = [node for node in ast.walk(fn) if isinstance(node, ast.Call)]
            direct = [
                node
                for node in calls
                if isinstance(node.func, ast.Name)
                and node.func.id == "_load_stock_asset_manifest"
            ]
            self.assertFalse(
                direct,
                f"{fn.name} must not synchronously read the manifest on the event loop",
            )
            executor_calls = [
                node
                for node in calls
                if isinstance(node.func, ast.Attribute)
                and node.func.attr == "async_add_executor_job"
                and node.args
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id == "_load_stock_asset_manifest"
            ]
            self.assertTrue(executor_calls, f"{fn.name} must offload the manifest read")
        self.assertEqual(found, expected)

    def test_other_manifest_readers_remain_executor_scoped(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("await hass.async_add_executor_job(_list_assets)", source)
        self.assertIn(
            "await hass.async_add_executor_job(_verified_latest_reset_revisions)",
            source,
        )


if __name__ == "__main__":
    unittest.main()
