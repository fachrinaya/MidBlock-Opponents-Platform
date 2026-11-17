"""Build auditable Opponents panels from the recorded database snapshot."""
import argparse
import json
import math
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

STYLE = [
    ("poss", "Pass share · possession proxy", "%", 1),
    ("pacc", "Pass accuracy", "%", 1),
    ("dir", "Long-ball share", "%", 1),
    ("terr", "Opposition-half pass share", "%", 1),
    ("shots", "Shots per match", "", 1),
    ("xg", "Expected goals per match", "", 2),
    ("xgps", "Expected goals per shot", "", 3),
    ("cps", "Crosses per shot", "", 2),
    ("di", "Defensive actions per opposition shot", "", 2),
    ("step", "Tackles / (tackles + clearances)", "%", 1),
    ("aer", "Aerial-duel ratio · MidBlock formula", "%", 1),
    ("aw", "Aerial duels won", "%", 1),
]
CATS = {"Distribution":"distribution_score", "Duels":"duels_score",
        "Shooting":"shooting_score", "Defensive":"defensive_score",
        "Discipline":"discipline_score", "Possession":"possession_score",
        "Goalkeeping":"goalkeeping_score"}
WEIGHTS = {
    "G": {"Goalkeeping":60,"Defensive":5,"Distribution":20,"Possession":10,"Discipline":5},
    "D": {"Defensive":30,"Duels":25,"Distribution":20,"Possession":15,"Discipline":10},
    "M": {"Defensive":15,"Duels":15,"Distribution":35,"Shooting":10,"Possession":20,"Discipline":5},
    "F": {"Duels":25,"Distribution":20,"Shooting":40,"Possession":10,"Discipline":5},
}
METRICS = [
    ("passes_accurate", "Accurate passes /90", 1),
    ("long_balls_accurate", "Accurate long balls /90", 1),
    ("duels_won", "Duels won /90", 1),
    ("aerial_duels_won", "Aerial duels won /90", 1),
    ("shots_total", "Shots /90", 1),
    ("expected_goals", "Expected goals /90", 1),
    ("expected_assists", "Expected assists /90", 1),
    ("ball_recoveries", "Ball recoveries /90", 1),
    ("clearances", "Clearances /90", 1),
    ("touches", "Touches /90", 1),
    ("contests_won", "Successful dribbles /90", 1),
    ("saves", "Saves /90 · volume", 1),
    ("fouls_committed", "Fouls committed /90", -1),
    ("possession_lost_control", "Possession losses /90", -1),
]


def num(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def ratio(a, b):
    a, b = num(a), num(b)
    return a / b if a is not None and b is not None and b > 0 else None


def add(*values):
    values = [num(v) for v in values]
    return sum(values) if all(v is not None for v in values) else None


def style_row(r):
    g = r.get
    return {
        "poss": ratio(g("passes_total"), add(g("passes_total"),g("opp_passes_total"))),
        "pacc": ratio(g("passes_accurate"),g("passes_total")),
        "dir": ratio(g("long_balls_total"),g("passes_total")),
        "terr": ratio(g("opposition_half_passes_total"),g("passes_total")),
        "shots": num(g("shots_total")), "xg": num(g("expected_goals")),
        "xgps": ratio(g("expected_goals"),g("shots_total")),
        "cps": ratio(g("crosses_total"),g("shots_total")),
        "di": ratio(add(g("interceptions"),g("tackles"),g("clearances")),g("opp_shots_total")),
        "step": ratio(g("tackles"),add(g("tackles"),g("clearances"))),
        "aer": ratio(add(g("aerial_duels_won"),g("aerial_duels_lost")),add(g("duels_won"),g("duels_lost"),g("aerial_duels_won"),g("aerial_duels_lost"))),
        "aw": ratio(g("aerial_duels_won"),add(g("aerial_duels_won"),g("aerial_duels_lost"))),
    }


def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [clean(v) for v in value]
    if isinstance(value, np.ndarray): return clean(value.tolist())
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (np.floating,float)): return num(value)
    if isinstance(value, pd.Timestamp): return value.isoformat()
    if value is pd.NA or value is pd.NaT: return None
    return value


def records(frame):
    return json.loads(frame.to_json(orient="records",date_format="iso",double_precision=12))


def validate_snapshot(s):
    meta = s["meta"]
    cutoff = pd.Timestamp(meta["as_of"])
    if cutoff.tzinfo is None: raise ValueError("Missing timezone-aware cutoff")
    for name in ("matches","team_rows","player_rows","positions","heatmaps","derived"):
        if name not in s: continue
        for row in s[name]:
            if pd.Timestamp(row["start_timestamp"]) >= cutoff:
                raise ValueError(f"Future data leaked into {name}")
            for key in ("tournament_id","season_id"):
                if row.get(key) is not None and row[key] != meta[key]:
                    raise ValueError(f"Mixed competition/season in {name}")
    for name,keys in (("matches",["match_id"]),("team_rows",["match_id","team_id"]),
                      ("player_rows",["match_id","player_id"]),("positions",["match_id","player_id"])):
        if pd.DataFrame(s[name]).duplicated(keys).any():
            raise ValueError(f"Duplicate source grain in {name}")
    fixture = s["fixtures"][0]
    if pd.Timestamp(fixture["start_timestamp"]) < cutoff:
        raise ValueError("Fixture is not upcoming")
    if {fixture["home_team_id"],fixture["away_team_id"]} != {meta["team_id"],meta["opponent_id"]}:
        raise ValueError("Fixture team identity mismatch")
    return cutoff


def shape_window(pos, ids, focus):
    subset = pos[pos.match_id.isin(ids) & ~pos.substitute.fillna(True)].copy()
    if subset.empty: return {"players":[],"match_ids":ids,"covered_matches":0,"near":[]}
    players=[]
    for pid, group in subset.groupby("player_id"):
        group = group.dropna(subset=["average_x","average_y"])
        if group.empty: continue
        weights = pd.to_numeric(group.points_count,errors="coerce").fillna(0)
        if weights.sum() <= 0: continue
        rawx=float(np.average(group.average_x,weights=weights))
        rawy=float(np.average(group.average_y,weights=weights))
        # Same physical frame: own team attacks right; opponent attacks left.
        x,y=105*(1-rawx/100),68*(1-rawy/100)
        latest=group.sort_values("start_timestamp").iloc[-1]
        players.append({"player_id":int(pid),"name":latest.player_name,
            "number":str(latest.jersey_number),"position":latest.position,
            "x":x,"y":y,"raw_x":rawx,"raw_y":rawy,
            "starts_in_window":int(group.match_id.nunique()),"points":int(weights.sum()),
            "minutes":float(group.minutes_played.sum()),
            "distance_to_focus":math.hypot(x-focus["x"],y-focus["y"]) if focus else None})
    players=sorted(players,key=lambda p:(-p["starts_in_window"],-p["minutes"],p["player_id"]))
    keepers=[p for p in players if p["position"]=="G"][:1]
    players=keepers+[p for p in players if p["position"]!="G"][:10]
    near=sorted([p for p in players if p["position"]!="G"],key=lambda p:p["distance_to_focus"] or 0)[:3] if focus else []
    return {"players":players,"match_ids":ids,"covered_matches":int(subset.match_id.nunique()),"near":near}


def heat_window(heat, ids):
    part=heat[heat.match_id.isin(ids)].dropna(subset=["x","y"]).copy()
    if ((part.x<0)|(part.x>100)|(part.y<0)|(part.y>100)).any():
        raise ValueError("Coordinates outside the ingestion's documented range")
    if part.empty: return {"cells":[],"points":0,"match_ids":ids,"covered_matches":0,"sides":None,"thirds":None}
    # Render in opponent-left direction; bins correspond exactly to plotted points.
    cells,_,_=np.histogram2d(68*(1-part.y/100),105*(1-part.x/100),bins=[28,42],range=[[0,68],[0,105]])
    side=[float((part.y>=200/3).mean()*100),float(((part.y>=100/3)&(part.y<200/3)).mean()*100),float((part.y<100/3).mean()*100)]
    thirds=[float((part.x<100/3).mean()*100),float(((part.x>=100/3)&(part.x<200/3)).mean()*100),float((part.x>=200/3).mean()*100)]
    return {"cells":cells.astype(int).ravel().tolist(),"points":len(part),"match_ids":ids,
            "covered_matches":int(part.match_id.nunique()),"sides":side,"thirds":thirds}


def build(s, source_run="snapshot"):
    cutoff=validate_snapshot(s)
    m=s["meta"]; own,opp,pid=m["team_id"],m["opponent_id"],m["player_id"]
    matches=pd.DataFrame(s["matches"]); teams=pd.DataFrame(s["team_rows"])
    players=pd.DataFrame(s["player_rows"]); positions=pd.DataFrame(s["positions"])
    heat=pd.DataFrame(s["heatmaps"]); details=pd.DataFrame(s["details"])
    ratings=pd.DataFrame(s["ratings"])
    # A lineup/results-only scrape can store default zero counting stats while
    # all detailed passing/rating fields are absent. Those zeros are unknown,
    # not observations (e.g. a team scored goals but supposedly took no shots).
    missing_details=teams.passes_total.isna() & teams.avg_rating.isna()
    missing_pairs=set(zip(teams.loc[missing_details,"match_id"],teams.loc[missing_details,"team_id"]))
    missing_detail_rows=teams.loc[missing_details,["match_id","team_id","team_name","start_timestamp","shots_total","goals"]]
    observed_teams=teams[~missing_details].copy()
    observed_players=players[[((row.match_id,row.team_id) not in missing_pairs) for row in players.itertuples()]].copy()
    focus_rows=players[players.player_id==pid].sort_values("start_timestamp")
    focus_detail=details[details.player_id==pid].iloc[0]
    focus={**s["identity"][0],"number":str(focus_rows.iloc[-1].jersey_number),
        "roles":focus_detail.positions_detailed,"minutes":float(focus_rows.minutes_played.sum()),
        "appearances":int(focus_rows.match_id.nunique())}
    ownpos=positions[positions.player_id==pid].dropna(subset=["average_x","average_y"])
    if not ownpos.empty and ownpos.points_count.sum()>0:
        focus["x"]=float(np.average(ownpos.average_x,weights=ownpos.points_count))*1.05
        focus["y"]=float(np.average(ownpos.average_y,weights=ownpos.points_count))*.68
        focus["position_matches"]=int(ownpos.match_id.nunique())
    else: focus["x"]=focus["y"]=None
    opponent=teams[teams.team_id==opp].sort_values("start_timestamp")
    if opponent.empty: raise ValueError("No opponent match evidence")
    ids=opponent.match_id.astype(int).tolist(); recent=ids[-5:]
    window_ids={"last5":recent,"home":opponent.loc[opponent.home_team_id==opp,"match_id"].astype(int).tolist(),
                "away":opponent.loc[opponent.away_team_id==opp,"match_id"].astype(int).tolist()}
    derived=pd.DataFrame([{ "team_id":r.team_id,"match_id":r.match_id,**style_row(r)} for _,r in observed_teams.iterrows()])
    by_team=derived.groupby("team_id").mean(numeric_only=True)
    style=[]
    for key,label,unit,dec in STYLE:
        mine=derived.loc[derived.team_id==opp,key].dropna()
        avg=num(by_team[key].mean()); val=num(mine.mean())
        scale=100 if unit=="%" else 1
        style.append({"key":key,"label":label,"unit":unit,"decimals":dec,
            "value":val*scale if val is not None else None,
            "league":avg*scale if avg is not None else None,
            "matches":len(mine),"league_teams":int(by_team[key].count())})
    opstyle=derived[derived.team_id==opp].set_index("match_id")
    homeids=window_ids["home"]; awayids=window_ids["away"]
    lostids=[]; matchlog=[]; standings={}
    for _,r in matches.sort_values("start_timestamp").iterrows():
        for home in (True,False):
            tid=int(r.home_team_id if home else r.away_team_id)
            name=r.home_team_name if home else r.away_team_name
            gf,ga=num(r.home_score if home else r.away_score),num(r.away_score if home else r.home_score)
            if gf is None or ga is None: continue
            result="W" if gf>ga else "L" if gf<ga else "D"
            rec=standings.setdefault(tid,{"team_id":tid,"name":name,"played":0,"wins":0,"draws":0,"losses":0,"points":0,"gf":0,"ga":0})
            rec["played"]+=1; rec[{"W":"wins","D":"draws","L":"losses"}[result]]+=1
            rec["points"]+={"W":3,"D":1,"L":0}[result]; rec["gf"]+=gf; rec["ga"]+=ga
            if tid==opp:
                formation=r.home_formation if home else r.away_formation
                formation=formation if isinstance(formation,str) and re.fullmatch(r"\d+(?:-\d+){1,4}",formation) else None
                matchlog.append({"match_id":int(r.match_id),"date":r.start_timestamp,"opponent":r.away_team_name if home else r.home_team_name,
                    "home":home,"gf":gf,"ga":ga,"result":result,"formation":formation})
                if result=="L": lostids.append(int(r.match_id))
    table=sorted(standings.values(),key=lambda r:(-r["points"],-(r["gf"]-r["ga"]),-r["gf"],r["name"]))
    for i,row in enumerate(table): row["rank"]=i+1
    covered_home=[x for x in homeids if x in opstyle.index]
    covered_away=[x for x in awayids if x in opstyle.index]
    covered_lost=[x for x in lostids if x in opstyle.index]
    splits={"home_matches":len(homeids),"away_matches":len(awayids),"lost_matches":len(lostids),
        "home_stat_matches":len(covered_home),"away_stat_matches":len(covered_away),"lost_stat_matches":len(covered_lost),
        "home_pass_share":num(opstyle.loc[covered_home,"poss"].mean()) if covered_home else None,
        "away_pass_share":num(opstyle.loc[covered_away,"poss"].mean()) if covered_away else None,
        "lost_shots":num(opstyle.loc[covered_lost,"shots"].mean()) if covered_lost else None,
        "lost_direct_share":num(opstyle.loc[covered_lost,"dir"].mean()) if covered_lost else None,
        "losing_split_definition":"Full-match averages in matches ultimately lost, NOT minutes spent trailing."}
    shapes={key:shape_window(positions[positions.team_id==opp],v,focus if focus["x"] is not None else None) for key,v in window_ids.items()}
    for key,v in window_ids.items():
        forms=[r["formation"] for r in matchlog if r["match_id"] in v and r["formation"]]
        shapes[key]["formations"]={f:forms.count(f) for f in sorted(set(forms))}
    spaces={"season":heat_window(heat,ids),"last5":heat_window(heat,recent)}
    # Stored ratings already use the prototype's live, minutes-share-blended
    # within-position model. Preserve them rather than ranking those ranks again.
    totals=players.groupby("player_id").agg(minutes=("minutes_played","sum"),apps=("match_id","nunique"))
    canonical=details.drop_duplicates("player_id").set_index("player_id")
    eligible=totals[totals.minutes>=45]
    audit=ratings.set_index("player_id").join(eligible,how="outer")
    audit["consistent"]=(audit.minutes_played-audit.minutes).abs().lt(.01)&audit.matches_played.eq(audit.apps)
    rating_times=pd.to_datetime(ratings.ingested_at,format="ISO8601",utc=True,errors="coerce")
    ratings_ok=bool((rating_times<=cutoff).all()) and not ratings.empty
    if not ratings_ok:
        raise ValueError("Stored rating timestamps are missing or later than the analysis cutoff; provide a valid pre-cutoff rating snapshot")
    score_pool=ratings.copy()
    score_pool["position"]=score_pool.player_id.map(canonical.position)
    position_minutes=players.groupby(["player_id","position"]).minutes_played.sum().unstack(fill_value=0)
    shares=position_minutes.div(position_minutes.sum(axis=1),axis=0)
    for position in WEIGHTS:
        if position not in shares: shares[position]=0
        score_pool["share_"+position]=score_pool.player_id.map(shares[position])
        fallback=score_pool["share_"+position].isna()
        score_pool.loc[fallback,"share_"+position]=score_pool.loc[fallback,"position"].eq(position).astype(float)
    pool_sizes={}
    for pos in WEIGHTS:
        subset=score_pool["share_"+pos].gt(0)
        pool_sizes[pos]=int(subset.sum())
    score_pool["prototype_overall"]=score_pool.overall_score if ratings_ok else np.nan
    latest=players.sort_values("start_timestamp").drop_duplicates("player_id",keep="last").set_index("player_id")
    metric_rows=[]
    for player_id,group in observed_players.groupby("player_id"):
        pos=canonical.loc[player_id].position if player_id in canonical.index else group.iloc[-1].position
        mins=float(group.minutes_played.sum())
        if mins<45: continue
        for metric,label,direction in METRICS:
            values=pd.to_numeric(group[metric],errors="coerce")
            # Partial values are unavailable, not zeros over all season minutes.
            if values.isna().any(): continue
            metric_rows.append({"player_id":int(player_id),"position":pos,"metric":metric,"label":label,
                "value":float(values.sum()/mins*90),"direction":direction,"minutes":mins,"apps":len(group),
                "coverage_scope":"Available detailed-stat matches only; missing-detail fixtures excluded", "total_player_minutes":float(totals.loc[player_id,"minutes"]),"total_player_apps":int(totals.loc[player_id,"apps"])})
    if s.get("derived"):
        for player_id,group in pd.DataFrame(s["derived"]).groupby("player_id"):
            covered=group[group.has_xgot.eq(True)&group.gk_goals_prevented.notna()&group.position.eq("G")]
            covered_minutes=float(covered.minutes_played.sum())
            if covered_minutes>=45:
                metric_rows.append({"player_id":int(player_id),"position":"G","metric":"goals_prevented",
                    "label":"Goals prevented /90 · xGOT-covered matches", "value":float(covered.gk_goals_prevented.sum()/covered_minutes*90),
                    "direction":1,"minutes":covered_minutes,"apps":int(covered.match_id.nunique())})
    metric_df=pd.DataFrame(metric_rows)
    for _,indexes in metric_df.groupby(["position","metric"]).groups.items():
        vals=metric_df.loc[indexes,"value"]*metric_df.loc[indexes,"direction"]
        metric_df.loc[indexes,"percentile"]=vals.rank(method="average",pct=True)*100
        metric_df.loc[indexes,"pool_size"]=len(vals)
    near=shapes["last5"]["near"]
    direct_id=near[0]["player_id"] if near else None
    key_players=[]
    for pos in ["G","D","M","F"]:
        choices=score_pool[(score_pool.position==pos)&score_pool.player_id.map(latest.team_id).eq(opp)].copy()
        if choices.empty: continue
        # Prefer meaningful exposure within each line; preserve the prototype's
        # 45-minute percentile cohort but use starters for featured key players.
        regular=choices[choices.minutes_played>=180]
        if not regular.empty: choices=regular
        selection="Highest stored MidBlock Overall in this line among eligible opponent regulars" if ratings_ok else "Most recorded minutes in this line; score unavailable"
        if direct_id in set(choices.player_id): chosen=choices[choices.player_id==direct_id].iloc[0];selection="Nearest recent average activity location to the focus player"
        else: chosen=choices.sort_values(["prototype_overall","minutes_played"],ascending=False,na_position="last").iloc[0]
        kid=int(chosen.player_id); md=canonical.loc[kid] if kid in canonical.index else None
        stats=metric_df[(metric_df.player_id==kid)&metric_df.percentile.notna()]
        if pos!="G": stats=stats[stats.metric!="saves"]
        else: stats=stats[stats.metric.isin(["goals_prevented","saves","passes_accurate","long_balls_accurate","touches","ball_recoveries","possession_lost_control"])]
        strengths=stats[stats.percentile>=50].sort_values("percentile",ascending=False).head(2)
        weaker=stats[stats.percentile<50].sort_values("percentile").head(2)
        player_shares={p:num(chosen["share_"+p]) for p in WEIGHTS if chosen["share_"+p]>0}
        category_pools={c:{p:int((score_pool["share_"+p].gt(0)&score_pool[col].notna()).sum()) for p in player_shares if c!="Goalkeeping" or p=="G"} for c,col in CATS.items()}
        if abs(float(chosen.minutes_played)-float(totals.loc[kid,"minutes"]))>.01:
            raise ValueError("Featured player's saved rating and pre-cutoff minutes disagree")
        key_players.append({"player_id":kid,"name":chosen.player_name,"position":pos,
            "number":str(latest.loc[kid].jersey_number),"roles":md.positions_detailed if md is not None else [],
            "minutes":num(chosen.minutes_played),"appearances":int(totals.loc[kid,"apps"]),
            "overall":num(chosen.prototype_overall),"categories":{c:num(chosen[col]) for c,col in CATS.items() if (pos=="G" and c in WEIGHTS["G"]) or (pos!="G" and c!="Goalkeeping")},
            "position_pool":pool_sizes[pos],"strengths":records(strengths),"weaker":records(weaker),
            "position_shares":player_shares,"category_pools":category_pools,"rating_at":chosen.ingested_at,
            "all_metrics":records(stats),"direct_duel":kid==direct_id,"selection":selection,
            "age":int((cutoff.tz_localize(None)-pd.Timestamp(md.dob)).days/365.2425) if md is not None and md.dob else None})
    limits=[
        "Recorded league coverage only; the standings are reconstructed and do not include disciplinary point deductions or unrecorded fixtures.",
        "Pass share is a possession proxy; opposition-half pass share is not territorial time. Defensive-action ratios do not establish pressing, a high line, or action location.",
        "The losing-result split uses entire matches lost; event-level behaviour while trailing is not available in this export.",
        "Shape uses starting players' recorded average activity locations, weighted by sample counts, then the most frequent eleven starters. It is not a confirmed lineup or an off-ball formation.",
        "Coordinates retain the source's longitudinal range: own goal at x=0 and attacking goal at x=100. Both axes are mirrored for opponents on a nominal 105 by 68 drawing. Lateral bins mean upper-map / centre / lower-map, not verified named football flanks: the source's lateral convention needs reconciliation with recorded player roles.",
        "Heatmaps show recorded activity points, not a count of every touch or a tracking map. Match windows retain their actual map coverage.",
        "Category scores and Overall are the stored MidBlock model values, unchanged. Categories blend percentiles within each position played by minutes share; Overall blends the documented position weights. Carrying is not in the Overall. The eligible floor is 45 minutes.",
        "Per-90 metric comparisons use only players with complete recorded values across their available detailed-stat matches; the denominator is minutes in those matches, not all appearances. Each metric has its own pool size and coverage. Counting activity does not prove skill or efficiency.",
        "Featured key players use a 180-minute regular-player preference, separate from the 45-minute percentile floor. Small samples remain descriptive; availability and starting selections are unconfirmed.",
    ]
    limits.append("Stored match counts can include unused bench listings; displayed appearances count positive-minute matches. A few rating-pool players have season-aggregate data absent from this match export; raw-metric pools are therefore separate from saved rating-model cohorts.")
    limits.append("Fixtures with both pass totals and average player ratings absent are excluded from detailed-stat calculations, including default shot zeros. Results, appearance minutes, stored model scores and spatial coverage retain their own explicitly labelled scopes; saved model scores have not been recalculated to repair incomplete source inputs.")
    if not ratings_ok: limits.append("Stored season rating timestamps fail the pre-cutoff audit; Overall is unavailable.")
    evidence={"meta":m,"fixture":s["fixtures"][0],"focus":focus,"opponent":next(r for r in table if r["team_id"]==opp),
        "style":{"rows":style,"splits":splits,"match_ids":ids,"league_table":table,"match_log":matchlog,
                 "source_labels":next((r.get("full_label") for r in s["style_profiles"] if r["team_id"]==opp),None)},
        "shape":shapes,"space":spaces,"key_players":key_players,
        "ratings_audit":{"passed":ratings_ok,"matched_players":int(audit.consistent.sum()),"players":len(audit),
            "minutes_match":int((audit.minutes_played-audit.minutes).abs().lt(.01).sum()),
            "appearances_match":int(audit.matches_played.eq(audit.apps).sum()),
            "mismatches":records(audit[~audit.consistent].reset_index()[["player_id","player_name","minutes_played","minutes","matches_played","apps"]]),
            "position_pools":pool_sizes,"weights":WEIGHTS},
        "data_quality":{"excluded_detailed_stat_team_rows":records(missing_detail_rows),"available_opponent_stat_matches":len(opstyle),"opponent_fixtures":len(ids)},
        "disclosures":limits,"source_snapshot_run":source_run}
    return clean(evidence)


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("snapshot");args=parser.parse_args()
    evidence=build(json.loads(Path(args.snapshot).read_text()),Path(args.snapshot).name)
    output=Path(os.environ.get("NUTMEG_OUTPUT_DIR", "."))
    output.mkdir(parents=True, exist_ok=True)
    (output/"evidence.json").write_text(json.dumps(evidence,ensure_ascii=False,indent=2,allow_nan=False))
    print(json.dumps({"fixture":evidence["fixture"],"focus":evidence["focus"],"opponent":evidence["opponent"],
        "style":evidence["style"]["rows"],"keys":[{k:p[k] for k in ["name","position","overall","minutes","direct_duel"]} for p in evidence["key_players"]],
        "ratings_audit":{k:v for k,v in evidence["ratings_audit"].items() if k!="mismatches"}},ensure_ascii=False))
