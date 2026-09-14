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
        template = body.split("## Output Format\n", 1)[1].split("## Examples\n", 1)[0]
    except IndexError:
        fail("skills/shell-portability/SKILL.md has no bounded Output Format section")
    for marker in CONTRACT.normal_markers:
        if marker not in template:
            fail(f"skills/shell-portability/SKILL.md is missing normal marker {marker!r}")
    for marker in CONTRACT.reduced_markers:
        if marker not in template:
            fail(f"skills/shell-portability/SKILL.md is missing reduced marker {marker!r}")


def requires_marker(task: Path, projection: dict[str, object], marker: str) -> None:
    patterns = projection.get("regex_match")
    if not isinstance(patterns, list):
        fail(f"{task.relative_to(ROOT)} has no regex_match projection")
    if not any(marker.casefold() in pattern.casefold() for pattern in patterns):
        fail(f"{task.relative_to(ROOT)} does not require {marker!r} in task_completion")


def check_task_projections() -> None:
    reduced = TASKS / "positive-edge-1.yaml"
    projection = load_projection(reduced)
    for marker in CONTRACT.reduced_markers:
        requires_marker(reduced, projection, marker)
    for task in sorted(TASKS.glob("positive-*.yaml")):
        if task == reduced:
            continue
        projection = load_projection(task)
        for marker in CONTRACT.normal_markers:
            requires_marker(task, projection, marker)
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


def expect_rejected(name: str, output: str) -> None:
    try:
        CONTRACT.validate(output)
    except ContractError:
        return
    fail(f"mutation {name!r} unexpectedly passed")


def check_mutation_matrix() -> int:
    normal = CONTRACT.render_normal(
        verdict="CLEAN",
        target="POSIX sh on macOS and Linux",
        interpreter="#!/bin/sh",
        findings=(),
        checklist={item: "covered" for item in CONTRACT.checklist_items},
        residual_risk="None",
    )
    reduced = CONTRACT.render_insufficient_context(target="default baseline")
    if CONTRACT.validate(normal) != "normal" or CONTRACT.validate(reduced) != "insufficient-context":
        fail("canonical renderers did not round-trip")
    concerns = CONTRACT.render_normal(
        verdict="CONCERNS",
        target="POSIX sh on macOS and Linux",
        interpreter="#!/bin/sh",
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
        ("missing target", lambda: normal.replace("Target: POSIX sh on macOS and Linux\n", "", 1)),
        ("reordered target", lambda: normal.replace("Target: POSIX sh on macOS and Linux\nInterpreter", "Interpreter").replace("#!/bin/sh\n\nFindings", "#!/bin/sh\nTarget: POSIX sh on macOS and Linux\n\nFindings")),
        ("duplicate verdict", lambda: normal.replace("Target:", "Verdict: CLEAN\nTarget:", 1)),
        ("invalid verdict", lambda: normal.replace("Verdict: CLEAN", "Verdict: VALID", 1)),
        ("invalid checklist value", lambda: normal.replace("Bashisms: covered", "Bashisms: optional", 1)),
        ("CLEAN with a finding", lambda: concerns.replace("Verdict: CONCERNS", "Verdict: CLEAN", 1)),
        ("trailing prose", lambda: normal + "\nExtra explanation"),
        ("reduced wrong verdict", lambda: reduced.replace("Verdict: BLOCK", "Verdict: CLEAN", 1)),
        ("reduced full-only field", lambda: reduced.replace("\n\nFindings:", "\nInterpreter: undeclared\n\nFindings:", 1)),
        ("reduced missing finding", lambda: reduced.replace("1. Missing context\n", "", 1)),
    ]
    normal_fields = (
        ("verdict", "Verdict: CLEAN\n"),
        ("target", "Target: POSIX sh on macOS and Linux\n"),
        ("interpreter", "Interpreter: #!/bin/sh\n"),
        ("findings", "Findings: None\n"),
        ("checklist header", "Checklist status:\n"),
        *((f"checklist {item}", f"- {item}: covered\n") for item in CONTRACT.checklist_items),
        ("residual risk", "Residual risk: None"),
    )
    reduced_fields = (
        ("verdict", "Verdict: BLOCK\n"),
        ("target", "Target: default baseline\n"),
        ("findings header", "Findings:\n"),
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
