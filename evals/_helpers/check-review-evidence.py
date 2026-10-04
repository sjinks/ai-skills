#!/usr/bin/env python3
"""Run trusted local contrastive probes and report distinct verification claims."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import stat
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
    return subprocess.check_output(["git", "-C", str(root), "--literal-pathspecs", *args], text=True).strip()



def scope_diff(root: Path, tree: str, scope: list[str]) -> str:
    """Compare scoped files without human-facing diff drivers or conversions.

    Both pre-probe identity and post-probe integrity checks use this policy.
    """
    difference = git(root, "diff", "--no-ext-diff", "--no-textconv", tree, "--", *scope)
    if difference:
        return difference
    # Clean filters, EOL normalization and core.fileMode can also conceal changes.
    for path in scope:
        entry = git(root, "ls-tree", "-z", tree, "--", path)
        metadata, name = entry.split("\t", 1)
        mode, kind, object_id = metadata.split()
        require(name == path + "\0" and kind == "blob" and mode in {"100644", "100755"}, "scope tree entry must be one regular file")
        file = root / path
        if file.is_symlink() or not file.is_file():
            return "scoped file is no longer regular: " + path
        content = subprocess.check_output(["git", "-C", str(root), "cat-file", "blob", object_id])
        executable = bool(file.stat().st_mode & stat.S_IXUSR)
        if file.read_bytes() != content or executable != (mode == "100755"):
            return "scoped bytes or executable mode differ: " + path
    return ""


def has_traceback(result: subprocess.CompletedProcess) -> bool:
    """Recognize standard Python and exception-group traceback headers.

    Inspect both streams. This is not authentication of arbitrary validator
    termination: custom exception hooks can suppress traceback evidence.
    """
    pattern = r"(?m)^[ \t+|]*(?:Exception Group )?Traceback \(most recent call last\):"
    return re.search(pattern, result.stdout) is not None or re.search(pattern, result.stderr) is not None


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
    require(scope_diff(root, tree, scope) == "", "working scope differs from tree")
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
        require(not has_traceback(positive), "conforming example emitted a Python traceback: " + rule["id"])
        require(positive.returncode == 0, "conforming example rejected: " + rule["id"])
        negative = subprocess.run([sys.executable, *command[1:]], cwd=root, input=rule["reject"], text=True, capture_output=True, timeout=30)
        require(not has_traceback(negative), "counterexample emitted a Python traceback: " + rule["id"])
        require(negative.returncode == 1 and re.search(rule["rejection"], negative.stderr) is not None, "counterexample did not produce its expected rejection: " + rule["id"])
    require(scope_diff(root, tree, scope) == "", "probe changed scoped files")
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
