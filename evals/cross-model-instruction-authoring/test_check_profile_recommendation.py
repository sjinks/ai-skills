#!/usr/bin/env python3
"""Execute deterministic profile-recommendation validator mutations."""

import importlib.util
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
