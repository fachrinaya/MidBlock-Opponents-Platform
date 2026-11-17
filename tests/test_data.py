"""Offline data-contract checks, including incomplete fixtures and cutoff leaks."""
import copy
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.build_evidence import build
from pipeline.build_threat_dossier import METRICS, build_dossier
from pipeline.data import _additional_players, build_dataset
from pipeline.export_snapshot import DataAcquisitionError, database_url, main


class FrozenDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot_path = ROOT / "data" / "raw" / "snapshot.json"
        cls.expected_path = ROOT / "examples" / "luka-menalo" / "evidence.json"
        if not cls.snapshot_path.is_file() or not cls.expected_path.is_file():
            raise unittest.SkipTest("Frozen raw snapshot and approved evidence have not been staged")
        cls.snapshot = json.loads(cls.snapshot_path.read_text())
        cls.expected = json.loads(cls.expected_path.read_text())
        with tempfile.TemporaryDirectory() as folder:
            cls.evidence = build_dataset(cls.snapshot_path, folder)
            cls.dossier = json.loads((Path(folder) / "threat-dossier.json").read_text())
            cls.saved = json.loads((Path(folder) / "evidence.json").read_text())

    def test_frozen_calculations_match_the_reviewed_example(self):
        # These are the approved report's actual numeric panels, not copies of
        # implementation formulas. Any coverage/denominator/ranking drift fails.
        for key in ("fixture", "focus", "opponent", "style", "shape", "space", "key_players", "data_quality"):
            with self.subTest(panel=key):
                self.assertEqual(self.evidence[key], self.expected[key])
        self.assertEqual(self.evidence, self.saved)
        self.assertEqual(self.evidence["meta"]["report_language"], "en")

    def test_frozen_additional_threats_come_from_config(self):
        config = json.loads((ROOT / "config" / "report.json").read_text())
        main_ids = [p["player_id"] for p in self.evidence["key_players"]]
        actual = [p["player_id"] for p in self.evidence["scouting_supplement"]["players"]]
        self.assertEqual(actual, main_ids + config["additional_threat_ids"])
        self.assertEqual(len(actual), len(set(actual)))
        self.assertEqual(self.evidence["orientation_labels"]["sides"],
                         ["Upper-map band", "Centre band", "Lower-map band"])

    def test_saved_ratings_are_preserved_and_pre_cutoff(self):
        self.assertTrue(self.evidence["ratings_audit"]["passed"])
        ratings = {p["player_id"]: p for p in self.snapshot["ratings"]}
        for player in self.evidence["key_players"]:
            self.assertEqual(player["overall"], ratings[player["player_id"]]["overall_score"])
        changed = copy.deepcopy(self.snapshot)
        changed["ratings"][0]["ingested_at"] = "2099-01-01T00:00:00Z"
        with self.assertRaisesRegex(ValueError, "pre-cutoff rating snapshot"):
            build(changed)
        changed["ratings"][0]["ingested_at"] = None
        with self.assertRaisesRegex(ValueError, "pre-cutoff rating snapshot"):
            build(changed)

    def test_cutoff_leak_and_duplicate_grain_are_rejected(self):
        changed = copy.deepcopy(self.snapshot)
        changed["heatmaps"][0]["start_timestamp"] = changed["meta"]["as_of"]
        with self.assertRaisesRegex(ValueError, "Future data leaked"):
            build(changed)
        changed = copy.deepcopy(self.snapshot)
        changed["player_rows"].append(copy.deepcopy(changed["player_rows"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate source grain"):
            build(changed)

    def test_lineup_only_fixture_does_not_become_observed_zero_shots(self):
        excluded = self.evidence["data_quality"]["excluded_detailed_stat_team_rows"]
        self.assertTrue(any(row["goals"] > 0 and row["shots_total"] == 0 for row in excluded))
        self.assertLess(self.evidence["data_quality"]["available_opponent_stat_matches"],
                        self.evidence["data_quality"]["opponent_fixtures"])
        self.assertTrue(any(p["covered_minutes"] < p["total_minutes"] for p in self.dossier["players"]))


class PartialCoverageTests(unittest.TestCase):
    def fixture(self):
        # Synthetic IDs and observations exercise scope semantics; these are
        # not provider records or an alternative football report dataset.
        meta = {"opponent_id": 2, "player_id": 1, "tournament_id": 3,
                "season_id": 4, "as_of": "2026-11-17T00:00:00+07:00"}
        rows = []
        for match_id, minutes, passes, goals, crosses in (
                (101, 90, 40, 1, 2), (102, 45, 0, 2, 0), (103, 90, None, 0, 4)):
            rows.append({**{metric: 0 for metric in METRICS},
                "player_id": 5, "team_id": 2, "player_name": "Synthetic player",
                "jersey_number": "7", "match_id": match_id,
                "start_timestamp": f"2026-11-{match_id-100:02d}T00:00:00Z",
                "minutes_played": minutes, "passes_total": passes,
                "goals": goals, "crosses_total": crosses})
        snapshot = {"meta": meta, "player_rows": rows, "details": []}
        evidence = {"meta": dict(meta), "style": {}, "space": {}, "focus": {},
                    "key_players": [], "source_snapshot_run": "synthetic-test",
                    "data_quality": {"excluded_detailed_stat_team_rows": [{"match_id": 102, "team_id": 2}]}}
        return snapshot, evidence

    def test_unknown_metric_is_not_zero_and_uses_its_known_match_count(self):
        snapshot, evidence = self.fixture()
        player = build_dossier(snapshot, evidence)["players"][0]
        self.assertEqual(player["total_minutes"], 225)
        self.assertEqual(player["covered_minutes"], 180)
        self.assertEqual(player["total_appearances"], 3)
        self.assertEqual(player["covered_appearances"], 2)
        self.assertEqual(player["metrics"]["passes_total"],
                         {"covered_total": 40.0, "known_matches": 1, "per90": None})
        self.assertEqual(player["metrics"]["crosses_total"],
                         {"covered_total": 6.0, "known_matches": 2, "per90": 3.0})
        self.assertEqual(player["metrics"]["goals"]["covered_total"], 1.0)
        self.assertEqual(player["goals_in_all_appearance_records"], 3.0)

    def test_scope_mismatch_is_rejected(self):
        snapshot, evidence = self.fixture()
        evidence["meta"]["season_id"] = 99
        with self.assertRaisesRegex(ValueError, "different analysis scopes"):
            build_dossier(snapshot, evidence)

    def test_generic_selection_deduplicates_and_avoids_partial_cross_totals(self):
        def player(pid, crosses, goals, known=2):
            return {"player_id": pid, "covered_appearances": 2,
                    "goals_in_all_appearance_records": goals,
                    "metrics": {"crosses_total": {"covered_total": crosses, "known_matches": known}}}
        players = [player(11, 100, 10), player(12, 20, 4),
                   player(13, 2, 6), player(14, 3, 5), player(15, 999, 0, known=1)]
        self.assertEqual([p["player_id"] for p in _additional_players(players, [11], {})],
                         [12, 13, 14])
        self.assertEqual([p["player_id"] for p in _additional_players(players, [11],
                         {"additional_threat_ids": [13, 13, 12, 11]})], [13, 12])


class AcquisitionConfigurationTests(unittest.TestCase):
    def test_environment_password_characters_are_not_url_interpolation(self):
        environment = {"DB_USER": "read_only_test", "DB_PASSWORD": "a@b:c/$d", "DB_PORT": "5432"}
        with patch.dict(os.environ, environment, clear=True), patch("pipeline.export_snapshot.load_dotenv"):
            url = database_url()
        self.assertEqual(url.password, environment["DB_PASSWORD"])
        self.assertNotIn(environment["DB_PASSWORD"], str(url))

    def test_connection_failure_is_sanitized_and_read_only(self):
        environment = {"DATABASE_URL": "postgresql://test:synthetic-secret@localhost/football"}
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, environment, clear=True), \
             patch("pipeline.export_snapshot.load_dotenv"), \
             patch("pipeline.export_snapshot.create_engine", side_effect=RuntimeError("synthetic-secret")) as factory:
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                status = main(["--player", "Synthetic player", "--as-of", "2026-11-17T00:00:00+07:00",
                               "--output-dir", folder])
            self.assertEqual(status, 1)
            self.assertNotIn("synthetic-secret", stderr.getvalue())
            self.assertFalse((Path(folder) / "snapshot.json").exists())
            self.assertEqual(factory.call_args.kwargs["isolation_level"], "REPEATABLE READ")
            self.assertIn("default_transaction_read_only=on", factory.call_args.kwargs["connect_args"]["options"])

    def test_timezone_is_required_before_any_connection(self):
        with patch("pipeline.export_snapshot.create_engine") as factory:
            from pipeline.export_snapshot import export_snapshot
            with self.assertRaisesRegex(DataAcquisitionError, "explicit timezone"):
                export_snapshot("Synthetic player", "2026-11-17", ".")
            factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
