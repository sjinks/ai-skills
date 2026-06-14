# auth-claim-contract-review

> Use when: reviewing, designing, implementing, or testing auth/security claim contracts for optional claims, JWT/OIDC/SAML/session/token claims, missing-vs-invalid semantics, issuer-validator-consumer drift, role/scope/permission/tenant/org/account mapping, claim origin, propagation, serialization/cache/session restoration, revocation/freshness, fallback defaults, or confused-deputy risks.

This skill is aimed at auth and security claim contracts where issuer, validator, consumer, missing-vs-invalid, propagation, or restoration behavior affects authorization or session safety.

It helps an assistant:

- map claim source, validators, consumers, and intended missing-vs-invalid semantics before judging
- review optional claims, JWT/OIDC/SAML/session/token claims, role/scope/permission/tenant/org/account mappings, origin markers, fallback defaults, and confused-deputy risks
- check serialization, cache/session restoration, token refresh, revocation, freshness, lifetime, and propagation boundaries for contract drift
- keep sensitive-data boundaries explicit by using redacted or synthetic examples instead of raw tokens, auth headers, secrets, credentials, private keys, customer PII, or private raw data
- return `BLOCK`, `CONCERNS`, or `CLEAN` with findings, checklist status, assumptions, unverified areas, and residual risk

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
