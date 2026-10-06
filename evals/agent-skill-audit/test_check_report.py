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
    profile_rows = {
        "GPT-6 Luna": (
            "Long procedures obscure the short normal path and explicit defaults.",
            "Use a simple output grammar.",
        ),
        "GPT-6 Sol": (
            "The procedure misses clear outcomes and evidence.",
            "Allow adaptable tool use within side-effect boundaries.",
        ),
        "GPT-6.1 Sol": (
            "The literal broad scope needs a clear bound.",
            "Keep delegation optional only for independent workstreams.",
        ),
        "GPT-6 Astra": (
            "State a concise mission and hard boundaries.",
            "Preserve strategic freedom and pause conditions.",
        ),
    }
    compatibility = "\n".join(
        f"| {name} | Suitable with limitations | "
        f"{profile_rows.get(name, ('risk', 'adaptation'))[0]} | "
        f"{profile_rows.get(name, ('risk', 'adaptation'))[1]} |"
        for name in REPORT.MODELS
    )
    return (
        "# Agent/Skill Readiness Audit\n\nAudit: example\n\n## Audit Scope\n"
        "- Artifact type: Custom agent\n- Mode: core\n- Status: completed\n"
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
    report = valid_report().replace("## Material Findings\n\nNone.", "## Material Findings\n\n" + findings)
    return report.replace("Verdict: Ready with limitations", "Verdict: Needs revision")


def swap_model_assessments(text: str, first_model: str, second_model: str) -> str:
    """Swap risk and adaptation cells while preserving both model identities."""
    rows = text.splitlines()
    indexes = {
        model: next(index for index, line in enumerate(rows) if line.startswith(f"| {model} |"))
        for model in (first_model, second_model)
    }
    first = [cell.strip() for cell in rows[indexes[first_model]].strip("|").split("|")]
    second = [cell.strip() for cell in rows[indexes[second_model]].strip("|").split("|")]
    for destination, source in ((first_model, second), (second_model, first)):
        original = [cell.strip() for cell in rows[indexes[destination]].strip("|").split("|")]
        rows[indexes[destination]] = f"| {original[0]} | {original[1]} | {source[2]} | {source[3]} |"
    return "\n".join(rows) + "\n"


def swap_model_rows(text: str, first_model: str, second_model: str) -> str:
    """Swap complete table rows to isolate a roster-order mutation."""
    rows = text.splitlines()
    indexes = {
        model: next(index for index, line in enumerate(rows) if line.startswith(f"| {model} |"))
        for model in (first_model, second_model)
    }
    rows[indexes[first_model]], rows[indexes[second_model]] = rows[indexes[second_model]], rows[indexes[first_model]]
    return "\n".join(rows) + "\n"


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
        with self.assertRaisesRegex(REPORT.ValidationError, "finding is incomplete"):
            REPORT.validate(text)

    def test_rejects_severity_after_correction(self) -> None:
        """Require finding severity before its later fields."""
        text = finding_report(canonical_finding())
        text = text.replace("Severity: LOW\n", "", 1).replace("Correction: Fix the condition.", "Correction: Fix the condition.\nSeverity: LOW")
        with self.assertRaisesRegex(REPORT.ValidationError, "canonical severity in order"):
            REPORT.validate(text)

    def test_rejects_area_after_correction(self) -> None:
        """Require the readiness area in its canonical finding position."""
        text = finding_report(canonical_finding())
        text = text.replace("Area: Model and runtime portability\n", "", 1).replace("Correction: Fix the condition.", "Correction: Fix the condition.\nArea: Model and runtime portability")
        with self.assertRaisesRegex(REPORT.ValidationError, "readiness area in order"):
            REPORT.validate(text)

    def test_rejects_duplicate_finding_id(self) -> None:
        """Reject finding IDs that do not increment within the report."""
        text = finding_report(canonical_finding() + "\n\n" + canonical_finding())
        with self.assertRaisesRegex(REPORT.ValidationError, "unique and sequential"):
            REPORT.validate(text)

    def test_rejects_finding_content_before_first_heading(self) -> None:
        """Reject finding fields that precede every numbered finding."""
        text = finding_report(canonical_finding()).replace(
            "## Material Findings\n\n### ASR-001",
            "## Material Findings\n\nSeverity: LOW\n\n### ASR-001",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "before the first numbered finding"):
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
        with self.assertRaisesRegex(REPORT.ValidationError, "requires completed audit status"):
            REPORT.validate(text)

    def test_rejects_omitted_rating(self) -> None:
        """Reject a report that omits one required rating row."""
        text = valid_report().replace("| Operational completeness | 4 | None. |\n", "")
        with self.assertRaisesRegex(REPORT.ValidationError, "five rows"):
            REPORT.validate(text)

    def test_rejects_missing_scope_field(self) -> None:
        """Reject a report missing a required audit-scope field."""
        text = valid_report().replace("- Artifact type: Custom agent\n", "")
        with self.assertRaisesRegex(REPORT.ValidationError, "Artifact type"):
            REPORT.validate(text)

    def test_rejects_audit_marker_after_scope_heading(self) -> None:
        """Keep the Audit marker before the Audit Scope section."""
        text = valid_report().replace("Audit: example\n\n## Audit Scope", "## Audit Scope\n\nAudit: example")
        with self.assertRaisesRegex(REPORT.ValidationError, "Audit marker must follow"):
            REPORT.validate(text)

    def test_rejects_duplicate_empty_audit_marker(self) -> None:
        """Count empty Audit markers when enforcing exact marker cardinality."""
        text = valid_report().replace("Audit: example\n", "Audit:\nAudit: example\n", 1)
        with self.assertRaisesRegex(REPORT.ValidationError, "exactly one nonempty Audit marker"):
            REPORT.validate(text)

    def test_rejects_audit_marker_without_separator_space(self) -> None:
        """Reject malformed nonempty Audit lines without an uncaught lookup error."""
        text = valid_report().replace("Audit: example", "Audit:example", 1)
        with self.assertRaisesRegex(REPORT.ValidationError, "exactly one nonempty Audit marker"):
            REPORT.validate(text)

    def test_rejects_whitespace_only_audit_value(self) -> None:
        """Require non-whitespace content after the Audit marker."""
        for value in ("Audit:  ", "Audit:\t"):
            with self.subTest(value=value):
                text = valid_report().replace("Audit: example", value, 1)
                with self.assertRaisesRegex(REPORT.ValidationError, "exactly one nonempty Audit marker"):
                    REPORT.validate(text)

    def test_rejects_invalid_scope_enum(self) -> None:
        """Reject an artifact type outside the canonical domain."""
        text = valid_report().replace("- Artifact type: Custom agent", "- Artifact type: Skill")
        with self.assertRaisesRegex(REPORT.ValidationError, "artifact type"):
            REPORT.validate(text)

    def test_rejects_wrong_artifact_type_for_supplied_agent(self) -> None:
        """Keep task-specific scope aligned with its supplied custom agent."""
        text = valid_report().replace("- Artifact type: Custom agent", "- Artifact type: Agent Skill")
        with self.assertRaisesRegex(REPORT.ValidationError, "audits a Custom agent"):
            REPORT.validate(text)

    def test_rejects_package_mode_for_single_pasted_artifact(self) -> None:
        """Use core mode for the one pasted artifact in this task."""
        text = valid_report().replace("- Mode: core", "- Mode: package")
        with self.assertRaisesRegex(REPORT.ValidationError, "requires core audit mode"):
            REPORT.validate(text)

    def test_rejects_custom_target_model_scope(self) -> None:
        """Keep the task scope bound to the full default target set."""
        text = valid_report().replace("- Target models: default set", "- Target models: Claude Sonnet 5")
        with self.assertRaisesRegex(REPORT.ValidationError, "requires the default target model set"):
            REPORT.validate(text)

    def test_rejects_empty_scope_values(self) -> None:
        """Reject empty target, runtime, and limitation values independently."""
        for field, error in (("Target models", "Target models"), ("Target runtimes", "Target runtimes"), ("Limitations", "Limitations")):
            with self.subTest(field=field):
                text = valid_report().replace(f"- {field}: " + ("default set" if field == "Target models" else "Not supplied" if field == "Target runtimes" else "Static validation only."), f"- {field}:")
                with self.assertRaisesRegex(REPORT.ValidationError, error):
                    REPORT.validate(text)

    def test_rejects_unsupplied_runtime_value_other_than_exact_marker(self) -> None:
        """Bind the target-runtime field to the fixture's known input state."""
        for value in ("None.", "unknown"):
            with self.subTest(value=value):
                text = valid_report().replace("- Target runtimes: Not supplied", f"- Target runtimes: {value}")
                with self.assertRaisesRegex(REPORT.ValidationError, "no supplied target runtime"):
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
        text = text.replace("Verdict: Ready with limitations", "Verdict: Needs revision")
        REPORT.validate(text)

    def test_rejects_duplicate_verdict(self) -> None:
        """Reject an additional verdict line before the terminal verdict."""
        text = valid_report().replace("## Priority Changes\n\nNone.", "## Priority Changes\n\nVerdict: Ready")
        with self.assertRaisesRegex(REPORT.ValidationError, "exactly one Verdict"):
            REPORT.validate(text)

    def test_rejects_not_assessed_ratings_branch(self) -> None:
        """Reject the blocked-report sentinel for this readable input task."""
        text = valid_report().replace(
            "| Area | Rating | Main risk |\n|---|---:|---|\n"
            + "\n".join(f"| {name} | 4 | None. |" for name in REPORT.RATINGS),
            "Not assessed.",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "readiness ratings require header and five rows"):
            REPORT.validate(text)

    def test_rejects_rating_one_with_ready_verdict(self) -> None:
        """Require Major redesign when any area receives rating one."""
        text = valid_report().replace("| Discovery and delegation | 4 |", "| Discovery and delegation | 1 |")
        with self.assertRaisesRegex(REPORT.ValidationError, "rating 1 requires Major redesign"):
            REPORT.validate(text)

    def test_accepts_major_redesign_for_rating_one(self) -> None:
        """Accept the canonical major-redesign mapping for rating one."""
        text = valid_report()
        text = text.replace("| Discovery and delegation | 4 |", "| Discovery and delegation | 1 |")
        text = text.replace("Verdict: Ready with limitations", "Verdict: Major redesign")
        REPORT.validate(text)

    def test_accepts_needs_revision_for_rating_three(self) -> None:
        """Accept Needs revision when any area is rated three."""
        text = valid_report().replace("| Discovery and delegation | 4 |", "| Discovery and delegation | 3 |")
        text = text.replace("Verdict: Ready with limitations", "Verdict: Needs revision")
        REPORT.validate(text)

    def test_accepts_major_redesign_for_multiple_twos(self) -> None:
        """Accept numeric eligibility when the evidence says architecture is fundamentally wrong."""
        text = valid_report()
        for area in REPORT.RATINGS[:2]:
            text = text.replace(f"| {area} | 4 | None. |", f"| {area} | 2 | The architecture is fundamentally wrong because it cannot preserve conflicting evidence and dependent subagent work discards disagreement. |")
        text = text.replace("Verdict: Ready with limitations", "Verdict: Major redesign")
        REPORT.validate(text)

    def test_accepts_numeric_major_eligibility_for_two_twos(self) -> None:
        """Leave causal architecture assessment to the task's substance judge."""
        text = valid_report()
        for area in REPORT.RATINGS[:2]:
            text = text.replace(f"| {area} | 4 | None. |", f"| {area} | 2 | None. |")
        text = text.replace("Verdict: Ready with limitations", "Verdict: Major redesign")
        REPORT.validate(text)

    def test_allows_needs_revision_when_one_rating_two_mentions_architecture(self) -> None:
        """Do not infer the multiple-area redesign condition from one rating."""
        text = valid_report().replace(
            "| Discovery and delegation | 4 | None. |",
            "| Discovery and delegation | 2 | The architecture is fundamentally wrong. |",
        )
        text = text.replace("Verdict: Ready with limitations", "Verdict: Needs revision")
        REPORT.validate(text)

    def test_accepts_ready_without_limitations(self) -> None:
        """Accept Ready when all ratings are high and limitations are None."""
        text = valid_report().replace("- Limitations: Static validation only.", "- Limitations: None.")
        text = text.replace("Verdict: Ready with limitations", "Verdict: Ready")
        REPORT.validate(text)

    def test_accepts_unverified_runtime_as_a_real_limitation(self) -> None:
        """Accept unavailable runtime verification as a real limitation."""
        for limitation in (
            "Runtime compatibility has not been tested.",
            "Runtime is unsupported by this deployment.",
            "Runtime does not support image generation.",
            "Model does not support tool calls.",
            "Model limitations include no browser support.",
            "Runtime compatibility has not been tested; model limitations are none.",
            "Runtime verification has not been tested; model limitations are resolved.",
            "Evidence is not unavailable, but results are missing.",
            "No model test evidence was obtained.",
            "Runtime lacks browser support; model testing is complete.",
            "Source evidence was not obtained; runtime verification is complete.",
            "No model test evidence was obtained; runtime compatibility was verified.",
            "Runtime compatibility has not been tested; model testing is complete.",
            "Source evidence was not obtained; runtime verification is complete.",
            "No model test evidence was obtained; runtime compatibility was verified.",
            "Model limitations are resolved, but runtime lacks browser support.",
            "Runtime lacks browser support; model limitations are resolved.",
            "No model limitations remain; static validation only.",
            "Static validation only; no model limitations remain.",
            "No model limitations remain and runtime lacks browser support.",
            "Runtime lacks browser support and no model limitations remain.",
        ):
            with self.subTest(limitation=limitation):
                text = valid_report().replace("- Limitations: Static validation only.", f"- Limitations: {limitation}")
                REPORT.validate(text)

    def test_rejects_unrelated_limitation_for_ready_with_limitations(self) -> None:
        """Do not let unrelated context justify Ready with limitations."""
        text = valid_report().replace("- Limitations: Static validation only.", "- Limitations: Report submitted late.")
        with self.assertRaisesRegex(REPORT.ValidationError, "requires a model, runtime, or unavailable-evidence"):
            REPORT.validate(text)

    def test_rejects_negated_model_limitation_for_ready_with_limitations(self) -> None:
        """A model mention must identify an actual limitation, not deny one."""
        for limitation in (
            "Static validation only is no longer true; runtime and model compatibility were verified.",
            "Not static validation only; runtime and model compatibility were verified.",
            "No longer static validation only; runtime and model compatibility were verified.",
            "Static validation only was not true; runtime and model compatibility were verified.",
            "Runtime was unavailable, but verification is now complete.",
            "Model behavior was verified; no remaining limitations.",
            "No model or runtime constraints remain.",
            "Model limitations are resolved; no runtime constraints remain.",
            "No runtime constraints remain; model limitations are resolved.",
            "No model or runtime limitations apply.",
            "Runtime has no remaining limitations.",
            "Model limitations are not present.",
            "The model limitation is not applicable.",
            "Evidence is not unavailable for the model.",
            "Model behavior was verified.",
            "The model is not applicable.",
            "Model/runtime limitations: N/A.",
            "Model limitations: not applicable.",
            "Model limitation: none.",
            "Runtime limitation: not required.",
            "Model limitations are immaterial.",
            "Runtime limitations are hypothetical.",
            "Model limitations are theoretical.",
            "Model not limited; no constraints apply.",
            "Runtime has no constraints.",
            "Model has no constraints.",
            "Model does not have limitations.",
            "Runtime does not have any limitations.",
            "Runtime verification is no longer unavailable.",
            "Runtime compatibility is not unavailable.",
            "Model limitations have been resolved.",
            "The model limitation was fixed.",
            "Runtime limitations have been addressed.",
            "The runtime limitation has been removed.",
            "Runtime has no unsupported features.",
            "No unsupported model or runtime features were identified.",
            "No unsupported features remain for the model.",
            "No unsupported features were found in runtime.",
            "The model supports every required feature; no unsupported features remain.",
            "Model limitations are resolved, but runtime needs no adaptation.",
            "Model limitations are resolved; runtime needs no reconfiguration.",
        ):
            with self.subTest(limitation=limitation):
                text = valid_report().replace("- Limitations: Static validation only.", f"- Limitations: {limitation}")
                with self.assertRaisesRegex(REPORT.ValidationError, "requires a model, runtime, or unavailable-evidence"):
                    REPORT.validate(text)

    def test_task_contract_requires_finding_for_known_defect_fixture(self) -> None:
        """The expanded-roster fixture has known defects and must report one."""
        with self.assertRaisesRegex(REPORT.ValidationError, "known-defect task requires"):
            REPORT.validate(valid_report(), require_findings=True)

    def test_rejects_finding_hidden_in_code_block(self) -> None:
        """Do not count indented code as a material finding in the report."""
        finding = "\n".join("    " + line for line in canonical_finding().splitlines())
        with self.assertRaisesRegex(REPORT.ValidationError, "cannot be indented as a code block"):
            REPORT.validate(finding_report(finding), require_findings=True)

    def test_rejects_tab_indented_finding_code_block(self) -> None:
        """Reject a tab-indented code block as a required finding."""
        finding = "\n".join("\t" + line for line in canonical_finding().splitlines())
        with self.assertRaisesRegex(REPORT.ValidationError, "cannot be indented as a code block"):
            REPORT.validate(finding_report(finding), require_findings=True)

    def test_rejects_mixed_space_tab_indented_finding_code_block(self) -> None:
        """Reject a tab reached after spaces as code-block indentation."""
        finding = "\n".join("   \t" + line for line in canonical_finding().splitlines())
        with self.assertRaisesRegex(REPORT.ValidationError, "cannot be indented as a code block"):
            REPORT.validate(finding_report(finding), require_findings=True)

    def test_rejects_clean_verdict_with_material_finding(self) -> None:
        """Require Needs revision when a material finding remains."""
        text = finding_report(canonical_finding()).replace("Verdict: Needs revision", "Verdict: Ready with limitations")
        with self.assertRaisesRegex(REPORT.ValidationError, "corrective findings/priorities require Needs revision"):
            REPORT.validate(text)

    def test_rejects_clean_verdict_with_priority_change(self) -> None:
        """Require Needs revision when a corrective priority remains."""
        text = valid_report().replace(
            "## Priority Changes\n\nNone.",
            "## Priority Changes\n\n1. Revise the instruction sequence.",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "corrective findings/priorities require Needs revision"):
            REPORT.validate(text)

    def test_rejects_needs_revision_without_corrective_basis(self) -> None:
        """Reject Needs revision when ratings and sections show no correction need."""
        text = valid_report().replace("- Limitations: Static validation only.", "- Limitations: None.")
        text = text.replace("Verdict: Ready with limitations", "Verdict: Needs revision")
        with self.assertRaisesRegex(REPORT.ValidationError, "clean ratings require Ready"):
            REPORT.validate(text)

    def test_rejects_major_redesign_without_prerequisite(self) -> None:
        """Reject Major redesign when ratings do not meet its threshold."""
        text = valid_report().replace("Verdict: Ready with limitations", "Verdict: Major redesign")
        with self.assertRaisesRegex(REPORT.ValidationError, "Major redesign requires"):
            REPORT.validate(text)

    def test_rejects_reordered_models(self) -> None:
        """Reject a table whose model rows violate canonical roster order."""
        text = swap_model_rows(valid_report(), "GPT-6 Luna", "GPT-6 Sol")
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
        """Reject swapped profile analysis while preserving model identities."""
        text = swap_model_assessments(valid_report(), "GPT-6.1 Sol", "GPT-6 Astra")
        with self.assertRaisesRegex(REPORT.ValidationError, "model-specific profile evidence"):
            REPORT.validate(text)

    def test_rejects_independent_workstreams_without_optional_delegation(self) -> None:
        """Require both parts of the GPT-6.1 Sol delegation cue."""
        text = valid_report().replace("Keep delegation optional only for independent workstreams.", "Keep independent workstreams.")
        with self.assertRaisesRegex(REPORT.ValidationError, "model-specific profile evidence"):
            REPORT.validate(text)

    def test_gpt61_accepts_two_profile_cues_without_delegation(self) -> None:
        """Delegation is one of three cues, not mandatory when two others appear."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Preserve the literal broad scope and explicit invariants.",
        )
        REPORT.validate(text)

    def test_rejects_optional_delegation_extended_to_dependent_work(self) -> None:
        """Reject optional delegation when its stated scope includes dependent work."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Delegation is optional for all tasks, including dependent work; independent workstreams are merely listed separately.",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "delegation must remain limited"):
            REPORT.validate(text)

    def test_rejects_negated_optional_delegation(self) -> None:
        """A negated optionality statement is not the GPT-6.1 profile cue."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Delegation is not optional only for independent workstreams.",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "delegation must remain limited"):
            REPORT.validate(text)

    def test_rejects_same_clause_contradictory_delegation_scope(self) -> None:
        """A nearby local-work carve-out cannot excuse broader delegation."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Keep delegation optional for independent workstreams, dependent tasks stay local, and also delegate all tasks.",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "delegation must remain limited"):
            REPORT.validate(text)

    def test_rejects_positive_delegation_after_a_negated_scope(self) -> None:
        """A local negative clause cannot mask a separate broad affirmative verb."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Keep delegation optional only for independent workstreams and do not delegate dependent tasks and delegate all tasks.",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "delegation must remain limited"):
            REPORT.validate(text)

    def test_rejects_positive_delegation_after_negated_predicate_and_then(self) -> None:
        """Do not carry a negative predicate across a later sequence marker."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Keep delegation optional only for independent workstreams; dependent tasks must not be delegated, then delegate all tasks.",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "delegation must remain limited"):
            REPORT.validate(text)

    def test_rejects_optional_delegation_extended_to_shared_context_work(self) -> None:
        """Reject an additional delegation scope beside independent workstreams."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Keep delegation optional for independent workstreams and shared-context investigations.",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "delegation must remain limited"):
            REPORT.validate(text)

    def test_rejects_optional_delegation_extended_to_dependent_scope(self) -> None:
        """Reject a second delegation target beyond independent workstreams."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Keep delegation optional for independent workstreams or for dependent tasks.",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "delegation must remain limited"):
            REPORT.validate(text)

    def test_rejects_optional_delegation_for_every_task(self) -> None:
        """Do not accept an independent-work mention that is not the delegation scope."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Delegation is optional for every task; independent workstreams are listed separately.",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "delegation must remain limited"):
            REPORT.validate(text)

    def test_rejects_additional_delegation_in_a_later_sentence(self) -> None:
        """Reject contradictory broader delegation outside the cue sentence."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Keep delegation optional only for independent workstreams. Also delegate dependent tasks.",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "delegation must remain limited"):
            REPORT.validate(text)

    def test_accepts_excluding_dependent_work_from_optional_delegation(self) -> None:
        """Allow dependent-work wording when the instruction excludes its delegation."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Keep delegation optional for independent workstreams; do not delegate dependent work.",
        )
        REPORT.validate(text)

    def test_accepts_dependent_scope_with_intervening_negation_modifier(self) -> None:
        """Preserve clear dependent-work exclusions with ordinary modifiers."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Keep delegation optional only for independent workstreams; do not under any circumstances delegate dependent tasks.",
        )
        REPORT.validate(text)

    def test_accepts_nominal_dependent_work_exclusion(self) -> None:
        """Accept a nominal statement that dependent tasks receive no delegation."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Keep delegation optional only for independent workstreams; no delegation for dependent tasks.",
        )
        REPORT.validate(text)

    def test_accepts_dependent_work_that_stays_local(self) -> None:
        """Accept a clear independent-only scope expressed by keeping other work local."""
        for wording in (
            "Delegation is optional for independent workstreams; any tasks that depend on shared context stay local.",
            "Keep delegation optional for independent workstreams, and keep dependent tasks together.",
            "Keep optional delegation for independent workstreams and other tasks local.",
        ):
            with self.subTest(wording=wording):
                text = valid_report().replace(
                    "Keep delegation optional only for independent workstreams.", wording
                )
                REPORT.validate(text)

    def test_accepts_grammatical_optional_delegation_variant(self) -> None:
        """Accept equivalent ordinary wording for optional delegation."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Delegation is optional only for independent workstreams.",
        )
        REPORT.validate(text)

    def test_accepts_optional_delegation_verb_form(self) -> None:
        """Accept a concise verb-form cue with the same profile meaning."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Optionally delegate only independent workstreams.",
        )
        REPORT.validate(text)

    def test_accepts_optional_delegation_with_intervening_context(self) -> None:
        """Accept both delegation concepts when separated by relevant detail."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Allow optional delegation after confirming tool availability, choosing bounded ownership, and preserving parent context; use it only for independent workstreams.",
        )
        REPORT.validate(text)

    def test_accepts_passive_optional_delegation_wording(self) -> None:
        """Accept passive grammar when optionality and independent scope remain."""
        for wording in (
            "Delegation of independent workstreams is optional only.",
            "Independent workstreams can optionally be delegated only.",
        ):
            with self.subTest(wording=wording):
                text = valid_report().replace(
                    "Keep delegation optional only for independent workstreams.", wording
                )
                REPORT.validate(text)

    def test_rejects_unassessed_default_model(self) -> None:
        """Require assessment of every model for this readable-input task."""
        text = valid_report().replace("| Claude Sonnet 5 | Suitable with limitations |", "| Claude Sonnet 5 | Not assessed |")
        with self.assertRaisesRegex(REPORT.ValidationError, "every target model to be assessed"):
            REPORT.validate(text)

    def test_rejects_partial_status_for_supplied_core_artifact(self) -> None:
        """Require completed status when the full single artifact is supplied."""
        text = valid_report().replace("- Status: completed", "- Status: partial")
        with self.assertRaisesRegex(REPORT.ValidationError, "requires completed audit status"):
            REPORT.validate(text)

    def test_rejects_none_mixed_with_material_findings(self) -> None:
        """Keep empty and populated findings branches mutually exclusive."""
        text = valid_report().replace("## Material Findings\n\nNone.", "## Material Findings\n\nNone.\n\n" + canonical_finding())
        with self.assertRaisesRegex(REPORT.ValidationError, "cannot mix None"):
            REPORT.validate(text)

    def test_rejects_prose_inside_rating_table(self) -> None:
        """Reject non-table content within a required table section."""
        text = valid_report().replace("| Maintainability and evaluability | 4 | None. |", "Note: ratings are provisional.\n| Maintainability and evaluability | 4 | None. |")
        with self.assertRaisesRegex(REPORT.ValidationError, "well-formed table rows"):
            REPORT.validate(text)

    def test_rejects_blank_line_inside_rating_table(self) -> None:
        """Reject a blank line that breaks the Markdown rating table."""
        text = valid_report().replace("| Area | Rating | Main risk |\n|---|---:|---|", "| Area | Rating | Main risk |\n\n|---|---:|---|")
        with self.assertRaisesRegex(REPORT.ValidationError, "well-formed table rows"):
            REPORT.validate(text)

    def test_rejects_blank_line_inside_compatibility_table(self) -> None:
        """Reject a blank line that breaks the Markdown compatibility table."""
        text = valid_report().replace("| Model | Verdict | Main risk | Required adaptation |\n|---|---|---|---|", "| Model | Verdict | Main risk | Required adaptation |\n\n|---|---|---|---|")
        with self.assertRaisesRegex(REPORT.ValidationError, "well-formed table rows"):
            REPORT.validate(text)

    def test_rejects_four_space_indented_rating_rows(self) -> None:
        """Reject indented code-block rows as a readiness table."""
        text = valid_report().replace("| Discovery and delegation | 4 | None. |", "    | Discovery and delegation | 4 | None. |")
        with self.assertRaisesRegex(REPORT.ValidationError, "only well-formed table rows"):
            REPORT.validate(text)

    def test_rejects_four_space_indented_compatibility_rows(self) -> None:
        """Reject indented code-block rows as a compatibility table."""
        text = valid_report().replace("| GPT-6 Luna |", "    | GPT-6 Luna |", 1)
        with self.assertRaisesRegex(REPORT.ValidationError, "only well-formed table rows"):
            REPORT.validate(text)

    def test_accepts_up_to_three_space_indented_markdown_table_rows(self) -> None:
        """Accept Markdown table rows indented within the supported syntax."""
        text = valid_report().replace("| Discovery and delegation |", "   | Discovery and delegation |", 1)
        text = text.replace("| GPT-6 Luna |", "  | GPT-6 Luna |", 1)
        REPORT.validate(text)

    def test_rejects_open_code_fence_before_structured_sections(self) -> None:
        """Do not accept headings and verdict rendered inside an open fence."""
        text = finding_report(canonical_finding()).replace(
            "Correction: Fix the condition.",
            "Correction: Fix the condition.\n```markdown",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "fenced code blocks"):
            REPORT.validate(text, require_findings=True)

    def test_rejects_open_tilde_fence_before_structured_sections(self) -> None:
        """Reject Markdown tilde fences that would hide later report sections."""
        text = finding_report(canonical_finding()).replace(
            "Correction: Fix the condition.",
            "Correction: Fix the condition.\n~~~markdown",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "fenced code blocks"):
            REPORT.validate(text, require_findings=True)

    def test_rejects_code_indented_final_verdict(self) -> None:
        """Require the terminal verdict to render as report text."""
        text = valid_report().replace("Verdict: Ready with limitations", "    Verdict: Ready with limitations")
        with self.assertRaisesRegex(REPORT.ValidationError, "final verdict cannot be indented as code"):
            REPORT.validate(text)

    def test_rejects_code_indented_audit_marker(self) -> None:
        """Require Audit to be a report marker, not a code-block example."""
        text = valid_report().replace("Audit: example", "    Audit: example", 1)
        with self.assertRaisesRegex(REPORT.ValidationError, "Audit marker"):
            REPORT.validate(text)

    def test_rejects_code_indented_scope_field(self) -> None:
        """Do not use a code-block field to satisfy required audit scope."""
        text = valid_report().replace("- Status: completed", "    - Status: completed", 1)
        with self.assertRaisesRegex(REPORT.ValidationError, "scope fields cannot be indented as code"):
            REPORT.validate(text)

    def test_accepts_indented_markdown_separator_and_headings(self) -> None:
        """Accept permitted indentation on table separators and headings."""
        text = valid_report().replace("|---|---:|---|", "   |---|---:|---|", 1)
        text = text.replace("## Audit Scope", "   ## Audit Scope", 1)
        REPORT.validate(text)

    def test_accepts_soft_wrapped_finding_correction(self) -> None:
        """Accept a line-wrapped correction while preserving field order."""
        text = finding_report(canonical_finding()).replace(
            "Correction: Fix the condition.", "Correction: Fix the\ncondition."
        )
        REPORT.validate(text)

    def test_accepts_escaped_pipe_in_rating_cell(self) -> None:
        """Treat an escaped pipe as cell text rather than another column."""
        text = valid_report().replace("| Discovery and delegation | 4 | None. |", "| Discovery and delegation | 4 | Literal a\\|b is ambiguous. |")
        REPORT.validate(text)

    def test_accepts_escaped_pipe_in_compatibility_cell(self) -> None:
        """Treat an escaped pipe in a model risk as cell text."""
        text = valid_report().replace("| Claude Haiku 4.5 | Suitable with limitations | risk | adaptation |", "| Claude Haiku 4.5 | Suitable with limitations | Literal a\\|b is ambiguous. | adaptation |")
        REPORT.validate(text)

    def test_accepts_escaped_pipe_at_end_of_rating_cell(self) -> None:
        """Accept an escaped pipe immediately before the closing table delimiter."""
        text = valid_report().replace("| Discovery and delegation | 4 | None. |", "| Discovery and delegation | 4 | Literal a\\||")
        REPORT.validate(text)

    def test_accepts_escaped_pipe_at_end_of_compatibility_cell(self) -> None:
        """Accept an escaped pipe immediately before a model-row delimiter."""
        text = valid_report().replace("| Claude Haiku 4.5 | Suitable with limitations | risk | adaptation |", "| Claude Haiku 4.5 | Suitable with limitations | Literal a\\|| adaptation |")
        REPORT.validate(text)

    def test_rejects_extra_edge_pipe_in_table_row(self) -> None:
        """Reject malformed doubled trailing delimiters."""
        text = valid_report().replace("| Discovery and delegation | 4 | None. |", "| Discovery and delegation | 4 | None. ||")
        with self.assertRaisesRegex(REPORT.ValidationError, "invalid number of columns"):
            REPORT.validate(text)

    def test_rejects_escaped_pipe_as_closing_table_delimiter(self) -> None:
        """Require a real closing delimiter after a terminal escaped pipe."""
        text = valid_report().replace(
            "| Discovery and delegation | 4 | None. |",
            "| Discovery and delegation | 4 | None. \\|",
        )
        with self.assertRaisesRegex(REPORT.ValidationError, "unescaped closing pipe"):
            REPORT.validate(text)

    def test_rejects_rating_separator_with_wrong_column_count(self) -> None:
        """Reject a one-column separator under the three-column rating header."""
        text = valid_report().replace("|---|---:|---|", "|---|", 1)
        with self.assertRaisesRegex(REPORT.ValidationError, "separator must match header columns"):
            REPORT.validate(text)

    def test_rejects_compatibility_separator_with_wrong_column_count(self) -> None:
        """Reject a one-column separator under the four-column compatibility header."""
        text = valid_report().replace("|---|---|---|---|", "|---|", 1)
        with self.assertRaisesRegex(REPORT.ValidationError, "separator must match header columns"):
            REPORT.validate(text)

    def test_accepts_compound_profile_cue_across_long_cell_text(self) -> None:
        """Do not impose an undocumented distance limit on a complete profile cue."""
        text = valid_report().replace(
            "Keep delegation optional only for independent workstreams.",
            "Keep delegation optional only for independent workstreams while preserving all stated invariants and broad scope across incident stages.",
        )
        REPORT.validate(text)

    def test_rejects_more_than_five_priority_changes(self) -> None:
        """Enforce the skill's five-item maximum for corrective priorities."""
        items = "\n".join(f"{number}. Corrective action {number}." for number in range(1, 7))
        text = valid_report().replace("## Priority Changes\n\nNone.", "## Priority Changes\n\n" + items)
        text = text.replace("Verdict: Ready with limitations", "Verdict: Needs revision")
        with self.assertRaisesRegex(REPORT.ValidationError, "must not exceed five"):
            REPORT.validate(text)

    def test_accepts_unindented_wrapped_priority_continuation(self) -> None:
        """Accept a wrapped Markdown list item without continuation indentation."""
        text = valid_report().replace(
            "## Priority Changes\n\nNone.",
            "## Priority Changes\n\n1. Replace fixed delegation\nwith independent workstreams.",
        ).replace("Verdict: Ready with limitations", "Verdict: Needs revision")
        REPORT.validate(text)

    def test_rejects_code_indented_priority_item(self) -> None:
        """Do not count an indented code sample as a numbered priority."""
        text = valid_report().replace(
            "## Priority Changes\n\nNone.",
            "## Priority Changes\n\n    1. Correct the finding.",
        ).replace("Verdict: Ready with limitations", "Verdict: Needs revision")
        with self.assertRaisesRegex(REPORT.ValidationError, "priority items cannot be indented as code"):
            REPORT.validate(text)

    def test_accepts_supported_indentation_for_empty_priorities(self) -> None:
        """Treat one to three spaces before None. as ordinary Markdown text."""
        text = valid_report().replace("## Priority Changes\n\nNone.", "## Priority Changes\n\n   None.")
        REPORT.validate(text)

    def test_rejects_code_indented_empty_priorities(self) -> None:
        """Do not treat code-block None. as the empty-priority branch."""
        text = valid_report().replace("## Priority Changes\n\nNone.", "## Priority Changes\n\n    None.")
        with self.assertRaisesRegex(REPORT.ValidationError, "None. priority cannot be indented as code"):
            REPORT.validate(text)

    def test_rejects_none_mixed_after_numbered_priority(self) -> None:
        """Keep the None and numbered-priority branches exclusive."""
        text = valid_report().replace(
            "## Priority Changes\n\nNone.",
            "## Priority Changes\n\n1. Correct the finding.\n\nNone.",
        ).replace("Verdict: Ready with limitations", "Verdict: Needs revision")
        with self.assertRaisesRegex(REPORT.ValidationError, "cannot be mixed"):
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
