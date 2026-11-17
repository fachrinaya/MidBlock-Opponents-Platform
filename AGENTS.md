# Working in this handoff

The accepted player report and all new player-facing drafts are English.
Read START_HERE.md and docs/SECTION_MAP.md before changing the workflow.

Use the portable code in pipeline/ and the section wrappers in sections/.
Nutmeg references are pinned upstream methodology, not evidence or live tools.
Their historical installation paths are preserved for source integrity; run the
included CLI with `python3 tools/nutmeg.py`, not a path outside this folder.

Preserve explicit cutoffs, detailed-stat exclusions, separate sample denominators
and stored category scores. Do not fabricate tactical behaviour from aggregates.
Keep practical, conditional player instructions. Every generated report needs
factual/editorial review before rendering; schema validation alone is insufficient.

Do not copy credentials or private keys into the project. Keep raw data and
generated outputs excluded from git. Use new workspaces for new evidence.
