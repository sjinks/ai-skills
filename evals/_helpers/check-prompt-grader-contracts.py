#!/usr/bin/env python3
"""Check decoded Waza prompt graders for the binary tool-call contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

import yaml


GRADE_PASS = "set_waza_grade_pass"
GRADE_FAIL = "set_waza_grade_fail"
NUMERIC_LINE_GRADE = re.compile(
    r"\b(?:last|final)\s+line\s*[:,]?\s*(?:write\s+)?(?:only\s+)?"
    r"(?:one of\s*:\s*)?(?:1\.0|0\.5|0\.0)\b|"
    r"\b(?:write|output|return|emit|print)\b[^\n]*\bonly\s+"
    r"(?:1\.0|0\.5|0\.0)\b|"
    r"\bonly\s+(?:1\.0|0\.5|0\.0)\b[^\n]*\b(?:last|final)\s+line",
    re.I,
)
ONE_CALL = re.compile(r"exactly one (?:grading )?tool call|exactly once", re.I)


def repository_evals() -> Path:
    """Return the repository's canonical eval directory.

    Resolve relative to this checker so callers may invoke it from any cwd.
    """
    return Path(__file__).resolve().parents[1]


def check_prompt(prompt: str) -> list[str]:
    """Report violations of Waza's prompt-grader call protocol.

    Only the decoded grader instruction is inspected; numeric values in a
    student's task input or in unrelated metric thresholds are not grades.
    """
    problems = []
    if GRADE_PASS not in prompt:
        problems.append("missing pass tool")
    if GRADE_FAIL not in prompt:
        problems.append("missing fail tool")
    if not ONE_CALL.search(prompt):
        problems.append("missing exactly-one-call instruction")
    if not re.search(r"\botherwise\b", prompt, re.I):
        problems.append("missing complementary failure outcome")
    if not re.search(r"\breason(?:ing)?\b", prompt, re.I):
        problems.append("missing tool-call reason instruction")
    if NUMERIC_LINE_GRADE.search(prompt):
        problems.append("numeric or final-line grade instruction")
    return problems


def check_tree(root: Path) -> tuple[int, list[str]]:
    """Decode all task YAML files and check every prompt grader.

    Return the grader count and path-qualified violations. YAML parse failures
    are reported too, so an unparseable task cannot silently evade the scan.
    """
    count = 0
    failures = []
    for path in sorted(root.rglob("*.yaml")):
        try:
            task = yaml.safe_load(path.read_text())
        except (OSError, yaml.YAMLError) as error:
            failures.append(f"{path}: YAML decode failed: {error}")
            continue
        if not isinstance(task, dict):
            continue
        for index, grader in enumerate(task.get("graders", [])):
            if not isinstance(grader, dict) or grader.get("type") != "prompt":
                continue
            count += 1
            prompt = grader.get("config", {}).get("prompt")
            if not isinstance(prompt, str):
                failures.append(f"{path}: grader {index}: missing prompt string")
                continue
            for problem in check_prompt(prompt):
                failures.append(f"{path}: grader {index}: {problem}")
    return count, failures


def run_self_test() -> None:
    """Exercise one valid prompt and isolated protocol mutations.

    Each invalid fixture changes one requirement so its rejection diagnostic
    identifies that missing or contradictory instruction independently.
    """
    valid = (
        "The artifact uses version 1.0 and ends with the final line Verdict: OK. "
        "A numeric rubric threshold of 0.5 may appear in the artifact. "
        "Call set_waza_grade_pass exactly once if every requirement holds. "
        "Otherwise call set_waza_grade_fail exactly once, including partial "
        "completion. Put the reasoning in the tool call's reason argument."
    )
    assert check_prompt(valid) == []
    mutations = {
        "missing pass tool": valid.replace(GRADE_PASS, "grade_success"),
        "missing fail tool": valid.replace(GRADE_FAIL, "grade_failure"),
        "missing exactly-one-call instruction": valid.replace("exactly once", "", 2),
        "missing complementary failure outcome": valid.replace("Otherwise", "When uncertain,"),
        "missing tool-call reason instruction": valid.replace(
            "Put the reasoning in the tool call's reason argument.", ""
        ),
        "numeric or final-line grade instruction": valid
        + " On the final line write only 1.0, 0.5, or 0.0.",
    }
    for expected, mutated in mutations.items():
        assert check_prompt(mutated) == [expected], (expected, check_prompt(mutated))


def main() -> int:
    """Run an isolated prompt check or the repository-wide scan.

    The stdin mode lets review-evidence probes check one conforming or mutated
    instruction without wrapping this validator in a Python command string.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=repository_evals())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--prompt", action="store_true", help="check one prompt read from stdin")
    options = parser.parse_args()
    if options.self_test:
        run_self_test()
        print("isolated mutation cases: pass")
    if options.prompt:
        failures = check_prompt(sys.stdin.read())
        for failure in failures:
            print(failure, file=sys.stderr)
        print(f"prompt violations: {len(failures)}")
        return int(bool(failures))
    count, failures = check_tree(options.root)
    for failure in failures:
        print(failure, file=sys.stderr)
    print(f"decoded prompt graders checked: {count}; violations: {len(failures)}")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
