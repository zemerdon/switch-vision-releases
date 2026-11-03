# Switch Vision Core release provenance

Canonical Core engineering source, branches, reviews and Git history live locally on `sv-dev`, independently mirrored to `sv-release-lab`. GitHub hosts deliberate public release projections and customer artifacts; it is not the authoritative development repository, continuity store or private backup. Historical public tags and assets remain immutable.

## Current release model

The reviewed publishing chain is:

1. Develop a bounded change in a deliberate non-`main` local branch/worktree, preserving component version and source/dependency contracts.
2. Run relevant product-owned tests, review the diff, and guarded-merge the approved source into clean local canonical `main`. A shipped source/runtime change receives the required new component version before release-candidate acceptance.
3. Run `sv release check core` for a reusable, non-authorizing development-validation attestation bound to the exact source/version/dependency set.
4. On an explicit local-first request, `sv release prepare core <version>` performs the focused publication-specific checks and projects the exact candidate into Switch Vision Local without publishing. An explicit public release request uses `sv release publish core <version>`, which prepares when needed.
5. Before public mutation, the guarded release controller exercises the required real `sv-haos-test` practical, including exact candidate/rollback and applicable authenticated Native faceplate/Calibration checks. Failed gates block publication.
6. Only after passing the practical and exact-source identity rechecks may the isolated publisher project the reviewed version/tag and install/source ZIP plus checksum artifacts to the public GitHub release channel. Temporary transport PRs are not ordinary development merges or source authority.
7. Independently verify the exact public tag, source identity and published assets. Reconcile any ambiguous or partially completed publisher before retry; never replace an independently verified release.
8. Verify the published version and served source on `sv-haos-test`, close the canonical release journal, clean disposable transport/worktrees and verify the independent local recovery mirror.

Release state and transport checkpoints are owned by the one local release transaction journal; the reusable development attestation is the only other durable release-validation owner. `sv audit` (which includes the exhaustive regression engine) is explicit deep health, not an automatic release gate. Forum mutation and outbound mail require separate authorization. No development or documentation edit by itself authorizes publication.

Provenance remains: canonical local source/version/dependency identities -> reviewed local `main` -> exact staged candidate and real practical -> guarded public tag/artifacts -> independent verification and fixture parity.

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
