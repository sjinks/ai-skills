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


def headings(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if re.match(r"^#{1,6}\s+", line)]


def validate(text: str) -> None:
    actual = headings(text)
    if len(actual) != len(EXPECTED):
        raise ValueError(f"expected exactly {len(EXPECTED)} headings, found {len(actual)}")
    if not actual[0].startswith(EXPECTED[0]) or actual[0] == EXPECTED[0]:
        raise ValueError("first heading must be '# Continuation Packet: <work item>'")
    if tuple(actual[1:]) != EXPECTED[1:]:
        raise ValueError("headings must match the required labels and order exactly")


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
    mutations = (
        valid.replace("## Evidence\n", "", 1),
        valid.replace("## State\n", "## State\n- Duplicate.\n## State\n", 1),
        valid.replace(
            "## State\n- Dirty.\n## Evidence\n- Not run.",
            "## Evidence\n- Not run.\n## State\n- Dirty.",
            1,
        ),
        valid + "### Extra status\n- Not allowed.\n",
        valid.replace("## Unknowns", "## Open Questions", 1),
    )
    for mutation in mutations:
        try:
            validate(mutation)
        except ValueError:
            continue
        raise AssertionError("invalid schema mutation passed")


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return 0
    try:
        validate(sys.stdin.read())
    except ValueError as error:
        print(f"handoff schema contract failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
