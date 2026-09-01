#!/usr/bin/env python3
"""Validate equivalence-class-audit output from Waza's JSON stdin envelope.

Waza passes a JSON object whose ``output`` member is the model response. Invoke
this script as ``python3 check-report.py <task-id>``; each profile checks the
response structure and the task-specific rows that RE2 cannot express safely.
"""

import json
import html
import re
import sys
import unicodedata
from collections import Counter


AXES = (
    "Opposite Bound", "Sibling Parameter/Field", "Mirror Call Site/Use Site",
    "Inverse Operation", "Type/Schema Narrowing",
    "Validation vs Normalization/Sanitization",
    "Happy/Error/Retry/Cancel Path Twin", "Race/Shared-State Twin",
    "Permission/Authorization Class", "Observability Twin", "Resource Cleanup",
    "Contract Symmetry", "Equivalence by Naming", "Test Mirror",
    "Empty/Sentinel Equivalence", "Async/Sync or Mode Twin",
    "Documentation/Spec Prose Twin", "Cache/Projection/Source-of-Truth Twin",
)
SECTIONS = (
    "Defects to fix now", "Deferred follow-ups",
    "Out-of-scope candidates discovered", "Blocking questions",
    "Test/doc implications",
)
MISSING = ("missing", "not provided", "not supplied", "required", "needed")
PRESENCE_VALUES = {
    "present", "absent", "n/a — structurally inapplicable",
    "n/a — no candidates in scope", "blocked — clarification needed",
}
DISPOSITIONS = {"fix-now", "defer-with-owner", "n/a", "blocked"}
METADATA_PLACEHOLDERS = {"name", "owner", "provenance", "rationale", "reason", "source"}
NON_POPULATED_METADATA = {
    "missing", "unknown", "unavailable", "not supplied", "none", "n/a", "tbd",
    "unassigned", "not the owner",
}
FIELD_NON_POPULATED_METADATA = {
    "owner": {"nobody", "no one", "someone", "somebody", "unowned", "pending"},
    "reason": {"pending", "unresolved"},
    "provenance": {"somewhere", "pending", "unresolved"},
}
PROFILES = {
    "positive-edge-001", "positive-edge-002", "positive-edge-003",
    "positive-edge-004", "positive-edge-005", "positive-edge-006",
    "positive-edge-007", "positive-edge-008", "positive-edge-009", "positive-edge-010",
    "positive-edge-011",
    "positive-trigger-001", "positive-trigger-002",
}
PROFILE_HEADERS = {
    "positive-edge-001": (("timeoutseconds", "health"), ("config/healthcheck.yml", "docs")),
    "positive-edge-002": (("delete /teams/{teamid}", "organization membership"),
                          ("src/routes/team.routes.ts", "src/controllers/team.controller.ts",
                           "tests/team.controller.spec.ts")),
    "positive-edge-004": (("maxitems", "zero", "pagination"),
                          ("src/pagination.ts", "tests/pagination.test.ts")),
    "positive-edge-005": (("maxretries", "zero"), ("config/retry.yml", "docs/operations.md")),
    "positive-edge-007": (("minitems", "zero", "pagination"),
                          ("src/pagination.ts", "src/batch-pagination.ts", "tests/pagination.test.ts",
                           "docs/api.md")),
    "positive-edge-008": (("maxretries", "zero"),
                          ("config/retry.yml", "docs/api.md", "docs/operations.md")),
    "positive-edge-009": (("maxretries", "zero"), ("config/retry.yml", "docs/api.md")),
    "positive-edge-010": (("minitems", "zero"),
                          ("src/pagination.ts", "tests/pagination.test.ts", "docs/api.md")),
    "positive-trigger-001": (("maxretries", "zero", "inc-17"),
                             ("config/retry.yml", "src/retry_policy.py", "tests/test_retry_policy.py",
                              "docs/operations.md")),
    "positive-trigger-002": (("can_export", "projects", "export"),
                             ("routes/projects.yml", "controllers/project_export.go",
                              "controllers/project_archive.go", "controllers/project_report.go",
                              "policies/project_permissions.rego", "tests/project_permissions_test.go",
                              "project exports")),
}


def fail(message):
    print(message, file=sys.stderr)
    raise SystemExit(1)


def canonical_unicode(value):
    """Decode entities, remove format controls, and normalize compatibility forms."""
    value = html.unescape(value)
    value = "".join(character for character in value
                    if unicodedata.category(character) != "Cf")
    value = unicodedata.normalize("NFKC", value)
    value = "".join(character for character in value
                    if unicodedata.category(character) != "Cf")
    return unicodedata.normalize("NFKC", value)


def strip_markdown_markers(value):
    previous = None
    while value != previous:
        previous = value
        value = re.sub(r"(`{1,3}|\*{1,3}|~{2})(.+?)\1", r"\2", value)
        value = re.sub(r"(?<!\w)(_{1,2})([^_\n]+?)\1(?!\w)", r"\2", value)
    return value


def label_norm(value):
    value = strip_markdown_markers(canonical_unicode(value))
    return " ".join(value.casefold().split())


def norm(value):
    value = strip_markdown_markers(canonical_unicode(value))
    value = re.sub(r"\b0\b", "zero", value)
    return " ".join(value.lower().split())


def visible(value):
    return bool(re.search(r"\w", visible_text(value), flags=re.UNICODE))


def visible_text(value):
    value = html.unescape(value)
    value = re.sub(r"<!--.*?-->", "", value, flags=re.DOTALL)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"&(?:#\d+|#x[0-9a-f]+|[a-z]+);", "", value, flags=re.I).strip()


def contains(value, *terms):
    value = value.lower()
    return all(term.lower() in value for term in terms)


def missing_marker(value):
    value = norm(value)
    if value in MISSING:
        return True
    return bool(re.search(r"\b(?:missing|not provided|not supplied)\b", value)
                or re.search(r"\b(?:is|are|remains?)\s+(?:required|needed)\b", value))


def missing_header_marker(value):
    value = norm(value)
    if value in MISSING:
        return True
    return bool(re.fullmatch(
        r"^(?:the\s+|this\s+)?(?:triggering finding|locked audit scope|scope|finding|input)\s+"
        r"(?:is|are|remains?)\s+(?:missing|not provided|not supplied|required|needed)[.!?]?",
        value,
    ))


def populated_metadata(value):
    if not visible(value):
        return False
    normalized = unicodedata.normalize("NFKC", norm(visible_text(value)))
    bare = re.sub(r"^\W+|\W+$", "", normalized, flags=re.UNICODE)
    return bool(bare) and bare not in METADATA_PLACEHOLDERS


def non_populated_metadata(value, field=None):
    normalized = unicodedata.normalize("NFKC", norm(visible_text(value)))
    bare = re.sub(r"^\W+|\W+$", "", normalized, flags=re.UNICODE)
    field_terms = {
        "owner": r"owner|ownership|owning team|assignee",
        "reason": r"reason|rationale|justification",
        "provenance": r"provenance|source",
    }
    terms = field_terms.get(field, "|".join(field_terms.values()))
    negative_phrase = re.search(
        rf"\b(?:not\s+(?:the\s+|an?\s+)?(?:{terms})|"
        rf"without\s+(?:the\s+|an?\s+)?(?:{terms})|"
        rf"(?:{terms})\s+(?:(?:is|are|was|were|remains?)\s+)?"
        rf"(?:unknown|missing|unavailable|unsupplied|unassigned|pending|tbd|"
        rf"unspecified|not\s+(?:known|provided|supplied|available|assigned)|"
        rf"cannot\s+be\s+(?:determined|identified|confirmed)))\b",
        bare,
    )
    no_value_phrase = re.search(
        rf"\bno\s+(?:{terms})(?:\s+(?:is|was|has been))?\s*"
        rf"(?:provided|supplied|given|available|known|assigned)\b|"
        rf"\bno\s+(?:{terms})\s*(?:$|[,;.)\]])",
        bare,
    )
    invalid_suffix = re.search(
        r"(?:\(|[;,:]|\s[—–-])\s*"
        r"(?:missing|unknown|unavailable|not supplied|none|n/a|tbd|unassigned)\s*$",
        bare,
    )
    if negative_phrase or no_value_phrase or invalid_suffix:
        return True
    return (bare in NON_POPULATED_METADATA
        or bare in FIELD_NON_POPULATED_METADATA.get(field, set())
        or bool(re.fullmatch(
        r"to be (?:assigned|determined)|(?:unknown|missing|unassigned|tbd)\s+"
        r"(?:owner|ownership|team|source|provenance|reason|metadata|assignment)(?:\s+.*)?"
        r"|not supplied(?: by .+)?|no\s+(?:owner|team|source|provenance|reason|metadata)",
        bare,
    )))


def overlaps(left, right):
    words = set(re.findall(r"[a-z0-9_./-]{4,}", norm(left)))
    return bool(words & set(re.findall(r"[a-z0-9_./-]{4,}", norm(right))))


def candidate_spans(candidate, bullet):
    candidate = label_norm(candidate)
    bullet = label_norm(bullet)
    return [match.span() for match in re.finditer(
        rf"(?<![a-z0-9_./-]){re.escape(candidate)}(?![a-z0-9_/-]|\.[a-z0-9_])",
        bullet,
    )]


def candidate_named(candidate, bullet):
    return bool(candidate_spans(candidate, bullet))


def mentioned_candidate_indexes(candidates, bullet):
    raw = [index for index, candidate in enumerate(candidates)
           if candidate_named(candidate, bullet)]
    mentions = []
    for candidate_index in raw:
        spans = candidate_spans(candidates[candidate_index], bullet)
        contained = all(any(
            other_start <= start and end <= other_end
            and label_norm(candidates[candidate_index]) != label_norm(candidates[other_index])
            for other_index in raw
            for other_start, other_end in candidate_spans(candidates[other_index], bullet)
        ) for start, end in spans)
        if not contained:
            mentions.append(candidate_index)
    return mentions


def has_mode_term(value, mode):
    patterns = {
        "sync": r"\bsync(?:hronous)?\b",
        "async": r"\basync(?:hronous)?\b",
    }
    return bool(re.search(patterns[mode], norm(value)))


def requests(value):
    value = value.strip()
    value = re.sub(
        r"^([_*~]{1,3})(provide|specify|clarify|confirm|need)\1(?=\s|$)",
        r"\2",
        value,
        flags=re.I,
    )
    while True:
        for marker in ("___", "***", "~~~", "__", "**", "~~", "_", "*", "~"):
            if value.startswith(marker) and value.endswith(marker) and len(value) > 2 * len(marker):
                value = value[len(marker):-len(marker)].strip()
                break
        else:
            break
    value = norm(value)
    if re.match(r"^(?:please\s+)?(?:do not|don't|need not|not)\b", value):
        return False
    imperative = re.match(r"^(?:please\s+)?(?:provide|specify|clarify|confirm|need)\b", value)
    question = re.match(r"^(?:what|which|who|why|can|could|would|are|does|do|is|should)\b.*\?$", value)
    return bool(imperative or question)


def table_cells(line):
    line = line.strip(" \t")
    if not line.startswith("|") or not line.endswith("|"):
        return None
    cells = []
    cell = []
    escaped = False
    for character in line[1:-1]:
        if escaped:
            if character != "|":
                cell.append("\\")
            cell.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "|":
            cells.append("".join(cell).strip())
            cell = []
        else:
            cell.append(character)
    if escaped:
        cell.append("\\")
    cells.append("".join(cell).strip())
    return cells


def table_separator(cells):
    return len(cells) == 5 and all(re.fullmatch(r"-{3,}", cell) for cell in cells)


def parse_output():
    try:
        envelope = json.load(sys.stdin)
    except json.JSONDecodeError:
        fail("invalid JSON envelope")
    if not isinstance(envelope, dict):
        fail("JSON envelope must be an object")
    output = envelope.get("output")
    if not isinstance(output, str) or not output.strip():
        fail("missing output")
    return output.replace("\r\n", "\n").replace("\r", "\n")


def parse_report(output):
    lines = output.split("\n")
    report_indexes = [index for index, line in enumerate(lines)
                      if line.strip() == "## Equivalence-Class Audit Report"]
    if len(report_indexes) != 1:
        fail("expected exactly one report heading")
    report_index = report_indexes[0]
    if any(line.strip() for line in lines[:report_index]):
        fail("report heading must be the first content line")

    headers = {}
    header_indexes = {}
    for name in ("Triggering finding", "Locked audit scope", "Output depth"):
        matches = [(index, line.strip().split(":", 1)[1].strip())
                   for index, line in enumerate(lines)
                   if line.strip().startswith(f"{name}:")]
        if len(matches) != 1 or not visible(matches[0][1]):
            fail(f"expected exactly one populated {name} header")
        header_indexes[name], headers[name] = matches[0]
    ordered_headers = [header_indexes[name] for name in ("Triggering finding", "Locked audit scope", "Output depth")]
    if ordered_headers != sorted(ordered_headers) or ordered_headers[0] <= report_index:
        fail("report headers must follow the report heading in canonical order")
    for left, right in zip([report_index] + ordered_headers, ordered_headers):
        if any(line.strip() for line in lines[left + 1:right]):
            fail("report heading and headers may be separated only by blank lines")

    heading_entries = [(index, line[4:].strip()) for index, line in enumerate(lines)
                       if line.startswith("### ")]
    headings = [heading for _, heading in heading_entries]
    expected = list(SECTIONS)
    if headers["Output depth"].lower() == "quick":
        expected.append("Omitted axes (quick mode only)")
    if headings != expected:
        fail("headings must be canonical, singleton, and ordered")

    sections = {}
    for index, heading in enumerate(headings):
        start = heading_entries[index][0] + 1
        end = heading_entries[index + 1][0] if index + 1 < len(headings) else len(lines)
        if any(line.strip() and not line.startswith("- ") for line in lines[start:end]):
            fail(f"{heading} payload must use bullets only")
        payload = [visible_text(line[2:].strip()) for line in lines[start:end] if line.startswith("- ")]
        if not payload:
            fail(f"{heading} needs a local bullet payload")
        if "None" in payload and payload != ["None"]:
            fail(f"{heading} cannot mix None with other bullets")
        if any(bullet != "None" and not visible(bullet) for bullet in payload):
            fail(f"{heading} bullets must contain visible text")
        if heading == "Out-of-scope candidates discovered" and payload != ["None"]:
            for bullet in payload:
                match = re.search(r"\bprovenance:\s*(.+)$", bullet, flags=re.I)
                if (not match or not populated_metadata(match[1])
                    or non_populated_metadata(match[1], "provenance")):
                    fail("out-of-scope bullets need populated provenance metadata")
        sections[heading] = payload

    first_section = heading_entries[0][0]
    if first_section <= ordered_headers[-1]:
        fail("report sections must follow the canonical headers")
    table_entries = [(index, line.strip(" \t")) for index, line in enumerate(lines)
                     if line.strip(" \t").startswith("|")]
    table_lines = [line for _, line in table_entries]
    rows = []
    if table_lines:
        if any(table_cells(line) is None for line in table_lines):
            fail("every table line must use leading and trailing pipes")
        if any(index <= ordered_headers[-1] or index >= first_section for index, _ in table_entries):
            fail("table must appear before report sections")
        table_indexes = [index for index, _ in table_entries]
        if table_indexes != list(range(table_indexes[0], table_indexes[-1] + 1)):
            fail("table lines must be contiguous")
        header_cells = ["Axis", "Candidate", "Presence", "Disposition", "Evidence"]
        header_indexes = [index for index, line in enumerate(table_lines)
                          if table_cells(line) == header_cells]
        separator_indexes = [index for index, line in enumerate(table_lines)
                             if table_cells(line) and table_separator(table_cells(line))]
        if len(header_indexes) != 1 or len(separator_indexes) != 1:
            fail("table must use canonical header and separator")
        if separator_indexes[0] != header_indexes[0] + 1:
            fail("table separator must follow the canonical header")
        if header_indexes[0] != 0:
            fail("canonical table header must be the first table line")
        if any(line.strip() for line in lines[ordered_headers[-1] + 1:table_indexes[0]]):
            fail("only blank lines may precede the table")
        if any(line.strip() for line in lines[table_indexes[-1] + 1:first_section]):
            fail("only blank lines may follow the table")
        for index, line in enumerate(table_lines):
            if index in (header_indexes[0], separator_indexes[0]):
                continue
            cells = [visible_text(cell) for cell in table_cells(line)]
            if len(cells) != 5:
                fail("table row must have five cells")
            if not visible(cells[4]):
                fail("candidate and evidence must be visibly substantive")
            item = dict(zip(("axis", "candidate", "presence", "disposition", "evidence"), cells))
            if item["axis"] not in AXES:
                fail("table axis must be a canonical catalogue axis")
            if item["presence"] not in PRESENCE_VALUES or item["disposition"] not in DISPOSITIONS:
                fail("table row has an invalid Presence or Disposition value")
            expected = {
                "present": {"fix-now", "defer-with-owner", "blocked"},
                "absent": {"n/a"},
                "n/a — structurally inapplicable": {"n/a"},
                "n/a — no candidates in scope": {"n/a"},
                "blocked — clarification needed": {"blocked"},
            }
            if item["disposition"] not in expected[item["presence"]]:
                fail("table Presence and Disposition values conflict")
            if not visible(item["candidate"]) and not (
                item["candidate"].strip() == "-" and item["presence"].startswith("n/a")
            ):
                fail("candidate must be named unless the row is n/a")
            evidence_raw = item["evidence"]
            evidence = norm(evidence_raw)
            explicit_artifact = re.search(
                r"`(?:\.[a-z0-9_.+-]+|[a-z0-9][a-z0-9_.+-]*)`",
                evidence_raw,
                flags=re.I,
            )
            citation = explicit_artifact or re.search(
                r"(?:[\w.-]+/)+[\w.-]+|"
                r"\b[a-z][a-z0-9 _/-]{2,} section\b|\b(?:dockerfile|makefile|readme|license)\b|"
                r"\b(?:test (?:file|case)|"
                r"(?:policy|api|json) spec|(?:json )?schema(?: artifact)?|migration(?: file)?|"
                r"config(?:uration)? (?:block|artifact)|(?:audit )?log(?: entry)?|incident(?: note)?|"
                r"triggering finding)\b",
                evidence,
            )
            n_a_reason = re.search(
                r"\b(?:in scope|locked scope|out of scope|structurally inapplicable|no candidates?)\b",
                evidence,
            )
            reason_allowed = item["presence"].startswith("n/a") or item["presence"] == "blocked — clarification needed"
            if not citation and not (reason_allowed and n_a_reason):
                fail("evidence must cite an artifact or an applicable n/a reason")
            rows.append(item)
        pairs = [(norm(row["axis"]), norm(row["candidate"])) for row in rows]
        if any(count > 1 for count in Counter(pairs).values()):
            fail("duplicate normalized axis/candidate pair")
    elif any(line.strip() for line in lines[ordered_headers[-1] + 1:first_section]):
        fail("only blank lines may separate report headers and sections")
    headers["_has_table"] = bool(table_lines)
    return headers, sections, rows


def row(rows, axis, candidate_terms=(), presence=None, disposition=None, excluded_terms=(), candidate_any=()):
    for item in rows:
        if norm(item["axis"]) != norm(axis):
            continue
        candidate = norm(item["candidate"])
        if candidate_terms and not all(norm(term) in candidate for term in candidate_terms):
            continue
        if candidate_any and not any(norm(term) in candidate for term in candidate_any):
            continue
        if any(norm(term) in candidate for term in excluded_terms):
            continue
        if presence and norm(item["presence"]) != norm(presence):
            continue
        if disposition and norm(item["disposition"]) != norm(disposition):
            continue
        return item
    fail(f"missing required {axis} row")


def standard_table(headers, rows, depth="standard"):
    if headers["Output depth"].lower() != depth:
        fail(f"expected {depth} output depth")
    if not rows:
        fail("complete report requires a table")
    if depth in ("standard", "exhaustive"):
        missing = [axis for axis in AXES if not any(norm(item["axis"]) == norm(axis) for item in rows)]
        if missing:
            fail(f"missing catalogue axes: {', '.join(missing)}")


def summary_assignments(candidates, bullets, section, one_to_one=False):
    if not candidates:
        if bullets != ["None"]:
            fail(f"{section} has a bullet without a compatible table row")
        return {}
    if bullets == ["None"]:
        fail(f"{section} cannot be None when table rows require it")
    if section == "Defects to fix now":
        for bullet in bullets:
            action = norm(bullet)
            for candidate in candidates:
                if candidate_named(candidate, bullet):
                    action = re.sub(
                        rf"(?<![a-z0-9_./-]){re.escape(norm(candidate))}(?![a-z0-9_/-]|\.[a-z0-9_])",
                        " ", action,
                    )
            if re.search(r"\b(?:do not fix|don't fix|need not fix|not fix|no action|skip)\b", action):
                fail(f"{section} cannot contain a negated action")
    elif section == "Deferred follow-ups":
        for bullet in bullets:
            action = norm(bullet)
            if re.search(
                r"\b(?:(?:do not|don't|never|not)\s+defer|"
                r"(?:skip|cancel)\s+(?:the\s+)?deferral)\b",
                action,
            ):
                fail(f"{section} cannot negate deferral")
    mentions_by_bullet = {
        bullet_index: mentioned_candidate_indexes(candidates, bullet)
        for bullet_index, bullet in enumerate(bullets)
    }
    matches = {
        candidate_index: sorted(
            (bullet_index for bullet_index, mentions in mentions_by_bullet.items()
             if candidate_index in mentions),
            key=lambda index: (len(norm(bullets[index])), index),
        )
        for candidate_index in range(len(candidates))
    }
    for candidate_index, matching in matches.items():
        if not matching:
            fail(f"{section} must name {candidates[candidate_index]}")

    if one_to_one:
        assignments = {}
        assigned_by_label = {}
        for bullet_index, bullet in enumerate(bullets):
            bullet_candidates = mentions_by_bullet[bullet_index]
            labels = {label_norm(candidates[index]) for index in bullet_candidates}
            if len(labels) != 1:
                fail(f"{section} bullets must each name exactly one candidate")
            label = labels.pop()
            label_candidates = [
                index for index, candidate in enumerate(candidates)
                if label_norm(candidate) == label
            ]
            used = assigned_by_label.get(label, 0)
            if used >= len(label_candidates):
                fail(f"{section} must use one bullet per candidate")
            candidate_index = label_candidates[used]
            assignments[candidate_index] = bullet_index
            assigned_by_label[label] = used + 1
        if len(assignments) != len(candidates):
            fail(f"{section} must use one bullet per candidate")
    else:
        assignments = {
            candidate_index: matching[0]
            for candidate_index, matching in matches.items()
        }
    for bullet in bullets:
        if not any(candidate_named(candidate, bullet) for candidate in candidates):
            fail(f"{section} has a bullet without a compatible table row")
    return assignments


def summary_bullet(candidates, bullets, candidate_index, section, one_to_one=False):
    assignments = summary_assignments(candidates, bullets, section, one_to_one)
    return bullets[assignments[candidate_index]]


def reconcile_summaries(sections, rows):
    dispositions_by_label = {}
    for item in rows:
        label = label_norm(item["candidate"])
        dispositions_by_label.setdefault(label, set()).add(item["disposition"])
    for label, dispositions in dispositions_by_label.items():
        if len(dispositions) > 1:
            fail(f"candidate label {label} has multiple dispositions")
    for disposition, section in (("fix-now", "Defects to fix now"),
                                 ("defer-with-owner", "Deferred follow-ups")):
        candidates = [item["candidate"] for item in rows
                      if item["presence"] == "present" and item["disposition"] == disposition]
        summary_assignments(candidates, sections[section], section)
    blocked = [item["candidate"] for item in rows if item["disposition"] == "blocked"]
    blocker_bullets = sections["Blocking questions"]
    if blocked and len(blocker_bullets) != len(blocked):
        fail("Blocking questions must contain one bullet per blocked row")
    assignments = summary_assignments(
        blocked, blocker_bullets, "Blocking questions", one_to_one=True
    )
    for candidate_index, bullet_index in assignments.items():
        candidate = blocked[candidate_index]
        if not requests(blocker_bullets[bullet_index]):
            fail(f"Blocking questions must name and request clarification for {candidate}")
    for bullet in blocker_bullets:
        if bullet == "None":
            continue
        if not requests(bullet):
            fail("each blocking question must request clarification")
    disposition_sections = {
        "fix-now": "Defects to fix now",
        "defer-with-owner": "Deferred follow-ups",
        "blocked": "Blocking questions",
    }
    all_candidates = [item["candidate"] for item in rows]
    for disposition, section in disposition_sections.items():
        for bullet in sections[section]:
            if bullet == "None":
                continue
            for candidate_index in mentioned_candidate_indexes(all_candidates, bullet):
                item = rows[candidate_index]
                if item["disposition"] != disposition:
                    fail(f"{section} must not name {item['candidate']} from another disposition")
    for bullet in sections["Deferred follow-ups"]:
        if bullet == "None":
            continue
        metadata = re.search(r"\bowner:\s*([^;]+);\s*reason:\s*(.+)$", bullet, flags=re.I)
        if not metadata or not all(populated_metadata(value) for value in metadata.groups()):
            fail("each deferred candidate bullet needs owner and reason metadata")
        if any(non_populated_metadata(value, field)
               for field, value in zip(("owner", "reason"), metadata.groups())):
            fail("deferred candidate metadata must be positive and populated")
    implications = [item["candidate"] for item in rows if item["presence"] == "present"
                    and item["axis"] in ("Test Mirror", "Documentation/Spec Prose Twin")]
    if implications and sections["Test/doc implications"] == ["None"]:
        fail("Test/doc implications cannot be None for present test/docs rows")
    mentioned_implications = set()
    for bullet in sections["Test/doc implications"]:
        mentioned_implications.update(mentioned_candidate_indexes(implications, bullet))
    for candidate_index, candidate in enumerate(implications):
        if candidate_index not in mentioned_implications:
            fail(f"Test/doc implications must name {candidate}")


def reduced(headers, sections, rows, missing_header, quick=False, expected_missing=None):
    if headers["_has_table"] or rows:
        fail("reduced report must not include a table")
    expected_missing = set(expected_missing or (missing_header,))
    for header in ("Triggering finding", "Locked audit scope"):
        is_missing = missing_header_marker(headers[header])
        if is_missing != (header in expected_missing):
            state = "missing" if header in expected_missing else "supplied"
            fail(f"{header} must remain {state}")
    for section in ("Defects to fix now", "Deferred follow-ups",
                    "Out-of-scope candidates discovered", "Test/doc implications"):
        if sections[section] != ["None"]:
            fail(f"reduced {section} must contain only None")
    if len(sections["Blocking questions"]) != 1:
        fail("reduced report needs exactly one blocking question")
    blockers = sections["Blocking questions"][0]
    if (not contains(blockers, missing_header.lower())
            or not requests(blockers)):
        fail("blocking question must name the missing required input")
    if quick:
        omitted = " ".join(sections["Omitted axes (quick mode only)"])
        if not any(term in omitted.lower() for term in ("missing", "required input", "triggering finding")) or not any(
            term in omitted.lower() for term in ("no axes", "not enumerated", "not expanded", "omitted")
        ):
            fail("quick reduced report needs a local omitted-axes explanation")


def validate(profile, headers, sections, rows):
    if profile != "positive-edge-009" and any(item["disposition"] == "defer-with-owner" for item in rows):
        fail("profile does not provide an explicit deferral boundary")
    if profile in PROFILE_HEADERS:
        for name, terms in zip(("Triggering finding", "Locked audit scope"), PROFILE_HEADERS[profile]):
            value = norm(headers[name])
            if missing_header_marker(value) or not all(norm(term) in value for term in terms):
                fail(f"{name} must preserve the supplied task input")
    if profile == "positive-edge-003":
        if headers["Output depth"].lower() != "standard":
            fail("expected standard output depth")
        reduced(
            headers, sections, rows, "Locked audit scope",
            expected_missing={"Locked audit scope"},
        )
        supplied = headers["Triggering finding"].lower()
        if missing_header_marker(supplied) or not all(term in supplied for term in (
            "security review", "delete /teams/{teamid}", "organization membership", "tenant ownership",
        )):
            fail("missing-scope report must preserve the supplied triggering finding")
    elif profile == "positive-edge-006":
        if headers["Output depth"].lower() != "quick":
            fail("expected quick output depth")
        reduced(
            headers, sections, rows, "Triggering finding", quick=True,
            expected_missing={"Triggering finding"},
        )
        supplied = headers["Locked audit scope"].lower()
        if missing_header_marker(supplied) or not all(
            term in supplied for term in ("src/pagination.ts", "tests/pagination.test.ts")
        ):
            fail("missing-finding report must preserve the supplied locked scope")
    elif profile == "positive-edge-011":
        if headers["Output depth"].lower() != "standard":
            fail("expected standard output depth")
        reduced(
            headers, sections, rows, "Triggering finding",
            expected_missing={"Triggering finding", "Locked audit scope"},
        )
        if not missing_header_marker(headers["Locked audit scope"]):
            fail("both-missing report must preserve the missing locked scope header")
    elif profile == "positive-edge-004":
        standard_table(headers, rows, "quick")
        reconcile_summaries(sections, rows)
        allowed = {"Opposite Bound", "Test Mirror", "Empty/Sentinel Equivalence"}
        if any(item["axis"] not in allowed for item in rows):
            fail("quick profile may include only target-specific rows")
        for axis, terms in (("Opposite Bound", ("zero",)), ("Test Mirror", ("zero",))):
            item = row(rows, axis, terms, "present", "fix-now")
            if not any(token in item["evidence"].lower() for token in ("src/pagination.ts", "tests/pagination.test.ts", "triggering finding")):
                fail(f"{axis} needs scoped evidence")
            row(rows, "Empty/Sentinel Equivalence", ("zero",), "present", "fix-now")
        omitted = " ".join(sections["Omitted axes (quick mode only)"]).lower()
        if "omitted" not in omitted or not any(term in omitted for term in ("scope", "inapplicable", "material")):
            fail("quick report needs an omitted-axis reason")
    else:
        standard_table(headers, rows, "exhaustive" if profile == "positive-edge-007" else "standard")
        reconcile_summaries(sections, rows)

    if profile == "positive-edge-001":
        row(rows, "Opposite Bound", ("timeoutseconds",), "present", "fix-now")
        for axis in ("Sibling Parameter/Field", "Inverse Operation", "Permission/Authorization Class",
                     "Resource Cleanup", "Async/Sync or Mode Twin", "Cache/Projection/Source-of-Truth Twin"):
            matches = [item for item in rows if item["axis"] == axis]
            if len(matches) != 1:
                fail(f"{axis} must have exactly one no-candidate row")
            item = matches[0]
            if item["presence"] not in ("n/a — structurally inapplicable", "n/a — no candidates in scope") or item["disposition"] != "n/a":
                fail(f"{axis} must be an explicit n/a row")
        row(rows, "Documentation/Spec Prose Twin", ("docs",), "present", "fix-now")
    elif profile == "positive-edge-002":
        delete_row = row(rows, "Permission/Authorization Class", ("delete",),
                         "blocked — clarification needed", "blocked")
        row(rows, "Mirror Call Site/Use Site", ("get", "tenantguard"), "absent", "n/a")
        row(rows, "Test Mirror", ("tenant mismatch",), "present", "fix-now")
        blocked_rows = [item for item in rows if item["disposition"] == "blocked"]
        delete_index = next(index for index, item in enumerate(blocked_rows) if item is delete_row)
        blocker = summary_bullet(
            [item["candidate"] for item in blocked_rows],
            sections["Blocking questions"],
            delete_index,
            "Blocking questions",
            one_to_one=True,
        )
        if (not all(term in blocker.lower() for term in (
                "tenantguard", "tenant ownership", "policy spec"))
            or not requests(blocker)):
            fail("authorization blocker must name tenantGuard, ownership, and policy spec")
        out_of_scope = sections["Out-of-scope candidates discovered"]
        for term in ("tenantguard", "policy"):
            matching = [bullet for bullet in out_of_scope if term in bullet.lower()]
            if len(matching) != 1 or "provenance" not in matching[0].lower():
                fail(f"out-of-scope section must report {term} with provenance")
    elif profile == "positive-edge-005":
        docs_rows = [item for item in rows if norm(item["axis"]) == norm("Documentation/Spec Prose Twin")]
        if len(docs_rows) != 1:
            fail("expected one documentation candidate")
        item = docs_rows[0]
        if item["presence"] != "present" or item["disposition"] != "blocked":
            fail("documentation candidate must remain present and blocked")
        row(rows, "Opposite Bound", ("maxretries",), "present", "fix-now")
        if sections["Deferred follow-ups"] != ["None"]:
            fail("blocked deferral must not appear in deferred follow-ups")
        if any(candidate_named(item["candidate"], bullet)
               for bullet in sections["Defects to fix now"]):
            fail("blocked documentation must not appear in fix-now summary")
        blocked_rows = [candidate for candidate in rows if candidate["disposition"] == "blocked"]
        item_index = next(index for index, candidate in enumerate(blocked_rows) if candidate is item)
        blocker = summary_bullet(
            [candidate["candidate"] for candidate in blocked_rows],
            sections["Blocking questions"],
            item_index,
            "Blocking questions",
            one_to_one=True,
        ).lower()
        if not all(term in blocker for term in ("doc", "owner", "reason")) or not requests(blocker):
            fail("documentation blocker must request owner and reason")
    elif profile == "positive-edge-007":
        row(rows, "Opposite Bound", presence="present", disposition="fix-now",
            candidate_any=("minitems", "zero"))
        row(rows, "Sibling Parameter/Field", ("maxitems",))
        mirror_rows = [item for item in rows if item["axis"] == "Mirror Call Site/Use Site"]
        synchronous = [item for item in mirror_rows
                   if has_mode_term(item["candidate"], "sync")
                   and not has_mode_term(item["candidate"], "async")]
        asynchronous = [item for item in mirror_rows
                if has_mode_term(item["candidate"], "async")]
        if len(synchronous) != 1 or len(asynchronous) != 1 or any(
            item["presence"] != "present" or item["disposition"] != "fix-now"
            or "validator" not in item["candidate"].lower()
            for item in synchronous + asynchronous
        ):
            fail("exhaustive report needs separate sync and async validator call sites")
        mode_rows = [item for item in rows if item["axis"] == "Async/Sync or Mode Twin"
                     and has_mode_term(item["candidate"], "async")
                     and item["presence"] == "present" and item["disposition"] == "fix-now"]
        if len(mode_rows) != 1:
            fail("exhaustive report needs one async mode candidate")
        zero = row(rows, "Test Mirror", ("zero",), "present", "fix-now")
        async_tests = [item for item in rows if item["axis"] == "Test Mirror"
                       and has_mode_term(item["candidate"], "async")
                       and item["presence"] == "present" and item["disposition"] == "fix-now"]
        if len(async_tests) != 1:
            fail("exhaustive report needs one async Test Mirror candidate")
        async_row = async_tests[0]
        if has_mode_term(zero["candidate"], "async") or "zero" in async_row["candidate"].lower():
            fail("zero and async Test Mirror candidates must be distinct")
        row(rows, "Documentation/Spec Prose Twin", ("zero",), "present", "fix-now")
    elif profile == "positive-edge-008":
        row(rows, "Opposite Bound", ("maxretries",), "present", "fix-now")
        docs_rows = [item for item in rows if norm(item["axis"]) == norm("Documentation/Spec Prose Twin")]
        if len(docs_rows) != 2:
            fail("expected separate API and operations documentation candidates")
        for document, need in (("docs/api.md", "reason"), ("docs/operations.md", "owner")):
            other = "docs/operations.md" if document == "docs/api.md" else "docs/api.md"
            document_row = row(rows, "Documentation/Spec Prose Twin", (document,), "present", "blocked", (other,))
            blocked_rows = [item for item in rows if item["disposition"] == "blocked"]
            document_index = next(index for index, item in enumerate(blocked_rows)
                                  if item is document_row)
            blocker = summary_bullet(
                [item["candidate"] for item in blocked_rows],
                sections["Blocking questions"],
                document_index,
                "Blocking questions",
                one_to_one=True,
            ).lower()
            if need not in blocker or not requests(blocker):
                fail(f"{document} needs a separate blocker requesting {need}")
        if sections["Deferred follow-ups"] != ["None"]:
            fail("blocked docs must not appear in deferred follow-ups")
        if any(candidate_named(item["candidate"], bullet)
               for item in docs_rows
               for bullet in sections["Defects to fix now"]):
            fail("blocked docs must not appear in fix-now summary")
    elif profile == "positive-edge-009":
        row(rows, "Opposite Bound", ("maxretries",), "present", "fix-now")
        docs_row = row(rows, "Documentation/Spec Prose Twin", ("docs/api.md",),
                       "present", "defer-with-owner")
        deferred_rows = [item for item in rows
                         if item["presence"] == "present" and item["disposition"] == "defer-with-owner"]
        if len(deferred_rows) != 1 or deferred_rows[0] is not docs_row:
            fail("documentation must be the only deferred candidate")
        deferred = summary_bullet(
            [item["candidate"] for item in deferred_rows],
            sections["Deferred follow-ups"],
            0,
            "Deferred follow-ups",
        )
        if not all(term in deferred.lower() for term in ("docs/api.md", "platform docs")):
            fail("deferred follow-up must contain the docs path and owner")
    elif profile == "positive-edge-010":
        if any(item["presence"] not in (
            "absent", "n/a — structurally inapplicable", "n/a — no candidates in scope",
        ) for item in rows):
            fail("clean audit may contain only absent or n/a rows")
        if any(sections[section] != ["None"] for section in SECTIONS):
            fail("clean audit summaries must contain only None")
    elif profile == "positive-trigger-001":
        row(rows, "Opposite Bound", ("maxretries", "upper"), "present", "fix-now")
        row(rows, "Sibling Parameter/Field", ("retrydelayseconds",), "present", "fix-now")
        row(rows, "Empty/Sentinel Equivalence", ("null",), "present", "fix-now")
        test_rows = [item for item in rows if item["axis"] == "Test Mirror"
                     and item["presence"] == "present" and item["disposition"] == "fix-now"]
        used = set()
        for term in ("upper", "retrydelayseconds", "null"):
            match = next((index for index, item in enumerate(test_rows)
                          if index not in used and term in item["candidate"].lower()), None)
            if match is None:
                fail("trigger-001 requires distinct Test Mirror candidates")
            used.add(match)
        item = row(rows, "Documentation/Spec Prose Twin", ("docs/operations.md",), "present", "fix-now")
        if not visible(item["evidence"]):
            fail("documentation row needs substantive evidence")
    elif profile == "positive-trigger-002":
        export = row(rows, "Permission/Authorization Class", ("export",), "present", "fix-now",
                 excluded_terms=("archive",))
        if "can_export" not in export["evidence"].lower():
            fail("export candidate needs can_export evidence")
        row(rows, "Permission/Authorization Class", ("archive",), "present", "fix-now",
            excluded_terms=("export",))
        report = row(rows, "Permission/Authorization Class", ("report",), "absent", "n/a")
        if "can_view_report" not in report["evidence"].lower():
            fail("report candidate needs can_view_report evidence")
        row(rows, "Observability Twin", ("denied",), "present", "fix-now")
        row(rows, "Test Mirror", ("export", "denied"), "present", "fix-now", ("archive",))
        row(rows, "Test Mirror", ("archive", "denied"), "present", "fix-now", ("export",))
        row(rows, "Documentation/Spec Prose Twin", ("archive",), "present", "fix-now")


def main():
    if len(sys.argv) != 2:
        fail("usage: check-report.py <task-id>")
    if sys.argv[1] not in PROFILES:
        fail("unknown task profile")
    output = parse_output()
    headers, sections, rows = parse_report(output)
    validate(sys.argv[1], headers, sections, rows)


if __name__ == "__main__":
    main()