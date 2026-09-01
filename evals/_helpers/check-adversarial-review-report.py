#!/usr/bin/env python3
"""Validate the structured output emitted by the adversarial-review skill."""

from __future__ import annotations

import re
import sys

MARKERS = (
    "Verdict:",
    "Target:",
    "Intended behavior:",
    "Evidence basis:",
    "What works:",
    "Assumptions:",
    "Findings:",
    "Adversarial tests:",
    "Mitigations / acceptance criteria:",
    "Residual risk:",
)

CATEGORIES = {
    "requirements-clarity",
    "contract-logic",
    "input-handling",
    "error-rollback",
    "state-concurrency",
    "auth-tenancy",
    "data-integrity",
    "resource-lifecycle",
    "user-workflow",
    "verification-gap",
}
SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
CONFIDENCES = {"high", "medium", "low"}
CLASSIFICATIONS = {
    "Confirmed issue",
    "Likely risk",
    "Open question",
    "Accepted tradeoff",
    "Test gap",
}
FINDING_FIELDS = (
    "Artifact",
    "Category",
    "Severity",
    "Confidence",
    "Classification",
    "Trigger",
    "Risk",
    "Evidence",
    "Suggested fix",
)


class ValidationError(Exception):
    """Raised when an output does not satisfy the report contract."""


def fail(message: str) -> None:
    raise ValidationError(message)


def marker_positions(lines: list[str]) -> dict[str, int]:
    positions: dict[str, int] = {}
    for marker in MARKERS:
        matches = [index for index, line in enumerate(lines) if line.startswith(marker)]
        if len(matches) != 1:
            fail(f"expected exactly one top-level {marker!r} line, found {len(matches)}")
        positions[marker] = matches[0]
    if list(positions.values()) != sorted(positions.values()):
        fail("top-level report markers are not in canonical order")
    return positions


def require_value(line: str, marker: str) -> str:
    value = line[len(marker) :].strip()
    if not value:
        fail(f"{marker} requires a non-empty value")
    return value


def require_blank_only(lines: list[str], start: int, end: int, context: str) -> None:
    if any(line.strip() for line in lines[start:end]):
        fail(f"unexpected content {context}")


def parse_findings(lines: list[str], positions: dict[str, int]) -> bool:
    start = positions["Findings:"]
    end = positions["Adversarial tests:"]
    inline = lines[start][len("Findings:") :].strip()
    body = lines[start + 1 : end]
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()

    if inline:
        if inline != "None" or body:
            fail("inline Findings content must be exactly None with no additional entries")
        return True
    if body == ["None"]:
        return True
    if not body:
        fail("Findings must contain None or one or more complete finding records")

    index = 0
    expected_number = 1
    while index < len(body):
        title_match = re.fullmatch(r"[ \t]*(\d+)\.[ \t]+\S.*", body[index])
        if not title_match or int(title_match.group(1)) != expected_number:
            fail(f"expected finding {expected_number} title")
        index += 1

        values: dict[str, str] = {}
        for field in FINDING_FIELDS:
            if index >= len(body):
                fail(f"finding {expected_number} is missing {field}")
            match = re.fullmatch(rf"[ \t]+{re.escape(field)}:[ \t]+(.+)", body[index])
            if not match:
                fail(f"finding {expected_number} expected {field} in canonical order")
            values[field] = match.group(1).strip()
            index += 1

        if values["Category"] not in CATEGORIES:
            fail(f"finding {expected_number} has invalid Category")
        if values["Severity"] not in SEVERITIES:
            fail(f"finding {expected_number} has invalid Severity")
        if values["Confidence"] not in CONFIDENCES:
            fail(f"finding {expected_number} has invalid Confidence")
        if values["Classification"] not in CLASSIFICATIONS:
            fail(f"finding {expected_number} has invalid Classification")

        while index < len(body) and not body[index].strip():
            index += 1
        expected_number += 1

    return False


def validate() -> None:
    output = sys.stdin.read()
    if not output.strip():
        fail("grader input contains no agent output")

    lines = output.strip().splitlines()
    positions = marker_positions(lines)

    if positions["Verdict:"] != 0:
        fail("Verdict must be the first non-whitespace line")
    if positions["Residual risk:"] != len(lines) - 1:
        fail("Residual risk must be the final non-whitespace line")

    for first, second in zip(MARKERS[:6], MARKERS[1:6]):
        if positions[second] != positions[first] + 1:
            fail(f"{second} must immediately follow {first}")
    require_blank_only(
        lines,
        positions["Assumptions:"] + 1,
        positions["Findings:"],
        "between Assumptions and Findings",
    )
    require_blank_only(
        lines,
        positions["Adversarial tests:"] + 1,
        positions["Mitigations / acceptance criteria:"],
        "between Adversarial tests and Mitigations / acceptance criteria",
    )
    require_blank_only(
        lines,
        positions["Mitigations / acceptance criteria:"] + 1,
        positions["Residual risk:"],
        "between Mitigations / acceptance criteria and Residual risk",
    )

    verdict = require_value(lines[positions["Verdict:"]], "Verdict:")
    if verdict not in {"BLOCK", "CONCERNS", "CLEAN"}:
        fail("Verdict must be BLOCK, CONCERNS, or CLEAN")
    values = {
        marker: require_value(lines[positions[marker]], marker)
        for marker in MARKERS[1:6] + MARKERS[7:]
    }

    findings_are_none = parse_findings(lines, positions)
    if verdict == "CLEAN":
        if not findings_are_none:
            fail("CLEAN requires Findings: None")
        if values["Adversarial tests:"] != "None":
            fail("CLEAN requires Adversarial tests: None")
        if values["Mitigations / acceptance criteria:"] != "None":
            fail("CLEAN requires Mitigations / acceptance criteria: None")
        if values["Residual risk:"] == "None":
            fail("CLEAN requires a residual caveat or No material residual risk identified")
    elif values["Mitigations / acceptance criteria:"] == "None":
        fail("non-CLEAN reports require mitigation or acceptance-criteria content")


def main() -> None:
    reject_mode = sys.argv[1:] == ["--reject"]
    if sys.argv[1:] not in ([], ["--reject"]):
        print("usage: check-adversarial-review-report.py [--reject]", file=sys.stderr)
        raise SystemExit(2)

    try:
        validate()
    except ValidationError as error:
        if reject_mode:
            return
        print(error, file=sys.stderr)
        raise SystemExit(1) from error

    if reject_mode:
        print("output unexpectedly matches the adversarial-review report contract", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
