#!/usr/bin/env python3
"""Run the deterministic Go validator for decoded task regexes."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
from typing import Optional


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def command(root: Path, cases: Optional[Path], go: str) -> list[str]:
    runner = Path(__file__).resolve().with_name("go-regex-runner")
    result = [go, "run", ".", "--root", str(root.resolve())]
    if cases is not None:
        result.extend(("--cases", str(cases.resolve())))
    return result


def parse_args(arguments: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Decode task YAML and compile every text-grader regex with Go regexp."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=repository_root() / "evals",
        help="evals root containing */tasks/*.yaml",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        help="optional JSON file containing contrastive regex cases",
    )
    parser.add_argument("--go", default="go", help="Go executable")
    return parser.parse_args(arguments)


def main(arguments: Optional[list[str]] = None) -> int:
    options = parse_args(arguments)
    runner = Path(__file__).resolve().with_name("go-regex-runner")
    try:
        completed = subprocess.run(
            command(options.root, options.cases, options.go),
            cwd=runner,
            check=False,
        )
    except FileNotFoundError as error:
        print(f"unable to run {options.go}: {error}", file=sys.stderr)
        return 1
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
