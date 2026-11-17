#!/usr/bin/env python3
"""Entry point for the portable opponent prototype and repeatable analysis flow."""
import argparse
from datetime import datetime,timezone
import hashlib
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import importlib.util
import json
import math
from pathlib import Path
import platform
import shutil
import sys
import webbrowser

sys.dont_write_bytecode=True

ROOT=Path(__file__).resolve().parent
ORDER=["style","shape","space","players","awareness","verdict","about"]
FOLDERS={"verdict":"00_verdict","style":"01_how_they_play","shape":"02_their_shape","space":"03_where_they_play","players":"04_key_players","awareness":"05_awareness","about":"06_about"}


def path(value):
    p=Path(value).expanduser();return p if p.is_absolute() else ROOT/p


def read(p):return json.loads(Path(p).read_text())
def save(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+"\n")
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def object_digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode()).hexdigest()
def stamp():return datetime.now(timezone.utc).isoformat()


def assert_subset(expected,actual,label="evidence"):
    """Refuse reuse of an approved narrative against changed football evidence."""
    if isinstance(expected,dict):
        for k,v in expected.items():
            if k not in actual:raise ValueError(f"Approved example differs at {label}.{k}")
            assert_subset(v,actual[k],label+"."+k)
    elif isinstance(expected,list):
        if len(expected)!=len(actual):raise ValueError(f"Approved example differs at {label}")
        for i,(a,b) in enumerate(zip(expected,actual)):assert_subset(a,b,f"{label}[{i}]")
    elif isinstance(expected,(int,float)) and not isinstance(expected,bool):
        if actual is None or not math.isclose(expected,actual,rel_tol=1e-10,abs_tol=1e-8):raise ValueError(f"Approved example differs at {label}")
    elif expected!=actual:raise ValueError(f"Approved example differs at {label}")


def verify_example(evidence):
    approved=read(ROOT/"examples/luka-menalo/evidence.json")
    for key in ["fixture","focus","opponent","style","shape","space","key_players","ratings_audit","data_quality"]:
        assert_subset(approved[key],evidence[key],key)
    expected={p["player_id"]:p for p in approved["scouting_supplement"]["players"]}
    actual={p["player_id"]:p for p in evidence["scouting_supplement"]["players"]}
    for pid,p in expected.items():assert_subset(p,actual.get(pid,{}),f"scouting.{pid}")


def module(section):
    file=ROOT/"sections"/FOLDERS[section]/"pipeline.py"
    spec=importlib.util.spec_from_file_location("section_"+section,file)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def build(args):
    from pipeline.data import build_dataset
    work=path(args.workspace);work.mkdir(parents=True,exist_ok=True)
    result=build_dataset(path(args.snapshot),work,path(args.config))
    save(work/"run-manifest.json",{"created_at":stamp(),"stage":"build","snapshot_sha256":digest(path(args.snapshot)),"config_sha256":digest(path(args.config)),"evidence_sha256":object_digest(result),"python":platform.python_version(),"code_sha256":{str(f.relative_to(ROOT)):digest(f) for f in sorted((ROOT/"pipeline").glob("*.py"))}})
    print("Built evidence:",work/"evidence.json")
    return result


def evidence_for(args):
    p=path(args.workspace)/"evidence.json"
    return read(p) if p.exists() else build(args)


def approve_example(work,evidence):
    verify_example(evidence)
    n=read(ROOT/"examples/luka-menalo/narrative.json")
    save(work/"reviewed-narrative.json",n)
    save(work/"review.json",{"reviewed":True,"reviewer":"Previously accepted by the user; English editorial version","reviewed_at":stamp(),"source":"examples/luka-menalo/narrative.json","evidence_sha256":object_digest(evidence),"narrative_sha256":object_digest(n),"note":"Reuse permitted only after comparing the rebuilt numerical evidence and contributions against the reviewed example."})
    return n


def demo(args):
    work=path(args.workspace);e=build(args);n=approve_example(work,e)
    provenance=read(ROOT/"examples/luka-menalo/provenance.json")
    save(work/"provenance.json",provenance)
    for section in ORDER:
        m=module(section);folder=work/"sections"/FOLDERS[section]
        save(folder/"input.json",m.get_input(e));out=m.extract(n,e,provenance);m.validate(out,e);save(folder/"output.json",out)
    render_work(args)
    print("Offline rebuild complete. No database connection or AI call was made.")


def render_work(args):
    from pipeline.render import render
    work=path(args.workspace);e=read(work/"evidence.json");n=read(work/"reviewed-narrative.json");review=read(work/"review.json")
    if not review.get("reviewed") or review.get("evidence_sha256")!=object_digest(e) or review.get("narrative_sha256")!=object_digest(n):
        raise ValueError("Review is missing or stale. Review the draft and use the approve command before rendering.")
    from pipeline.sections import extract_section,validate_section
    for section in ORDER:validate_section(section,extract_section(section,n,e),e)
    p=read(work/"provenance.json") if (work/"provenance.json").exists() else {}
    p["local_review"]=review
    render(e,n,p,work/"report",pdf=not args.no_pdf)
    print("Report:",work/"report/english.html")


def prepare_charts(args,e):
    from pipeline.render import render
    work=path(args.workspace);charts=work/"charts";meta=charts/"evidence-hash.json"
    if not meta.exists() or read(meta).get("sha256")!=object_digest(e):
        render(e,None,None,charts,pdf=False);save(meta,{"sha256":object_digest(e)})
    return charts


def section_command(args):
    e=evidence_for(args);work=path(args.workspace);folder=work/"sections"/FOLDERS[args.name]
    m=module(args.name);save(folder/"input.json",m.get_input(e))
    if args.generate or args.dry_run:
        from pipeline.sections import generate_section
        charts=prepare_charts(args,e)
        result=generate_section(args.name,e,charts,folder,dry_run=args.dry_run)
        if not args.dry_run:save(folder/"draft.json",result)
    else:
        verify_example(e);n=read(ROOT/"examples/luka-menalo/narrative.json");p=read(ROOT/"examples/luka-menalo/provenance.json")
        result=m.extract(n,e,p);m.validate(result,e);save(folder/"output.json",result)
    print("Section:",folder)


def generate(args):
    from pipeline.sections import generate_section
    e=evidence_for(args);work=path(args.workspace);charts=prepare_charts(args,e);n={};chart_notes=[]
    if not args.dry_run:
        # A new draft may not inherit approval from an earlier narrative.
        (work/"review.json").unlink(missing_ok=True)
    for section in ORDER:
        result=generate_section(section,e,charts,work/"sections"/FOLDERS[section],prior_analysis=n,dry_run=args.dry_run)
        if args.dry_run:continue
        chart_notes.extend(result.pop("visualization_analysis",[]))
        if section!="about":n.update(result)
    if not args.dry_run:
        n["visualization_analysis"]=chart_notes;save(work/"draft-narrative.json",n)
        from pipeline.bedrock import configuration
        settings=configuration(ROOT)
        save(work/"provenance.json",{"model":settings["model"],"region":settings["region"],"generated_at":stamp(),"language":"en","state":"unreviewed draft","methodology":"Vendored Nutmeg methodology with English section-specific prompts. Structural validation is not factual review."})
        print("Draft ready for factual review:",work/"draft-narrative.json")
    else:print("Prepared requests only; no AI or database connection was made.")


def approve(args):
    from pipeline.sections import extract_section,validate_section
    work=path(args.workspace);e=read(work/"evidence.json");n=read(path(args.narrative) if args.narrative else work/"draft-narrative.json")
    for section in ORDER:validate_section(section,extract_section(section,n,e),e)
    save(work/"reviewed-narrative.json",n)
    save(work/"review.json",{"reviewed":True,"reviewer":args.reviewer,"reviewed_at":stamp(),"evidence_sha256":object_digest(e),"narrative_sha256":object_digest(n),"note":args.note,"scope":"Reviewer attestation; this command validates structure and records review, not automatic football fact verification."})
    print("Recorded your review. You can now render this exact narrative and evidence.")


class PreviewHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control","no-store, max-age=0")
        super().end_headers()


def serve(args):
    from functools import partial
    folder=(path(args.workspace)/"report") if args.workspace else ROOT/"prototype"
    if not (folder/"english.html").exists():raise ValueError("No English report here. Run demo first or omit --workspace for the bundled prototype.")
    server=ThreadingHTTPServer(("127.0.0.1",args.port),partial(PreviewHandler,directory=str(folder)))
    url=f"http://127.0.0.1:{server.server_port}/english.html"
    print(url,flush=True)
    if args.open:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()


def doctor(args):
    print("Python:",platform.python_version())
    for name in ["numpy","pandas","pydantic","playwright","boto3","sqlalchemy","psycopg2","dotenv"]:
        print(name+":", "installed" if importlib.util.find_spec(name) else "missing (run setup.sh)")
    for name in ["data/raw/snapshot.json","prototype/english.html","vendor/nutmeg/core/nutmeg.py"]:
        print(name+":", "present" if (ROOT/name).exists() else "missing")
    from pipeline.render import chromium_path
    print("Chromium:",chromium_path() or "Install with python -m playwright install chromium")
    print("No credentials were read or connections attempted.")


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest="command",required=True)
    for name in ["demo","build","render","section","generate","approve"]:
        p=sub.add_parser(name);p.add_argument("--workspace",default="work/demo");p.add_argument("--snapshot",default="data/raw/snapshot.json");p.add_argument("--config",default="config/report.json");p.add_argument("--no-pdf",action="store_true")
        if name=="section":p.add_argument("name",choices=FOLDERS);p.add_argument("--generate",action="store_true");p.add_argument("--dry-run",action="store_true")
        if name=="generate":p.add_argument("--dry-run",action="store_true")
        if name=="approve":p.add_argument("--reviewer",required=True);p.add_argument("--note",required=True);p.add_argument("--narrative")
    p=sub.add_parser("serve");p.add_argument("--port",type=int,default=4182);p.add_argument("--open",action="store_true");p.add_argument("--workspace")
    sub.add_parser("doctor")
    p=sub.add_parser("acquire");p.add_argument("--player",required=True);p.add_argument("--as-of",required=True);p.add_argument("--output-dir",default="data/raw/new-snapshot");p.add_argument("--fixture")
    args=parser.parse_args()
    try:
        if args.command=="acquire":
            from pipeline.export_snapshot import export_snapshot
            export_snapshot(args.player,args.as_of,path(args.output_dir),fixture_path=path(args.fixture) if args.fixture else None,env_path=ROOT/".env")
        else:{"demo":demo,"build":build,"render":render_work,"section":section_command,"generate":generate,"approve":approve,"serve":serve,"doctor":doctor}[args.command](args)
    except (ValueError,FileNotFoundError,ModuleNotFoundError) as exc:
        parser.exit(1,f"{type(exc).__name__}: {exc}\n")


if __name__=="__main__":main()
