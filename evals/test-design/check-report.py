#!/usr/bin/env python3
"""Validate the test-design report grammar without a model call."""

import argparse
import json
import re
import sys

MARKERS = ("Designed cases:", "Design evidence:", "Test execution:")
PROFILES = {"plan", "implement", "assessment", "blocked"}
IMPLEMENT_STATUS_PATTERN = r"(?:Unverified: \S[^\n]*|Ran: \S(?:[^\n]*\S)? => (?:passed|failed|exit -?\d+))"


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Decode an object without silently accepting repeated case fields.

    The counted-case representation requires each field exactly once.
    """
    if len(pairs) != len({key for key, _ in pairs}):
        raise ValueError("duplicate case field")
    return dict(pairs)


def parse_args(arguments: list[str]) -> argparse.Namespace:
    """Parse the shared validator CLI used by tasks and projection checks.

    Case count is optional; ordinary reports retain their existing body format.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", choices=sorted(PROFILES))
    parser.add_argument("labels", nargs="*")
    parser.add_argument("--case-count", type=int)
    return parser.parse_args(arguments)


def validate(
    report: str,
    profile: str,
    labels: tuple[str, str, str] = MARKERS,
    case_count: int | None = None,
) -> None:
    """Check label order, required content, branch, and terminal status."""
    if profile not in PROFILES:
        raise ValueError("invalid profile")
    if case_count is not None and (type(case_count) is not int or case_count < 1 or profile == "blocked"):
        raise ValueError("case count must be positive and requires a nonblocked profile")
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
    if case_count is not None:
        selected = json.loads(cases, object_pairs_hook=unique_object)
        if not isinstance(selected, list) or len(selected) != case_count:
            raise ValueError("cases must be a JSON array with the requested count")
        for case in selected:
            if not isinstance(case, dict) or set(case) != {"behavior", "expected", "defect"}:
                raise ValueError("each case requires exactly behavior, expected, and defect")
            if any(not isinstance(value, str) or not value.strip() for value in case.values()):
                raise ValueError("case fields must be nonempty strings")
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
SINGLE_CASE = [{"behavior": "invalid middle row", "expected": "reports the offending row; zero rows persisted", "defect": "partial commit instead of atomic rollback"}]
SINGLE_ASSESSMENT = "Designed cases: " + json.dumps(SINGLE_CASE) + "\nDesign evidence: supplied contract; retain required 90% coverage gate; retry decision missing\nTest execution: Not run; no tests changed."
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
    validate(SINGLE_ASSESSMENT, "assessment", case_count=1)
    validate(SINGLE_ASSESSMENT.replace(json.dumps(SINGLE_CASE), json.dumps([dict(reversed(list(SINGLE_CASE[0].items())))], indent=2)), "assessment", case_count=1)
    validate(SINGLE_ASSESSMENT.replace("Designed cases:", "Case set:").replace("Design evidence:", "Design basis:").replace("Test execution:", "Run record:"), "assessment", CUSTOM_LABELS, case_count=1)
    validate(SINGLE_ASSESSMENT.replace(json.dumps(SINGLE_CASE), json.dumps(SINGLE_CASE * 2)), "assessment", case_count=2)
    validate(SINGLE_ASSESSMENT.replace(json.dumps(SINGLE_CASE), json.dumps(SINGLE_CASE * 2)), "assessment")
    for name, body in {
        "zero cases": "[]",
        "two cases": json.dumps(SINGLE_CASE * 2),
        "object instead of array": json.dumps(SINGLE_CASE[0]),
        "prose instead of array": "one invalid row case",
        "code fence instead of raw array": "```json\n" + json.dumps(SINGLE_CASE) + "\n```",
        "extra case field": json.dumps([dict(SINGLE_CASE[0], priority="high")]),
        "missing case field": json.dumps([{"behavior": "invalid row", "expected": "zero persisted"}]),
        "wrong field type": json.dumps([dict(SINGLE_CASE[0], expected=["zero persisted"])]),
        "empty field": json.dumps([dict(SINGLE_CASE[0], defect=" ")]),
        "duplicate JSON key": '[{"behavior":"first","behavior":"second","expected":"zero","defect":"commit"}]',
        "trailing case prose": json.dumps(SINGLE_CASE) + "\nAnother invalid row case.",
    }.items():
        candidate = SINGLE_ASSESSMENT.replace(json.dumps(SINGLE_CASE), body)
        try:
            validate(candidate, "assessment", case_count=1)
        except ValueError:
            continue
        raise AssertionError(f"accepted counted case mutation: {name}")
    for count in (0, -1, True):
        try:
            validate(SINGLE_ASSESSMENT, "assessment", case_count=count)
        except ValueError:
            continue
        raise AssertionError(f"accepted invalid case count: {count}")
    try:
        validate(VALID["blocked"], "blocked", case_count=1)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted blocked/count crossover")
    for profile, base_report in VALID.items():
        for labels in (MARKERS, CUSTOM_LABELS):
            candidate = base_report
            for marker, label in zip(MARKERS, labels):
                candidate = candidate.replace(marker, label)
            candidate = candidate.replace(labels[2] + " ", labels[2] + " Final line: ")
            try:
                validate(candidate, profile, labels)
            except ValueError:
                continue
            raise AssertionError(f"accepted explanatory prefix: {profile}, {labels}")
    base = VALID["plan"]
    invalid = {
        "preamble": "Here is the report.\n" + base,
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
    args = parse_args(sys.argv[1:])
    try:
        labels = tuple(args.labels) if args.labels else MARKERS
        validate(sys.stdin.read(), args.profile, labels, args.case_count)
    except ValueError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
