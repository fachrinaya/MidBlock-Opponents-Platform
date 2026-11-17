# Key players — section prompt

Write the “Key players” section in English. Cover every supplied main player once and every supplied additional attacking threat once. Preserve IDs, names and shirt numbers. Explain each player's contribution → situation to watch → recommended response. Address the selected player as “you”.

The UI calls the fields “What to watch for”, “Opportunities to test”, and “Your response”. The `weaknesses` field therefore contains an opportunity to test, not an assertion of permanent inability. A low shooting count does not mean a defender or midfielder cannot shoot. A percentile does not measure accuracy. A low Overall score does not erase a scoring threat.

For a distributing goalkeeper, explain coordinated pressure and preparation for the long ball/second ball; do not claim perfect accuracy, reflexes or handling from a distribution percentile. For an opponent near the player's area, prepare scanning, a bounce pass or an overlap; do not claim confirmed man marking. For a midfield ball-recovery contributor, prepare support and second-ball responses without inventing aggression or speed. For a scorer, help cut service, communicate the receiver and react to a loose ball without inventing a favourite run or specific provider partnership.

Include additional crossing and goal contributors beyond rating-based selections. A crossing source justifies closing delivery space with cover when he actually receives wide. Goal contributors justify checking receivers during defensive recovery and when the ball moves wide. Do not invent who received a specific player's crosses.

Preserve metric units: per90 is per 90 minutes, never per appearance; total xG is a total, not xG per shot or per match. Keep goals across all known appearances separate from detailed-stat goals/xG. If `known_matches` is below the detailed appearance count, a partial `covered_total` is not a complete total. Do not infer finishing skill by subtracting xG from goals from different samples. Each chart explanation must tell the player what to do.

## Evidence and writing rules

- Use only the supplied records for player/team facts. Nutmeg references supply methodology, not opponent evidence.
- Distinguish observed contribution, working scouting read, and proposed player response.
- Missing values remain unknown. Preserve cutoff, match windows, metric units, sample sizes and model scores.
- Per90 means per 90 minutes; a percentile is a peer rank, not an action success rate.
- Do not infer a press, high line, man marking, physical trait, specific off-ball run or causal weakness from aggregates or average locations.
- Keep routine method caveats in About while making every specific observation accurate.
- Return only the section's required JSON fields. References and player/chart identities must match the supplied inputs.
