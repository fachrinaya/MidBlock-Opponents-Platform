"""Portable read-only PostgreSQL acquisition; no application or SSH dependency."""
import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url

ROOT = Path(__file__).resolve().parents[1]


class DataAcquisitionError(ValueError):
    """A safe user-facing error that does not contain database credentials."""


def _cutoff(value):
    try:
        cutoff = pd.Timestamp(value)
    except Exception:
        raise DataAcquisitionError("The analysis cutoff is not a valid timestamp") from None
    if pd.isna(cutoff) or cutoff.tzinfo is None:
        raise DataAcquisitionError("The analysis cutoff must include an explicit timezone")
    return cutoff


def database_url(env_path=None):
    """Read DATABASE_URL or DB_*; preserve existing process environment values."""
    load_dotenv(Path(env_path) if env_path is not None else ROOT / ".env", override=False)
    configured = os.environ.get("DATABASE_URL")
    if configured:
        try:
            if configured.startswith("postgres://"):
                configured = "postgresql://" + configured[len("postgres://"):]
            url = make_url(configured)
        except Exception:
            raise DataAcquisitionError("DATABASE_URL is invalid; check the local environment configuration") from None
        if url.get_backend_name() != "postgresql":
            raise DataAcquisitionError("Acquisition requires a PostgreSQL DATABASE_URL")
        return url
    user = os.environ.get("DB_USER")
    if not user:
        raise DataAcquisitionError("Configure DATABASE_URL or DB_USER with the DB_* connection settings")
    try:
        port = int(os.environ.get("DB_PORT", "5432"))
        if not 1 <= port <= 65535:
            raise ValueError()
    except ValueError:
        raise DataAcquisitionError("DB_PORT must be a valid TCP port") from None
    return URL.create(
        "postgresql+psycopg2", username=user,
        password=os.environ.get("DB_PASSWORD", ""),
        host=os.environ.get("DB_HOST", "127.0.0.1"), port=port,
        database=os.environ.get("DB_NAME", "football_analytics"),
    )


def _external_fixture(path, focus, params, cutoff, read):
    public = json.loads(Path(path).read_text())
    if not public.get("sources") or not public.get("checked_on"):
        raise DataAcquisitionError("An external fixture needs sources and a checked_on date")
    import re
    def season_key(value):
        return [int(part) % 100 for part in re.findall(r"\d+", str(value))]
    if season_key(public["season_name"]) != season_key(focus["season_name"]):
        raise DataAcquisitionError("Stored player appearances do not cover the external fixture's season")
    if _cutoff(public["start_timestamp"]) <= cutoff:
        raise DataAcquisitionError("The external fixture must be after the analysis cutoff")
    own_name = str(focus["team_name"]).casefold()
    sides = [public["home_team_name"], public["away_team_name"]]
    own_sides = [index for index, name in enumerate(sides)
                 if name.casefold() in own_name or own_name in name.casefold()]
    if len(own_sides) != 1:
        raise DataAcquisitionError("The external fixture does not uniquely match the player's latest club")
    params["opponent_name"] = "%" + sides[1-own_sides[0]] + "%"
    opponent = read("opponent_identity")
    if opponent.team_id.nunique() != 1:
        raise DataAcquisitionError("External opponent identity is unresolved in this league and season")
    opponent_id = int(opponent.iloc[0].team_id)
    return pd.DataFrame([{
        **public, "match_id": None,
        "home_team_id": params["team_id"] if own_sides[0] == 0 else opponent_id,
        "away_team_id": opponent_id if own_sides[0] == 0 else params["team_id"],
        "tournament_id": params["tournament_id"], "season_id": params["season_id"],
        "match_status": "Scheduled (external fixture source)",
    }])


def export_snapshot(player, as_of, output_dir, fixture_path=None, env_path=None):
    """Return a snapshot and save snapshot.json/coverage.json after all reads succeed.

    The bundled query adapter resolves the next Indonesia Super League fixture.
    No ingestion functions, database writes, SSH commands or model calls occur.
    """
    cutoff = _cutoff(as_of)
    if not isinstance(player, str) or not player.strip():
        raise DataAcquisitionError("A player name is required")
    queries = json.loads(Path(__file__).with_name("snapshot_queries.json").read_text())
    params = {"player_name": player.strip(), "cutoff": cutoff.to_pydatetime()}
    url = database_url(env_path)
    engine = None
    try:
        engine = create_engine(url, isolation_level="REPEATABLE READ", connect_args={
            "connect_timeout": 8,
            "options": "-c default_transaction_read_only=on -c statement_timeout=60000",
        })
        with engine.connect() as conn:
            def read(name):
                statement = queries[name]
                if not statement.lstrip().upper().startswith("SELECT"):
                    raise DataAcquisitionError("The bundled acquisition adapter permits SELECT queries only")
                return pd.read_sql(text(statement), conn, params=params)
            identity = read("identity")
            if identity.empty:
                raise DataAcquisitionError("No completed league appearance resolves the player before the cutoff")
            if identity.player_id.nunique() != 1:
                raise DataAcquisitionError("Player name is ambiguous; resolve the identity before exporting")
            focus = identity.iloc[0].to_dict()
            params.update({key: int(focus[key]) for key in
                           ("player_id", "team_id", "tournament_id", "season_id")})
            fixtures = read("next_fixtures")
            if fixtures.empty:
                if fixture_path is None:
                    raise DataAcquisitionError("No upcoming league fixture is stored; provide an attributed external fixture or update schedule coverage")
                fixtures = _external_fixture(fixture_path, focus, params, cutoff, read)
            fixture = fixtures.iloc[0].to_dict()
            params.update({key: int(fixture[key]) for key in ("tournament_id", "season_id")})
            params["opponent_id"] = int(fixture["away_team_id"]
                if int(fixture["home_team_id"]) == params["team_id"] else fixture["home_team_id"])
            tables = {"identity": identity, "fixtures": fixtures.head(1)}
            for name in ("matches", "team_rows", "player_rows", "positions", "heatmaps",
                         "ratings", "details", "style_profiles", "schema", "derived"):
                tables[name] = read(name)
                if name in ("matches", "team_rows", "player_rows") and tables[name].empty:
                    raise DataAcquisitionError("Required pre-cutoff league evidence is missing; no synthetic replacement is allowed")
            snapshot = {name: json.loads(frame.to_json(orient="records", date_format="iso", double_precision=15))
                        for name, frame in tables.items()}
            snapshot["meta"] = {
                "as_of": cutoff.isoformat(),
                **{key: params[key] for key in ("player_id", "team_id", "opponent_id", "tournament_id", "season_id")},
                "source": "MidBlock PostgreSQL, existing Sofascore ingestion", "read_only": True,
                "limits": [
                    "Export uses stored coverage; fixture and completed-match completeness need review.",
                    "Stored season rating timestamps and featured-player minutes are audited when evidence is built.",
                    "Definitions come from the supplied ingestion contract; lateral named-flank mapping remains unverified.",
                ],
            }
    except DataAcquisitionError:
        raise
    except Exception:
        # Database exceptions can include full URLs, passwords, driver arguments
        # and SQL parameters. Never surface their text or chained tracebacks.
        raise DataAcquisitionError("Database export failed; check reachability, credentials, permissions and source schema") from None
    finally:
        if engine is not None:
            engine.dispose()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    coverage = {name: len(frame) for name, frame in tables.items()}
    for name, value in (("snapshot.json", snapshot), ("coverage.json", coverage)):
        destination = output / name
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))
        temporary.replace(destination)
    return snapshot


def export(args):
    """Compatibility wrapper for a parent CLI's argparse Namespace."""
    return export_snapshot(args.player, args.as_of, args.output_dir,
                           getattr(args, "fixture", None), getattr(args, "env_file", None))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--player", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--fixture", help="Optional attributed external fixture JSON")
    parser.add_argument("--env-file", help="Optional local dotenv file; defaults to project-root .env")
    args = parser.parse_args(argv)
    try:
        export(args)
    except DataAcquisitionError as error:
        print(str(error), file=sys.stderr)
        return 1
    except Exception:
        print("Unable to save the snapshot; check local paths and output permissions", file=sys.stderr)
        return 1
    print("Read-only snapshot exported successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
