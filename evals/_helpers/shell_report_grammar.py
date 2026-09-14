"""Canonical, typed grammar for shell skill report envelopes.

This module owns report field order and validation for deterministic preflight
checks. Waza still evaluates its serialized assertions independently, so
projection checks must prove both surfaces agree.
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
    """Validate SCC semantic fields shared by rendering and parsing."""

    values = (report.result, report.assessment, report.candidate, report.authority, report.next)
    if not all(isinstance(value, str) for value in values):
        raise GrammarError("SCC field values must be strings")
    if any("\x00" in value for value in values):
        raise GrammarError("SCC field values must not contain NUL")
    if any(any(separator in value for separator in LINE_SEPARATORS) for value in (report.result, report.assessment, report.authority, report.next)):
        raise GrammarError("SCC result, assessment, authority, and next step must be one line")
    if any(separator in report.candidate for separator in LINE_SEPARATORS if separator != "\n"):
        raise GrammarError("SCC candidate must use LF for multiline serialization")
    if report.result not in RESULTS:
        raise GrammarError("SCC result must be VALID, REWRITE, or BLOCKED")
    if not report.assessment.strip() or not report.next.strip():
        raise GrammarError("SCC assessment and next step must contain non-whitespace text")
    if report.authority != AUTHORITY:
        raise GrammarError("SCC authority must use the exact not-assessed literal")
    if report.result == "BLOCKED":
        if report.candidate != "Not provided":
            raise GrammarError("BLOCKED SCC reports must use the Not provided candidate")
    elif not report.candidate.strip():
        raise GrammarError("VALID and REWRITE SCC reports require a nonempty candidate")


def _is_multiline_candidate(report: SCCReport) -> bool:
    if report.result == "BLOCKED":
        return False
    stripped = report.candidate.lstrip()
    return "\n" in report.candidate or report.candidate == "Not provided" or (
        stripped.startswith("|") and not stripped[1:].strip()
    )


def _field_value(line: str, label: str, *, compact: bool = False, canonical: bool = False) -> str:
    prefix = f"{label}: " if canonical else f"{label}:"
    if not line.startswith(prefix):
        raise GrammarError("SCC envelope has an unexpected label or field order")
    value = line.removeprefix(prefix)
    if canonical:
        return value
    if compact:
        return value.lstrip(" \t")
    if value.startswith(" "):
        return value[1:]
    return value.lstrip("\t")


def render(report: SCCReport, labels: tuple[str, str, str, str, str] = SCC_CANONICAL_LABELS) -> str:
    """Serialize one unambiguous SCC envelope, including block candidates."""

    validate_labels(labels)
    validate_report(report)
    result_label, assessment_label, candidate_label, authority_label, next_label = labels
    lines = (
        f"{result_label}: {report.result}",
        f"{assessment_label}: {report.assessment}",
    )
    if _is_multiline_candidate(report):
        lines += (f"{candidate_label}: |", *(f"  {line}" for line in report.candidate.split("\n")))
    else:
        lines += (f"{candidate_label}: {report.candidate}",)
    return "\n".join((*lines, f"{authority_label}: {report.authority}", f"{next_label}: {report.next}"))


def parse(output: str, labels: tuple[str, str, str, str, str] = SCC_CANONICAL_LABELS) -> SCCReport:
    """Parse exactly one SCC envelope with a caller-selected label map."""

    validate_labels(labels)
    if not isinstance(output, str):
        raise GrammarError("SCC envelope must be a string")
    if any(separator in output for separator in LINE_SEPARATORS if separator != "\n"):
        raise GrammarError("SCC envelope fields must be separated by LF only")
    if output.endswith("\n"):
        output = output[:-1]
    lines = output.split("\n")
    result_label, assessment_label, candidate_label, authority_label, next_label = labels
    canonical = labels == SCC_CANONICAL_LABELS
    if len(lines) < len(labels):
        raise GrammarError("SCC envelope has an unexpected field count")
    result = _field_value(lines[0], result_label, compact=True, canonical=canonical)
    assessment = _field_value(lines[1], assessment_label, canonical=canonical)
    candidate_marker = (
        lines[2] == f"{candidate_label}: |"
        if canonical
        else lines[2].removeprefix(f"{candidate_label}:").strip(" \t") == "|"
    )
    candidate = "|" if candidate_marker else _field_value(lines[2], candidate_label, canonical=canonical)
    index = 3
    if candidate_marker:
        payload: list[str] = []
        while index < len(lines) and lines[index].startswith("  "):
            payload.append(lines[index].removeprefix("  "))
            index += 1
        if not payload or not any(line.strip() for line in payload):
            raise GrammarError("SCC block candidate requires non-whitespace payload text")
        candidate = "\n".join(payload)
    elif result != "BLOCKED":
        stripped = candidate.lstrip()
        if candidate == "Not provided" or (stripped.startswith("|") and not stripped[1:].strip()):
            raise GrammarError("SCC reserved and bare-pipe candidates require block serialization")
    if index + 2 != len(lines):
        raise GrammarError("SCC envelope has an unexpected authority field or trailing content")
    authority = _field_value(lines[index], authority_label, compact=True, canonical=canonical)
    next_step = _field_value(lines[index + 1], next_label, canonical=canonical)
    report = SCCReport(result, assessment, candidate, authority, next_step)
    validate_report(report)
    return report
