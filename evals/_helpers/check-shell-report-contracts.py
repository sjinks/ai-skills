#!/usr/bin/env python3
"""Deterministic projection and mutation checks for shell report contracts.

This preflight is deliberately local: it validates the source contract, the
skill template, and decoded task projections without making any model/API call.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Callable

from report_contract import ContractError, Finding, SHELL_PORTABILITY_CONTRACT


ROOT = Path(__file__).resolve().parents[2]
PORTABILITY_ROOT = ROOT / "evals/shell-portability"
TASKS = PORTABILITY_ROOT / "tasks"
SKILL = ROOT / "skills/shell-portability/SKILL.md"
RUNNER = Path(__file__).resolve().with_name("go-regex-runner")
CONTRACT = SHELL_PORTABILITY_CONTRACT


class CheckError(Exception):
    """Raised when a source or projection drifts from the canonical contract."""


def fail(message: str) -> None:
    raise CheckError(message)


def load_projection(path: Path) -> dict[str, object]:
    completed = subprocess.run(
        ("go", "run", ".", "--yaml-projection", str(path)),
        cwd=RUNNER,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        fail(f"could not decode {path.relative_to(ROOT)}: {completed.stderr.strip()}")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        fail(f"could not read projection for {path.relative_to(ROOT)}: {error}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} returned an invalid YAML projection")
    for key in ("regex_match", "regex_not_match", "not_contains"):
        if value.get(key) is None:
            value[key] = []
        if not isinstance(value[key], list) or not all(isinstance(item, str) for item in value[key]):
            fail(f"{path.relative_to(ROOT)} returned an invalid YAML projection")
    return value


def check_skill_template() -> None:
    body = SKILL.read_text()
    try:
        output_format = body.split("## Output Format\n", 1)[1].split("## Examples\n", 1)[0]
    except IndexError:
        fail("skills/shell-portability/SKILL.md has no bounded Output Format section")
    templates = [part.split("```", 1)[0] for part in output_format.split("```text\n")[1:]]
    if len(templates) != 2:
        fail("skills/shell-portability/SKILL.md must define exactly normal and insufficient-context templates")
    normal, reduced = templates
    for profile, template, markers in (
        ("normal", normal, CONTRACT.normal_markers),
        ("insufficient-context", reduced, CONTRACT.reduced_markers),
    ):
        positions: list[int] = []
        for marker in markers:
            if template.count(marker) != 1:
                fail(f"skills/shell-portability/SKILL.md {profile} template must contain {marker!r} exactly once")
            positions.append(template.index(marker))
        if positions != sorted(positions):
            fail(f"skills/shell-portability/SKILL.md {profile} template markers are out of order")
    for marker in sorted(set(CONTRACT.normal_markers) - set(CONTRACT.reduced_markers)):
        if marker in reduced:
            fail(f"skills/shell-portability/SKILL.md insufficient-context template must not contain {marker!r}")


def requires_marker(task: Path, projection: dict[str, object], marker: str) -> None:
    patterns = projection.get("regex_match")
    if not isinstance(patterns, list):
        fail(f"{task.relative_to(ROOT)} has no regex_match projection")
    if not any(has_required_literal(pattern, marker) for pattern in patterns):
        fail(f"{task.relative_to(ROOT)} does not require {marker!r} with a canonical task_completion assertion")


def has_required_literal(pattern: str, marker: str) -> bool:
    """Recognize a literal marker that is not made optional by a local group."""

    start = 0
    while (index := pattern.casefold().find(marker.casefold(), start)) >= 0:
        before = pattern[:index]
        after = pattern[index + len(marker) :]
        if not (before.endswith("(?:") and after.startswith(")?")):
            return True
        start = index + len(marker)
    return False


def check_weakened_marker_rejected(task: Path, projection: dict[str, object], marker: str) -> None:
    """Prove that the assertion check rejects removed or optional markers."""

    patterns = projection.get("regex_match")
    if not isinstance(patterns, list):
        fail(f"{task.relative_to(ROOT)} has no regex_match projection")
    matching = [pattern for pattern in patterns if has_required_literal(pattern, marker)]
    if not matching:
        fail(f"{task.relative_to(ROOT)} has no canonical assertion to mutate for {marker!r}")
    removed = {**projection, "regex_match": [pattern for pattern in patterns if pattern not in matching]}
    optional = {
        **projection,
        "regex_match": [
            pattern.replace(marker, f"(?:{marker})?", 1) if pattern in matching else pattern
            for pattern in patterns
        ],
    }
    for weakness, candidate in (("removed", removed), ("optional", optional)):
        try:
            requires_marker(task, candidate, marker)
        except CheckError:
            continue
        fail(f"{task.relative_to(ROOT)} accepts a {weakness} {marker!r} assertion")


def check_task_projections() -> None:
    for task in sorted(TASKS.glob("positive-*.yaml")):
        projection = load_projection(task)
        normal_only_markers = tuple(
            marker for marker in CONTRACT.normal_markers if marker not in CONTRACT.reduced_markers
        )
        required_normal_only = [
            marker
            for marker in normal_only_markers
            if any(has_required_literal(pattern, marker) for pattern in projection["regex_match"])
        ]
        if len(required_normal_only) == len(normal_only_markers):
            markers = CONTRACT.normal_markers
        elif required_normal_only:
            fail(f"{task.relative_to(ROOT)} mixes normal and insufficient-context task_completion markers")
        else:
            markers = CONTRACT.reduced_markers
            for marker in sorted(set(CONTRACT.normal_markers) - set(CONTRACT.reduced_markers)):
                if not rejects_marker(projection, marker):
                    fail(f"{task.relative_to(ROOT)} does not reject normal-only marker {marker!r}")
        for marker in markers:
            requires_marker(task, projection, marker)
            check_weakened_marker_rejected(task, projection, marker)
    for task in sorted(TASKS.glob("negative-*.yaml")):
        projection = load_projection(task)
        forbidden = projection.get("not_contains")
        if not isinstance(forbidden, list):
            fail(f"{task.relative_to(ROOT)} has no not_contains projection")
        prompt = projection.get("prompt")
        if not isinstance(prompt, str):
            fail(f"{task.relative_to(ROOT)} has no prompt projection")
        for marker in CONTRACT.normal_markers:
            if marker not in forbidden:
                fail(f"{task.relative_to(ROOT)} does not reject {marker!r}")
            if marker in prompt:
                fail(f"{task.relative_to(ROOT)} cannot forbid a marker present in its prompt")


def rejects_marker(projection: dict[str, object], marker: str) -> bool:
    """Accept literal exclusions and regex exclusions that name the label."""

    forbidden = projection.get("not_contains")
    patterns = projection.get("regex_not_match")
    if not isinstance(forbidden, list) or not isinstance(patterns, list):
        return False
    label = marker.removesuffix(":")
    return marker in forbidden or any(label.casefold() in pattern.casefold() for pattern in patterns)


def expect_rejected(name: str, output: str) -> None:
    try:
        CONTRACT.validate(output)
    except ContractError:
        return
    fail(f"mutation {name!r} unexpectedly passed")


def check_mutation_matrix() -> int:
    target = "POSIX sh on macOS and Linux"
    interpreter = "#!/bin/sh"
    normal_target = f"{CONTRACT.target_label}: {target}"
    normal_interpreter = f"{CONTRACT.interpreter_label}: {interpreter}"
    normal_findings = f"{CONTRACT.findings_label}: None"
    normal_verdict = f"{CONTRACT.verdict_label}: CLEAN"
    reduced_verdict = f"{CONTRACT.verdict_label}: BLOCK"
    reduced_target = f"{CONTRACT.target_label}: default baseline"
    reduced_findings = f"{CONTRACT.findings_label}:"
    normal = CONTRACT.render_normal(
        verdict="CLEAN",
        target=target,
        interpreter=interpreter,
        findings=(),
        checklist={item: "covered" for item in CONTRACT.checklist_items},
        residual_risk="None",
    )
    reduced = CONTRACT.render_insufficient_context(target="default baseline")
    if CONTRACT.validate(normal) != "normal" or CONTRACT.validate(reduced) != "insufficient-context":
        fail("canonical renderers did not round-trip")
    concerns = CONTRACT.render_normal(
        verdict="CONCERNS",
        target=target,
        interpreter=interpreter,
        findings=(
            Finding(
                title="GNU-only flag",
                severity="HIGH",
                classification="Confirmed issue",
                evidence="readlink -f",
                rule="utilities-flags",
                risk="macOS cannot resolve the path",
                portable_fix="Use a shell function",
                verification="Run under macOS sh",
            ),
        ),
        checklist={item: "covered" for item in CONTRACT.checklist_items},
        residual_risk="None",
    )
    if CONTRACT.validate(concerns) != "normal":
        fail("non-CLEAN normal renderer did not round-trip")
    mutations: list[tuple[str, Callable[[], str]]] = [
        ("missing target", lambda: normal.replace(normal_target + "\n", "", 1)),
        ("reordered target", lambda: normal.replace(normal_target + "\n" + normal_interpreter, normal_interpreter).replace(interpreter + "\n\n" + normal_findings, interpreter + "\n" + normal_target + "\n\n" + normal_findings)),
        ("duplicate verdict", lambda: normal.replace(f"{CONTRACT.target_label}:", normal_verdict + "\n" + f"{CONTRACT.target_label}:", 1)),
        ("invalid verdict", lambda: normal.replace(normal_verdict, f"{CONTRACT.verdict_label}: VALID", 1)),
        ("invalid checklist value", lambda: normal.replace("Bashisms: covered", "Bashisms: optional", 1)),
        ("CLEAN with a finding", lambda: concerns.replace(f"{CONTRACT.verdict_label}: CONCERNS", normal_verdict, 1)),
        ("non-CLEAN with Findings: None", lambda: normal.replace(normal_verdict, f"{CONTRACT.verdict_label}: CONCERNS", 1)),
        ("invalid finding severity", lambda: concerns.replace("Severity: HIGH", "Severity: INFO", 1)),
        ("invalid finding classification", lambda: concerns.replace("Classification: Confirmed issue", "Classification: Unknown", 1)),
        ("invalid finding rule", lambda: concerns.replace("Rule: utilities-flags", "Rule: made-up-rule", 1)),
        ("truncated normal report", lambda: "\n".join(normal.splitlines()[:3])),
        ("trailing prose", lambda: normal + "\nExtra explanation"),
        ("reduced wrong verdict", lambda: reduced.replace(reduced_verdict, normal_verdict, 1)),
        ("reduced full-only field", lambda: reduced.replace("\n\n" + reduced_findings, "\n" + f"{CONTRACT.interpreter_label}: undeclared" + "\n\n" + reduced_findings, 1)),
        ("reduced missing finding", lambda: reduced.replace("1. Missing context\n", "", 1)),
    ]
    normal_fields = (
        ("verdict", normal_verdict + "\n"),
        ("target", normal_target + "\n"),
        ("interpreter", normal_interpreter + "\n"),
        ("findings", normal_findings + "\n"),
        ("checklist header", f"{CONTRACT.checklist_label}:\n"),
        *((f"checklist {item}", f"- {item}: covered\n") for item in CONTRACT.checklist_items),
        ("residual risk", f"{CONTRACT.residual_label}: None"),
    )
    reduced_fields = (
        ("verdict", reduced_verdict + "\n"),
        ("target", reduced_target + "\n"),
        ("findings header", reduced_findings + "\n"),
        ("numbered finding", "1. Missing context\n"),
        ("severity", "  Severity: LOW\n"),
        ("classification", "  Classification: Open question\n"),
        ("evidence", "  Evidence: No script or commands supplied\n"),
        ("rule", "  Rule: verification\n"),
        ("risk", "  Risk: A portability conclusion would be speculative\n"),
        ("portable fix", "  Portable fix: Provide the script or commands\n"),
        ("verification", "  Verification: N/A"),
    )
    for profile, output, fields in (("normal", normal, normal_fields), ("reduced", reduced, reduced_fields)):
        for field, token in fields:
            mutations.append((f"missing {profile} {field}", lambda output=output, token=token: output.replace(token, "", 1)))
    for name, mutate in mutations:
        expect_rejected(name, mutate())
    return len(mutations)


def main() -> int:
    try:
        check_skill_template()
        check_task_projections()
        mutations = check_mutation_matrix()
    except (CheckError, OSError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f"validated shell portability report contract, task projections, and {mutations} mutations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
