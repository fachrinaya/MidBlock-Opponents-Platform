# What to expect — analysis logic

## Selection logic

There is no extra prediction model or match-outcome probability. The verdict is a synthesis of evidence already calculated for the other sections. It adds no numeric aggregation.

1. Confirm the selected player, upcoming opponent and venue from the snapshot.
2. Read the style, shape, space, players and awareness outputs.
3. Choose the threats that matter most to the player's role, including delivery sources and goal contributors.
4. Connect them to a small number of observable cues and coordinated responses.
5. Check that every numeric statement is already present in the evidence and that a recommendation has not become a claim about an observed opponent tactic.

## Dependencies

Generate this after the substantive analysis and awareness sections. Display order is independent from generation order: the final report puts the verdict first.

## Boundaries

“Passing-oriented working read” can be supported by supplied pass and chance patterns. “They will use this exact press”, “their full-back always leaves space”, and a predicted score cannot be derived from these aggregates. The verdict must not present those as facts.

## Implementation boundary

The shared data pipeline computes the evidence once. This folder’s `pipeline.py` selects the section input, extracts the approved example output, and validates section structure/identities using `pipeline.sections`. Editing the prompt changes future draft writing; editing a formula requires a data-pipeline change and an offline rebuild. Neither action rewrites the frozen approved example automatically.
