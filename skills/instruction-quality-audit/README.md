# instruction-quality-audit

> Use when identifying exact defects in AI instruction artifacts.

This skill performs a high-confidence diagnostic audit for contradictions,
precedence gaps, ambiguity, authority and side-effect conflicts, incomplete
decision rules, missing failure behavior, harmful cognitive burden or
duplication, output-contract defects, and explicitly requested custom
diagnostics.

It does not provide holistic readiness ratings or model-by-model
certification; use `agent-skill-audit` for that.

## Files

- [`SKILL.md`](SKILL.md) — the full instruction-quality audit definition.
- [`references/diagnostic-rules.md`](references/diagnostic-rules.md) — finding types, false-positive checks, and custom-diagnostic trust rules.
- [`references/package-analysis.md`](references/package-analysis.md) — package/path load-graph rules and cross-file interaction guidance.
- [`references/report-contract.md`](references/report-contract.md) — the required diagnostic report markers, blocked behavior, and no-findings contract.
