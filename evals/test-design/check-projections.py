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
    manifest = yaml.safe_load((root / "eval.yaml").read_text())
    metrics = {metric["name"]: metric for metric in manifest["metrics"]}
    assert abs(sum(metric["weight"] for metric in metrics.values()) - 1.0) < 1e-9
    assert metrics["production_unchanged"]["threshold"] == 1.0
    for path in sorted((root / "tasks").glob("*.yaml")):
        task = yaml.safe_load(path.read_text())
        graders = {grader["name"]: grader for grader in task["graders"]}
        assert graders.keys() <= metrics.keys(), (path.name, "unregistered metric")
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
    assert "defect" in patterns[4]
    assert patterns[2] == "(?m)^" + report.MARKERS[2] + " " + report.IMPLEMENT_STATUS_PATTERN + "$"
    diff = graders["production_unchanged"]
    assert diff["type"] == "diff" and diff["config"]["update_snapshots"] is False
    expectation = diff["config"]["expected_files"]
    assert expectation == [{"path": "clamp.js", "snapshot": "snapshots/clamp.js"}]
    repo = root.parents[1]
    snapshot = repo / diff["config"]["context_dir"] / expectation[0]["snapshot"]
    fixture = next(file["content"] for file in task["inputs"]["files"] if file["path"] == "clamp.js")
    assert snapshot.read_bytes() == fixture.encode(), "production snapshot drift"
    assert snapshot.read_bytes() != fixture.replace("Math.max", "Math.min").encode()
    # A canonical sibling response must remain legal on negative tasks.
    sibling = "Test cases:\n- F-1 rollback case\nEvidence: supplied review finding\nVerification: proposed"
    assert not any(token in sibling for token in exclusions)
    for skill_root in (repo / "skills", repo / ".agents/skills"):
        for path in skill_root.rglob("*.md"):
            if path.resolve().is_relative_to((repo / "skills/test-design").resolve()):
                continue
            content = path.read_text()
            assert not any(label in content for label in report.MARKERS + report.CUSTOM_LABELS), (
                path, "report marker collision",
            )
    for name in expected:
        task = yaml.safe_load((root / "tasks" / name).read_text())
        patterns = next(g for g in task["graders"] if g["name"] == "task_completion")["config"]["regex_match"]
        assert all("(?is)" in pattern for pattern in patterns if ".{" in pattern), (name, "missing DOTALL")
    print("test-design task/profile/label projections: passed")


if __name__ == "__main__":
    main()
