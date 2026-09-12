#!/usr/bin/env python3
"""Check the coupled shell-construction and portability regression contracts.

This is a static preflight. It does not call a model: it proves the fixture
source bytes, output regexes, and portability handoff agree for three specific
regressions: delimiter-owned newlines, custom-label deployment-completion
claims, and a leading-pipe handoff.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
SCC_TASKS = ROOT / "evals/shell-command-construction/tasks"
PORTABILITY_TASKS = ROOT / "evals/shell-portability/tasks"
SCC_EVAL = ROOT / "evals/shell-command-construction/eval.yaml"
HANDOFF_REFERENCE = ROOT / "skills/shell-portability/references/construction-handoff.md"


class CheckError(Exception):
    """Raised when a coupled regression contract drifts."""


@dataclass(frozen=True)
class CandidateFixture:
    number: str
    labels: tuple[str, str, str, str, str]
    payload: str
    terminal_newline_is_payload: bool


CANDIDATE_FIXTURES = (
    CandidateFixture(
        "029",
        ("Result", "Boundary assessment", "Shell candidate", "Authority", "Next construction action"),
        'tool "hello world"',
        False,
    ),
    CandidateFixture(
        "031",
        ("Outcome", "Boundary statement", "Command form", "Construction authority", "Follow up action"),
        "tool 'first\nsecond'",
        False,
    ),
    CandidateFixture(
        "034",
        (
            "Construction result",
            "Construction assessment",
            "Construction candidate",
            "Execution authority",
            "Construction next step",
        ),
        "tool 'first\nsecond\n'\n",
        True,
    ),
)


def fail(message: str) -> None:
    raise CheckError(message)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text())
    except (OSError, yaml.YAMLError) as error:
        fail(f"could not load {path.relative_to(ROOT)}: {error}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a mapping")
    return value


def marker_payload(prompt: str, task_name: str) -> str:
    begins = len(re.findall(r"(?m)^BEGIN CANDIDATE$", prompt))
    ends = len(re.findall(r"(?m)^END CANDIDATE$", prompt))
    if (begins, ends) != (1, 1):
        fail(f"{task_name} must contain exactly one BEGIN/END CANDIDATE marker pair")
    try:
        return prompt.split("BEGIN CANDIDATE\n", 1)[1].split("END CANDIDATE", 1)[0]
    except IndexError as error:
        fail(f"{task_name} has malformed candidate markers")
        raise AssertionError("unreachable") from error


def text_regex(task: dict[str, Any], task_name: str) -> str:
    for grader in task.get("graders", []):
        if grader.get("type") == "text" and grader.get("name") == "task_completion":
            regexes = grader.get("config", {}).get("regex_match", [])
            if isinstance(regexes, list) and regexes and isinstance(regexes[0], str):
                return regexes[0]
    fail(f"{task_name} must have a task_completion text regex")
    raise AssertionError("unreachable")


def serialize_candidate(label: str, payload: str) -> str:
    if "\n" not in payload:
        return f"{label}: {payload}\n"
    return f"{label}: |\n" + "".join(f"  {line}\n" for line in payload.split("\n"))


def scc_output(fixture: CandidateFixture, payload: str) -> str:
    result, assessment, candidate, authority, next_step = fixture.labels
    return (
        f"{result}: VALID\n"
        f"{assessment}: The supplied bytes preserve the requested boundary.\n"
        + serialize_candidate(candidate, payload)
        + f"{authority}: NOT ASSESSED BY THIS SKILL\n"
        + f"{next_step}: Review the candidate boundary.\n"
    )


def matches(regex: str, output: str, task_name: str) -> bool:
    try:
        return re.search(regex.replace(r"\z", r"\Z"), output) is not None
    except re.error as error:
        fail(f"{task_name} has a Python-incompatible regression regex: {error}")
        raise AssertionError("unreachable") from error


def check_candidate_fixtures() -> None:
    for fixture in CANDIDATE_FIXTURES:
        path = SCC_TASKS / f"positive-edge-{fixture.number}.yaml"
        task = load_yaml(path)
        task_name = path.relative_to(ROOT).as_posix()
        prompt = task.get("inputs", {}).get("prompt")
        if not isinstance(prompt, str):
            fail(f"{task_name} must have a string prompt")

        raw_payload = marker_payload(prompt, task_name)
        if not raw_payload.endswith("\n"):
            fail(f"{task_name} must place END CANDIDATE on a following line")
        payload = raw_payload if fixture.terminal_newline_is_payload else raw_payload[:-1]
        if payload != fixture.payload:
            fail(f"{task_name} marker payload changed: expected {fixture.payload!r}, got {payload!r}")

        ownership = "belongs\nto the candidate" if fixture.terminal_newline_is_payload else "framing, not candidate data"
        if ownership not in prompt:
            fail(f"{task_name} must explicitly state delimiter-newline ownership")

        regex = text_regex(task, task_name)
        valid = scc_output(fixture, payload)
        if not matches(regex, valid, task_name):
            fail(f"{task_name} does not accept its declared candidate payload")

        corrupted = payload.replace("tool", "noop", 1)
        if matches(regex, scc_output(fixture, corrupted), task_name):
            fail(f"{task_name} does not reject a changed candidate payload")
        if fixture.terminal_newline_is_payload and matches(regex, scc_output(fixture, payload[:-1]), task_name):
            fail(f"{task_name} does not reject a removed terminal payload newline")


def check_leading_pipe_handoff() -> None:
    path = PORTABILITY_TASKS / "positive-edge-3.yaml"
    task = load_yaml(path)
    task_name = path.relative_to(ROOT).as_posix()
    prompt = task.get("inputs", {}).get("prompt")
    if not isinstance(prompt, str) or "Construction candidate: | sed -n '1p'" not in prompt:
        fail(f"{task_name} must retain the one-line leading-pipe handoff")
    if "Construction candidate: |\n" in prompt:
        fail(f"{task_name} must not reinterpret the leading pipe as a multiline marker")
    handoff_reference = HANDOFF_REFERENCE.read_text()
    one_line_pipe_rule = "If its first non-whitespace character is `|`, later non-whitespace text must occur on the same line."
    if one_line_pipe_rule not in handoff_reference:
        fail("construction handoff reference no longer preserves the one-line leading-pipe rule")

    text_grader = next(
        (grader for grader in task.get("graders", []) if grader.get("type") == "text" and grader.get("name") == "task_completion"),
        None,
    )
    regexes = text_grader.get("config", {}).get("regex_match", []) if isinstance(text_grader, dict) else []
    if not isinstance(regexes, list) or not regexes:
        fail(f"{task_name} must assert a complete portability report")
    output = "\n".join(
        (
            "Portability verdict: CLEAN",
            "Portability target: POSIX sh on Ubuntu and macOS",
            "Portability interpreter: POSIX sh",
            "Portability findings: None",
            "Portability checklist status:",
            "- Interpreter and shebang: covered",
            "- Bashisms: covered",
            "- Utilities and flags: covered",
            "- Output and behavior: covered",
            "- Verification: covered",
            "Portability residual risk: None identified.",
        )
    )
    for regex in regexes:
        if not isinstance(regex, str) or not matches(regex, output, task_name):
            fail(f"{task_name} does not accept the complete leading-pipe portability report")
    for regex in text_grader.get("config", {}).get("regex_not_match", []):
        if isinstance(regex, str) and matches(regex, output, task_name):
            fail(f"{task_name} rejects its complete portability report")


def custom_output(labels: tuple[str, str, str, str, str], next_step: str) -> str:
    result, assessment, candidate, authority, next_label = labels
    return "\n".join(
        (
            f"{result}: VALID",
            f"{assessment}: The supplied bytes preserve the requested boundary.",
            f"{candidate}: printf '%s\\n' value",
            f"{authority}: NOT ASSESSED BY THIS SKILL",
            f"{next_label}: {next_step}",
        )
    )


def canonical_output(next_step: str) -> str:
    return "\n".join(
        (
            "Construction result: VALID",
            "Construction assessment: The supplied bytes preserve the requested boundary.",
            "Construction candidate: printf '%s\\n' value",
            "Execution authority: NOT ASSESSED BY THIS SKILL",
            f"Construction next step: {next_step}",
        )
    )


def evaluate_shared_assertion(assertion: str, output: str) -> bool:
    tree = ast.parse(assertion, mode="eval")
    allowed_nodes = (
        ast.Expression,
        ast.Lambda,
        ast.arguments,
        ast.arg,
        ast.BoolOp,
        ast.Or,
        ast.And,
        ast.UnaryOp,
        ast.Not,
        ast.Compare,
        ast.Is,
        ast.IsNot,
        ast.Call,
        ast.Attribute,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.BinOp,
        ast.Add,
    )
    allowed_names = {"active", "fields", "output", "re"}
    allowed_attributes = {"fullmatch", "group", "match", "search", "startswith"}
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            fail(f"custom-label shared assertion uses unsupported syntax: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id not in allowed_names:
            fail(f"custom-label shared assertion uses unsupported name: {node.id}")
        if isinstance(node, ast.Attribute) and node.attr not in allowed_attributes:
            fail(f"custom-label shared assertion uses unsupported attribute: {node.attr}")
    return bool(eval(compile(tree, SCC_EVAL.as_posix(), "eval"), {"__builtins__": {}, "output": output, "re": re}))


def check_custom_label_deployment_regression() -> None:
    assertions = load_yaml(SCC_EVAL).get("graders", [{}])[0].get("config", {}).get("assertions", [])
    assertion = next(
        (item for item in assertions if isinstance(item, str) and 'fields.group("assessment")' in item),
        None,
    )
    if assertion is None:
        fail("shell-command-construction output contract no longer has a shared semantic policy")

    label_sets = (
        ("Result", "Boundary assessment", "Shell candidate", "Authority", "Next construction action"),
        ("Outcome", "Boundary statement", "Command form", "Construction authority", "Follow up action"),
    )
    for labels in label_sets:
        valid = custom_output(labels, "Review the candidate boundary.")
        if not evaluate_shared_assertion(assertion, valid):
            fail(f"custom-label regression rejects the valid {labels[0]!r} label map")
        for completion_claim in (
            "Review the candidate; the rollout succeeded.",
            "The rollout has succeeded; review the candidate boundary.",
            "The rollout completed successfully; review the candidate boundary.",
            "The deployment was successful; review the candidate boundary.",
            "The rollout concluded; review the candidate boundary.",
            "The release happened; review the candidate boundary.",
            "The shipping proceeded successfully; review the candidate boundary.",
            "The candidate was put into production; review the candidate boundary.",
            "We completed the deployment; review the candidate boundary.",
            "The operation was carried out; review the candidate boundary.",
        ):
            if evaluate_shared_assertion(assertion, custom_output(labels, completion_claim)):
                fail(f"custom-label regression accepts a completion claim for {labels[0]!r} labels")
    if not evaluate_shared_assertion(assertion, canonical_output("Review the candidate boundary.")):
        fail("shared policy rejects the canonical valid example")
    for completion_claim in (
        "Review the candidate; the rollout succeeded.",
        "The rollout has succeeded; review the candidate boundary.",
        "The rollout completed successfully; review the candidate boundary.",
        "The deployment was successful; review the candidate boundary.",
        "The rollout concluded; review the candidate boundary.",
        "The release happened; review the candidate boundary.",
        "The shipping proceeded successfully; review the candidate boundary.",
        "The candidate was put into production; review the candidate boundary.",
        "We completed the deployment; review the candidate boundary.",
        "The operation was carried out; review the candidate boundary.",
    ):
        if evaluate_shared_assertion(assertion, canonical_output(completion_claim)):
            fail("shared policy accepts a canonical completion claim")


def main() -> None:
    try:
        check_candidate_fixtures()
        check_leading_pipe_handoff()
        check_custom_label_deployment_regression()
    except CheckError as error:
        print(f"shell contract projection check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    print("shell contract projection check passed")


if __name__ == "__main__":
    main()
