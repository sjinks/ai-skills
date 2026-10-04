#!/usr/bin/env python3
"""Run trusted local contrastive probes and report distinct verification claims."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

DIMENSIONS = {"defaults", "optional-inputs", "multiplicity", "side-effects", "payload-boundary", "outcomes"}
CLAIMS = {"contract", "workspace", "execution", "model-behavior"}


def require(condition: bool, message: str) -> None:
    """Fail with a named gate condition rather than silently omitting evidence."""
    if not condition:
        raise ValueError(message)


def populated(value: object) -> bool:
    """Accept only nonempty strings for human-readable decisions and evidence."""
    return isinstance(value, str) and bool(value.strip())


def git(root: Path, *args: str) -> str:
    """Read repository identity and tracked scope without executing a shell."""
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def check(manifest: dict, root: Path) -> dict:
    """Verify the immutable scope, then run positive and single-change negative probes.

    Commands are trusted repository Python validators, explicitly scoped and
    inspected by the author. This gate cannot prove a declared mutation is the
    only semantic difference or that a validator has no external side effects.
    """
    tree = manifest.get("tree")
    require(isinstance(tree, str) and re.fullmatch(r"[0-9a-f]{40}", tree) is not None, "tree must be a full immutable object ID")
    require(git(root, "cat-file", "-t", tree) == "tree", "tree ID must identify a tree")
    scope = manifest.get("scope")
    require(isinstance(scope, list) and bool(scope), "scope is required")
    for path in scope:
        require(populated(path) and not Path(path).is_absolute() and ".." not in Path(path).parts and not path.startswith("-"), "scope paths must be relative")
        require((root / path).is_file() and not (root / path).is_symlink(), "scope must list existing regular files")
        require(git(root, "ls-tree", tree, "--", path) != "", "scope file absent from tree")
    require(git(root, "diff", tree, "--", *scope) == "", "working scope differs from tree")
    require(git(root, "ls-files", "--others", "--exclude-standard", "--", *scope) == "", "untracked scope is not bound to tree")
    rules = manifest.get("rules")
    require(isinstance(rules, list) and bool(rules), "rules are required")
    ids = set()
    covered = set()
    for rule in rules:
        require(isinstance(rule, dict) and populated(rule.get("id")) and rule["id"] not in ids, "rule IDs must be unique")
        ids.add(rule["id"])
        require(populated(rule.get("source")) and rule["source"] in scope, "rule source must be scoped")
        require(populated(rule.get("mutation")), "name the single changed condition")
        dimensions = rule.get("dimensions")
        require(isinstance(dimensions, list) and bool(dimensions) and all(d in DIMENSIONS for d in dimensions), "rule dimensions must be known")
        covered.update(dimensions)
        command = rule.get("command")
        require(isinstance(command, list) and len(command) >= 2 and all(isinstance(a, str) for a in command), "command must be an argv list")
        require(command[0] == "python3" and command[1] in scope and command[1].endswith(".py"), "command must name a scoped Python validator")
        require(isinstance(rule.get("accept"), str) and isinstance(rule.get("reject"), str) and rule["accept"] != rule["reject"], "distinct accept and reject inputs required")
        require(populated(rule.get("rejection")), "expected rejection diagnostic required")
        re.compile(rule["rejection"])
    exclusions = manifest.get("not-applicable")
    require(isinstance(exclusions, dict) and all(d in DIMENSIONS and populated(reason) for d, reason in exclusions.items()), "dimension exclusions need reasons")
    require(covered.isdisjoint(exclusions) and covered | set(exclusions) == DIMENSIONS, "every dimension must be covered or explicitly inapplicable")
    claims = manifest.get("claims")
    require(isinstance(claims, dict) and set(claims) == CLAIMS, "four separate evidence claims required")
    for name, claim in claims.items():
        require(isinstance(claim, dict) and claim.get("status") in {"verified", "unverified", "not-applicable"} and populated(claim.get("evidence")), "claim status and evidence required: " + name)
    review = manifest.get("independent-review")
    require(isinstance(review, dict) and review.get("status") in {"completed", "unavailable"} and populated(review.get("evidence")), "independent review result or constraint required")
    if review["status"] == "completed":
        require(review.get("tree") == tree and populated(review.get("reviewer")), "independent reviewer must be bound to this tree")
    for rule in rules:
        command = rule["command"]
        positive = subprocess.run([sys.executable, *command[1:]], cwd=root, input=rule["accept"], text=True, capture_output=True, timeout=30)
        require(positive.returncode == 0, "conforming example rejected: " + rule["id"])
        negative = subprocess.run([sys.executable, *command[1:]], cwd=root, input=rule["reject"], text=True, capture_output=True, timeout=30)
        require(negative.returncode == 1 and re.search(rule["rejection"], negative.stderr) is not None, "counterexample did not produce its expected rejection: " + rule["id"])
    require(git(root, "diff", tree, "--", *scope) == "", "probe changed scoped files")
    return {"tree": tree, "contrastive-checks": "passed", "claims": claims, "independent-review": review}


def main() -> None:
    """Read an author-reviewed manifest and fail closed on malformed evidence."""
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text())
        require(isinstance(manifest, dict), "manifest must be an object")
        result = check(manifest, args.repo.resolve())
    except (ValueError, KeyError, TypeError, OSError, re.error, subprocess.SubprocessError) as error:
        raise SystemExit(str(error)) from error
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
