"""Review binding and safe example reuse are part of the handoff contract."""
import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
import run


ROOT=Path(__file__).resolve().parents[1]


class ReviewBinding(unittest.TestCase):
    def test_changed_numbers_cannot_reuse_an_approved_example(self):
        expected={"player":{"shots":20,"xg":3.69}}
        changed=copy.deepcopy(expected);changed["player"]["xg"]=36.9
        with self.assertRaisesRegex(ValueError,"Approved example differs"):
            run.assert_subset(expected,changed)

    def test_render_rejects_an_edited_narrative_after_review(self):
        example=ROOT/"examples/luka-menalo"
        e=json.loads((example/"evidence.json").read_text())
        n=json.loads((example/"narrative.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp)
            run.save(work/"evidence.json",e)
            run.save(work/"review.json",{"reviewed":True,"evidence_sha256":run.object_digest(e),"narrative_sha256":run.object_digest(n)})
            n["verdict"]="Changed after review. "+n["verdict"]
            run.save(work/"reviewed-narrative.json",n)
            with self.assertRaisesRegex(ValueError,"Review is missing or stale"):
                run.render_work(SimpleNamespace(workspace=str(work),no_pdf=True))

    def test_incomplete_contribution_evidence_cannot_reuse_approved_text(self):
        e=json.loads((ROOT/"examples/luka-menalo/evidence.json").read_text())
        e["scouting_supplement"]["players"].pop()
        with self.assertRaisesRegex(ValueError,"Approved example differs"):
            run.verify_example(e)


if __name__=="__main__":unittest.main()
