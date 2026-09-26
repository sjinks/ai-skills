#!/usr/bin/env python3
"""Validate the stable factcheck report contract from Waza stdin."""
import re
import sys

SECTIONS = (
    "Fact-Check Summary", "Scope", "Claims Checked", "Evidence Reviewed",
    "Findings", "Recommended Corrections", "Open Questions",
    "Verification Limits", "Residual Uncertainty",
)
VERDICTS = {"SUPPORTED", "MOSTLY_SUPPORTED", "MIXED", "UNSUPPORTED", "CONTRADICTED", "UNVERIFIABLE", "NOT_A_FACTUAL_CLAIM"}
CONFIDENCE = {"high", "medium", "low"}
ACCESS = {"supplied-only", "approved retrieval", "insufficient authorization"}
SUPPORT = {"direct", "partial", "contextual", "none"}
CLASSES = {"identity/date", "quantity", "comparison", "causal", "universal/scope", "current-state", "verbatim quotation", "other"}


def fail(message):
    print(message, file=sys.stderr)
    raise SystemExit(1)


def section(text, name, following):
    pattern = rf"(?ms)^{re.escape(name)}\s*$\n(.*?)(?=^{re.escape(following)}\s*$)"
    match = re.search(pattern, text)
    if not match:
        fail(f"missing or misplaced {name}")
    return match.group(1)


def values(block, label):
    return re.findall(rf"(?mi)^\s*(?:-\s*)?{re.escape(label)}:\s*(\S.*)$", block)


def validate(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    headings = re.findall(r"(?m)^([^\n]+)$", text)
    found = [line for line in headings if line in SECTIONS]
    if found != list(SECTIONS) or not text.startswith("Fact-Check Summary\n"):
        fail("sections must be unique, ordered, and begin the response")
    blocks = {name: section(text, name, SECTIONS[index + 1])
              for index, name in enumerate(SECTIONS[:-1])}
    blocks[SECTIONS[-1]] = text.split("Residual Uncertainty\n", 1)[1]
    access = values(blocks["Scope"], "Evidence access")
    if len(access) != 1 or access[0] not in ACCESS:
        fail("Scope must contain one canonical Evidence access value")
    claims = re.findall(r"(?m)^- (C\d+):\s*\S.+$", blocks["Claims Checked"])
    if not claims or len(claims) != len(set(claims)):
        fail("Claims Checked must contain unique C IDs")
    if len(values(blocks["Claims Checked"], "Claim class")) != len(claims):
        fail("each claim needs one Claim class")
    for item in values(blocks["Claims Checked"], "Claim class"):
        if any(value not in CLASSES for value in re.split(r"\s*,\s*", item)):
            fail("Claim class must use canonical values")
    evidence = re.findall(r"(?m)^- (E\d+):\s*\S.+$", blocks["Evidence Reviewed"])
    if not evidence or len(evidence) != len(set(evidence)):
        fail("Evidence Reviewed must contain unique E IDs")
    for label in ("Type", "Date/currentness", "Locator", "Claim support", "Relevance", "Limitation"):
        if len(values(blocks["Evidence Reviewed"], label)) != len(evidence):
            fail(f"each evidence item needs one {label}")
    for item in values(blocks["Evidence Reviewed"], "Claim support"):
        if item.split(",", 1)[0].strip() not in SUPPORT:
            fail("Claim support must begin with a canonical value")
    findings = re.findall(r"(?m)^- (C\d+)\s*$", blocks["Findings"])
    corrections = re.findall(r"(?m)^- (C\d+):\s*\S.+$", blocks["Recommended Corrections"])
    if findings != claims or corrections != claims:
        fail("Findings and Recommended Corrections must cover each claim once in order")
    for label, allowed in (("Verdict", VERDICTS), ("Confidence", CONFIDENCE)):
        items = values(blocks["Findings"], label)
        if len(items) != len(claims) or any(item not in allowed for item in items):
            fail(f"each finding needs a canonical {label}")
    for label in ("Confidence reason", "Evidence", "Reasoning"):
        if len(values(blocks["Findings"], label)) != len(claims):
            fail(f"each finding needs one {label}")
    if re.search(r"\n\S", blocks["Residual Uncertainty"]):
        fail("trailing prose is not allowed after Residual Uncertainty")


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"positive-(?:trigger|edge)-\d{3}", sys.argv[1]):
        fail("usage: check-report.py <positive task id>")
    validate(sys.stdin.read())


if __name__ == "__main__":
    main()
