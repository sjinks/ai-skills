import contextlib
import importlib.util
import io
import pathlib
import re
import sys
import unittest
from unittest import mock

import yaml


MODULE_PATH = pathlib.Path(__file__).with_name("check-report.py")
SPEC = importlib.util.spec_from_file_location("check_report", MODULE_PATH)
CHECK_REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_REPORT)


HEADERS = {
    "positive-edge-001": (
        "timeoutSeconds breaks health checks",
        "config/healthcheck.yml and the Health check timeout section",
    ),
    "positive-edge-002": (
        "DELETE /teams/{teamId} checks organization membership but lacks tenant ownership",
        "src/routes/team.routes.ts, src/controllers/team.controller.ts, and tests/team.controller.spec.ts",
    ),
    "positive-edge-004": (
        "maxItems zero breaks pagination", "src/pagination.ts and tests/pagination.test.ts"
    ),
    "positive-edge-005": (
        "maxRetries accepts zero",
        "config/retry.yml and the Retry Configuration section of docs/operations.md",
    ),
    "positive-edge-007": (
        "minItems zero breaks pagination",
        "src/pagination.ts, src/batch-pagination.ts, tests/pagination.test.ts, and the Pagination section of docs/api.md",
    ),
    "positive-edge-008": (
        "maxRetries accepts zero",
        "config/retry.yml, the Retry Configuration section of docs/api.md, and the Retry Operations section of docs/operations.md",
    ),
    "positive-edge-009": (
        "maxRetries accepts zero",
        "config/retry.yml and the Retry Configuration section of docs/api.md",
    ),
    "positive-edge-010": (
        "fixed minItems zero pagination defect previously crashed requests",
        "src/pagination.ts, tests/pagination.test.ts, and the Pagination section of docs/api.md",
    ),
    "positive-trigger-001": (
        "INC-17: maxRetries accepts zero",
        "config/retry.yml, src/retry_policy.py, tests/test_retry_policy.py, and the Retry Configuration section of docs/operations.md",
    ),
    "positive-trigger-002": (
        "can_export is missing for Projects export",
        "routes/projects.yml, controllers/project_export.go, controllers/project_archive.go, "
        "controllers/project_report.go, policies/project_permissions.rego, "
        "tests/project_permissions_test.go, and the Project exports API documentation section",
    ),
}
PROFILE_OUTCOMES = {
    "positive-edge-001": ("CONCERNS", "MEDIUM"),
    "positive-edge-002": ("BLOCK", "HIGH"),
    "positive-edge-004": ("CONCERNS", "MEDIUM"),
    "positive-edge-005": ("BLOCK", "MEDIUM"),
    "positive-edge-007": ("CONCERNS", "MEDIUM"),
    "positive-edge-008": ("BLOCK", "MEDIUM"),
    "positive-edge-009": ("CONCERNS", "MEDIUM"),
    "positive-edge-010": ("CLEAN", "NONE"),
    "positive-trigger-001": ("CONCERNS", "MEDIUM"),
    "positive-trigger-002": ("BLOCK", "HIGH"),
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
    verdict, severity = PROFILE_OUTCOMES[profile]
    overrides = overrides or {}
    rows = []
    axes = overrides if depth == "quick" else CHECK_REPORT.AXES
    for axis in axes:
        values = overrides.get(
            axis,
            ("-", "n/a — no candidates in scope", "n/a", "no candidates in locked scope"),
        )
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
        f"Verdict: {verdict}\n"
        f"Severity: {severity}\n"
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
        "Verdict: BLOCK\n"
        "Severity: UNASSESSED\n"
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
            "Documentation/Spec Prose Twin": (
                "docs health guidance", "present", "fix-now", "Health check timeout section"
            ),
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
            "Mirror Call Site/Use Site": (
                "GET /teams/{teamId}/members tenantGuard",
                "absent", "n/a", "src/routes/team.routes.ts",
            ),
            "Test Mirror": (test, "present", "fix-now", "tests/team.controller.spec.ts"),
        }, report_sections(
            fix=[f"Add {test}."],
            out_of_scope=[
                "tenantGuard candidate; provenance: supplied Known facts",
                "tenant ownership policy spec; provenance: supplied Known facts",
            ],
            blockers=[f"Clarify {blocked}: tenantGuard tenant ownership policy spec?"],
            implications=[f"Add {test}."],
        ))
    if profile == "positive-edge-004":
        candidates = {
            "Opposite Bound": ("maxItems zero bound", "present", "fix-now", "src/pagination.ts"),
            "Test Mirror": ("maxItems zero test", "present", "fix-now", "tests/pagination.test.ts"),
        }
        return complete_report(profile, candidates, report_sections(
            fix=["Fix maxItems zero bound and maxItems zero test."],
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
            blockers=[f"Provide owner and reason for {docs}; missing: owner, reason"],
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
            blockers=[
                f"Provide reason for {api}; missing: reason",
                f"Provide owner for {operations}; missing: owner",
            ],
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
            "Contract Symmetry": (
                "retry docs/config mismatch", "present", "fix-now", "Retry Configuration section"
            ),
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
        "Documentation/Spec Prose Twin": [
            ("export docs defect", "present", "fix-now", "Project exports API section"),
            ("archive docs defect", "present", "fix-now", "Project exports API section"),
        ],
    }, report_sections(
        fix=[f"Fix {exports}, {archive}, denied audit event, {export_test}, {archive_test}, export docs defect, and archive docs defect."],
        implications=[f"Add {export_test}, {archive_test}, and update export docs defect and archive docs defect."],
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
        "maxItems zero test | present | fix-now",
        "maxItems zero test | absent | n/a",
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
        "| Opposite Bound | - | n/a — no candidates in scope | n/a | no candidates in locked scope |",
        "| Opposite Bound | Opposite Bound candidate | present | fix-now | src/pagination.ts |",
    ),
    "positive-edge-011": ("Provide the Triggering finding.", "Provide the Locked audit scope."),
    "positive-trigger-001": ("null retry test | present | fix-now", "sentinel test | present | fix-now"),
    "positive-trigger-002": (
        "policies/project_permissions.rego can_export",
        "policies/project_permissions.rego permission",
    ),
}
BEHAVIOR_REPAIRS = {
    "positive-edge-001": (("Fix timeoutSeconds bound and docs health guidance.", "Fix docs health guidance."),),
    "positive-edge-002": (("### Blocking questions\n- Clarify DELETE", "### Blocking questions\n- None\n<!-- removed blocker -->\n- Clarify DELETE"),),
    "positive-edge-004": (("Fix maxItems zero bound and maxItems zero test.", "Fix maxItems zero bound."),),
    "positive-edge-005": (
        ("### Blocking questions\n- Provide owner and reason for docs/operations.md documentation defect; missing: owner, reason", "### Blocking questions\n- None"),
        ("### Test/doc implications\n- Update docs/operations.md documentation defect after clarification.", "### Test/doc implications\n- None"),
    ),
    "positive-edge-007": (("sync validator, async validator, async validator mode", "sync validator, worker validator, async validator mode"),),
    "positive-edge-008": (
        ("Provide owner for docs/operations.md documentation defect; missing: owner", "Provide owner for docs/other.md documentation defect; missing: owner"),
        ("Track docs/api.md documentation defect and docs/operations.md documentation defect.", "Track docs/api.md documentation defect and docs/other.md documentation defect."),
    ),
    "positive-edge-010": (("### Defects to fix now\n- None", "### Defects to fix now\n- Fix Opposite Bound candidate."),),
    "positive-trigger-001": (("null retry test", "sentinel test"),),
}
PROFILE_FAILURES = {
    "positive-edge-001": "missing required Opposite Bound row",
    "positive-edge-002": "missing required Permission/Authorization Class row",
    "positive-edge-003": "blocking question must name the missing required input",
    "positive-edge-004": "missing required Test Mirror row",
    "positive-edge-005": "documentation candidate must remain present and blocked",
    "positive-edge-006": "quick reduced report needs a local omitted-axes explanation",
    "positive-edge-007": "exhaustive report needs separate sync and async validator call sites",
    "positive-edge-008": "missing required Documentation/Spec Prose Twin row",
    "positive-edge-009": "deferred follow-up must contain the docs path and owner",
    "positive-edge-010": "clean audit may contain only absent or n/a rows",
    "positive-edge-011": "blocking question must name the missing required input",
    "positive-trigger-001": "trigger-001 requires distinct Test Mirror candidates",
    "positive-trigger-002": "export candidate needs can_export evidence",
}


def behavior_invalid_report(profile):
    report = profile_report(profile)
    old, new = BEHAVIOR_MUTATIONS[profile]
    if old not in report:
        raise AssertionError(f"missing behavior mutation anchor for {profile}: {old}")
    report = report.replace(old, new, 1)
    for repair_old, repair_new in BEHAVIOR_REPAIRS.get(profile, ()):
        if repair_old not in report:
            raise AssertionError(f"missing behavior repair anchor for {profile}: {repair_old}")
        report = report.replace(repair_old, repair_new, 1)
    if profile == "positive-edge-002":
        report = report.replace(
            "\n<!-- removed blocker -->\n- Clarify DELETE /teams/{teamId} tenant ownership check: tenantGuard tenant ownership policy spec?",
            "",
            1,
        )
    if profile == "positive-trigger-001":
        report = report.replace("null retry test", "sentinel test")
    return report


def run_main(report, profile):
    envelope = io.StringIO(report)
    with mock.patch.object(sys, "argv", ["check-report.py", profile]):
        with mock.patch.object(sys, "stdin", envelope):
            CHECK_REPORT.main()


def matrix_reduced_report(missing_finding, missing_scope, depth):
    finding = "missing" if missing_finding else "maxRetries accepts zero"
    scope = "missing" if missing_scope else "config/retry.yml"
    blocker = (
        "Provide the Triggering finding."
        if missing_finding
        else "Provide the Locked audit scope."
    )
    sections = report_sections(
        blockers=[blocker],
        omitted=["Required input is missing, so no axes were enumerated."]
        if depth == "quick" else None,
    )
    headings = list(CHECK_REPORT.SECTIONS)
    if depth == "quick":
        headings.append("Omitted axes (quick mode only)")
    return (
        "## Equivalence-Class Audit Report\n"
        f"Triggering finding: {finding}\n"
        f"Locked audit scope: {scope}\n"
        f"Output depth: {depth}\n"
        "Verdict: BLOCK\n"
        "Severity: UNASSESSED\n"
        + "\n".join(
            f"### {name}\n" + "\n".join(f"- {bullet}" for bullet in sections[name])
            for name in headings
        )
    )


class SummaryAssignmentsTests(unittest.TestCase):
    def test_candidate_boundaries_are_unicode_category_aware(self):
        self.assertTrue(CHECK_REPORT.candidate_named("док", "Fix док."))
        self.assertFalse(CHECK_REPORT.candidate_named("док", "Fix предок."))
        self.assertFalse(CHECK_REPORT.candidate_named("a", "Fix a\u0301."))

    def test_anonymous_na_sentinel_is_not_matched_as_punctuation(self):
        rows = [
            {"axis": "Opposite Bound", "candidate": "config defect",
             "presence": "present", "disposition": "fix-now"},
            {"axis": "Inverse Operation", "candidate": "-",
             "presence": "n/a — no candidates in scope", "disposition": "n/a"},
        ]
        sections = {
            "Defects to fix now": ["Fix config defect - add validation."],
            "Deferred follow-ups": ["None"],
            "Out-of-scope candidates discovered": ["None"],
            "Blocking questions": ["None"],
            "Test/doc implications": ["None"],
        }
        CHECK_REPORT.reconcile_summaries(sections, rows)

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

    def test_identical_blocked_rows_share_one_candidate_blocker(self):
        rows = [
            {"axis": "Opposite Bound", "candidate": "shared config",
             "presence": "blocked — clarification needed", "disposition": "blocked"},
            {"axis": "Contract Symmetry", "candidate": "shared config",
             "presence": "blocked — clarification needed", "disposition": "blocked"},
        ]
        sections = {
            "Defects to fix now": ["None"],
            "Deferred follow-ups": ["None"],
            "Out-of-scope candidates discovered": ["None"],
            "Blocking questions": ["Clarify shared config?"],
            "Test/doc implications": ["None"],
        }
        CHECK_REPORT.reconcile_summaries(sections, rows)

        sections["Blocking questions"] = [
            "Clarify shared config?", "Who owns shared config?",
        ]
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.reconcile_summaries(sections, rows)

    def test_summary_sections_reject_other_disposition_candidates(self):
        rows = [
            {"axis": "Opposite Bound", "candidate": "config defect",
             "presence": "present", "disposition": "fix-now"},
            {"axis": "Sibling Parameter/Field", "candidate": "docs defect",
             "presence": "present", "disposition": "defer-with-owner"},
            {"axis": "Contract Symmetry", "candidate": "policy defect",
             "presence": "blocked — clarification needed", "disposition": "blocked"},
            {"axis": "Inverse Operation", "candidate": "inactive candidate",
             "presence": "absent", "disposition": "n/a"},
        ]
        base = {
            "Defects to fix now": ["Fix config defect."],
            "Deferred follow-ups": [
                "Defer docs defect; owner: Platform Docs; reason: documentation ownership"
            ],
            "Out-of-scope candidates discovered": ["None"],
            "Blocking questions": ["Clarify policy defect?"],
            "Test/doc implications": ["None"],
        }
        mutations = (
            ("Defects to fix now", "Fix config defect and docs defect."),
            ("Defects to fix now", "Fix config defect and policy defect."),
            ("Deferred follow-ups", "Defer docs defect and config defect; owner: Platform Docs; reason: documentation ownership"),
            ("Deferred follow-ups", "Defer docs defect and policy defect; owner: Platform Docs; reason: documentation ownership"),
            ("Blocking questions", "Clarify policy defect and config defect?"),
            ("Blocking questions", "Clarify policy defect and docs defect?"),
            ("Defects to fix now", "Fix config defect and inactive candidate."),
            ("Deferred follow-ups", "Defer docs defect and inactive candidate; owner: Platform Docs; reason: documentation ownership"),
            ("Blocking questions", "Clarify policy defect and inactive candidate?"),
        )
        for section, bullet in mutations:
            sections = {name: list(values) for name, values in base.items()}
            sections[section] = [bullet]
            error = io.StringIO()
            with self.subTest(section=section, bullet=bullet):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        CHECK_REPORT.reconcile_summaries(sections, rows)
                self.assertIn(f"{section} must not name", error.getvalue())

    def test_identical_candidate_label_cannot_use_multiple_dispositions(self):
        rows = [
            {"axis": "Opposite Bound", "candidate": "shared candidate",
             "presence": "present", "disposition": "fix-now"},
            {"axis": "Contract Symmetry", "candidate": "shared candidate",
             "presence": "blocked — clarification needed", "disposition": "blocked"},
        ]
        sections = {
            "Defects to fix now": ["Fix shared candidate."],
            "Deferred follow-ups": ["None"],
            "Out-of-scope candidates discovered": ["None"],
            "Blocking questions": ["Clarify shared candidate?"],
            "Test/doc implications": ["None"],
        }
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.reconcile_summaries(sections, rows)
        self.assertIn("candidate label shared candidate has multiple dispositions", error.getvalue())

    def test_format_controls_cannot_hide_cross_disposition_candidates(self):
        rows = [
            {"axis": "Opposite Bound", "candidate": "config defect",
             "presence": "present", "disposition": "fix-now"},
            {"axis": "Sibling Parameter/Field", "candidate": "docs defect",
             "presence": "present", "disposition": "defer-with-owner"},
            {"axis": "Contract Symmetry", "candidate": "policy defect",
             "presence": "blocked — clarification needed", "disposition": "blocked"},
        ]
        base = {
            "Defects to fix now": ["Fix config defect."],
            "Deferred follow-ups": [
                "Defer docs defect; owner: Platform Docs; reason: documentation ownership"
            ],
            "Out-of-scope candidates discovered": ["None"],
            "Blocking questions": ["Clarify policy defect?"],
            "Test/doc implications": ["None"],
        }
        hidden = {
            "config": "config\u200b defect",
            "docs": "docs\u2066 defect",
            "policy": "policy\u202e defect",
        }
        mutations = (
            ("Defects to fix now", f"Fix config defect and {hidden['docs']}."),
            ("Defects to fix now", f"Fix config defect and {hidden['policy']}."),
            ("Deferred follow-ups", f"Defer docs defect and {hidden['config']}; owner: Platform Docs; reason: documentation ownership"),
            ("Deferred follow-ups", f"Defer docs defect and {hidden['policy']}; owner: Platform Docs; reason: documentation ownership"),
            ("Blocking questions", f"Clarify policy defect and {hidden['config']}?"),
            ("Blocking questions", f"Clarify policy defect and {hidden['docs']}?"),
        )
        for section, bullet in mutations:
            sections = {name: list(values) for name, values in base.items()}
            sections[section] = [bullet]
            with self.subTest(section=section, bullet=bullet):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        CHECK_REPORT.reconcile_summaries(sections, rows)

    def test_format_controls_cannot_distinguish_duplicate_labels(self):
        rows = [
            {"axis": "Opposite Bound", "candidate": "shared candidate",
             "presence": "present", "disposition": "fix-now"},
            {"axis": "Contract Symmetry", "candidate": "shared\u200b candidate",
             "presence": "blocked — clarification needed", "disposition": "blocked"},
        ]
        sections = {
            "Defects to fix now": ["Fix shared candidate."],
            "Deferred follow-ups": ["None"],
            "Out-of-scope candidates discovered": ["None"],
            "Blocking questions": ["Clarify shared candidate?"],
            "Test/doc implications": ["None"],
        }
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.reconcile_summaries(sections, rows)
        self.assertIn("candidate label shared candidate has multiple dispositions", error.getvalue())

    def test_nfkc_equivalent_labels_cannot_use_multiple_dispositions(self):
        rows = [
            {"axis": "Opposite Bound", "candidate": "shared candidate",
             "presence": "present", "disposition": "fix-now"},
            {"axis": "Contract Symmetry", "candidate": "ｓｈａｒｅｄ candidate",
             "presence": "blocked — clarification needed", "disposition": "blocked"},
        ]
        sections = {
            "Defects to fix now": ["Fix shared candidate."],
            "Deferred follow-ups": ["None"],
            "Out-of-scope candidates discovered": ["None"],
            "Blocking questions": ["Clarify shared candidate?"],
            "Test/doc implications": ["None"],
        }
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.reconcile_summaries(sections, rows)

    def test_format_control_removal_precedes_nfkc_composition(self):
        self.assertEqual(
            CHECK_REPORT.label_norm("café"),
            CHECK_REPORT.label_norm("cafe\u200b\u0301"),
        )

    def test_nfkc_precedes_markdown_marker_removal(self):
        self.assertEqual("candidate", CHECK_REPORT.label_norm("｀candidate｀"))
        self.assertEqual("candidate", CHECK_REPORT.label_norm("＊candidate＊"))
        self.assertEqual("candidate", CHECK_REPORT.label_norm("_candidate_"))
        self.assertEqual("candidate", CHECK_REPORT.label_norm("__candidate__"))
        self.assertEqual("candidate", CHECK_REPORT.label_norm("＿candidate＿"))
        self.assertEqual("candidate", CHECK_REPORT.label_norm("&#95;candidate&#95;"))
        self.assertEqual(
            CHECK_REPORT.label_norm("candidate ``` inner"),
            CHECK_REPORT.label_norm("````candidate ``` inner````"),
        )

    def test_same_disposition_nested_labels_need_distinct_mentions(self):
        cases = (
            ("Defects to fix now", ["Fix docs/api.md migration note."], False),
            ("Deferred follow-ups", [
                "Defer docs/api.md migration note; owner: Platform Docs; reason: migration ownership"
            ], False),
            ("Blocking questions", ["Clarify docs/api.md migration note?"], True),
        )
        candidates = ["docs/api.md", "docs/api.md migration note"]
        for section, bullets, one_to_one in cases:
            with self.subTest(section=section):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        CHECK_REPORT.summary_assignments(
                            candidates, bullets, section, one_to_one=one_to_one
                        )

    def test_nested_test_implications_need_distinct_mentions(self):
        rows = [
            {"axis": "Test Mirror", "candidate": "docs/api.md",
             "presence": "present", "disposition": "fix-now"},
            {"axis": "Test Mirror", "candidate": "docs/api.md migration note",
             "presence": "present", "disposition": "fix-now"},
        ]
        sections = {
            "Defects to fix now": [
                "Fix docs/api.md.",
                "Fix docs/api.md migration note.",
            ],
            "Deferred follow-ups": ["None"],
            "Out-of-scope candidates discovered": ["None"],
            "Blocking questions": ["None"],
            "Test/doc implications": ["Update docs/api.md migration note."],
        }
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.reconcile_summaries(sections, rows)
        self.assertIn("Test/doc implications must name docs/api.md", error.getvalue())

    def test_test_implications_cannot_synthesize_labels_across_bullets(self):
        cases = (
            (["alpha beta"], ["alpha", "beta"]),
            (
                ["docs/api.md", "docs/api.md migration note"],
                ["docs/api.md", "docs/api.md migration", "note"],
            ),
            (["cafe\u200b\u0301"], ["cafe", "accent follow-up"]),
            (["ａｌｐｈａ beta"], ["alpha", "beta"]),
        )
        for candidates, implications in cases:
            rows = [
                {"axis": "Test Mirror", "candidate": candidate,
                 "presence": "present", "disposition": "fix-now"}
                for candidate in candidates
            ]
            sections = {
                "Defects to fix now": [f"Fix {candidate}." for candidate in candidates],
                "Deferred follow-ups": ["None"],
                "Out-of-scope candidates discovered": ["None"],
                "Blocking questions": ["None"],
                "Test/doc implications": implications,
            }
            with self.subTest(candidates=candidates, implications=implications):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        CHECK_REPORT.reconcile_summaries(sections, rows)

    def test_nested_labels_with_distinct_dispositions_remain_valid(self):
        section_for = {
            "fix-now": "Defects to fix now",
            "defer-with-owner": "Deferred follow-ups",
            "blocked": "Blocking questions",
        }

        def bullet(disposition, candidate):
            if disposition == "fix-now":
                return f"Fix {candidate}."
            if disposition == "defer-with-owner":
                return f"Defer {candidate}; owner: Platform Docs; reason: migration ownership"
            return f"Clarify {candidate}?"

        dispositions = tuple(section_for)
        for short_disposition in dispositions:
            for long_disposition in dispositions:
                if short_disposition == long_disposition:
                    continue
                rows = [
                    {
                        "axis": "Opposite Bound",
                        "candidate": "docs/api.md",
                        "presence": "blocked — clarification needed"
                        if short_disposition == "blocked" else "present",
                        "disposition": short_disposition,
                    },
                    {
                        "axis": "Contract Symmetry",
                        "candidate": "docs/api.md migration note",
                        "presence": "blocked — clarification needed"
                        if long_disposition == "blocked" else "present",
                        "disposition": long_disposition,
                    },
                ]
                sections = {
                    "Defects to fix now": ["None"],
                    "Deferred follow-ups": ["None"],
                    "Out-of-scope candidates discovered": ["None"],
                    "Blocking questions": ["None"],
                    "Test/doc implications": ["None"],
                }
                sections[section_for[short_disposition]] = [
                    bullet(short_disposition, "docs/api.md")
                ]
                sections[section_for[long_disposition]] = [
                    bullet(long_disposition, "docs/api.md migration note")
                ]
                with self.subTest(
                    short_disposition=short_disposition,
                    long_disposition=long_disposition,
                ):
                    CHECK_REPORT.reconcile_summaries(sections, rows)


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
        for value in ("missing", "not provided", "not supplied", "required", "needed"):
            with self.subTest(value=value):
                self.assertTrue(CHECK_REPORT.missing_header_marker(value))

        for value in (
            "MISSING",
            "Not Provided",
            "Triggering finding is required.",
            "scope is not provided",
            "missing (no defect supplied)",
            "**missing**",
            "`missing`",
            "ｍｉｓｓｉｎｇ",
            "&#109;issing",
            "<strong>missing</strong>",
            "Triggering finding is required input: INC-17 maxRetries accepts zero",
            "security review found a missing tenant ownership check",
        ):
            with self.subTest(value=value):
                self.assertFalse(CHECK_REPORT.missing_header_marker(value))


class CheckerContractTests(unittest.TestCase):
    def test_visible_text_preserves_code_span_angle_brackets(self):
        for value in ("`handler<Foo>`", "`handler<Bar>`", "`std::map<Key, Value>`"):
            with self.subTest(value=value):
                self.assertEqual(value, CHECK_REPORT.visible_text(value))

        self.assertEqual(
            "visible content",
            CHECK_REPORT.visible_text("visible <!-- hidden --> <span>content</span>"),
        )
        self.assertEqual("<Foo>", CHECK_REPORT.visible_text("&lt;Foo&gt;"))
        for element in ("script", "style", "template"):
            with self.subTest(element=element):
                self.assertFalse(CHECK_REPORT.visible(f"<{element}>hidden</{element}>"))
                self.assertFalse(CHECK_REPORT.visible(
                    f"<{element}>outer <{element}>inner</{element}> remainder</{element}>"
                ))
                self.assertFalse(CHECK_REPORT.visible(f"<{element}>unclosed"))
                code = f"`<{element}>visible</{element}>`"
                self.assertEqual(code, CHECK_REPORT.visible_text(code))
                escaped = f"&lt;{element}&gt;visible&lt;/{element}&gt;"
                self.assertEqual(f"<{element}>visible</{element}>", CHECK_REPORT.visible_text(escaped))
        for element in ("details", "dialog"):
            with self.subTest(element=element):
                self.assertFalse(CHECK_REPORT.visible(f"<{element}>hidden</{element}>"))
                self.assertFalse(CHECK_REPORT.visible(
                    f"<{element}>outer <{element}>inner</{element}> remainder</{element}>"
                ))
                self.assertFalse(CHECK_REPORT.visible(f"<{element}>unclosed"))
                code = f"`<{element}>visible</{element}>`"
                self.assertEqual(code, CHECK_REPORT.visible_text(code))
                escaped = f"&lt;{element}&gt;visible&lt;/{element}&gt;"
                self.assertEqual(f"<{element}>visible</{element}>", CHECK_REPORT.visible_text(escaped))
            self.assertFalse(CHECK_REPORT.visible("visible <!-- unclosed"))
            self.assertFalse(CHECK_REPORT.visible("<span hidden>hidden</span>"))
            self.assertFalse(CHECK_REPORT.visible("owner: <span hidden"))
            self.assertFalse(CHECK_REPORT.visible('<span aria-hidden="true">hidden</span>'))
            self.assertFalse(CHECK_REPORT.visible('<span style="display:none">hidden</span>'))
            self.assertFalse(CHECK_REPORT.visible('<div style="visibility:hidden">hidden</div>'))
            self.assertFalse(CHECK_REPORT.visible('<span style=display:none>hidden</span>'))
            self.assertFalse(CHECK_REPORT.visible('<div style=visibility:hidden>hidden</div>'))
            self.assertFalse(CHECK_REPORT.visible('<span style="display:/**/none">hidden</span>'))
            self.assertFalse(CHECK_REPORT.visible('owner: <span style="display:none"'))
            code = "````handler<`Foo`> and ```nested``` code````"
            self.assertEqual(code, CHECK_REPORT.visible_text(code))
        self.assertFalse(CHECK_REPORT.visible("<!-- hidden --><span></span>"))

    def test_bracketed_metadata_placeholders_are_rejected(self):
        cases = (
            ("owner", "Platform Docs [TBD]"),
            ("reason", "documentation ownership [unknown]"),
            ("provenance", "docs/api.md {unavailable}"),
            ("owner", "Platform Docs ［owner］"),
            ("reason", "documentation ownership ｛reason｝"),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                self.assertTrue(CHECK_REPORT.non_populated_metadata(value, field))
        self.assertFalse(CHECK_REPORT.non_populated_metadata("Platform Docs [API team]", "owner"))

    def test_missing_metadata_combination_uses_canonical_order(self):
        self.assertEqual(
            {"owner", "reason"},
            CHECK_REPORT.missing_metadata_fields("Provide metadata; missing: owner, reason"),
        )
        self.assertEqual(
            set(),
            CHECK_REPORT.missing_metadata_fields("Provide metadata; missing: reason, owner"),
        )

    def test_duplicate_row_identity_uses_label_normalization(self):
        base = profile_report("positive-edge-010")
        marker = "|---|---|---|---|---|\n"
        duplicate_rows = (
            "| Opposite Bound | Straße | absent | n/a | tests/example.md |\n"
            "| Opposite Bound | STRASSE | absent | n/a | tests/example.md |\n"
        )
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.parse_report(base.replace(marker, marker + duplicate_rows, 1))

        distinct_rows = (
            "| Opposite Bound | candidate 0 | absent | n/a | tests/example.md |\n"
            "| Opposite Bound | candidate zero | absent | n/a | tests/example.md |\n"
        )
        CHECK_REPORT.parse_report(base.replace(marker, marker + distinct_rows, 1))

    def test_mixed_latin_cyrillic_candidate_is_rejected(self):
        invalid = profile_report("positive-edge-010").replace(
            "| Opposite Bound | - | n/a — no candidates in scope | n/a | no candidates in locked scope |",
            "| Opposite Bound | shаred candidate | n/a — no candidates in scope | n/a | no candidates in locked scope |",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.parse_report(invalid)
        self.assertIn("candidate label must not mix Latin and Cyrillic letters", error.getvalue())

    def test_missing_input_blockers_require_one_verbatim_header_label(self):
        self.assertTrue(CHECK_REPORT.requests_missing_input(
            "Provide the Triggering finding.", "Triggering finding"
        ))
        self.assertTrue(CHECK_REPORT.requests_missing_input(
            "Provide the Locked audit scope.", "Locked audit scope"
        ))
        self.assertTrue(CHECK_REPORT.requests_missing_input(
            "Provide the Locked audit scope for the bug report.", "Locked audit scope"
        ))
        for value in (
            "Provide the Triggering finding and list the files.",
            "Provide no Triggering finding.",
            "Need no Locked audit scope.",
            "What defect should be used as the trigger?",
            "Provide the triggering defect.",
            "Provide the triggering finding.",
            "Provide the locked audit scope.",
            "Which finding should the audit use?",
            "Which files and modules should the audit inspect?",
            "Provide the audit scope.",
            "Which artifacts should the audit include?",
            "Which defect files should the audit inspect?",
            "Provide the triggering defect and audit scope.",
            "Provide the Triggering finding and Locked audit scope.",
            "Provide the Triggering finding; then provide the locked audit scope.",
            "Provide the Triggering finding; then provide the Locked audit scope.",
            "Provide the Unlocked audit scope.",
            "Provide the Locked audit scopeish.",
            "Provide the Triggering finding-ish.",
            "Provide the Locked audit scope.md.",
            "Provide the NotTriggering finding.",
            "Provide the Triggering findingish.",
        ):
            with self.subTest(value=value):
                self.assertFalse(CHECK_REPORT.requests_missing_input(value, "Triggering finding"))
                self.assertFalse(CHECK_REPORT.requests_missing_input(value, "Locked audit scope"))

    def test_output_depth_requires_canonical_lowercase(self):
        for depth in ("STANDARD", "Standard", "Quick", "EXHAUSTIVE"):
            invalid = profile_report("positive-edge-010").replace(
                "Output depth: standard",
                f"Output depth: {depth}",
                1,
            )
            error = io.StringIO()
            with self.subTest(depth=depth):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        CHECK_REPORT.parse_report(invalid)
                self.assertIn("Output depth must use a canonical lowercase value", error.getvalue())

    def test_verdict_severity_state_matrix(self):
        section_none = {name: ["None"] for name in CHECK_REPORT.SECTIONS}
        states = (
            (
                "reduced",
                {"_has_table": False},
                section_none,
                [],
                {("BLOCK", "UNASSESSED")},
            ),
            (
                "clean",
                {"_has_table": True},
                section_none,
                [{"presence": "absent", "disposition": "n/a"}],
                {("CLEAN", "NONE")},
            ),
            (
                "actionable",
                {"_has_table": True},
                section_none,
                [{"presence": "present", "disposition": "fix-now"}],
                {
                    ("BLOCK", "CRITICAL"), ("BLOCK", "HIGH"),
                    ("CONCERNS", "MEDIUM"), ("CONCERNS", "LOW"),
                },
            ),
            (
                "implication-only",
                {"_has_table": True},
                {**section_none, "Test/doc implications": ["Add a regression test."]},
                [{"presence": "absent", "disposition": "n/a"}],
                {
                    ("BLOCK", "CRITICAL"), ("BLOCK", "HIGH"),
                    ("CONCERNS", "MEDIUM"), ("CONCERNS", "LOW"),
                },
            ),
            (
                "blocked",
                {"_has_table": True},
                {**section_none, "Blocking questions": ["Clarify candidate?"]},
                [{"presence": "blocked — clarification needed", "disposition": "blocked"}],
                {
                    ("BLOCK", "CRITICAL"), ("BLOCK", "HIGH"),
                    ("BLOCK", "MEDIUM"), ("BLOCK", "LOW"),
                    ("BLOCK", "UNASSESSED"),
                },
            ),
        )
        for state, base_headers, sections, rows, allowed in states:
            for verdict in CHECK_REPORT.VERDICTS:
                for severity in CHECK_REPORT.SEVERITIES:
                    headers = {**base_headers, "Verdict": verdict, "Severity": severity}
                    with self.subTest(state=state, verdict=verdict, severity=severity):
                        if (verdict, severity) in allowed:
                            CHECK_REPORT.validate_report_outcome(headers, sections, rows)
                        else:
                            with contextlib.redirect_stderr(io.StringIO()):
                                with self.assertRaises(SystemExit):
                                    CHECK_REPORT.validate_report_outcome(headers, sections, rows)

class CheckerIntegrationTests(unittest.TestCase):
    def test_edge_002_header_preserves_tenant_ownership_omission(self):
        invalid = profile_report("positive-edge-002").replace(
            " but lacks tenant ownership",
            "",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-002")
        self.assertIn("Triggering finding must preserve the supplied task input", error.getvalue())

    def test_trigger_001_requires_contract_symmetry_candidate(self):
        invalid = profile_report("positive-trigger-001").replace(
            "| Contract Symmetry | retry docs/config mismatch | present | fix-now | Retry Configuration section |",
            "| Contract Symmetry | retry docs/config mismatch | absent | n/a | Retry Configuration section |",
            1,
        ).replace(
            "retry docs/config mismatch, ",
            "",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-trigger-001")
        self.assertIn("missing required Contract Symmetry row", error.getvalue())

    def test_complete_reports_reject_ambiguous_metadata_alternatives(self):
        cases = (
            (
                "positive-edge-009",
                "owner: Platform Docs;",
                "owner: Platform Docs or someone;",
            ),
            (
                "positive-edge-002",
                "provenance: supplied Known facts",
                "provenance: supplied Known facts or somewhere",
            ),
        )
        for profile, original, ambiguous in cases:
            with self.subTest(profile=profile):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        run_main(profile_report(profile).replace(original, ambiguous, 1), profile)

    def test_clean_profile_rejects_current_defect_finding(self):
        for finding in (
            "minItems zero still crashes pagination",
            "current unfixed minItems zero defect previously crashed requests",
            "current minItems zero pagination defect was previously fixed",
            "minItems zero defect was not yet fixed and previously crashed requests",
        ):
            invalid = profile_report("positive-edge-010").replace(
                "fixed minItems zero pagination defect previously crashed requests",
                finding,
                1,
            )
            error = io.StringIO()
            with self.subTest(finding=finding):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, "positive-edge-010")
                self.assertIn("clean profile triggering finding", error.getvalue())

    def test_deferred_reason_cannot_negate_deferral(self):
        for reason in ("no reason to defer", "no-reason-to-defer"):
            invalid = profile_report("positive-edge-009").replace(
                "reason: documentation is owned outside this change",
                f"reason: {reason}",
                1,
            )
            error = io.StringIO()
            with self.subTest(reason=reason):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, "positive-edge-009")
                self.assertIn("Deferred follow-ups cannot negate deferral", error.getvalue())

    def test_fix_now_summary_rejects_never_fix(self):
        for action in ("Never fix", "Never-fix"):
            invalid = profile_report("positive-edge-009").replace(
                "Fix maxRetries zero bound.",
                f"{action} maxRetries zero bound.",
                1,
            )
            error = io.StringIO()
            with self.subTest(action=action):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, "positive-edge-009")
                self.assertIn("Defects to fix now cannot contain a negated action", error.getvalue())

    def test_complete_report_rejects_standalone_blocking_question(self):
        rows = [{
            "axis": "Opposite Bound", "candidate": "checked candidate",
            "presence": "absent", "disposition": "n/a",
        }]
        sections = {
            "Defects to fix now": ["None"],
            "Deferred follow-ups": ["None"],
            "Out-of-scope candidates discovered": ["None"],
            "Blocking questions": ["Clarify checked candidate?"],
            "Test/doc implications": ["None"],
        }
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.reconcile_summaries(sections, rows)

    def test_edge_004_contains_only_supported_active_candidates(self):
        report = profile_report("positive-edge-004")
        self.assertNotIn("| Empty/Sentinel Equivalence |", report)
        run_main(report, "positive-edge-004")

    def test_trigger_002_requires_export_and_archive_documentation(self):
        invalid = profile_report("positive-trigger-002").replace(
            "| Documentation/Spec Prose Twin | export docs defect | present | fix-now | Project exports API section |",
            "| Documentation/Spec Prose Twin | export docs defect | absent | n/a | Project exports API section |",
            1,
        ).replace(
            ", export docs defect, and archive docs defect.",
            ", and archive docs defect.",
            1,
        ).replace(
            "update export docs defect and archive docs defect.",
            "update archive docs defect.",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-trigger-002")
        self.assertIn("missing required Documentation/Spec Prose Twin row", error.getvalue())

    def test_trigger_002_documentation_uses_named_section_evidence(self):
        for candidate, code_path in (
            ("export docs defect", "controllers/project_export.go"),
            ("archive docs defect", "controllers/project_archive.go"),
        ):
            invalid = profile_report("positive-trigger-002").replace(
                f"| Documentation/Spec Prose Twin | {candidate} | present | fix-now | Project exports API section |",
                f"| Documentation/Spec Prose Twin | {candidate} | present | fix-now | {code_path} |",
                1,
            )
            error = io.StringIO()
            with self.subTest(candidate=candidate):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, "positive-trigger-002")
                self.assertIn("documentation row must cite the Project exports API section", error.getvalue())

    def test_known_impact_blocked_profiles_reject_unassessed(self):
        for profile in ("positive-edge-005", "positive-edge-008"):
            invalid = profile_report(profile).replace("Severity: MEDIUM", "Severity: UNASSESSED", 1)
            error = io.StringIO()
            with self.subTest(profile=profile):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, profile)
                self.assertIn("known-impact blocked profile must use an assessed severity", error.getvalue())

    def test_task_supplied_incident_evidence_is_allowed(self):
        report = profile_report("positive-trigger-001").replace(
            "| Opposite Bound | maxRetries upper bound | present | fix-now | config/retry.yml |",
            "| Opposite Bound | maxRetries upper bound | present | fix-now | config/retry.yml and incident note INC-17 |",
            1,
        )
        run_main(report, "positive-trigger-001")

    def test_edge_007_rejects_unsupported_extra_active_candidate(self):
        invalid = profile_report("positive-edge-007").replace(
            "| Resource Cleanup | - | n/a — no candidates in scope | n/a | no candidates in locked scope |",
            "| Resource Cleanup | timer leak | present | fix-now | src/pagination.ts |",
            1,
        ).replace(
            "Fix minItems zero bound, sync validator",
            "Fix minItems zero bound, timer leak, sync validator",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-007")
        self.assertIn("report contains an unsupported active candidate set", error.getvalue())

    def test_blocked_row_requires_artifact_citation(self):
        for evidence in (
            "no candidates in locked scope",
            "triggering finding",
            "no artifact is available",
            "no artifact section",
            "no policy spec is available",
            "policy spec not supplied",
            "policy spec not provided",
            "Health section required",
            "Health section needed",
        ):
            invalid = profile_report("positive-edge-005").replace(
                "| Documentation/Spec Prose Twin | docs/operations.md documentation defect | present | blocked | docs/operations.md |",
                f"| Documentation/Spec Prose Twin | docs/operations.md documentation defect | present | blocked | {evidence} |",
                1,
            )
            error = io.StringIO()
            with self.subTest(evidence=evidence):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, "positive-edge-005")
                self.assertIn("blocked row evidence must cite an artifact", error.getvalue())

    def test_nonblocked_row_rejects_triggering_finding_as_evidence(self):
        invalid = profile_report("positive-edge-010").replace(
            "| Opposite Bound | - | n/a — no candidates in scope | n/a | no candidates in locked scope |",
            "| Opposite Bound | checked candidate | absent | n/a | triggering finding |",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.parse_report(invalid)
        self.assertIn("evidence must cite an artifact", error.getvalue())

    def test_table_evidence_paths_stay_inside_profile_scope(self):
        for evidence in (
            "secrets/production.env",
            "`production.env`",
            "tenant ownership policy spec",
        ):
            invalid = profile_report("positive-edge-009").replace(
                "| Opposite Bound | maxRetries zero bound | present | fix-now | config/retry.yml |",
                f"| Opposite Bound | maxRetries zero bound | present | fix-now | {evidence} |",
                1,
            )
            error = io.StringIO()
            with self.subTest(evidence=evidence):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, "positive-edge-009")
                self.assertIn("table evidence citation must stay within the locked scope", error.getvalue())

    def test_edge_007_requires_maxitems_absent_state(self):
        invalid = profile_report("positive-edge-007").replace(
            "| Sibling Parameter/Field | maxItems sibling | absent | n/a | src/pagination.ts |",
            "| Sibling Parameter/Field | maxItems sibling | present | fix-now | src/pagination.ts |",
            1,
        ).replace(
            "Fix minItems zero bound, sync validator",
            "Fix minItems zero bound, maxItems sibling, sync validator",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-007")
        self.assertIn("missing required Sibling Parameter/Field row", error.getvalue())

    def test_default_rows_are_anonymous_na_with_scope_reason(self):
        report = profile_report("positive-edge-010")
        self.assertNotIn("tests/example.md", report)
        self.assertIn(
            "| Opposite Bound | - | n/a — no candidates in scope | n/a | no candidates in locked scope |",
            report,
        )

    def test_all_supplied_scope_profiles_reject_added_artifact(self):
        for profile in sorted(CHECK_REPORT.PROFILE_SCOPE_ARTIFACTS):
            report = profile_report(profile)
            lines = report.splitlines()
            lines = [
                line + ", secrets/production.env"
                if line.startswith("Locked audit scope:")
                else line
                for line in lines
            ]
            error = io.StringIO()
            with self.subTest(profile=profile):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main("\n".join(lines), profile)
                self.assertIn("Locked audit scope", error.getvalue())

    def test_missing_input_and_depth_matrix(self):
        missing_cases = (
            (True, False, "Triggering finding"),
            (False, True, "Locked audit scope"),
            (True, True, "Triggering finding"),
        )
        for missing_finding, missing_scope, expected_blocker in missing_cases:
            for depth in ("quick", "standard", "exhaustive"):
                with self.subTest(
                    missing_finding=missing_finding,
                    missing_scope=missing_scope,
                    depth=depth,
                ):
                    report = matrix_reduced_report(missing_finding, missing_scope, depth)
                    headers, sections, rows = CHECK_REPORT.parse_report(report)
                    self.assertEqual(depth, headers["Output depth"])
                    expected_missing = {
                        header for header, missing in (
                            ("Triggering finding", missing_finding),
                            ("Locked audit scope", missing_scope),
                        ) if missing
                    }
                    CHECK_REPORT.reduced(
                        headers,
                        sections,
                        rows,
                        expected_blocker,
                        quick=depth == "quick",
                        expected_missing=expected_missing,
                    )

                    for header in expected_missing:
                        invalid = report.replace(f"{header}: missing", f"{header}: fabricated value", 1)
                        invalid_headers, invalid_sections, invalid_rows = CHECK_REPORT.parse_report(invalid)
                        with contextlib.redirect_stderr(io.StringIO()):
                            with self.assertRaises(SystemExit):
                                CHECK_REPORT.reduced(
                                    invalid_headers, invalid_sections, invalid_rows,
                                    expected_blocker, quick=depth == "quick",
                                    expected_missing=expected_missing,
                                )

                    for header in ({"Triggering finding", "Locked audit scope"} - expected_missing):
                        prefix = f"{header}: "
                        invalid_lines = report.splitlines()
                        invalid_lines = [
                            f"{header}: missing" if line.startswith(prefix) else line
                            for line in invalid_lines
                        ]
                        invalid_headers, invalid_sections, invalid_rows = CHECK_REPORT.parse_report(
                            "\n".join(invalid_lines)
                        )
                        with contextlib.redirect_stderr(io.StringIO()):
                            with self.assertRaises(SystemExit):
                                CHECK_REPORT.reduced(
                                    invalid_headers, invalid_sections, invalid_rows,
                                    expected_blocker, quick=depth == "quick",
                                    expected_missing=expected_missing,
                                )

                    if depth == "quick":
                        invalid = report.replace(
                            "Required input is missing, so no axes were enumerated.",
                            "Audit postponed.",
                            1,
                        )
                        invalid_headers, invalid_sections, invalid_rows = CHECK_REPORT.parse_report(invalid)
                        with contextlib.redirect_stderr(io.StringIO()):
                            with self.assertRaises(SystemExit):
                                CHECK_REPORT.reduced(
                                    invalid_headers, invalid_sections, invalid_rows,
                                    expected_blocker, quick=True,
                                    expected_missing=expected_missing,
                                )

    def test_every_profile_accepts_a_valid_raw_response(self):
        for profile in sorted(CHECK_REPORT.PROFILES):
            with self.subTest(profile=profile):
                run_main(profile_report(profile), profile)

    def test_every_profile_rejects_a_profile_specific_invalid_raw_response(self):
        for profile in sorted(CHECK_REPORT.PROFILES):
            invalid = behavior_invalid_report(profile)
            with self.subTest(profile=profile):
                error = io.StringIO()
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, profile)
                self.assertIn(PROFILE_FAILURES[profile], error.getvalue())

    def test_edge_001_rejects_documentation_scope_drift(self):
        for replacement in (
            "unrelated deployment documentation",
            "the Health check timeout section and docs/other.md",
        ):
            invalid = profile_report("positive-edge-001").replace(
                "the Health check timeout section",
                replacement,
                1,
            )
            error = io.StringIO()
            with self.subTest(replacement=replacement):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, "positive-edge-001")
                self.assertIn("Locked audit scope", error.getvalue())

    def test_edge_001_accepts_scope_preserving_paraphrase(self):
        report = profile_report("positive-edge-001").replace(
            "config/healthcheck.yml and the Health check timeout section",
            "config/healthcheck.yml and its Health check timeout documentation section",
            1,
        )
        run_main(report, "positive-edge-001")

    def test_edge_001_accepts_plus_connector(self):
        report = profile_report("positive-edge-001").replace(
            "config/healthcheck.yml and the Health check timeout section",
            "config/healthcheck.yml plus its Health check timeout documentation section",
            1,
        )
        run_main(report, "positive-edge-001")

    def test_same_file_section_drift_is_rejected(self):
        replacements = {
            "positive-edge-001": "Health check timeout",
            "positive-edge-005": "Retry Configuration",
            "positive-edge-007": "Pagination",
            "positive-edge-008": "Retry Configuration",
            "positive-edge-009": "Retry Configuration",
            "positive-edge-010": "Pagination",
            "positive-trigger-001": "Retry Configuration",
            "positive-trigger-002": "Project exports API documentation",
        }
        for profile, section in replacements.items():
            invalid = profile_report(profile).replace(section, "Unrelated", 1)
            error = io.StringIO()
            with self.subTest(profile=profile):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, profile)
                self.assertIn("Locked audit scope", error.getvalue())

    def test_incident_evidence_preserves_identifier(self):
        invalid = profile_report("positive-trigger-001").replace(
            "| Opposite Bound | maxRetries upper bound | present | fix-now | config/retry.yml |",
            "| Opposite Bound | maxRetries upper bound | present | fix-now | config/retry.yml and incident note INC-999 |",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-trigger-001")
        self.assertIn("table evidence citation must stay within the locked scope", error.getvalue())

    def test_edge_001_requires_explicit_na_reasons(self):
        for evidence in ("candidate is in scope", "config/healthcheck.yml"):
            invalid = profile_report("positive-edge-001").replace(
                "no candidates in locked scope",
                evidence,
                1,
            )
            error = io.StringIO()
            with self.subTest(evidence=evidence):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, "positive-edge-001")
                self.assertIn(
                    "n/a row evidence must include an explicit absence or inapplicability reason",
                    error.getvalue(),
                )

    def test_quick_omitted_axes_requires_an_actual_missing_declaration(self):
        for explanation in (
            "Triggering finding was supplied; no axes were enumerated.",
            "No required input is missing; no axes were enumerated.",
            "Neither required input is missing; no axes were enumerated.",
            "No required input is needed; no axes were enumerated.",
            "Neither input is required; no axes were enumerated.",
            "Input is not required; no axes were enumerated.",
            "Input is not needed; no axes were enumerated.",
        ):
            invalid = profile_report("positive-edge-006").replace(
                "Required input is missing, so no axes were enumerated.",
                explanation,
                1,
            )
            error = io.StringIO()
            with self.subTest(explanation=explanation):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, "positive-edge-006")
                self.assertIn("quick reduced report needs a local omitted-axes explanation", error.getvalue())

    def test_reduced_profiles_reject_noncanonical_blocker_aliases(self):
        cases = (
            (
                "positive-edge-003",
                "Provide the Locked audit scope.",
                "Which files and modules should the audit inspect?",
            ),
            (
                "positive-edge-006",
                "Provide the Triggering finding.",
                "What defect should be used as the trigger?",
            ),
            (
                "positive-edge-011",
                "Provide the Triggering finding.",
                "Which finding should the audit use?",
            ),
        )
        for profile, original, alias in cases:
            with self.subTest(profile=profile, alias=alias):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        run_main(profile_report(profile).replace(original, alias, 1), profile)

    def test_metadata_profiles_bind_missing_fields_and_owner_assignment(self):
        cases = (
            (
                "positive-edge-005",
                "missing: owner, reason",
                "missing: owner",
                "documentation blocker must request owner and reason",
            ),
            (
                "positive-edge-008",
                "missing: reason",
                "missing: owner",
                "docs/api.md needs a separate blocker requesting reason",
            ),
            (
                "positive-edge-009",
                "owner: Platform Docs; reason: documentation is owned outside this change",
                "owner: API Team; reason: Platform Docs requested transfer",
                "documentation deferral owner must be Platform Docs",
            ),
            (
                "positive-edge-009",
                "reason: documentation is owned outside this change",
                "reason: pending legal approval",
                "documentation deferral reason must cite ownership outside this change",
            ),
        )
        for profile, original, invalid_value, expected_error in cases:
            error = io.StringIO()
            with self.subTest(profile=profile):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(
                            profile_report(profile).replace(original, invalid_value, 1),
                            profile,
                        )
                self.assertIn(expected_error, error.getvalue())

    def test_edge_002_policy_provenance_uses_supplied_facts(self):
        cases = (
            ("tenantGuard candidate", "src/routes/team.routes.ts", "tenantguard"),
            ("tenant ownership policy spec", "policies/team.rego", "policy"),
        )
        for candidate, fabricated, label in cases:
            invalid = profile_report("positive-edge-002").replace(
                f"{candidate}; provenance: supplied Known facts",
                f"{candidate}; provenance: {fabricated}",
                1,
            )
            error = io.StringIO()
            with self.subTest(candidate=candidate):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, "positive-edge-002")
                self.assertIn(
                    f"{label} provenance must cite the supplied Known facts",
                    error.getvalue(),
                )

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
                "provenance: supplied Known facts",
                "provenance: supplied Known facts (unknown)",
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
                "| Opposite Bound | - | n/a — no candidates in scope | n/a | no candidates in locked scope |",
                f"| Opposite Bound | artifact candidate | absent | n/a | {filename} |",
                1,
            )
            with self.subTest(filename=filename):
                CHECK_REPORT.parse_report(report)

    def test_unquoted_standalone_special_basenames_are_not_evidence(self):
        for filename in ("README", "Dockerfile", "Makefile", "LICENSE"):
            invalid = profile_report("positive-edge-010").replace(
                "| Opposite Bound | - | n/a — no candidates in scope | n/a | no candidates in locked scope |",
                f"| Opposite Bound | artifact candidate | absent | n/a | {filename} |",
                1,
            )
            with self.subTest(filename=filename):
                with contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        CHECK_REPORT.parse_report(invalid)

    def test_edge_005_rejects_reversed_missing_metadata_order(self):
        invalid = profile_report("positive-edge-005").replace(
            "missing: owner, reason",
            "missing: reason, owner",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-005")
        self.assertIn("documentation blocker must request owner and reason", error.getvalue())

    def test_dotted_status_prose_is_not_an_artifact_citation(self):
        invalid = profile_report("positive-edge-010").replace(
            "| Opposite Bound | - | n/a — no candidates in scope | n/a | no candidates in locked scope |",
            "| Opposite Bound | artifact candidate | absent | n/a | candidate.present |",
            1,
        )
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                CHECK_REPORT.parse_report(invalid)

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

    def test_edge_009_rejects_an_unrelated_deferred_candidate(self):
        invalid = profile_report("positive-edge-009")
        invalid = invalid.replace(
            "| Sibling Parameter/Field | - | n/a — no candidates in scope | n/a | no candidates in locked scope |",
            "| Sibling Parameter/Field | Sibling Parameter/Field candidate | present | defer-with-owner | config/retry.yml |",
            1,
        )
        invalid = invalid.replace(
            "defer docs/api.md documentation defect; owner:",
            "defer docs/api.md documentation defect and Sibling Parameter/Field candidate; owner:",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-009")
        self.assertIn("documentation must be the only deferred candidate", error.getvalue())

    def test_edge_009_rejects_fix_now_candidate_in_deferred_bullet(self):
        invalid = profile_report("positive-edge-009").replace(
            "defer docs/api.md documentation defect; owner:",
            "defer docs/api.md documentation defect and maxRetries zero bound; owner:",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-009")
        self.assertIn(
            "Deferred follow-ups must not name maxRetries zero bound from another disposition",
            error.getvalue(),
        )

    def test_edge_009_rejects_format_control_smuggling(self):
        invalid = profile_report("positive-edge-009").replace(
            "defer docs/api.md documentation defect; owner:",
            "defer docs/api.md documentation defect and max\u200bRetries zero bound; owner:",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-009")
        self.assertIn(
            "Deferred follow-ups must not name maxRetries zero bound from another disposition",
            error.getvalue(),
        )

    def test_edge_009_rejects_na_candidate_smuggling(self):
        for candidate in (
            "Contract Symmetry candidate",
            "Contract\u200b Symmetry candidate",
        ):
            invalid = profile_report("positive-edge-009").replace(
                "| Contract Symmetry | - | n/a — no candidates in scope | n/a | no candidates in locked scope |",
                "| Contract Symmetry | Contract Symmetry candidate | n/a — no candidates in scope | n/a | no candidates in locked scope |",
                1,
            ).replace(
                "defer docs/api.md documentation defect; owner:",
                f"defer docs/api.md documentation defect and {candidate}; owner:",
                1,
            )
            error = io.StringIO()
            with self.subTest(candidate=candidate):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit):
                        run_main(invalid, "positive-edge-009")
                self.assertIn(
                    "Deferred follow-ups must not name Contract Symmetry candidate from another disposition",
                    error.getvalue(),
                )

    def test_edge_009_rejects_deferred_candidate_in_fix_now_bullet(self):
        invalid = profile_report("positive-edge-009").replace(
            "Fix maxRetries zero bound.",
            "Fix maxRetries zero bound and docs/api.md documentation defect.",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-009")
        self.assertIn(
            "Defects to fix now must not name docs/api.md documentation defect from another disposition",
            error.getvalue(),
        )

    def test_edge_009_rejects_identical_label_with_blocked_disposition(self):
        invalid = profile_report("positive-edge-009").replace(
            "| Contract Symmetry | - | n/a — no candidates in scope | n/a | no candidates in locked scope |",
            "| Contract Symmetry | docs/api.md documentation defect | blocked — clarification needed | blocked | docs/api.md |",
            1,
        ).replace(
            "### Blocking questions\n- None",
            "### Blocking questions\n- Clarify docs/api.md documentation defect?",
            1,
        )
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-009")
        self.assertIn(
            "candidate label docs/api.md documentation defect has multiple dispositions",
            error.getvalue(),
        )

    def test_authorization_profile_requires_policy_spec_in_blocker(self):
        invalid = profile_report("positive-edge-002").replace(
            "tenantGuard tenant ownership policy spec?",
            "tenantGuard tenant ownership policy?",
            1,
        )
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                run_main(invalid, "positive-edge-002")


class ConfigurationTests(unittest.TestCase):
    def test_edge_002_valid_fixture_satisfies_text_grader(self):
        root = pathlib.Path(__file__).parent
        task = yaml.safe_load((root / "tasks" / "positive-edge-2.yaml").read_text())
        config = next(
            grader["config"] for grader in task["graders"]
            if grader["type"] == "text"
        )
        report = profile_report("positive-edge-002")
        for pattern in config.get("regex_match", []):
            self.assertIsNotNone(re.search(pattern, report), pattern)
        for pattern in config.get("regex_not_match", []):
            self.assertIsNone(re.search(pattern, report), pattern)
        for token in config.get("not_contains", []):
            self.assertNotIn(token.lower(), report.lower(), token)

    def test_suppressed_yaml_fixes_remain_projected(self):
        root = pathlib.Path(__file__).parent / "tasks"
        for name in (
            "positive-edge-5.yaml",
            "positive-edge-8.yaml",
            "positive-trigger-1.yaml",
        ):
            text = (root / name).read_text(encoding="utf-8")
            not_contains = text.split("not_contains:", 1)[1]
            self.assertNotIn('- "defer-with-owner"', not_contains, name)
        edge_007 = (root / "positive-edge-7.yaml").read_text(encoding="utf-8")
        self.assertIn("`maxItems` already rejects zero", edge_007)
        trigger_001 = (root / "positive-trigger-1.yaml").read_text(encoding="utf-8")
        self.assertNotIn('- "Verdict: BLOCK"', trigger_001.split("not_contains:", 1)[1])

    def test_reduced_task_missing_markers_match_checker_vocabulary(self):
        root = pathlib.Path(__file__).parent / "tasks"
        cases = {
            "positive-edge-3.yaml": ("Locked audit scope",),
            "positive-edge-6.yaml": ("Triggering finding",),
            "positive-edge-11.yaml": ("Triggering finding", "Locked audit scope"),
        }
        for name, headers in cases.items():
            text = (root / name).read_text(encoding="utf-8")
            for header in headers:
                match = re.search(
                    rf"'(?P<pattern>\(\?im\)\^{re.escape(header)}:[^']+)'",
                    text,
                )
                self.assertIsNotNone(match, f"{name}: {header}")
                pattern = match.group("pattern")
                for marker in CHECK_REPORT.MISSING:
                    self.assertRegex(f"{header}: {marker}", pattern)
                    self.assertTrue(CHECK_REPORT.missing_header_marker(marker))
                for invalid in (
                    f"{header}: missing (clarifier)",
                    f"{header}: The {header.lower()} is missing.",
                ):
                    self.assertIsNone(re.search(pattern, invalid), (name, invalid))

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
        strict_outcomes = {
            "positive-edge-003": ("BLOCK", "UNASSESSED"),
            "positive-edge-006": ("BLOCK", "UNASSESSED"),
            "positive-edge-010": ("CLEAN", "NONE"),
            "positive-edge-011": ("BLOCK", "UNASSESSED"),
            "positive-trigger-002": ("BLOCK", "HIGH"),
        }
        actionable_profiles = {
            "positive-edge-001", "positive-edge-004", "positive-edge-007",
            "positive-edge-009", "positive-trigger-001",
        }
        blocked_profiles = {"positive-edge-002"}
        known_impact_blocked_profiles = {"positive-edge-005", "positive-edge-008"}
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
            profile = task_id.group(1)
            if profile in actionable_profiles:
                self.assertIn("^Verdict:\\s*(BLOCK|CONCERNS)\\s*$", text, task_file.name)
                self.assertIn("^Severity:\\s*(CRITICAL|HIGH|MEDIUM|LOW)\\s*$", text, task_file.name)
            elif profile in blocked_profiles:
                self.assertIn("^Verdict:\\s*BLOCK\\s*$", text, task_file.name)
                self.assertIn(
                    "^Severity:\\s*(CRITICAL|HIGH|MEDIUM|LOW|UNASSESSED)\\s*$",
                    text,
                    task_file.name,
                )
            elif profile in known_impact_blocked_profiles:
                self.assertIn("^Verdict:\\s*BLOCK\\s*$", text, task_file.name)
                self.assertIn(
                    "^Severity:\\s*(CRITICAL|HIGH|MEDIUM|LOW)\\s*$",
                    text,
                    task_file.name,
                )
            else:
                verdict, severity = strict_outcomes[profile]
                self.assertIn(f"^Verdict:\\s*{verdict}\\s*$", text, task_file.name)
                self.assertIn(f"^Severity:\\s*{severity}\\s*$", text, task_file.name)
            profile_ids.add(task_id.group(1))
        self.assertEqual(CHECK_REPORT.PROFILES, profile_ids)

        for name in ("negative-close-1.yaml", "negative-close-2.yaml", "negative-trigger-1.yaml"):
            text = (root / "tasks" / name).read_text(encoding="utf-8")
            self.assertIn('- "Verdict:"', text, name)
            self.assertIn('- "Severity:"', text, name)


if __name__ == "__main__":
    unittest.main()