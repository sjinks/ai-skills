# commit-message-quality

> Prepare or assess commit messages that preserve motivation, decisions and behavioral consequences for humans and LLMs reading Git history without PR access.

Standalone usefulness comes before formatting. Explain the problem or trigger, its impact and the resulting behavior. Preserve consequential choices and their evidenced reasons, constraints, invariants and compatibility effects. Links supplement that explanation. Stable domain terms and exact identifiers help future readers find and interpret decisions; vague activity summaries and file inventories do not replace outcomes.

Require a body when the subject omits needed context or selected rules require one. Otherwise a self-contained subject is enough, regardless of diff size. Omitted unnecessary Body now uses `n/a (not needed)` rather than `n/a (trivial)`; omission status still distinguishes intentional/already absent content from correction by deletion. Routine check inventories, counts and process history are omitted by default. Retain a regression scenario, observation or reproduction detail when it explains a defect, decision or boundary; distinguish intended coverage from executed results.

Individual messages describe their own changes. Squash/combined messages describe the final surviving change, retaining still-relevant rationale without stale approaches or concatenated fixup chronology. Missing required rationale or unresolved final scope needs author input. Optional unknown alternatives, deliberation and runtime-success claims are not invented.

The skill activates for message preparation within broader implementation, PR or history work, but never executes Git operations or reviews code correctness. Caller rules precede readable repository rules, consistent history and formatting defaults. Conventional-by-default grammar, subject-length rules, breaking-change disclosures, real trailers and sourced cleanup advice remain in effect. The returned message covers the supplied scope unless the caller explicitly selects a prospective split.

Draft/repair corrects text; validate preserves safe text and reports defects. Claims need evidence; the assessed message does not prove itself. Missing required facts/rules take status precedence over remaining violations and passing repairs. Reports retain the established labels, conventional/plain modes, Subject/Body/Footers checks, and CLEAN/CONCERNS/BLOCK verdict mapping. Drafting/correction still produces CONCERNS under this package's existing mapping; this update changes content criteria and the Body omission reason, not that verdict policy.

Sensitive content is excluded in every mode. An excluded-source Input/error requires CONCERNS without inventing a failing message part or fourth check. Unusable required input produces reduced BLOCK. Non-violating cleanup advice is informational and does not alone require author input or prevent CLEAN.

## Files

- [`SKILL.md`](SKILL.md) — routing, standalone content criteria, grammar defaults, status/verdict rules and report contract.
- [`references/history-and-rationale.md`](references/history-and-rationale.md) — motivation, decisions, body necessity, squash scope, illustrations and static regression cases.
- [`references/types-and-examples.md`](references/types-and-examples.md) — subject grammar, type/removal policy, evidence/omission examples and a complete validation report.
- [`references/git-cleanup.md`](references/git-cleanup.md) — comment-like heading preservation and conditional cleanup advice.
