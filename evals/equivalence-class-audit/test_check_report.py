import contextlib
import importlib.util
import io
import json
import pathlib
import re
import sys
import unittest
from unittest import mock


MODULE_PATH = pathlib.Path(__file__).with_name("check-report.py")
SPEC = importlib.util.spec_from_file_location("check_report", MODULE_PATH)
CHECK_REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_REPORT)


HEADERS = {
    "positive-edge-001": ("timeoutSeconds breaks health checks", "config/healthcheck.yml and docs"),
    "positive-edge-002": (
        "DELETE /teams/{teamId} checks organization membership",
        "src/routes/team.routes.ts, src/controllers/team.controller.ts, and tests/team.controller.spec.ts",
    ),
    "positive-edge-004": (
        "maxItems zero breaks pagination", "src/pagination.ts and tests/pagination.test.ts"
    ),
    "positive-edge-005": ("maxRetries accepts zero", "config/retry.yml and docs/operations.md"),
    "positive-edge-007": (
        "minItems zero breaks pagination",
        "src/pagination.ts, src/batch-pagination.ts, tests/pagination.test.ts, and docs/api.md",
    ),
    "positive-edge-008": (
        "maxRetries accepts zero", "config/retry.yml, docs/api.md, and docs/operations.md"
    ),
    "positive-edge-009": ("maxRetries accepts zero", "config/retry.yml and docs/api.md"),
    "positive-edge-010": (
        "minItems accepts zero", "src/pagination.ts, tests/pagination.test.ts, and docs/api.md"
    ),
    "positive-trigger-001": (
        "INC-17: maxRetries accepts zero",
        "config/retry.yml, src/retry_policy.py, tests/test_retry_policy.py, and docs/operations.md",
    ),
    "positive-trigger-002": (
        "can_export is missing for Projects export",
        "routes/projects.yml, controllers/project_export.go, controllers/project_archive.go, "
        "controllers/project_report.go, policies/project_permissions.rego, "
        "tests/project_permissions_test.go, and project exports",
    ),
}


def report_sections(fix=None, deferred=None, out_of_scope=None, blockers=None, implications=None,
                    omitted=None):
    result = {
        "Defects to fix now": fix or ["None"],
        "Deferred follow-ups": deferred or ["None"],
        "Out-of-scope candidates discovered": out_of_scope or ["None"],
        "Blocking questions": blockers or ["None"],
        "Test/doc implications": implications or ["None"],
    }
    if omitted is not None:
        result["Omitted axes (quick mode only)"] = omitted
    return result


def complete_report(profile, overrides=None, sections=None, depth="standard"):
    finding, scope = HEADERS[profile]
    overrides = overrides or {}
    rows = []
    axes = overrides if depth == "quick" else CHECK_REPORT.AXES
    for axis in axes:
        values = overrides.get(axis, (f"{axis} candidate", "absent", "n/a", "tests/example.md"))
        entries = [values] if isinstance(values, tuple) else values
        for candidate, presence, disposition, evidence in entries:
            rows.append(f"| {axis} | {candidate} | {presence} | {disposition} | {evidence} |")
    sections = sections or report_sections()
    headings = list(CHECK_REPORT.SECTIONS)
    if depth == "quick":
        headings.append("Omitted axes (quick mode only)")
    section_text = "\n".join(
        f"### {name}\n" + "\n".join(f"- {bullet}" for bullet in sections[name])
        for name in headings
    )
    return (
        "## Equivalence-Class Audit Report\n"
        f"Triggering finding: {finding}\n"
        f"Locked audit scope: {scope}\n"
        f"Output depth: {depth}\n"
        "| Axis | Candidate | Presence | Disposition | Evidence |\n"
        "|---|---|---|---|---|\n"
        + "\n".join(rows)
        + "\n"
        + section_text
    )


def reduced_report(profile, quick=False):
    if profile == "positive-edge-003":
        finding = (
            "Security review found a missing tenant ownership check: DELETE /teams/{teamId} "
            "checks organization membership only."
        )
        scope = "missing"
        blocker = "Provide the Locked audit scope."
    elif profile == "positive-edge-011":
        finding = "missing"
        scope = "missing"
        blocker = "Provide the Triggering finding."
    else:
        finding = "missing"
        scope = "src/pagination.ts and tests/pagination.test.ts"
        blocker = "Provide the Triggering finding."
    sections = report_sections(
        blockers=[blocker],
        omitted=["Required input is missing, so no axes were enumerated."] if quick else None,
    )
    headings = list(CHECK_REPORT.SECTIONS)
    if quick:
        headings.append("Omitted axes (quick mode only)")
    return (
        "## Equivalence-Class Audit Report\n"
        f"Triggering finding: {finding}\n"
        f"Locked audit scope: {scope}\n"
        f"Output depth: {'quick' if quick else 'standard'}\n"
        + "\n".join(
            f"### {name}\n" + "\n".join(f"- {bullet}" for bullet in sections[name])
            for name in headings
        )
    )


def profile_report(profile):
    if profile == "positive-edge-003":
        return reduced_report(profile)
    if profile == "positive-edge-006":
        return reduced_report(profile, quick=True)
    if profile == "positive-edge-011":
        return reduced_report(profile)
    if profile == "positive-edge-001":
        overrides = {
            "Opposite Bound": ("timeoutSeconds bound", "present", "fix-now", "config/healthcheck.yml"),
            "Documentation/Spec Prose Twin": ("docs health guidance", "present", "fix-now", "docs/health.md"),
        }
        for axis in (
            "Sibling Parameter/Field", "Inverse Operation", "Permission/Authorization Class",
            "Resource Cleanup", "Async/Sync or Mode Twin", "Cache/Projection/Source-of-Truth Twin",
        ):
            overrides[axis] = ("no candidate", "n/a — no candidates in scope", "n/a", "no candidates in locked scope")
        return complete_report(profile, overrides, report_sections(
            fix=["Fix timeoutSeconds bound and docs health guidance."],
            implications=["Update docs health guidance."],
        ))
    if profile == "positive-edge-002":
        blocked = "DELETE /teams/{teamId} tenant ownership check"
        test = "tenant mismatch test"
        return complete_report(profile, {
            "Permission/Authorization Class": (blocked, "blocked — clarification needed", "blocked", "src/routes/team.routes.ts"),
            "Mirror Call Site/Use Site": ("GET tenantGuard", "absent", "n/a", "src/routes/team.routes.ts"),
            "Test Mirror": (test, "present", "fix-now", "tests/team.controller.spec.ts"),
        }, report_sections(
            fix=[f"Add {test}."],
            out_of_scope=[
                "tenantGuard candidate; provenance: src/routes/team.routes.ts",
                "policy candidate; provenance: policies/team.rego",
            ],
            blockers=[f"Clarify {blocked}: tenantGuard tenant ownership policy spec?"],
            implications=[f"Add {test}."],
        ))
    if profile == "positive-edge-004":
        candidates = {
            "Opposite Bound": ("maxItems zero bound", "present", "fix-now", "src/pagination.ts"),
            "Test Mirror": ("maxItems zero test", "present", "fix-now", "tests/pagination.test.ts"),
            "Empty/Sentinel Equivalence": ("maxItems zero sentinel", "present", "fix-now", "src/pagination.ts"),
        }
        return complete_report(profile, candidates, report_sections(
            fix=["Fix maxItems zero bound, maxItems zero test, and maxItems zero sentinel."],
            implications=["Add maxItems zero test."],
            omitted=["Other axes omitted because they are not material to the locked scope."],
        ), depth="quick")
    if profile == "positive-edge-005":
        docs = "docs/operations.md documentation defect"
        return complete_report(profile, {
            "Opposite Bound": ("maxRetries zero bound", "present", "fix-now", "config/retry.yml"),
            "Documentation/Spec Prose Twin": (docs, "present", "blocked", "docs/operations.md"),
        }, report_sections(
            fix=["Fix maxRetries zero bound."],
            blockers=[f"Provide owner and reason for {docs}."],
            implications=[f"Update {docs} after clarification."],
        ))
    if profile == "positive-edge-007":
        overrides = {
            "Opposite Bound": ("minItems zero bound", "present", "fix-now", "src/pagination.ts"),
            "Sibling Parameter/Field": ("maxItems sibling", "absent", "n/a", "src/pagination.ts"),
            "Mirror Call Site/Use Site": [
                ("sync validator", "present", "fix-now", "src/pagination.ts"),
                ("async validator", "present", "fix-now", "src/batch-pagination.ts"),
            ],
            "Async/Sync or Mode Twin": ("async validator mode", "present", "fix-now", "src/batch-pagination.ts"),
            "Test Mirror": [
                ("zero boundary test", "present", "fix-now", "tests/pagination.test.ts"),
                ("async validator test", "present", "fix-now", "tests/pagination.test.ts"),
            ],
            "Documentation/Spec Prose Twin": ("zero docs defect", "present", "fix-now", "docs/api.md"),
        }
        names = [entry[0] for value in overrides.values() for entry in ([value] if isinstance(value, tuple) else value) if entry[2] == "fix-now"]
        return complete_report(profile, overrides, report_sections(
            fix=["Fix " + ", ".join(names) + "."],
            implications=["Update zero boundary test, async validator test, and zero docs defect."],
        ), depth="exhaustive")
    if profile == "positive-edge-008":
        api = "docs/api.md documentation defect"
        operations = "docs/operations.md documentation defect"
        return complete_report(profile, {
            "Opposite Bound": ("maxRetries zero bound", "present", "fix-now", "config/retry.yml"),
            "Documentation/Spec Prose Twin": [
                (api, "present", "blocked", "docs/api.md"),
                (operations, "present", "blocked", "docs/operations.md"),
            ],
        }, report_sections(
            fix=["Fix maxRetries zero bound."],
            blockers=[f"Provide reason for {api}.", f"Provide owner for {operations}."],
            implications=[f"Track {api} and {operations}."],
        ))
    if profile == "positive-edge-009":
        docs = "docs/api.md documentation defect"
        return complete_report(profile, {
            "Opposite Bound": ("maxRetries zero bound", "present", "fix-now", "config/retry.yml"),
            "Documentation/Spec Prose Twin": (docs, "present", "defer-with-owner", "docs/api.md"),
        }, report_sections(
            fix=["Fix maxRetries zero bound."],
            deferred=[
                f"Do not fix this now; defer {docs}; owner: Platform Docs; "
                "reason: documentation is owned outside this change"
            ],
            implications=[f"Track {docs}."],
        ))
    if profile == "positive-edge-010":
        return complete_report(profile)
    if profile == "positive-trigger-001":
        overrides = {
            "Opposite Bound": ("maxRetries upper bound", "present", "fix-now", "config/retry.yml"),
            "Sibling Parameter/Field": ("retryDelaySeconds bound", "present", "fix-now", "config/retry.yml"),
            "Empty/Sentinel Equivalence": ("null retry value", "present", "fix-now", "src/retry_policy.py"),
            "Test Mirror": [
                ("upper bound test", "present", "fix-now", "tests/test_retry_policy.py"),
                ("retryDelaySeconds test", "present", "fix-now", "tests/test_retry_policy.py"),
                ("null retry test", "present", "fix-now", "tests/test_retry_policy.py"),
            ],
            "Documentation/Spec Prose Twin": ("docs/operations.md retry prose", "present", "fix-now", "docs/operations.md"),
        }
        names = [entry[0] for value in overrides.values() for entry in ([value] if isinstance(value, tuple) else value)]
        return complete_report(profile, overrides, report_sections(
            fix=["Fix " + ", ".join(names) + "."],
            implications=["Update upper bound test, retryDelaySeconds test, null retry test, and docs/operations.md retry prose."],
        ))
    exports = "project export permission"
    archive = "project archive permission"
    export_test = "export denied test"
    archive_test = "archive denied test"
    return complete_report(profile, {
        "Permission/Authorization Class": [
            (exports, "present", "fix-now", "policies/project_permissions.rego can_export"),
            (archive, "present", "fix-now", "controllers/project_archive.go"),
            ("project report permission", "absent", "n/a", "policies/project_permissions.rego can_view_report"),
        ],
        "Observability Twin": ("denied audit event", "present", "fix-now", "controllers/project_export.go"),
        "Test Mirror": [
            (export_test, "present", "fix-now", "tests/project_permissions_test.go"),
            (archive_test, "present", "fix-now", "tests/project_permissions_test.go"),
        ],
        "Documentation/Spec Prose Twin": ("archive docs defect", "present", "fix-now", "docs/project_exports.md"),
    }, report_sections(
        fix=[f"Fix {exports}, {archive}, denied audit event, {export_test}, {archive_test}, and archive docs defect."],
        implications=[f"Add {export_test}, {archive_test}, and update archive docs defect."],
    ))


BEHAVIOR_MUTATIONS = {
    "positive-edge-001": (
        "timeoutSeconds bound | present | fix-now",
        "timeoutSeconds bound | absent | n/a",
    ),
    "positive-edge-002": (
        "blocked — clarification needed | blocked",
        "absent | n/a",
    ),
    "positive-edge-003": ("Provide the Locked audit scope.", "Provide the Triggering finding."),
    "positive-edge-004": (
        "maxItems zero sentinel | present | fix-now",
        "maxItems zero sentinel | absent | n/a",
    ),
    "positive-edge-005": (
        "docs/operations.md documentation defect | present | blocked",
        "docs/operations.md documentation defect | absent | n/a",
    ),
    "positive-edge-006": (
        "Required input is missing, so no axes were enumerated.",
        "Audit postponed.",
    ),
    "positive-edge-007": (
        "| Mirror Call Site/Use Site | async validator |",
        "| Mirror Call Site/Use Site | worker validator |",
    ),
    "positive-edge-008": (
        "docs/operations.md documentation defect | present | blocked",
        "docs/other.md documentation defect | present | blocked",
    ),
    "positive-edge-009": ("owner: Platform Docs", "owner: Platform Writers"),
    "positive-edge-010": (
        "Opposite Bound candidate | absent | n/a",
        "Opposite Bound candidate | present | fix-now",
    ),
    "positive-edge-011": ("Provide the Triggering finding.", "Provide the Locked audit scope."),
    "positive-trigger-001": ("null retry test | present | fix-now", "sentinel test | present | fix-now"),
    "positive-trigger-002": (
        "policies/project_permissions.rego can_export",
        "policies/project_permissions.rego permission",
    ),
}


def behavior_invalid_report(profile):
    report = profile_report(profile)
    old, new = BEHAVIOR_MUTATIONS[profile]
    if old not in report:
        raise AssertionError(f"missing behavior mutation anchor for {profile}: {old}")
    return report.replace(old, new, 1)


def run_main(report, profile):
    envelope = io.StringIO(json.dumps({"output": report}))
    with mock.patch.object(sys, "argv", ["check-report.py", profile]):
        with mock.patch.object(sys, "stdin", envelope):
            CHECK_REPORT.main()


class SummaryAssignmentsTests(unittest.TestCase):
    def test_fix_now_candidates_may_share_one_bullet(self):
        assignments = CHECK_REPORT.summary_assignments(
            ["docs/api.md", "docs/operations.md"],
            ["Fix docs/api.md and docs/operations.md together."],
            "Defects to fix now",
        )

        self.assertEqual({0: 0, 1: 0}, assignments)

    def test_blocked_candidates_require_separate_bullets(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.summary_assignments(
                    ["docs/api.md", "docs/operations.md"],
                    ["Who owns docs/api.md and docs/operations.md?"],
                    "Blocking questions",
                    one_to_one=True,
                )

    def test_combined_blocker_bullets_cannot_fake_one_to_one_matching(self):
        bullets = [
            "Who owns docs/api.md and docs/operations.md?",
            "Clarify docs/api.md and docs/operations.md ownership.",
        ]
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.summary_assignments(
                    ["docs/api.md", "docs/operations.md"],
                    bullets,
                    "Blocking questions",
                    one_to_one=True,
                )

    def test_overlapping_candidate_names_allow_separate_blockers(self):
        assignments = CHECK_REPORT.summary_assignments(
            ["docs/api.md", "docs/api.md migration note"],
            [
                "Who owns docs/api.md?",
                "Clarify the owner of docs/api.md migration note.",
            ],
            "Blocking questions",
            one_to_one=True,
        )

        self.assertEqual({0: 0, 1: 1}, assignments)

    def test_identical_candidate_names_allow_counted_separate_blockers(self):
        assignments = CHECK_REPORT.summary_assignments(
            ["shared config", "shared config"],
            ["Who owns shared config?", "Clarify the policy for shared config."],
            "Blocking questions",
            one_to_one=True,
        )

        self.assertEqual({0: 0, 1: 1}, assignments)

    def test_identical_candidate_names_still_require_matching_bullet_count(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.summary_assignments(
                    ["shared config", "shared config"],
                    ["Who owns shared config?"],
                    "Blocking questions",
                    one_to_one=True,
                )


class MetadataTests(unittest.TestCase):
    def test_rejects_embedded_negative_owner_phrases(self):
        for value in (
            "Platform Docs (not the owner)",
            "Platform Docs; owner is unknown",
            "Platform Docs, no owner supplied",
            "Platform Docs, owner not known",
            "documentation ownership is unknown",
            "owner cannot be determined",
        ):
            with self.subTest(value=value):
                self.assertTrue(CHECK_REPORT.non_populated_metadata(value, "owner"))

    def test_rejects_embedded_negative_reason_phrases(self):
        for value in (
            "public API reference has no reason supplied",
            "public API reference; reason is missing",
            "public API reference without a reason",
            "reason unspecified",
        ):
            with self.subTest(value=value):
                self.assertTrue(CHECK_REPORT.non_populated_metadata(value, "reason"))

    def test_field_aware_check_allows_valid_negative_wording(self):
        self.assertFalse(CHECK_REPORT.non_populated_metadata(
            "documentation is not the source of truth", "reason"
        ))
        self.assertFalse(CHECK_REPORT.non_populated_metadata(
            "No reason to alter runtime behavior; docs-only follow-up", "reason"
        ))

    def test_provenance_metadata_rejects_missing_forms(self):
        for value in (
            "schema source cannot be determined",
            "provenance unspecified",
            "artifact without a source",
        ):
            with self.subTest(value=value):
                self.assertTrue(CHECK_REPORT.non_populated_metadata(value, "provenance"))

    def test_positive_metadata_values_are_not_rejected(self):
        for field, value in (
            ("owner", "Platform Docs"),
            ("reason", "public API reference ownership boundary"),
            ("reason", "pending legal approval"),
            ("provenance", "docs/api.md"),
            ("provenance", "unresolved incident INC-17"),
        ):
            with self.subTest(field=field, value=value):
                self.assertFalse(CHECK_REPORT.non_populated_metadata(value, field))

    def test_field_specific_vague_values_are_rejected(self):
        for field, value in (
            ("owner", "nobody"),
            ("owner", "someone"),
            ("reason", "pending"),
            ("provenance", "somewhere"),
        ):
            with self.subTest(field=field, value=value):
                self.assertTrue(CHECK_REPORT.non_populated_metadata(value, field))

    def test_embedded_invalid_metadata_suffixes_are_rejected(self):
        for field, value in (
            ("owner", "Platform Docs (unassigned)"),
            ("reason", "public API reference (TBD)"),
            ("provenance", "docs/api.md (unknown)"),
        ):
            with self.subTest(field=field, value=value):
                self.assertTrue(CHECK_REPORT.non_populated_metadata(value, field))


class HeaderMarkerTests(unittest.TestCase):
    def test_missing_header_marker_accepts_only_complete_declarations(self):
        for value in ("missing", "Triggering finding is required.", "scope is not provided"):
            with self.subTest(value=value):
                self.assertTrue(CHECK_REPORT.missing_header_marker(value))

        for value in (
            "Triggering finding is required input: INC-17 maxRetries accepts zero",
            "security review found a missing tenant ownership check",
        ):
            with self.subTest(value=value):
                self.assertFalse(CHECK_REPORT.missing_header_marker(value))

class CheckerIntegrationTests(unittest.TestCase):
    def test_every_profile_accepts_a_valid_json_envelope(self):
        for profile in sorted(CHECK_REPORT.PROFILES):
            with self.subTest(profile=profile):
                run_main(profile_report(profile), profile)

    def test_every_profile_rejects_a_profile_specific_invalid_envelope(self):
        for profile in sorted(CHECK_REPORT.PROFILES):
            invalid = behavior_invalid_report(profile)
            with self.subTest(profile=profile):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, profile)

    def test_complete_reports_reject_embedded_invalid_metadata_suffixes(self):
        cases = (
            (
                "positive-edge-009",
                "owner: Platform Docs;",
                "owner: Platform Docs (unassigned);",
            ),
            (
                "positive-edge-009",
                "reason: documentation is owned outside this change",
                "reason: documentation is owned outside this change (TBD)",
            ),
            (
                "positive-edge-002",
                "provenance: src/routes/team.routes.ts",
                "provenance: src/routes/team.routes.ts (unknown)",
            ),
        )
        for profile, old, new in cases:
            invalid = profile_report(profile).replace(old, new, 1)
            with self.subTest(profile=profile, replacement=new):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, profile)

    def test_generic_filename_extensions_are_valid_evidence(self):
        for filename in (
            "`project_permissions.rego`", "`main.cpp`", "`lib.rs`",
            "`.env`", "`BUILD`", "`WORKSPACE`",
        ):
            report = profile_report("positive-edge-010").replace(
                "tests/example.md", filename, 1
            )
            with self.subTest(filename=filename):
                run_main(report, "positive-edge-010")

    def test_dotted_status_prose_is_not_an_artifact_citation(self):
        invalid = profile_report("positive-edge-010").replace(
            "tests/example.md", "candidate.present", 1
        )
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-010")

    def test_full_sync_and_async_words_pass_every_mode_branch(self):
        report = profile_report("positive-edge-007")
        report = report.replace("async validator", "asynchronous validator")
        report = report.replace("sync validator", "synchronous validator")
        run_main(report, "positive-edge-007")

    def test_negated_deferral_is_rejected(self):
        invalid = profile_report("positive-edge-009").replace(
            "Do not fix this now; defer", "Do not defer", 1
        )
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-009")

    def test_authorization_profile_requires_policy_spec_in_blocker(self):
        invalid = profile_report("positive-edge-002").replace("policy spec", "policy", 1)
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-002")


class ConfigurationTests(unittest.TestCase):
    def test_report_contract_metric_and_all_positive_profiles_are_registered(self):
        root = pathlib.Path(__file__).parent
        eval_text = (root / "eval.yaml").read_text(encoding="utf-8")
        metric_block = eval_text.split("metrics:", 1)[1].split("graders:", 1)[0]
        weights = [float(value) for value in re.findall(r"^\s+weight:\s*([0-9.]+)$", metric_block, re.M)]
        self.assertAlmostEqual(1.0, sum(weights))
        metric = re.search(
            r"(?ms)^  - name: report_contract\s*$.*?(?=^  - name:|\Z)", metric_block
        )
        self.assertIsNotNone(metric)
        self.assertRegex(metric.group(0), r"(?m)^    weight: 0\.20$")
        self.assertRegex(metric.group(0), r"(?m)^    threshold: 0\.9$")

        task_files = sorted((root / "tasks").glob("positive-*.yaml"))
        profile_ids = set()
        for task_file in task_files:
            text = task_file.read_text(encoding="utf-8")
            task_id = re.search(r"(?m)^id: (positive-(?:edge|trigger)-\d{3})$", text)
            self.assertIsNotNone(task_id, task_file.name)
            blocks = re.findall(r"(?ms)^  - type: program\s*$.*?(?=^  - type:|\Z)", text)
            self.assertEqual(1, len(blocks), task_file.name)
            block = blocks[0]
            self.assertRegex(block, r"(?m)^    name: report_contract\s*$")
            self.assertRegex(block, r"(?m)^      command: python3\s*$")
            self.assertIn("- evals/equivalence-class-audit/check-report.py", block)
            args = re.findall(r"(?m)^        - (positive-(?:edge|trigger)-\d{3})\s*$", block)
            self.assertEqual([task_id.group(1)], args, task_file.name)
            profile_ids.add(task_id.group(1))
        self.assertEqual(CHECK_REPORT.PROFILES, profile_ids)


if __name__ == "__main__":
    unittest.main()