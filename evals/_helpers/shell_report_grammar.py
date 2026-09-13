"""Canonical, typed grammar for shell skill report envelopes.

This module owns report field order and label validation for deterministic
preflight checks. Waza still evaluates its serialized assertions independently,
so projection checks must prove both surfaces agree.
"""

from __future__ import annotations

from dataclasses import dataclass


SCC_FIELDS = ("result", "assessment", "candidate", "authority", "next")
SCC_CANONICAL_LABELS = (
    "Construction result",
    "Construction assessment",
    "Construction candidate",
    "Execution authority",
    "Construction next step",
)


class GrammarError(ValueError):
    """Raised when an envelope cannot be represented by the SCC grammar."""


@dataclass(frozen=True)
class SCCReport:
    result: str
    assessment: str
    candidate: str
    authority: str
    next: str


def validate_labels(labels: tuple[str, str, str, str, str]) -> None:
    if len(labels) != len(SCC_FIELDS):
        raise GrammarError("SCC reports require exactly five labels")
    if not all(isinstance(label, str) for label in labels):
        raise GrammarError("SCC labels must be strings")
    normalized = tuple(label.casefold() for label in labels)
    if len(set(normalized)) != len(labels):
        raise GrammarError("SCC labels must be distinct case-insensitively")
    for label in labels:
        if not label or ":" in label or "\n" in label:
            raise GrammarError("SCC labels must be nonempty one-line colon-free text")


def render(report: SCCReport, labels: tuple[str, str, str, str, str] = SCC_CANONICAL_LABELS) -> str:
    """Serialize one unambiguous one-line SCC envelope."""

    validate_labels(labels)
    values = (report.result, report.assessment, report.candidate, report.authority, report.next)
    if not all(isinstance(value, str) for value in values):
        raise GrammarError("SCC field values must be strings")
    if any(not value or any(separator in value for separator in "\n\r\v\f\x1c\x1d\x1e\x85") for value in values):
        raise GrammarError("render() accepts nonempty one-line field values only")
    return "\n".join(f"{label}: {value}" for label, value in zip(labels, values, strict=True))


def parse(output: str, labels: tuple[str, str, str, str, str] = SCC_CANONICAL_LABELS) -> SCCReport:
    """Parse exactly one one-line SCC envelope with a caller-selected label map."""

    validate_labels(labels)
    lines = output.splitlines()
    if len(lines) != len(labels):
        raise GrammarError("SCC envelope has an unexpected field count")
    values: list[str] = []
    for label, line in zip(labels, lines, strict=True):
        prefix = f"{label}: "
        if not line.startswith(prefix):
            raise GrammarError("SCC envelope has an unexpected label or field order")
        value = line.removeprefix(prefix)
        if not value:
            raise GrammarError("SCC envelope field values must be nonempty")
        values.append(value)
    return SCCReport(*values)
