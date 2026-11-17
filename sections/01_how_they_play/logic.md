# How they play — analysis logic

## Source and grain

`pipeline/build_evidence.py` implements `style_row` and the aggregation in `build`. Each source row is one team in one completed match. An opponent's result history retains all valid completed fixtures; detailed-stat averages use their own covered rows.

A team-match row is excluded from detailed calculations when **both** `passes_total` and `avg_rating` are missing. Its default shot zeros are treated as unknown. The matching player rows are excluded from detailed per-90 calculations. Match results, appearance minutes, spatial points and stored scores keep their own scopes.

## Per-match formulas

For each covered team-match row, compute the following. A ratio is missing when its denominator is missing or non-positive, or a required numerator is missing. Required sums are missing if any component is unknown.

| Displayed metric | Per-match calculation |
| --- | --- |
| Pass share | `passes_total / (passes_total + opp_passes_total)` |
| Pass accuracy | `passes_accurate / passes_total` |
| Long-ball share | `long_balls_total / passes_total` |
| Opposition-half pass share | `opposition_half_passes_total / passes_total` |
| Shots per match | `shots_total` |
| Expected goals per match | `expected_goals` |
| Expected goals per shot | `expected_goals / shots_total` |
| Crosses per shot | `crosses_total / shots_total` |
| Defensive actions per opposition shot | `(interceptions + tackles + clearances) / opp_shots_total` |
| Tackles / (tackles + clearances) | `tackles / (tackles + clearances)` |
| Aerial-duel ratio · MidBlock formula | `(aerial_duels_won + aerial_duels_lost) / (duels_won + duels_lost + aerial_duels_won + aerial_duels_lost)` |
| Aerial duels won | `aerial_duels_won / (aerial_duels_won + aerial_duels_lost)` |

Percentage rows are multiplied by 100 for display. The aerial-duel ratio preserves this application's formula; do not substitute an assumed provider definition.

## Aggregation and comparisons

- Opponent value: arithmetic mean of its available per-match values for that metric.
- League baseline: first compute each team's mean, then average those team means. Every team with that metric receives equal weight; it is not a pooled-total ratio or a match-count-weighted league mean.
- `matches` reports the actual number of nonmissing opponent observations for each row.
- Home and away pass-share values use covered detailed-stat rows within each venue window; the denominator counts for all fixtures and covered fixtures remain separate.
- The losing-result split uses full matches the opponent **ultimately lost**. It does not measure minutes spent trailing. Missing minute-level score-state data is disclosed.

## Interpretation

The code calculates descriptive comparisons. It does not infer a pressing system, high defensive line, off-ball block, tempo, passing network or counterattack route. The narrative can propose a coordinated response to the measured profile, conditional on the cue occurring.

## Implementation boundary

The shared data pipeline computes the evidence once. This folder’s `pipeline.py` selects the section input, extracts the approved example output, and validates section structure/identities using `pipeline.sections`. Editing the prompt changes future draft writing; editing a formula requires a data-pipeline change and an offline rebuild. Neither action rewrites the frozen approved example automatically.
