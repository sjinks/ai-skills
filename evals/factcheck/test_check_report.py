#!/usr/bin/env python3
"""Deterministic mutation coverage for the factcheck report validator."""
import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("check-report.py")
spec = importlib.util.spec_from_file_location("check_report", MODULE_PATH)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

VALID = """Fact-Check Summary
- Overall result: 1 SUPPORTED
- Mode: report-only
- Sensitive domain: no

Scope
- Target: sample
- In scope: C1
- Out of scope: none
- Time frame / jurisdiction / domain: not specified
- Evidence access: supplied-only

Claims Checked
- C1: The sample is correct.
  Location: supplied sentence
  Checkability: factual
  Claim class: identity/date

Evidence Reviewed
- E1: supplied record
  Type: primary, user-provided
  Date/currentness: 2026 supplied excerpt
  Locator: supplied excerpt paragraph 1
  Claim support: direct, C1 states the same fact
  Relevance: C1
  Limitation: supplied-only evidence

Findings
- C1
  Verdict: SUPPORTED
  Confidence: high
  Confidence reason: direct supplied record
  Evidence: E1, supplied excerpt paragraph 1
  Reasoning: the record entails the claim.

Recommended Corrections
- C1: No correction needed

Open Questions
- None

Verification Limits
- Supplied-only evidence

Residual Uncertainty
- No material residual uncertainty identified
"""


class ReportContractTests(unittest.TestCase):
    def assert_invalid(self, text):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                checker.validate(text)

    def test_valid_report(self):
        checker.validate(VALID)

    def test_missing_section_is_rejected(self):
        self.assert_invalid(VALID.replace("\nOpen Questions\n- None\n", "\n"))

    def test_reordered_section_is_rejected(self):
        text = VALID.replace("\nOpen Questions\n- None\n\nVerification Limits\n- Supplied-only evidence\n", "\nVerification Limits\n- Supplied-only evidence\n\nOpen Questions\n- None\n")
        self.assert_invalid(text)

    def test_duplicate_field_is_rejected(self):
        self.assert_invalid(VALID.replace("  Locator: supplied excerpt paragraph 1\n", "  Locator: supplied excerpt paragraph 1\n  Locator: duplicate\n"))

    def test_invalid_enum_is_rejected(self):
        self.assert_invalid(VALID.replace("Claim support: direct", "Claim support: decisive"))

    def test_profile_crossover_is_rejected(self):
        original_argv, original_stdin = sys.argv, sys.stdin
        try:
            sys.argv = ["check-report.py", "negative-trigger-001"]
            sys.stdin = io.StringIO(VALID)
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    checker.main()
        finally:
            sys.argv, sys.stdin = original_argv, original_stdin

    def test_trailing_prose_is_rejected(self):
        self.assert_invalid(VALID + "\nExtra prose")


if __name__ == "__main__":
    unittest.main()
