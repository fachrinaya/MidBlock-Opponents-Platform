# Start here

This is the accepted **English Luka Menalo vs Bali United opponent prototype**,
plus its source data, section prompts, calculation logic, repeatable pipeline,
Nutmeg methodology and audit trail.

**See the result:** double-click `Open Prototype.command`. It opens the English
report at `http://127.0.0.1:4182/english.html`. Keep the terminal window open.
The included PDF is `prototype/luka-menalo-bali-united-english.pdf`.

**Run the pipeline:** open Terminal in this folder:

```sh
./setup.sh
.venv/bin/python run.py demo
.venv/bin/python run.py serve --workspace work/demo --open
```

The demo rebuilds the evidence from the frozen snapshot, checks it against the
reviewed example, and renders the approved English narrative and a fresh PDF.
It uses no database connection or AI credits. It is an offline replay of the
accepted report, not a claim that an AI will independently reproduce the same prose.

**Read the logic:** start with [README.md](README.md), then
[analysis logic](docs/ANALYSIS_LOGIC.md), [pipeline flow](docs/FLOW.md), and
[the section map](docs/SECTION_MAP.md). Each folder under `sections/` contains
its own prompt, logic, pipeline wrapper, output schema and real input/output example.

The included snapshot has a fixed November 2026 cutoff. New matches need fresh
data. Database and Bedrock access use your own configuration; passwords and
private keys are not included.
