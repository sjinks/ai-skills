#!/usr/bin/env python3
"""Validate single or repeated per-test quality reports without calling a model."""
from __future__ import annotations

import argparse
import re
import sys

MARKERS = ("Verdict:", "Findings:", "Authored test:")
PROFILES = {"review", "author", "missing"}
WIRE_PATTERN = r"TEST\(\s*FrameTest\s*,\s*SerializesPingFrame\s*\)\s*\{\s*Frame\s+frame\s*=\s*Frame::ping\(0x1234\)\s*;\s*auto\s+bytes\s*=\s*serialize\(frame\)\s*;\s*EXPECT_EQ\(\s*bytes\s*,\s*std::vector<uint8_t>\(\s*\{0x09,\s*0x00,\s*0x12,\s*0x34\}\s*\)\s*\)\s*;\s*\}"
WIRE_CODE = "TEST(FrameTest, SerializesPingFrame) {\n  Frame frame = Frame::ping(0x1234);\n  auto bytes = serialize(frame);\n  EXPECT_EQ(bytes, std::vector<uint8_t>({0x09, 0x00, 0x12, 0x34}));\n}"
VERDICTS = {"solid", "weak", "cannot-fail", "insufficient-context"}


def validate_one(text: str, profile: str, labels: tuple[str, ...] = (), expected: str | None = None, wire_fixture: bool = False) -> None:
    """Validate marker cardinality, order, domains, branch and termination.

    Findings use file/snippet location syntax; authored code is fenced last.
    """
    if wire_fixture and profile != "author":
        raise ValueError("wire fixture requires author profile")
    if profile not in PROFILES:
        raise ValueError("unknown profile")
    active = MARKERS if profile == "author" else MARKERS[:2]
    labels = labels or active
    if len(labels) != len(active) or len(set(labels)) != len(labels) or any(not label.endswith(":") or "\n" in label for label in labels):
        raise ValueError("invalid caller labels")
    text = text.replace("\r\n", "\n").replace("\r", "\n").rstrip()
    lines = text.split("\n")
    envelope = lines
    if profile == "author":
        authored = next((i for i, line in enumerate(lines) if line.startswith(labels[2])), None)
        if authored is None:
            raise ValueError("missing authored-code label")
        envelope = lines[:authored + 1]
    if any(line.startswith(marker) for line in envelope for marker in MARKERS if marker not in labels):
        raise ValueError("inactive or replaced marker")
    positions = []
    for label in labels:
        matches = [i for i, line in enumerate(envelope) if line.startswith(label)]
        if len(matches) != 1:
            raise ValueError("marker must occur exactly once")
        positions.append(matches[0])
    if positions[0] != 0 or positions != sorted(positions) or positions[1] != 1:
        raise ValueError("report must start with ordered verdict and findings")
    verdict = lines[0][len(labels[0]):].strip()
    if verdict not in VERDICTS or (verdict == "insufficient-context") != (profile == "missing"):
        raise ValueError("invalid verdict for profile")
    if expected is not None and verdict != expected:
        raise ValueError("wrong task verdict")
    end = positions[2] if profile == "author" else len(lines)
    findings = lines[1:end]
    first = findings[0][len(labels[1]):].strip()
    if profile == "missing":
        if len(findings) != 1 or not re.fullmatch(r"Missing: \S.*", first):
            raise ValueError("missing input must be named in one line")
    elif verdict == "solid":
        if len(findings) != 1 or not re.fullmatch(r"None\. \S.*", first):
            raise ValueError("solid requires no findings and justification")
    else:
        if first or len(findings) < 2:
            raise ValueError("weak/cannot-fail requires finding bullets")
        for line in findings[1:]:
            fields = line.split(" | ")
            if len(fields) != 4 or not re.fullmatch(r"- [1-6]", fields[0]) or any(not value.strip() or "|" in value for value in fields[1:]):
                raise ValueError("invalid numbered finding")
            if not re.fullmatch(r"\S(?:.*\S)?:[1-9][0-9]*", fields[1]):
                raise ValueError("finding location requires a file/snippet and line")
            if profile == "review" and fields[1].startswith("generated snippet:"):
                raise ValueError("review cannot cite ungenerated code")
    if profile == "author":
        code = lines[end:]
        if code[0] != labels[2] or len(code) < 4 or not re.fullmatch(r"```[A-Za-z0-9_+-]*", code[1]) or code[-1] != "```":
            raise ValueError("authored code must be a final fenced block")
        if not any(line.strip() for line in code[2:-1]) or any(line.startswith("```") for line in code[2:-1]):
            raise ValueError("authored code must be one nonempty block")
        if wire_fixture:
            uncommented = re.sub(r"/\*.*?\*/|//[^\n]*", "", "\n".join(code[2:-1]), flags=re.DOTALL).strip()
            if not re.fullmatch(WIRE_PATTERN, uncommented, re.DOTALL):
                raise ValueError("wire fixture requires the constructed executable test")
        for line in findings[1:]:
            location = line.split(" | ")[1]
            if wire_fixture and not location.startswith("generated snippet:"):
                raise ValueError("wire fixture has no source file; cite generated snippet")
            if location.startswith("generated snippet:") and int(location.rsplit(":", 1)[1]) > len(code[2:-1]):
                raise ValueError("generated snippet line out of bounds")


def validate(text: str, profile: str, labels: tuple[str, ...] = (), expected: str | None = None, wire_fixture: bool = False, test_count: int = 1, verdicts: tuple[str, ...] = ()) -> None:
    """Frame repeated review reports and validate each one independently.

    Authoring invocations remain singular. Batch expectations
    are optional outside task fixtures; report count is always explicit here.
    """
    if wire_fixture and profile != "author":
        raise ValueError("wire fixture requires author profile")
    if type(test_count) is not int or test_count < 1 or (test_count != 1 and profile != "review"):
        raise ValueError("multiple reports require review profile and positive test count")
    if verdicts and (expected is not None or len(verdicts) != test_count or any(value not in VERDICTS for value in verdicts)):
        raise ValueError("per-test verdicts must match the report count")
    if test_count == 1:
        validate_one(text, profile, labels, verdicts[0] if verdicts else expected, wire_fixture)
        return
    active = labels or MARKERS[:2]
    if len(active) != 2:
        raise ValueError("review requires two labels")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").rstrip().split("\n")
    starts = [index for index, line in enumerate(lines) if line.startswith(active[0])]
    if len(starts) != test_count or starts[0] != 0:
        raise ValueError("report count or first marker mismatch")
    if any(lines[start - 1].strip() for start in starts[1:]):
        raise ValueError("separate review reports with a blank line")
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        report = "\n".join(lines[start:end])
        report_verdict = lines[start][len(active[0]):].strip()
        report_profile = "missing" if report_verdict == "insufficient-context" else "review"
        validate_one(report, report_profile, active, verdicts[index] if verdicts else expected)


VALID = {
    "review": "Verdict: cannot-fail\nFindings:\n- 1 | supplied snippet:4 | self-comparison | assert expected 900",
    "author": "Verdict: solid\nFindings: None. Exact bytes match the wire contract.\nAuthored test:\n```cpp\nTEST(FrameTest, SerializesPingFrame) { EXPECT_EQ(serialize(Frame::ping(0x1234)), expected); }\n```",
    "missing": "Verdict: insufficient-context\nFindings: Missing: expected result",
}


def self_test() -> None:
    """Exercise each branch and the required omission/crossover mutations.

    Caller replacements and generated snippet provenance use the same grammar.
    """
    for profile, text in VALID.items():
        active = MARKERS if profile == "author" else MARKERS[:2]
        custom = ("Decision:", "Quality notes:", "Generated code:")[:len(active)]
        for labels in (active, custom):
            candidate = text
            for old, new in zip(active, labels):
                candidate = candidate.replace(old, new)
            validate(candidate, profile, labels)
            validate(candidate + "\n", profile, labels)
            mutations = ["\n" + candidate, " " + candidate, candidate + "\nTrailing prose.", candidate.replace(labels[0], labels[0] + " bad-enum", 1)]
            for label in labels:
                mutations.extend([candidate.replace(label, "Omitted:", 1), candidate + "\n" + label])
            lines = candidate.splitlines()
            mutations.append("\n".join([lines[1], lines[0]] + lines[2:]))
            for mutation in mutations:
                try:
                    validate(mutation, profile, labels)
                except ValueError:
                    continue
                raise AssertionError((profile, "accepted mutation", mutation))
        for other in PROFILES - {profile}:
            try:
                validate(text, other)
            except ValueError:
                continue
            raise AssertionError((profile, other, "accepted crossover"))
    validate("Verdict: solid\nFindings: None. Exact bytes are the specified wire contract; keep strict assertions.", "review")
    # Report-looking literals inside a code fence are data, including replaced labels.
    literal_code = 'TEST(ParserTest, KeepsReportText) {\nconst char* text = R"(\nVerdict: solid\nFindings: None.\nAuthored test:\nDecision: solid\nQuality notes: None.\nGenerated code:\n)";\nEXPECT_EQ(parse(text), expected);\n}'
    for verdict in ("solid", "weak", "cannot-fail"):
        findings = "Findings: None. Parser result matches its contract." if verdict == "solid" else "Findings:\n- 6 | generated snippet:1 | vague name | describe the promised parsing result"
        literal_report = "Verdict: " + verdict + "\n" + findings + "\nAuthored test:\n```cpp\n" + literal_code + "\n```"
        for labels in (MARKERS, ("Decision:", "Quality notes:", "Generated code:")):
            envelope, code = literal_report.split("```cpp", 1)
            for old, new in zip(MARKERS, labels):
                envelope = envelope.replace(old, new)
            candidate = envelope + "```cpp" + code
            validate(candidate, "author", labels)
            for mutation in (candidate.replace(labels[2] + "\n```", labels[2] + "\n" + labels[2] + "\n```", 1), candidate + "\n" + labels[0], candidate.replace("\n```cpp", "\nVerdict: solid\n```cpp", 1)):
                try:
                    validate(mutation, "author", labels)
                except ValueError:
                    continue
                raise AssertionError("accepted report-envelope mutation")
    weak = VALID["review"].replace("cannot-fail", "weak")
    validate(weak, "review")
    author_weak = "Verdict: weak\nFindings:\n- 6 | generated snippet:1 | vague name | name the expected result\nAuthored test:\n```cpp\nTEST(F, T) { EXPECT_EQ(f(), 8); }\n```"
    validate(author_weak, "author")
    for mutation in (author_weak.replace("snippet:1", "snippet:2"), weak.replace("- 1", "- 7"), weak.replace("supplied snippet:4", "unknown"), weak.replace("self-comparison", ""), weak.replace("self-comparison", "issue|extra"), VALID["author"].replace("TEST(FrameTest, SerializesPingFrame) { EXPECT_EQ(serialize(Frame::ping(0x1234)), expected); }", "")):
        try:
            validate(mutation, "author" if "Authored test:" in mutation else "review")
        except ValueError:
            continue
        raise AssertionError("accepted field mutation")
    wire = VALID["author"].split("```cpp", 1)[0] + "```cpp\n" + WIRE_CODE + "\n```"
    validate(wire, "author", wire_fixture=True)
    validate(wire.replace("Frame frame", "/* setup */ Frame frame"), "author", wire_fixture=True)
    for code in ("// " + WIRE_CODE.replace("\n", "\n// "), "/* " + WIRE_CODE + " */", WIRE_CODE.replace("0x34", "0x35"), WIRE_CODE.replace("auto bytes = serialize(frame);", ""), WIRE_CODE.replace("TEST(FrameTest, SerializesPingFrame)", "void example()"), 'const char* text = "' + WIRE_CODE.replace("\n", " ") + '";'):
        try:
            validate(wire.replace(WIRE_CODE, code), "author", wire_fixture=True)
        except ValueError:
            continue
        raise AssertionError("accepted unconstructed wire fixture")
    batch = VALID["review"] + "\n\nVerdict: solid\nFindings: None. The supplied contract value is asserted directly."
    for labels in (MARKERS[:2], ("Decision:", "Quality notes:")):
        candidate = batch.replace(MARKERS[0], labels[0]).replace(MARKERS[1], labels[1])
        validate(candidate, "review", labels, test_count=2, verdicts=("cannot-fail", "solid"))
        for mutation in (candidate.replace("\n\n", "\n"), candidate.split("\n\n", 1)[0], candidate + "\n" + candidate, candidate.replace(labels[1] + " None.", "Omitted: None."), candidate.replace("solid", "invalid"), candidate + "\nTrailing prose."):
            try:
                validate(mutation, "review", labels, test_count=2, verdicts=("cannot-fail", "solid"))
            except ValueError:
                continue
            raise AssertionError("accepted batch report mutation")
    partial = batch.split("\n\n", 1)[0] + "\n\n" + VALID["missing"]
    validate(partial, "review", test_count=2, verdicts=("cannot-fail", "insufficient-context"))
    for index in range(2):
        reports = batch.split("\n\n")
        original = reports[index]
        mutations = [original.replace("Verdict:", "Omitted:", 1), original + "\nFindings:", original.replace("Verdict:", "Authored test:", 1)]
        lines = original.splitlines()
        mutations.append("\n".join([lines[1], lines[0]] + lines[2:]))
        for mutation in mutations:
            changed = reports[:]
            changed[index] = mutation
            try:
                validate("\n\n".join(changed), "review", test_count=2)
            except ValueError:
                continue
            raise AssertionError("accepted per-report batch mutation")
    for options in ({"wire_fixture": True}, {"verdicts": ("solid",)}, {"verdicts": ("invalid", "solid")}, {"expected": "solid", "verdicts": ("cannot-fail", "solid")}, {"labels": ("Verdict:", "Verdict:")}, {"labels": ("Verdict", "Findings:")}, {"profile": "author"}, {"profile": "missing"}):
        kwargs = {"profile": "review", "test_count": 2}
        kwargs.update(options)
        try:
            validate(batch, **kwargs)
        except ValueError:
            continue
        raise AssertionError("accepted invalid batch options")
    for count in (0, -1, True):
        try:
            validate(batch, "review", test_count=count)
        except ValueError:
            continue
        raise AssertionError("accepted invalid report count")
    print("quality report profiles and deterministic mutations: passed")


def main() -> None:
    """Read reports from stdin, or run free local mutation checks."""
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", choices=sorted(PROFILES))
    parser.add_argument("labels", nargs="*")
    parser.add_argument("--verdict", choices=sorted(VERDICTS))
    parser.add_argument("--wire-fixture", action="store_true")
    parser.add_argument("--test-count", type=int, default=1)
    parser.add_argument("--verdicts", help="comma-separated per-test verdicts")
    args = parser.parse_intermixed_args()
    try:
        validate(sys.stdin.read(), args.profile, tuple(args.labels), args.verdict, args.wire_fixture, args.test_count, tuple(args.verdicts.split(",")) if args.verdicts else ())
    except ValueError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
