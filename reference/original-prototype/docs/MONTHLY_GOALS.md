# Monthly Goals

While a month is running, the player sets their own goal for each category rating. The goal is the value they want to reach by the end of the month. The platform recalculates their **Overall score goal** after every change, and the saved goals show on the Monthly page with progress.

- The prototype implements this in `prototype/monthly.js`: `goalBase`, `goalIdx`, `goalFlag`, `currentCard`, `goalsView`, `paintSummary` and `saveGoals`.
- The rating model it builds on is in [RATING_MODEL.md](RATING_MODEL.md). Read §3 and §5 there first.

---

## 1. User flow

1. **Monthly list (`#/monthly`).** The running month (e.g. October) has no recap yet; recaps are published on the 1st of the next month. A card for it sits at the top of the list.
   - **No goals saved:** a dashed card, "October is still going · In progress". It says when the recap arrives, has a **Set your October goals** button, and shows "Last benchmark: week N, date".
   - **Goals saved:** a card titled "Your October goals". It shows:
     - the Overall score **now → goal** (e.g. 63.4 → 67.5);
     - "k of n goals reached so far";
     - one progress row per category (bar = now, white tick = goal, chip "X to go" or "Reached");
     - an **Edit goals** button.
2. **Goals editor (`#/monthly/goals`).** Each category row shows:
   - **Start:** the last benchmark before the month began.
   - **Now:** the latest benchmark.
   - **Per month:** the player's typical monthly change.
   - The goal, set with − / + buttons, a number field and a slider (all kept in sync).
   - A flag chip under the row.

   The side panel shows the Overall **now** and **if you hit every goal**, the change, and what each category contributes. It is recalculated on every input, with no save needed. The editor opens with suggested goals (or the saved ones), and **Use suggested** resets to the suggestions.
3. **Save** stores the goals and returns to the list, with a "October goals saved" toast. Goals can be edited again until the month ends.
   - **Reset goals** (in the editor, only when goals are saved) asks for confirmation, deletes the month's goals and returns to the list with a "October goals reset" toast. The running-month card goes back to the "Set your October goals" invitation.
4. **Next (not in the prototype yet):** the month's recap gets a "Your goals: hit or missed" section, judged against the last benchmark of the month.

The player sets the goals, not the coach. Goals are private to the player, like the rest of their data.

---

## 2. Definitions

| Term | Production meaning | Prototype |
|---|---|---|
| Month | Calendar month in Asia/Jakarta time, key `YYYY-MM` | `CURRENT = "2026-10"` |
| Pool | The player's main league season: the `season_id` × `tournament_id` where they have the most minutes this season | one league |
| Benchmark | A row of `player_category_rating_season_history` for that pool (one per team matchday) | `D.WEEKS` |
| **Start** | The last history row with `snapshot_at` **before** the month starts. If none exists, the first row inside the month. | last week of the previous month |
| **Now** | The latest history row | latest week |
| **End of month** (evaluation) | The last history row with `snapshot_at` inside the month | not built yet |
| First row | The first history row of the season (used for the typical change) | `D.WEEKS[0]` |
| Categories | Every category with a score in **Now**, excluding Carrying. Goalkeeping appears only for players with goalkeeper minutes. | 6 categories |

---

## 3. Calculations

Every number below must be calculated the same way on frontend and backend.

### 3.1 Typical monthly change, per category
```
months_elapsed = max(1, (now.snapshot_at − first.snapshot_at) in days / 30.4)
typical_c      = clamp(round((now_c − first_c) / months_elapsed), 1, 5)
```
It is always between +1 and +5. It isn't a prediction, just a sensible step size.

### 3.2 Suggested goal
`suggested_c = min(99, now_c + typical_c)`

### 3.3 Input rules
- Integers from 0 to 100.
- The slider runs from `max(0, min(now_c, start_c) − 10)` to 100. The number field accepts the full 0–100 range.

### 3.4 Flag per category (shown under the row)
| Condition (Δ = goal − now) | Chip | Tone |
|---|---|---|
| Δ < 0 | "Below where you are now" | warn (amber) |
| Δ = 0 | "Hold your level" | neutral |
| Δ > 2 × typical **and** Δ > 5 | "Ambitious: +Δ in a month" | warn (amber) |
| otherwise | "+Δ to reach" | good (emerald) |

These are warnings only and never block saving.

### 3.5 Overall score goal (recalculated on every change)
Use the rating model's `overall()` function (RATING_MODEL.md §5), with the player's **minutes shares at Now**:
```
goal_overall = overall(goals, shares_now)
now_overall  = overall(now_scores, shares_now)       // equals the stored overall_score
change       = goal_overall − now_overall
contribution_c = w_c × (goal_c − now_c) / Σ w      // the "Where it comes from" bars; they add up to change
```
Show one decimal. Never add a fixed number per point; always recalculate from the weights.

### 3.6 Progress on the Monthly card
- Reached when `now_c ≥ goal_c`. Otherwise show "`goal_c − now_c` to go".
- "k of n goals reached so far" counts the reached categories.
- The header shows `now_overall → goal_overall` (the saved `target_overall`).

### 3.7 Test values
Use these from the prototype as acceptance tests. The player is a midfielder (`shares = {M: 1}`, weights Distribution 35, Duels 15, Shooting 10, Defensive 15, Discipline 5, Possession 20).

| | Distribution | Duels | Shooting | Defensive | Discipline | Possession | Overall |
|---|---|---|---|---|---|---|---|
| Start (week 26) | 62 | 54 | 68 | 43 | 60 | 72 | 60.5 |
| Now (week 28) | 68 | 54 | 70 | 41 | 62 | 76 | **63.4** |
| Typical per month | 5 | 3 | 5 | 2 | 2 | 5 | |
| Suggested goal | 73 | 57 | 75 | 43 | 64 | 81 | **67.5** (67.45) |
| Contribution | +1.75 | +0.45 | +0.50 | +0.30 | +0.10 | +1.00 | **+4.1** |

The typical values come from the first row (week 20: 44, 48, 59, 37, 58, 59), with 1.84 months elapsed.

A two-position test (shares D 0.577, M 0.423) is in RATING_MODEL.md §4. The expected Overall is 56.4.

---

## 4. Data model (proposal for `cruyff`)

```sql
CREATE TABLE player_monthly_goal (
  id              BIGSERIAL PRIMARY KEY,
  user_id         BIGINT      NOT NULL REFERENCES users(id),   -- the player's account
  player_id       BIGINT      NOT NULL,                        -- football_analytics player_id
  month           CHAR(7)     NOT NULL,                        -- 'YYYY-MM', Asia/Jakarta
  season_id       INT         NOT NULL,                        -- pool the goals were set against
  tournament_id   INT         NOT NULL,
  targets         JSONB       NOT NULL,   -- {"distribution_score":73,"duels_score":57,...}
  target_overall  NUMERIC(5,2) NOT NULL,  -- goal_overall at save time (server-computed)
  baseline        JSONB       NOT NULL,   -- {"start":{...,"round":N},"now":{...,"round":N},"shares":{"M":1},"weights":{...}}
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, month)
);
```

- `targets` keys are the rating column names: `distribution_score`, `duels_score`, `shooting_score`, `defensive_score`, `discipline_score`, `possession_score`, `goalkeeping_score`.
- `baseline` freezes what the player saw when saving, so the recap can explain the goal even after the ratings move.
- One goal set per player per month. Saving again overwrites it (upsert).

---

## 5. API (proposal)

| Method | Path | Does |
|---|---|---|
| GET | `/api/v1/me/monthly-goals/{month}` | Returns the editor payload: `start`, `now`, `first`, `typical`, `suggested`, `shares`, `weights`, `now_overall`, the saved `targets` / `target_overall` if any, and `editable` |
| PUT | `/api/v1/me/monthly-goals/{month}` | Body `{ "targets": { "distribution_score": 73, ... } }`. Validates, computes `target_overall` with §3.5, stores, and returns the saved object |
| DELETE | `/api/v1/me/monthly-goals/{month}` | Resets the month's goals (deletes the row). Same edit rules as PUT; returns 204 |
| GET | `/api/v1/me/monthly` | The Monthly list. The running month carries `goals: null` or `{ targets, target_overall, now, reached, total }` |

Rules:
- **Authority:** the server is the authority for `target_overall`. The frontend calculates the same number live for the preview, using the `weights` and `shares` from GET, so the two always agree.
- **Who can edit:** only the logged-in player, only for their own `player_id`, and only while `month` is the running month. Otherwise return `editable: false` and 403 on PUT.
- **Validation:** reject category keys that aren't in the player's category set, and values that aren't integers from 0 to 100.
- **No rating yet:** if the player has none this season (< 45 minutes), GET returns `available: false`. The card then says goals open once they have a rating.

---

## 6. Edge cases

- **No history row inside the month yet:** Start = Now = the last row before the month. Goals can still be set.
- **Category without data** (e.g. Possession in some leagues): it isn't shown. The Overall rescales over the rest, per the rating model.
- **The player changes position mid-month:** shares come from the Now row at save time and are stored in `baseline`. The recap evaluates categories one by one, so a position change doesn't break the goals.
- **Transfer to another league mid-month:** the pool changes. Keep the saved goals tied to their `season_id` / `tournament_id`, and show "goals were set at your previous club" in the recap.
- **Rating model changes:** goals keep the `baseline.weights` they were saved with.

---

## 7. Frontend notes

- **Labels:** "Overall score", never "index" (see RATING_MODEL.md §7). Category labels are Distribution, Duels, Shooting, Defensive, Discipline and Possession.
- **Explainer:** show a short line in the editor saying why one point is worth more in some categories. For example, for a midfielder, one point in Distribution moves the Overall seven times as much as one point in Discipline (35 vs 5). Generate it from the weights; don't hard-code it.
- **Design:** components are described in [DESIGN.md](../DESIGN.md) → "Monthly goals".
- **Prototype storage:** the prototype keeps goals in `localStorage` under `mb_goals3`. Production uses the API above.
