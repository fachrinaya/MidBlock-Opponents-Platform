"""Portable snapshot-to-evidence adapter; no database or model calls."""
import json
from pathlib import Path

from .build_evidence import build
from .build_threat_dossier import build_dossier

ROOT = Path(__file__).resolve().parents[1]
COACHING_REFERENCES = [
    "https://www.fifatrainingcentre.com/en/practice/talent-coach-programme/sessions/preventing-progression-through-central-areas.php",
    "https://www.fifatrainingcentre.com/en/practice/elite-sessions/out-of-possession/defending-as-a-unit.php",
]


def _additional_players(players, main_ids, config):
    by_id = {player["player_id"]: player for player in players}
    configured = config.get("additional_threat_ids")
    if configured is not None:
        result = []
        seen = set(main_ids)
        for player_id in configured:
            if isinstance(player_id, bool) or not isinstance(player_id, int):
                raise ValueError("additional_threat_ids must contain integer player IDs")
            if player_id not in by_id:
                raise ValueError("A configured additional threat is absent from this opponent snapshot")
            if player_id not in seen:
                result.append(by_id[player_id])
                seen.add(player_id)
        return result[:3]
    # Alternate the strongest recorded crossing source and scoring sources,
    # excluding the main cards. Ties use player ID for reproducibility.
    eligible = [p for p in players if p["player_id"] not in main_ids]
    crosses = sorted(
        [p for p in eligible if p["metrics"]["crosses_total"]["covered_total"] is not None
         and p["metrics"]["crosses_total"]["known_matches"] == p["covered_appearances"]
         and p["metrics"]["crosses_total"]["covered_total"] > 0],
        key=lambda p: (-p["metrics"]["crosses_total"]["covered_total"], p["player_id"]),
    )
    scorers = sorted(
        [p for p in eligible if p["goals_in_all_appearance_records"] is not None
         and p["goals_in_all_appearance_records"] > 0],
        key=lambda p: (-p["goals_in_all_appearance_records"], p["player_id"]),
    )
    candidates = [*crosses[:1], *scorers, *crosses[1:]]
    result, seen = [], set(main_ids)
    for player in candidates:
        if player["player_id"] not in seen:
            result.append(player)
            seen.add(player["player_id"])
        if len(result) == 3:
            break
    return result


def build_dataset(snapshot_path, output_dir, config_path=None):
    """Write evidence.json and threat-dossier.json; return English report evidence.

    config/report.json supplies optional explicit additional_threat_ids for a
    frozen example. Omit that setting to select recorded crossing/scoring
    contributors from the current opponent, without hardcoded example IDs.
    """
    snapshot_path, output_dir = Path(snapshot_path), Path(output_dir)
    config_file = Path(config_path) if config_path is not None else ROOT / "config" / "report.json"
    if config_path is not None and not config_file.is_file():
        raise ValueError("The supplied report config file does not exist")
    config = json.loads(config_file.read_text()) if config_file.is_file() else {}
    if not isinstance(config, dict):
        raise ValueError("Report config must be a JSON object")
    snapshot = json.loads(snapshot_path.read_text())
    evidence = build(snapshot, source_run=snapshot_path.name)
    evidence["meta"] = {**evidence["meta"], "report_language": "en"}
    dossier = build_dossier(snapshot, evidence)
    by_id = {p["player_id"]: p for p in dossier["players"]}
    main_ids = [p["player_id"] for p in evidence["key_players"]]
    main = [by_id[player_id] for player_id in main_ids if player_id in by_id]
    additional = _additional_players(dossier["players"], main_ids, config)
    evidence["scouting_supplement"] = {
        "source_run": "threat-dossier.json", "players": [*main, *additional],
        "coaching_references": COACHING_REFERENCES,
        "scope": (
            "Player contributions are observed. Match responses are proposed coaching actions, "
            "not claims of a confirmed tactical scheme. Full-appearance goals and detailed-stat "
            "contributions retain different samples; per90 means per 90 minutes, never per appearance."
        ),
        "lateral_caution": "Do not assign named football flanks from the aggregate heatmap; the lateral source convention needs reconciliation.",
    }
    evidence["orientation_labels"] = {
        "fixture": "Focus team HOME; opponent AWAY" if evidence["fixture"]["home_team_id"] == evidence["meta"]["team_id"] else "Focus team AWAY; opponent HOME",
        "sides": ["Upper-map band", "Centre band", "Lower-map band"],
        "thirds": ["Opponent own third", "Middle third", "Opponent attacking third"],
    }
    evidence["valid_references"] = [
        "style", "scouting", "shape.last5", "shape.home", "shape.away",
        "space.season", "space.last5",
        *[f"key.{player_id}" for player_id in main_ids],
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in (("evidence.json", evidence), ("threat-dossier.json", dossier)):
        (output_dir / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
    return evidence
