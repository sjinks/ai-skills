#!/usr/bin/env python3
"""Check test-design task projections without model calls."""

import ast
import importlib.util
from pathlib import Path

import yaml


def main() -> None:
    """Check every supported report profile has a matching task consumer.

    Also check caller labels, negative exclusions, and implementation assertions.
    """
    root = Path(__file__).resolve().parent
    ast.parse((root / "check-report.py").read_text(), feature_version=(3, 9))
    spec = importlib.util.spec_from_file_location("report_contract", root / "check-report.py")
    report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(report)
    assert isinstance(report.validate.__annotations__["case_count"], str)
    expected = {
        "positive-trigger-1.yaml": "plan",
        "positive-edge-1.yaml": "blocked",
        "positive-edge-2.yaml": "implement",
        "positive-edge-3.yaml": "assessment",
        "positive-edge-4.yaml": "implement",
        "positive-edge-5.yaml": "implement",
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
            options = report.parse_args(args[1:])
            labels = tuple(options.labels) if options.labels else report.MARKERS
            fixture = report.CUSTOM_BLOCKED if labels == report.CUSTOM_LABELS else report.VALID[args[1]]
            if path.name == "positive-edge-3.yaml":
                assert options.case_count == 1, "singleton task needs machine enforcement"
                assert '"behavior", "expected", "defect"' in task["inputs"]["prompt"]
                fixture = report.SINGLE_ASSESSMENT
            elif path.name == "positive-edge-4.yaml":
                fixture = fixture.replace("=> passed", "=> failed")
            elif path.name == "positive-edge-5.yaml":
                fixture = fixture.rsplit("Test execution:", 1)[0] + "Test execution: Unverified: physical sensor unavailable"
            report.validate(fixture, args[1], labels, options.case_count)
            for label in labels:
                assert any(label in pattern for pattern in text["regex_match"]), (path.name, label)
        else:
            assert set(text["not_contains"]) == exclusions, (path.name, "negative exclusions")
            assert all(token not in task["inputs"]["prompt"] for token in exclusions), path.name
            assert "skill_invocation" not in graders, path.name
    task = yaml.safe_load((root / "tasks/positive-edge-2.yaml").read_text())
    graders = {grader["name"]: grader for grader in task["graders"]}
    test_diff = graders["changed_test_file"]
    assert test_diff["type"] == "diff" and test_diff["config"]["update_snapshots"] is False
    test_expectation = test_diff["config"]["expected_files"]
    assert test_expectation == [{"path": "test/clamp.test.js", "snapshot": "snapshots/clamp.test.js"}]
    test_snapshot = root / "snapshots/clamp.test.js"
    expected_test = test_snapshot.read_text()
    assert expected_test in task["inputs"]["prompt"] or expected_test.split("test('clamps below range'", 1)[1] in task["inputs"]["prompt"]
    assert expected_test.count("test('") == 3
    assert expected_test != "// " + expected_test.replace("\n", "\n// "), "comments cannot replace tests"
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
        assert all(any(flag in pattern for flag in ("(?is)", "(?ims)")) for pattern in patterns if ".{" in pattern), (name, "missing DOTALL")
    # Exact file contracts reject omitted, commented, and altered assertions.
    for name in ("positive-edge-2.yaml", "positive-edge-4.yaml", "positive-edge-5.yaml"):
        task = yaml.safe_load((root / "tasks" / name).read_text())
        graders = {grader["name"]: grader for grader in task["graders"]}
        assert graders["changed_test_file"]["type"] == "diff", name
        for metric in ("changed_test_file", "production_unchanged"):
            config = graders[metric]["config"]
            assert config["context_dir"] == "evals/test-design" and config["update_snapshots"] is False
            expected_file = config["expected_files"][0]
            snapshot = (root / expected_file["snapshot"]).read_text()
            supplied = next(file["content"] for file in task["inputs"]["files"] if file["path"] == expected_file["path"])
            if metric == "production_unchanged":
                assert snapshot == supplied, name
            else:
                assert snapshot != supplied, (name, "tests were not changed")
                assert snapshot != "\n".join("// " + line for line in snapshot.splitlines()) + "\n"
                assert snapshot != snapshot.replace("assert.equal", "// assert.equal")
                assert snapshot != snapshot.replace(", 20);", ", 21);").replace(", 0);", ", 1);"), name
        if name == "positive-edge-4.yaml":
            assert graders["task_completion"]["config"]["regex_match"][2] == r"(?m)^Test execution: Ran: node --test test/clamp\.test\.js => (?:failed|exit 1)$"
        elif name == "positive-edge-5.yaml":
            assert "Unverified:" in graders["task_completion"]["config"]["regex_match"][2]
    assessment = yaml.safe_load((root / "tasks/positive-edge-3.yaml").read_text())
    semantic = next(g for g in assessment["graders"] if g["name"] == "task_completion")["config"]["regex_match"]
    assert all(pattern.startswith("(?ims)^Design evidence:") and pattern.endswith(r"\nTest execution: [^\n]*$") for pattern in semantic[7:9])
    quality = (repo / "skills/test-quality-review/SKILL.md").read_text()
    assert "writing one preselected test" in quality
    assert "caller has already selected one behavior and its expected result" in quality
    quality_root = repo / "evals/test-quality-review"
    spec = importlib.util.spec_from_file_location("quality_report", quality_root / "check-report.py")
    quality_report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(quality_report)
    quality_manifest = yaml.safe_load((quality_root / "eval.yaml").read_text())
    quality_metrics = {m["name"]: m for m in quality_manifest["metrics"]}
    assert "report_contract" in quality_metrics
    assert abs(sum(m["weight"] for m in quality_metrics.values()) - 1.0) < 1e-9
    for path in (quality_root / "tasks").glob("*.yaml"):
        quality_task = yaml.safe_load(path.read_text())
        quality_graders = {g["name"]: g for g in quality_task["graders"]}
        assertions = quality_graders["task_completion"]["config"]
        if quality_task["expected"]["should_trigger"]:
            patterns = assertions["regex_match"]
            assert any("^Verdict:" in pattern for pattern in patterns), path
            assert any("^Findings:" in pattern for pattern in patterns), path
            profile = "author" if path.name == "positive-edge-1.yaml" else "review"
            args = quality_graders["report_contract"]["config"]["args"]
            assert args[1] == profile
            assert ("--wire-fixture" in args) == (profile == "author")
            expected_verdict = {"positive-trigger-1.yaml": "cannot-fail", "positive-trigger-2.yaml": "weak", "positive-edge-1.yaml": "solid"}[path.name]
            assert args[args.index("--verdict") + 1] == expected_verdict
            fixture = quality_report.VALID[profile]
            if profile == "review":
                fixture = fixture.replace("cannot-fail", expected_verdict)
            else:
                fixture = fixture.split("```cpp", 1)[0] + "```cpp\n" + quality_report.WIRE_CODE + "\n```"
            quality_report.validate(fixture, profile, expected=expected_verdict, wire_fixture=profile == "author")
            if profile == "author":
                assert any("^Authored test:" in pattern for pattern in patterns), path
        else:
            forbidden = set(quality_report.MARKERS + ("test-quality-review",))
            assert set(assertions["not_contains"]) == forbidden, path
            assert all(token not in quality_task["inputs"]["prompt"] for token in forbidden), path
            assert "skill_invocation" not in quality_graders, path
    for skill_root in (repo / "skills", repo / ".agents/skills"):
        for path in skill_root.rglob("*.md"):
            if path.resolve().is_relative_to((repo / "skills/test-quality-review").resolve()):
                continue
            assert quality_report.MARKERS[2] not in path.read_text(), (path, "authored marker collision")
    writing = yaml.safe_load((quality_root / "tasks/positive-edge-1.yaml").read_text())
    assert "Write one preselected" in writing["inputs"]["prompt"]
    assert "No dedicated framework" in writing["inputs"]["prompt"]
    assert "TEST(" not in writing["inputs"]["prompt"]
    assert "EXPECT_EQ(" not in writing["inputs"]["prompt"]
    source = (repo / "skills/test-design/SKILL.md").read_text()
    assert "Start with the first label." in source
    assert "regardless of case count" in source
    assert "writing one preselected test" in source
    assert (root / "tasks/negative-close-5.yaml").exists()
    assert "Run final changed tests." in source
    assert "If tests change, rerun." in source
    for name in ("positive-edge-2.yaml", "positive-edge-4.yaml"):
        task = yaml.safe_load((root / "tasks" / name).read_text())
        assert "Execute the final edited tests." in task["inputs"]["prompt"]
        assert "If diagnosis changes tests, rerun them" in task["inputs"]["prompt"]
    assert "including diagnosed failures" in source
    assert "verified or" not in source
    print("test-design task/profile/label projections: passed")


if __name__ == "__main__":
    main()
