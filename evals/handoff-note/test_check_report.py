#!/usr/bin/env python3
"""Static projection checks for handoff-note's exact-schema eval profiles."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parent
TASKS = ROOT / "tasks"
NEGATIVE_MARKERS = {
    "# Handoff Note",
    "Handoff Note:",
    "# Handoff Audit",
    "# Continuation Packet:",
    "# Review:",
    "# Continuation:",
    "handoff-note",
    "## Objective",
    "## State",
    "## Evidence",
    "## Risks and Constraints",
    "## Actions",
    "## Unknowns",
    "## Findings",
    "## Corrections",
    "## Ready",
    "## Goal",
    "## Current State",
    "## Completed Work",
    "## Tried and Avoid",
    "## Next Steps",
    "## Constraints and Boundaries",
    "## Open Questions",
    "## Completeness Findings",
    "## Required Corrections",
    "## Ready to Hand Off",
    "Verdict: BLOCK",
    "Missing input:",
    "Smallest addition to proceed:",
}
STOP_MARKERS = NEGATIVE_MARKERS | {"## Risks"}


def task(name: str) -> dict:
    return yaml.safe_load((TASKS / name).read_text(encoding="utf-8"))


def not_contains(data: dict) -> set[str]:
    grader = next(item for item in data["graders"] if item["type"] == "text")
    return set(grader["config"].get("not_contains", []))


def program_args(data: dict) -> tuple[str, ...]:
    grader = next(item for item in data["graders"] if item["type"] == "program")
    return tuple(grader["config"]["args"])


class HandoffProjectionTests(unittest.TestCase):
    def test_negatives_exclude_all_non_broad_output_markers_and_skill_name(self) -> None:
        for path in sorted(TASKS.glob("negative-*.yaml")):
            with self.subTest(path=path.name):
                self.assertTrue(NEGATIVE_MARKERS <= not_contains(task(path.name)))
                # The prompt itself asks for risks; do not forbid ordinary English.
                self.assertNotIn("## Risks", not_contains(task(path.name)))

    def test_exact_schema_tasks_use_the_matching_validator_profile(self) -> None:
        self.assertEqual(
            ("evals/handoff-note/check-report.py",),
            program_args(task("positive-edge-9.yaml")),
        )
        self.assertEqual(
            ("evals/handoff-note/check-report.py", "--audit-update"),
            program_args(task("positive-edge-10.yaml")),
        )
        self.assertEqual(
            ("evals/handoff-note/check-report.py", "--audit-only"),
            program_args(task("positive-edge-13.yaml")),
        )

    def test_stop_paths_exclude_every_rendered_profile_marker(self) -> None:
        for name in ("positive-edge-11.yaml", "positive-edge-12.yaml"):
            with self.subTest(task=name):
                self.assertTrue(STOP_MARKERS <= not_contains(task(name)))


if __name__ == "__main__":
    unittest.main()
