# AI generation, analysis logic and acceptance

The accepted report is a substantially edited Haiku draft. It is not an example
of unedited model output. Its first drafts mixed per-match and per90 values,
confused total xG with rates, and asserted tactical movement that aggregate data
did not establish. The English example preserves the corrected facts and the
player preparation approach accepted by the user.

## Writing contract

Every section should answer: what does the opponent do, why does it matter to
you, what cue should you recognise, and what should you do? A practical plan can
be conditional without pretending the data proves an opponent weakness.

Examples from the accepted approach:

- Goppel's recorded crossing volume justifies preparing to close the delivery
  space with a covering teammate. It does not prove a specific crossing partner.
- Yachida and Irfan's scoring contributions justify checking their positions
  when the ball moves wide. They do not establish exact off-ball running routes.
- Geypens's nearby activity area suggests preparing support before receiving.
  It does not establish a confirmed marking assignment.

The shared English voice is in `prompts/shared.md`; section-specific instructions
are in `sections/*/prompt.md`. Charts supplied to Haiku are screenshots of the
actual rendered evidence, not invented illustrations.

## Automatic checks

Strict schemas reject missing/extra fields and very short prose. Identity checks
require every supplied key-player ID and additional threat exactly once, preserve
names/numbers, require each actual chart explanation, and reject unavailable
awareness references. Bedrock must finish with `end_turn`. A truncated response
is rejected. Requests and raw drafts are kept separately from reviewed text.

These checks do not understand all football claims and cannot verify that every
sentence is supported. They are not a substitute for factual review.

## Human review checklist

1. Check each figure against the evidence and source sample.
2. Check units: per90, per appearance, total, per shot, percentage and percentile.
3. Keep full-appearance goals separate from detailed-stat xG/shot coverage.
4. Preserve stored MidBlock category scores; do not rerank them or call them
   action success percentages.
5. Remove unsupported claims about pressing, blocks, marking, pace, high lines,
   specific runs, pass partnerships, future starters or causal weaknesses.
6. Keep useful instructions: recognisable cue, concrete action, teammate cover.
   Do not reduce every section to a generic request to inspect video.
7. Use neutral upper-map / centre / lower-map labels while the lateral source
   convention remains unresolved. Do not attach Goppel to an inferred map flank.
8. Check English language throughout, including drills and chart notes.

After editing the complete draft, `approve` records your name and notes and
binds the exact evidence and narrative hashes. A later edit makes the review
stale and blocks rendering. The command records your attestation; it does not
claim to have independently verified the football content.

The per-section `--generate` command writes an isolated draft. For a complete
new narrative, use `generate`, or manually merge reviewed section changes into
the full draft and refresh awareness/verdict before approval. A generated draft
never silently overwrites the accepted bundled prototype.

## What was tested

The accepted generation used the original configured Bedrock pipeline. The
refactored package's offline path, request preparation, response validation and
mocked Converse transport are exercised by tests. No new paid Bedrock call and
no live database call is required or claimed during package assembly. Developer
credentials and reachable service access are needed for those live paths.
