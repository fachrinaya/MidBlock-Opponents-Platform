# Key players — analysis logic

## Main profile selection

The evidence builder preserves the stored MidBlock `overall_score` and category scores. The upstream rating model already blends within-position percentiles by played-position minutes. It must not be re-ranked, replaced with a canonical-position percentile, or interpreted as an action success percentage.

For each canonical line G/D/M/F, select opponent candidates from the supplied score rows. Prefer candidates with at least 180 recorded minutes when any exist in that line. If the nearest recent average-activity candidate is in that candidate set, feature that player; otherwise use highest stored Overall, then minutes. If rating timestamps fail the cutoff audit, scores are unavailable and minutes drive the fallback. Featured-player stored minutes must agree with pre-cutoff appearance totals.

The 180-minute feature preference is distinct from the upstream model's 45-minute eligibility floor and the raw-metric floor. Count appearances from positive-minute match records, not unused bench listings. The original example's four selected profiles are Hauptmeijer, Geypens, Receveur and van der Sande.

## Stored scores and pools

- Preserve supplied categories and Overall exactly.
- Compute displayed played-position shares from recorded minutes in each position divided by all player minutes.
- Players with upstream rating data but no matching detailed export retain the canonical-position fallback disclosed by the builder; do not manufacture missing match rows.
- Category cohort counts are specific to category and position involvement. A player can belong to more than one position cohort.
- Raw-metric peer groups are separate from these stored-score cohorts.

## Raw metric rates and percentiles

Exclude team-match pairs with missing pass totals and average rating. For each player, sum minutes in the remaining detailed-stat matches. Require at least 45 minutes. A metric receives a per90 value only if every retained player row contains that metric:

`per90 = 90 × sum(metric in covered rows) / sum(minutes in covered rows)`

Never divide an eight-match detailed total by nine-match full appearance minutes. Missing component values make that rate unavailable. The raw-metric peer position comes from the supplied canonical player detail (falling back to a recorded position), not a re-ranking of stored blended categories.

For each raw metric and canonical position, use average-tie percentile rank × 100. Higher is treated as more activity for most metrics; fouls and possession losses reverse direction before ranking. This direction is a display convention, not a validated skill judgement. Select up to two metrics at/above the 50th percentile and up to two below it for the bars.

For goalkeepers, goals prevented per90 uses only goalkeeper rows with `has_xgot` true, known goals prevented and at least 45 covered minutes. Keep the xGOT-covered sample visible. This does not identify reaction, positioning or handling mechanisms.

## Additional attacking contributions

`build_threat_dossier.py` groups the opponent's player-match rows. For each metric it writes `covered_total`, `known_matches`, and complete-data `per90`. It also retains `total_appearances`, `total_minutes`, `covered_appearances`, and `covered_minutes`.

`goals_in_all_appearance_records` is only available when goals are known in every positive-minute appearance. It keeps the full appearance scope rather than discarding a recorded goal merely because detailed passing data was missing in that match.

A partial metric total must not be described as a complete covered-sample total when `known_matches < covered_appearances`. The package's selection/configuration supplies the additional threats; the narrator must cover those exact IDs rather than inventing names. Goppel, Yachida and Irfan Jaya are the explicit additional threats in the accepted example. This list supplements the positional ratings; it is not an automated claim that they are the only threats.

## Coaching interpretation

The evidence supplies contribution and involvement, not fixed habits or physical mechanisms. Give conditional advice: close a cross with cover when the ball travels wide; scan a scorer when shifting; offer a bounce pass if marked tightly; prepare second balls when distribution goes long. These instructions can be useful without asserting an observed tactical weakness.

## Implementation boundary

The shared data pipeline computes the evidence once. This folder’s `pipeline.py` selects the section input, extracts the approved example output, and validates section structure/identities using `pipeline.sections`. Editing the prompt changes future draft writing; editing a formula requires a data-pipeline change and an offline rebuild. Neither action rewrites the frozen approved example automatically.
