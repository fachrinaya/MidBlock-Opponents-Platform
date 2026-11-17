# Where they play — analysis logic

## Source and windows

Use actual exported opponent `heatmaps` points, after checking x and y are within the source range of 0 to 100. Drop points with missing coordinates. Do not create synthetic heat blobs.

- `season`: all available opponent league-fixture IDs before the cutoff.
- `last5`: the opponent's last five fixture IDs before the cutoff.

`points` counts exported records. `covered_matches` counts fixtures represented by points; `match_ids` retains the full window. Neither equals tracking coverage or minutes of possession.

## Binning

Mirror the opponent into the same relative report frame as the shape plot:

`display_x = 105 × (1 - source_x / 100)`

`display_y = 68 × (1 - source_y / 100)`

Use `numpy.histogram2d(display_y, display_x, bins=[28, 42], range=[[0,68],[0,105]])`. Flatten the resulting 28-row × 42-column matrix for the chart helper. The renderer scales each period's colours to that panel's own maximum.

## Shares

Shares are percentages of retained recorded points, not time:

| Display label | Source-coordinate condition |
| --- | --- |
| Upper map lane | `source_y >= 200/3` |
| Centre | `100/3 <= source_y < 200/3` |
| Lower map lane | `source_y < 100/3` |
| Opponent's own third | `source_x < 100/3` |
| Middle third | `100/3 <= source_x < 200/3` |
| Attacking third | `source_x >= 200/3` |

For each condition, `share = 100 × matching_points / retained_points`. Empty windows return no shares rather than zeros.

## Limits and decisions

Source lateral comments conflict with some player-role labels, so the upper/lower labels are deliberately neutral. Do not tie Goppel's football flank to one heatmap lane. A dense zone can motivate preparation for support and scanning, but it does not prove pressure, trapping, a passing route or defensive weakness. Do not compare absolute panel brightness or treat overlapping windows as independent validation.

## Implementation boundary

The shared data pipeline computes the evidence once. This folder’s `pipeline.py` selects the section input, extracts the approved example output, and validates section structure/identities using `pipeline.sections`. Editing the prompt changes future draft writing; editing a formula requires a data-pipeline change and an offline rebuild. Neither action rewrites the frozen approved example automatically.
