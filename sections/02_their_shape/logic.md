# Their shape — analysis logic

## Windows

`pipeline/build_evidence.py` creates three opponent match-ID windows after sorting completed pre-cutoff fixtures:

- `last5`: the last five opponent fixtures, or all available fixtures if fewer exist.
- `home`: all opponent home fixtures in this competition/season before the cutoff.
- `away`: all opponent away fixtures in that same scope.

A window is defined by fixtures even when some lack position data. `covered_matches` and `match_ids` preserve this difference. Counts of recorded, syntactically valid formation strings come from the corresponding fixture records; they do not fill missing formation data.

## Activity composite

`shape_window` keeps opponent starters (`substitute` is false), drops rows without average coordinates, and weights each player's coordinates by `points_count`. A player with no positive total weight is omitted.

`raw_x = sum(average_x × points_count) / sum(points_count)`

`raw_y = sum(average_y × points_count) / sum(points_count)`

The source is drawn on a nominal 105 × 68 pitch. Opponent coordinates are mirrored on both axes into the report's relative frame:

`x = 105 × (1 - raw_x / 100)`

`y = 68 × (1 - raw_y / 100)`

The focus player's own weighted coordinates are scaled without opponent mirroring:

`focus_x = 1.05 × weighted_average_x`

`focus_y = 0.68 × weighted_average_y`

Sort candidates by starts in the window, then minutes, then player ID. Keep the first goalkeeper and up to ten outfield players. This is a composite of frequently used starters; it can combine players from different actual line-ups.

## Nearby activity

Calculate Euclidean distance from each outfield composite position to the focus player's season activity position. Highlight the three nearest, and use the nearest recent player as a possible matchup candidate in key-player selection when eligible. The Menalo example identifies Geypens's nearby activity area. It does not establish that the two players have already faced each other or will man-mark each other.

## Coordinate limits

The local ingestion comment about lateral y direction conflicts with some named player-role labels. Retain the relative plotted coordinates; do not translate the y lanes into definitive left/right player roles. The heatmap section uses neutral upper-map / centre / lower-map labels. Neither average locations nor formation labels reveal off-ball positioning, pressure triggers or future personnel.

## Implementation boundary

The shared data pipeline computes the evidence once. This folder’s `pipeline.py` selects the section input, extracts the approved example output, and validates section structure/identities using `pipeline.sections`. Editing the prompt changes future draft writing; editing a formula requires a data-pipeline change and an offline rebuild. Neither action rewrites the frozen approved example automatically.
