# About this report

Show the scope, data coverage, provenance, review status and interpretation limits that make the briefing understandable and checkable.

## Files

| File | Purpose |
| --- | --- |
| `prompt.md` | Instructions supplied when generating this section. |
| `logic.md` | Exact calculations, selection rules and interpretation boundaries. |
| `pipeline.py` | Callable input/extraction/validation entry points. |
| `input.json` | Example section input, generated from the frozen evidence. |
| `output.json` | Approved example output, extracted from the reviewed English narrative. |

The frozen JSON examples are included here. The demo writes fresh section files under work/demo/sections/; do not invent replacement numbers manually.

## Input

`meta`, fixture and source timestamps, `disclosures`, `data_quality`, rating audit/pools, source-run metadata, model provenance and factual/editorial review records.

## Output

Deterministic report metadata and disclosures, rendered from evidence/provenance. This section does not require a Haiku call.

## Run from the package root

```sh
python3 run.py demo
python3 run.py section about --workspace work/demo
python3 run.py section about --workspace work/demo --dry-run
```

The normal section command prepares inputs and extracts the approved example. Dry-run prepares a request without an external call. To request a new Haiku draft after configuring your own Bedrock access:

```sh
python3 run.py section about --workspace work/demo --generate
```

About is deterministic. The generate path does not need a model call for this section.

Render an approved assembled narrative with:

```sh
python3 run.py render --workspace work/demo
```

See the root README for environment setup, full-generation order and review commands.
