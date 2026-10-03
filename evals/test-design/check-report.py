#!/usr/bin/env python3
"""Validate the test-design report grammar without a model call."""

import re
import sys

MARKERS = ("Test cases:", "Evidence:", "Verification:")
PROFILES = {"plan", "implement", "assessment", "blocked"}


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
    elif not re.fullmatch(r"(?:Ran|Unverified): .+", verification):
        raise ValueError("invalid verification status")
    elif verification.startswith("Ran:") and not re.search(
        r"\b(?:pass(?:ed)?|fail(?:ed)?|exit(?:ed)?(?:\s+(?:code|status|with))?\s*[:=]?\s*-?\d+)\b",
        verification, re.IGNORECASE,
    ):
        raise ValueError("Ran requires a pass/fail/exit result")


VALID = {
    "plan": "Test cases: - valid transfer; expected balances; catches wrong debit\nEvidence: supplied contract\nVerification: Not run; no tests changed.",
    "implement": "Test cases: - clamp below min; expected min; catches wrong bound\nEvidence: contract and repository test pattern\nVerification: Ran: node --test test/clamp.test.js; 3 tests passed",
    "assessment": "Test cases: - invalid middle row; zero persisted; catches partial commit\nEvidence: supplied contract and suite list\nVerification: Not run; no tests changed.",
    "blocked": "Test cases: Blocked.\nEvidence: Need the feature behavior.\nVerification: Not run; no tests changed.",
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
        prefix = VALID[profile].rsplit("Verification:", 1)[0]
        for status, changed in (
            ("Not run; no tests changed.", False),
            ("Ran: node --test; 3 tests passed", True),
            ("Ran: node --test; 1 test failed", True),
            ("Ran: node --test; exit code 1", True),
            ("Unverified: test runner unavailable", True),
        ):
            expected = changed if profile == "implement" else not changed
            try:
                validate(prefix + "Verification: " + status, profile)
            except ValueError:
                assert not expected, (profile, status, "unexpected rejection")
            else:
                assert expected, (profile, status, "unexpected acceptance")
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
    for name, report in {
        "default label in custom report": CUSTOM_BLOCKED.replace("Case set:", "Test cases:"),
        "custom blocked trailing prose": CUSTOM_BLOCKED + "\nExtra text.",
        "custom blocked wrong branch": CUSTOM_BLOCKED.replace("Blocked.", "a planned case"),
    }.items():
        try:
            validate(report, "blocked", CUSTOM_LABELS)
        except ValueError:
            continue
        raise AssertionError(f"accepted {name}")
    for status in ("Passed", "Ran: node --test test/clamp.test.js", "Ran:", "Unverified:"):
        report = VALID["implement"].rsplit("Verification:", 1)[0] + "Verification: " + status
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
