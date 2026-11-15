#!/usr/bin/env python3
"""Check canonical skill severity declarations; never run models or skill commands."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
LEVELS = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
LEGACY = "Critical|High|Medium|Low|critical|high|medium|low|error|warning|information|blocker|should-fix|suggestion"
FIELD = re.compile(r"^\s*(?:-\s*)?Severity:\s*(.*)$")
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


def inspect_package(package):
    errors = []
    sources = sorted(package.rglob("*.md"))
    combined = "\n".join(path.read_text() for path in sources)
    # Match declared severity sections/fields, not incidental mentions or log levels.
    emits = bool(re.search(r"^#{2,3} Severity|^\s*(?:-\s*)?Severity:", combined, re.M))
    if emits and not all(re.search(rf"\b{level}\b", combined) for level in LEVELS):
        errors.append(f"{package.relative_to(ROOT)}: missing four-level severity vocabulary")
    for path in sources:
        axis = None
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if line.startswith("#"):
                axis = "severity" if re.search(r"\bSeverity\b", line) else None
            if re.search(r"Use confidence|confidence label", line, re.I):
                axis = "confidence"
            location = f"{path.relative_to(ROOT)}:{number}"
            if (axis == "severity" and OLD_RUBRIC.search(line)) or OLD_ENTRY.search(line) or OLD_OUTPUT.search(line):
                errors.append(f"{location}: obsolete emitted severity or summary label")
            field = FIELD.match(line)
            if field:
                value = field[1].strip()
                # Placeholders are governed by the containing report contract.
                if value.startswith(("<", "`", "FINDING_SEVERITY")):
                    continue
                values = set(re.split(r"\s*\|\s*", value))
                if not values <= LEVELS | {"NONE", "UNASSESSED"}:
                    errors.append(f"{location}: invalid literal Severity field: {value}")
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
