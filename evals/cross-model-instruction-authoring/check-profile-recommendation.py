#!/usr/bin/env python3
"""Validate the Profile Recommendation output contract."""

from __future__ import annotations

import sys


HEADINGS = (
    "Profile recommendation:",
    "Justified behavioral patches:",
    "Evidence still needed:",
)
PROFILES = {
    "fast-general",
    "strong-general",
    "deep-reasoning",
    "coding-agent",
    "specialized-classifier",
}


class ValidationError(ValueError):
    """Raised when the profile recommendation violates its grammar."""


def validate(
    text: str,
    expected_profile: str | None = None,
    expected_no_patches: bool = False,
) -> None:
    lines = text.splitlines()
    headings = [
        (index, line)
        for index, line in enumerate(lines)
        if line in HEADINGS
    ]
    if tuple(line for _, line in headings) != HEADINGS:
        raise ValidationError("headings must occur exactly once and in order")
    if any(line.strip() for line in lines[: headings[0][0]]):
        raise ValidationError("content must begin with 'Profile recommendation:'")
    bodies = []
    for offset, (start, _) in enumerate(headings):
        end = headings[offset + 1][0] if offset + 1 < len(headings) else len(lines)
        body = [line for line in lines[start + 1 : end] if line]
        if not body:
            raise ValidationError("every heading requires a body")
        bodies.append(body)
    if len(bodies[0]) != 1 or not bodies[0][0].startswith("- "):
        raise ValidationError("profile must be exactly one bullet")
    profile = bodies[0][0][2:]
    if profile not in PROFILES:
        raise ValidationError("profile must be a capability-profile identifier")
    if expected_profile is not None and profile != expected_profile:
        raise ValidationError(f"profile must be exactly '{expected_profile}'")
    if not all(line.startswith("- ") for line in bodies[1]):
        raise ValidationError("patches must use bullets or '- None.'")
    if expected_no_patches and bodies[1] != ["- None."]:
        raise ValidationError("patches must be exactly '- None.'")
    if not all(line.startswith("- ") for line in bodies[2]):
        raise ValidationError("evidence must use bullets")


def rejected(
    text: str,
    expected_profile: str | None = None,
    expected_no_patches: bool = False,
) -> None:
    try:
        validate(text, expected_profile, expected_no_patches)
    except ValidationError:
        return
    raise AssertionError("invalid recommendation passed")


def self_test() -> None:
    def recommendation(profile: str) -> str:
        return f"""Profile recommendation:
- {profile}
Justified behavioral patches:
- None.
Evidence still needed:
- Run a representative evaluation before adding a patch.
"""

    valid = recommendation("coding-agent")
    validate(valid)
    for profile in PROFILES:
        validate(recommendation(profile))
    validate(valid, "coding-agent", True)
    rejected(valid.replace("- coding-agent\n", "", 1))
    rejected(valid.replace("Profile recommendation:", "Evidence still needed:", 1))
    rejected(valid.replace("Justified behavioral patches:", "Profile recommendation:", 1))
    rejected(valid.replace("- coding-agent\n", "- coding-agent\nProfile recommendation:\n- coding-agent\n", 1))
    rejected(valid.replace("- coding-agent", "- unsupported-profile", 1))
    rejected(valid, "fast-general", True)
    rejected(valid.replace("- None.", "not-a-bullet", 1))
    rejected(valid.replace("- None.", "- bounded-exploration", 1), "coding-agent", True)
    rejected(valid + "Unscoped trailing prose.\n")
    rejected("Preamble.\n" + valid)
    validate(valid.replace(
        "- Run a representative evaluation before adding a patch.",
        "- Reproduce the observed failure:",
    ))


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return 0
    expected_profile = None
    expected_no_patches = False
    arguments = iter(sys.argv[1:])
    for argument in arguments:
        if argument == "--expected-profile":
            expected_profile = next(arguments, None)
            if expected_profile not in PROFILES:
                print("unknown expected profile", file=sys.stderr)
                return 2
        elif argument == "--expected-no-patches":
            expected_no_patches = True
        else:
            print(
                "usage: check-profile-recommendation.py "
                "[--expected-profile PROFILE] [--expected-no-patches]",
                file=sys.stderr,
            )
            return 2
    try:
        validate(sys.stdin.read(), expected_profile, expected_no_patches)
    except ValidationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
