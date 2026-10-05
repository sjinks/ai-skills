#!/usr/bin/env python3
"""Execute deterministic profile-recommendation validator mutations."""

import importlib.util
import copy
import re

import pytest
import yaml
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "check_profile_recommendation",
    Path(__file__).with_name("check-profile-recommendation.py"),
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_self_test() -> None:
    MODULE.self_test()


def projection(task: dict) -> None:
    """Bind profile-bullet text assertions to the program-selected profile.

    This checks transport metadata, not semantic patch or evidence adequacy.
    """
    graders = {grader['name']: grader for grader in task['graders']}
    program = graders['profile_recommendation_contract']
    assert program['type'] == 'program', 'profile-mismatch: program grader type'
    assert program['config']['command'] == 'python3', 'profile-mismatch: program command'
    args = program['config']['args']
    assert args[0] == 'evals/cross-model-instruction-authoring/check-profile-recommendation.py', 'profile-mismatch: validator path'
    assert args.count('--expected-profile') == 1, 'profile-mismatch: expected profile binding'
    profile = args[args.index('--expected-profile') + 1]
    assert profile in MODULE.PROFILES, 'profile-mismatch: profile domain'
    patterns = graders['task_completion']['config']['regex_match']
    canonical = '(?m)^- ' + profile + '$'
    assert canonical in patterns, 'profile-mismatch: missing selected profile assertion'
    profile_patterns = [pattern for pattern in patterns if pattern.startswith('(?m)^- ')]
    assert all(re.search(pattern, '- ' + profile) for pattern in profile_patterns), 'profile-mismatch: incompatible profile assertion'


@pytest.mark.parametrize('name', ('positive-edge-9.yaml', 'positive-edge-10.yaml', 'positive-edge-11.yaml'))
def test_task_profile_projection(name: str) -> None:
    """Reject a swapped, omitted or extra incompatible profile assertion.

    Mutations keep all other assertions and the program profile unchanged.
    """
    data = yaml.safe_load((Path(__file__).parent / 'tasks' / name).read_text())
    projection(data)
    for mutation in ('swap', 'omit', 'extra', 'grader-type', 'command', 'checker-path'):
        changed = copy.deepcopy(data)
        patterns = next(grader['config']['regex_match'] for grader in changed['graders'] if grader['name'] == 'task_completion')
        index = patterns.index('(?m)^- coding-agent$')
        if mutation == 'swap':
            patterns[index] = '(?m)^- fast-general$'
        elif mutation == 'omit':
            del patterns[index]
        elif mutation == 'extra':
            patterns.append('(?m)^- fast-general$')
        else:
            grader = next(grader for grader in changed['graders'] if grader['name'] == 'profile_recommendation_contract')
            if mutation == 'grader-type':
                grader['type'] = 'text'
            elif mutation == 'command':
                grader['config']['command'] = 'echo'
            else:
                grader['config']['args'][0] = 'other-checker.py'
        with pytest.raises(AssertionError, match='profile-mismatch:'):
            projection(changed)
