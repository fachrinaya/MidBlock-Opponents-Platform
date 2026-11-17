# What to be aware of — analysis logic

## Dependency and synthesis

This section introduces no new statistical model. Prepare style, shape, space and player sections first, then derive awareness priorities from those outputs and their evidence. Preserve whether prior analysis is a draft or reviewed; structural validity alone is not factual approval.

Each priority should answer:

1. What can the player observe during the match?
2. What should the player do in response?
3. Which measured threat motivates that response?
4. Which teammate or handover is needed so the action does not open another route?

## Reference validation

References must be nonempty and drawn from the package's valid reference list, including `style`, `scouting`, `shape.last5/home/away`, `space.season/last5`, and `key.<supplied player_id>`. A string merely matching the list is not proof of support: the factual reviewer must check that the referenced input actually supports the observation.

## Priority selection

Keep a small set of three to five items. Prefer distinct responsibilities over repeated warnings. The accepted example covers closing Goppel's crossing space, checking Yachida and Irfan as the ball goes wide, supported pressure on Hauptmeijer, receiving near Geypens, and recovering to protect the inside route. Second-ball tasks also appear in the related goalkeeper and striker profiles; they need not become another repetitive priority.

## Drills

A drill is an optional, clearly labelled proposed exercise. It rehearses the recommended behaviour, such as coordinated wide defending, scanning and handover, or pressing then reacting to a long ball. It is not an existing club drill, a match event, a personalised workload, or confirmation of an opponent scheme. Avoid unsupported numerical dosage and invented match-location precision.

## Implementation boundary

The shared data pipeline computes the evidence once. This folder’s `pipeline.py` selects the section input, extracts the approved example output, and validates section structure/identities using `pipeline.sections`. Editing the prompt changes future draft writing; editing a formula requires a data-pipeline change and an offline rebuild. Neither action rewrites the frozen approved example automatically.
