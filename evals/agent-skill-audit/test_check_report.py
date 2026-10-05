"""Mutation tests for the default-roster report contract."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


CHECKER = Path(__file__).with_name("check-report.py")
SPEC = importlib.util.spec_from_file_location("agent_skill_audit_report", CHECKER)
assert SPEC is not None and SPEC.loader is not None
REPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORT)


def valid_report() -> str:
    """Build one conforming default-set report for isolated mutations."""
    ratings = "\n".join(f"| {name} | 4 | None. |" for name in REPORT.RATINGS)
    compatibility = "\n".join(
        f"| {name} | Suitable with limitations | risk | adaptation |" for name in REPORT.MODELS
    )
    return (
        "# Agent/Skill Readiness Audit\n\nAudit: example\n\n## Audit Scope\n"
        "- Artifact type: Agent Skill\n- Mode: package\n- Status: completed\n"
        "- Target models: default set\n- Target runtimes: Not supplied\n"
        "- Files included:\n  - skill.md\n- Files excluded:\n  - none — out of scope\n"
        "- Limitations: Static validation only.\n\n## Readiness Ratings\n"
        "| Area | Rating | Main risk |\n|---|---:|---|\n" + ratings
        + "\n\n## Material Findings\n\nNone.\n\n## Target-Model Compatibility\n"
        "| Model | Verdict | Main risk | Required adaptation |\n|---|---|---|---|\n" + compatibility
        + "\n\n## Priority Changes\n\nNone.\n\nVerdict: Ready with limitations\n"
    )


def canonical_finding(identifier: str = "ASR-001") -> str:
    """Build one complete finding block with a selectable identifier."""
    return (
        f"### {identifier} — Example finding\n\nSeverity: LOW\n"
        "Area: Model and runtime portability\nLocations:\n- example.md\n"
        "Evidence:\n> example\nRisk: A concrete failure.\nCorrection: Fix the condition."
    )


def finding_report(findings: str) -> str:
    """Replace the empty findings branch with supplied finding text."""
    return valid_report().replace("## Material Findings\n\nNone.", "## Material Findings\n\n" + findings)


class ReportContractTests(unittest.TestCase):
    """Check one valid report and single-rule-breaking mutations."""

    def test_valid_default_report(self) -> None:
        """Accept a conforming report with every default model exactly once."""
        REPORT.validate(valid_report())

    def test_accepts_numbered_material_finding(self) -> None:
        """Accept the canonical nested finding heading within the report."""
        REPORT.validate(finding_report(canonical_finding()))

    def test_rejects_incomplete_second_finding(self) -> None:
        """Reject a later finding that borrows fields from the first block."""
        text = finding_report(canonical_finding() + "\n\n### ASR-002 — Missing fields")
        with self.assertRaisesRegex(REPORT.ValidationError, "canonical severity"):
            REPORT.validate(text)

    def test_rejects_duplicate_finding_id(self) -> None:
        """Reject finding IDs that do not increment within the report."""
        text = finding_report(canonical_finding() + "\n\n" + canonical_finding())
        with self.assertRaisesRegex(REPORT.ValidationError, "unique and sequential"):
            REPORT.validate(text)

    def test_rejects_invalid_severity_suffix(self) -> None:
        """Reject severity values that only begin with a valid enum."""
        text = finding_report(canonical_finding().replace("Severity: LOW", "Severity: LOWgarbage"))
        with self.assertRaisesRegex(REPORT.ValidationError, "canonical severity"):
            REPORT.validate(text)

    def test_rejects_missing_location(self) -> None:
        """Reject findings whose Locations field has no location item."""
        text = finding_report(canonical_finding().replace("Locations:\n- example.md\n", "Locations:\n"))
        with self.assertRaisesRegex(REPORT.ValidationError, "at least one location"):
            REPORT.validate(text)

    def test_rejects_missing_evidence_quote(self) -> None:
        """Reject findings whose Evidence field has no quoted source."""
        text = finding_report(canonical_finding().replace("Evidence:\n> example\n", "Evidence:\n"))
        with self.assertRaisesRegex(REPORT.ValidationError, "evidence quote"):
            REPORT.validate(text)

    def test_rejects_blocked_status_for_usable_input(self) -> None:
        """Reject blocked status for the task's complete supplied artifact."""
        text = valid_report().replace("- Status: completed", "- Status: blocked")
        with self.assertRaisesRegex(REPORT.ValidationError, "completed or partial"):
            REPORT.validate(text)

    def test_rejects_omitted_rating(self) -> None:
        """Reject a report that omits one required rating row."""
        text = valid_report().replace("| Operational completeness | 4 | None. |\n", "")
        with self.assertRaisesRegex(REPORT.ValidationError, "five rows"):
            REPORT.validate(text)

    def test_rejects_missing_scope_field(self) -> None:
        """Reject a report missing a required audit-scope field."""
        text = valid_report().replace("- Artifact type: Agent Skill\n", "")
        with self.assertRaisesRegex(REPORT.ValidationError, "Artifact type"):
            REPORT.validate(text)

    def test_rejects_invalid_scope_enum(self) -> None:
        """Reject an artifact type outside the canonical domain."""
        text = valid_report().replace("- Artifact type: Agent Skill", "- Artifact type: Skill")
        with self.assertRaisesRegex(REPORT.ValidationError, "artifact type"):
            REPORT.validate(text)

    def test_rejects_empty_scope_values(self) -> None:
        """Reject empty target, runtime, and limitation values independently."""
        for field, error in (("Target models", "Target models"), ("Target runtimes", "Target runtimes"), ("Limitations", "Limitations")):
            with self.subTest(field=field):
                text = valid_report().replace(f"- {field}: " + ("default set" if field == "Target models" else "Not supplied" if field == "Target runtimes" else "Static validation only."), f"- {field}:")
                with self.assertRaisesRegex(REPORT.ValidationError, error):
                    REPORT.validate(text)

    def test_rejects_empty_findings(self) -> None:
        """Reject an empty material-findings section."""
        text = valid_report().replace("## Material Findings\n\nNone.", "## Material Findings\n\n")
        with self.assertRaisesRegex(REPORT.ValidationError, "findings"):
            REPORT.validate(text)

    def test_rejects_empty_priority_changes(self) -> None:
        """Reject an empty priority-changes section."""
        text = valid_report().replace("## Priority Changes\n\nNone.", "## Priority Changes\n\n")
        with self.assertRaisesRegex(REPORT.ValidationError, "priority changes"):
            REPORT.validate(text)

    def test_accepts_wrapped_priority_item(self) -> None:
        """Accept an indented continuation line in a numbered priority item."""
        text = valid_report().replace("## Priority Changes\n\nNone.", "## Priority Changes\n\n1. Replace fixed delegation\n   with independent workstreams.")
        REPORT.validate(text)

    def test_rejects_duplicate_verdict(self) -> None:
        """Reject an additional verdict line before the terminal verdict."""
        text = valid_report().replace("## Priority Changes\n\nNone.", "## Priority Changes\n\nVerdict: Ready")
        with self.assertRaisesRegex(REPORT.ValidationError, "exactly one Verdict"):
            REPORT.validate(text)

    def test_rejects_reordered_models(self) -> None:
        """Reject a table whose model rows violate canonical roster order."""
        text = valid_report().replace(
            "| GPT-6 Luna | Suitable with limitations | risk | adaptation |\n| GPT-6 Sol |",
            "| GPT-6 Sol | Suitable with limitations | risk | adaptation |\n| GPT-6 Luna |",
            1,
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "reordered"):
            REPORT.validate(text)

    def test_rejects_duplicate_model(self) -> None:
        """Reject a table that repeats one model name."""
        text = valid_report().replace("| GPT-6 Sol |", "| GPT-6 Luna |", 1)
        with self.assertRaisesRegex(REPORT.ValidationError, "duplicated"):
            REPORT.validate(text)

    def test_rejects_invalid_enum(self) -> None:
        """Reject a target-model verdict outside the allowed enum."""
        text = valid_report().replace("| GPT-6 Luna | Suitable with limitations |", "| GPT-6 Luna | Excellent |", 1)
        with self.assertRaisesRegex(REPORT.ValidationError, "invalid columns, verdict"):
            REPORT.validate(text)

    def test_rejects_profile_crossover(self) -> None:
        """Reject a profile name substituted for a distinct roster entry."""
        text = valid_report().replace("| GPT-6.1 Sol |", "| GPT-6 Astra |", 1)
        with self.assertRaisesRegex(REPORT.ValidationError, "unexpected"):
            REPORT.validate(text)

    def test_rejects_trailing_prose(self) -> None:
        """Reject prose appended after the final readiness verdict."""
        with self.assertRaisesRegex(REPORT.ValidationError, "final content line"):
            REPORT.validate(valid_report() + "Extra commentary.\n")

    def test_accepts_trailing_blank_lines(self) -> None:
        """Accept blank lines after the final report line."""
        REPORT.validate(valid_report() + "\n\n")


if __name__ == "__main__":
    unittest.main()
