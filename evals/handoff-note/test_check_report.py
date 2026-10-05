#!/usr/bin/env python3
"""Static projection checks for handoff-note's exact-schema eval profiles."""

from __future__ import annotations

import unittest
import copy
import importlib.util
import re
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
    "## Risks and Constraints",
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
DISTINCTIVE_CUSTOM_PROFILE_START_MARKERS = {
    "# Continuation Packet:",
    "# Review:",
    "# Continuation:",
}
STOP_MARKERS = NEGATIVE_MARKERS | {"## Risks"}


def task(name: str) -> dict:
    return yaml.safe_load((TASKS / name).read_text(encoding="utf-8"))


def not_contains(data: dict) -> set[str]:
    grader = next(item for item in data["graders"] if item["type"] == "text")
    return set(grader["config"].get("not_contains", []))


def program_args(data: dict) -> tuple[str, ...]:
    """Read the canonical schema validator's arguments after binding its role.

    A different grader type or executable cannot enforce this report grammar.
    """
    grader = next(item for item in data["graders"] if item["name"] == "schema_contract")
    assert grader['type'] == 'program', 'profile-mismatch: schema grader type'
    assert grader['config']['command'] == 'python3', 'profile-mismatch: schema command'
    return tuple(grader["config"]["args"])


class HandoffProjectionTests(unittest.TestCase):
    def test_text_assertions_match_exact_profile_headings(self) -> None:
        """Check task header assertions against the program-selected profile.

        A swapped assertion must reject without changing the program binding.
        """
        spec = importlib.util.spec_from_file_location('handoff_report', ROOT / 'check-report.py')
        report = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(report)
        profiles = {'positive-edge-9.yaml': report.PACKET_HEADINGS,
                    'positive-edge-10.yaml': report.AUDIT_UPDATE_HEADINGS,
                    'positive-edge-13.yaml': report.AUDIT_HEADINGS}
        for name, headings in profiles.items():
            with self.subTest(task=name):
                data = task(name)
                patterns = next(item['config']['regex_match'] for item in data['graders'] if item['type'] == 'text')
                envelope = '\n'.join(headings)
                self.assertTrue(all(re.search(pattern, envelope) for pattern in patterns), 'profile-mismatch: ' + name)
                self.assertTrue(all(any(heading in pattern for pattern in patterns) for heading in headings), 'missing profile heading assertion')
                for heading in headings:
                    index = next(index for index, pattern in enumerate(patterns) if heading in pattern)
                    wrong = list(patterns)
                    wrong[index] = wrong[index].replace(heading, '# Contradictory Profile:', 1)
                    self.assertFalse(all(re.search(token, envelope) for token in wrong), 'accepted profile heading mismatch')

    def test_negatives_exclude_all_non_broad_output_markers_and_skill_name(self) -> None:
        for path in sorted(TASKS.glob("negative-*.yaml")):
            with self.subTest(path=path.name):
                self.assertTrue(NEGATIVE_MARKERS <= not_contains(task(path.name)))
                self.assertTrue(
                    DISTINCTIVE_CUSTOM_PROFILE_START_MARKERS <= not_contains(task(path.name))
                )
                # The prompt itself asks for risks; do not forbid ordinary English.
                self.assertNotIn("## Risks", not_contains(task(path.name)))
                for marker in (
                    "## Objective", "## State", "## Evidence", "## Actions", "## Unknowns",
                    "## Findings", "## Corrections", "## Ready",
                ):
                    self.assertNotIn(marker, not_contains(task(path.name)))

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

    def test_schema_binding_mutations(self) -> None:
        """Reject an isolated grader-type, command or validator-path change.

        The selected profile flags and all text assertions stay unchanged.
        """
        for name in ('positive-edge-9.yaml', 'positive-edge-10.yaml', 'positive-edge-13.yaml'):
            data = task(name)
            expected = program_args(data)
            for condition in ('type', 'command', 'path'):
                changed = copy.deepcopy(data)
                grader = next(item for item in changed['graders'] if item['name'] == 'schema_contract')
                if condition == 'type':
                    grader['type'] = 'text'
                elif condition == 'command':
                    grader['config']['command'] = 'echo'
                else:
                    grader['config']['args'][0] = 'other-checker.py'
                with self.assertRaises(AssertionError):
                    self.assertEqual(program_args(changed), expected, 'profile-mismatch: schema path')

    def test_stop_paths_exclude_every_rendered_profile_marker(self) -> None:
        for name in ("positive-edge-11.yaml", "positive-edge-12.yaml"):
            with self.subTest(task=name):
                self.assertTrue(STOP_MARKERS <= not_contains(task(name)))


if __name__ == "__main__":
    unittest.main()
