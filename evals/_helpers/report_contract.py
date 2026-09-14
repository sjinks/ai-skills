"""Canonical, executable grammar primitives for structured skill reports.

Keep the field order, enum domains, and report termination in one small
module.  Suite-specific preflights should instantiate a contract here instead
of maintaining divergent regex-shaped copies of the same envelope.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional


class ContractError(ValueError):
    """Raised when text does not represent exactly one contract report."""


@dataclass(frozen=True)
class Finding:
    """One normal-profile finding in the canonical shell report grammar."""

    title: str
    severity: str
    classification: str
    evidence: str
    rule: str
    risk: str
    portable_fix: str
    verification: str


@dataclass(frozen=True)
class ReportContract:
    """A fixed-order report with normal and insufficient-context profiles."""

    name: str
    verdict_label: str
    verdicts: frozenset[str]
    target_label: str
    interpreter_label: str
    findings_label: str
    checklist_label: str
    checklist_items: tuple[str, ...]
    checklist_values: frozenset[str]
    residual_label: str

    @property
    def normal_markers(self) -> tuple[str, ...]:
        return (
            f"{self.verdict_label}:",
            f"{self.target_label}:",
            f"{self.interpreter_label}:",
            f"{self.findings_label}:",
            f"{self.checklist_label}:",
            f"{self.residual_label}:",
        )

    @property
    def reduced_markers(self) -> tuple[str, ...]:
        return (
            f"{self.verdict_label}:",
            f"{self.target_label}:",
            f"{self.findings_label}:",
        )

    def render_normal(
        self,
        *,
        verdict: str,
        target: str,
        interpreter: str,
        findings: tuple[Finding, ...],
        checklist: Mapping[str, str],
        residual_risk: str,
    ) -> str:
        """Serialize a normal report and reject unrepresentable input."""

        if set(checklist) != set(self.checklist_items):
            raise ContractError(f"{self.name}: checklist keys must match the canonical list")
        lines: list[str] = [
            f"{self.verdict_label}: {verdict}",
            f"{self.target_label}: {target}",
            f"{self.interpreter_label}: {interpreter}",
            "",
        ]
        if findings:
            lines.append(f"{self.findings_label}:")
            for number, finding in enumerate(findings, start=1):
                lines.extend(
                    (
                        f"{number}. {finding.title}",
                        f"  Severity: {finding.severity}",
                        f"  Classification: {finding.classification}",
                        f"  Evidence: {finding.evidence}",
                        f"  Rule: {finding.rule}",
                        f"  Risk: {finding.risk}",
                        f"  Portable fix: {finding.portable_fix}",
                        f"  Verification: {finding.verification}",
                    )
                )
        else:
            lines.append(f"{self.findings_label}: None")
        lines.extend(
            (
                "",
                f"{self.checklist_label}:",
                *(f"- {item}: {checklist[item]}" for item in self.checklist_items),
                "",
                f"{self.residual_label}: {residual_risk}",
            )
        )
        output = "\n".join(lines)
        self.validate(output)
        return output

    def render_insufficient_context(self, *, target: str) -> str:
        """Serialize the reduced missing-input report profile."""

        output = "\n".join(
            (
                f"{self.verdict_label}: BLOCK",
                f"{self.target_label}: {target}",
                "",
                f"{self.findings_label}:",
                "1. Missing context",
                "  Severity: LOW",
                "  Classification: Open question",
                "  Evidence: No script or commands supplied",
                "  Rule: verification",
                "  Risk: A portability conclusion would be speculative",
                "  Portable fix: Provide the script or commands",
                "  Verification: N/A",
            )
        )
        self.validate(output)
        return output

    def validate(self, output: str) -> str:
        """Accept exactly one canonical profile; return its profile name."""

        if not isinstance(output, str) or "\x00" in output or "\r" in output:
            raise ContractError(f"{self.name}: report must be LF-only text without NUL")
        if output.endswith("\n"):
            output = output[:-1]
        lines = output.split("\n")
        if len(lines) >= 3 and lines[2].startswith(f"{self.interpreter_label}: "):
            self._validate_normal(lines)
            return "normal"
        self._validate_insufficient_context(lines)
        return "insufficient-context"

    def _scalar(self, line: str, label: str) -> str:
        prefix = f"{label}: "
        if not line.startswith(prefix) or not line[len(prefix) :].strip():
            raise ContractError(f"{self.name}: expected nonempty {label} field")
        return line[len(prefix) :]

    def _validate_verdict(self, line: str, expected: Optional[str] = None) -> str:
        verdict = self._scalar(line, self.verdict_label)
        if verdict not in self.verdicts or (expected is not None and verdict != expected):
            raise ContractError(f"{self.name}: invalid verdict")
        return verdict

    def _validate_normal(self, lines: list[str]) -> None:
        verdict = self._validate_verdict(lines[0])
        self._scalar(lines[1], self.target_label)
        self._scalar(lines[2], self.interpreter_label)
        if lines[3] != "":
            raise ContractError(f"{self.name}: normal report requires the canonical section separator")
        index = self._validate_normal_findings(lines, 4, verdict)
        if index >= len(lines) or lines[index] != "" or index + 1 >= len(lines) or lines[index + 1] != f"{self.checklist_label}:":
            raise ContractError(f"{self.name}: checklist is missing or out of order")
        index += 2
        for item in self.checklist_items:
            if index >= len(lines):
                raise ContractError(f"{self.name}: normal report has a truncated checklist")
            value = self._scalar(lines[index], f"- {item}")
            if value not in self.checklist_values:
                raise ContractError(f"{self.name}: invalid checklist value for {item}")
            index += 1
        if index + 2 != len(lines) or lines[index] != "":
            raise ContractError(f"{self.name}: residual-risk separator is missing")
        self._scalar(lines[index + 1], self.residual_label)

    def _validate_normal_findings(self, lines: list[str], index: int, verdict: str) -> int:
        if index >= len(lines):
            raise ContractError(f"{self.name}: normal report has no findings field")
        if lines[index] == f"{self.findings_label}: None":
            if verdict != "CLEAN":
                raise ContractError(f"{self.name}: only CLEAN may use Findings: None")
            return index + 1
        if lines[index] != f"{self.findings_label}:":
            raise ContractError(f"{self.name}: findings are missing or out of order")
        if verdict == "CLEAN":
            raise ContractError(f"{self.name}: CLEAN must use Findings: None")
        number = 1
        index += 1
        while index < len(lines) and lines[index] != "":
            if lines[index] != f"{number}. " and not lines[index].startswith(f"{number}. "):
                raise ContractError(f"{self.name}: findings must be consecutively numbered")
            if not lines[index][len(f"{number}. ") :].strip():
                raise ContractError(f"{self.name}: finding title must be nonempty")
            index += 1
            expected = (
                ("Severity", ("CRITICAL", "HIGH", "MEDIUM", "LOW")),
                ("Classification", ("Confirmed issue", "Likely risk", "Open question", "Accepted tradeoff")),
                ("Evidence", None),
                ("Rule", ("interpreter-shebang", "bashisms", "utilities-flags", "output-behavior", "verification")),
                ("Risk", None),
                ("Portable fix", None),
                ("Verification", None),
            )
            for label, values in expected:
                if index >= len(lines):
                    raise ContractError(f"{self.name}: finding {number} is truncated")
                value = self._scalar(lines[index], f"  {label}")
                if values is not None and value not in values:
                    raise ContractError(f"{self.name}: invalid {label} in finding {number}")
                index += 1
            number += 1
        if number == 1:
            raise ContractError(f"{self.name}: non-CLEAN reports require a finding")
        return index

    def _validate_insufficient_context(self, lines: list[str]) -> None:
        if len(lines) != 12:
            raise ContractError(f"{self.name}: insufficient-context report has trailing or missing fields")
        self._validate_verdict(lines[0], "BLOCK")
        self._scalar(lines[1], self.target_label)
        if lines[2] != "" or lines[3] != f"{self.findings_label}:":
            raise ContractError(f"{self.name}: insufficient-context fields are out of order")
        if not lines[4].startswith("1. ") or not lines[4][3:].strip():
            raise ContractError(f"{self.name}: insufficient-context requires one numbered finding")
        expected = (
            ("Severity", "LOW"),
            ("Classification", "Open question"),
            ("Evidence", None),
            ("Rule", None),
            ("Risk", None),
            ("Portable fix", None),
            ("Verification", "N/A"),
        )
        for line, (label, required) in zip(lines[5:], expected):
            value = self._scalar(line, f"  {label}")
            if required is not None and value != required:
                raise ContractError(f"{self.name}: invalid insufficient-context {label}")


SHELL_PORTABILITY_CONTRACT = ReportContract(
    name="shell-portability",
    verdict_label="Verdict",
    verdicts=frozenset(("BLOCK", "CONCERNS", "CLEAN")),
    target_label="Target",
    interpreter_label="Interpreter",
    findings_label="Findings",
    checklist_label="Checklist status",
    checklist_items=(
        "Interpreter and shebang",
        "Bashisms",
        "Utilities and flags",
        "Output and behavior",
        "Verification",
    ),
    checklist_values=frozenset(("covered", "missing", "n/a")),
    residual_label="Residual risk",
)
