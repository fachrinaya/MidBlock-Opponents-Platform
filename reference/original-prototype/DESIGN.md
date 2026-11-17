---
name: MidBlock Player Platform
description: A friendly personal feed for a player's season, in MidBlock's graphite, red and emerald on a dark graphite ground.
colors:
  ground-graphite: "#0b0b0c"
  card-graphite: "#161617"
  inset-deep: "#101011"
  track: "#232325"
  track-on: "#343437"
  pop-graphite: "#2b2b2e"
  ink-light: "#f5f5f6"
  ink-soft: "#b4b4b8"
  ink-mute: "#8a8a90"
  line-graphite: "#2a2a2d"
  line-soft: "#212123"
  rail-graphite: "#0f0f10"
  rail-graphite-raised: "#19191a"
  rail-graphite-hover: "#242426"
  on-rail: "#f5f5f6"
  on-rail-muted: "#b4b4b8"
  action-red: "#db1a1a"
  action-red-hover: "#c21616"
  action-red-text: "#ff9090"
  emerald-deep: "#1f8f4e"
  emerald-text: "#5fd38d"
  emerald-dot: "#34b36b"
  emerald-wash: "#14301f"
  amber: "#f0a500"
  amber-wash: "#3a2d0e"
  amber-text: "#f3c75f"
  negative-ember: "#f2a45e"
  pitch-green: "#122219"
  pitch-line: "#4f7a62"
  away-graphite: "#5a5a60"
typography:
  display:
    fontFamily: "Satoshi, system-ui, sans-serif"
    fontSize: "40px"
    fontWeight: 800
    lineHeight: 1.05
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Satoshi, system-ui, sans-serif"
    fontSize: "28px"
    fontWeight: 800
    lineHeight: 1.12
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Satoshi, system-ui, sans-serif"
    fontSize: "20px"
    fontWeight: 800
    lineHeight: 1.2
    letterSpacing: "-0.015em"
  body:
    fontFamily: "Satoshi, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
    fontFeature: "tabular-nums"
  label:
    fontFamily: "Satoshi, system-ui, sans-serif"
    fontSize: "13px"
    fontWeight: 700
    lineHeight: 1.5
rounded:
  ctl: "10px"
  card: "16px"
  pill: "999px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.action-red}"
    textColor: "#ffffff"
    rounded: "{rounded.pill}"
    padding: "0 20px"
    height: "44px"
  button-primary-hover:
    backgroundColor: "{colors.action-red-hover}"
  button-soft:
    backgroundColor: "{colors.track}"
    textColor: "{colors.ink-light}"
    rounded: "{rounded.pill}"
    padding: "0 20px"
    height: "44px"
  card:
    backgroundColor: "{colors.card-graphite}"
    textColor: "{colors.ink-light}"
    rounded: "{rounded.card}"
    padding: "24px"
  input:
    backgroundColor: "{colors.inset-deep}"
    textColor: "{colors.ink-light}"
    rounded: "{rounded.ctl}"
    padding: "10px 14px"
    height: "44px"
  chip-good:
    backgroundColor: "{colors.emerald-wash}"
    textColor: "{colors.emerald-text}"
    rounded: "{rounded.pill}"
    padding: "4px 10px"
  chip-warn:
    backgroundColor: "{colors.amber-wash}"
    textColor: "{colors.amber-text}"
    rounded: "{rounded.pill}"
    padding: "4px 10px"
  nav-item:
    textColor: "{colors.on-rail-muted}"
    rounded: "{rounded.ctl}"
    padding: "12px 14px"
  nav-item-active:
    backgroundColor: "{colors.action-red}"
    textColor: "#ffffff"
  tab-selected:
    backgroundColor: "{colors.track-on}"
    textColor: "{colors.ink-light}"
    rounded: "{rounded.pill}"
    padding: "10px 18px"
---

# Design System: MidBlock Player Platform

## Overview

**Creative North Star: "The Personal Feed"**

A player's season presented the way a friendly consumer app presents a life: graphite cards on a deep graphite ground, plain words, and one bright action colour. It is a working app (profile, report log, benchmark log, monthly recap, media builder, improve plan), not a cold analyst dashboard, while keeping the connected structure of the match report. The palette is MidBlock's own: a deep graphite rail, red for things you can press, light emerald for positive movement and chart data, amber for highlight. The page is dark (`color-scheme: dark`); the ground is no longer blush.

Personality is warm, confident, and playful in motion. Names and numbers are heavy; everything else is quiet. The signature moves are the customizable banner with an overlapping avatar and name plate, and a spring press (scale to 0.96) on every action.

**Key Characteristics:**
- Dark graphite ground, slightly lighter graphite cards, deep graphite rail; depth is tonal, with a faint white ring and a deep black drop.
- Red is reserved for pressable things; emerald carries "good" and chart data (light emerald for text, deep emerald for fills).
- One typeface (Satoshi variable): extra-bold for names and big numbers, regular to bold for reading text.
- Moderate radii: 16px cards, 10px controls, full pills for buttons and tabs.
- The player's chosen accent (`--accent`, default emerald) tints their avatar only.

## Colors

A graphite neutral field, graphite structure, and three working accents, each with one job. Text is a near-white on dark.

### Primary
- **Action Red** (`action-red`): primary buttons, the active navigation item, selected preset borders, checkbox/radio accents. Its rarity on a screen is the point: if it is not pressable, it is not red. Hover: **Action Red Hover** (`action-red-hover`). Error text and the red post tile use **Action Red Text** (`action-red-text`), a light pink that stays legible on dark.

### Secondary
- **Emerald Deep** (`emerald-deep`): fills only (white text on top): high rating tiles, bar fills, AI spark tile, goal markers, peer-chip border, avatar default.
- **Emerald Text** (`emerald-text`): on dark, emerald as text and line: links, focus ring and input focus border (with a 20% ring), positive deltas ("good"), selected peer chips, AI "who" label, selection highlight, latest-item outline.
- **Emerald Dot** (`emerald-dot`): player markers on the formation and scatter graphics.
- **Emerald Wash** (`emerald-wash`): good chips, AI text panels, selected peer chips, the "me" table row, mid rating tiles.

### Tertiary
- **Amber** (`amber`): highlight only: nav count dot, bookings, transition-state bar, warning bars. **Amber Wash** and **Amber Text** (`amber-wash`, `amber-text`) form the warn chip, note and low-rating pairing.
- **Negative Ember** (`negative-ember`): negative deltas, a light orange. Declines are orange, never red, so red stays an action signal.

### Neutral
- **Ground Graphite** (`ground-graphite`): page background. **Card Graphite** (`card-graphite`): cards. **Inset Deep** (`inset-deep`): inputs, embeds, date tiles and disabled table rows, sunk below the card.
- **Track** (`track`): tab and segment tracks, bar tracks, neutral chips, soft buttons. **Track On** (`track-on`): selected tab, segment and chapter link. **Pop Graphite** (`pop-graphite`): tooltips and toasts.
- **Ink Light** (`ink-light`): primary text. **Ink Soft** (`ink-soft`) for secondary text, **Ink Mute** (`ink-mute`) for tertiary text and placeholders.
- **Line Graphite** (`line-graphite`) for control borders and axes, **Line Soft** (`line-soft`) for row dividers and chart grids.
- **Rail Graphite** (`rail-graphite`): the rail, banner base, report hero and login art. **Rail Graphite Raised / Hover** (`rail-graphite-raised`, `rail-graphite-hover`), **On Rail** (`on-rail`) and **On Rail Muted** (`on-rail-muted`) for content on the rail.
- **Pitch Green** (`pitch-green`) and **Pitch Line** (`pitch-line`): pitch graphic surface and markings. **Away Graphite** (`away-graphite`): opposition markers and opposition timeline icons.

### Named Rules
**The Press Means Red Rule.** Red marks only what can be pressed (primary action, active nav). Never use it for data, status or decoration.
**The Emerald Is Good Rule.** Positive movement and chart fills are emerald, light emerald when it is text on dark and deep emerald when it is a fill; negatives are light orange; highlights are amber. Colour never carries meaning alone: deltas also carry a sign and words.

## Typography

**Display Font:** Satoshi (variable, bundled `fonts/Satoshi-Variable.woff2`, weight 300-900) with system-ui, sans-serif
**Body Font:** Satoshi, same file, regular to bold weights
**Label/Mono Font:** none; numbers use Satoshi's tabular figures globally.

**Character:** One family, two voices. Extra-bold (800) for names, headings and big numbers; 400 to 700 for reading and labels.

### Hierarchy
- **Display** (800, 40px, 1.05): profile name (h1); 32px on small screens; 44px on the login panel.
- **Headline** (800, 28px, 1.12): page and chapter headings, and pinned stat numbers.
- **Title** (800, 20px, 1.2): card headings; log-item titles 19px.
- **Body** (400, 16px, 1.5): reading text, capped near 62-70ch; secondary copy 14-15px in Ink Soft.
- **Label** (700, 13px): field labels, table headers, legends, deltas, chips. Sentence case, no tracking.
- **Score numeral** (800, 56px, tracking -0.03em): the match score only.

### Named Rules
**The Heavy Names Rule.** Extra-bold is for names and numbers that matter; running text stays at 400 to 700.
**The Tabular Numbers Rule.** Tabular figures stay on everywhere so columns and deltas align.

## Layout

A fixed 252px graphite rail beside a fluid content column; content centres at a 1060px maximum with 32px side padding. Pages stack as a single grid with 24px gaps; two-column splits use 24px gaps (equal, or 3fr/2fr). The report adds a sticky 200px chapter list beside the article. Spacing rhythm is 4/8/12/16/24/32px, with 16px inside feed stacks and 24px inside cards.

Responsive: at 1100px two-column grids and the report collapse to one column and the chapter list becomes a horizontal scroll strip. At 900px the rail becomes a fixed bottom bar of icon-over-label items, the banner shrinks to 150px and the avatar to 96px, and log items re-flow to a two-column grid.

## Elevation & Depth

Mostly tonal: on a dark ground, depth comes from the lighter graphite card (`#161617` over `#0b0b0c`) plus one shadow of a faint white 1px ring and a deep black drop. Lift appears on hover for pressable cards. The graphite rail and report hero sit slightly apart from the ground.

### Shadow Vocabulary
- **Card** (`box-shadow: 0 0 0 1px rgba(255,255,255,.04), 0 12px 28px -14px rgba(0,0,0,.7)`): all cards.
- **Card hover** (`0 1px 2px rgba(255,255,255,.06), 0 16px 32px -14px rgba(0,0,0,.8)`): pressable log items.
- **Selected control** (`0 2px 8px -3px rgba(15,25,35,.25)`): selected tab, segment or chapter link (it barely reads on Track On; the fill carries selection).
- **Primary glow** (`0 8px 18px -10px rgba(219,26,26,.7)`): primary button only.
- **Avatar plate** (`0 0 0 6px var(--card), 0 10px 24px -10px rgba(0,0,0,.6)`): profile avatar over the banner, ringed in card colour.
- **Tooltip** (`0 10px 24px -10px rgba(0,0,0,.8)`): tooltips.

### Named Rules
**The Soft Lift Rule.** Shadows are diffuse with negative spread (the only hard element is the 1px white ring at 4%); no offset shadows.

## Shapes

Moderately rounded. Cards 16px, controls and nav items 10px, banner presets and embeds 12-18px, buttons, tabs, chips and toasts are full pills, avatars and swatches are circles. Chart bars are pills; legend swatches are 4px-radius squares. Borders are 1.5px Line Graphite on controls and 1px Line Soft for dividers; cards carry no border.

Motion: entry is a 0.45s rise (10px, ease-out `cubic-bezier(0.16,1,0.3,1)`); presses use scale 0.96-0.99 on `cubic-bezier(0.25,1,0.5,1)` (0.3s). Reduced-motion removes all animation and transition.

## Components

### Buttons
- **Shape:** full pill, 44px tall (36px small), 700 weight, 15px.
- **Primary:** Action Red fill, white text, 20px side padding, red glow shadow; hover Action Red Hover.
- **Soft:** Track fill, 1.5px Line Graphite border, Ink Light text, hover lightens border to Ink Mute. **Ghost:** transparent, 7% white tint on hover. **On-dark:** 14% white glass with white border, for use over the banner.
- **Press:** scale 0.96 spring. **Disabled:** Track fill, Ink Mute text, no shadow.

### Chips
- Pill, 13px/700. Neutral Track/Ink Soft; good (Emerald Wash/Emerald Text), warn (Amber Wash/Amber Text), graphite (white on Rail Graphite Hover, for "new" pills).

### Cards / Containers
- 16px radius, Card Graphite, Card shadow, 24px padding; flush variant (no padding, clipped) for the profile header and media. Embeds and date tiles sink to Inset Deep.

### Inputs / Fields
- 44px, 10px radius, 1.5px Line Graphite border, Inset Deep fill; hover border lightens; focus shows Emerald Text border plus 4px emerald 20% ring. Labels 13px/700 Ink Soft above. Errors in Action Red Text, 14px/600.

### Navigation
- Rail items (Profile, Reports, Benchmark, Opponents, Monthly, Media, Improve) are 10px-radius rows, On Rail Muted text; hover lifts to Rail Graphite Raised; the current page is filled Action Red with white text; a pill amber count dot may sit at the end.
- Content tabs and segmented controls: Track pill track, selected pill is Track On with Ink Light text.

### Profile header (signature)
- 220px customizable banner (preset art or upload), overlapping 120px avatar with a 6px card-colour ring, name in Display, pinned stats in Headline numerals with 13px labels, and a Customize action.

### Feed post and AI narrative
- Post: 52px 18px-radius icon tile (emerald wash, red 20% tint, amber wash or graphite) beside the text, with an optional bordered Inset Deep embed. AI text sits in a Emerald Wash panel with a deep-emerald spark tile and a shimmer loading state.

### Monthly recap
- Month card: the latest month is a featured Card Graphite card with a Emerald Text outline; its header row (date tile, title, record, verdict line, video pills, rating numeral) links to the recap, and an Inset Deep brief sits inside below a Line Soft divider (team style table against season average, player KPIs, best and still-level category chips). Older months are plain cards without the brief.
- Video card: 16:9 pitch-green poster with faint route arrows, a 64px glass play disc that turns Action Red on hover, a duration chip and a tag (The Good: Emerald Deep; The Bad: Amber with Graphite text). Body carries title, a emerald or amber one-line purpose, summary and meta.
- Video player: modal over a blurred scrim, a screen, a segmented progress track (one segment per clip, emerald or amber fill), play/pause, a coach note panel and a clip list beside it (bottom on mobile). Footage is a placeholder in the prototype.

### Monthly goals
Logic, formulas and API: `docs/MONTHLY_GOALS.md`. Classes: `gl-*` in `prototype/styles.css`.

- **Running-month card, no goals yet:** the top of the Monthly list, styled as `mo-wait`: a transparent card with a 1.5px dashed Line Graphite border, an Inset Deep date tile (OCT / 2026), the title "October is still going", a neutral "In progress" chip, one line of copy, and a small primary (Action Red) button "Set your October goals" with a target icon. A tiny Ink Mute line beside it reads "Last benchmark: week N, date".
- **Running-month card, goals saved:** a plain Card Graphite card with no emerald outline. The outline stays with the latest published recap, so only one card is outlined.
  - **Header row:** date tile, title "Your October goals", "In progress" chip, a meta line, an Overall block (Ink Mute label, `now → goal` in 28px/800, goal in Emerald Text), and a soft small "Edit goals" button with a pencil icon.
  - **Below a Line Soft divider, on Inset Deep:**
    - "k of n goals reached so far" (h4), with a legend: emerald square "Where you are now", Ink Light square "Your goal".
    - One `pct-row` per category: name with "W% of your overall" under it; a bar where the fill is now and an Ink Light tick marks the goal; `now / goal`; and a chip, either neutral "X to go" or good "Reached" with a check.
  - **Mobile:** the header stacks (date and title, then Overall, then button); progress rows become `name · value · chip` over a full-width bar.
- **Goals editor (`#/monthly/goals`):** a 3fr/2fr grid that collapses to one column at 1100px.
  - **Left card, "One goal per category":** one row per category, with Line Soft dividers.
    - Name in 17px/800, with a tiny line "W% of your overall · median CM 50".
    - Three facts (Start, Now, Per month) as 12px Ink Mute labels over 18px/800 numbers.
    - The control: 44px round soft − / + steppers around a 72px centred number input (800 weight, no spinner), with a full-width range slider (emerald accent) on its own line below.
    - A flag chip, right-aligned: good "+Δ to reach", neutral "Hold your level", or warn "Below where you are now" / "Ambitious: +Δ in a month".
    - A ghost "Use suggested" button sits in the card header.
  - **Right card (sticky, `aria-live="polite"`), "Your overall score goal":**
    - Now (40px/800, Ink Light) › goal (40px/800, Emerald Text), with a delta chip "+4.1 on your overall score".
    - "Where it comes from": one 8px pill bar per category scaled to the largest contribution (emerald fill, Negative Ember when negative), with a signed value.
    - A tiny explainer of the position weights.
    - Primary "Save October goals" and a ghost "Cancel".
  - Every change repaints the right card in place, with no page re-render. The steppers, number field and slider stay in sync.
  - Saving returns to the list with the toast "October goals saved".

### Opponents
Classes: `op-*` in `prototype/styles.css`; code in `prototype/opponents.js`.

- **Next-match card:** Inset Deep day tile (weekday / day / month), an Emerald Text eyebrow "Next match · Round N", the opponent in Title with "away"/"at home" in Ink Soft, a meta line (kick-off in WIB, venue, league position), neutral style chips and form tiles (20px squares: W Emerald Deep, D Track On, L Amber with graphite text), then a big countdown numeral and a primary **Prepare** button.
- **Calendar:** a 7-column month grid (Mon first) of Inset Deep cells. A match is a Track pill with the opponent's short code, H/A and kick-off time; played matches carry a 3px inset left edge (emerald won, grey drew, amber lost) and link to the match report; postponed is amber; the next match has a 2px Emerald Text ring. Today's cell has a 1.5px Ink Mute ring. Soft round buttons switch month. At 900px the grid is replaced by an agenda list.
- **Coming up:** rows of Inset Deep with a Track date tile, opponent, kick-off and style labels; the next one carries a "Next" pill.
- **Scouting report:** the report layout (sticky chapter list, graphite hero with kick-off time in place of the score and a days-to-go tile, "What to expect" verdict). Opponent markers are Ink Soft discs with graphite numbers; the players nearest the player's average position are Amber, with a dashed amber zone; the player is a dashed red ring with "8"; key players have a white ring. Arrows label "Their attack" and "Your attack". The style table colours difference from the league average (emerald more, amber less), never good or bad.
- **Key players:** four tiles (GK, DEF, MID, FWD) with a light number tile, name, a one-line watch note and the Overall score; the selected tile has an Action Red border. The detail shows an amber radar against a dashed median polygon, strength bars (emerald) and weakness bars (amber) with a median tick, and an Inset Deep "How to play against him" box. The direct duel gets a warn chip.

### Media builder
- Two-column builder: a sticky control card (320px) and a stage. Segmented controls for format and visual, swatches for background, a text field for the headline.
- Social canvas: 1:1 (1080) or 9:16 (1080 by 1920) drawn on a canvas so the preview and the PNG are identical; Satoshi, MidBlock wordmark, faint pitch motif, three backgrounds (night, emerald, red).
- Scouting sheet: an A4 page (794 by 1123 px) scaled to fit the stage. It is deliberately light paper (white, graphite header band, Ink graphite text, Emerald Deep and Amber data colours) because it is a printed artefact; it is the one exception to the dark theme and does not use the app's tokens. It prints through a clone appended to the body with the app hidden.

### Rating and bars
- Rating tile: 30px high 10px-radius numeral (Emerald Deep fill with white text high, Emerald Wash mid, Amber Wash low). Bars: 8-10px pills on a Track, Emerald Deep fill, amber variant, Ink Light tick for the reference.
- **Category ratings and the Overall score** follow `docs/RATING_MODEL.md`.
  - Categories: Distribution, Duels, Shooting, Defensive, Discipline, Possession.
  - Values are 0–100 percentiles within the player's position. The position median is 50, so bars and radars use 50 as the median reference.
  - The Overall score (0–100, one decimal) is labelled "Overall score". Never call it "index" (that's the Player Index) or "rating" (that's the Sofascore average match rating, labelled "Avg match rating").
- **Radars** (profile, benchmark, scouting sheet, social graphic) run from 0 to 100, with grid rings at 25 / 50 / 75 / 100. The median polygon is dashed.

## Do's and Don'ts

### Do:
- **Do** reserve Action Red for pressable things and give every action the spring press.
- **Do** put names and key numbers in 800-weight Satoshi and keep running text at 400 to 700.
- **Do** show positive movement in light emerald and declines in light orange, always with a sign or word.
- **Do** use 16px graphite cards on the graphite ground with the single card shadow; step down to Inset Deep for sunken content.
- **Do** use Emerald Text for emerald on dark and Emerald Deep only as a fill.
- **Do** keep 44px minimum touch height on controls and respect reduced motion.

### Don't:
- **Don't** return to a cold, dense analyst-dashboard arrangement: flat grey ground, small tables everywhere, no personality.
- **Don't** use red for data, errors-as-decoration or status fills.
- **Don't** use hard offset shadows or borders on cards.
- **Don't** introduce a second typeface.
- **Don't** hardcode new neutrals; add a token instead.
- **Don't** set Emerald Deep as text on the dark ground; it is too dim.
