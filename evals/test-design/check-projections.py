#!/usr/bin/env python3
"""Check test-design task projections without model calls."""

import importlib.util
from pathlib import Path

import yaml


def main() -> None:
    """Check every supported report profile has a matching task consumer.

    Also check caller labels, negative exclusions, and implementation assertions.
    """
    root = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("report_contract", root / "check-report.py")
    report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(report)
    expected = {
        "positive-trigger-1.yaml": "plan",
        "positive-edge-1.yaml": "blocked",
        "positive-edge-2.yaml": "implement",
        "positive-edge-3.yaml": "assessment",
    }
    assert report.PROFILES == set(expected.values()), "unsupported or orphan report profile"
    exclusions = set(report.MARKERS + report.CUSTOM_LABELS + ("test-design",))
    for path in sorted((root / "tasks").glob("*.yaml")):
        task = yaml.safe_load(path.read_text())
        graders = {grader["name"]: grader for grader in task["graders"]}
        text = graders["task_completion"]["config"]
        if task["expected"]["should_trigger"]:
            args = graders["report_contract"]["config"]["args"]
            assert args[1] == expected[path.name], (path.name, "wrong profile")
            labels = tuple(args[2:]) if len(args) > 2 else report.MARKERS
            fixture = report.CUSTOM_BLOCKED if labels == report.CUSTOM_LABELS else report.VALID[args[1]]
            report.validate(fixture, args[1], labels)
            for label in labels:
                assert any(label in pattern for pattern in text["regex_match"]), (path.name, label)
        else:
            assert set(text["not_contains"]) == exclusions, (path.name, "negative exclusions")
            assert all(token not in task["inputs"]["prompt"] for token in exclusions), path.name
            assert "skill_invocation" not in graders, path.name
    task = yaml.safe_load((root / "tasks/positive-edge-2.yaml").read_text())
    graders = {grader["name"]: grader for grader in task["graders"]}
    assert graders["changed_test_file"]["type"] == "file"
    patterns = graders["task_completion"]["config"]["regex_match"]
    assert "defect" in patterns[4] and "exit" in patterns[2]
    print("test-design task/profile/label projections: passed")


if __name__ == "__main__":
    main()
