# Rating model: category ratings and Overall score

How MidBlock rates a player, for the frontend and backend teams building the Player Platform.

- The prototype (`prototype/`) implements this model with sample data.
- The production numbers are computed by the scraper (`MidBlock/scraper/scrapers/ratings.py`, weights in `MidBlock/scraper/db/constants.py`). They are stored in PostgreSQL `football_analytics`.
- The platform backend **reads** these numbers. The only place the platform calculates an Overall itself is the Monthly Goals feature ([MONTHLY_GOALS.md](MONTHLY_GOALS.md)), and it must use the exact formula in §5.

The model has been live since 30 Oct 2026 and was extended on 1 Nov 2026 (cards counted per match, goalkeeper shot-stopping, shot quality — see §3.4). Every table and history row was rebuilt each time. Earlier numbers are kept only in backups: `MidBlock/backups/ratings_pre_position_c_20261030.dump` (before 30 Oct) and `MidBlock/backups/ratings_pre_20261101.dump` (30 Oct – 1 Nov).

---

## 1. Summary

1. **Per-90 stats:** a player's match stats are summed over the pool (one league season), then converted to per-90 numbers.
2. **Category scores:** in each category, a weighted sum of those per-90 stats gives a raw score. In **Goalkeeping** and **Shooting**, which mix ratios with per-90 counts, each metric is first put on a common scale (standardised), so the weights mean importance.
3. **Percentiles within position:** the raw score is ranked against players of the **same position** (G, D, M, F) in that league season and becomes a **percentile from 0 to 100**. The median player of a position is about 50.
4. **Two positions:** a player who played more than one position is ranked in each position's group, and the percentiles are blended by **minutes share**.
5. **Overall score (0–100):** a **position-weighted average** of the category percentiles. The weights are blended by the same minutes share.

Things that are **not** part of it:
- **Carrying:** it is still computed and stored, but it never counts in the Overall.
- **Running / tracking data and match rating:** these are never used in the Overall.
- **Season-total-only metrics:** big chances created, pass to assist, error leading to goal and possession won in the final third were dropped. A rating is built only from per-match data, so it can be rebuilt for any past matchday. Cards are back (since 1 Nov 2026), counted per match from match incidents, which exist for the 26/27 seasons only.
- **Finishing luck:** goals minus xG and xGOT minus xG are not rated. Over one season they are mostly noise (split-half correlation ≈ 0).

---

## 2. Categories and their metrics

Weights are relative inside a category. A `−` metric is "less is better" (direction −1). Everything is per 90 minutes.

| Category | DB column | Metrics (weight) |
|---|---|---|
| **Distribution** | `distribution_score` | key passes .16, assists .13, accurate passes .10, accurate passes in opposition half .10, accurate long balls .08, accurate crosses .08, accurate passes in own half .07, total passes .05, total crosses .03, total long balls .03, total passes in opposition half .01, total passes in own half .01 |
| **Duels** | `duels_score` | duels won .30, aerial duels won .25, take-ons won .20, take-ons attempted .05, duels lost −.10, aerial duels lost −.07, challenges lost (dribbled past) −.03 |
| **Shooting** | `shooting_score` | xG .25, goals .20, shots on target .18, **xG per shot** .15, total shots .12, hit woodwork .03, big chances missed −.04, shots off target −.02 |
| **Defensive** | `defensive_score` | ball recoveries .19, interceptions .17, tackles won .17, clearances .13, tackles .09, blocked shots (opponent's) .05, dispossessed −.03, errors leading to a shot −.03 |
| **Discipline** | `discipline_score` | fouls drawn .23, penalties won .20, fouls committed −.16, red cards −.14, penalties conceded −.12, yellow cards −.08, offsides −.05, own goals −.02 |
| **Possession & Control** | `possession_score` | touches .40, unsuccessful touches −.35, possession lost −.25 |
| **Goalkeeping** (goalkeepers only) | `goalkeeping_score` | **goals prevented** .35, **save %** .25, successful high claims .10, accurate sweeper actions .08, saves .05, saves inside the box .05, penalty saves .05, punches .04, total sweeper actions .02, crosses not claimed −.01 |
| **Carrying** (stored, not in the Overall) | `carrying_score` | progressive carries .30, total progression .25, total carries .18, progressive carry distance .12, carry distance .10, best single carry .05 |

The source of truth is `METRIC_WEIGHTS` / `METRIC_CATEGORIES` / `SHOT_DERIVED_METRIC_CATEGORIES` in `constants.py`. If the two ever disagree, the code wins. The metrics in bold and the cards are computed from other tables; §3.4 defines them. Own shot blocked and penalties faced are still stored but no longer rated.

---

## 3. Step by step

### 3.1 Pool and data
- **Pool (season grain):** one league season (`season_id` × `tournament_id`). Stored in `player_category_rating_season`.
- **Pool (tournament grain):** all seasons of a tournament together. Stored in `player_category_rating_tournament`.
- **Minutes:** a player needs **≥ 45 minutes** in the pool to be rated (`MIN_MINUTES`).
- **Source:** metrics come from `player_match_stats`; cards from `match_incidents`; goals prevented, save % and xG per shot from `shot_match_stats` (§3.4). Leagues with no per-match scraping use the season totals in `player_league_stats` instead, with the same metric names after mapping (no cards and none of the §3.4 metrics there).

### 3.2 Per 90
`value_p90 = metric_sum / minutes_played × 90`.

If a metric is never tracked for a whole league, it stays **empty** for that league. It is never turned into 0. For example, Carrying is empty for all Indonesian leagues.

### 3.3 Raw category score
`raw_c = Σ direction_m × weight_m × value_p90_m`, summed over the metrics in category *c* that exist.

In **Goalkeeping** and **Shooting**, `value_p90_m` is first standardised within the pool: `(value − mean) / sd`, with mean and sd taken over the pool's goalkeepers (Goalkeeping) or all its players (Shooting). A missing value counts as the mean. The other categories use the raw per-90 values.

A player with no tracked metric in a category has **no score** for it (null). Never treat that as 0.

### 3.4 Metrics computed from other tables

All are per match, so a past matchday can be rebuilt exactly. They are stored per player per match in `player_match_derived_stats` (built by `scraper/scrapers/derived_stats.py`, a cron step after `incidents` and before `ratings`; NULL = unknown, never 0), and the rating sums those columns. The ratios (save %, xG per shot) are computed from the summed columns, not stored per match.

- **Cards** (`red_cards`, `yellow_cards`): counted from `match_incidents` (`incident_type = 'card'`; red = `red` + `yellowRed`, so a second yellow is one red; rescinded cards, staff and players who didn't play are left out). A match with no incidents scraped is **unknown**, not 0, and the per-90 rate uses only minutes from matches with incidents. Incidents exist for the 26/27 seasons only, so 25/26 has no cards. Season totals from `player_league_stats` are never used for cards.
- **Goals prevented** (keepers, per 90): over the shots on target the keeper faced while on the pitch, `Σ (xGOT − 1 if goal else xGOT)`. On-pitch window from the substitution incidents, else from minutes played. Penalties included; own goals and shootout kicks excluded. A goal without xGOT (2–4% in leagues that have it) gets the league season's average xGOT of goals (penalties separately). Per 90 of minutes in matches with xGOT. Leagues without xGOT (Thai League 25/26, ACL Two, ASEAN Championship) have no value; the other metrics carry the category.
- **Save %** (keepers): `(saves + 15 × pool_save_rate) / (shots on target faced + 15)` — saves over shots on target faced, pulled toward the pool's average by 15 shots so small samples stay near average.
- **xG per shot** (shooting quality): `(npxG + 10 × pool_rate) / (np shots + 10)` over non-penalty shots with xG (penalties would inflate it for penalty takers), pulled toward the pool's average by 10 shots. No value in leagues without xG.

### 3.5 Minutes share per position
Every match row in `player_match_stats.position` holds one of `G`, `D`, `M`, `F`.

`share_p = minutes at position p / total minutes with a position`.

- Players with no per-match data (season-totals leagues) count 100% at their profile position (`player_league_details.position`).
- If no position is known at all, they count as M.

### 3.6 Percentile within position
For each category and each position *p*:
- **The group** is every player with `share_p > 0` and data in that category. A player with minutes at two positions is in both groups.
- **The rank** is the average rank, so ties share a rank (pandas `rank(pct=True)`). For a value with *L* lower values and *E* equal values (itself included) in a group of *n*:

  `pct = (L + (E + 1) / 2) / n × 100`

  Example: the group values are `0, 0, 0, 1.2, 2.5`. The three zeros each get **40**, then **80** and **100**.

The player's category score is the minutes-share blend over the positions they played, divided by the shares that actually have a percentile:

`score_c = Σ_p share_p × pct_{c,p} / Σ_p share_p`

**Goalkeeping** is ranked only in the G group, so outfield players have no Goalkeeping score.

### 3.7 Overall score
Weights per position (%):

| Category | G | D | M | F |
|---|---|---|---|---|
| Goalkeeping | 60 | – | – | – |
| Defensive | 5 | 30 | 15 | – |
| Duels | – | 25 | 15 | 25 |
| Distribution | 20 | 20 | 35 | 20 |
| Shooting | – | – | 10 | 40 |
| Possession & Control | 10 | 15 | 20 | 10 |
| Discipline | 5 | 10 | 5 | 5 |

These come from `POSITION_OVERALL_WEIGHTS` in `constants.py`.

1. **Blend the weights by minutes share:** `w_c = Σ_p share_p × W[p][c]`.
2. **Take the weighted average over the categories that have a score**, rescaling the weights:

   `overall = Σ_c w_c × score_c / Σ_c w_c`

So if Possession has no data (as in some leagues), the remaining weights are rescaled to 100%.

---

## 4. Worked examples

**Single position, the prototype's player, week 28.** He is a midfielder, so `share_M = 1`.

| | Distribution | Duels | Shooting | Defensive | Discipline | Possession |
|---|---|---|---|---|---|---|
| Score | 68 | 54 | 70 | 41 | 62 | 76 |
| M weight | 35 | 15 | 10 | 15 | 5 | 20 |

Overall = (35·68 + 15·54 + 10·70 + 15·41 + 5·62 + 20·76) / 100 = **63.35 → 63.4**.

If Possession had no data, it would be (35·68 + 15·54 + 10·70 + 15·41 + 5·62) / 80 = **60.2**.

**Two positions.** The player has 357 minutes at D and 262 at M, so the shares are 0.577 / 0.423.

| | Distribution | Duels | Shooting | Defensive | Discipline | Possession |
|---|---|---|---|---|---|---|
| Percentile among D | 70 | 60 | 55 | 50 | 60 | 45 |
| Percentile among M | 40 | 65 | 30 | 80 | 60 | 35 |
| **Blended score** | 57.3 | 62.1 | 44.4 | 62.7 | 60.0 | 40.8 |
| **Blended weight** | 26.35 | 20.77 | 4.23 | 23.65 | 7.88 | 17.12 |

Overall = Σ weight × score / 100 = **56.4**.

---

## 5. The Overall formula for clients

Any place that recalculates an Overall from category values (Monthly Goals, "what if" tools) must use exactly §3.7:

```
overall(scores, shares) =
  w_c   = Σ_p shares[p] × W[p][c]          for every category c except Carrying
  keep  = categories where scores[c] is not null and w_c > 0
  return Σ_keep w_c × scores[c] / Σ_keep w_c
```

- **Round only for display.** Show one decimal.
- **Use the same `shares` the stored rating used.** That is the minutes split up to that snapshot; the player's main position alone is only a fallback.
- **Self-check:** with the player's current category scores, this function returns their stored `overall_score`, apart from rounding.

The prototype runs on a single position (centre-midfielder): `D.CAT_W` and `D.overall()` in `prototype/data.js`.

---

## 6. Where the numbers live

| Table | Grain | Notes |
|---|---|---|
| `player_category_rating_season` | player × season × tournament | Current rating. `*_score` columns + `overall_score`, `minutes_played`, `matches_played`. |
| `player_category_rating_tournament` | player × tournament | All seasons of the tournament pooled. |
| `player_category_rating_season_history` | player × season × tournament × `round` | One row per **team matchday** ("after round N"). `snapshot_at` = time of the last change, `pool_size` = players rated. Rows with `round` NULL are the single snapshot of season-totals-only leagues. |
| `player_category_rating_tournament_history` | player × tournament × season × `round` | Same idea for the tournament pool. |

- **Column meaning:** the schema is unchanged. Every `*_score` column now means "percentile among players of the same position", and `overall_score` is the position-weighted Overall.
- **Not the same thing:** `player_index_season.overall_index` is the **Player Index**, a different metric (the player's share of team output). Never label it "Overall score".
- **Update timing:** the daily scraper (10:00 WIB) re-rates every league it scrapes and writes the current round into history. A completed round stays as it was once the team plays its next round.

---

## 7. Display rules (frontend)

- **Labels:** call the 0–100 number **"Overall score"**.
  - Not "rating": the Sofascore **average match rating** (e.g. 7.4) is a separate stat, shown as "Avg match rating".
  - Not "index": that's the Player Index.
- **Category values:** show integers from 0 to 100.
  - The position median is **50**, so a reference line or tick at 50 means "median player of your position".
  - Against a chosen peer group, use that group's median instead and say so.
- **Radars run 0–100**, with rings at 25 / 50 / 75 / 100. Don't start the scale above 0, because percentiles below 40 are common.
- **Show the position next to the score.** Overall scores compare across positions only as relative standing. The same number means "stands out as much among his own position", not "equally good".
  - Forwards top out slightly lower, because F mixes wingers and strikers.
  - Goalkeeper groups are small, so their scores are noisy.
- **Small samples:** under ~270 minutes, add a sample-size hint.
