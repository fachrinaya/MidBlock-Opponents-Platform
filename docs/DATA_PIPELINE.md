# Data acquisition and build contract

The portable pipeline reads an existing MidBlock database or a frozen raw
snapshot. It does not scrape providers, start an SSH tunnel, write production
tables, or call a model. Database credentials are read from the process
environment or the handoff root's local `.env`; no original server address,
private key, password, or application checkout is needed by the code.

## Acquire a new snapshot

Configure either `DATABASE_URL` for PostgreSQL, or these environment variables:

```dotenv
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=football_analytics
DB_USER=your_read_role
DB_PASSWORD=your_local_secret
```

Use a database route that is already reachable from the developer's machine.
If that route is an existing local tunnel, set its local host and port. The
adapter does not create or reconfigure network access.

From the handoff root:

```sh
python3 run.py acquire --player 'Luka Menalo' --as-of '2026-11-17T00:00:00+07:00'
```

The underlying module can also be called directly:

```sh
python3 -m pipeline.export_snapshot --player 'Luka Menalo' --as-of '2026-11-17T00:00:00+07:00' --output-dir data/raw
```

Its public API is
`export_snapshot(player, as_of, output_dir, fixture_path=None, env_path=None)`.
It returns the snapshot and writes `snapshot.json` and `coverage.json` only
after all queries succeed. Exceptions exposed by the adapter are sanitized;
driver exception strings and connection URLs are not printed. The connection
uses read-only transactions, a repeatable-read snapshot, and statement/connect
timeouts. Environment values take precedence over `.env` values.

`pipeline/snapshot_queries.json` contains the exact query adapter. Its current
identity resolver intentionally targets Indonesia Super League / Liga 1;
change that league resolver for other competitions. Player, team, opponent,
season and competition IDs are resolved from database records, never from an
example ID list. The next stored fixture comes from `match_schedule`, scoped
to the player's latest recorded club and league season. A separately attributed
external fixture can be supplied with `--fixture` when schedule coverage is
missing; the adapter checks club and season and does not invent a match ID.

## Source tables and scopes

| Table | Use and scope |
| --- | --- |
| `match_schedule` | Next unstarted fixture after the timezone-aware cutoff. |
| `match` | Completed matches strictly before the cutoff, in one competition and season; results and formation observations. |
| `team_match_stats` | Per-team detailed match metrics and league comparisons. |
| `player_match_stats` | Positive-minute appearances, actual appearance minutes and recorded per-match contributions. |
| `player_average_positions` | Recorded average activity coordinates and sample counts, restricted to the two teams. |
| `heatmap_player_match` | Opponent activity points; not tracking data or a verified count of every touch. |
| `player_category_rating_season` | Stored category and Overall scores; preserve their existing model values. |
| `player_league_details` | Canonical profile position, detailed role labels, identity and date of birth. |
| `team_style_profile` | Existing profile labels, retained as source context. |
| `player_match_derived_stats` | Existing derived values, including goalkeeper goals prevented and its xGOT coverage. |

The exporter also includes selected `information_schema` metadata for inspection.
It reads no raw secret or connection setting into the snapshot. Completed-match
cutoffs, source-grain uniqueness and fixture identity are checked again at build
time. Rating timestamps must be at or before the analysis cutoff. The current
rating table cannot reconstruct a historical model snapshot by itself: provide
an appropriate archived rating snapshot for an earlier cutoff.

## Build report evidence offline

```python
from pipeline.data import build_dataset

evidence = build_dataset('data/raw/snapshot.json', 'output/data')
```

The API is `build_dataset(snapshot_path, output_dir, config_path=None) -> dict`.
It writes `evidence.json` and `threat-dossier.json`, sets `report_language` to
`en`, and performs no database or model call. By default it reads
`config/report.json`. The expected frozen example selects additional attacking
contributors through that file's `additional_threat_ids`; no example player IDs
are embedded in the pipeline. Remove that property for automatic selection of
the leading fully recorded crossing contributor and scoring contributors,
excluding the main profiles, deduplicated and capped at three additions.

`build_dossier(snapshot, evidence) -> dict` is independently importable. It
preserves the raw metric's known-match count. A partial `covered_total` is only
the sum of recorded values: `per90` is null if any detailed-stat appearance
lacks that metric. Full-appearance goals have their own explicit field and are
never divided by a detailed-stat denominator.

## Denominators and interpretation

- A lineup/results-only fixture can contain default counting-stat zeros. Rows
  with both pass totals and average player ratings absent are excluded from
  detailed-stat means and player raw-rate denominators. Verified results,
  appearance minutes, stored ratings and independently available spatial data
  retain their own scopes. This conservative rule is visible in `data_quality`.
- Team comparisons use the mean of per-match ratios for each team, then the
  mean across available teams. Each displayed metric carries its match count
  and league-team count. Pass share is a possession proxy; defensive-action
  ratios do not establish pressing or tactical quality. Losing-result splits
  describe whole matches eventually lost, not minutes spent trailing.
- Main profiles preserve the stored MidBlock category and Overall scores.
  Their position percentiles already blend positions by played-minute shares;
  do not rank those values again. Category-specific pool counts and stored
  snapshot timestamps remain available. Saved appearance counts can include
  bench listings; displayed appearances use positive-minute records.
- A missing-detail exclusion does not recalculate or repair historical inputs
  to the stored rating model. Raw contribution comparisons and model scores
  therefore retain separately disclosed coverage.
- Shape is a sample-count-weighted composite of frequent starters, with one
  goalkeeper. It is neither a confirmed lineup nor an off-ball formation.
  The player's season activity overlay and opponent windows use different
  samples. Nearness suggests an area to prepare for, not a marking assignment.
- Heatmap lateral shares mean **upper-map / centre / lower-map**. The supplied
  source comments conflict with some recorded role labels; do not rename them
  as verified left/right football flanks. Both axes are mirrored for opponents
  on the existing nominal pitch frame; the underlying calculations are retained.

## Verification

```sh
python3 -m unittest discover -s tests -p test_data.py
```

Offline checks compare the frozen numeric panels with the approved example,
preserve saved ratings, reject future records and duplicate grains, exercise
the lineup-only exclusion and partial-rate semantics, verify configurable and
automatic threat selection, and verify sanitized read-only acquisition errors
without making any database connection. Frozen parity checks skip only if the
raw snapshot or approved example has not yet been staged.

Build dependencies: `pandas`, `numpy`. Acquisition also needs `SQLAlchemy`,
`python-dotenv`, and a PostgreSQL driver such as `psycopg2-binary`.
