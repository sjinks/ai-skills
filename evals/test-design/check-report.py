#!/usr/bin/env python3
"""Validate the test-design report grammar without a model call."""

import re
import sys

MARKERS = ("Test cases:", "Evidence:", "Verification:")
PROFILES = {"plan", "implement", "assessment", "blocked", "changed"}


def validate(report: str, profile: str) -> None:
    """Check label order, required content, branch, and terminal status."""
    if profile not in PROFILES:
        raise ValueError("invalid profile")
    lines = report.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n")
    positions = []
    for marker in MARKERS:
        matching = [index for index, line in enumerate(lines) if line.startswith(marker)]
        if len(matching) != 1:
            raise ValueError(f"{marker} must occur once")
        positions.append(matching[0])
    if positions != sorted(positions) or positions[0] != 0:
        raise ValueError("labels must be ordered and start the report")
    cases = "\n".join(lines[positions[0]:positions[1]])[len(MARKERS[0]):].strip()
    evidence = "\n".join(lines[positions[1]:positions[2]])[len(MARKERS[1]):].strip()
    if not evidence:
        raise ValueError("evidence must be nonempty")
    if profile == "blocked":
        if cases != "Blocked.":
            raise ValueError("blocked profile requires Blocked. and no cases")
    elif cases in {"", "Blocked."}:
        raise ValueError("nonblocked profile requires cases")
    if positions[2] != len(lines) - 1:
        raise ValueError("verification must be the final line")
    verification = lines[-1][len(MARKERS[2]):].strip()
    if profile in {"blocked", "plan", "assessment", "implement"}:
        if verification != "Not run; no tests changed.":
            raise ValueError("this profile requires the no-changes verification status")
    elif not re.fullmatch(r"(?:Ran|Unverified): .+", verification):
        raise ValueError("invalid verification status")


VALID = {
    "plan": "Test cases: - valid transfer; expected balances; catches wrong debit\nEvidence: supplied contract\nVerification: Not run; no tests changed.",
    "implement": "Test cases: - clamp below min; expected min; catches wrong bound\nEvidence: supplied contract\nVerification: Not run; no tests changed.",
    "assessment": "Test cases: - invalid middle row; zero persisted; catches partial commit\nEvidence: supplied contract and suite list\nVerification: Not run; no tests changed.",
    "blocked": "Test cases: Blocked.\nEvidence: Need the feature behavior.\nVerification: Not run; no tests changed.",
    "changed": "Test cases: - clamp below min; expected min; catches wrong bound\nEvidence: contract and repository test pattern\nVerification: Ran: npm test passed",
}


def self_test() -> None:
    """Exercise valid profiles and deterministic mutation classes."""
    for profile, report in VALID.items():
        validate(report, profile)
    validate(VALID["changed"].replace("Ran: npm test passed", "Unverified: test runner unavailable"), "changed")
    base = VALID["plan"]
    invalid = {
        "omission": base.replace("Evidence: supplied contract\n", ""),
        "reorder": base.replace("Evidence: supplied contract\nVerification: Not run; no tests changed.", "Verification: Not run; no tests changed.\nEvidence: supplied contract"),
        "duplicate": base.replace("Evidence: supplied contract", "Evidence: supplied contract\nEvidence: duplicate"),
        "invalid status": base.replace("Not run; no tests changed.", "Passed"),
        "profile crossover": VALID["blocked"],
        "trailing prose": base + "\nAdditional prose.",
    }
    for name, report in invalid.items():
        try:
            validate(report, "plan")
        except ValueError:
            continue
        raise AssertionError(f"accepted {name}")
    try:
        validate(base, "blocked")
    except ValueError:
        pass
    else:
        raise AssertionError("accepted reverse profile crossover")
    try:
        validate(VALID["changed"].replace("Ran: npm test passed", "Passed"), "changed")
    except ValueError:
        pass
    else:
        raise AssertionError("accepted changed-profile invalid status")
    print("test-design report contract: valid profiles and mutations passed")


def main() -> None:
    """Validate stdin for a selected profile, or run local mutation checks."""
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        return
    if len(sys.argv) != 2:
        raise SystemExit("usage: check-report.py <profile>|--self-test")
    try:
        validate(sys.stdin.read(), sys.argv[1])
    except ValueError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
