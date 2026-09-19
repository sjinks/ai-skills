#!/usr/bin/env python3
"""Validate the standard cross-model-authoring output wrapper."""

from __future__ import annotations

import sys


LABELS = (
    "Finished artifact:",
    "Material assumptions:",
    "Runtime adapter:",
    "Compatibility note:",
)


class ValidationError(ValueError):
    """Raised when the standard wrapper violates its grammar."""


def validate(text: str) -> None:
    lines = text.splitlines()
    label_positions = [
        (index, line) for index, line in enumerate(lines) if line in LABELS
    ]
    if tuple(line for _, line in label_positions) != LABELS:
        raise ValidationError("labels must occur exactly once and in order")
    if any(line.strip() for line in lines[: label_positions[0][0]]):
        raise ValidationError("content must begin with 'Finished artifact:'")

    bodies: list[list[str]] = []
    for offset, (start, _) in enumerate(label_positions):
        end = label_positions[offset + 1][0] if offset + 1 < len(label_positions) else len(lines)
        body = [line for line in lines[start + 1 : end] if line.strip()]
        if not body:
            raise ValidationError("every label requires a nonempty body")
        bodies.append(body)

    if len(bodies[-1]) != 1:
        raise ValidationError("compatibility note must be one line and terminate the response")


def rejected(text: str) -> None:
    try:
        validate(text)
    except ValidationError:
        return
    raise AssertionError("invalid standard output passed")


def self_test() -> None:
    valid = """Finished artifact:
Use the checked artifact.
Material assumptions:
None.
Runtime adapter:
None.
Compatibility note:
None known; evaluation is still required.
"""
    validate(valid)
    rejected(valid.replace("Finished artifact:\n", "", 1))
    rejected(valid.replace("Material assumptions:", "Compatibility note:", 1))
    rejected(valid.replace(
        "Material assumptions:\n",
        "Material assumptions:\nNone.\nMaterial assumptions:\n",
        1,
    ))
    rejected("Preamble.\n" + valid)
    rejected(valid + "Trailing prose.\n")


def main() -> int:
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return 0
    try:
        validate(sys.stdin.read())
    except ValidationError as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
