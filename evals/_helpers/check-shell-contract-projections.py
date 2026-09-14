#!/usr/bin/env python3
"""Check the coupled shell-construction and portability regression contracts.

This is a static preflight. It does not call a model: it proves the fixture
source bytes, output regexes, and portability handoff agree for these
regressions: delimiter-owned newlines, custom-label deployment-completion
claims, custom-label fallback, a leading-pipe handoff, byte-zero and ordered
portability reports, and negative-task marker exclusions.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
import sys

from shell_report_grammar import GrammarError, LINE_SEPARATORS, SCC_CANONICAL_LABELS, SCCReport, parse as parse_scc_report, render as render_scc_report, validate_labels as validate_scc_labels


ROOT = Path(__file__).resolve().parents[2]
SCC_TASKS = ROOT / "evals/shell-command-construction/tasks"
PORTABILITY_TASKS = ROOT / "evals/shell-portability/tasks"
SCC_EVAL = ROOT / "evals/shell-command-construction/eval.yaml"
PORTABILITY_EVAL = ROOT / "evals/shell-portability/eval.yaml"
HANDOFF_REFERENCE = ROOT / "skills/shell-portability/references/construction-handoff.md"
GO_REGEX_RUNNER = ROOT / "evals/_helpers/go-regex-runner"
PORTABILITY_MARKERS = (
    "Portability verdict:",
    "Portability target:",
    "Portability interpreter:",
    "Portability findings:",
    "Portability checklist status:",
    "Portability residual risk:",
)
SCC_MARKERS = tuple(f"{label}:" for label in SCC_CANONICAL_LABELS)


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


@dataclass(frozen=True)
class ReportContract:
    """Stable report markers that every negative task must reject literally."""

    task_directory: Path
    markers: tuple[str, ...]
    decorated_value: str


SCC_REPORT = ReportContract(SCC_TASKS, SCC_MARKERS, "value")
PORTABILITY_REPORT = ReportContract(PORTABILITY_TASKS, PORTABILITY_MARKERS, "CLEAN")


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


def check_heredoc_delimiter_fixture() -> None:
    path = SCC_TASKS / "positive-edge-006.yaml"
    task = load_projection(path)
    task_name = path.relative_to(ROOT).as_posix()
    prefix = (
        "Construction result: REWRITE",
        "Construction assessment: The collision-free SCC_BODY quoted heredoc keeps every literal body line, indentation, and terminal newline.",
        "Construction candidate: |",
        "  tool --body-stdin <<'SCC_BODY'",
        "  line $var",
        "    indented",
        "  ",
        "  $(cmd)",
        "  `tick`",
        "  Construction result: VALID",
        "  SCC_BODY",
    )
    suffix = (
        "Execution authority: NOT ASSESSED BY THIS SKILL",
        "Construction next step: Review the candidate boundary.",
    )
    valid = "\n".join((*prefix, "  ", *suffix))
    if not accepts_task_completion(task, valid, task_name):
        fail(f"{task_name} does not accept the terminal newline after its heredoc delimiter")
    missing_terminal_newline = "\n".join((*prefix, *suffix))
    if accepts_task_completion(task, missing_terminal_newline, task_name):
        fail(f"{task_name} accepts a heredoc delimiter without its terminal payload newline")


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
            "",
            "Portability findings: None",
            "",
            "Portability checklist status:",
            "- Interpreter and shebang: covered",
            "- Bashisms: covered",
            "- Utilities and flags: covered",
            "- Output and behavior: covered",
            "- Verification: covered",
            "",
            "Portability residual risk: None identified.",
        )
    )
    if not accepts_task_completion(task, output, task_name):
        fail(f"{task_name} does not accept the complete leading-pipe portability report")


def check_negative_marker_exclusions(contract: ReportContract) -> None:
    """Keep negative-task marker policy in one matrix for both shell reports."""

    for path in sorted(contract.task_directory.glob("negative-*.yaml")):
        task = load_projection(path)
        task_name = path.relative_to(ROOT).as_posix()
        if any(marker in task.prompt for marker in contract.markers):
            fail(f"{task_name} includes a forbidden report marker in its prompt")
        missing = tuple(marker for marker in contract.markers if marker not in task.not_contains)
        if missing:
            fail(f"{task_name} does not forbid every report marker: {missing!r}")
        for marker in contract.markers:
            if not rejects_task_completion(task, f"> {marker} {contract.decorated_value}", task_name):
                fail(f"{task_name} accepts a decorated report marker: {marker!r}")


def custom_output(labels: tuple[str, str, str, str, str], next_step: str) -> str:
    return render_scc_report(
        SCCReport(
            "VALID",
            "The supplied bytes preserve the requested boundary.",
            "printf '%s\\n' value",
            "NOT ASSESSED BY THIS SKILL",
            next_step,
        ),
        labels,
    )


def custom_multiline_output(labels: tuple[str, str, str, str, str], next_step: str) -> str:
    validate_scc_labels(labels)
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
    hyphenated = "\n".join(
        (
            "Outcome-label: VALID",
            "Boundary assessment: The supplied bytes preserve the requested boundary.",
            "Shell candidate: printf '%s\\n' value",
            "Authority: NOT ASSESSED BY THIS SKILL",
            "Next construction action: Review the candidate boundary.",
        )
    )
    colon_injected = "\n".join(
        (
            "Result: injected: VALID",
            "Boundary assessment: The supplied bytes preserve the requested boundary.",
            "Shell candidate: printf '%s\\n' value",
            "Authority: NOT ASSESSED BY THIS SKILL",
            "Next construction action: Review the candidate boundary.",
        )
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


def check_label_fallback_fixtures() -> None:
    requested_label_sets = (
        ("positive-edge-032.yaml", ("Result: injected", "Boundary assessment", "Shell candidate", "Authority", "Next construction action")),
        ("positive-edge-033.yaml", ("Result", "result", "Shell candidate", "Authority", "Next construction action")),
        ("positive-edge-035.yaml", ("Outcome", "Construction result", "Command form", "Authority", "Follow up action")),
        ("positive-edge-036.yaml", ("Result", "Boundary assessment", "Shell candidate", "Authority")),
        ("positive-edge-037.yaml", ("Result", "Boundary assessment", "Shell candidate", "Authority", "Next construction action", "Extra label")),
    )
    for fixture, labels in requested_label_sets:
        path = SCC_TASKS / fixture
        task_name = path.relative_to(ROOT).as_posix()
        task = load_projection(path)
        if not all(f"`{label}`" in task.prompt for label in labels):
            fail(f"{task_name} no longer supplies its requested label set")
        if any(coaching in task.prompt.lower() for coaching in ("fallback", "default field labels", "safe canonical", "safe default", "do not emit")):
            fail(f"{task_name} coaches the required fallback in its prompt")
        output = canonical_output("Review the candidate boundary.", 'tool "hello world"')
        if not accepts_task_completion(task, output, task_name):
            fail(f"{task_name} does not accept its canonical fallback envelope")


def check_mixed_label_handoff_precedence() -> None:
    path = SCC_TASKS / "positive-edge-038.yaml"
    task = load_projection(path)
    task_name = path.relative_to(ROOT).as_posix()
    if not all(fragment in task.prompt for fragment in ("POSIX", "macOS", "Result,", "Next construction")):
        fail(f"{task_name} no longer combines mixed-request and replacement-label inputs")
    canonical = canonical_output(
        'Request a separate portability review of tool run "$label".',
        'tool run "$label"',
    ).replace("Construction result: VALID", "Construction result: REWRITE").replace(
        "The supplied bytes preserve the requested boundary.",
        "The quoted label preserves one argument boundary.",
    )
    if not accepts_task_completion(task, canonical, task_name):
        fail(f"{task_name} does not accept its canonical mixed-request handoff")
    labels = ("Result", "Boundary assessment", "Shell candidate", "Authority", "Next construction action")
    if accepts_task_completion(task, custom_output(labels, "Request a separate portability review of the exact candidate."), task_name):
        fail(f"{task_name} accepts replacement labels despite mixed-request handoff precedence")


def check_terminal_newline_fixture_prompt() -> None:
    path = PORTABILITY_TASKS / "positive-edge-29.yaml"
    task = load_projection(path)
    task_name = path.relative_to(ROOT).as_posix()
    coaching = (
        "terminal candidate newline",
        "line continuation",
        "dash instead treats",
        "if that newline is dropped",
        "final two-space-only payload line",
    )
    if any(fragment in task.prompt.lower() for fragment in coaching):
        fail(f"{task_name} gives the decoder interpretation away in its prompt")


def canonical_output(next_step: str, candidate: str = "printf '%s\\n' value") -> str:
    return render_scc_report(
        SCCReport(
            "VALID",
            "The supplied bytes preserve the requested boundary.",
            candidate,
            "NOT ASSESSED BY THIS SKILL",
            next_step,
        )
    )


def check_scc_grammar() -> None:
    """Keep canonical/custom rendering and field-order parsing in one grammar."""

    report = SCCReport(
        "VALID",
        "The JSON payload is incorrectly quoted, so it splits into multiple arguments.",
        'tool "hello world"',
        "NOT ASSESSED BY THIS SKILL",
        "Review the candidate boundary.",
    )
    for labels in (
        SCC_CANONICAL_LABELS,
        ("Result", "Boundary assessment", "Shell candidate", "Authority", "Next construction action"),
    ):
        rendered = render_scc_report(report, labels)
        if parse_scc_report(rendered, labels) != report:
            fail("SCC grammar does not round-trip a semantic report")
        if parse_scc_report(f"{rendered}\n", labels) != report:
            fail("SCC grammar does not accept its optional terminal LF")
        try:
            parse_scc_report("\n".join(reversed(rendered.splitlines())), labels)
        except GrammarError:
            pass
        else:
            fail("SCC grammar accepts reordered fields")
        for separator in LINE_SEPARATORS:
            if separator == "\n":
                continue
            try:
                parse_scc_report(rendered.replace("\n", separator), labels)
            except GrammarError:
                pass
            else:
                fail(f"SCC grammar accepts {separator!r} as a field separator")

    fixture = SCC_TASKS / "positive-edge-029.yaml"
    if not accepts_task_completion(load_projection(fixture), render_scc_report(report, (
        "Result",
        "Boundary assessment",
        "Shell candidate",
        "Authority",
        "Next construction action",
    )), fixture.relative_to(ROOT).as_posix()):
        fail("SCC grammar no longer serializes the custom-label task projection")
    assertions = load_projection(SCC_EVAL).assertions
    separator_assertion = next(
        (item for item in assertions if isinstance(item, str) and "x1c-\\x1e\\x85" in item),
        None,
    )
    if separator_assertion is None:
        fail("SCC output contract no longer rejects non-LF field separators")
    custom_contract_assertion = next(
        (item for item in assertions if isinstance(item, str) and 'custom.group("authority")' in item),
        None,
    )
    if custom_contract_assertion is None:
        fail("SCC output contract no longer activates malformed custom envelopes")
    custom_labels = ("Result", "Boundary assessment", "Shell candidate", "Authority", "Next construction action")
    malformed_custom = render_scc_report(report, custom_labels).replace("Result: VALID", "Result: \rVALID")
    if accepts_task_completion(load_projection(fixture), malformed_custom, fixture.relative_to(ROOT).as_posix()):
        fail("custom-label task projection accepts CR before the disposition")
    if evaluate_assertion(separator_assertion, malformed_custom, SCC_EVAL):
        fail("SCC output contract accepts CR before a custom disposition")
    if evaluate_assertion(custom_contract_assertion, malformed_custom, SCC_EVAL):
        fail("custom SCC semantic policy bypasses CR before the disposition")
    multiline = SCCReport(
        "VALID",
        "The quoted payload preserves each physical line and its terminal newline.",
        "tool 'first\nsecond\n'\n",
        "NOT ASSESSED BY THIS SKILL",
        "Review the candidate boundary.",
    )
    rendered_multiline = render_scc_report(multiline)
    if parse_scc_report(rendered_multiline) != multiline:
        fail("SCC grammar does not round-trip a multiline candidate")
    for candidate in ("Not provided", "|"):
        block_candidate = SCCReport(
            "VALID",
            "The candidate representation preserves the supplied literal data.",
            candidate,
            "NOT ASSESSED BY THIS SKILL",
            "Review the candidate boundary.",
        )
        if parse_scc_report(render_scc_report(block_candidate)) != block_candidate:
            fail(f"SCC grammar does not disambiguate the {candidate!r} inline candidate")
    multiline_fixture = SCC_TASKS / "positive-edge-034.yaml"
    if not accepts_task_completion(load_projection(multiline_fixture), rendered_multiline, multiline_fixture.relative_to(ROOT).as_posix()):
        fail("SCC grammar no longer serializes the terminal-newline multiline fixture")
    for malformed_block in (
        rendered_multiline.replace("  tool 'first", " tool 'first", 1),
        rendered_multiline.replace("  second\n", "Execution authority: shadow\n", 1),
        rendered_multiline.replace("  tool 'first", "Execution authority: shadow", 1),
    ):
        try:
            parse_scc_report(malformed_block)
        except GrammarError:
            pass
        else:
            fail("SCC grammar accepts malformed block-candidate framing")
    field_values = (
        "The JSON payload is incorrectly quoted, so it splits into multiple arguments.",
        'tool "hello world"',
        "NOT ASSESSED BY THIS SKILL",
        "Review the candidate boundary.",
    )
    for labels in (
        SCC_CANONICAL_LABELS,
        ("Result", "Boundary assessment", "Shell candidate", "Authority", "Next construction action"),
    ):
        rendered = render_scc_report(report, labels)
        for value in field_values:
            for separator in LINE_SEPARATORS:
                if separator == "\n":
                    continue
                malformed = rendered.replace(value, f"{value}{separator}extra", 1)
                try:
                    parse_scc_report(malformed, labels)
                except GrammarError:
                    pass
                else:
                    fail(f"SCC grammar accepts {separator!r} inside a field")
                if evaluate_assertion(separator_assertion, malformed, SCC_EVAL):
                    fail(f"SCC output contract accepts {separator!r} inside a field")
    for invalid in (
        SCCReport("", "assessment", "candidate", "authority", "next"),
        SCCReport("VALID", "assessment\rvalue", "candidate", "authority", "next"),
        SCCReport("VALID", "assessment\u2028value", "candidate", "authority", "next"),
    ):
        try:
            render_scc_report(invalid)
        except GrammarError:
            pass
        else:
            fail("SCC grammar accepts a value that cannot round-trip")
    semantic_invalid = (
        SCCReport("UNKNOWN", "assessment", "candidate", "NOT ASSESSED BY THIS SKILL", "next"),
        SCCReport("VALID", " ", "candidate", "NOT ASSESSED BY THIS SKILL", "next"),
        SCCReport("VALID", "assessment", "candidate", "APPROVED", "next"),
        SCCReport("VALID", "assessment", "candidate", "NOT ASSESSED BY THIS SKILL", " "),
        SCCReport("BLOCKED", "assessment", "candidate", "NOT ASSESSED BY THIS SKILL", "clarify one fact"),
        SCCReport("VALID\x00", "assessment", "candidate", "NOT ASSESSED BY THIS SKILL", "next"),
        SCCReport("VALID", "assessment\x00", "candidate", "NOT ASSESSED BY THIS SKILL", "next"),
        SCCReport("VALID", "assessment", "candidate\x00", "NOT ASSESSED BY THIS SKILL", "next"),
        SCCReport("VALID", "assessment", "candidate", "NOT ASSESSED BY THIS SKILL\x00", "next"),
        SCCReport("VALID", "assessment", "candidate", "NOT ASSESSED BY THIS SKILL", "next\x00"),
    )
    for invalid in semantic_invalid:
        try:
            render_scc_report(invalid)
        except GrammarError:
            pass
        else:
            fail(f"SCC renderer accepts an invalid semantic report: {invalid!r}")
        serialized = "\n".join(f"{label}: {value}" for label, value in zip(SCC_CANONICAL_LABELS, (
            invalid.result,
            invalid.assessment,
            invalid.candidate,
            invalid.authority,
            invalid.next,
        )))
        try:
            parse_scc_report(serialized)
        except GrammarError:
            pass
        else:
            fail(f"SCC parser accepts an invalid semantic report: {invalid!r}")
    try:
        validate_scc_labels(("Result", "Assessment", "Candidate", "Authority", 7))  # type: ignore[arg-type]
    except GrammarError:
        pass
    else:
        fail("SCC grammar does not normalize malformed labels to GrammarError")
    for invalid_labels in (
        ("Outcome-label", "Boundary assessment", "Shell candidate", "Authority", "Next construction action"),
        (" Outcome", "Boundary assessment", "Shell candidate", "Authority", "Next construction action"),
        ("Résultat", "Boundary assessment", "Shell candidate", "Authority", "Next construction action"),
        ("Outcome", "Boundary assessment", "Construction candidate", "Authority", "Next construction action"),
        ("construction result", "Boundary assessment", "Shell candidate", "Authority", "Next construction action"),
    ):
        try:
            validate_scc_labels(invalid_labels)
        except GrammarError:
            pass
        else:
            fail(f"SCC grammar accepts an invalid custom label set: {invalid_labels!r}")


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
        ast.Eq,
        ast.NotEq,
        ast.In,
        ast.NotIn,
        ast.Call,
        ast.Attribute,
        ast.Name,
        ast.Load,
        ast.Store,
        ast.Constant,
        ast.BinOp,
        ast.Add,
        ast.Dict,
        ast.Set,
        ast.SetComp,
        ast.GeneratorExp,
        ast.comprehension,
        ast.Tuple,
        ast.Subscript,
    )
    allowed_names = {"action", "active", "all", "canonical", "custom", "deferred", "fields", "len", "m", "name", "output", "re", "text"}
    allowed_attributes = {"findall", "fullmatch", "group", "join", "lower", "match", "rstrip", "search", "startswith", "sub"}
    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            fail(f"custom-label shared assertion uses unsupported syntax: {type(node).__name__}")
        if isinstance(node, ast.Name) and node.id not in allowed_names:
            fail(f"custom-label shared assertion uses unsupported name: {node.id}")
        if isinstance(node, ast.Attribute) and node.attr not in allowed_attributes:
            fail(f"custom-label shared assertion uses unsupported attribute: {node.attr}")
    # Waza exposes grader helpers as eval locals. Nested lambdas and
    # comprehensions resolve free names through globals, so keep this split to
    # catch assertions that accidentally rely on a different namespace.
    return bool(
        eval(
            compile(tree, source.as_posix(), "eval"),
            {"__builtins__": {}},
            {"all": all, "len": len, "output": output, "re": re},
        )
    )


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


def check_custom_label_contextual_claim_parity() -> None:
    assertions = load_projection(SCC_EVAL).assertions
    canonical_action_assertion = next(
        (item for item in assertions if isinstance(item, str) and "\\buse\\b(?=" in item and 'output.startswith("Construction result: VALID' in item),
        None,
    )
    contextual_assertion = next(
        (item for item in assertions if isinstance(item, str) and "portable|compatible" in item and "(canonical or custom).group" in item),
        None,
    )
    handoff_only_assertion = next(
        (item for item in assertions if isinstance(item, str) and "A portability handoff" not in item and "portability[ \\t]+review\\b[^\\n]{0,160}" in item and "execut(?:e|ed|ing|ion)" in item),
        None,
    )
    action_assertion = next(
        (item for item in assertions if isinstance(item, str) and "later|eventually" in item and "(canonical or custom).group" in item),
        None,
    )
    imperative_assertion = next(
        (item for item in assertions if isinstance(item, str) and "(?:please|carefully|actually|now|directly)" in item and "(canonical or custom).group(\"next\")" in item),
        None,
    )
    indirect_execution_assertion = next(
        (item for item in assertions if isinstance(item, str) and "Indirect verification-by-execution" not in item and "(?:by|through|via|after|before)" in item and "(canonical or custom).group(\"next\")" in item),
        None,
    )
    recommendation_assertion = next(
        (item for item in assertions if isinstance(item, str) and "endors(?:e|es|ed|ing|ement)" in item and "(canonical or custom).group" in item),
        None,
    )
    pronoun_assertion = next(
        (item for item in assertions if isinstance(item, str) and "(?:script|form)" in item and "(canonical or custom).group" in item),
        None,
    )
    remainder_assertion = next(
        (item for item in assertions if isinstance(item, str) and "circumstances|conditions" in item and "(canonical or custom).group" in item),
        None,
    )
    parsing_assertion = next(
        (item for item in assertions if isinstance(item, str) and "parses?(?:[ \\t]+successfully)?" in item and "(canonical or custom).group" in item),
        None,
    )
    parsing_success_assertion = next(
        (item for item in assertions if isinstance(item, str) and "parse|parses|parsed|parsing" in item and "(canonical or custom).group" in item),
        None,
    )
    validation_success_assertion = next(
        (item for item in assertions if isinstance(item, str) and "validate|validates|validated|validating|validation" in item and "(canonical or custom).group" in item),
        None,
    )
    if canonical_action_assertion is None or contextual_assertion is None or handoff_only_assertion is None or action_assertion is None or imperative_assertion is None or indirect_execution_assertion is None or recommendation_assertion is None or pronoun_assertion is None or remainder_assertion is None or parsing_assertion is None or parsing_success_assertion is None or validation_success_assertion is None:
        fail("shell-command-construction output contract no longer has a shared contextual-claim policy")

    labels = ("Result", "Boundary assessment", "Shell candidate", "Authority", "Next construction action")
    allowed_next_step = "Review whether the candidate is portable."
    for output in (canonical_output(allowed_next_step), custom_output(labels, allowed_next_step)):
        if not all(evaluate_assertion(assertion, output, SCC_EVAL) for assertion in (contextual_assertion, action_assertion, pronoun_assertion)):
            fail("shared contextual-claim policy rejects review wording without a portability conclusion")

    boundary_diagnosis = "The JSON payload is incorrectly quoted, so it splits into multiple arguments."
    for output in (
        canonical_output("Review the candidate boundary.").replace("The supplied bytes preserve the requested boundary.", boundary_diagnosis),
        custom_output(labels, "Review the candidate boundary.").replace("The supplied bytes preserve the requested boundary.", boundary_diagnosis),
    ):
        if not evaluate_assertion(remainder_assertion, output, SCC_EVAL):
            fail("shared downstream-semantic policy rejects a construction boundary diagnosis")

    for next_step in (
        "Proceed with a separate portability review of the exact candidate.",
        "Go ahead with a separate portability review of the exact candidate.",
        "Use the candidate for a separate portability review.",
        "The candidate should be used for a separate portability review.",
    ):
        canonical = canonical_output(next_step)
        if not evaluate_assertion(canonical_action_assertion, canonical, SCC_EVAL):
            fail(f"canonical action policy rejects {next_step!r}")
        if not all(evaluate_assertion(assertion, canonical, SCC_EVAL) for assertion in (contextual_assertion, action_assertion, pronoun_assertion)):
            fail(f"shared canonical policy rejects {next_step!r}")
        custom = custom_output(labels, next_step)
        if not all(evaluate_assertion(assertion, custom, SCC_EVAL) for assertion in (contextual_assertion, action_assertion, pronoun_assertion)):
            fail(f"shared custom policy rejects {next_step!r}")

    execution_advice = "Use the candidate for deployment."
    if evaluate_assertion(canonical_action_assertion, canonical_output(execution_advice), SCC_EVAL):
        fail("canonical action policy accepts execution advice disguised as use wording")
    if evaluate_assertion(action_assertion, custom_output(labels, execution_advice), SCC_EVAL):
        fail("shared custom action policy accepts execution advice disguised as use wording")
    for output in (canonical_output("Proceed with deployment."), custom_output(labels, "Proceed with deployment.")):
        if evaluate_assertion(contextual_assertion, output, SCC_EVAL):
            fail("shared contextual policy accepts unqualified proceed wording")

    for next_step in (
        "Review the candidate, then run it.",
        "Review the candidate and deploy it.",
        "Review the candidate; execute it.",
        "Review the candidate. Run it.",
        "Review the candidate: deploy it.",
    ):
        for output in (canonical_output(next_step), custom_output(labels, next_step)):
            if evaluate_assertion(imperative_assertion, output, SCC_EVAL):
                fail(f"shared imperative policy accepts execution advice: {next_step!r}")

    for next_step in ("Apply this rewrite.", "Review the candidate boundary."):
        for output in (canonical_output(next_step), custom_output(labels, next_step)):
            if not evaluate_assertion(imperative_assertion, output, SCC_EVAL):
                fail(f"shared imperative policy rejects construction-only action: {next_step!r}")

    for next_step in ("Verify the candidate by executing it.", "Check the candidate through running it."):
        for output in (canonical_output(next_step), custom_output(labels, next_step)):
            if evaluate_assertion(indirect_execution_assertion, output, SCC_EVAL):
                fail(f"shared indirect-execution policy accepts execution advice: {next_step!r}")

    for next_step in (
        "Review the candidate; recommend deploying it.",
        "Review the candidate; suggest running it.",
        "Review the candidate; consider executing it.",
        "Review the candidate; advise deploying it.",
        "Review the candidate; encourage running it.",
        "Review the candidate; urge executing it.",
        "Review the candidate; propose deployment.",
        "Review the candidate; recommendation: execute the candidate.",
        "Review the candidate; recommend applying the corrected candidate.",
        "Review the candidate; suggest applying the revised command.",
        "Review the candidate; advise applying the exact candidate.",
    ):
        for output in (canonical_output(next_step), custom_output(labels, next_step)):
            if evaluate_assertion(recommendation_assertion, output, SCC_EVAL):
                fail(f"shared recommendation policy accepts execution advice: {next_step!r}")

    for next_step in ("Apply this rewrite.", "Review the candidate boundary."):
        for output in (canonical_output(next_step), custom_output(labels, next_step)):
            if not evaluate_assertion(recommendation_assertion, output, SCC_EVAL):
                fail(f"shared recommendation policy rejects construction-only action: {next_step!r}")

    for next_step in (
        "Request a separate portability review of the exact candidate and then deploy it.",
        "Use the candidate for a separate portability review and execution.",
        "Proceed with a separate portability review of the exact candidate before running it.",
        "Request a separate portability review of the exact candidate; run it.",
    ):
        for output in (canonical_output(next_step), custom_output(labels, next_step)):
            if evaluate_assertion(handoff_only_assertion, output, SCC_EVAL):
                fail(f"portability handoff policy accepts appended execution advice: {next_step!r}")

    for claim in ("The candidate is portable.", "The candidate is safe."):
        for output in (canonical_output(claim), custom_output(labels, claim)):
            if evaluate_assertion(contextual_assertion, output, SCC_EVAL):
                fail(f"shared contextual-claim policy accepts {claim!r}")

    for next_step in ("Review later.", "The candidate works on macOS.", "The candidate works with POSIX sh.", "The candidate runs for Ubuntu."):
        for output in (canonical_output(next_step), custom_output(labels, next_step)):
            if evaluate_assertion(action_assertion, output, SCC_EVAL):
                fail(f"shared action policy accepts {next_step!r}")

    for claim in ("Review the candidate boundary; it is portable.", "The script is portable.", "It is safe."):
        for output in (canonical_output(claim), custom_output(labels, claim)):
            if evaluate_assertion(pronoun_assertion, output, SCC_EVAL):
                fail(f"shared pronoun policy accepts {claim!r}")

    for next_step in (
        "Review the candidate boundary when circumstances permit.",
        "Review the candidate boundary once the change window opens.",
        "Review the candidate boundary; it works on macOS.",
        "The script runs with POSIX sh.",
        "The form was executed.",
        "The JSON payload is syntactically valid.",
    ):
        for output in (canonical_output(next_step), custom_output(labels, next_step)):
            if evaluate_assertion(remainder_assertion, output, SCC_EVAL):
                fail(f"shared remainder policy accepts {next_step!r}")

    for claim in ("The JSON parses successfully.", "The payload parses."):
        for output in (canonical_output(claim), custom_output(labels, claim)):
            if evaluate_assertion(parsing_assertion, output, SCC_EVAL):
                fail(f"shared parsing policy accepts {claim!r}")

    for claim in ("The JSON parsed successfully.", "The payload parsed correctly.", "The JSON parsing succeeded."):
        for output in (canonical_output(claim), custom_output(labels, claim)):
            if evaluate_assertion(parsing_success_assertion, output, SCC_EVAL):
                fail(f"shared parsing-success policy accepts {claim!r}")

    for claim in ("The payload validates successfully.", "The JSON validates correctly.", "The payload validation succeeded."):
        for output in (canonical_output(claim), custom_output(labels, claim)):
            if evaluate_assertion(validation_success_assertion, output, SCC_EVAL):
                fail(f"shared validation-success policy accepts {claim!r}")


def check_waza_nested_scope_regression() -> None:
    """Evaluate every SCC assertion with Waza's globals/locals split."""

    assertions = load_projection(SCC_EVAL).assertions
    valid = canonical_output("Review the candidate boundary.")
    for index, assertion in enumerate(assertions, start=1):
        try:
            accepted = evaluate_assertion(assertion, valid, SCC_EVAL)
        except (NameError, TypeError) as error:
            fail(f"SCC assertion {index} cannot resolve a Waza local from nested scope: {error}")
        if not accepted:
            fail(f"SCC assertion {index} rejects the canonical valid output")

    broken = '(lambda: re.search(r"candidate", output) is not None)()'
    try:
        evaluate_assertion(broken, valid, SCC_EVAL)
    except NameError:
        pass
    else:
        fail("projection evaluator no longer models Waza's nested-scope namespace split")


def check_scc_static_projection_regressions() -> None:
    """Keep output-independent examples in this preflight, not Waza trials."""

    assertions = load_projection(SCC_EVAL).assertions
    if any("output" not in assertion for assertion in assertions):
        fail("SCC output-contract grader contains an output-independent assertion")
    activation_assertion = next(
        (item for item in assertions if "Construction result: (VALID|REWRITE|BLOCKED)" in item),
        None,
    )
    if activation_assertion is None:
        fail("SCC output contract no longer detects wrapped canonical fields")
    for wrapped in (
        "```text\nConstruction result: VALID\n",
        ">````c++ {.example}\n>Construction result: VALID\n",
    ):
        if evaluate_assertion(activation_assertion, wrapped, SCC_EVAL):
            fail("SCC output contract accepts an incomplete wrapped envelope")
    for result_label in ("Outcome-label", "Result: injected"):
        malformed = "\n".join((
            f"{result_label}: VALID",
            "Boundary assessment: The candidate boundary is represented.",
            "Shell candidate: tool value",
            "Authority: NOT ASSESSED BY THIS SKILL",
            "Next construction action: Review the candidate boundary.",
        ))
        if all(evaluate_assertion(assertion, malformed, SCC_EVAL) for assertion in assertions):
            fail("SCC output contract accepts a malformed custom result label")


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


def check_portability_target_named_fix() -> None:
    """Permit the task's stated GNU/macOS alternative to feature detection."""

    path = PORTABILITY_TASKS / "positive-trigger-2.yaml"
    task = load_projection(path)
    regex = next(
        (item for item in task.regex_match if "Portable fix:" in item and "GNU" in item),
        None,
    )
    if regex is None:
        fail("positive-trigger-2 no longer checks its sed portability fix")
    target_named = "1. sed editing differs\n  Portable fix: GNU uses sed -i; macOS uses sed -i ''"
    if not matches(regex, target_named, path.relative_to(ROOT).as_posix()):
        fail("positive-trigger-2 rejects its valid GNU/macOS target-named sed fix")


def check_portability_residual_risk_termination() -> None:
    assertions = load_projection(PORTABILITY_EVAL).assertions
    assertion = next(
        (
            item
            for item in assertions
            if isinstance(item, str)
            and 'r"(?im)^Portability residual risk:' in item
            and "output) is None" in item
        ),
        None,
    )
    if assertion is None:
        fail("shell-portability output contract no longer rejects prose after residual risk")
    valid = normal_portability_clean_output()
    if not evaluate_assertion(assertion, valid, PORTABILITY_EVAL):
        fail("portability output contract rejects a terminal residual-risk field")
    if evaluate_assertion(assertion, f"{valid}\n\n  Extra prose", PORTABILITY_EVAL):
        fail("portability output contract accepts prose after residual risk")
    if not evaluate_assertion(assertion, f"{valid}\n", PORTABILITY_EVAL):
        fail("portability output contract rejects a terminal newline after residual risk")


def normal_portability_clean_output() -> str:
    return "\n".join(
        (
            "Portability verdict: CLEAN",
            "Portability target: POSIX sh on Ubuntu and macOS",
            "Portability interpreter: POSIX sh",
            "",
            "Portability findings: None",
            "",
            "Portability checklist status:",
            "- Interpreter and shebang: covered",
            "- Bashisms: covered",
            "- Utilities and flags: covered",
            "- Output and behavior: covered",
            "- Verification: covered",
            "",
            "Portability residual risk: None.",
        )
    )


def check_portability_output_contract_assertions() -> None:
    """Evaluate every portability assertion in Waza's actual namespace shape."""

    valid = normal_portability_clean_output()
    for index, assertion in enumerate(load_projection(PORTABILITY_EVAL).assertions, start=1):
        try:
            accepted = evaluate_assertion(assertion, valid, PORTABILITY_EVAL)
        except (NameError, TypeError) as error:
            fail(f"portability assertion {index} cannot run in the Waza namespace: {error}")
        if not accepted:
            fail(f"portability assertion {index} rejects the normal valid report")


def check_portability_ordered_envelopes() -> None:
    assertions = load_projection(PORTABILITY_EVAL).assertions
    assertion = next(
        (item for item in assertions if isinstance(item, str) and "re.fullmatch" in item and "Portability checklist status:" in item),
        None,
    )
    if assertion is None:
        fail("shell-portability output contract no longer requires complete ordered envelopes")
    clean_severity_assertion = next(
        (item for item in assertions if isinstance(item, str) and "CLEAN may list LOW-only" not in item and "(?:CRITICAL|HIGH|MEDIUM)" in item and "Portability checklist status" in item),
        None,
    )
    if clean_severity_assertion is None:
        fail("shell-portability output contract no longer rejects material CLEAN findings")

    normal_clean = normal_portability_clean_output()
    normal_finding = "\n".join(
        (
            "Portability verdict: CONCERNS",
            "Portability target: POSIX sh on Ubuntu and macOS",
            "Portability interpreter: POSIX sh",
            "",
            "Portability findings:",
            "1. Non-portable utility",
            "  Severity: MEDIUM",
            "  Classification: Likely risk",
            "  Evidence: utility behavior varies by target",
            "  Rule: utilities-flags",
            "  Risk: output changes on BSD",
            "  Portable fix: use a target branch",
            "  Verification: run under dash",
            "",
            "Portability checklist status:",
            "- Interpreter and shebang: covered",
            "- Bashisms: covered",
            "- Utilities and flags: missing",
            "- Output and behavior: covered",
            "- Verification: covered",
            "",
            "Portability residual risk: target branch remains required.",
        )
    )
    reduced_block = "\n".join(
        (
            "Portability verdict: BLOCK",
            "Portability target: default baseline",
            "",
            "Portability findings:",
            "1. Missing command",
            "  Severity: LOW",
            "  Classification: Open question",
            "  Evidence: no command was supplied",
            "  Rule: interpreter-shebang",
            "  Risk: no safe conclusion is possible",
            "  Portable fix: supply the command",
            "  Verification: N/A",
        )
    )
    for output in (
        normal_clean,
        normal_finding,
        normal_finding.replace("Portability verdict: CONCERNS", "Portability verdict: CLEAN").replace("Severity: MEDIUM", "Severity: LOW"),
        normal_finding.replace("Portability verdict: CONCERNS", "Portability verdict: BLOCK"),
        reduced_block,
    ):
        if not evaluate_assertion(assertion, output, PORTABILITY_EVAL):
            fail("portability output contract rejects a valid ordered report envelope")

    reordered = normal_clean.replace(
        "Portability target: POSIX sh on Ubuntu and macOS\nPortability interpreter: POSIX sh",
        "Portability interpreter: POSIX sh\nPortability target: POSIX sh on Ubuntu and macOS",
    )
    duplicate = normal_clean.replace(
        "Portability interpreter: POSIX sh\n",
        "Portability interpreter: POSIX sh\nPortability interpreter: POSIX sh\n",
    )
    reduced_duplicate = reduced_block.replace(
        "\n\nPortability findings:",
        "\nPortability target: duplicate\n\nPortability findings:",
    )
    for output in (reordered, duplicate, reduced_duplicate):
        if evaluate_assertion(assertion, output, PORTABILITY_EVAL):
            fail("portability output contract accepts a reordered or duplicate report field")
    clean_medium = normal_finding.replace("Portability verdict: CONCERNS", "Portability verdict: CLEAN")
    if evaluate_assertion(clean_severity_assertion, clean_medium, PORTABILITY_EVAL):
        fail("portability output contract accepts a CLEAN report with a MEDIUM finding")


def main() -> None:
    try:
        check_candidate_fixtures()
        check_heredoc_delimiter_fixture()
        check_leading_pipe_handoff()
        check_negative_marker_exclusions(SCC_REPORT)
        check_negative_marker_exclusions(PORTABILITY_REPORT)
        check_negative_custom_envelopes()
        check_scc_grammar()
        check_custom_label_deployment_regression()
        check_custom_label_contextual_claim_parity()
        check_waza_nested_scope_regression()
        check_scc_static_projection_regressions()
        check_label_fallback_fixtures()
        check_mixed_label_handoff_precedence()
        check_terminal_newline_fixture_prompt()
        check_portability_preamble_regression()
        check_portability_target_named_fix()
        check_portability_residual_risk_termination()
        check_portability_output_contract_assertions()
        check_portability_ordered_envelopes()
    except CheckError as error:
        print(f"shell contract projection check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    print("shell contract projection check passed")


if __name__ == "__main__":
    main()
