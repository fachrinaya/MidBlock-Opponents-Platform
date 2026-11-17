"""Portable local HTML/chart/PDF rendering; never calls an AI or a database."""
from pathlib import Path
import hashlib
import json
import os
import shutil

ROOT=Path(__file__).resolve().parents[1]


def chromium_path():
    if os.getenv("PDF_CHROMIUM_PATH"):
        return os.environ["PDF_CHROMIUM_PATH"]
    mac=Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if mac.exists():
        return str(mac)
    return shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")


def write_page(folder,evidence,narrative=None,provenance=None):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/"pipeline/assets",folder/"assets",dirs_exist_ok=True)
    data=json.dumps({"evidence":evidence,"narrative":narrative,"provenance":provenance},ensure_ascii=False,allow_nan=False).replace("</","<\\/")
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>English · Opponent match briefing · MidBlock</title><link rel="icon" href="assets/img/mb-mark.png"><link rel="stylesheet" href="assets/styles.css"><link rel="stylesheet" href="assets/report.css"></head><body><div id="app"></div><script type="application/json" id="report-data">'+data+'</script><script src="assets/charts.js"></script><script src="assets/report.js"></script></body></html>'
    for asset in ["assets/styles.css","assets/report.css","assets/charts.js","assets/report.js"]:
        digest=hashlib.sha256((folder/asset).read_bytes()).hexdigest()[:12]
        page=page.replace('"'+asset+'"','"'+asset+'?v='+digest+'"')
    for name in ["index.html","english.html"]:(folder/name).write_text(page)


def capture_figures(page,folder):
    folder=Path(folder)
    page.goto((folder/"index.html").as_uri(),wait_until="load")
    page.wait_for_function("window.reportReady === true")
    page.evaluate("document.fonts.ready")
    manifest=[]
    nodes=page.locator("[data-figure-id]")
    for i in range(nodes.count()):
        node=nodes.nth(i)
        page.evaluate("window.originalHidden=[...document.querySelectorAll('[hidden]')];window.originalHidden.forEach(n=>n.hidden=false)")
        entry={"chart_index":i,"figure_id":node.get_attribute("data-figure-id"),"section":node.get_attribute("data-figure-section"),"label":node.inner_text()}
        node.screenshot(path=str(folder/f"figure-{i}.png"))
        page.evaluate("window.originalHidden.forEach(n=>n.hidden=true)")
        manifest.append(entry)
    (folder/"chart_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    return manifest


def render(evidence,narrative,provenance,folder,*,pdf=True):
    from playwright.sync_api import sync_playwright
    folder=Path(folder)
    write_page(folder,evidence,narrative,provenance)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chromium_path(),headless=True)
        try:
            page=browser.new_page(viewport={"width":1440,"height":1000})
            errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
            manifest=capture_figures(page,folder)
            if narrative is not None:
                byid={x["figure_id"]:x for x in narrative["visualization_analysis"]}
                if set(byid)!={c["figure_id"] for c in manifest}:
                    raise ValueError("Narrative must cover every actual chart exactly once")
                narrative["visualization_analysis"]=[{**byid[c["figure_id"]],"chart_index":c["chart_index"],"chart_label":c["label"],"section":c["section"]} for c in manifest]
                write_page(folder,evidence,narrative,provenance)
                page.reload(wait_until="load");page.wait_for_function("window.reportReady === true")
            page.evaluate("document.fonts.ready")
            page.screenshot(path=str(folder/"desktop.png"),full_page=True)
            checks={"browser_errors":errors,"charts":len(manifest),"sections":page.locator("section.chapter").count(),"language":page.locator("html").get_attribute("lang"),"viewports":[]}
            for width in [1440,768,390,320]:
                page.set_viewport_size({"width":width,"height":1000})
                overflow=page.evaluate("document.documentElement.scrollWidth>innerWidth")
                if overflow:raise ValueError(f"Page overflow at {width}px")
                checks["viewports"].append({"width":width,"page_overflow":overflow})
            page.set_viewport_size({"width":390,"height":844});page.screenshot(path=str(folder/"mobile.png"),full_page=True)
            if errors:raise ValueError("Browser errors: "+"; ".join(errors))
            if pdf:
                page.set_viewport_size({"width":1440,"height":1000})
                page.pdf(path=str(folder/"opponent-report-english.pdf"),format="A4",print_background=True,prefer_css_page_size=True)
            (folder/"browser-checks.json").write_text(json.dumps(checks,indent=2))
        finally:
            browser.close()
    return manifest
