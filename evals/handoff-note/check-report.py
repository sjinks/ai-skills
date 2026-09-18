#!/usr/bin/env python3
"""Validate the exact caller-required schema in handoff-note edge case 009.

Waza sends the raw response on stdin. This checker intentionally covers only
the custom-schema task: ordinary handoffs may use the default schema.
"""

from __future__ import annotations

import re
import sys


EXPECTED = (
    "# Continuation Packet:",
    "## Objective",
    "## State",
    "## Evidence",
    "## Risks and Constraints",
    "## Actions",
    "## Unknowns",
)
AUDIT_UPDATE_EXPECTED = (
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


def headings(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if re.match(r"^#{1,6}\s+", line)]


def heading_positions(lines: list[str]) -> list[tuple[int, str]]:
    return [
        (index, line.strip())
        for index, line in enumerate(lines)
        if re.match(r"^#{1,6}\s+", line)
    ]


def require_nonempty_sections(lines: list[str], positions: list[tuple[int, str]]) -> None:
    for offset, (start, heading) in enumerate(positions):
        end = positions[offset + 1][0] if offset + 1 < len(positions) else len(lines)
        if not any(line.strip() for line in lines[start + 1 : end]):
            raise ValueError(f"{heading} requires a nonempty body")


def omit_section_body(text: str, heading: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if re.match(r"^#{1,6}\s+", lines[index])
        ),
        len(lines),
    )
    return "".join(lines[: start + 1] + lines[end:])


def validate(text: str) -> None:
    if not re.match(r"\A# Continuation Packet: \S(?:.*\S)?\n", text):
        raise ValueError("output must start with '# Continuation Packet: <work item>'")
    actual = headings(text)
    if len(actual) != len(EXPECTED):
        raise ValueError(f"expected exactly {len(EXPECTED)} headings, found {len(actual)}")
    if not re.fullmatch(r"# Continuation Packet: \S(?:.*\S)?", actual[0]):
        raise ValueError("first heading must be '# Continuation Packet: <work item>'")
    if tuple(actual[1:]) != EXPECTED[1:]:
        raise ValueError("headings must match the required labels and order exactly")
    lines = text.splitlines()
    positions = heading_positions(lines)
    require_nonempty_sections(lines, positions[1:])
    unknowns = lines[lines.index("## Unknowns") + 1 :]
    if any(line.strip() and not line.startswith("- ") for line in unknowns):
        raise ValueError("Unknowns may contain only bullet entries; trailing prose is not allowed")


def validate_audit_update(text: str) -> None:
    if not re.match(r"\A# Review: \S(?:.*\S)?\n", text):
        raise ValueError("output must start with '# Review: <work item>'")
    actual = headings(text)
    if len(actual) != len(AUDIT_UPDATE_EXPECTED):
        raise ValueError(
            f"expected exactly {len(AUDIT_UPDATE_EXPECTED)} headings, found {len(actual)}"
        )
    if not re.fullmatch(r"# Review: \S(?:.*\S)?", actual[0]):
        raise ValueError("first heading must be '# Review: <work item>'")
    if tuple(actual[1:4]) != AUDIT_UPDATE_EXPECTED[1:4]:
        raise ValueError("review headings must match the required labels and order exactly")
    if not re.fullmatch(r"# Continuation: \S(?:.*\S)?", actual[4]):
        raise ValueError("continuation heading must be '# Continuation: <work item>'")
    if tuple(actual[5:]) != AUDIT_UPDATE_EXPECTED[5:]:
        raise ValueError("handoff headings must match the required labels and order exactly")
    lines = text.splitlines()
    positions = heading_positions(lines)
    require_nonempty_sections(lines, positions[1:4] + positions[5:])
    continuation_index = next(
        index for index, line in enumerate(lines) if line.startswith("# Continuation: ")
    )
    ready = lines[lines.index("## Ready") + 1 : continuation_index]
    ready_entries = [line.strip() for line in ready if line.strip()]
    if len(ready_entries) != 1 or not re.fullmatch(
        r"- (?:yes|no), \S.*", ready_entries[0], flags=re.IGNORECASE
    ):
        raise ValueError("Ready must contain exactly '- yes|no, <reason>'")
    unknowns = lines[lines.index("## Unknowns") + 1 :]
    if any(line.strip() and not line.startswith("- ") for line in unknowns):
        raise ValueError("Unknowns may contain only bullet entries; trailing prose is not allowed")


def self_test() -> None:
    valid = """# Continuation Packet: retry fix
## Objective
- Finish it.
## State
- Dirty.
## Evidence
- Not run.
## Risks and Constraints
- Do not change capture.
## Actions
1. Export a patch.
## Unknowns
- None.
"""
    validate(valid)
    mutations = [
        valid.replace("## Evidence\n", "", 1),
        valid.replace("## State\n", "## State\n- Duplicate.\n## State\n", 1),
        valid.replace(
            "## State\n- Dirty.\n## Evidence\n- Not run.",
            "## Evidence\n- Not run.\n## State\n- Dirty.",
            1,
        ),
        valid + "### Extra status\n- Not allowed.\n",
        valid.replace("## Unknowns", "## Open Questions", 1),
        valid.replace("# Continuation Packet: retry fix", "# Continuation Packet:retry fix", 1),
        valid.replace("# Continuation Packet: retry fix", "# Continuation Packet:", 1),
        "Preamble\n" + valid,
        valid + "Unscoped epilogue.\n",
    ]
    mutations.extend(omit_section_body(valid, heading) for heading in EXPECTED[1:])
    for mutation in mutations:
        try:
            validate(mutation)
        except ValueError:
            continue
        raise AssertionError("invalid schema mutation passed")

    audit_update = """# Review: retry fix
## Findings
- Missing validation status.
## Corrections
1. Add the missing evidence.
## Ready
- No, validation status is missing.
# Continuation: retry fix
## Objective
- Finish it.
## State
- Dirty.
## Evidence
- Not run.
## Risks
- Do not change capture.
## Actions
1. Add a test.
## Unknowns
- None.
"""
    validate_audit_update(audit_update)
    audit_mutations = [
        audit_update.replace("## Corrections\n", "", 1),
        audit_update.replace("# Continuation: retry fix", "# Continuation:retry fix", 1),
        audit_update.replace("## Findings\n", "## Ready\n", 1),
        audit_update + "### Extra status\n- Not allowed.\n",
        "Preamble\n" + audit_update,
        audit_update + "Unscoped epilogue.\n",
        audit_update.replace(
            "- No, validation status is missing.",
            "- Maybe, validation status is missing.",
            1,
        ),
        audit_update.replace("- No, validation status is missing.", "- No.", 1),
        audit_update.replace(
            "- No, validation status is missing.",
            "- No, validation status is missing.\n- No, another reason.",
            1,
        ),
    ]
    audit_mutations.extend(
        omit_section_body(audit_update, heading)
        for heading in AUDIT_UPDATE_EXPECTED[1:4] + AUDIT_UPDATE_EXPECTED[5:]
    )
    for mutation in audit_mutations:
        try:
            validate_audit_update(mutation)
        except ValueError:
            continue
        raise AssertionError("invalid audit-update schema mutation passed")

    for validator, other_fixture in ((validate, audit_update), (validate_audit_update, valid)):
        try:
            validator(other_fixture)
        except ValueError:
            continue
        raise AssertionError("profile crossover passed")


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return 0
    if sys.argv[1:] == ["--audit-update"]:
        validator = validate_audit_update
    elif not sys.argv[1:]:
        validator = validate
    else:
        print("usage: check-report.py [--audit-update | --self-test]", file=sys.stderr)
        return 2
    try:
        validator(sys.stdin.read())
    except ValueError as error:
        print(f"handoff schema contract failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
