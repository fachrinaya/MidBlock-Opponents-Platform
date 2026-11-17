# Where they play

Turn recorded activity concentration into practical positioning and scanning responsibilities.

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

`space.season`, `space.last5`, the fixture/player context, and relevant prior section interpretations.

## Output

`space_notes.season/last5` and chart explanations for `space-season` and `space-last5`.

## Run from the package root

```sh
python3 run.py demo
python3 run.py section space --workspace work/demo
python3 run.py section space --workspace work/demo --dry-run
```

The normal section command prepares inputs and extracts the approved example. Dry-run prepares a request without an external call. To request a new Haiku draft after configuring your own Bedrock access:

```sh
python3 run.py section space --workspace work/demo --generate
```

A new model response is a draft. Review its facts and player instructions before assembling it into a final report.

Render an approved assembled narrative with:

```sh
python3 run.py render --workspace work/demo
```

See the root README for environment setup, full-generation order and review commands.
