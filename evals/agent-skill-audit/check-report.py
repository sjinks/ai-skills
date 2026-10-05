#!/usr/bin/env python3
"""Validate the single default-roster report required by positive-edge-010."""

from __future__ import annotations

import re
import sys


HEADINGS = (
    "# Agent/Skill Readiness Audit",
    "## Audit Scope",
    "## Readiness Ratings",
    "## Material Findings",
    "## Target-Model Compatibility",
    "## Priority Changes",
)
MODELS = (
    "GPT-6 Luna",
    "GPT-6 Sol",
    "GPT-6.1 Sol",
    "GPT-6 Astra",
    "Claude Haiku 4.5",
    "Claude Sonnet 5",
    "Claude Opus 4.8",
    "Claude Opus 5",
    "Claude Fable 5",
)
RATINGS = (
    "Discovery and delegation",
    "Instruction architecture",
    "Operational completeness",
    "Model and runtime portability",
    "Maintainability and evaluability",
)
MODEL_VERDICTS = ("Suitable", "Suitable with limitations", "Unsuitable", "Not assessed")
FINAL_VERDICTS = ("Ready", "Ready with limitations", "Needs revision", "Major redesign", "Blocked")
ARTIFACT_TYPES = ("Agent Skill", "Custom agent", "Persistent instructions", "Other")
AUDIT_MODES = ("core", "package", "path")
AUDIT_STATUSES = ("completed", "partial", "blocked")
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")


class ValidationError(ValueError):
    """Raised when an output violates the task's report contract."""


def require(condition: bool, message: str) -> None:
    """Raise a readable validation error when a report condition is false."""
    if not condition:
        raise ValidationError(message)


def section_lines(lines: list[str], heading: str, next_heading: str) -> list[str]:
    """Return the nonblank lines between two already validated headings."""
    start = lines.index(heading) + 1
    end = lines.index(next_heading)
    return [line.strip() for line in lines[start:end] if line.strip()]


def validate(text: str) -> None:
    """Validate heading order, report rows, enum domains, and final termination."""
    lines = text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    headings = [line.strip() for line in lines if re.match(r"^ {0,3}#{1,2}\s+", line)]
    require(headings == list(HEADINGS), "expected exactly one report with canonical headings in order")
    require(bool(lines) and lines[0].strip() == HEADINGS[0], "report must start with its title")
    require(sum(bool(re.fullmatch(r"Audit: .+", line.strip())) for line in lines) == 1, "report requires exactly one nonempty Audit marker")
    scope = section_lines(lines, HEADINGS[1], HEADINGS[2])
    for field in ("Artifact type", "Mode", "Status", "Target models", "Target runtimes", "Files included", "Files excluded", "Limitations"):
        require(sum(line.startswith(f"- {field}:") for line in scope) == 1, f"scope requires exactly one {field} field")
    require(any(scope_line == f"- Artifact type: {value}" for scope_line in scope for value in ARTIFACT_TYPES), "artifact type is outside its allowed domain")
    require(any(scope_line == f"- Mode: {value}" for scope_line in scope for value in AUDIT_MODES), "audit mode is outside its allowed domain")
    require(any(scope_line == f"- Status: {value}" for scope_line in scope for value in ("completed", "partial")), "this usable-input task requires completed or partial audit status")
    for field in ("Target models", "Target runtimes", "Limitations"):
        require(any(line.startswith(f"- {field}: ") and line.removeprefix(f"- {field}: ").strip() for line in scope), f"scope field {field} must be nonempty")
    included_index = scope.index("- Files included:")
    excluded_index = scope.index("- Files excluded:")
    require(included_index + 1 < excluded_index and scope[included_index + 1].startswith("- ") and not scope[included_index + 1].startswith("- Files "), "scope must list included files")
    require(excluded_index + 1 < len(scope) - 1 and scope[excluded_index + 1].startswith("- ") and not scope[excluded_index + 1].startswith("- Limitations:"), "scope must list excluded files")
    rating_lines = section_lines(lines, HEADINGS[2], HEADINGS[3])
    rating_rows = [line for line in rating_lines if line.startswith("|") and not re.fullmatch(r"\|[\s:|-]+\|", line)]
    if rating_lines == ["Not assessed."]:
        pass
    else:
        require(len(rating_rows) == 6, "readiness ratings require header and five rows")
        parsed = [[cell.strip() for cell in re.split(r"\|", row.strip().strip("|"))] for row in rating_rows]
        require(parsed[0] == ["Area", "Rating", "Main risk"], "readiness rating table header is invalid")
        require([row[0] for row in parsed[1:]] == list(RATINGS), "readiness rating rows are missing, reordered, or duplicated")
        require(all(len(row) == 3 and row[1] in {"1", "2", "3", "4", "5"} and bool(row[2]) for row in parsed[1:]), "rating row has invalid columns, score, or risk")
    findings = section_lines(lines, HEADINGS[3], HEADINGS[4])
    require(findings == ["None."] or any(re.fullmatch(r"### ASR-\d{3} — .+", line) for line in findings), "findings must be None. or contain a numbered finding")
    if findings != ["None."]:
        starts = [index for index, line in enumerate(findings) if re.fullmatch(r"### ASR-\d{3} — .+", line)]
        identifiers = [re.fullmatch(r"### (ASR-\d{3}) — .+", findings[index]).group(1) for index in starts]
        require(identifiers == [f"ASR-{number:03d}" for number in range(1, len(starts) + 1)], "finding IDs must be unique and sequential")
        blocks = [findings[start : starts[offset + 1] if offset + 1 < len(starts) else len(findings)] for offset, start in enumerate(starts)]
        for block in blocks:
            severity = [line.removeprefix("Severity: ") for line in block if line.startswith("Severity:")]
            area = [line.removeprefix("Area: ") for line in block if line.startswith("Area:")]
            require(len(severity) == 1 and severity[0] in SEVERITIES, "each finding requires one canonical severity")
            require(len(area) == 1 and area[0] in RATINGS, "each finding requires one canonical readiness area")
            require(block.count("Locations:") == 1 and block.count("Evidence:") == 1, "each finding requires one Locations and Evidence field")
            location_start = block.index("Locations:") + 1
            evidence_start = block.index("Evidence:")
            require(location_start < evidence_start and any(line.startswith("- ") for line in block[location_start:evidence_start]), "each finding requires at least one location")
            evidence_end = max((index for index, line in enumerate(block) if line.startswith(("Risk:", "Correction:"))), default=len(block))
            require(any(line.startswith("> ") and len(line) > 2 for line in block[evidence_start + 1 : evidence_end]), "each finding requires a nonempty evidence quote")
            require(sum(line.startswith("Risk:") and len(line) > len("Risk:") for line in block) == 1, "each finding requires one nonempty Risk field")
            require(sum(line.startswith("Correction:") and len(line) > len("Correction:") for line in block) == 1, "each finding requires one nonempty Correction field")
    compat = section_lines(lines, HEADINGS[4], HEADINGS[5])
    compat_rows = [line for line in compat if line.startswith("|") and not re.fullmatch(r"\|[\s:|-]+\|", line)]
    require(len(compat_rows) == 10, "compatibility table requires header and nine model rows")
    parsed_compat = [[cell.strip() for cell in re.split(r"\|", row.strip().strip("|"))] for row in compat_rows]
    require(parsed_compat[0] == ["Model", "Verdict", "Main risk", "Required adaptation"], "compatibility table header is invalid")
    require([row[0] for row in parsed_compat[1:]] == list(MODELS), "compatibility model rows are missing, reordered, duplicated, or unexpected")
    require(all(len(row) == 4 and row[1] in MODEL_VERDICTS and bool(row[2]) and bool(row[3]) for row in parsed_compat[1:]), "compatibility row has invalid columns, verdict, risk, or adaptation")
    final = re.fullmatch(r"Verdict: (.+)", lines[-1].strip()) if lines else None
    require(final is not None and final.group(1) in FINAL_VERDICTS, "final content line must contain an allowed readiness verdict")
    require(sum(bool(re.fullmatch(r"Verdict: .+", line.strip())) for line in lines) == 1, "report requires exactly one Verdict line")
    priority = [line for line in lines[lines.index(HEADINGS[5]) + 1 : -1] if line.strip()]
    starts = [line.strip() for line in priority if re.match(r"^\s*\d+\. \S", line)]
    require(priority == ["None."] or (bool(starts) and all(line[:1].isspace() for line in priority if not re.match(r"^\s*\d+\. \S", line))), "priority changes must be None. or numbered with indented continuations")
    if priority != ["None."]:
        require([re.match(r"\s*(\d+)\.", line).group(1) for line in starts] == [str(number) for number in range(1, len(starts) + 1)], "priority changes must be sequentially numbered")


def main() -> int:
    """Read Waza's stdin payload and return a conventional checker status."""
    try:
        validate(sys.stdin.read())
    except ValidationError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: default roster report contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
