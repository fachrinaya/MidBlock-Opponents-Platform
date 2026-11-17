# MidBlock Opponents — working handoff

This folder contains the English prototype you accepted and the material needed
to understand, rebuild and extend it. The example is Luka Menalo preparing for
Persib vs Bali United on 22 November 2026, with evidence cut off at 17 November
2026, 00:00 Asia/Jakarta. It is a frozen example, not a live fixture feed.

## Open the prototype

Double-click `Open Prototype.command`, or run:

```sh
python3 run.py serve --open
```

Open `http://127.0.0.1:4182/english.html`. The preview serves only the report
directory and sends no-cache headers. The explicit English URL and versioned
assets prevent the earlier same-address language confusion. The accepted PDF
is `prototype/luka-menalo-bali-united-english.pdf`.

## Folder guide

| Folder/file | What it contains |
| --- | --- |
| `prototype/` | The accepted English HTML, assets, charts and PDF. Works without a database or AI. |
| `sections/` | Seven sections, each with prompt, logic, Python entry points, schema and real examples. |
| `pipeline/` | Portable acquisition, calculations, section generation, validation and rendering. |
| `prompts/shared.md` | English language, player voice, practical coaching and evidence rules shared across sections. |
| `config/report.json` | Frozen example configuration, additional threat IDs and Bedrock defaults. |
| `data/raw/snapshot.json` | User-approved read-only database export for offline calculation replay. |
| `examples/luka-menalo/` | Reviewed English narrative, evidence, provenance and original chart manifest. |
| `vendor/nutmeg/` | Pinned methodology, skills, core CLI and source attribution. |
| `vendor/wheels/` | Python dependency wheels for Python 3.11 on this Apple Silicon Mac. |
| `docs/` | Flow, analysis logic, data contract, AI/review rules, operations and validation. |
| `tests/` | Actual-data regression and failure-case checks. |
| `audit/original-research.zip` | Nutmeg handover bundle with original claims, runs, source queries and raw evidence. |
| `reference/original-prototype/` | Original multi-feature prototype and design/rating documentation. Its sample data is separate from the real report. |
| `work/` | Rebuilt evidence, section requests/drafts, review records and rendered reports. |

## Install and rebuild offline

Use Python 3.10 or newer; the supplied wheelhouse was tested with Python 3.11
on macOS Apple Silicon. Google Chrome is already available on this Mac.

```sh
./setup.sh
.venv/bin/python run.py doctor
.venv/bin/python run.py demo
```

The offline rebuild validates scope and source grain, computes the evidence
and contribution dossier, verifies that those numbers still match the reviewed
example, extracts each section, then renders the interactive report and PDF.
It writes `work/demo/report/english.html` and
`work/demo/report/opponent-report-english.pdf`.

For another platform, `setup.sh` installs from the pinned requirements through
pip. If Chrome/Chromium is unavailable, use
`.venv/bin/python -m playwright install chromium` or set `PDF_CHROMIUM_PATH`.
The browser binary itself is not bundled. Serving the accepted prototype needs
only Python's standard library; calculation and PDF rebuilds need setup.

## Work on one section

```sh
.venv/bin/python run.py section players --workspace work/demo
.venv/bin/python run.py section players --workspace work/demo --dry-run
```

The first command exports the approved example's input/output for that section.
The second saves the actual prompt, compact evidence, output schema and chart
references that would be sent to Haiku, without making an external call.

Section IDs are `verdict`, `style`, `shape`, `space`, `players`, `awareness`,
and `about`. See [the section map](docs/SECTION_MAP.md). Edit a section's
`prompt.md` to change future writing instructions. Calculations are shared so
sections cannot silently use different denominators; each `logic.md` points
to those functions.

## Generate a fresh Haiku draft

Copy `.env.example` to `.env` and configure your own Bedrock access. The default
model is Claude Haiku 4.5 through Amazon Bedrock. You can use a bearer token
or the standard AWS credential chain. Do not copy the original app's Indonesian
voice prompt into this flow; `prompts/shared.md` explicitly requires English.

```sh
.venv/bin/python run.py generate --workspace work/new --dry-run
.venv/bin/python run.py generate --workspace work/new
```

The second command makes six model calls: style, shape, space, players,
awareness, then verdict. About is assembled deterministically. Requests and raw
responses remain inspectable under the workspace. Every generated response is
an unreviewed draft. New generation invalidates prior workspace approval.

Review and edit `work/new/draft-narrative.json` against its evidence, then record
your review and render:

```sh
.venv/bin/python run.py approve --workspace work/new --reviewer 'Your name' --note 'Checked facts, units, sample scopes and coaching instructions'
.venv/bin/python run.py render --workspace work/new
.venv/bin/python run.py serve --workspace work/new --open
```

Approval is a human attestation, not an automated factual verdict. Rendering
binds the approved narrative and evidence by checksum and rejects stale review.
See [AI and review](docs/AI_AND_REVIEW.md).

## Refresh source data or change player

Configure a working PostgreSQL route in your own `.env`; source SQL is included.
Use your personal SSH key if a tunnel is needed. The package includes no secrets.

```sh
.venv/bin/python run.py acquire --player 'Luka Menalo' --as-of '2026-11-17T00:00:00+07:00' --output-dir data/raw/new-snapshot
.venv/bin/python run.py build --snapshot data/raw/new-snapshot/snapshot.json --workspace work/new
```

The next fixture is resolved from stored schedule data. The current identity
query targets Indonesia Super League / Liga 1. For another opponent, remove or
change the fixture-specific `additional_threat_ids` in `config/report.json`;
without that setting, additions are selected from crossing/scoring contributions.
The renderer uses the supplied player/team names, while the frozen accepted
prototype and original reference naturally retain the example's names.

Use a new workspace when changing source data. Run `build` with the new snapshot
before `generate`; do not reuse the approved Menalo narrative for changed evidence.
See [the data pipeline](docs/DATA_PIPELINE.md) and [operations](docs/OPERATIONS.md).

## Nutmeg and verification

```sh
.venv/bin/python tools/nutmeg.py --help
.venv/bin/python -m unittest discover -s tests -v
```

Nutmeg methodology is loaded into every AI request after checksum verification.
The included core CLI can record research runs and claims; the original audit
bundle already contains the actual report's ledger and run history. The demo's
local manifest records source/config/code checksums; that manifest alone is not
a Nutmeg claim ledger. See [Nutmeg integration](docs/NUTMEG.md) for recorded-run
commands and the difference between methodology, ledger and factual review.

The local snapshot and generated outputs are excluded by `.gitignore`. There
are no passwords, private keys, AWS tokens, database writes or deployments in
the handoff. Live PostgreSQL and Bedrock access require developer configuration;
the offline pipeline and model-request contracts are tested separately.
