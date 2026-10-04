#!/usr/bin/env python3
"""Guard unchanged package configuration and forbidden install artifacts."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile

PACKAGE_BYTES = b'{"type":"module"}'
FORBIDDEN = {"node_modules", "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock", "bun.lockb", ".npmrc", ".yarnrc", ".yarnrc.yml", ".yarn", ".pnp.cjs", ".pnp.loader.mjs"}


def validate(root: Path) -> None:
    """Inspect the task workspace without executing or following dependencies.

    The inert fixtures supply exactly one unchanged root package configuration.
    """
    if not root.is_dir():
        raise ValueError("workspace directory unavailable")
    package = root / "package.json"
    if package.is_symlink() or not package.is_file() or package.read_bytes() != PACKAGE_BYTES:
        raise ValueError("package.json must retain supplied bytes")
    for path in root.rglob("*"):
        if path.name in FORBIDDEN or (path.name == "package.json" and path != package):
            raise ValueError(f"unexpected package/install artifact: {path.relative_to(root)}")


def self_test() -> None:
    """Exercise package mutation, deletion and install-artifact variants.

    Simulated workspaces are temporary and no package manager is invoked.
    """
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        package = root / "package.json"
        package.write_bytes(PACKAGE_BYTES)
        (root / "test").mkdir()
        (root / "test/sensor.test.js").write_text("// inert test fixture\n")
        validate(root)
        for content in (b'{"type":"module","dependencies":{"@lab/calibrated-sensor":"*"}}', b'{}', b''):
            package.write_bytes(content)
            try:
                validate(root)
            except ValueError:
                pass
            else:
                raise AssertionError("accepted package mutation")
        package.unlink()
        try:
            validate(root)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted missing package")
        package.write_bytes(PACKAGE_BYTES)
        for name in sorted(FORBIDDEN | {"package.json"}):
            path = root / "test" / name
            path.write_text("artifact")
            try:
                validate(root)
            except ValueError:
                pass
            else:
                raise AssertionError(f"accepted installation artifact: {name}")
            path.unlink()
        validate(root)
    print("package integrity and install-artifact mutations: passed")


def main() -> None:
    """Read the Waza workspace environment, failing closed when absent."""
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
