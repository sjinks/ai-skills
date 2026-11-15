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
    def inspect(self, text):
        with tempfile.TemporaryDirectory() as directory:
            original_root = vocabulary.ROOT
            try:
                vocabulary.ROOT = Path(directory)
                package = vocabulary.ROOT / "skills" / "fixture"
                package.mkdir(parents=True)
                (package / "SKILL.md").write_text(text)
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


if __name__ == "__main__":
    unittest.main()
