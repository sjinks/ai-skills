#!/usr/bin/env python3
"""Validate one per-test quality report without calling a model."""
from __future__ import annotations

import argparse
import re
import sys

MARKERS = ("Verdict:", "Findings:", "Authored test:")
PROFILES = {"review", "author", "missing"}
WIRE_PATTERN = r"TEST\(\s*FrameTest\s*,\s*SerializesPingFrame\s*\)\s*\{\s*Frame\s+frame\s*=\s*Frame::ping\(0x1234\)\s*;\s*auto\s+bytes\s*=\s*serialize\(frame\)\s*;\s*EXPECT_EQ\(\s*bytes\s*,\s*std::vector<uint8_t>\(\s*\{0x09,\s*0x00,\s*0x12,\s*0x34\}\s*\)\s*\)\s*;\s*\}"
WIRE_CODE = "TEST(FrameTest, SerializesPingFrame) {\n  Frame frame = Frame::ping(0x1234);\n  auto bytes = serialize(frame);\n  EXPECT_EQ(bytes, std::vector<uint8_t>({0x09, 0x00, 0x12, 0x34}));\n}"
VERDICTS = {"solid", "weak", "cannot-fail", "insufficient-context"}


def validate(text: str, profile: str, labels: tuple[str, ...] = (), expected: str | None = None, wire_fixture: bool = False) -> None:
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
    if any(line.startswith(marker) for line in lines for marker in MARKERS if marker not in labels):
        raise ValueError("inactive or replaced marker")
    positions = []
    for label in labels:
        matches = [i for i, line in enumerate(lines) if line.startswith(label)]
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
    print("quality report profiles and deterministic mutations: passed")


def main() -> None:
    """Read one report from stdin, or run free local mutation checks."""
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", choices=sorted(PROFILES))
    parser.add_argument("labels", nargs="*")
    parser.add_argument("--verdict", choices=sorted(VERDICTS))
    parser.add_argument("--wire-fixture", action="store_true")
    args = parser.parse_intermixed_args()
    try:
        validate(sys.stdin.read(), args.profile, tuple(args.labels), args.verdict, args.wire_fixture)
    except ValueError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
