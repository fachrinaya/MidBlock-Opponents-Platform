"""Aggregate observed opponent contributions without filling unknowns with zero."""
import argparse
import json
import os
from pathlib import Path

import pandas as pd

METRICS = [
    "goals", "assists", "shots_total", "shots_on_target", "expected_goals",
    "expected_assists", "key_passes", "crosses_total", "crosses_accurate",
    "long_balls_total", "long_balls_accurate", "passes_total", "passes_accurate",
    "touches", "duels_won", "duels_lost", "aerial_duels_won", "aerial_duels_lost",
    "contests_total", "contests_won", "ball_recoveries", "fouls_committed",
    "possession_lost_control",
]


def build_dossier(snapshot, evidence):
    """Return totals, metric coverage and rates for the actual opponent players.

    A partial covered_total is the sum of known values, not a complete season
    total. Its per90 remains null unless every detailed-stat appearance has a
    recorded value. Known goals across all appearances retain their own scope.
    """
    if snapshot["meta"]["opponent_id"] != evidence["meta"]["opponent_id"]:
        raise ValueError("Snapshot and evidence identify different opponents")
    for key in ("as_of", "tournament_id", "season_id", "player_id"):
        if snapshot["meta"][key] != evidence["meta"][key]:
            raise ValueError("Snapshot and evidence have different analysis scopes")
    players = pd.DataFrame(snapshot["player_rows"])
    opponent = evidence["meta"]["opponent_id"]
    excluded = {(r["match_id"], r["team_id"]) for r in
                evidence["data_quality"]["excluded_detailed_stat_team_rows"]}
    rows = players[players.team_id.eq(opponent)].copy()
    details = {r["player_id"]: r for r in snapshot["details"]}
    result = []
    for player_id, group in rows.groupby("player_id"):
        group = group.sort_values("start_timestamp")
        latest = group.iloc[-1]
        observed = group.loc[[((r.match_id, r.team_id) not in excluded)
                              for r in group.itertuples()]].copy()
        minutes = float(observed.minutes_played.sum())
        item = {
            "player_id": int(player_id), "name": latest.player_name,
            "number": str(latest.jersey_number),
            "roles": details.get(int(player_id), {}).get("positions_detailed", []),
            "total_appearances": len(group),
            "total_minutes": float(group.minutes_played.sum()),
            "covered_appearances": len(observed), "covered_minutes": minutes,
            "metrics": {},
        }
        for metric in METRICS:
            values = pd.to_numeric(observed.get(metric, pd.Series(index=observed.index, dtype=float)), errors="coerce")
            known = values.notna()
            total = float(values.sum()) if known.any() else None
            item["metrics"][metric] = {
                "covered_total": total, "known_matches": int(known.sum()),
                "per90": total / minutes * 90
                if total is not None and known.all() and minutes >= 45 else None,
            }
        goals = pd.to_numeric(group.goals, errors="coerce")
        item["goals_in_all_appearance_records"] = float(goals.sum()) if goals.notna().all() else None
        result.append(item)
    return {
        "source_snapshot": evidence.get("source_snapshot_run", "snapshot"),
        "source_evidence": "evidence.json", "players": result,
        "team": evidence["style"],
        "spatial": {k: {field: value for field, value in panel.items() if field != "cells"}
                    for k, panel in evidence["space"].items()},
        "focus": evidence["focus"], "selected_keys": evidence["key_players"],
        "measurement_note": (
            "Only complete metric values in detailed-stat fixtures receive a per90 rate; "
            "unknown values remain unknown. Partial covered totals retain known_matches. "
            "Goals are shown separately across known appearance records. Tactical responses "
            "are recommendations, not confirmed opponent instructions."
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot")
    parser.add_argument("evidence")
    parser.add_argument("--output-dir", default=os.environ.get("NUTMEG_OUTPUT_DIR", "."))
    args = parser.parse_args()
    result = build_dossier(json.loads(Path(args.snapshot).read_text()),
                           json.loads(Path(args.evidence).read_text()))
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "threat-dossier.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
