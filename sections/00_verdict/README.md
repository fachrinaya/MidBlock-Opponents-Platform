# What to expect

Give the player a short, useful match plan that combines the report’s most important threats and responsibilities.

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

The focus player and fixture, team style, spatial context, key-player contributions, and the already-prepared style, shape, space, players and awareness sections.

## Output

`verdict`: one connected briefing paragraph. The report displays it at the top even though it is generated near the end.

## Run from the package root

```sh
python3 run.py demo
python3 run.py section verdict --workspace work/demo
python3 run.py section verdict --workspace work/demo --dry-run
```

The normal section command prepares inputs and extracts the approved example. Dry-run prepares a request without an external call. To request a new Haiku draft after configuring your own Bedrock access:

```sh
python3 run.py section verdict --workspace work/demo --generate
```

A new model response is a draft. Review its facts and player instructions before assembling it into a final report.

Render an approved assembled narrative with:

```sh
python3 run.py render --workspace work/demo
```

See the root README for environment setup, full-generation order and review commands.
