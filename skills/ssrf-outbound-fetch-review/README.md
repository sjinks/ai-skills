# ssrf-outbound-fetch-review

> Use when: performing code review, pull request review, security review, designing, implementing, or testing SSRF fixes, outbound HTTP requests, outbound fetch helpers, user-supplied URLs, URL validation, DNS lookup, private IP blocking, proxies, redirects, archive/plugin downloads, crawlers, importers, webhook fetches, HTTP client wrappers, or egress policy changes.

This skill is aimed at code paths that accept or derive URLs from untrusted or semi-trusted input and then perform outbound requests, especially when policy, parsing, DNS, proxy, transport, redirect, and trusted private-target opt-in behavior all need to line up.

It helps an assistant:

- define explicit egress and port policy contracts before implementation
- review URL parsing, normalization, IP classification, and DNS handling, including connection-time lookup and rebinding risks
- reason about proxy behavior and transport semantics such as SNI, Host, and certificate verification
- assess redirect safety, sensitive-header handling, and trusted private-target opt-ins
- build realistic adversarial tests for SSRF-related edge cases
- support local output depth (`quick`, `standard`, or `exhaustive`), while `quick` still reports missing context, blockers, high-risk concerns, and target-specific findings
- return findings in a consistent, review-ready format

The skill covers both implementation concerns and review discipline, including boundaries, required input context, a definition of done, and a structured output contract.

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/`](references/) — extended workflow and reference material.
