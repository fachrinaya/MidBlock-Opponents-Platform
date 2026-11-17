# What to be aware of

Convert the preceding analysis into a small set of memorable match cues, player actions, and proposed practice exercises.

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

The reviewed or draft style, shape, space and player analyses, plus their underlying evidence and valid reference IDs.

## Output

`awareness_summary` and `awareness` items containing `title`, `analysis`, `evidence_refs`, and an optional proposed `drill` with `title` and `instructions`.

## Run from the package root

```sh
python3 run.py demo
python3 run.py section awareness --workspace work/demo
python3 run.py section awareness --workspace work/demo --dry-run
```

The normal section command prepares inputs and extracts the approved example. Dry-run prepares a request without an external call. To request a new Haiku draft after configuring your own Bedrock access:

```sh
python3 run.py section awareness --workspace work/demo --generate
```

A new model response is a draft. Review its facts and player instructions before assembling it into a final report.

Render an approved assembled narrative with:

```sh
python3 run.py render --workspace work/demo
```

See the root README for environment setup, full-generation order and review commands.
