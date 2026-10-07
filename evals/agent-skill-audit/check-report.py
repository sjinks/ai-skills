#!/usr/bin/env python3
"""Validate the single default-roster report required by positive-edge-010."""

from __future__ import annotations

import re
import sys
import argparse


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
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
PROFILE_MARKERS = {
    "GPT-6 Luna": (
        (r"short (?:normal )?path",),
        (r"explicit defaults?",),
        (r"simple output grammar",),
    ),
    "GPT-6 Sol": (
        (r"clear outcomes?",),
        (r"evidence",),
        (r"adaptable tool use",),
        (r"side-effect boundar",),
    ),
    "GPT-6.1 Sol": (
        (r"literal broad scope",),
        (r"invariants?",),
        (r"\bdelegat\w*\b.{0,200}\boptional\b.{0,200}\bindependent workstreams?\b|\boptional\b.{0,200}\bdelegat\w*\b.{0,200}\bindependent workstreams?\b|\boptionally\s+delegat\w*\b.{0,200}\bindependent workstreams?\b|\bindependent workstreams?\b.{0,60}\boptionally\b.{0,30}\bdelegat\w*\b|\bdelegation of independent workstreams is optional\b",),
    ),
    "GPT-6 Astra": (
        (r"concise mission",),
        (r"hard boundar",),
        (r"strategic freedom",),
        (r"pause conditions?",),
    ),
}


class ValidationError(ValueError):
    """Raised when an output violates the task's report contract."""


def require(condition: bool, message: str) -> None:
    """Raise a readable validation error when a report condition is false."""
    if not condition:
        raise ValidationError(message)


def has_later_resolution(clauses: list[str], index: int) -> bool:
    """Check for later verification that resolves the same subject's limitation."""
    resolution_pattern = (
        r"\b(?:verification|compatibility)\b.{0,35}\b(?:is|was|are|were)?\s*(?:now\s+)?(?:complete|completed|verified|passed|successful)\b|"
        r"\b(?:complete|completed|verified|passed|successful)\b.{0,35}\b(?:verification|compatibility)\b|"
        r"\b(?:evidence|source)\b(?:\s+(?:is|was|are|were|has been|have been))?\s*(?:now\s+)?(?:available|obtained|verified|provided|supplied|collected)\b|"
        r"\bresults?\b(?:\s+(?:is|was|are|were|has been|have been))?\s*(?:now\s+)?(?:available|obtained|verified|complete|completed)\b"
    )
    source = clauses[index]
    source_subjects = set()
    for subject, pattern in (
        ("model", r"\bmodel\b"),
        ("runtime", r"\bruntime\b"),
        ("static", r"\bstatic(?: review| validation)?\b"),
        ("evidence", r"\b(?:evidence|source|results?)\b"),
        ("assessment", r"\bassessment\b"),
    ):
        if re.search(pattern, source, re.IGNORECASE):
            source_subjects.add(subject)
    source_subjects.update(
        f"model:{model}"
        for model in MODELS
        if re.search(re.escape(model), source, re.IGNORECASE)
    )
    for later_index, clause in enumerate(clauses[index + 1 :], start=index + 1):
        if not re.search(resolution_pattern, clause, re.IGNORECASE):
            continue
        later_subjects = set()
        for subject, pattern in (
            ("model", r"\bmodel\b"),
            ("runtime", r"\bruntime\b"),
            ("static", r"\bstatic(?: review| validation)?\b"),
            ("evidence", r"\b(?:evidence|source|results?)\b"),
            ("assessment", r"\bassessment\b"),
        ):
            if re.search(pattern, clause, re.IGNORECASE):
                later_subjects.add(subject)
        later_subjects.update(
            f"model:{model}"
            for model in MODELS
            if re.search(re.escape(model), clause, re.IGNORECASE)
        )
        if (
            (
                later_index == index + 1
                and not later_subjects
                and source_subjects == {"runtime"}
            )
            or (source_subjects and source_subjects <= later_subjects)
            or (source_subjects == {"static"} and "runtime" in later_subjects)
        ):
            return True
    return False


def has_affirmative_broad_delegation(clause: str) -> bool:
    """Find a broad delegation instruction whose own verb is not negated."""
    broad_scope = (
        r"(?:all|any|every|other|dependent|shared[- ]context|tightly coupled|non-independent)\s+"
        r"(?:tasks?|workstreams?|investigations?|work)"
    )
    patterns = (
        rf"\b(?:also\s+)?delegat(?:e|es|ed|ing)\b.{{0,40}}\b{broad_scope}\b",
        rf"\b{broad_scope}\b.{{0,40}}\bdelegat(?:e|es|ed|ing)\b",
    )
    negation_before_verb = re.compile(
        r"\b(?:do not|don't|never|should (?:not|never)|must (?:not|never)|will (?:not|never)|can (?:not|never)|cannot|can't)\s+"
        r"(?:(?:ever|under any circumstances|under any condition|at any time|in any case)\s+)?(?:be\s+)?$|"
        r"\b(?:is|are|was|were)\s+(?:not|never)\s+(?:ever\s+)?(?:to\s+)?(?:be\s+)?$",
        re.IGNORECASE,
    )
    for pattern in patterns:
        for match in re.finditer(pattern, clause, re.IGNORECASE):
            verb = re.search(r"\bdelegat(?:e|es|ed|ing)\b", match.group(), re.IGNORECASE)
            if verb is None:
                continue
            verb_start = match.start() + verb.start()
            if not negation_before_verb.search(clause[:verb_start]):
                return True
    return False


def section_lines(lines: list[str], heading: str, next_heading: str) -> list[str]:
    """Return the nonblank lines between two already validated headings."""
    start = next(index for index, line in enumerate(lines) if line.strip() == heading) + 1
    end = next(index for index, line in enumerate(lines) if line.strip() == next_heading)
    return [line.strip() for line in lines[start:end] if line.strip()]


def raw_section_lines(lines: list[str], heading: str, next_heading: str) -> list[str]:
    """Return every line between headings so table blank lines remain visible."""
    start = next(index for index, line in enumerate(lines) if line.strip() == heading) + 1
    end = next(index for index, line in enumerate(lines) if line.strip() == next_heading)
    section = lines[start:end]
    while section and not section[0].strip():
        section.pop(0)
    while section and not section[-1].strip():
        section.pop()
    return [line.rstrip() for line in section]


def split_table_row(line: str) -> list[str]:
    """Split one pipe table row while preserving escaped cell pipes."""
    line = line.strip()
    cells: list[str] = []
    cell: list[str] = []
    for character in line[1:-1]:
        if character == "|":
            preceding_backslashes = 0
            for previous in reversed(cell):
                if previous != "\\":
                    break
                preceding_backslashes += 1
            if preceding_backslashes % 2 == 0:
                cells.append("".join(cell).strip())
                cell = []
                continue
        cell.append(character)
    cells.append("".join(cell).strip())
    return cells


def has_unescaped_closing_pipe(line: str) -> bool:
    """Return whether a table row ends with a pipe delimiter, not cell text."""
    row = line.rstrip()
    if not row.endswith("|"):
        return False
    cell_text = row[:-1]
    backslashes = len(cell_text) - len(cell_text.rstrip("\\"))
    return backslashes % 2 == 0


def is_code_indented(line: str) -> bool:
    """Return whether leading spaces or tabs reach Markdown code indentation."""
    column = 0
    for character in line:
        if character == " ":
            column += 1
        elif character == "\t":
            column += 4 - column % 4
        else:
            break
        if column >= 4:
            return True
    return False


def parse_table_rows(section: list[str], header: list[str], row_count: int, diagnostic: str) -> list[list[str]]:
    """Parse a Markdown table after removing its separator row."""
    require(
        all(re.fullmatch(r" {0,3}\|.*\|[ \t]*", line) and not line.lstrip().startswith("||") for line in section),
        "table sections must contain only well-formed table rows",
    )
    require(
        all(has_unescaped_closing_pipe(line) for line in section),
        "table rows require an unescaped closing pipe",
    )
    table = section
    require(len(table) == row_count + 2, diagnostic)
    parsed = [split_table_row(line) for line in table]
    require(parsed[0] == header, "table header is invalid")
    separator = [cell.strip() for cell in table[1].strip().strip("|").split("|")]
    require(
        len(separator) == len(header) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator),
        "table separator must match header columns",
    )
    rows = [row for row in parsed[2:]]
    require(all(len(row) == len(header) for row in rows), "table row has an invalid number of columns")
    return rows


def validate_final_verdict(
    verdict: str,
    scores: list[int],
    has_findings: bool,
    has_priorities: bool,
    limitations: str,
) -> None:
    """Enforce the deterministic rating, correction, and limitation mapping."""
    revision_required = any(score in {2, 3} for score in scores) or has_findings or has_priorities
    if 1 in scores:
        require(verdict == "Major redesign", "rating 1 requires Major redesign")
        return
    if verdict == "Major redesign":
        require(scores.count(2) >= 2, "Major redesign requires a rating 1 or multiple rating-2 areas")
        return
    if revision_required:
        require(verdict == "Needs revision", "rating 2/3 or corrective findings/priorities require Needs revision")
        return
    expected = "Ready" if limitations == "None." else "Ready with limitations"
    if expected == "Ready with limitations":
        model_runtime_limit_pattern = (
            r"\b(?:model|runtime)\b.{0,45}\b(?:limitations?|limited|constraints?|unsupported|unavailable|not supplied|not available|not measured|not (?:been )?tested|not (?:been )?verified|not performed|(?:does not|doesn't|do not|don't|cannot|can't) support|missing|incomplete|lacks?|cannot|can't|unable)\b|"
            r"\b(?:limitations?|limited|constraints?|unsupported|unavailable|not supplied|not available|not measured|not (?:been )?tested|not (?:been )?verified|not performed|(?:does not|doesn't|do not|don't|cannot|can't) support|missing|incomplete|lacks?|cannot|can't|unable)\b.{0,45}\b(?:model|runtime)\b|"
            r"\b(?:model|runtime)\b.{0,35}\bneeds?\s+(?:a\s+|an\s+|some\s+|further\s+)?(?:adaptation|reconfiguration|configuration|workaround|support)\b|"
            r"\bneeds?\s+(?:a\s+|an\s+|some\s+|further\s+)?(?:adaptation|reconfiguration|configuration|workaround|support)\b.{0,35}\b(?:model|runtime)\b"
        )
        explicit_denial_pattern = (
            r"\bno\b.{0,45}\b(?:remaining\s+)?(?:limitations?|constraints?)\b|"
            r"\bno\b.{0,40}\b(?:model|runtime)\b.{0,25}\b(?:limitations?|constraints?)\b.{0,20}\b(?:remain|exist|apply|identified)\b|"
            r"\bno\b.{0,35}\bunsupported features?\b.{0,35}\b(?:remain|were identified|were found|exist|apply|are present|for the model|in runtime)\b|"
            r"\bno\b.{0,35}\bunsupported\b.{0,35}\b(?:model|runtime)\b|"
            r"\b(?:model|runtime)\b.{0,40}\b(?:limitations?|constraints?)\b(?:\s*[:=]\s*|\s+(?:are|is|remain|remains|have been|has been|was|were)\s+).{0,25}\b(?:none|n/?a|no longer|not present|not applicable|not required|not needed|not identified|not remaining|not material|not relevant|not significant|not a concern|immaterial|irrelevant|negligible|insignificant|theoretical|hypothetical|absent|inapplicable|resolved|fixed|removed|eliminated|cleared|addressed)\b|"
            r"\b(?:model|runtime)\b.{0,40}\b(?:limitations?|constraints?)\s+(?:not present|not applicable|not required|not needed|not identified|not remaining|not material|not relevant|not significant|not a concern|immaterial|irrelevant|negligible|insignificant|theoretical|hypothetical|absent|inapplicable|resolved|fixed|removed|eliminated|cleared|addressed)\b|"
            r"\b(?:model|runtime)\b.{0,25}\b(?:not|never|isn't|aren't|doesn't|don't)\b.{0,20}\b(?:limited|constrained|restricted|affected)\b|"
            r"\b(?:model|runtime)\b.{0,25}\b(?:no|not|never|isn't|doesn't|do not|don't)\b.{0,20}\b(?:unsupported|unavailable|missing|incomplete)\b|"
            r"\b(?:model|runtime)\b.{0,25}\b(?:has|have)\s+no\s+(?:limitations?|constraints?|restrictions?)\b|"
            r"\b(?:model|runtime)\b.{0,25}\b(?:does not|doesn't|do not|don't)\s+have\s+(?:any\s+)?(?:limitations?|constraints?|restrictions?)\b|"
            r"\b(?:model|runtime)\b.{0,25}\bneeds?\s+no\s+(?:(?:further|additional)\s+)?(?:adaptation|changes?|limitations?|constraints?|reconfiguration|configuration|workaround|support)\b|"
            r"\b(?:limitations?|constraints?)\b.{0,25}\b(?:are|is|do|does)\s+not\b.{0,20}\b(?:present|applicable|apply|remain|exist|identified|needed|material|relevant|significant|a concern)\b"
        )
        limitation_clauses = re.split(
            r";|,\s*but\b|\bbut\b|\bhowever\b|\band\s+(?=(?:no\b|(?:the\s+)?(?:model|runtime)\b))",
            limitations,
            flags=re.IGNORECASE,
        )
        runtime_unverified = any(
            re.search(
                r"\b(?:model|runtime)\b.{0,45}\b(?:not (?:been )?tested|not (?:been )?verified|not measured|not performed|unavailable)\b",
                clause,
                re.IGNORECASE,
            )
            and not re.search(
                r"\b(?:not|is not|isn't|no longer|no)\s+(?:unavailable|missing|incomplete|not supplied|not available|not measured|not verified|not performed)\b",
                clause,
                re.IGNORECASE,
            )
            and not has_later_resolution(limitation_clauses, index)
            for index, clause in enumerate(limitation_clauses)
        )
        unavailable_evidence = any(
            re.search(
                r"\b(?:unavailable|not supplied|not available|not measured|not verified|not performed|missing|incomplete|not obtained|never obtained|not collected|never collected)\b.{0,40}\b(?:evidence|source|assessment|verification|results?)\b|"
                r"\b(?:evidence|source|assessment|verification|results?)\b.{0,40}\b(?:unavailable|not supplied|not available|not measured|not verified|not performed|missing|incomplete|not obtained|never obtained|not collected|never collected)\b|"
                r"\b(?:evidence|source|assessment|verification|results?)\b.{0,40}\b(?:was|were)\s+(?:not|never)\s+(?:obtained|collected|gathered|recorded|available|supplied|provided)\b|"
                r"\bno\s+(?:model\s+)?(?:test\s+)?evidence\b.{0,30}\b(?:was\s+)?obtained\b",
                clause,
                re.IGNORECASE,
            )
            and not re.search(
                r"\b(?:not|is not|isn't|no longer|no)\s+(?:unavailable|missing|incomplete|not supplied|not available|not measured|not verified|not performed)\b|"
                r"\b(?:evidence|source|assessment|verification|results?)\b.{0,20}\b(?:is\s+)?(?:not|never)\s+unavailable\b",
                clause,
                re.IGNORECASE,
            )
            and not has_later_resolution(limitation_clauses, index)
            for index, clause in enumerate(limitation_clauses)
        )
        static_only = any(
            re.search(r"\bstatic(?: review| validation)? only\b", clause, re.IGNORECASE)
            and not re.search(
                r"\b(?:not\s+static(?: review| validation)? only|(?:no longer|not|is not|was not|were not|are not|isn't|wasn't|weren't|aren't)\s+static(?: review| validation)? only|static(?: review| validation)? only\s+(?:is|was|were|are)?\s*(?:not|no longer|isn't|wasn't|weren't|aren't)\s+(?:true|valid|applicable|the case))\b",
                clause,
                re.IGNORECASE,
            )
            and not has_later_resolution(limitation_clauses, index)
            for index, clause in enumerate(limitation_clauses)
        )
        independent_active_limit = any(
            re.search(model_runtime_limit_pattern, clause, re.IGNORECASE)
            and not re.search(explicit_denial_pattern, clause, re.IGNORECASE)
            and not re.search(r"\b(?:not|is not|isn't|no longer|no)\s+(?:unavailable|missing|incomplete|not supplied|not available|not measured|not verified|not performed)\b", clause, re.IGNORECASE)
            and not has_later_resolution(limitation_clauses, index)
            for index, clause in enumerate(limitation_clauses)
        )
        require(
            runtime_unverified
            or independent_active_limit
            or static_only
            or unavailable_evidence,
            "Ready with limitations requires a model, runtime, or unavailable-evidence limitation",
        )
    require(verdict == expected, f"clean ratings require {expected} based on the limitations field")


def validate_profile_rows(rows: list[list[str]]) -> None:
    """Keep task-required GPT profile signals attached to their named rows."""
    for row in rows:
        model = row[0]
        if model not in PROFILE_MARKERS:
            continue
        prose = " ".join(row[2:])
        matches = sum(
            any(re.search(pattern, prose, flags=re.IGNORECASE) for pattern in alternatives)
            for alternatives in PROFILE_MARKERS[model]
        )
        require(matches >= 2, f"{model} row is missing model-specific profile evidence")
        if model == "GPT-6.1 Sol":
            delegation_cue_present = any(
                re.search(pattern, prose, re.IGNORECASE)
                for pattern in PROFILE_MARKERS[model][2]
            )
            negated_optionality = re.search(
                r"\b(?:delegation|delegat\w*)\b.{0,30}\b(?:not|never|isn't|aren't|wasn't|weren't)\s+optional\b|"
                r"\b(?:not|never|isn't|aren't|wasn't|weren't)\s+optional\b.{0,30}\b(?:delegation|delegat\w*)\b|"
                r"\b(?:delegation|delegat\w*)\b.{0,30}\b(?:mandatory|required)\b|"
                r"\b(?:mandatory|required)\b.{0,30}\b(?:delegation|delegat\w*)\b",
                prose,
                re.IGNORECASE,
            ) is not None
            explicitly_independent = re.search(
                r"\bonly\b.{0,80}\bindependent workstreams?\b|\bindependent workstreams?\b.{0,80}\bonly\b",
                prose,
                re.IGNORECASE,
            ) is not None
            excluded_scope_pattern = (
                r"\b(?:any|all|other|dependent|shared[- ]context|tightly coupled|non-independent)\s+(?:tasks?|workstreams?|investigations?)\b.{0,60}\b(?:stay|remain)\s+local\b|"
                r"\bother tasks?\s+local\b|\bdependent tasks?\b.{0,30}\btogether\b|"
                r"\b(?:do not|don't|never)(?:\s+\w+){0,4}\s+delegate\s+(?:any\s+)?(?:dependent|shared[- ]context|tightly coupled|other|non-independent)\b"
            )
            excluded_scope = re.search(
                excluded_scope_pattern,
                prose,
                re.IGNORECASE,
            ) is not None
            delegation_clauses = re.split(r"[.;]|\bbut\b|\bhowever\b", prose, flags=re.IGNORECASE)
            affirmative_delegation_clauses = re.split(
                r"[.;]|\b(?:and|then|but|however)\b|,\s*(?=(?:also|then|and|but|however)\b)",
                prose,
                flags=re.IGNORECASE,
            )
            expanded_scope = any(
                re.search(
                    r"\bindependent workstreams?\b.{0,100}\b(?:and|or)\s+(?:for\s+)?(?:all|any|every|dependent|shared[- ]context|tightly coupled|other|non-independent)\s+(?:tasks?|workstreams?|investigations?)\b",
                    clause,
                    re.IGNORECASE,
                )
                and not re.search(
                    r"\b(?:other tasks?\s+local|(?:any|all|dependent|shared[- ]context|tightly coupled|non-independent)\s+(?:tasks?|workstreams?|investigations?)\s+(?:stay|remain)\s+local|dependent tasks?\s+together)\b",
                    clause,
                    re.IGNORECASE,
                )
                for clause in delegation_clauses
            )
            affirmative_extra_scope = any(
                has_affirmative_broad_delegation(clause)
                for clause in affirmative_delegation_clauses
            )
            if delegation_cue_present:
                require(
                    not negated_optionality
                    and (explicitly_independent or excluded_scope)
                    and not expanded_scope
                    and not affirmative_extra_scope,
                    "GPT-6.1 Sol delegation must remain limited to independent workstreams",
                )


def validate(text: str, *, require_findings: bool = False) -> None:
    """Validate heading order, report rows, enum domains, and final termination."""
    lines = text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    require(
        not any(re.match(r"^ {0,3}(?:`{3,}|~{3,})", line) for line in lines),
        "fenced code blocks are not allowed in this report",
    )
    headings = [line.strip() for line in lines if re.match(r"^ {0,3}#{1,2}\s+", line)]
    require(headings == list(HEADINGS), "expected exactly one report with canonical headings in order")
    require(bool(lines) and lines[0].strip() == HEADINGS[0], "report must start with its title")
    audit_markers = [line for line in lines if re.match(r" {0,3}Audit:", line)]
    require(
        len(audit_markers) == 1 and re.fullmatch(r" {0,3}Audit:\s+\S.*", audit_markers[0]) is not None,
        "report requires exactly one nonempty Audit marker",
    )
    audit_index = lines.index(audit_markers[0])
    scope_heading_index = next(index for index, line in enumerate(lines) if line.strip() == HEADINGS[1])
    require(audit_index < scope_heading_index, "Audit marker must follow the title and precede Audit Scope")
    scope_raw = raw_section_lines(lines, HEADINGS[1], HEADINGS[2])
    require(all(not is_code_indented(line) for line in scope_raw), "scope fields cannot be indented as code")
    scope = [line.strip() for line in scope_raw if line.strip()]
    for field in ("Artifact type", "Mode", "Status", "Target models", "Target runtimes", "Files included", "Files excluded", "Limitations"):
        require(sum(line.startswith(f"- {field}:") for line in scope) == 1, f"scope requires exactly one {field} field")
    require(any(scope_line == f"- Artifact type: {value}" for scope_line in scope for value in ARTIFACT_TYPES), "artifact type is outside its allowed domain")
    require(any(scope_line == f"- Mode: {value}" for scope_line in scope for value in AUDIT_MODES), "audit mode is outside its allowed domain")
    require("- Artifact type: Custom agent" in scope, "this task audits a Custom agent")
    require("- Mode: core" in scope, "a single pasted artifact requires core audit mode")
    require("- Status: completed" in scope, "this readable single-artifact task requires completed audit status")
    for field in ("Target models", "Target runtimes", "Limitations"):
        require(any(line.startswith(f"- {field}: ") and line.removeprefix(f"- {field}: ").strip() for line in scope), f"scope field {field} must be nonempty")
    require("- Target models: default set" in scope, "this task requires the default target model set")
    require("- Target runtimes: Not supplied" in scope, "this task has no supplied target runtime")
    included_index = scope.index("- Files included:")
    excluded_index = scope.index("- Files excluded:")
    require(included_index + 1 < excluded_index and scope[included_index + 1].startswith("- ") and not scope[included_index + 1].startswith("- Files "), "scope must list included files")
    require(excluded_index + 1 < len(scope) - 1 and scope[excluded_index + 1].startswith("- ") and not scope[excluded_index + 1].startswith("- Limitations:"), "scope must list excluded files")
    rating_lines = raw_section_lines(lines, HEADINGS[2], HEADINGS[3])
    require(rating_lines != ["Not assessed."], "readiness ratings require header and five rows")
    ratings = parse_table_rows(
        rating_lines,
        ["Area", "Rating", "Main risk"],
        len(RATINGS),
        "readiness ratings require header and five rows",
    )
    require([row[0] for row in ratings] == list(RATINGS), "readiness rating rows are missing, reordered, or duplicated")
    require(all(len(row) == 3 and row[1] in {"1", "2", "3", "4", "5"} and bool(row[2]) for row in ratings), "rating row has invalid columns, score, or risk")
    findings_raw = raw_section_lines(lines, HEADINGS[3], HEADINGS[4])
    require(
        all(not is_code_indented(line) for line in findings_raw),
        "finding content cannot be indented as a code block",
    )
    findings = [line.strip() for line in findings_raw if line.strip()]
    require(findings == ["None."] or any(re.fullmatch(r"### ASR-\d{3} — .+", line) for line in findings), "findings must be None. or contain a numbered finding")
    require(findings == ["None."] or "None." not in findings, "findings cannot mix None. with numbered findings")
    require(not require_findings or findings != ["None."], "this known-defect task requires at least one material finding")
    if findings != ["None."]:
        starts = [index for index, line in enumerate(findings) if re.fullmatch(r"### ASR-\d{3} — .+", line)]
        identifiers = [re.fullmatch(r"### (ASR-\d{3}) — .+", findings[index]).group(1) for index in starts]
        require(identifiers == [f"ASR-{number:03d}" for number in range(1, len(starts) + 1)], "finding IDs must be unique and sequential")
        require(starts[0] == 0, "findings cannot contain content before the first numbered finding")
        blocks = [findings[start : starts[offset + 1] if offset + 1 < len(starts) else len(findings)] for offset, start in enumerate(starts)]
        for block in blocks:
            require(len(block) >= 8, "finding is incomplete")
            severity = block[1].removeprefix("Severity: ") if block[1].startswith("Severity:") else ""
            area = block[2].removeprefix("Area: ") if block[2].startswith("Area:") else ""
            require(severity in SEVERITIES, "each finding requires one canonical severity in order")
            require(area in RATINGS, "each finding requires one canonical readiness area in order")
            require(block[3] == "Locations:", "each finding requires Locations after Area")
            cursor = 4
            location_start = cursor
            while cursor < len(block) and block[cursor].startswith("- "):
                cursor += 1
            require(cursor > location_start, "each finding requires at least one location")
            require(cursor < len(block) and block[cursor] == "Evidence:", "each finding requires Evidence after Locations")
            cursor += 1
            evidence_start = cursor
            while cursor < len(block) and block[cursor].startswith("> ") and len(block[cursor]) > 2:
                cursor += 1
            require(cursor > evidence_start, "each finding requires a nonempty evidence quote")
            require(cursor < len(block) and block[cursor].startswith("Risk: ") and len(block[cursor]) > len("Risk: "), "each finding requires one nonempty Risk field after Evidence")
            cursor += 1
            while cursor < len(block) and not block[cursor].startswith("Correction: "):
                require(bool(block[cursor].strip()), "finding field continuation cannot be blank")
                require(not re.match(r"^(?:Severity|Area|Locations|Evidence|Risk|Correction):", block[cursor]), "finding fields must follow the canonical order")
                cursor += 1
            require(cursor < len(block) and block[cursor].startswith("Correction: ") and len(block[cursor]) > len("Correction: "), "each finding requires one nonempty Correction field after Risk")
            cursor += 1
            while cursor < len(block):
                require(bool(block[cursor].strip()), "finding field continuation cannot be blank")
                require(not re.match(r"^(?:Severity|Area|Locations|Evidence|Risk|Correction):", block[cursor]), "finding fields must follow the canonical order")
                cursor += 1
            require(cursor == len(block), "finding fields must follow the canonical order")
    compat = raw_section_lines(lines, HEADINGS[4], HEADINGS[5])
    compatibility = parse_table_rows(
        compat,
        ["Model", "Verdict", "Main risk", "Required adaptation"],
        len(MODELS),
        "compatibility table requires header and nine model rows",
    )
    require([row[0] for row in compatibility] == list(MODELS), "compatibility model rows are missing, reordered, duplicated, or unexpected")
    require(all(len(row) == 4 and row[1] in MODEL_VERDICTS and bool(row[2]) and bool(row[3]) for row in compatibility), "compatibility row has invalid columns, verdict, risk, or adaptation")
    require(all(row[1] != "Not assessed" for row in compatibility), "usable-input task requires every target model to be assessed")
    validate_profile_rows(compatibility)
    require(not is_code_indented(lines[-1]) if lines else False, "final verdict cannot be indented as code")
    final = re.fullmatch(r" {0,3}Verdict: (.+)", lines[-1]) if lines else None
    require(final is not None and final.group(1) in FINAL_VERDICTS, "final content line must contain an allowed readiness verdict")
    require(sum(bool(re.fullmatch(r"Verdict: .+", line.strip())) for line in lines) == 1, "report requires exactly one Verdict line")
    priority_heading_index = next(index for index, line in enumerate(lines) if line.strip() == HEADINGS[5])
    priority = [line for line in lines[priority_heading_index + 1 : -1] if line.strip()]
    starts = [line.strip() for line in priority if re.match(r"^\s*\d+\. \S", line)]
    empty_priority_line = len(priority) == 1 and priority[0].strip() == "None."
    require(
        not empty_priority_line or not is_code_indented(priority[0]),
        "None. priority cannot be indented as code",
    )
    no_priorities = empty_priority_line
    if not no_priorities:
        seen_priority = False
        for line in priority:
            numbered = re.match(r"^\s*\d+\. \S", line)
            if numbered:
                require(not is_code_indented(line), "priority items cannot be indented as code")
                seen_priority = True
            else:
                require(seen_priority, "priority continuation must follow a numbered item")
                require(line.strip() != "None.", "None. cannot be mixed with numbered priority items")
        require(bool(starts), "priority changes must be None. or numbered with continuations")
    if priority != ["None."]:
        require([re.match(r"\s*(\d+)\.", line).group(1) for line in starts] == [str(number) for number in range(1, len(starts) + 1)], "priority changes must be sequentially numbered")
        require(len(starts) <= 5, "priority changes must not exceed five items")
    limitations = next(line.removeprefix("- Limitations: ") for line in scope if line.startswith("- Limitations: "))
    validate_final_verdict(
        final.group(1),
        [int(row[1]) for row in ratings],
        findings != ["None."],
        not no_priorities,
        limitations,
    )


def main() -> int:
    """Read a report and return a conventional checker status."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-empty-findings",
        action="store_true",
        help="validate the canonical report contract without the task fixture's required finding",
    )
    arguments = parser.parse_args()
    try:
        validate(sys.stdin.read(), require_findings=not arguments.allow_empty_findings)
    except ValidationError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: default roster report contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
