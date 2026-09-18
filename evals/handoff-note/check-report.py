#!/usr/bin/env python3
"""Validate exact caller-schema output for handoff-note edge tasks 009, 010, and 013.

Waza passes raw output on stdin. Each profile validates its heading grammar,
section-local required content, allowed value domains, and termination.
"""

from __future__ import annotations

import re
import sys


PACKET_HEADINGS = (
    "# Continuation Packet:",
    "## Objective",
    "## State",
    "## Evidence",
    "## Risks and Constraints",
    "## Actions",
    "## Unknowns",
)
AUDIT_UPDATE_HEADINGS = (
    "# Review:",
    "## Findings",
    "## Corrections",
    "## Ready",
    "# Continuation:",
    "## Objective",
    "## State",
    "## Evidence",
    "## Risks",
    "## Actions",
    "## Unknowns",
)
AUDIT_HEADINGS = (
    "# Review:",
    "## Findings",
    "## Corrections",
    "## Ready",
)


class ValidationError(ValueError):
    """Raised when output does not satisfy its caller-required schema."""


def heading_positions(lines: list[str]) -> list[tuple[int, str]]:
    return [
        (index, line.strip())
        for index, line in enumerate(lines)
        if re.match(r"^#{1,6}\s+", line)
    ]


def require_heading_layout(
    lines: list[str], expected: tuple[str, ...], first_pattern: str, profile: str
) -> list[tuple[int, str]]:
    positions = heading_positions(lines)
    actual = tuple(heading for _, heading in positions)
    if not lines or not re.fullmatch(first_pattern, lines[0].strip()):
        raise ValidationError(f"{profile} must start with {expected[0]!r} plus a work item")
    if len(actual) != len(expected):
        raise ValidationError(f"{profile} expected exactly {len(expected)} headings, found {len(actual)}")
    if not re.fullmatch(first_pattern, actual[0]):
        raise ValidationError(f"{profile} first heading is invalid")
    for index, marker in enumerate(expected[1:], start=1):
        if marker.startswith("# "):
            if not re.fullmatch(r"# Continuation: \S(?:.*\S)?", actual[index]):
                raise ValidationError("continuation heading is invalid")
        elif actual[index] != marker:
            raise ValidationError(f"{profile} expected heading {marker!r} at position {index + 1}")
    return positions


def section_bodies(lines: list[str], positions: list[tuple[int, str]]) -> dict[str, list[str]]:
    bodies: dict[str, list[str]] = {}
    for offset, (start, heading) in enumerate(positions):
        end = positions[offset + 1][0] if offset + 1 < len(positions) else len(lines)
        bodies[heading] = [line.strip() for line in lines[start + 1 : end] if line.strip()]
    return bodies


def require_nonempty(bodies: dict[str, list[str]], headings: tuple[str, ...]) -> None:
    for heading in headings:
        if not bodies.get(heading):
            raise ValidationError(f"{heading} requires a nonempty body")


def require_match(body: list[str], pattern: str, heading: str) -> None:
    if not re.search(pattern, "\n".join(body), flags=re.IGNORECASE | re.DOTALL):
        raise ValidationError(f"{heading} is missing required task content")


def validate_unknowns(body: list[str]) -> None:
    if body and all(entry.startswith("- ") for entry in body):
        return
    if body == ["unknown"]:
        return
    if len(body) == 1 and re.fullmatch(r"Unknown: \S.*", body[0]):
        return
    raise ValidationError(
        "Unknowns must contain bullets, 'unknown', or 'Unknown: <missing obligation>'"
    )


def validate_ready(body: list[str], required_value: str | None = None) -> None:
    if len(body) != 1:
        raise ValidationError("Ready must contain exactly one entry")
    match = re.fullmatch(r"- (yes|no), \S.*", body[0], flags=re.IGNORECASE)
    if not match:
        raise ValidationError("Ready must contain exactly '- yes|no, <reason>'")
    if required_value and match.group(1).lower() != required_value:
        raise ValidationError(f"Ready must be {required_value!r} for this task")


def validate_packet(text: str) -> None:
    lines = text.splitlines()
    positions = require_heading_layout(
        lines, PACKET_HEADINGS, r"# Continuation Packet: \S(?:.*\S)?", "continuation packet"
    )
    bodies = section_bodies(lines, positions)
    require_nonempty(bodies, PACKET_HEADINGS[1:])
    require_match(bodies["## State"], r"uncommitted|unpushed", "## State")
    require_match(bodies["## State"], r"patch|transfer|unavailable", "## State")
    require_match(
        bodies["## Evidence"],
        r"(?:not run.{0,300}(?:focused test|test)|(?:focused test|test).{0,300}not run|user-stated)",
        "## Evidence",
    )
    require_match(bodies["## Risks and Constraints"], r"five|duplicate charges", "## Risks and Constraints")
    require_match(bodies["## Risks and Constraints"], r"do not repeat|avoid", "## Risks and Constraints")
    require_match(bodies["## Risks and Constraints"], r"payment-capture", "## Risks and Constraints")
    if not re.match(r"1\. .*?(?:transfer|patch|share|push|recreate)", bodies["## Actions"][0], re.I):
        raise ValidationError("first Actions entry must transfer the local change")
    require_match(bodies["## Actions"], r"idempotency test", "## Actions")
    validate_unknowns(bodies["## Unknowns"])


def validate_audit_update(text: str) -> None:
    lines = text.splitlines()
    positions = require_heading_layout(
        lines, AUDIT_UPDATE_HEADINGS, r"# Review: \S(?:.*\S)?", "audit-update"
    )
    bodies = section_bodies(lines, positions)
    require_nonempty(bodies, AUDIT_UPDATE_HEADINGS[1:4] + AUDIT_UPDATE_HEADINGS[5:])
    require_match(bodies["## Findings"], r"missing|lacks|no validation", "## Findings")
    require_match(bodies["## Corrections"], r"add|record", "## Corrections")
    require_match(bodies["## Corrections"], r"validation|evidence", "## Corrections")
    validate_ready(bodies["## Ready"], required_value="no")
    require_match(
        bodies["## Evidence"], r"not run.{0,300}(?:focused test|test)|(?:focused test|test).{0,300}not run", "## Evidence"
    )
    require_match(bodies["## Risks"], r"five|duplicate charges", "## Risks")
    require_match(bodies["## Risks"], r"do not repeat|avoid", "## Risks")
    require_match(bodies["## Risks"], r"payment-capture", "## Risks")
    require_match(bodies["## Actions"], r"idempotency test", "## Actions")
    validate_unknowns(bodies["## Unknowns"])


def validate_audit_only(text: str) -> None:
    lines = text.splitlines()
    positions = require_heading_layout(lines, AUDIT_HEADINGS, r"# Review: \S(?:.*\S)?", "audit-only")
    bodies = section_bodies(lines, positions)
    require_nonempty(bodies, AUDIT_HEADINGS[1:])
    require_match(bodies["## Findings"], r"missing|lacks|no validation", "## Findings")
    require_match(bodies["## Corrections"], r"add|record", "## Corrections")
    require_match(bodies["## Corrections"], r"validation|evidence", "## Corrections")
    validate_ready(bodies["## Ready"], required_value="no")


def swap_heading_lines(text: str, first: str, second: str) -> str:
    """Return a report with two headings out of order, preserving their bodies."""
    lines = text.splitlines(keepends=True)
    first_index = next(index for index, line in enumerate(lines) if line.strip() == first)
    second_index = next(index for index, line in enumerate(lines) if line.strip() == second)
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    return "".join(lines)


def duplicate_heading(text: str, heading: str) -> str:
    """Insert a second heading, which exact-layout validation must reject."""
    return text.replace(heading + "\n", heading + "\n- Duplicate section.\n" + heading + "\n", 1)


def replace_heading(text: str, heading: str) -> str:
    """Create an invalid heading without changing the number of headings."""
    return text.replace(heading, "## Invalid Heading", 1)


def omit_body(text: str, heading: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    end = next(
        (index for index in range(start + 1, len(lines)) if re.match(r"^#{1,6}\s+", lines[index])),
        len(lines),
    )
    return "".join(lines[: start + 1] + lines[end:])


def assert_rejected(validator, text: str) -> None:
    try:
        validator(text)
    except ValidationError:
        return
    raise AssertionError("invalid report passed")


def self_test() -> None:
    packet = """# Continuation Packet: retry fix
## Objective
- Finish it.
## State
- Uncommitted local retry edits need transfer by patch.
## Evidence
- Focused test: not run after the latest edit.
## Risks and Constraints
- Raising retries to five caused duplicate charges; do not repeat it. Do not change payment-capture behavior.
## Actions
1. Export a patch before validation.
2. Add an idempotency test.
## Unknowns
- None.
"""
    audit_update = """# Review: retry fix
## Findings
- Missing validation status.
## Corrections
1. Add the missing validation evidence.
## Ready
- No, validation status is missing.
# Continuation: retry fix
## Objective
- Finish it.
## State
- Branch: fix/checkout-retry.
## Evidence
- Focused test: not run after the latest edit.
## Risks
- Raising retries to five caused duplicate charges; do not repeat it. Do not change payment-capture behavior.
## Actions
1. Add an idempotency test.
## Unknowns
- None.
"""
    audit_only = """# Review: retry fix
## Findings
- Missing validation status.
## Corrections
1. Add the missing validation evidence.
## Ready
- No, validation status is missing.
"""
    validate_packet(packet)
    validate_audit_update(audit_update)
    validate_audit_only(audit_only)

    for validator, fixture in ((validate_packet, packet), (validate_audit_update, audit_update)):
        for sentinel in ("unknown", "Unknown: missing obligation"):
            validator(fixture.replace("- None.", sentinel, 1))
    for fixture, validator, headings in (
        (packet, validate_packet, PACKET_HEADINGS[1:]),
        (audit_update, validate_audit_update, AUDIT_UPDATE_HEADINGS[1:4] + AUDIT_UPDATE_HEADINGS[5:]),
        (audit_only, validate_audit_only, AUDIT_HEADINGS[1:]),
    ):
        for heading in headings:
            assert_rejected(validator, omit_body(fixture, heading))
        assert_rejected(validator, swap_heading_lines(fixture, headings[0], headings[1]))
        assert_rejected(validator, duplicate_heading(fixture, headings[0]))
        assert_rejected(validator, replace_heading(fixture, headings[0]))

    # Packet Unknowns has a constrained sentinel domain; audit Ready has yes/no.
    assert_rejected(validate_packet, packet.replace("- None.", "Known", 1))
    assert_rejected(validate_audit_update, audit_update.replace("- No,", "- Maybe,"))
    assert_rejected(validate_audit_only, audit_only.replace("- No,", "- Maybe,"))
    assert_rejected(validate_packet, packet + "Unscoped epilogue.\n")
    assert_rejected(validate_audit_update, audit_update + "Unscoped epilogue.\n")
    assert_rejected(validate_audit_only, audit_only + "Unscoped epilogue.\n")
    assert_rejected(validate_packet, audit_update)
    assert_rejected(validate_audit_update, packet)
    assert_rejected(validate_audit_only, audit_update)
    assert_rejected(validate_audit_update, audit_only)
    assert_rejected(validate_audit_only, audit_only.replace("- No,", "- Maybe,"))
    assert_rejected(validate_audit_only, audit_only.replace("- No, validation status is missing.", "- No."))


def main() -> int:
    args = sys.argv[1:]
    if args == ["--self-test"]:
        self_test()
        return 0
    validators = {
        (): validate_packet,
        ("--audit-update",): validate_audit_update,
        ("--audit-only",): validate_audit_only,
    }
    validator = validators.get(tuple(args))
    if validator is None:
        print("usage: check-report.py [--audit-update | --audit-only | --self-test]", file=sys.stderr)
        return 2
    try:
        validator(sys.stdin.read())
    except ValidationError as error:
        print(f"handoff schema contract failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
