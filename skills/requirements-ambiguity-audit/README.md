# requirements-ambiguity-audit

> Use when: auditing a draft specification, requirements document, feature request, user story, or product brief for ambiguity: vague quantifiers, undefined terms, TBD placeholders, conflicting requirements, missing actors, or untestable wording, before implementation planning starts.

This skill is aimed at draft specs, requirements documents, feature requests, user stories, and product briefs that need an ambiguity check before planning or implementation.

It helps an assistant:

- sweep eight ambiguity classes: vague quantifiers, undefined terms, missing actors, conflicting requirements, placeholders, unspecified paths, ambiguous references, and untestable wording
- quote the exact text, name its location, and state the plausible readings for every finding
- propose rewrites that preserve intent and turn unknowns into explicit open questions instead of invented values
- respect supplied glossaries and explicitly delegated flexibility instead of flagging them
- assign `blocker`, `should-fix`, or `suggestion` severity and return `BLOCK`, `CONCERNS`, or `CLEAN` verdicts
- emit a deterministic BLOCK template when spec text is missing or unreadable

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
