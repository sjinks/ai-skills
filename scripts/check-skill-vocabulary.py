#!/usr/bin/env python3
"""Check canonical skill severity declarations; never run models or skill commands."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
LEVELS = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
SENTINELS = {"NONE", "UNASSESSED"}
LEGACY = "Critical|High|Medium|Low|critical|high|medium|low|error|warning|information|blocker|should-fix|suggestion"
FIELD = re.compile(r"^\s*(?:-\s*)?Severity:\s*(.*)$")
NAMED_ENUM = re.compile(r"`FINDING_SEVERITY`\s*[-—]\s*one of\s+(.*)")
ATOM = r"(?:`+[^`]+`+|\*\*[^*]+\*\*|[A-Za-z_][A-Za-z0-9_-]*)"
SEPARATOR = r"(?:\s*\|\s*|\s*,\s*(?:or\s+)?|\s+or\s+)"
ENUM = re.compile(rf"{ATOM}(?:{SEPARATOR}{ATOM})*\.?$")
FORMATTED = r"(?:`+[^`]+`+|\*\*[^*]+\*\*)"
FIRST_DEFINITION = re.compile(rf"({FORMATTED})\s+(?:means|for)\b")
PROSE_DEFINITION = re.compile(rf"(?:^|[;,]\s*(?:(?:and|or)\s+)?)({FORMATTED})\s+(?:means|for)\b")
BULLET_DEFINITION = re.compile(rf"^\s*-\s+({ATOM})\s*:")
HEADING = re.compile(r"^(#{1,6})\s+(.*)")
COVERAGE_STATES = {"covered", "gap", "not-assessed", "n/a"}
COVERAGE_ENUM = re.compile(r":\s*<?(covered\s*\|[^\n]+)")
CLASSIFICATION_FIELD = re.compile(r"^\s*(?:-\s*)?Classification:\s*(.*)$")
ACTION_CLASSIFICATIONS = {
    "blocker", "required test", "follow-up", "accepted tradeoff", "not applicable",
    "fix-now", "add-verification", "clarify", "defer-with-owner", "retain-accepted",
}
FINDING_STATE_REPORTS = {"code-quality", "review-cycle-gatekeeper"}
OLD_RUBRIC = re.compile(rf"^\s*-\s+(?:`({LEGACY})`|\*\*({LEGACY}):\*\*)\s*:?")
OLD_ENTRY = re.compile(
    rf"(?:Title|Body|Footers|Input|Convention|Structure|Disclosure):\s*(?:{LEGACY})(?:\s|$)"
)
# Legacy inputs may appear in compatibility tables and prose, never emitted fields.
OLD_OUTPUT = re.compile(
    rf"Severity:\s*`?(?:{LEGACY})(?:`|\s|\||$)|"
    rf"FINDING_SEVERITY.*one of.*`(?:{LEGACY})`|"
    r"Input/(?:error|information)|Body: information|Convention: information|"
    r"by severity: critical|— (?:high|medium|low|none):|"
    r"Errors: (?:ERROR_COUNT|0|Not assessed)|"
    r"Warnings: (?:WARNING_COUNT|0|Not assessed)|"
    r"Informational findings: (?:INFORMATIONAL_FINDING_COUNT|0|Not assessed)"
)


def unformat(value):
    """Remove one matching Markdown code/bold wrapper, not literal word content."""
    code = re.fullmatch(r"(`+)([^`]+)\1", value)
    if code:
        return code[2]
    bold = re.fullmatch(r"\*\*([^*]+)\*\*", value)
    if bold:
        return bold[1].rstrip(":")
    return value


def literal_members(value):
    value = unformat(value.strip())
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1].strip()
        # A descriptive slot is not an enum. Template alternatives are literals.
        if not re.search(r"\||,|\sor\s", value):
            return None
    if value == "FINDING_SEVERITY" or not ENUM.fullmatch(value):
        return None  # Exact schema placeholder or explanatory prose.
    return [unformat(match[1]) for match in re.finditer(
        rf"(?:^|{SEPARATOR})({ATOM})", value.rstrip(".")
    )]


def check_members(members, location, errors, *, complete):
    values = set(members)
    if not values <= LEVELS | SENTINELS:
        errors.append(f"{location}: invalid literal Severity values: {', '.join(members)}")
    if complete and values - SENTINELS and not LEVELS <= values:
        errors.append(f"{location}: missing four-level severity vocabulary in this declaration")


def check_shared_states(line, location, errors, *, finding_lifecycle):
    plain = line.replace("`", "").replace("**", "").replace(r"\|", "|")
    for match in COVERAGE_ENUM.finditer(plain):
        values = {
            re.sub(r"\s*\([^)]*\)\s*$", "", value).strip(" <>.")
            for value in match[1].split("|")
        }
        if values != COVERAGE_STATES:
            errors.append(f"{location}: incomplete or obsolete checklist coverage enum")
    classification = CLASSIFICATION_FIELD.match(plain)
    if classification:
        values = {value.strip().strip("<>") for value in classification[1].split("|")}
        if values & (ACTION_CLASSIFICATIONS | {"Needs more evidence"}):
            errors.append(f"{location}: action or missing-evidence label in Classification field")
    if finding_lifecycle and re.match(r"^\s*(?:Status|State):\s*(?:Open|Resolved|owned-with-remediation-plan|waived-with-rationale)(?:\s|$)", plain):
        errors.append(f"{location}: legacy emitted finding state")
    if re.search(r"\bFindings:\s+none(?:[.\s]|$)", plain):
        errors.append(f"{location}: use the canonical Findings: None marker")


def inspect_package(package):
    errors = []
    emits = False
    for path in sorted(package.rglob("*.md")):
        text = path.read_text()
        emits |= bool(re.search(r"^#{2,3} .*Severity|^\s*(?:-\s*)?Severity:", text, re.M))
        axis = None
        rubric = []
        rubric_line = 0
        fence = None

        def finish_rubric():
            if rubric and path.name != "README.md":
                # Outside a named severity section, only a run containing an
                # impact label is a rubric; arbitrary domain lists are not.
                if axis == "severity" or set(rubric) & LEVELS:
                    check_members(rubric, f"{path.relative_to(ROOT)}:{rubric_line}", errors, complete=True)
            rubric.clear()

        for number, line in enumerate(text.splitlines(), 1):
            location = f"{path.relative_to(ROOT)}:{number}"
            check_shared_states(line, location, errors, finding_lifecycle=package.name in FINDING_STATE_REPORTS)
            delimiter = re.match(r"^\s*(`{3,}|~{3,})", line)
            if delimiter:
                if fence is None:
                    finish_rubric()
                    fence = delimiter[1]
                elif delimiter[1][0] == fence[0] and len(delimiter[1]) >= len(fence):
                    fence = None
                continue
            heading = HEADING.match(line) if fence is None else None
            if heading:
                title = heading[2]
                label_heading = axis == "severity" and re.fullmatch(FORMATTED, title)
                if not label_heading:
                    finish_rubric()
                    axis = "severity" if re.search(r"\bSeverity\b", title) else None
                if re.search(r"\bConfidence\b", title, re.I):
                    finish_rubric()
                    axis = "confidence"
                if label_heading:
                    if not rubric:
                        rubric_line = number
                    rubric.append(unformat(title))
            if re.search(r"Use confidence|confidence label", line, re.I):
                finish_rubric()
                axis = "confidence"
            if re.match(r"\s*(?:Verdicts?:|Verdict mapping|Verdict precedence|Use .*verdict)", line, re.I):
                finish_rubric()
                axis = None
            if (axis == "severity" and OLD_RUBRIC.search(line)) or OLD_ENTRY.search(line) or OLD_OUTPUT.search(line):
                errors.append(f"{location}: obsolete emitted severity or summary label")
            field = FIELD.match(line) or NAMED_ENUM.search(line)
            if field:
                members = literal_members(field[1])
                if members is not None:
                    check_members(members, location, errors, complete=len(members) > 1)
            if fence is not None or heading or axis == "confidence":
                continue
            bullet = BULLET_DEFINITION.match(line)
            first = FIRST_DEFINITION.search(line)
            definitions = [] if first is None else [
                unformat(match[1]) for match in PROSE_DEFINITION.finditer(line[first.start():])
            ]
            if bullet:
                label = unformat(bullet[1])
                if label in {"BLOCK", "CONCERNS", "CLEAN"} or not (
                    re.fullmatch(r"[A-Z][A-Z_-]*", label) or label in LEGACY.split("|")
                ):
                    finish_rubric()
                    axis = None
                    continue
                if not rubric:
                    rubric_line = number
                rubric.append(unformat(bullet[1]))
            elif len(definitions) >= 2 and re.search(r"severity", line, re.I):
                finish_rubric()
                check_members(definitions, location, errors, complete=True)
            elif rubric and line.strip() and axis != "severity":
                finish_rubric()
        finish_rubric()
    return emits, errors


def main():
    packages = sorted(path.parent for path in (ROOT / "skills").glob("*/SKILL.md"))
    errors = []
    producers = []
    for package in packages:
        emits, findings = inspect_package(package)
        if emits:
            producers.append(package.name)
        errors.extend(findings)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Vocabulary check passed: {len(packages)} packages; {len(producers)} with severity sections/fields.")
    print("Static declarations only; domain semantics and legacy-input mappings require review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
