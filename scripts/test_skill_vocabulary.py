"""Regression checks for vocabulary validation, including confidence/legacy boundaries."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "vocabulary", Path(__file__).with_name("check-skill-vocabulary.py")
)
vocabulary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vocabulary)

CANONICAL = "## Severity\n\nSeverity: CRITICAL | HIGH | MEDIUM | LOW\n"


class VocabularyTests(unittest.TestCase):
    def inspect(self, text, files=None, *, package_name="fixture"):
        with tempfile.TemporaryDirectory() as directory:
            original_root = vocabulary.ROOT
            try:
                vocabulary.ROOT = Path(directory)
                package = vocabulary.ROOT / "skills" / package_name
                package.mkdir(parents=True)
                (package / "SKILL.md").write_text(text)
                for name, content in (files or {}).items():
                    path = package / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content)
                return vocabulary.inspect_package(package)
            finally:
                vocabulary.ROOT = original_root

    def test_canonical_output_and_lowercase_confidence_pass(self):
        emits, errors = self.inspect(
            CANONICAL + "Use confidence per finding:\n- `high`: direct evidence.\n"
        )
        self.assertTrue(emits)
        self.assertEqual(errors, [])

    def test_legacy_input_aliases_do_not_become_output_errors(self):
        _, errors = self.inspect(
            CANONICAL + "### Input compatibility\n| `High` | `HIGH` |\n"
        )
        self.assertEqual(errors, [])

    def test_old_severity_field_fails_even_with_canonical_words_present(self):
        _, errors = self.inspect(CANONICAL + "Severity: High | Medium | Low\n")
        self.assertTrue(any("obsolete emitted severity" in error for error in errors))

    def test_lowercase_impact_rubric_fails(self):
        _, errors = self.inspect(CANONICAL + "- `high`: major harm.\n")
        self.assertTrue(any("obsolete emitted severity" in error for error in errors))

    def test_old_summary_projection_fails(self):
        _, errors = self.inspect(CANONICAL + "Errors: ERROR_COUNT\n")
        self.assertTrue(any("obsolete emitted severity" in error for error in errors))

    def test_old_enum_declaration_fails(self):
        _, errors = self.inspect(CANONICAL + "`FINDING_SEVERITY` - one of `error`, `warning`.\n")
        self.assertTrue(any("obsolete emitted severity" in error for error in errors))

    def test_old_no_issue_action_sentinel_fails(self):
        _, errors = self.inspect(CANONICAL + "- a1a1a1a: keep — none: No issue.\n")
        self.assertTrue(any("obsolete emitted severity" in error for error in errors))

    def test_bold_legacy_rubric_fails(self):
        _, errors = self.inspect(CANONICAL + "- **High:** major harm.\n")
        self.assertTrue(any("obsolete emitted severity" in error for error in errors))

    def test_confidence_only_package_needs_no_severity(self):
        emits, errors = self.inspect("## Confidence\n- `high`: direct evidence.\n")
        self.assertFalse(emits)
        self.assertEqual(errors, [])

    def test_missing_critical_level_fails(self):
        _, errors = self.inspect("## Severity\nSeverity: HIGH | MEDIUM | LOW\n")
        self.assertTrue(any("missing four-level" in error for error in errors))

    def test_unknown_output_level_fails(self):
        _, errors = self.inspect(CANONICAL + "Severity: URGENT\n")
        self.assertTrue(any("invalid literal Severity" in error for error in errors))

    def test_readme_cannot_complete_a_core_enum(self):
        _, errors = self.inspect(
            "## Severity\nSeverity: HIGH | MEDIUM | LOW\n",
            {"README.md": CANONICAL},
        )
        self.assertTrue(any("SKILL.md" in error and "missing four-level" in error for error in errors))

    def test_another_complete_enum_cannot_complete_a_partial_enum(self):
        levels = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
        for missing in levels:
            with self.subTest(missing=missing):
                partial = " | ".join(level for level in levels if level != missing)
                _, errors = self.inspect(CANONICAL + "Severity: " + partial + "\n")
                self.assertTrue(any("missing four-level" in error for error in errors))

    def test_examples_cannot_complete_a_partial_rubric(self):
        _, errors = self.inspect(
            "## Severity\n- `HIGH`: major.\n- `MEDIUM`: bounded.\n- `LOW`: local.\n"
            "## Examples\nSeverity: CRITICAL\n",
            {"README.md": CANONICAL},
        )
        self.assertTrue(any("missing four-level" in error for error in errors))

    def test_complete_referenced_rubric_passes(self):
        _, errors = self.inspect(
            "## Severity\nRead [rubric](references/rubric.md).\n",
            {"references/rubric.md": "## Severity\n" + "\n".join(
                f"- `{level}`: impact." for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
            )},
        )
        self.assertEqual(errors, [])

    def test_readme_cannot_complete_a_referenced_rubric(self):
        _, errors = self.inspect(
            "## Severity\nRead [rubric](references/rubric.md).\n",
            {"README.md": CANONICAL, "references/rubric.md":
             "## Severity\n- `HIGH`: major.\n- `MEDIUM`: bounded.\n- `LOW`: local.\n"},
        )
        self.assertTrue(any("references/rubric.md" in error and "missing four-level" in error for error in errors))

    def test_quoted_unknown_or_legacy_members_fail_at_every_position(self):
        for invalid in ("URGENT", "High"):
            for position in range(4):
                values = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
                values[position] = invalid
                with self.subTest(invalid=invalid, position=position):
                    _, errors = self.inspect(CANONICAL + "Severity: " + " | ".join(
                        f"`{value}`" for value in values
                    ) + "\n")
                    self.assertTrue(any("invalid literal Severity" in error for error in errors))

    def test_quoted_unknown_scalar_fails(self):
        _, errors = self.inspect(CANONICAL + "Severity: `URGENT`\n")
        self.assertTrue(any("invalid literal Severity" in error for error in errors))

    def test_whole_code_and_bold_enums_cannot_hide_unknown_members(self):
        for value in ("`CRITICAL | HIGH | URGENT | LOW`",
                      "**CRITICAL** | **HIGH** | **URGENT** | **LOW**"):
            with self.subTest(value=value):
                _, errors = self.inspect(CANONICAL + "Severity: " + value + "\n")
                self.assertTrue(any("invalid literal Severity" in error for error in errors))

    def test_formatted_canonical_enums_pass(self):
        for value in (
            "`CRITICAL` | `HIGH` | `MEDIUM` | `LOW`",
            "`CRITICAL | HIGH | MEDIUM | LOW`",
            "**CRITICAL** | **HIGH** | **MEDIUM** | **LOW**",
            "<CRITICAL | HIGH | MEDIUM | LOW>",
            "`CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`.",
            "CRITICAL or HIGH or MEDIUM or LOW",
        ):
            with self.subTest(value=value):
                _, errors = self.inspect("## Severity\nSeverity: " + value + "\n")
                self.assertEqual(errors, [])

    def test_placeholders_and_prose_remain_exempt_from_literal_validation(self):
        for value in ("<one permitted value>", "FINDING_SEVERITY", "`FINDING_SEVERITY`",
                      "`CRITICAL` means severe harm; `HIGH` means major harm; "
                      "`MEDIUM` means bounded harm; `LOW` means local harm."):
            with self.subTest(value=value):
                _, errors = self.inspect(CANONICAL + "Severity: " + value + "\n")
                self.assertEqual(errors, [])

    def test_formatted_named_enum_cannot_hide_unknown_members(self):
        _, errors = self.inspect(
            CANONICAL + "`FINDING_SEVERITY` - one of `CRITICAL`, `HIGH`, `URGENT`, `LOW`.\n"
        )
        self.assertTrue(any("invalid literal Severity" in error for error in errors))

    def test_scalar_samples_and_sentinels_pass(self):
        for value in ("LOW", "`HIGH`", "NONE", "`UNASSESSED`"):
            with self.subTest(value=value):
                _, errors = self.inspect(CANONICAL + "Severity: " + value + "\n")
                self.assertEqual(errors, [])

    def test_angle_template_enum_members_are_validated(self):
        _, errors = self.inspect(CANONICAL + "Severity: <CRITICAL | HIGH | URGENT | LOW>\n")
        self.assertTrue(any("invalid literal Severity" in error for error in errors))

    def test_inline_rubric_is_not_completed_by_readme(self):
        _, errors = self.inspect(
            "Severity: `HIGH` for major harm; `MEDIUM` for bounded harm; `LOW` for local harm.\n",
            {"README.md": CANONICAL},
        )
        self.assertTrue(any("missing four-level" in error for error in errors))

    def test_separate_rubrics_cannot_complete_one_another(self):
        _, errors = self.inspect(
            "## Severity\n- `HIGH`: major.\n- `MEDIUM`: bounded.\n- `LOW`: local.\n"
            "## Another Severity Rubric\n- `CRITICAL`: severe.\n"
        )
        self.assertEqual(sum("missing four-level" in error for error in errors), 2)

    def test_heading_based_rubric_passes(self):
        _, errors = self.inspect("## Severity\n" + "\n".join(
            f"### `{level}`\nUse for impact.\n" for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
        ))
        self.assertEqual(errors, [])

    def test_comma_separated_prose_rubric_passes(self):
        _, errors = self.inspect(
            "## Severity\nRate issues `CRITICAL` for severe, `HIGH` for major, "
            "`MEDIUM` for bounded; `LOW` for local, and `NONE` for no issue.\n"
        )
        self.assertEqual(errors, [])

    def test_classifications_after_a_rubric_do_not_become_levels(self):
        _, errors = self.inspect(
            "## Severity, Classification, Verdict\n" + "\n".join(
                f"- `{level}`: impact." for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
            ) + "\n- `Confirmed issue`: evidence.\n- `BLOCK`: stop.\n"
        )
        self.assertEqual(errors, [])

    def test_readme_and_unrelated_example_words_cannot_fill_an_enum(self):
        _, errors = self.inspect(
            "Severity: `HIGH` | `MEDIUM` | `LOW`\n",
            {"README.md": CANONICAL, "references/examples.md": CANONICAL},
        )
        self.assertTrue(any("SKILL.md" in error and "missing four-level" in error for error in errors))

    def test_generic_coverage_enum_requires_all_four_states(self):
        for value in ("covered | missing | n/a", "covered | gap | n/a",
                      "covered | gap | unknown | n/a", "covered | not-assessed | n/a"):
            with self.subTest(value=value):
                _, errors = self.inspect("Checklist status:\n- Tests: " + value + "\n")
                self.assertTrue(any("coverage enum" in error for error in errors))

    def test_complete_coverage_enum_passes(self):
        for value in ("covered | gap | not-assessed | n/a",
                      "covered | gap | not-assessed | n/a (<reason>)"):
            with self.subTest(value=value):
                _, errors = self.inspect("Checklist status:\n- Tests: " + value + "\n")
                self.assertEqual(errors, [])

    def test_coverage_checks_every_member_including_unknown_trailing_values(self):
        for value in ("covered | gap | not-assessed | n/a | invented",
                      "covered | invented | gap | not-assessed | n/a",
                      "`covered` | `gap` | `not-assessed` | `n/a` | `invented`"):
            with self.subTest(value=value):
                _, errors = self.inspect("- Tests: " + value + "\n")
                self.assertTrue(any("coverage enum" in error for error in errors))

    def test_coverage_enum_cannot_be_completed_by_another_declaration(self):
        _, errors = self.inspect(
            "- Code: covered | gap | not-assessed | n/a\n- Tests: covered | gap | n/a\n"
        )
        self.assertTrue(any("coverage enum" in error for error in errors))

    def test_actions_and_missing_evidence_are_not_general_classifications(self):
        for value in ("blocker", "required test", "follow-up", "accepted tradeoff",
                      "not applicable", "Needs more evidence", "fix-now", "clarify"):
            with self.subTest(value=value):
                _, errors = self.inspect("Classification: Confirmed issue | `" + value + "`\n")
                self.assertTrue(any("Classification field" in error for error in errors))

    def test_general_and_domain_classifications_pass(self):
        for value in ("Confirmed issue", "Likely risk", "Open question", "Accepted tradeoff",
                      "Test gap", "Defense-in-depth", "Measurement gap", "true positive"):
            with self.subTest(value=value):
                _, errors = self.inspect("Classification: " + value + "\n")
                self.assertEqual(errors, [])

    def test_canonical_finding_states_pass_and_legacy_outputs_fail(self):
        for value in ("open", "fixed", "deferred", "waived"):
            with self.subTest(value=value):
                _, errors = self.inspect("Status: " + value + "\n", package_name="code-quality")
                self.assertEqual(errors, [])
        for value in ("Open", "Resolved", "`Resolved`", "owned-with-remediation-plan",
                      "waived-with-rationale"):
            with self.subTest(value=value):
                _, errors = self.inspect("Status: " + value + "\n", package_name="code-quality")
                self.assertTrue(any("legacy emitted finding state" in error for error in errors))

    def test_legacy_input_state_mapping_prose_passes(self):
        _, errors = self.inspect("Normalize input `Open` to `open` and `Resolved` to `fixed`.\n")
        self.assertEqual(errors, [])

    def test_domain_artifact_status_is_not_a_finding_lifecycle(self):
        _, errors = self.inspect("Status: Open\nState: Resolved\n", package_name="domain-workflow")
        self.assertEqual(errors, [])

    def test_no_findings_marker_has_one_canonical_case(self):
        _, errors = self.inspect("Findings: none\n")
        self.assertTrue(any("Findings: None marker" in error for error in errors))
        _, errors = self.inspect("Findings: None\n")
        self.assertEqual(errors, [])

    def test_task_specific_absence_and_unassessed_forms_pass(self):
        _, errors = self.inspect("Footers: none\nAssessment: Not assessed.\nSeverity: UNASSESSED\n")
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
