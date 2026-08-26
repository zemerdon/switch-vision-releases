#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import re
from pathlib import Path

SCHEMA = "switch-vision-forum-desired-state-v1"
ALLOWED = {
    "welcome": (25, 5, 5, "forum/topics/05_Welcome_to_Switch_Vision.bbcode"),
    "support_request": (11, 71, 71, "forum/topics/71_Support_Request_Template.bbcode"),
    "start_here": (54, 81, 81, "forum/topics/81_Start_Here_Install_Update.bbcode"),
    "using": (54, 83, 83, "forum/topics/83_Using_Switch_Vision.bbcode"),
    "support_my_switch": (54, 85, 85, "forum/topics/85_Support_My_Switch.bbcode"),
    "troubleshooting": (11, 86, 86, "forum/topics/86_Troubleshooting_Recovery.bbcode"),
    "core_reference": (54, 95, 95, "forum/topics/95_Reference_Core_Dashboard_Settings.bbcode"),
    "components_reference": (54, 96, 96, "forum/topics/96_Reference_Components.bbcode"),
    "advanced_yaml": (54, 97, 97, "forum/topics/97_Advanced_Custom_Lovelace_YAML.bbcode"),
    "calibration": (54, 99, 99, "forum/topics/99_Calibration_Faceplates_Card_Configuration.bbcode"),
}
HEX = re.compile(r"^[0-9a-f]{64}$")
CONTRIBUTION_ID_RE = re.compile(r"\bSV-\d{4}-\d{6}\b", re.IGNORECASE)
MAC_RE = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b")
IPV4_RE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
SECRET_WORD_RE = re.compile(
    r"(?i)\b(?:snmp_community|mqtt_password|api_key|support_contributor_value|password)\b\s*[:=]"
)
WORKFLOW_DISCLOSURE = (
    "automatically maintained",
    "maintained automatically",
    "managed automatically",
    "published automatically",
    "forum publisher",
    "index generated from",
    "index is generated",
    "generated only from",
    "automated workflow",
)


def canonical(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.endswith("\n"):
        text = text[:-1]
    return text


def body_sha(text: str) -> str:
    return hashlib.sha256(canonical(text).encode("utf-8")).hexdigest()


def privacy_guard(text: str, path: str) -> None:
    if CONTRIBUTION_ID_RE.search(text):
        raise SystemExit(f"{path}: contribution identifier detected")
    if MAC_RE.search(text):
        raise SystemExit(f"{path}: MAC address detected")
    if SECRET_WORD_RE.search(text):
        raise SystemExit(f"{path}: secret-like assignment detected")
    for candidate in IPV4_RE.findall(text):
        try:
            address = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        if address.is_private or address.is_loopback or address.is_link_local:
            raise SystemExit(f"{path}: non-public IPv4 address detected")
    lowered = text.casefold()
    for marker in WORKFLOW_DISCLOSURE:
        if marker in lowered:
            raise SystemExit(f"{path}: internal forum workflow disclosure detected: {marker}")


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path}: expected JSON object")
    return data


def validate(manifest_path: Path, base_path: Path | None = None) -> None:
    data = load_json(manifest_path)
    if data.get("schema") != SCHEMA:
        raise SystemExit("forum desired-state schema mismatch")
    revision = data.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision <= 0:
        raise SystemExit("forum desired-state revision must be a positive integer")
    if data.get("forum_impact") != "update":
        raise SystemExit("forum_impact must be update")
    if not isinstance(data.get("release_context"), dict):
        raise SystemExit("release_context must be an object")

    rows = data.get("posts")
    if not isinstance(rows, list) or len(rows) != len(ALLOWED):
        raise SystemExit("manifest must contain the complete exact managed-post set")

    seen: set[str] = set()
    hash_errors: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit("post row must be an object")
        name = row.get("name")
        if not isinstance(name, str) or name not in ALLOWED or name in seen:
            raise SystemExit(f"invalid/duplicate managed target: {name!r}")
        seen.add(name)
        expected_forum, expected_topic, expected_post, expected_path = ALLOWED[name]
        if (
            row.get("forum_id"),
            row.get("topic_id"),
            row.get("post_id"),
            row.get("body_path"),
        ) != (expected_forum, expected_topic, expected_post, expected_path):
            raise SystemExit(f"{name}: exact target/path allowlist mismatch")
        if row.get("topic_id") == 74 or row.get("post_id") == 74:
            raise SystemExit("Topic 74 is reserved for the supported-device reconciler")
        subject = row.get("subject")
        if not isinstance(subject, str) or not subject.strip() or any(ch in subject for ch in "\r\n[]\x00"):
            raise SystemExit(f"{name}: invalid subject")
        declared = row.get("body_sha256")
        if not isinstance(declared, str) or not HEX.fullmatch(declared):
            raise SystemExit(f"{name}: invalid body_sha256")
        body_path = Path(expected_path)
        if not body_path.is_file():
            raise SystemExit(f"{name}: missing BBCode file {expected_path}")
        body = body_path.read_text(encoding="utf-8")
        privacy_guard(body, expected_path)
        actual = body_sha(body)
        print(f"{name}: body_sha256={actual}")
        if actual != declared:
            hash_errors.append(f"{name}: declared {declared}, actual {actual}")

    if seen != set(ALLOWED):
        raise SystemExit("managed target set mismatch")
    if hash_errors:
        raise SystemExit("body hash mismatch(es):\n" + "\n".join(hash_errors))

    if base_path is not None and base_path.exists():
        base_raw = base_path.read_bytes()
        current_raw = manifest_path.read_bytes()
        if base_raw != current_raw:
            base = load_json(base_path)
            base_revision = base.get("revision")
            if isinstance(base_revision, bool) or not isinstance(base_revision, int):
                raise SystemExit("base desired-state revision is invalid")
            if revision <= base_revision:
                raise SystemExit(
                    f"desired-state changed without revision increment: base={base_revision}, current={revision}"
                )

    print(f"forum desired-state validation: PASS; revision={revision}; posts={len(rows)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", nargs="?", default="forum/desired-state.json")
    parser.add_argument("--base")
    args = parser.parse_args()
    validate(Path(args.manifest), Path(args.base) if args.base else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
