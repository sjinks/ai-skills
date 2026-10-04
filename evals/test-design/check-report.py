#!/usr/bin/env python3
"""Validate the test-design report grammar without a model call."""

import re
import sys

MARKERS = ("Designed cases:", "Design evidence:", "Test execution:")
PROFILES = {"plan", "implement", "assessment", "blocked"}
IMPLEMENT_STATUS_PATTERN = r"(?:Unverified: \S[^\n]*|Ran: \S(?:[^\n]*\S)? => (?:passed|failed|exit -?\d+))"


def validate(report: str, profile: str, labels: tuple[str, str, str] = MARKERS) -> None:
    """Check label order, required content, branch, and terminal status."""
    if profile not in PROFILES:
        raise ValueError("invalid profile")
    if len(labels) != 3 or len(set(labels)) != 3 or any("\n" in label or not label.endswith(":") for label in labels):
        raise ValueError("invalid labels")
    lines = report.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n")
    if labels != MARKERS and any(line.startswith(marker) for line in lines for marker in MARKERS if marker not in labels):
        raise ValueError("default labels cannot appear when caller labels replace them")
    positions = []
    for marker in labels:
        matching = [index for index, line in enumerate(lines) if line.startswith(marker)]
        if len(matching) != 1:
            raise ValueError(f"{marker} must occur once")
        positions.append(matching[0])
    if positions != sorted(positions) or positions[0] != 0:
        raise ValueError("labels must be ordered and start the report")
    cases = "\n".join(lines[positions[0]:positions[1]])[len(labels[0]):].strip()
    evidence = "\n".join(lines[positions[1]:positions[2]])[len(labels[1]):].strip()
    if not evidence:
        raise ValueError("evidence must be nonempty")
    if profile == "blocked":
        if cases != "Blocked.":
            raise ValueError("blocked profile requires Blocked. and no cases")
    elif cases in {"", "Blocked."}:
        raise ValueError("nonblocked profile requires cases")
    if positions[2] != len(lines) - 1:
        raise ValueError("verification must be the final line")
    verification = lines[-1][len(labels[2]):].strip()
    if profile in {"blocked", "plan", "assessment"}:
        if verification != "Not run; no tests changed.":
            raise ValueError("this profile requires the no-changes verification status")
    elif not re.fullmatch(IMPLEMENT_STATUS_PATTERN, verification):
        raise ValueError("invalid verification status")


VALID = {
    "plan": "Designed cases: - valid transfer; expected balances; catches wrong debit\nDesign evidence: supplied contract\nTest execution: Not run; no tests changed.",
    "implement": "Designed cases: - clamp below min; expected min; catches wrong bound\nDesign evidence: contract and repository test pattern\nTest execution: Ran: node --test test/clamp.test.js => passed",
    "assessment": "Designed cases: - invalid middle row; zero persisted; catches partial commit\nDesign evidence: supplied contract and suite list\nTest execution: Not run; no tests changed.",
    "blocked": "Designed cases: Blocked.\nDesign evidence: Need the feature behavior.\nTest execution: Not run; no tests changed.",
}
CUSTOM_LABELS = ("Case set:", "Design basis:", "Run record:")
CUSTOM_BLOCKED = "Case set: Blocked.\nDesign basis: Need the feature behavior.\nRun record: Not run; no tests changed."


def self_test() -> None:
    """Exercise valid profiles and deterministic mutation classes."""
    for profile, report in VALID.items():
        validate(report, profile)
    validate(CUSTOM_BLOCKED, "blocked", CUSTOM_LABELS)
    assert set(VALID) == PROFILES, "every supported profile needs a valid fixture"
    # Independent contract matrix: modes are checked against both status families.
    for profile in ("plan", "assessment", "blocked", "implement"):
        prefix = VALID[profile].rsplit("Test execution:", 1)[0]
        for status, changed in (
            ("Not run; no tests changed.", False),
            ("Ran: node --test => passed", True),
            ("Ran: node --test => failed", True),
            ("Ran: node --test => exit 1", True),
            ("Unverified: test runner unavailable", True),
        ):
            expected = changed if profile == "implement" else not changed
            try:
                validate(prefix + "Test execution: " + status, profile)
            except ValueError:
                assert not expected, (profile, status, "unexpected rejection")
            else:
                assert expected, (profile, status, "unexpected acceptance")
    base = VALID["plan"]
    invalid = {
        "omission": base.replace("Design evidence: supplied contract\n", ""),
        "reorder": base.replace("Design evidence: supplied contract\nTest execution: Not run; no tests changed.", "Test execution: Not run; no tests changed.\nDesign evidence: supplied contract"),
        "duplicate": base.replace("Design evidence: supplied contract", "Design evidence: supplied contract\nDesign evidence: duplicate"),
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
    for name, report in {
        "default label in custom report": CUSTOM_BLOCKED.replace("Case set:", "Designed cases:"),
        "custom blocked trailing prose": CUSTOM_BLOCKED + "\nExtra text.",
        "custom blocked wrong branch": CUSTOM_BLOCKED.replace("Blocked.", "a planned case"),
    }.items():
        try:
            validate(report, "blocked", CUSTOM_LABELS)
        except ValueError:
            continue
        raise AssertionError(f"accepted {name}")
    for status in (
        "Passed", "Ran: node --test test/clamp.test.js", "Ran:", "Unverified:",
        "Ran: 3 tests passed", "Ran: => passed", "Ran:    => failed",
        "Ran: node --test =>", "Ran: node --test => exit unknown",
        "Ran: node --test => passed and extra prose",
    ):
        report = VALID["implement"].rsplit("Test execution:", 1)[0] + "Test execution: " + status
        try:
            validate(report, "implement")
        except ValueError:
            continue
        raise AssertionError(f"accepted implementation invalid status: {status}")
    try:
        validate(VALID["implement"], "changed")
    except ValueError:
        pass
    else:
        raise AssertionError("accepted obsolete changed profile")
    print("test-design report contract: valid profiles and mutations passed")


def main() -> None:
    """Validate stdin for a selected profile, or run local mutation checks."""
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        self_test()
        return
    if len(sys.argv) not in (2, 5):
        raise SystemExit("usage: check-report.py <profile> [case-label evidence-label verification-label]|--self-test")
    try:
        labels = tuple(sys.argv[2:]) if len(sys.argv) == 5 else MARKERS
        validate(sys.stdin.read(), sys.argv[1], labels)
    except ValueError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
