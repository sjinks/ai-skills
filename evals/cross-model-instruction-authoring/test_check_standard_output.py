#!/usr/bin/env python3
"""Execute deterministic standard-output validator mutations."""

import importlib.util
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "check_standard_output",
    Path(__file__).with_name("check-standard-output.py"),
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_self_test() -> None:
    MODULE.self_test()
