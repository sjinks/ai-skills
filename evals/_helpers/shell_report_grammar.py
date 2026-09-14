"""Canonical, typed grammar for shell skill report envelopes.

This module owns report field order and label validation for deterministic
preflight checks. Waza still evaluates its serialized assertions independently,
so projection checks must prove both surfaces agree.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


SCC_FIELDS = ("result", "assessment", "candidate", "authority", "next")
SCC_CANONICAL_LABELS = (
    "Construction result",
    "Construction assessment",
    "Construction candidate",
    "Execution authority",
    "Construction next step",
)
LINE_SEPARATORS = "\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029"
CUSTOM_LABEL = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9 ]*[A-Za-z0-9])?\Z")
RESULTS = frozenset(("VALID", "REWRITE", "BLOCKED"))
AUTHORITY = "NOT ASSESSED BY THIS SKILL"


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
    if labels == SCC_CANONICAL_LABELS:
        return
    canonical = tuple(label.casefold() for label in SCC_CANONICAL_LABELS)
    if any(label in canonical for label in normalized):
        raise GrammarError("custom SCC labels must not collide with canonical labels")
    for label in labels:
        if CUSTOM_LABEL.fullmatch(label) is None:
            raise GrammarError("custom SCC labels must use ASCII letters, digits, and internal spaces")


def validate_report(report: SCCReport) -> None:
    """Validate the inline SCC semantic fields shared by rendering and parsing."""

    values = (report.result, report.assessment, report.candidate, report.authority, report.next)
    if not all(isinstance(value, str) for value in values):
        raise GrammarError("SCC field values must be strings")
    if any("\x00" in value or any(separator in value for separator in LINE_SEPARATORS) for value in values):
        raise GrammarError("SCC field values must not contain NUL or line separators")
    if report.result not in RESULTS:
        raise GrammarError("SCC result must be VALID, REWRITE, or BLOCKED")
    if not report.assessment.strip() or not report.next.strip():
        raise GrammarError("SCC assessment and next step must contain non-whitespace text")
    if report.authority != AUTHORITY:
        raise GrammarError("SCC authority must use the exact not-assessed literal")
    if report.result == "BLOCKED":
        if report.candidate != "Not provided":
            raise GrammarError("BLOCKED SCC reports must use the Not provided candidate")
    elif not report.candidate.strip() or report.candidate == "Not provided" or report.candidate.strip() == "|":
        raise GrammarError("VALID and REWRITE SCC reports require a nonempty inline candidate")


def render(report: SCCReport, labels: tuple[str, str, str, str, str] = SCC_CANONICAL_LABELS) -> str:
    """Serialize one unambiguous one-line SCC envelope."""

    validate_labels(labels)
    validate_report(report)
    values = (report.result, report.assessment, report.candidate, report.authority, report.next)
    return "\n".join(f"{label}: {value}" for label, value in zip(labels, values))


def parse(output: str, labels: tuple[str, str, str, str, str] = SCC_CANONICAL_LABELS) -> SCCReport:
    """Parse exactly one one-line SCC envelope with a caller-selected label map."""

    validate_labels(labels)
    if not isinstance(output, str):
        raise GrammarError("SCC envelope must be a string")
    if any(separator in output for separator in LINE_SEPARATORS if separator != "\n"):
        raise GrammarError("SCC envelope fields must be separated by LF only")
    if output.endswith("\n"):
        output = output[:-1]
    lines = output.split("\n")
    if len(lines) != len(labels):
        raise GrammarError("SCC envelope has an unexpected field count")
    values: list[str] = []
    for label, line in zip(labels, lines):
        prefix = f"{label}: "
        if not line.startswith(prefix):
            raise GrammarError("SCC envelope has an unexpected label or field order")
        value = line.removeprefix(prefix)
        if not value:
            raise GrammarError("SCC envelope field values must be nonempty")
        values.append(value)
    report = SCCReport(*values)
    validate_report(report)
    return report
