# Switch Vision Core release provenance

This repository contains the public Switch Vision Core/dashboard source and
release history.

## Current release model

For future Switch Vision Core releases, the intended provenance chain is:

1. The complete editable Core source is committed to this repository.
2. `VERSION` and all version-bearing runtime files identify the same release.
3. `Releases/switch-vision-<version>/` is generated from that source.
4. CI verifies source-to-release parity before merge.
5. The exact release commit is merged to `main`.
6. One annotated version tag is created for that exact release commit.
7. The install ZIP, source ZIP, and SHA-256 checksum artifacts are generated
   from the validated release source.
8. Published release artifacts are not silently replaced with different
   content under the same version.

The goal is a simple provenance relationship:

    version
      -> exact Git commit
      -> annotated version tag
      -> validated source tree
      -> validated release tree
      -> published install/source artifacts

## Historical tags

Older Switch Vision Core tags predate the current source-transparent release
workflow.

A number of historical version tags point to shared repository commits. Those
tags are retained unchanged because rewriting or deleting public historical
tags would itself damage release provenance for existing users and references.

For those historical releases, a Git tag should therefore not automatically
be interpreted as a unique snapshot of the exact source used to build that
version.

Where an explicitly published Switch Vision source archive and install archive
exist for an historical release, those attached release artifacts and their
published SHA-256 hashes are the authoritative release material.

Historical tags are preserved for compatibility and reference only.

## Core v2.2.2 source baseline

Core v2.2.2 is the first historical Core release whose authoritative source has
also been restored to normal Git history in this repository.

The repository now contains:

- `src/` — editable Core source;
- `build.py` — release build tooling;
- `VERSION` — Core release identity;
- `Releases/switch-vision-2.2.2/` — generated install tree;
- `tools/check_core_release_parity.py` — source/release parity validation;
- `.github/workflows/validate-core-source.yml` — continuous parity validation.

The restored `Releases/switch-vision-2.2.2/` tree was verified byte-for-byte
against the previously published v2.2.2 install ZIP contents before being
committed.

## Tag policy going forward

New Core releases should use:

    <version>

as the release tag format currently used by the Core repository.

Each new version tag should:

- be annotated;
- identify exactly one release version;
- resolve to the exact release commit;
- not be moved after publication;
- not share its release commit merely as a substitute for missing historical
  source snapshots.

Existing historical tags are explicitly exempt from this policy and must not
be rewritten merely to make the old history look cleaner.

## Release integrity

Release preparation should verify at minimum:

- clean Git worktree;
- Core source/release parity;
- consistent `VERSION` and manifest versions;
- Python compilation checks;
- no `__pycache__`, `.pyc`, `.pyo`, or other generated cache material;
- exact install asset name;
- SHA-256 hashes for published install/source artifacts;
- install ZIP contents correspond to the validated release tree.

Release artifacts should only be published after the exact source state has
been committed and reviewed.

## Independent component versions

Switch Vision Discovery, SNMP2MQTT Core, the SNMP2MQTT Home Assistant app,
UniFi2MQTT, and Installer have independent repositories and version streams.

Their tags identify those components only and do not need to match the Core
version number.
