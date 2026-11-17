"""Section input selection, identity validation, draft generation and extraction.

Each section folder supplies its editable prompt; this shared runtime enforces
the same evidence and identity contracts. A valid schema is not a fact check.
"""
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from .bedrock import configuration, generate_structured
from .models import schema_for

ROOT = Path(__file__).resolve().parents[1]
SECTION_FOLDERS = {
    "verdict": "00_verdict", "style": "01_how_they_play", "shape": "02_their_shape",
    "space": "03_where_they_play", "players": "04_key_players",
    "awareness": "05_awareness", "about": "06_about",
}
OUTPUT_KEYS = {
    "verdict": ["verdict"], "style": ["how_they_play"],
    "shape": ["shape_notes", "visualization_analysis"],
    "space": ["space_notes", "visualization_analysis"],
    "players": ["key_players_summary", "key_players", "other_threats", "visualization_analysis"],
    "awareness": ["awareness_summary", "awareness"], "about": ["about"],
}


def valid_references(evidence):
    return {"style", "shape.last5", "shape.home", "shape.away", "space.season", "space.last5",
            *(["scouting"] if evidence.get("scouting_supplement") else []),
            *[f"key.{p['player_id']}" for p in evidence["key_players"]]}


def expected_figures(section, evidence):
    if section == "shape":
        return ["shape-last5", "shape-home", "shape-away"]
    if section == "space":
        return ["space-season", "space-last5"]
    if section == "players":
        return [f"key-{p['player_id']}" for p in evidence["key_players"]]
    return []


def get_section_input(section, evidence, prior_analysis=None):
    schema_for(section)
    pack = copy.deepcopy(evidence)
    for window in pack.get("space", {}).values():
        window.pop("cells", None)
    pack.get("ratings_audit", {}).pop("mismatches", None)
    # Retain complete numerical context across sections: chart and narrative
    # cross-checks must not depend on an isolated statistic without its sample.
    return {
        "section": section, "language": "English", "evidence": pack,
        "valid_references": sorted(valid_references(evidence)),
        "expected_figure_ids": expected_figures(section, evidence),
        "required_output_keys": OUTPUT_KEYS[section],
        "prior_review_status": "Prior section drafts are context, not additional evidence.",
        "prior_analysis": copy.deepcopy(prior_analysis or {}),
        "instruction": "Write a practical pre-match briefing in English: threat/role, observable cue, recommended response. Preserve units and sample coverage; label recommendations conditionally. Do not invent opponent tactics or treat a percentile as accuracy.",
    }


def _about(evidence, provenance=None):
    provenance = provenance or {}
    return {"about": {
        "cutoff": evidence["meta"]["as_of"], "source": evidence["meta"].get("source", "MidBlock stored evidence"),
        "fixture_id": evidence["fixture"].get("match_id"),
        "disclosures": copy.deepcopy(evidence.get("disclosures", [])),
        "model": provenance.get("model"),
        "review_status": provenance.get("evidence_review", {}).get("status", "Unreviewed draft; no factual approval implied."),
    }}


def extract_section(section, narrative, evidence, provenance=None):
    schema_for(section)
    if section == "about":
        return _about(evidence, provenance)
    result = {key: copy.deepcopy(narrative[key]) for key in OUTPUT_KEYS[section]
              if key != "visualization_analysis"}
    if "visualization_analysis" in OUTPUT_KEYS[section]:
        ids = set(expected_figures(section, evidence))
        result["visualization_analysis"] = [
            {"figure_id": item["figure_id"], "explanation": item["explanation"]}
            for item in narrative["visualization_analysis"] if item["figure_id"] in ids
        ]
    validate_section(section, result, evidence)
    return result


def _same_ids(actual, expected, label):
    if len(actual) != len(expected) or set(actual) != set(expected):
        raise ValueError(f"{label} must cover exactly the supplied identities, once each.")


def validate_section(section, result, evidence):
    normalized = schema_for(section).model_validate(result).model_dump()
    if "visualization_analysis" in normalized:
        _same_ids([a["figure_id"] for a in normalized["visualization_analysis"]],
                  expected_figures(section, evidence), "Chart notes")
    if section == "players":
        main = {p["player_id"] for p in evidence["key_players"]}
        supplement = {p["player_id"]: p for p in evidence.get("scouting_supplement", {}).get("players", [])}
        _same_ids([p["player_id"] for p in normalized["key_players"]], main, "Key-player notes")
        _same_ids([p["player_id"] for p in normalized["other_threats"]], set(supplement) - main, "Other threats")
        for player in normalized["other_threats"]:
            source = supplement[player["player_id"]]
            if player["name"] != source["name"] or str(player["number"]) != str(source["number"]):
                raise ValueError("Other-threat name or shirt number differs from supplied evidence.")
    if section == "awareness":
        refs = valid_references(evidence)
        for item in normalized["awareness"]:
            if not set(item["evidence_refs"]) <= refs:
                raise ValueError("Awareness instruction refers to unavailable evidence.")
    return normalized


def _methodology():
    base = ROOT / "vendor" / "nutmeg"
    references = ["docs/accuracy-guardrail.md", "docs/metric-misuse.md",
                  "skills/analyse/SKILL.md", "skills/compute/SKILL.md"]
    manifest_path = base / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    blocks = []
    for rel in references:
        path = base / rel
        if not path.is_file():
            raise FileNotFoundError(f"Missing bundled Nutmeg methodology: {rel}")
        content = path.read_bytes()
        if manifest and rel in manifest.get("files", {}):
            if hashlib.sha256(content).hexdigest() != manifest["files"][rel]:
                raise ValueError(f"Bundled Nutmeg reference failed checksum: {rel}")
        # Agent tool permissions are not instructions for a text-only model.
        text = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", content.decode("utf-8"), count=1, flags=re.DOTALL)
        blocks.append(f"Reference: {rel}\n{text}")
    return ("Nutmeg references below are methodology, not evidence about this player. "
            "This model call has no tools: do not run commands, dispatch agents, ask setup questions, "
            "or pretend to verify live provider documentation. Preserve the supplied definitions and cohort.\n\n"
            + "\n\n".join(blocks))


def _chart_parts(section, evidence, charts_dir):
    ids = expected_figures(section, evidence)
    if not ids:
        return [], []
    charts_dir = Path(charts_dir)
    manifest = json.loads((charts_dir / "chart_manifest.json").read_text())
    selected = [item for item in manifest if item["figure_id"] in ids]
    _same_ids([item["figure_id"] for item in selected], ids, "Rendered section charts")
    parts, records = [], []
    for item in selected:
        path = charts_dir / f"figure-{item['chart_index']}.png"
        content = path.read_bytes()
        records.append({**item, "image": path.name, "sha256": hashlib.sha256(content).hexdigest()})
        parts.extend([{"text": json.dumps(item, ensure_ascii=False)},
                      {"image": {"format": "png", "source": {"bytes": content}}}])
    return parts, records


def generate_section(section, evidence, charts_dir, output_dir, prior_analysis=None, dry_run=False):
    """Persist an auditable request, then optionally generate an unreviewed draft.

    Dry-run validates prompts, schemas and chart files without creating a client.
    It returns a dry-run descriptor; real generation returns the section result.
    """
    schema = schema_for(section)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pack = get_section_input(section, evidence, prior_analysis)
    folder = ROOT / "sections" / SECTION_FOLDERS[section]
    shared = (ROOT / "prompts" / "shared.md").read_text()
    system = shared + "\n\n" + (folder / "prompt.md").read_text() + "\n\n" + _methodology()
    settings = configuration(ROOT)
    image_parts, charts = _chart_parts(section, evidence, charts_dir)
    user_text = json.dumps(pack, ensure_ascii=False, allow_nan=False)
    request = {"section": section, "settings": settings, "system": system,
               "user": pack, "charts": charts, "draft_only": True}
    for name, data in [("section_input.json", pack), ("output.schema.json", schema.model_json_schema()),
                       ("request.json", request)]:
        (output_dir / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False))
    if section == "about":
        result = _about(evidence)
        (output_dir / "model_output.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    if dry_run:
        return {"dry_run": True, "section": section, "request_path": str(output_dir / "request.json")}
    result, metadata = generate_structured(system, [{"text": user_text}, *image_parts], schema, settings)
    # Keep the returned draft even when identity checks reject it; never promote it.
    (output_dir / "raw_model_response.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    validate_section(section, result, evidence)
    (output_dir / "model_output.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    metadata.update({"section": section, "status": "draft, requires factual review",
                     "generated_at": datetime.now(timezone.utc).isoformat()})
    (output_dir / "generation.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    return result
