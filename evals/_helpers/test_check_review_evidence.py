"""Exercise contrastive failures, immutable scope and separated evidence claims."""
import copy
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("gate", Path(__file__).with_name("check-review-evidence.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class EvidenceGateTest(unittest.TestCase):
    """Use an inert temporary Git tree and validator without model/API calls."""

    def setUp(self):
        """Bind a predictable validator to a tree without creating a commit."""
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "validator.py").write_text('import sys\nif len(sys.argv) > 1:\n    sys.exit(2)\nif sys.stdin.read() != "valid":\n    sys.exit("invalid input")\n')
        subprocess.run(["git", "-C", str(self.root), "add", "validator.py"], check=True)
        tree = gate.git(self.root, "write-tree")
        self.manifest = {
            "tree": tree, "scope": ["validator.py"],
            "rules": [{"id": "input", "source": "validator.py", "dimensions": ["outcomes"], "mutation": "change valid to invalid input", "command": ["python3", "validator.py"], "accept": "valid", "reject": "invalid", "rejection": "^invalid input\\n$"}],
            "not-applicable": {d: "This fixture has no such branch" for d in gate.DIMENSIONS - {"outcomes"}},
            "claims": {d: {"status": "unverified", "evidence": "No runtime evidence supplied"} for d in gate.CLAIMS},
            "independent-review": {"status": "unavailable", "evidence": "No independent reviewer in this fixture"},
        }

    def test_valid_keeps_other_claims_unverified(self):
        """Contrastive success must not promote unrelated evidence claims."""
        result = gate.check(self.manifest, self.root)
        self.assertEqual(result["contrastive-checks"], "passed")
        self.assertTrue(all(v["status"] == "unverified" for v in result["claims"].values()))
        self.assertEqual(result["independent-review"]["status"], "unavailable")

    def test_bad_evidence_and_probe_mutations(self):
        """Reject omitted dimensions, wrong outcomes, crashes and stale review IDs."""
        mutations = []
        for field in ("tree", "scope", "rules", "claims", "independent-review", "not-applicable"):
            m = copy.deepcopy(self.manifest); m.pop(field); mutations.append(m)
        for field, value in (("accept", "invalid"), ("reject", "valid"), ("reject", ""), ("rejection", "different diagnostic"), ("command", ["python3", "absent.py"]), ("mutation", ""), ("dimensions", ["unknown"])):
            m = copy.deepcopy(self.manifest); m["rules"][0][field] = value
            if field == "reject" and value == "":
                m["rules"][0]["command"] += ["--invalid-python-flag"]
            mutations.append(m)
        m = copy.deepcopy(self.manifest); m["not-applicable"].pop("defaults"); mutations.append(m)
        m = copy.deepcopy(self.manifest); m["not-applicable"]["outcomes"] = "duplicated"; mutations.append(m)
        m = copy.deepcopy(self.manifest); m["rules"] *= 2; mutations.append(m)
        m = copy.deepcopy(self.manifest); m["claims"]["execution"]["evidence"] = ""; mutations.append(m)
        m = copy.deepcopy(self.manifest); m["independent-review"] = {"status": "completed", "reviewer": "fixture", "tree": "0" * 40, "evidence": "wrong tree"}; mutations.append(m)
        for m in mutations:
            with self.subTest(manifest=m), self.assertRaises(ValueError):
                gate.check(m, self.root)

    def test_completed_review_and_claim_domains(self):
        """Accept matching review identity and reject invented verification statuses."""
        m = copy.deepcopy(self.manifest)
        m["independent-review"] = {"status": "completed", "reviewer": "separate fixture reviewer", "tree": m["tree"], "evidence": "read-only fixture review"}
        self.assertEqual(gate.check(m, self.root)["independent-review"]["status"], "completed")
        for name in gate.CLAIMS:
            bad = copy.deepcopy(m)
            bad["claims"][name]["status"] = "passed"
            with self.assertRaises(ValueError):
                gate.check(bad, self.root)

    def test_stale_scope(self):
        """Reject working files that changed after the immutable tree was recorded."""
        (self.root / "validator.py").write_text("changed")
        with self.assertRaisesRegex(ValueError, "differs from tree"):
            gate.check(self.manifest, self.root)


if __name__ == "__main__":
    unittest.main()
