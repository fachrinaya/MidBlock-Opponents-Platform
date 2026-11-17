# Key players

Explain what important opponents contribute, why each matters to the player, and how the player should respond.

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

`key_players` category/rate profiles, their peer pools and coverage, nearby activity context, and `scouting_supplement.players` with full-appearance goals separately scoped from detailed-stat contributions.

## Output

`key_players_summary`; one profile per supplied key-player ID with `strengths`, `weaknesses`, `how_to_play`; supplied extra threats with `what_he_does` and `your_response`; one chart note per key-player radar.

## Run from the package root

```sh
python3 run.py demo
python3 run.py section players --workspace work/demo
python3 run.py section players --workspace work/demo --dry-run
```

The normal section command prepares inputs and extracts the approved example. Dry-run prepares a request without an external call. To request a new Haiku draft after configuring your own Bedrock access:

```sh
python3 run.py section players --workspace work/demo --generate
```

A new model response is a draft. Review its facts and player instructions before assembling it into a final report.

Render an approved assembled narrative with:

```sh
python3 run.py render --workspace work/demo
```

See the root README for environment setup, full-generation order and review commands.
