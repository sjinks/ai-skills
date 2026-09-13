#!/usr/bin/env python3
"""Check the coupled shell-construction and portability regression contracts.

This is a static preflight. It does not call a model: it proves the fixture
source bytes, output regexes, and portability handoff agree for three specific
regressions: delimiter-owned newlines, custom-label deployment-completion
claims, a leading-pipe handoff, and byte-zero portability reports.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
SCC_TASKS = ROOT / "evals/shell-command-construction/tasks"
PORTABILITY_TASKS = ROOT / "evals/shell-portability/tasks"
SCC_EVAL = ROOT / "evals/shell-command-construction/eval.yaml"
PORTABILITY_EVAL = ROOT / "evals/shell-portability/eval.yaml"
HANDOFF_REFERENCE = ROOT / "skills/shell-portability/references/construction-handoff.md"
GO_REGEX_RUNNER = ROOT / "evals/_helpers/go-regex-runner"


class CheckError(Exception):
    """Raised when a coupled regression contract drifts."""


@dataclass(frozen=True)
class CandidateFixture:
    number: str
    labels: tuple[str, str, str, str, str]
    payload: str
    terminal_newline_is_payload: bool


@dataclass(frozen=True)
class YAMLProjection:
    prompt: str
    regex_match: tuple[str, ...]
    regex_not_match: tuple[str, ...]
    not_contains: tuple[str, ...]
    assertions: tuple[str, ...]


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


def load_projection(path: Path) -> YAMLProjection:
    try:
        completed = subprocess.run(
            ("go", "run", ".", "--yaml-projection", str(path)),
            cwd=GO_REGEX_RUNNER,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        fail(f"could not run the Go YAML projection for {path.relative_to(ROOT)}: {error}")
    if completed.returncode:
        fail(f"could not load {path.relative_to(ROOT)}: {completed.stderr.strip()}")
    try:
        value = json.loads(completed.stdout)
        prompt = value["prompt"]
        regex_match = value["regex_match"] or []
        regex_not_match = value["regex_not_match"] or []
        not_contains = value["not_contains"] or []
        assertions = value["assertions"] or []
    except (TypeError, KeyError, json.JSONDecodeError) as error:
        fail(f"could not decode the Go YAML projection for {path.relative_to(ROOT)}: {error}")
    if not isinstance(prompt, str) or not all(isinstance(item, str) for item in (*regex_match, *regex_not_match, *not_contains, *assertions)):
        fail(f"{path.relative_to(ROOT)} has an invalid YAML projection")
    return YAMLProjection(prompt, tuple(regex_match), tuple(regex_not_match), tuple(not_contains), tuple(assertions))


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


def accepts_task_completion(task: YAMLProjection, output: str, task_name: str) -> bool:
    if not task.regex_match:
        fail(f"{task_name} must have a task_completion text regex")
    return all(matches(regex, output, task_name) for regex in task.regex_match) and not any(matches(regex, output, task_name) for regex in task.regex_not_match) and not any(value in output for value in task.not_contains)


def rejects_task_completion(task: YAMLProjection, output: str, task_name: str) -> bool:
    if not task.regex_not_match and not task.not_contains:
        fail(f"{task_name} must reject an SCC envelope")
    return any(matches(regex, output, task_name) for regex in task.regex_not_match) or any(value in output for value in task.not_contains)


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
        task = load_projection(path)
        task_name = path.relative_to(ROOT).as_posix()
        prompt = task.prompt
        if not prompt:
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

        valid = scc_output(fixture, payload)
        if not accepts_task_completion(task, valid, task_name):
            fail(f"{task_name} does not accept its declared candidate payload")

        corrupted = payload.replace("tool", "noop", 1)
        if accepts_task_completion(task, scc_output(fixture, corrupted), task_name):
            fail(f"{task_name} does not reject a changed candidate payload")
        if fixture.terminal_newline_is_payload and accepts_task_completion(task, scc_output(fixture, payload[:-1]), task_name):
            fail(f"{task_name} does not reject a removed terminal payload newline")


def check_leading_pipe_handoff() -> None:
    path = PORTABILITY_TASKS / "positive-edge-3.yaml"
    task = load_projection(path)
    task_name = path.relative_to(ROOT).as_posix()
    prompt = task.prompt
    if "Construction candidate: | sed -n '1p'" not in prompt:
        fail(f"{task_name} must retain the one-line leading-pipe handoff")
    if "Construction candidate: |\n" in prompt:
        fail(f"{task_name} must not reinterpret the leading pipe as a multiline marker")
    handoff_reference = HANDOFF_REFERENCE.read_text()
    one_line_pipe_rule = "If its first non-whitespace character is `|`, later non-whitespace text must occur on the same line."
    if one_line_pipe_rule not in handoff_reference:
        fail("construction handoff reference no longer preserves the one-line leading-pipe rule")

    if not task.regex_match:
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
    if not accepts_task_completion(task, output, task_name):
        fail(f"{task_name} does not accept the complete leading-pipe portability report")


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


def custom_multiline_output(labels: tuple[str, str, str, str, str], next_step: str) -> str:
    result, assessment, candidate, authority, next_label = labels
    return "\n".join(
        (
            f"{result}: VALID",
            f"{assessment}: The supplied bytes preserve the requested boundary.",
            f"{candidate}: |",
            "  tool 'hello world'",
            f"{authority}: NOT ASSESSED BY THIS SKILL",
            f"{next_label}: {next_step}",
        )
    )


def check_negative_custom_envelopes() -> None:
    labels = (
        "Result",
        "Boundary assessment",
        "Shell candidate",
        "Authority",
        "Next construction action",
    )
    inline = custom_output(labels, "Review the candidate boundary.")
    multiline = custom_multiline_output(labels, "Review the candidate boundary.")
    hyphenated = custom_output(
        ("Outcome-label", "Boundary assessment", "Shell candidate", "Authority", "Next construction action"),
        "Review the candidate boundary.",
    )
    colon_injected = custom_output(
        ("Result: injected", "Boundary assessment", "Shell candidate", "Authority", "Next construction action"),
        "Review the candidate boundary.",
    )
    outputs = (
        inline,
        multiline,
        f"Context only; the direct result follows.\n{inline}",
        f"```text\n{multiline}\n```",
        f"Context only; the direct result follows.\n{inline.replace('Result: VALID', 'Result: VALID -- direct construction result')}",
        f"```text\n{multiline.replace('Result: VALID', 'Result: VALID -- direct construction result')}\n```",
        f"Context only; the direct result follows.\n{hyphenated.replace('Outcome-label: VALID', 'Outcome-label: VALID -- direct construction result')}",
        f"```text\n{colon_injected.replace('Result: injected: VALID', 'Result: injected: VALID -- direct construction result')}\n```",
    )
    for path in sorted(SCC_TASKS.glob("negative-*.yaml")):
        task_name = path.relative_to(ROOT).as_posix()
        task = load_projection(path)
        for output in outputs:
            if not rejects_task_completion(task, output, task_name):
                fail(f"{task_name} accepts an unrequested custom SCC envelope")


def check_label_cardinality_fallback() -> None:
    requested_labels = (
        ("Result", "Boundary assessment", "Shell candidate", "Authority"),
        ("Result", "Boundary assessment", "Shell candidate", "Authority", "Next construction action", "Extra label"),
    )
    for fixture, labels in zip(("positive-edge-036.yaml", "positive-edge-037.yaml"), requested_labels, strict=True):
        path = SCC_TASKS / fixture
        task_name = path.relative_to(ROOT).as_posix()
        task = load_projection(path)
        if not all(f"`{label}`" in task.prompt for label in labels):
            fail(f"{task_name} no longer supplies its requested label set")
        if "fallback" in task.prompt.lower() or "default field labels" in task.prompt.lower():
            fail(f"{task_name} coaches the required fallback in its prompt")
        output = canonical_output("Review the candidate boundary.", 'tool "hello world"')
        if not accepts_task_completion(task, output, task_name):
            fail(f"{task_name} does not accept its canonical fallback envelope")


def canonical_output(next_step: str, candidate: str = "printf '%s\\n' value") -> str:
    return "\n".join(
        (
            "Construction result: VALID",
            "Construction assessment: The supplied bytes preserve the requested boundary.",
            f"Construction candidate: {candidate}",
            "Execution authority: NOT ASSESSED BY THIS SKILL",
            f"Construction next step: {next_step}",
        )
    )


def evaluate_assertion(assertion: str, output: str, source: Path) -> bool:
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
    return bool(eval(compile(tree, source.as_posix(), "eval"), {"__builtins__": {}, "output": output, "re": re}))


def check_custom_label_deployment_regression() -> None:
    assertions = load_projection(SCC_EVAL).assertions
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
        if not evaluate_assertion(assertion, valid, SCC_EVAL):
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
            if evaluate_assertion(assertion, custom_output(labels, completion_claim), SCC_EVAL):
                fail(f"custom-label regression accepts a completion claim for {labels[0]!r} labels")
    if not evaluate_assertion(assertion, canonical_output("Review the candidate boundary."), SCC_EVAL):
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
        if evaluate_assertion(assertion, canonical_output(completion_claim), SCC_EVAL):
            fail("shared policy accepts a canonical completion claim")


def check_portability_preamble_regression() -> None:
    assertions = load_projection(PORTABILITY_EVAL).assertions
    assertion = next(
        (item for item in assertions if 'output.startswith("Portability verdict:")' in item),
        None,
    )
    if assertion is None:
        fail("shell-portability output contract no longer requires a byte-zero report")
    report = "Portability verdict: CLEAN\nPortability residual risk: None"
    if not evaluate_assertion(assertion, report, PORTABILITY_EVAL):
        fail("portability output contract rejects a byte-zero report")
    if evaluate_assertion(assertion, f"Here is the review:\n{report}", PORTABILITY_EVAL):
        fail("portability output contract accepts a preamble before its report")
    if evaluate_assertion(assertion, f"  {report}", PORTABILITY_EVAL):
        fail("portability output contract accepts an indented report")
    legacy_assertion = next(
        (item for item in assertions if '^[ \\t]*(?:Verdict|Target|Interpreter|Findings|Checklist status|Residual risk):' in item),
        None,
    )
    if legacy_assertion is None:
        fail("shell-portability output contract no longer rejects indented legacy labels")
    if evaluate_assertion(legacy_assertion, f"{report}\n  Verdict: CLEAN", PORTABILITY_EVAL):
        fail("portability output contract accepts an indented legacy label")


def main() -> None:
    try:
        check_candidate_fixtures()
        check_leading_pipe_handoff()
        check_negative_custom_envelopes()
        check_custom_label_deployment_regression()
        check_label_cardinality_fallback()
        check_portability_preamble_regression()
    except CheckError as error:
        print(f"shell contract projection check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    print("shell contract projection check passed")


if __name__ == "__main__":
    main()
