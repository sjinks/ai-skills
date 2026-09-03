from __future__ import annotations

import importlib.util
import io
from pathlib import Path
import subprocess
import unittest
from unittest import mock
from contextlib import redirect_stderr


SCRIPT = Path(__file__).with_name("check-eval-regexes.py")
SPEC = importlib.util.spec_from_file_location("check_eval_regexes", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CheckEvalRegexesTest(unittest.TestCase):
    def test_command_omits_cases_when_not_supplied(self) -> None:
        result = MODULE.command(Path("evals"), None, "/go")
        self.assertEqual(
            result, ["/go", "run", ".", "--root", str(Path("evals").resolve())]
        )

    def test_command_uses_resolved_root_and_optional_cases(self) -> None:
        result = MODULE.command(Path("evals"), Path("cases.json"), "/go")
        self.assertEqual(result[:4], ["/go", "run", ".", "--root"])
        self.assertEqual(result[4], str(Path("evals").resolve()))
        self.assertEqual(result[5:], ["--cases", str(Path("cases.json").resolve())])

    @mock.patch.object(MODULE.subprocess, "run")
    def test_main_runs_go_module_and_returns_status(self, run: mock.Mock) -> None:
        run.return_value = subprocess.CompletedProcess([], 7)
        status = MODULE.main(["--root", "evals", "--go", "/go"])
        self.assertEqual(status, 7)
        run.assert_called_once_with(
            ["/go", "run", ".", "--root", str(Path("evals").resolve())],
            cwd=SCRIPT.with_name("go-regex-runner"),
            check=False,
        )

    @mock.patch.object(MODULE.subprocess, "run")
    def test_main_forwards_cases(self, run: mock.Mock) -> None:
        run.return_value = subprocess.CompletedProcess([], 0)
        self.assertEqual(
            MODULE.main(["--root", "evals", "--cases", "cases.json", "--go", "/go"]),
            0,
        )
        self.assertEqual(
            run.call_args.args[0][-2:],
            ["--cases", str(Path("cases.json").resolve())],
        )

    @mock.patch.object(MODULE.subprocess, "run", side_effect=PermissionError("denied"))
    def test_main_reports_missing_go(self, run: mock.Mock) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            self.assertEqual(MODULE.main(["--go", "/missing"]), 1)
        self.assertIn("unable to run /missing", stderr.getvalue())
        self.assertIn("denied", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
