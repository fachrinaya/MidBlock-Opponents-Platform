# How the opponent analysis is produced

The report helps a player prepare for the next league opponent. It answers four connected questions: what does this team tend to produce, which players contribute to the danger, what cue should the player notice, and what should the player do?

## The three layers

| Layer | What it contains | Example of an allowed statement |
| --- | --- | --- |
| Observed contribution | Counts, rates, categories, sample coverage and recorded activity locations | A named player attempted crosses in the covered sample. |
| Working scouting read | A cautious synthesis of compatible observations | The available passing profile suggests preparing for repeated circulation. |
| Proposed response | A conditional, coordinated football action | When that player receives wide, close the delivery space with teammate cover. |

A useful recommendation does not require proof of a permanent opponent weakness. It does require an observable cue, a relevant threat, and a responsibility compatible with teammate cover. Conversely, aggregate data does not establish a high press, a high line, a marking assignment, a specific run or a passing partnership.

## Data contract and filtering

1. Resolve the focus player's latest completed league appearance before an explicit timezone-aware cutoff.
2. Resolve the next scheduled fixture in that competition and season, preserving home/away identity and fixture attribution.
3. Export completed matches strictly before the cutoff. Duplicate source grains and mixed competition/season IDs are rejected.
4. Keep distinct evidence scopes: results and appearances; detailed team/player statistics; positions and heatmaps; stored rating rows; and derived goalkeeper coverage.
5. Exclude detailed-stat team-match pairs when both passing totals and average rating are missing. Remove their matching player rows from detailed per90 calculations. Do not convert default zeros in a results-only scrape into observations.
6. Audit source timestamps and featured-player minutes. Missing or inconsistent inputs remain visible; no synthetic football data replaces them.

## Team profile

The style section uses the existing MidBlock per-match formulas. Opponent values average available per-match observations. League comparisons average team means, giving equal weight to teams. This is not a pooled-total ratio. See `sections/01_how_they_play/logic.md` for every formula.

Pass share is a possession proxy, not clock time. Opposition-half pass share is not territorial time. Defensive actions per opposition shot and the tackle/clearance ratio are descriptive activity ratios, not pressure-location or defensive-quality measures. Full matches lost do not reveal behaviour during minutes spent trailing.

## Spatial preparation

Starter activity composites are points-count-weighted positions across defined recent and venue windows. Opponent coordinates are mirrored on both axes before drawing and proximity. The highlighted nearest areas suggest whom the player may encounter; they do not prove man marking or a prior head-to-head.

Heatmaps bin actual exported activity points into a 42 × 28 grid. Each panel rescales its own colour maximum. Counts and lane/third percentages describe records, not every touch or minutes of possession. Use neutral upper-map / centre / lower-map labels while the lateral source convention remains inconsistent. Do not attach Goppel's named flank to a heatmap bin.

## Player roles and threats

Preserve stored position/minutes-blended category scores and Overall. They are not newly recomputed ranks or action success percentages. Main profile selection prefers regular exposure and can include the nearest eligible activity candidate; raw per90 bars use separately disclosed complete-metric samples and peer pools.

Add meaningful delivery and scoring contributors beyond rating-based positional selections. The accepted example includes Goppel's crossing contribution and Yachida/Irfan's goal contribution. This supplements the four radar profiles rather than claiming the rating winners are the only dangerous players.

For detailed rates, divide complete metric totals by the minutes in those same covered rows and multiply by 90. Preserve full-appearance goals separately. A total xG is not xG per match, per90 or per shot. A partial total with missing metric rows cannot be called a complete total.

## Narrative and section dependencies

All writing is English and addresses the selected player as “you”. Lead with danger or responsibility, use only the most useful supporting observations, then give a practical response. Ordinary method explanations live primarily in About. Evidence limits still govern every sentence.

Style, shape, space and players can be prepared from the shared evidence. Awareness then selects a small set of cues/actions; verdict synthesises the match plan last while displaying first. About is deterministic metadata and needs no model request. See `SECTION_MAP.md` and each section's `prompt.md`, `logic.md`, and `pipeline.py`.

## Validation versus approval

Structural validation checks fields, IDs, references and chart coverage. It cannot prove that a tactical sentence is true. A factual/editorial reviewer must check units, denominators, unsupported causation, named roles and the usefulness of player instructions. New Haiku outputs remain drafts until that review is explicitly recorded. The accepted English example includes substantial editorial correction and preserves that authorship in its provenance.

## Reproducibility and changes

The frozen snapshot reproduces the measured evidence offline; the reviewed narrative reproduces the accepted report without another AI call. A new generation can legitimately phrase the plan differently and must not overwrite the approved example silently. A new cutoff, player, match, metric or source requires recomputation and review; changing names in the example is not a valid analysis pipeline.
