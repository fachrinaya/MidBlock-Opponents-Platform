# Operations and extension guide

## Configuration ownership

`config/report.json` supplies the frozen example's display language, analysis
selection defaults and Bedrock model settings. The raw snapshot supplies the
actual player/team/fixture identity and cutoff; changing a name in config does
not change source records. Export a new snapshot to analyse another player.

Bedrock values in `.env` or the environment override the root `config/report.json` defaults. `--config` selects the data/threat-selection configuration; service settings remain in the root config or environment. Database
configuration is read only by acquisition. No command imports the original
MidBlock app, reads its `.env`, or depends on the former workspace path.

For live acquisition, copy `.env.example` to `.env` and supply your own password
or PostgreSQL URL. Do not commit that file. If required, establish an approved
SSH route first, using the personal fachrinaya key. Example:

```sh
SSH_HOST=your-approved-server SSH_USER=ubuntu ./tools/tunnel.sh
```

The helper defaults to `~/.ssh/id_ed25519`, with explicit identity selection,
and forwards local port 5433 to remote localhost:5432. The key is not included.
Use `SSH_KEY_FILE` to select your own key path. Server source-IP access still
has to be approved by your infrastructure team.

## A new match

1. Choose a timezone-aware evidence cutoff before the fixture.
2. Acquire a snapshot to a new raw-data directory. Inspect coverage before use.
3. Review `config/report.json`: remove the example's `additional_threat_ids` to
   use automatic contribution-based additions, or supply IDs present in that
   opponent's exported data.
4. Build into a new workspace with `--snapshot` and `--config` where needed.
5. Inspect the generated evidence, missing-detail rows and saved-rating audit.
6. Preview requests using `generate --dry-run`.
7. Generate drafts, fact-check and edit them, then record review and render.

The existing league resolver targets Indonesia. The rating source is a current
season table, so a fresh database export cannot reconstruct an earlier rating
snapshot unless an archived rating source is supplied. Missing or post-cutoff
featured ratings may prevent a valid report instead of being silently invented.

## Workspace files

| File | Meaning |
| --- | --- |
| `evidence.json` | Computed, scoped input to every section. |
| `threat-dossier.json` | Player contributions with known-match counts and separate goal scope. |
| `run-manifest.json` | Local build inputs/config/code hashes and Python version. |
| `charts/` | Actual current-evidence chart screenshots for model requests. |
| `sections/<folder>/request.json` | System prompt, compact evidence, chart references and safe settings. |
| `sections/<folder>/raw_model_response.json` | Raw structured draft, retained before identity acceptance. |
| `draft-narrative.json` | Complete assembled model draft; not approved. |
| `reviewed-narrative.json` | Text explicitly accepted by a reviewer. |
| `review.json` | Reviewer attestation bound to the exact evidence and narrative hashes. |
| `provenance.json` | Model/editorial origin; not a fact-check certificate. |
| `report/` | Rendered English page, charts, PDF and layout checks. |

Rebuilding data changes the evidence. A prior review becomes stale when its
hash no longer matches. Real full generation also removes the previous approval.
The frozen accepted prototype is never overwritten by a new draft command.

## Common failures

- **Port already in use:** keep the existing preview open, or use
  `run.py serve --port 4183 --open`. Stop a preview with Ctrl-C.
- **Dependency missing:** run `setup.sh` from this folder, then use
  `.venv/bin/python` for pipeline commands.
- **No browser:** install Playwright Chromium or set `PDF_CHROMIUM_PATH`.
- **Database unreachable:** check the route/tunnel, local port and approved
  source IP. The offline demo still works.
- **Bedrock access denied:** check your own credential chain/token, region and
  model access. No credentials are bundled or inferred from the original app.
- **Approved example differs:** source numbers have changed. Generate and review
  new text rather than attaching the old approved narrative to changed evidence.
- **Review missing/stale:** review the current full narrative and use `approve`
  again; do not edit hash values manually.
- **Schema or identity rejection:** inspect the section request/raw response,
  correct the prompt or draft, and keep the rejected response out of reviewed text.

## Dependencies and moving the folder

The launch/setup helpers locate a supported Python even when Finder provides a minimal PATH. Set `PYTHON_BIN` to override that choice. The source code uses paths relative to this folder. A Python virtual environment
contains absolute installation paths: after moving the whole folder, recreate
`.venv` using `setup.sh`. Dependency wheels are included for Python 3.11/macOS
Apple Silicon; another platform may need pip downloads. The static report can
be opened/served without those analysis dependencies.
