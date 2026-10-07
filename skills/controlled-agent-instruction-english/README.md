# controlled-agent-instruction-english

> Write, rewrite, and audit model-facing operational prose with explicit modality, scope, conditions, precedence, and failure behavior.

This skill applies a controlled-English approach to agent instructions. It rewrites prose quoted as the editing target while preserving embedded literal quotations and technical literals and treats sentence-length thresholds as advisory. It does not claim ASD-STE100 compliance or measured cross-model reliability.

Author mode returns a complete instruction artifact. For a combined audit-and-rewrite request, it also preserves meaningful findings from the original text. Audit mode reports only meaningful errors and warnings. Blocked mode names missing input in either workflow, or unresolved intended behavior required for authoring. Audit mode retains ambiguity findings with clarification questions. The report uses `CAIE mode:`, `CAIE artifact:`, `CAIE findings:`, and `CAIE status:`.

The report contract is defined by the skill and its references. The intended compatibility floor is the `fast-general` profile; no model-specific patches or runtime adapters are required.

## Files

- [`SKILL.md`](SKILL.md) — compact entry point, triggers, reference loading, and report labels.
- [`references/operational-guide.md`](references/operational-guide.md) — scope, workflows, final consistency check, severity, and complete report contract.
- [`references/language-rules.md`](references/language-rules.md) — the full T/N/S/R/C/P/D/E rule catalog.
- [`references/examples.md`](references/examples.md) — non-normative examples of operational corrections.
