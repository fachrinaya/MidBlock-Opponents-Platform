# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack
Next.js 13 (Pages Router, repo `samba`) with a component library `dashboard-ui` built on campos (football visualization components; campos' input/output contract is the contract for every wrapper). Go 1.23 + Gin + PostgreSQL backend (`cruyff`). Internal account management lives in `midblock-cms` (Vite + React). Narrative AI via Gemini from the backend. Source plan: `~/Downloads/[PLAN] Player Consulting (Rollback & Future).md` (Part B).

## Users
Players. A player logs in (username + password) and sees their own profile and season dashboard, a log of per-match reports, and a benchmark against comparable players, with new reports arriving each week as they play. Internal staff create and manage player accounts through midblock-cms. The role model must be ready to grow to coach, team and agency users, so every user carries a role identifier.

## Product Purpose
Give each player a personal, always-fresh window into their own football data, so they understand how they played and where they stand, and want to keep coming back. Success is a player who opens it every week, explores their own numbers unprompted, and can explain their game and their gaps in plain language.

## Player Journey
- **Landing: the Profile.** On login the player first sees their Profile, built from the Streamlit Player Profile content (profile, season overview, category scores vs position median, radar, and the detail, season stats, match log, trend, shot and movement tabs). It is framed as a journey that shows how far they have come, not a stats sheet.
- **Report log: an activity feed of their matches.** Each match played adds an entry. Opening one gives the full match report with the same connected structure as the FastAPI report, so the player understands how the match went and what their own contribution was. AI explains every section.
- **Benchmark log: one report per week.** A weekly snapshot is saved per player (including the rank basis and comparable peers used), so past entries stay fixed. The latest entry is the player's current condition; earlier ones show progression, and the player can compare weeks and peers themselves.
- **Opponents: the matchday calendar and a scouting report per upcoming match.** A calendar of every matchday (from `match_schedule`, kick-off in WIB, home/away, status, result) with a next-match card and countdown. Played matches link to their match report; each upcoming match opens a scouting report on the opponent: how they play (`team_style_profile` against the league average, plus when losing and home vs away), their shape (`player_average_positions`, with the players nearest the player's own average position highlighted), where they play (`heatmap_player_match`, side and third shares), one key player per line (category ratings as percentiles within position, with strengths, weaknesses and how to play against him; in midfield the player's direct duel), and what to be aware of, linked to Improve drills. AI explains every section. A report opens a week before kick-off and refreshes after the opponent's next match.
- **Monthly recap: one report per month.** Each month the team publishes a recap that folds the match reports and the weekly benchmarks into one story: a verdict, two coach-made videos (The Good, what to keep; The Bad, what to fix), the month's matches, how the category ratings and Overall score moved, strengths and development priorities per 90, and next-month habits linked to drills. The Monthly list leads with the latest month, showing a brief of how the team played (style against its own season average) and how the player performed.
- **Monthly goals: the player sets them for the running month.** A recap only exists once a month is over, so the running month sits at the top of the Monthly list as an "in progress" card. There the player sets their own goal for each category rating, the value they want to reach by their last benchmark of the month. The Overall score goal is recalculated after every change, with the same position-weighted formula the ratings use. Once saved, the card shows each category's progress (now vs goal, "X to go" / "Reached") and the Overall now → goal. The player owns the goals, not the coach. Spec: `docs/MONTHLY_GOALS.md`.
- **Media: assets the player can take with them.** From fixed templates the player builds a Full Scouting Report (A4, saved as PDF) from any of their season data, or a Social graphic (1:1 Instagram post or 9:16 story, saved as PNG) from ratings and benchmarks only, choosing among cards, radar, pizza and rating form. The player picks content, never the design.
- **Social is a feel, not a feature.** The experience should feel like a social-media / Strava-style personal feed. There is no sharing, following or public profiles; each player's data stays private to them.

## Positioning
- Every match report and benchmark pairs charts with a connected, plain-language AI narrative (hypothesis to evidence, not isolated stat blurbs), generated lazily on first open and cached permanently.
- The benchmark is the player's to control: they choose the rank basis and the comparable players, inside a fairness guardrail (peers must have 0.5x to 2x the focus player's minutes, same season and competition).
- Interactive tools for playing with their own data, built to be habit-forming: players should get hooked on exploring and slicing their data, not just reading a static report.

## Operating Context
- Menus: Main Dashboard (Profile), Report (match log list and per-match detail), Benchmark (weekly log of snapshots, each opening as a full report), Opponents (matchday calendar and per-opponent scouting report), Monthly (one recap per month with two coach videos, plus goals for the running month), Media (template-based asset builder) and Improve (training plan and drills). Reuse `/login` and `/dashboard`.
- Ratings: every category rating and the Overall score follow the MidBlock rating model (`docs/RATING_MODEL.md`).
  - Six categories in the Overall: Distribution, Duels, Shooting, Defensive, Discipline and Possession, plus Goalkeeping for goalkeepers.
  - Each is a 0–100 percentile **within the player's position**. The position median is 50.
  - The Overall score (0–100) is a position-weighted average of them. A centre-midfielder's weights: Distribution 35, Possession 20, Duels 15, Defensive 15, Shooting 10, Discipline 5.
  - The numbers are computed by the MidBlock scraper into `player_category_rating_*`. The platform reads them, and recalculates an Overall only for Monthly goals, with the same formula.
- Report structure mirrors the existing PDF reports in order, structure and AI text. Match report: Hero, Verdict, TOC, Legend, then Match/Game State, Average Position, Team Phase, Heatmap/Spatial, Metrics by Category, Player Index, Footnote, with AI text after each section. Benchmark: Hero, Verdict, TOC, Legend, Category Ratings, Player Index, Market Value Benchmark, Strengths per-90, Development Priority per-90.
- Main Dashboard mirrors the Streamlit Player Profile: season filter, profile cards, season overview, category scores vs position median, radar, and tabs (detail, season stats, match log, trend, shot position, shot xG, movement).
- Data already sits in the PostgreSQL `football_analytics` database (local copy available for reference); new data should appear for users with minimal human intervention.
- Existing PDFs are produced by the internal `player-report` app; this platform is web only.

## Capabilities and Constraints
- In scope: player accounts and login, three menus, per-section AI analysis (English), football visualizations via campos, customizable benchmark, scalable section registry, player-set monthly goals (stored per player per month, see `docs/MONTHLY_GOALS.md`).
- Out of scope: free-form design of Media assets, manual chart annotation, drag-and-drop dashboards, email export, sharing or public profiles. In scope: the player downloading their own Monthly Recap content and Media assets (scouting report as PDF, social graphics as PNG).
- Monthly recap content: the coach uploads two videos per month (The Good, The Bad), each a compilation of timestamped clips with a short note. Everything else in the recap comes from the saved match reports and weekly benchmarks; the month's team-style brief needs team-level style data that the prototype only fakes.
- Monthly goals:
  - Editable only by the player, only for the running month (Asia/Jakarta calendar).
  - Judged against the player's last rating snapshot of the month: `player_category_rating_season_history`, one row per team matchday.
  - The server computes and stores the Overall goal. The client shows the same number live using the weights the server sends.
  - The "goals hit or missed" section of the next recap is still to be designed.
- Charts are rendered with our components, not matplotlib replicas; data and text match the PDFs.
- Benchmark changes the source plan: it is no longer one on-demand page but weekly stored snapshots per player (new data model; the plan's `cruyff` schema section needs updating).
- Narrative states: loading with retry, and a failed state with a retry action.
- Open: campos vendoring method and its component contracts (first task); `pass_match_events` schema for pass networks; production and staging data access for development.

## Brand Commitments
Company name: MidBlock. Verdict palette from the existing PDFs (teal and red) and brand tokens are carried into dashboard-ui; match-report AI text is styled red and benchmark AI text dark, as in the PDFs. No further visual commitments are made here.

## Evidence on Hand
- Two example PDF reports (Match Analysis and Benchmark) and the Streamlit dashboard as structure references.
- A working FastAPI `player-report` app with narrative prompts and schemas.
- A local `football_analytics` PostgreSQL database with match, shot, heatmap, average-position, leaderboard and player-index tables.
- The prototype's Opponents page uses synthetic fixtures and opponents shaped like `match_schedule`, `team_style_profile`, `player_average_positions` and `heatmap_player_match`; the prototype's "today" is 13 Oct 2026. The next opponent (Samudra FC) is hand-written, the others are generated by the same engine.
- The prototype's Monthly and Media pages use synthetic data and placeholder video (no real footage); the PDF is produced through the browser print dialog. The prototype keeps monthly goals in `localStorage` and models one position only (centre-midfielder); production blends weights by minutes per position.
- Implementation specs for the frontend and backend teams: `docs/RATING_MODEL.md` (how ratings and the Overall score are calculated, with worked examples) and `docs/MONTHLY_GOALS.md` (goals flow, formulas, data model, API, acceptance test values).
- No player testimonials, usage metrics or retention data exist yet; none may be invented.

## Product Principles
- Plain language first: every number is explained for a player, not an analyst.
- Analyst-grade structure, friendly experience: keep the connected report structure, make it easy and pleasant to read.
- Tell one connected story per report, not a pile of stats.
- Make exploration the habit: the player should be able to poke at their own data, and each interaction should reward curiosity.
- Fair comparisons by default: guardrails against biased cohorts, with the player in control inside them.
- Data appears without human steps: new matches show up and narratives generate on demand.
