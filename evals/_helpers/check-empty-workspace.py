#!/usr/bin/env python3
"""Validate the shared final-state contract for initially empty task workspaces."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile


def validate(root: Path) -> None:
    """Require an existing real directory with no entries, including hidden ones.

    Applicable only to tasks with no resource files. No symlink is followed;
    transient or outside-workspace changes are not observable in this check.
    """
    if root.is_symlink() or not root.is_dir():
        raise ValueError("workspace directory unavailable or symlinked")
    if next(root.iterdir(), None) is not None:
        raise ValueError("initially empty workspace must remain empty")


def self_test() -> None:
    """Reject files, hidden entries, directories, and live or dangling symlinks.

    Temporary inert fixtures exercise the shared guard without invoking a model.
    """
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        validate(root)
        for kind in ("file", "hidden", "directory", "symlink", "dangling"):
            path = root / (".hidden" if kind == "hidden" else "artifact")
            if kind == "directory":
                path.mkdir()
            elif kind in ("symlink", "dangling"):
                path.symlink_to(root if kind == "symlink" else root / "absent")
            else:
                path.write_text("created or edited content")
            try:
                validate(root)
            except ValueError:
                pass
            else:
                raise AssertionError("accepted workspace entry: " + kind)
            if kind == "directory":
                path.rmdir()
            else:
                path.unlink()
        for invalid in (root / "absent", root / "file", root / "link"):
            if invalid.name == "file":
                invalid.write_text("not a directory")
            elif invalid.name == "link":
                invalid.symlink_to(root)
            try:
                validate(invalid)
            except ValueError:
                pass
            else:
                raise AssertionError("accepted invalid workspace root")
    print("empty-workspace final-state mutations: passed")


def main() -> None:
    """Read Waza's post-execution directory and fail closed if it is unavailable."""
    if sys.argv[1:] == ["--self-test"]:
        self_test()
        return
    root = os.environ.get("WAZA_WORKSPACE_DIR")
    if not root:
        raise SystemExit("WAZA_WORKSPACE_DIR is required")
    try:
        validate(Path(root))
    except (ValueError, OSError) as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
