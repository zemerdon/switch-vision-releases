from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "src" / "devices" / "supported_devices.json"


def _rows() -> dict[str, dict]:
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {
        str(row.get("model")): row
        for row in payload.get("devices", [])
        if isinstance(row, dict) and row.get("model")
    }


def test_exact_model_faceplate_matrix() -> None:
    rows = _rows()

    expected = {
        # Exact five-port UniFi chassis.
        "USW Flex": (
            "faceplates/unifi-5rj45.png",
            "default_unifi_5_rj45",
            5,
            0,
        ),
        "USW Flex Mini": (
            "faceplates/usw-flex-mini.png",
            "usw_flex_mini",
            5,
            0,
        ),
        # Exact eight-RJ45 UniFi chassis.
        "USW-Lite-8-PoE": (
            "faceplates/unifi-8rj45.png",
            "default_unifi_8_rj45",
            8,
            0,
        ),
        # Exact eight-RJ45 plus two-optical UniFi chassis.
        "USW-Enterprise-8-PoE": (
            "faceplates/unifi-8-rj45-2sfp.png",
            "unifi_8_rj45_2sfp",
            8,
            2,
        ),
        "USW Pro XG 8 PoE": (
            "faceplates/unifi-8-rj45-2sfp.png",
            "unifi_8_rj45_2sfp",
            8,
            2,
        ),
        # Exact 24-RJ45 plus four-optical UniFi chassis.
        "USW Pro HD 24 PoE": (
            "faceplates/unifi-24-rj45-4sfp-inline.png",
            "unifi_24_rj45_4sfp_inline",
            24,
            4,
        ),
        # Exact high-density optical chassis.
        "USW Pro Aggregation": (
            "faceplates/unifi-32sfp.png",
            "unifi_32sfp",
            0,
            32,
        ),
        # Owner-calibrated compact UniFi chassis.
        "USW-16-PoE": (
            "faceplates/unifi-16rj45-2sfp.png",
            "unifi_16_rj45_2sfp",
            16,
            2,
        ),
        "US 16 PoE 150W": (
            "faceplates/unifi-16rj45-2sfp.png",
            "unifi_16_rj45_2sfp",
            16,
            2,
        ),
        "UDM Pro": (
            "faceplates/unifi-9rj45-2sfp.png",
            "unifi_9_rj45_2sfp",
            9,
            2,
        ),
        "UniFi Dream Machine PRO SE": (
            "faceplates/unifi-9rj45-2sfp.png",
            "unifi_9_rj45_2sfp",
            9,
            2,
        ),
        "UDM Pro Max": (
            "faceplates/unifi-9rj45-2sfp.png",
            "unifi_9_rj45_2sfp",
            9,
            2,
        ),
        # USW WAN has one real rear management RJ45 in the API contract,
        # while the faceplate intentionally renders only the three front SFP+.
        "USW WAN": (
            "faceplates/unifi-3sfp.png",
            "unifi_3sfp",
            1,
            3,
        ),
    }

    for model, (faceplate, profile, rj45, uplinks) in expected.items():
        assert model in rows, model
        row = rows[model]
        ports = row.get("ports") or {}
        visuals = row.get("visuals") or {}

        assert row.get("dashboard_support") is True, model
        assert row.get("default_faceplate") == faceplate, model
        assert row.get("calibration_profile") == profile, model
        assert ports.get("rj45") == rj45, model
        assert ports.get("uplinks") == uplinks, model
        assert visuals.get("recommended_faceplate") == faceplate, model
        assert visuals.get("calibration_profile") == profile, model
        assert (ROOT / "src" / faceplate).is_file(), model


def test_known_good_exact_unifi_visuals_stay_exact() -> None:
    rows = _rows()
    expected = {
        "US 8 60W": (
            "faceplates/unifi-8rj45.png",
            "default_unifi_8_rj45",
        ),
        "US-8-150W": (
            "faceplates/unifi-8-rj45-2sfp.png",
            "unifi_8_rj45_2sfp",
        ),
        "USW Flex 2.5G 5": (
            "faceplates/unifi-5rj45.png",
            "default_unifi_5_rj45",
        ),
        "US XG 16": (
            "faceplates/unifi-4-rj45-12sfp.png",
            "unifi_4_rj45_12sfp",
        ),
        "USW Ultra": (
            "faceplates/unifi-8rj45.png",
            "default_unifi_8_rj45",
        ),
        "UCG Ultra": (
            "faceplates/unifi-5rj45.png",
            "default_unifi_5_rj45",
        ),
    }

    for model, (faceplate, profile) in expected.items():
        assert model in rows, model
        row = rows[model]
        visuals = row.get("visuals") or {}
        assert row.get("default_faceplate") == faceplate, model
        assert row.get("calibration_profile") == profile, model
        assert visuals.get("recommended_faceplate") == faceplate, model
        assert visuals.get("calibration_profile") == profile, model
        assert (ROOT / "src" / faceplate).is_file(), model


def test_models_without_an_exact_asset_keep_truthful_physical_counts() -> None:
    rows = _rows()
    # These layouts do not have an exact bundled faceplate today.  Do not
    # "improve" them by selecting a visually similar but physically false asset.
    expected_counts = {
        "USW Flex 2.5G 8 PoE": (9, 1),
        "USW Lite 16 PoE": (16, 0),
    }
    for model, (rj45, uplinks) in expected_counts.items():
        assert model in rows, model
        ports = rows[model].get("ports") or {}
        assert ports.get("rj45") == rj45, model
        assert ports.get("uplinks") == uplinks, model


if __name__ == "__main__":
    test_exact_model_faceplate_matrix()
    test_known_good_exact_unifi_visuals_stay_exact()
    test_models_without_an_exact_asset_keep_truthful_physical_counts()
    print("Core exact-model faceplate matrix: PASS")
