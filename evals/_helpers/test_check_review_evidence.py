"""Exercise contrastive failures, immutable scope and separated evidence claims."""
import copy
import importlib.util
from pathlib import Path
import subprocess
import shlex
import sys
import tempfile
import unittest
from unittest import mock

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
        """Reject omitted dimensions, malformed probe metadata and stale review IDs."""
        mutations = []
        for field in ("tree", "scope", "rules", "claims", "independent-review", "not-applicable"):
            m = copy.deepcopy(self.manifest); m.pop(field); mutations.append(m)
        for field, value in (("reject", ""), ("rejection", "different diagnostic"), ("command", ["python3", "absent.py"]), ("mutation", ""), ("dimensions", ["unknown"])):
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

    def bind_validator(self, source):
        """Install and bind an inert alternate validator in this temporary tree."""
        (self.root / "validator.py").write_text(source)
        subprocess.run(["git", "-C", str(self.root), "add", "validator.py"], check=True)
        self.manifest["tree"] = gate.git(self.root, "write-tree")

    def test_conforming_input_is_rejected(self):
        """Keep inputs distinct and reach the positive outcome guard."""
        self.manifest["rules"][0]["accept"] = "another invalid input"
        with self.assertRaisesRegex(ValueError, "^conforming example rejected: input$"):
            gate.check(self.manifest, self.root)

    def test_counterexample_is_accepted(self):
        """Use two distinct accepted inputs and reach the negative outcome guard."""
        self.bind_validator('import sys\nif sys.stdin.read() not in ("valid", "also valid"):\n    sys.exit("invalid input")\n')
        self.manifest["rules"][0]["reject"] = "also valid"
        with self.assertRaisesRegex(ValueError, "^counterexample did not produce its expected rejection: input$"):
            gate.check(self.manifest, self.root)

    def test_identical_inputs_do_not_run_probes(self):
        """Keep distinct-input validation independently covered before execution."""
        self.manifest["rules"][0]["reject"] = "valid"
        with mock.patch.object(gate.subprocess, "run", wraps=subprocess.run) as probe:
            with self.assertRaisesRegex(ValueError, "^distinct accept and reject inputs required$"):
                gate.check(self.manifest, self.root)
            self.assertFalse(any(call.args[0][0] == sys.executable for call in probe.call_args_list))

    def test_positive_only_crash(self):
        """Apply traceback detection to the conforming branch as well."""
        self.bind_validator('import sys\nif sys.stdin.read() == "valid":\n    raise ValueError("invalid input")\nsys.exit("invalid input")\n')
        with self.assertRaisesRegex(ValueError, "^conforming example emitted a Python traceback: input$"):
            gate.check(self.manifest, self.root)

    def test_negative_only_crash_matching_diagnostic(self):
        """A traceback matching the configured diagnostic must not count as rejection."""
        self.bind_validator('import sys\nif sys.stdin.read() != "valid":\n    raise ValueError("invalid input")\n')
        self.manifest["rules"][0]["rejection"] = "invalid input"
        with self.assertRaisesRegex(ValueError, "^counterexample emitted a Python traceback: input$"):
            gate.check(self.manifest, self.root)

    def test_traceback_headers_in_both_streams(self):
        """Cover normal and grouped traceback headers, including a zero exit code."""
        headers = ["Traceback (most recent call last):", "  + Exception Group Traceback (most recent call last):"]
        for stream in ("stdout", "stderr"):
            for header in headers:
                args = {"stdout": "", "stderr": ""}
                args[stream] = header + "\ninvalid input"
                self.assertTrue(gate.has_traceback(subprocess.CompletedProcess([], 0, **args)))
        self.assertFalse(gate.has_traceback(subprocess.CompletedProcess([], 1, "", "invalid input\n")))

    def test_diff_drivers_cannot_hide_pre_or_post_edits(self):
        """Exercise real normalizing textconv and silent external diff in both phases."""
        for driver in ("textconv", "external"):
            for phase in ("pre", "post"):
                with self.subTest(driver=driver, phase=phase):
                    # Keep source runnable; only the rejected probe mutates it.
                    source = 'import sys\nvalue = sys.stdin.read()\nif value != "valid":\n'
                    if phase == "post":
                        source += '    with open(__file__, "a") as target:\n        target.write("# probe edit\\n")\n'
                    source += '    sys.exit("invalid input")\n'
                    self.bind_validator(source)
                    helper = self.root / "driver.py"
                    helper.write_text('print("normalized")\n' if driver == "textconv" else '')
                    command = shlex.quote(sys.executable) + " " + shlex.quote(str(helper))
                    if driver == "textconv":
                        (self.root / ".gitattributes").write_text("validator.py diff=normalize\n")
                        gate.git(self.root, "config", "diff.normalize.textconv", command)
                    else:
                        (self.root / ".gitattributes").write_text("validator.py -diff\n")
                        gate.git(self.root, "config", "diff.external", command)
                    if phase == "pre":
                        with (self.root / "validator.py").open("a") as target:
                            target.write("# pre edit\n")
                    diagnostic = "working scope differs from tree" if phase == "pre" else "probe changed scoped files"
                    with self.assertRaisesRegex(ValueError, diagnostic):
                        gate.check(self.manifest, self.root)
                    # Establish that the ordinary, configured comparison conceals the edit.
                    self.assertEqual(gate.git(self.root, "diff", self.manifest["tree"], "--", "validator.py"), "")

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

    def test_clean_filter_and_mode_cannot_hide_changes(self):
        """Sweep normalization and ignored executable modes beyond diff drivers."""
        original = (self.root / "validator.py").read_bytes()
        helper = self.root / "clean.py"
        helper.write_text("import sys\nsys.stdout.buffer.write(" + repr(original) + ")\n")
        (self.root / ".gitattributes").write_text("validator.py filter=normalize\n")
        gate.git(self.root, "config", "filter.normalize.clean", shlex.quote(sys.executable) + " " + shlex.quote(str(helper)))
        with (self.root / "validator.py").open("a") as file:
            file.write("# hidden by clean filter\n")
        self.assertEqual(gate.git(self.root, "diff", "--no-ext-diff", "--no-textconv", self.manifest["tree"], "--", "validator.py"), "")
        with self.assertRaisesRegex(ValueError, "working scope differs from tree"):
            gate.check(self.manifest, self.root)
        (self.root / "validator.py").write_bytes(original)
        gate.git(self.root, "config", "core.fileMode", "false")
        (self.root / "validator.py").chmod(0o755)
        self.assertEqual(gate.git(self.root, "diff", "--no-ext-diff", "--no-textconv", self.manifest["tree"], "--", "validator.py"), "")
        with self.assertRaisesRegex(ValueError, "working scope differs from tree"):
            gate.check(self.manifest, self.root)

    def test_normalization_cannot_hide_post_probe_changes(self):
        """Verify raw bytes and executable modes after an otherwise valid rejection."""
        for mechanism in ("clean", "mode"):
            with self.subTest(mechanism=mechanism):
                (self.root / ".gitattributes").write_text("")
                (self.root / "validator.py").chmod(0o644)
                source = 'import sys, os\nif sys.stdin.read() != "valid":\n'
                if mechanism == "clean":
                    source += '    with open(__file__, "a") as file:\n        file.write("# hidden edit\\n")\n'
                else:
                    source += '    os.chmod(__file__, 0o755)\n'
                source += '    sys.exit("invalid input")\n'
                self.bind_validator(source)
                gate.git(self.root, "config", "core.fileMode", "false")
                if mechanism == "clean":
                    helper = self.root / "clean.py"
                    helper.write_text("import sys\nsys.stdout.buffer.write(" + repr(source.encode()) + ")\n")
                    (self.root / ".gitattributes").write_text("validator.py filter=normalize\n")
                    gate.git(self.root, "config", "filter.normalize.clean", shlex.quote(sys.executable) + " " + shlex.quote(str(helper)))
                with self.assertRaisesRegex(ValueError, "^probe changed scoped files$"):
                    gate.check(self.manifest, self.root)
                self.assertEqual(gate.git(self.root, "diff", "--no-ext-diff", "--no-textconv", self.manifest["tree"], "--", "validator.py"), "")

    def test_replacements_cannot_hide_pre_or_post_changes(self):
        """Reject substituted trees and blobs, including normalization-hidden blobs."""
        for kind in ("tree", "blob"):
            for phase in ("pre", "post"):
                with self.subTest(kind=kind, phase=phase):
                    (self.root / ".gitattributes").write_text("")
                    source = 'import sys, subprocess\nif sys.stdin.read() != "valid":\n'
                    if phase == "post":
                        source += '    with open(__file__, "a") as file:\n        file.write("# replaced probe edit\\n")\n'
                        if kind == "tree":
                            source += '    subprocess.run(["git", "add", "validator.py"], check=True)\n    replacement = subprocess.check_output(["git", "write-tree"], text=True).strip()\n'
                        else:
                            source += '    replacement = subprocess.check_output(["git", "hash-object", "-w", "--no-filters", "validator.py"], text=True).strip()\n'
                        source += '    subprocess.run(["git", "replace", sys.argv[1], replacement], check=True)\n'
                    source += '    sys.exit("invalid input")\n'
                    self.bind_validator(source)
                    original = self.manifest["tree"] if kind == "tree" else gate.git(self.root, "rev-parse", self.manifest["tree"] + ":validator.py")
                    self.manifest["rules"][0]["command"] = ["python3", "validator.py", original]
                    if kind == "blob":
                        helper = self.root / "clean.py"
                        helper.write_text("import sys\nsys.stdout.buffer.write(" + repr(source.encode()) + ")\n")
                        (self.root / ".gitattributes").write_text("validator.py filter=normalize\n")
                        gate.git(self.root, "config", "filter.normalize.clean", shlex.quote(sys.executable) + " " + shlex.quote(str(helper)))
                    if phase == "pre":
                        with (self.root / "validator.py").open("a") as file:
                            file.write("# replaced pre edit\n")
                        if kind == "tree":
                            gate.git(self.root, "add", "validator.py")
                            replacement = gate.git(self.root, "write-tree")
                        else:
                            replacement = gate.git(self.root, "hash-object", "-w", "--no-filters", "validator.py")
                        gate.git(self.root, "replace", original, replacement)
                    try:
                        diagnostic = "working scope differs from tree" if phase == "pre" else "probe changed scoped files"
                        with self.assertRaisesRegex(ValueError, "^" + diagnostic + "$"):
                            gate.check(self.manifest, self.root)
                        # Ordinary object lookup shows the substituted identity/data.
                        if kind == "tree":
                            shown = subprocess.check_output(["git", "-C", str(self.root), "ls-tree", "-z", original, "--", "validator.py"])
                            real = subprocess.check_output(["git", "--no-replace-objects", "-C", str(self.root), "ls-tree", "-z", original, "--", "validator.py"])
                            self.assertNotEqual(shown, real)
                        else:
                            shown = subprocess.check_output(["git", "-C", str(self.root), "cat-file", "blob", original])
                            self.assertEqual(shown, (self.root / "validator.py").read_bytes())
                            self.assertNotEqual(shown, source.encode())
                            self.assertEqual(gate.git(self.root, "diff", "--no-ext-diff", "--no-textconv", self.manifest["tree"], "--", "validator.py"), "")
                    finally:
                        gate.git(self.root, "replace", "-d", original)

    def test_replacements_preserve_valid_unchanged_scope(self):
        """Replacements alone must not reject genuine original scoped contents."""
        original_tree = self.manifest["tree"]
        original_blob = gate.git(self.root, "rev-parse", original_tree + ":validator.py")
        source = (self.root / "validator.py").read_text()
        self.bind_validator(source + "# replacement-only content\n")
        replacement_tree = self.manifest["tree"]
        replacement_blob = gate.git(self.root, "rev-parse", replacement_tree + ":validator.py")
        (self.root / "validator.py").write_text(source)
        self.manifest["tree"] = original_tree
        gate.git(self.root, "replace", original_tree, replacement_tree)
        gate.git(self.root, "replace", original_blob, replacement_blob)
        result = gate.check(self.manifest, self.root)
        self.assertEqual(result["tree"], original_tree)
        self.assertEqual(result["contrastive-checks"], "passed")

    def test_stale_scope(self):
        """Reject working files that changed after the immutable tree was recorded."""
        (self.root / "validator.py").write_text("changed")
        with self.assertRaisesRegex(ValueError, "differs from tree"):
            gate.check(self.manifest, self.root)


if __name__ == "__main__":
    unittest.main()
