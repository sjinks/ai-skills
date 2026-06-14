# web-app-security-review

> >-

This skill is aimed at web application security reviews where the assistant needs to evaluate code, pull requests, designs, vulnerability reports, or fix validation with a defensive and evidence-based workflow.

For the expanded checklist and evidence standards, see [references/WORKFLOW.md](references/WORKFLOW.md).

It helps an assistant:

- set safe-use boundaries for static review, explicitly authorized active testing, and untrusted external report content
- map trust boundaries, actors, tenants, entry points, sensitive data, and downstream systems before judging
- review high-value areas such as broken access control / IDOR, auth and sessions, OAuth / OIDC / JWT, XSS, CSRF, injection, XXE, SSRF, CORS, browser headers, file uploads, GraphQL, WebSockets, webhooks, secrets, dependencies, cloud IAM, containers, ReDoS, and DoS
- use concrete grep and review heuristics without relying on weaponized payload lists
- classify findings with severity, confidence, evidence standards, false-positive discipline, and regression-test expectations
- recognize narrow outbound-fetch and filesystem path construction as separate review concerns when those specialized contracts apply

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/`](references/) — extended workflow and reference material.
