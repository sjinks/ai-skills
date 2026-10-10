# iteration-retrospective

> Use when: reflecting on multi-attempt work to turn evidence from implementations, debugging, investigations, or review/fix chains into prevention decisions and an evidence-backed reusable-skill recommendation when warranted.

This skill reconstructs what was attempted, compares what changed between related attempts, and turns supported lessons into decisions for the next attempt. It distinguishes observed improvements from causal attribution when several factors changed. It avoids generic self-critique and does not recommend a new skill when a validator, local instruction, or refactor is the smaller remedy.

Requests about multiple attempts or an explicitly abandoned approach reach the missing-evidence path even when evidence is unavailable. A single nonabandoned attempt and generic reflection remain excluded.

Environment-related failures are checked against existing safeguards, navigation, instruction usefulness, tool economy, and information access before prevention is selected. These lenses preserve the existing mechanism domains and cost ordering; missing checks alone do not establish a defect.

The report defines attempt statuses, evidence-bound cause grouping, skill candidates derived from selected prevention, and `CLEAN` / `CONCERNS` / `BLOCK` verdicts. Nonblocked failed or partially successful attempts require cause learnings, and `CONCERNS` requires next checks. Missing decisive comparison costs leave the affected prevention unselected while preserving other selections.

Nonblocked learning rows link to attempt IDs through `Attempts`; prevention rows link to learning IDs through `Learnings`. Every failed or partly-worked attempt is covered. Next checks identify learning IDs for unresolved causes or prevention decisions. Blocked reports retain their existing missing-evidence format.

Cost comparisons use the same current workflow and recurrence scenario. New dependencies count distinct directly required packages, tools, and services; new workflow steps count recurring operator actions. One-time implementation work, transitive dependencies, organizational prerequisites, and automatic actions are excluded from these counts. The assessment records the comparison evidence, and unavailable decisive counts remain unresolved.

Supported lessons state a condition and an action. Evidenced successes are inspected for practices worth repeating without assuming those practices caused success. Prevention candidates explain which failure step they would detect, prevent, or contain before costs are compared. Next checks identify uncertainty, evidence to obtain, and decisions for different results; they remain proposals rather than authorization to execute.

Default report markers use the `Retrospective` prefix to distinguish them from ordinary status and review labels. Caller-selected labels remain supported for nonblocked reports. Labels containing C0/C1 controls (U+0000–U+001F and U+007F–U+009F) or Unicode line separators (U+2028/U+2029) are invalid. Invalid nonblocked labels produce a fixed two-line label clarification instead of a report; blocked reports ignore all replacements.

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/environment-prevention.md`](references/environment-prevention.md) — evidence-gated environment lenses and mapping to existing prevention mechanisms.
- [`references/report-format.md`](references/report-format.md) — workflow, ordered status and candidate rules, row grammar, label replacement, and blocked reports.

- [`references/worked-examples.md`](references/worked-examples.md) — complete illustrative reports for failure followed by success, abandonment with uncertain cause, and mixed selected/unresolved prevention.
