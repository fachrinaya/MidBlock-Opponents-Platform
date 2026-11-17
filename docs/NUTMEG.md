# Nutmeg: methodology, runs and evidence

Nutmeg has two distinct roles in this handoff.

## Methodology inside each Haiku request

`pipeline/sections.py` reads the bundled analysis/compute skills and accuracy /
metric-misuse documents. It verifies their SHA-256 hashes against the pinned
manifest before using them. YAML tool permissions are stripped. The model is
told these references are methodology, not player-specific evidence and not
permission to run commands or claim a live provider-docs lookup.

The pinned upstream source and revision are in `vendor/nutmeg/manifest.json`
and `SOURCE.txt`. Files are kept verbatim for integrity. Some reference prose
retains historical Codex installation paths; the packaged Python runtime reads
its files relative to this folder and does not require those paths.

## Core research CLI and original audit trail

The full core CLI is included, with no Codex installation dependency:

```sh
.venv/bin/python tools/nutmeg.py --help
```

`audit/original-research.zip` is an actual `nutmeg bundle --raw yes` handover,
included after the user's explicit choice to include raw evidence. It preserves
the original question, plan, claim ledger, queries, run records, drafts and final
artifacts. Rejected drafts inside that archive are history, not the accepted
English player text. The main portable runtime is `pipeline/`; original scripts
in the archive may refer to the historical application layout.

The frozen source is original run R7, corrected evidence R19, contributions R24,
coaching draft R26, reviewed coaching R28, English translation R32, and the
final explicit-English page/PDF build R34. Later packaging runs test the portable
rebuild. The English narrative was substantially edited and translated by Codex.

## Record a new research run

From this folder, establish a local Git root if needed, then create a project:

```sh
git init
.venv/bin/python tools/nutmeg.py new next-opponent --question 'What should this player prepare for against the next league opponent?' --data-in-git no
.venv/bin/python tools/nutmeg.py plan choose --kind source --choice 'Frozen or read-only league snapshot before a timezone-aware cutoff' --why 'Prevent future-data leakage and preserve provenance' --rests-type user --rests-ref 'Opponent report handoff scope'
.venv/bin/python tools/nutmeg.py plan check
```

Follow the configured Nutmeg plan/run approval level. The portable recorded
demo entry point writes all generated files to the core's recorded output folder:

```sh
.venv/bin/python tools/nutmeg.py run tools/recorded_demo.py --input data/raw/snapshot.json --input examples/luka-menalo --input config --input pipeline --input sections --interpreter .venv/bin/python
```

The core prints the real run ID. Add computed claims with that ID and snapshots
through `claim add`, cite claims in your report, then run `check` and `workspace`.
For live model generation, declare the service and transmitted fields on the
run card. Use the core's source, claim and approval workflow rather than calling
ordinary local manifests a verified claim ledger.

The package's ordinary `run.py demo` is a convenient local replay. Its
`run-manifest.json` hashes source/config/code and evidence; it is not automatically
registered with Nutmeg. `tools/recorded_demo.py` is the explicit bridge when a
recorded run is wanted. Public publishing/sign-off is separate from this local
handoff and must follow your team's Nutmeg publishing requirements.
