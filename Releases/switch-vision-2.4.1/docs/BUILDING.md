# Building Switch Vision

Run the build from the project root.

## Build an exact public version

```bash
python3 build.py -v <version>
```

Automatic semantic-version bumps are supported:

```bash
python3 build.py --bump patch
python3 build.py --bump minor
python3 build.py --bump major
```

A wildcard selects the next free patch in a release line:

```bash
python3 build.py -v 1.9.x
```

Add `--gold` only when producing an officially promoted Gold baseline.

## Public release metadata

A normal non-Gold build writes manifest status:

```text
public-release
```

A Gold build writes:

```text
gold
```

The README and current release notes must describe the version being built. Historical changelog entries are never rewritten.

## Build output

A successful build for `<version>` creates:

```text
Releases/
├── switch-vision-<version>/
├── switch-vision-<version>.zip
└── switch-vision-<version>.zip.sha256

Switch_Vision_v<version>_source.zip
Switch_Vision_v<version>_SHA256SUMS.txt
```

The `.zip.sha256` file is safe to publish beside the public release ZIP. `Switch_Vision_v<version>_SHA256SUMS.txt` is the private build ledger covering both the public release and private source ZIP and must not be uploaded publicly.

## Installable release contents

The release archive includes:

- README, changelog, and current release notes;
- native Switch Vision integration and panel;
- dashboard card and assets;
- exact-model device registry;
- examples;
- installation, upgrade, field-reference, troubleshooting, support, and build documentation;
- public contribution and security guidance.

Discovery, SNMP2MQTT, and UniFi2MQTT remain separate repository-managed projects and are not bundled in the main release.

## Private source archive allowlist

The private source ZIP begins at the archive root and contains only approved project source material:

```text
.gitattributes
.gitignore
README.md
CHANGELOG.md
RELEASE_NOTES.md
CONTRIBUTING.md
SECURITY.md
VERSION
build.py
src/
Releases/switch-vision-<version>/
```

A `LICENSE` file is included automatically when one exists at the project root.

The source archive must not contain:

- itself or previous source archives;
- release ZIPs;
- unrelated release folders;
- tests unless explicitly requested;
- `__pycache__`, `.pytest_cache`, `.pyc`, or `.pyo` files;
- backup, temporary, PSD, Git, editor, or scratch artefacts;
- Gold-only documents in a non-Gold source archive.

## Version propagation

The build aligns:

- root `VERSION`;
- integration manifest and backend panel version;
- panel and card JavaScript versions;
- release manifest and resource URL;
- versioned example filenames and contents;
- extracted release folder and archives.

`src/js/switch-vision.js` is authoritative and is copied to the custom-component card source during the build.

## Validation

A public build validates:

- semantic version propagation;
- required source files;
- supported-device document generation;
- card-source synchronisation;
- shell LF endings and executable entrypoints;
- Python, JavaScript, JSON, YAML, and archive integrity checks performed by the release process;
- public documentation markers;
- repository-managed app exclusion from the main release/source archives;
- source/release package hygiene.

A failed build must not be published.

## Components requiring runtime action

- **Discovery changed:** publish/update the separate Discovery repository app; Home Assistant/Installer updates that app independently of the main release.
- **Custom component changed:** replace `/config/custom_components/switch_vision/` and restart Home Assistant Core.
- **Dashboard assets changed:** replace `/config/www/switch-vision/` and hard-refresh the browser.
- **Registry or Discovery mapping changed:** update the owning repository/runtime, then run Discovery once to regenerate current output.
