"""Regression checks for the actual approved example and section safety contracts."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pydantic import BaseModel, Field, ValidationError

from pipeline.bedrock import configuration, generate_structured, output_schema
from pipeline.models import schema_for
from pipeline.sections import (
    SECTION_FOLDERS, extract_section, get_section_input, generate_section,
    validate_section,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "luka-menalo"


class SectionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = json.loads((EXAMPLE / "evidence.json").read_text())
        cls.narrative = json.loads((EXAMPLE / "narrative.json").read_text())
        cls.provenance = json.loads((EXAMPLE / "provenance.json").read_text())

    def test_every_approved_section_satisfies_its_contract(self):
        for section in SECTION_FOLDERS:
            with self.subTest(section=section):
                result = extract_section(section, self.narrative, self.evidence, self.provenance)
                validate_section(section, result, self.evidence)

    def test_compaction_preserves_scope_and_does_not_mutate_evidence(self):
        before = copy.deepcopy(self.evidence)
        pack = get_section_input("space", self.evidence)
        self.assertEqual(self.evidence, before)
        for mode, window in self.evidence["space"].items():
            self.assertNotIn("cells", pack["evidence"]["space"][mode])
            self.assertEqual(window["points"], pack["evidence"]["space"][mode]["points"])
            self.assertEqual(window["match_ids"], pack["evidence"]["space"][mode]["match_ids"])
        self.assertNotIn("mismatches", pack["evidence"]["ratings_audit"])
        self.assertEqual(pack["evidence"]["scouting_supplement"], self.evidence["scouting_supplement"])
        self.assertEqual(pack["language"], "English")

    def test_wrong_or_duplicate_player_is_rejected(self):
        result = extract_section("players", self.narrative, self.evidence)
        result["key_players"][0]["player_id"] = result["key_players"][1]["player_id"]
        with self.assertRaisesRegex(ValueError, "supplied identities"):
            validate_section("players", result, self.evidence)

    def test_extra_or_missing_attacking_threat_is_rejected(self):
        for mutate in [lambda r: r["other_threats"].pop(),
                       lambda r: r["other_threats"].append(copy.deepcopy(r["other_threats"][0]))]:
            result = extract_section("players", self.narrative, self.evidence)
            mutate(result)
            with self.assertRaisesRegex(ValueError, "supplied identities"):
                validate_section("players", result, self.evidence)

    def test_a_correct_id_does_not_allow_a_wrong_name(self):
        result = extract_section("players", self.narrative, self.evidence)
        result["other_threats"][0]["name"] = "Wrong opponent identity"
        with self.assertRaisesRegex(ValueError, "name or shirt number"):
            validate_section("players", result, self.evidence)

    def test_missing_chart_or_wrong_section_chart_is_rejected(self):
        result = extract_section("shape", self.narrative, self.evidence)
        result["visualization_analysis"][0]["figure_id"] = "space-season"
        with self.assertRaisesRegex(ValueError, "Chart notes"):
            validate_section("shape", result, self.evidence)

    def test_unknown_evidence_reference_is_rejected(self):
        result = extract_section("awareness", self.narrative, self.evidence)
        result["awareness"][0]["evidence_refs"] = ["events.unavailable"]
        with self.assertRaisesRegex(ValueError, "unavailable evidence"):
            validate_section("awareness", result, self.evidence)

    def test_brief_or_unknown_model_fields_are_rejected(self):
        with self.assertRaises(ValidationError):
            validate_section("style", {"how_they_play": "Good team."}, self.evidence)
        result = extract_section("verdict", self.narrative, self.evidence)
        result["invented_result"] = "A future score prediction"
        with self.assertRaises(ValidationError):
            validate_section("verdict", result, self.evidence)

    def test_dry_run_prepares_request_without_calling_model(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "prompts").mkdir()
            (root / "prompts/shared.md").write_text("Write English coaching instructions from the supplied evidence.")
            prompt = root / "sections" / SECTION_FOLDERS["style"] / "prompt.md"
            prompt.parent.mkdir(parents=True)
            prompt.write_text("Explain the recorded team style and a conditional response.")
            for relative in ["docs/accuracy-guardrail.md", "docs/metric-misuse.md",
                             "skills/analyse/SKILL.md", "skills/compute/SKILL.md"]:
                path = root / "vendor/nutmeg" / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("---\nallowed-tools: [Bash, Agent]\n---\nMissing data is not zero. Preserve recorded samples.")
            with patch("pipeline.sections.ROOT", root), patch("pipeline.sections.generate_structured") as model:
                result = generate_section("style", self.evidence, root / "no-charts-needed", root / "out", dry_run=True)
                model.assert_not_called()
            self.assertTrue(result["dry_run"])
            request = json.loads((root / "out/request.json").read_text())
            self.assertEqual(request["user"]["language"], "English")
            self.assertNotIn("allowed-tools", request["system"])
            self.assertIn("Missing data is not zero", request["system"])
            self.assertTrue((root / "out/output.schema.json").is_file())


class BedrockTransport(unittest.TestCase):
    def test_json_configuration_defaults(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {}, clear=True):
            root = Path(temporary)
            (root / "config").mkdir()
            (root / "config/report.json").write_text(json.dumps({"bedrock": {
                "model_id": "configured-haiku-model", "region": "ap-southeast-2", "max_tokens": 14000}}))
            settings = configuration(root)
            self.assertEqual(settings, {"model": "configured-haiku-model", "region": "ap-southeast-2", "max_tokens": 14000})

    def test_environment_takes_precedence_over_json_and_aws_region(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {
            "BEDROCK_MODEL_ID": "environment-haiku-model", "BEDROCK_REGION": "us-east-1",
            "AWS_REGION": "us-west-2", "BEDROCK_MAX_TOKENS": "8000"}, clear=True):
            root = Path(temporary)
            (root / "config").mkdir()
            (root / "config/report.json").write_text(json.dumps({"bedrock": {
                "model_id": "configured-haiku-model", "region": "ap-southeast-2", "max_tokens": 14000}}))
            self.assertEqual(configuration(root), {"model": "environment-haiku-model", "region": "us-east-1", "max_tokens": 8000})
            del os.environ["BEDROCK_REGION"]
            self.assertEqual(configuration(root)["region"], "us-west-2")

    def test_schema_adaptation_preserves_property_names_and_local_validation(self):
        class TrickySchema(BaseModel):
            title: str = Field(min_length=10)
            minimum: int = Field(ge=3)

        adapted = output_schema(TrickySchema)
        self.assertIn("title", adapted["properties"])
        self.assertIn("minimum", adapted["properties"])
        self.assertNotIn("minLength", adapted["properties"]["title"])
        self.assertNotIn("minimum", adapted["properties"]["minimum"])
        self.assertFalse(adapted["additionalProperties"])
        with self.assertRaises(ValidationError):
            TrickySchema.model_validate({"title": "short", "minimum": 1})

    def test_transport_uses_haiku_fields_and_parses_structured_response(self):
        text = "Protect the central route and press with teammate cover when the pass travels wide."

        class FakeClient:
            def converse(self, **kwargs):
                self.request = kwargs
                return {"stopReason": "end_turn", "usage": {"outputTokens": 12},
                        "output": {"message": {"content": [{"text": json.dumps({"verdict": text})}]}}}

        client = FakeClient()
        settings = {"model": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
                    "region": "ap-southeast-1", "max_tokens": 1000}
        result, metadata = generate_structured("English briefing", [{"text": "Evidence"}], schema_for("verdict"), settings, client)
        self.assertEqual(result["verdict"], text)
        self.assertEqual(client.request["additionalModelRequestFields"], {"thinking": {"type": "disabled"}})
        self.assertEqual(client.request["outputConfig"]["textFormat"]["type"], "json_schema")
        self.assertEqual(metadata["usage"]["outputTokens"], 12)

    def test_truncated_generation_is_not_accepted_as_a_valid_draft(self):
        class TruncatedClient:
            def converse(self, **kwargs):
                return {"stopReason": "max_tokens", "output": {"message": {"content": []}}}

        settings = {"model": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
                    "region": "ap-southeast-1", "max_tokens": 10}
        with self.assertRaisesRegex(ValueError, "did not finish"):
            generate_structured("English briefing", [{"text": "Evidence"}], schema_for("verdict"), settings, TruncatedClient())

    def test_unsupported_model_is_rejected_before_client_creation(self):
        with patch("pipeline.bedrock.create_client") as client:
            with self.assertRaisesRegex(ValueError, "Haiku 4.5"):
                generate_structured("English briefing", [], schema_for("verdict"), {"model": "different-family"})
            client.assert_not_called()


if __name__ == "__main__":
    unittest.main()
