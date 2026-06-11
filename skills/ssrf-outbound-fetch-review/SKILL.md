---
name: ssrf-outbound-fetch-review
description: "Use when: performing code review, pull request review, security review, designing, implementing, or testing SSRF fixes, outbound HTTP requests, outbound fetch helpers, user-supplied URLs, URL validation, DNS lookup, private IP blocking, proxies, redirects, archive/plugin downloads, crawlers, importers, webhook fetches, HTTP client wrappers, or egress policy changes."
argument-hint: "Describe the outbound fetch change, affected files, threat model, runtime/client library, and tests or PR context."
user-invocable: true
---

# SSRF Outbound Fetch Review

Use this skill when code accepts, constructs, validates, follows, fetches, proxies, downloads, imports, crawls, or redirects to URLs that can be influenced by users, tenants, remote APIs, plugin/package metadata, webhooks, or other external data.

The goal is to turn SSRF work from reactive review comments into an upfront egress policy, implementation checklist, and adversarial test matrix.

## Boundaries

- Review and test only systems you are authorized to inspect.
- Prefer local unit tests, fixtures, fake resolvers, and mocked HTTP clients.
- Do not scan, probe, or attack live internal networks or third-party services.
- Do not treat this skill as a replacement for project-specific product, networking, or security policy decisions.
- Clearly separate confirmed vulnerabilities from assumptions, defense-in-depth suggestions, and compatibility tradeoffs.

## Trigger Conditions

Use this skill if any of these are true:

- A URL comes from a user, tenant, webhook, external API, package registry, plugin metadata, archive metadata, AI/tool output, or database state that may have originated externally.
- Code calls `fetch`, `undici`, `axios`, `got`, `http.request`, `https.request`, cURL, wget, browser automation navigation, object-store import, archive download, proxy logic, crawler logic, or package/plugin download logic.
- Code validates URL schemes, hostnames, IP addresses, DNS answers, redirects, proxy targets, or egress allowlists/denylists.
- Code changes redirect behavior, sensitive header forwarding, timeout handling, abort signals, response-body cleanup, response-size limits, or HTTP client dispatchers/agents.
- Tests use an HTTP mock client, fake dispatcher, or browser mock while URL validation depends on DNS or socket behavior.

## Required Input Context

Collect or ask for the narrowest useful context before reviewing or implementing:

- Affected files and functions.
- Runtime and HTTP client library, including major versions when relevant.
- URL source and actor that can influence it.
- Allowed schemes and allowed or disallowed host policy.
- Allowed ports and whether non-default HTTP(S) ports are legitimate.
- Whether private/internal targets are ever legitimate.
- Proxy behavior, ambient proxy environment variables, local development paths, or service-to-service callsites.
- Redirect behavior expected by callers.
- Sensitive headers that may be present.
- Current tests and what they mock versus what they exercise for real.

## Egress Policy Contract

Before implementation, define the contract in concrete terms:

- **Source boundary:** Which inputs can influence the target URL?
- **Scheme policy:** Which schemes are allowed? Usually server-side downloads should reject anything except explicit `https` unless the project has a documented reason.
- **Host policy:** Is there a host allowlist, a public-internet-only policy, or a hybrid? Record compatibility reasons for allowing broad public `https` hosts.
- **Port policy:** Are only default ports allowed, are custom ports permitted, and are dangerous or internal-service ports blocked or allowlisted?
- **Private-network policy:** Which private, loopback, link-local, metadata, multicast, reserved, documentation, unspecified, and broadcast ranges are blocked?
- **DNS policy:** Are hostnames resolved before the request? Are all returned A/AAAA records checked? What happens on empty, failed, mixed public/private, or CNAME-chain answers?
- **Connection-time policy:** Is the actual connect-time lookup guarded so DNS rebinding cannot bypass preflight checks? Can connection pooling, agents, or dispatchers reuse a connection across policy contexts?
- **Proxy policy:** Are ambient proxies such as `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`, and lowercase variants ignored, honored, or explicitly configured? If a proxy performs DNS resolution, how is proxy-side resolution constrained?
- **Redirect policy:** Who owns redirect following: the wrapper or the lower-level HTTP client? Are checks repeated for every hop?
- **Header policy:** Which headers are allowed on initial outbound requests, and which headers are stripped on cross-origin or cross-scheme redirects?
- **Trusted private-target opt-in policy:** Are private targets denied by default and allowed only through explicit trusted callsite options? Who is allowed to set that option?
- **Response policy:** Are timeout, response-size, content-type, decompression behavior, and body cleanup handled where relevant? If downloaded content is later extracted, treat extraction paths, links, file count, decompressed size, and compression ratio as separate review concerns outside this SSRF checklist.
- **Defense-in-depth policy:** Which infrastructure-level egress controls, metadata-service protections, firewall rules, or service-mesh policies exist, and are they only compensating controls or an explicitly accepted primary control?
- **Testability policy:** How can tests fake DNS and HTTP separately without hiding real validation behavior?

## Output Depth

Default to `standard`. `quick` still reports missing required context, blockers, unmitigated HIGH/CRITICAL findings, and target-specific concerns; it only omits non-applicable checklist expansion. `standard` covers the applicable egress checklist with concise evidence. `exhaustive` enumerates the full checklist and adversarial matrix only when asked or when the risk surface warrants it. If the user asks for `quick` or `exhaustive`, name the selected depth in the report.

## Implementation Checklist

### URL Parsing And Normalization

- Parse URLs with a standard URL parser before security decisions.
- Ensure the URL parser used for validation matches, or is stricter than, the parser and normalization behavior used by the HTTP client. Do not validate one representation and request another.
- Require a non-empty hostname for network URLs.
- Require explicit protocols; do not accept protocol-relative or parser-reinterpreted strings accidentally.
- Lowercase hostnames before comparisons.
- Strip one trailing DNS root dot, or reject it consistently, before hostname policy checks such as `localhost`, allowlist, denylist, private-suffix, and single-label checks.
- Reject or consistently normalize repeated trailing dots before hostname policy checks.
- Apply explicit port policy after parsing and before any request or redirect follow.
- Strip IPv6 brackets before IP parsing.
- Reject or explicitly normalize scoped IPv6 zone identifiers such as `[fe80::1%25eth0]`, and also test raw forms such as `fe80::1%eth0` if the runtime accepts them.
- Decide how to handle credentials in URLs; reject them unless explicitly required.
- Decide how to handle IDNA/punycode domains if host allowlists are used.
- If using host allowlists, define exact-host and wildcard-subdomain semantics explicitly. Avoid naive suffix checks; enforce DNS label boundaries after IDNA/punycode normalization and trailing-dot handling.
- Treat URL fragments as irrelevant to network fetch policy, but avoid logging full URLs if fragments may contain secrets.

### IP Classification

- Use a real IP parser or platform IP APIs; avoid regex-only classification.
- For public-internet-only fetches, block IPv4 loopback, private, link-local, carrier-grade NAT, documentation/test, benchmarking, multicast, reserved, unspecified, and broadcast ranges; document any narrower policy explicitly.
- For public-internet-only fetches, block IPv6 loopback, unique-local, link-local, documentation, discard, 6to4, Teredo, NAT64 well-known prefix when relevant, multicast, reserved, and unspecified ranges; document any narrower policy explicitly.
- For public-internet-only fetches, prefer a shared classifier based on the IANA IPv4 and IPv6 special-purpose address registries plus runtime-specific handling for mapped, compatible, scoped, and non-canonical address forms.
- Include full `0.0.0.0/8`, not only the literal `0.0.0.0`.
- Treat IPv4-mapped IPv6 addresses as their embedded IPv4 address before blocklist checks, including hex forms such as `::ffff:7f00:1`.
- Consider deprecated IPv4-compatible IPv6 forms such as `::127.0.0.1` when the runtime or legacy stack may route them to embedded IPv4.
- If the runtime accepts integer, octal, hex, or shortened IPv4 forms, normalize or reject them explicitly.

### DNS And Connection-Time Checks

- Validate literal IP hosts before any network request.
- For hostnames, resolve every address family the client may use, usually both A and AAAA, before any request.
- Define how mixed public/private answers are handled in policy terms; for example, reject the target if any returned A/AAAA answer is blocked when the policy requires all answers to be public, or select only allowed answers when the policy intentionally permits that.
- Whichever answer-handling rule is chosen, enforce the same selection at connection time so DNS rebinding or unguarded connect-time lookups cannot pick a different answer than preflight validated.
- Treat CNAME chains as part of the same target resolution decision; final A/AAAA answers must satisfy policy, and CNAME names must not bypass host allowlists or private-suffix rules.
- Decide whether to reject single-label hostnames, resolver search-domain expansion, and private DNS suffixes such as `.local`, `.internal`, `.svc`, or `.cluster.local`.
- Treat cloud metadata DNS names and addresses, for example `metadata.google.internal`, `169.254.169.254`, `fd00:ec2::254`, or provider-specific metadata aliases, according to the same private-target policy as link-local metadata IPs.
- Treat DNS resolution failure, empty answers, and invalid answers as fail-closed unless project policy says otherwise.
- Guard the actual connection-time lookup when the HTTP client allows it.
- Ensure connection pools, agents, or dispatchers are scoped so a connection validated under one policy, tenant, or trusted private-target opt-in cannot be reused for a different policy context.
- If the implementation pins a connection to a validated IP address, preserve the original hostname for `Host`, SNI, and certificate verification; do not disable TLS identity checks by replacing a hostname with a raw IP URL.
- If using Node `dns.lookup`, account for overloads such as numeric `family`, `LookupOptions`, `all: true`, and callback result shapes.
- Avoid relying only on DNS preflight if the HTTP client performs a separate unguarded lookup later.

### Proxy, Ports, And Transport Semantics

- Do not let ambient `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, or `NO_PROXY` settings silently change whether validation happens locally, at a proxy, or not at all.
- If proxies are supported, make proxy configuration explicit and validate the requested target before creating direct requests, proxy requests, or CONNECT tunnels.
- Document whether proxy-side DNS resolution is allowed; if it is, ensure it cannot bypass local public-target or allowlist policy.
- Apply port policy to the original URL and every redirect target, including explicit default ports and non-default HTTP(S) ports.
- Avoid transport rewrites that change TLS verification, SNI, `Host`, ALPN, or certificate hostname checks unless the replacement behavior is explicitly reviewed and tested.

### Redirects

- Prefer owning redirect handling in the wrapper so every hop can be validated.
- Re-run scheme, host, literal IP, DNS, and custom URL validation for each redirect target before requesting it.
- Enforce a maximum redirect count.
- Cancel or drain response bodies before throwing redirect-limit or redirect-policy errors.
- Preserve caller-visible redirect semantics only if they cannot bypass per-hop checks.
- Reject or carefully handle redirects to non-HTTP(S) schemes.
- Strip sensitive headers on cross-origin redirects.
- Strip sensitive headers on cross-scheme redirects, or explicitly justify preserving them even when the host is unchanged.
- Decide how POST-to-GET rewrites should handle body and content headers.

### Sensitive Headers And Credentials

- Do not forward ambient, inbound, session, tenant, cookie, authorization, or cloud credential headers to user-controlled targets by default, even for the initial request. Require an explicit outbound-header allowlist per trusted callsite.
- On redirects, strip at least `Authorization`, `Proxy-Authorization`, `Cookie`, `Cookie2`, and token-like project-specific headers such as `X-Api-Key`, `X-Auth-Token`, `X-Amz-Security-Token`, `X-Goog-*`, or tenant/session headers on cross-origin redirects, including scheme, host, or port changes.
- Do not include credentials in error messages, logs, thrown stack traces, or telemetry.
- Redact URLs before logging if credentials, tokens, signed URLs, or customer-controlled query strings may appear.

### Trusted Private-Target Opt-Ins

- Keep strict public-target behavior as the default.
- Add private-target opt-ins only as explicit options on trusted internal callsites.
- Name opt-ins precisely, for example `allowPrivateAddress`, not vague names like `unsafe` or `internal`.
- Document each trusted callsite and why private egress is legitimate.
- Ensure user-controlled request paths cannot set the opt-in.

### Shared Policy And Drift Prevention

- Keep IP blocklists, host normalization, mapped-IP handling, and sensitive-header lists in one shared helper when multiple layers need them.
- Avoid copying security-sensitive lists between DTO validation, service validation, fetch helpers, and tests.
- Add tests that prove ingress and runtime layers agree for literal IPs and hostname normalization.

### Test Environment Realism

- HTTP mocks do not necessarily mock DNS, socket lookup, redirects, or proxy behavior.
- If tests use `MockAgent`, fake dispatcher, or browser network mocks, separately test DNS and connection-time policy through injectable resolvers or focused lower-level tests.
- Keep tests deterministic, but do not disable the exact security behavior the test claims to cover.
- Include at least one test path that exercises the guarded lookup or resolver layer directly when the production code depends on it.

## Adversarial Test Matrix

Adapt this matrix to the runtime and policy. Mark each item as covered, not applicable, accepted tradeoff, intentionally deferred, or unresolved/blocking.

### URL Shape

- Missing hostname: `https:///path`, `https:path`, empty string, relative URL.
- Mixed-case scheme and hostname.
- Trailing dot: `https://localhost./` and allowlisted-host variants with a trailing dot.
- Repeated trailing dots: `https://localhost../` and allowlisted-host variants with repeated trailing dots.
- URL credentials: `https://user:pass@example.com/`.
- Explicit allowed, default, and disallowed ports.
- Encoded or unusual host forms accepted by the runtime.
- IDNA/punycode allowlist lookalikes when host allowlists exist.
- Host allowlist wildcard and suffix cases, for example ensuring `*.example.com` does not match `example.com.evil` or `evil-example.com`.

### Literal IPs

- For URL tests, exercise bracketed IPv6 URL forms such as `https://[::1]/` in addition to raw address classifier tests.
- IPv4 loopback: `127.0.0.1`.
- IPv4 private: `10.0.0.1`, `172.16.0.1`, `192.168.0.1`.
- Link-local metadata target: `169.254.169.254`.
- Full this-network range: `0.1.2.3`.
- Broadcast: `255.255.255.255`.
- IPv6 loopback: `::1`.
- IPv6 unique-local: `fc00::1` or `fd00::1`.
- IPv6 link-local: `fe80::1`.
- IPv6 scoped or zone identifier form, both as a URL such as `https://[fe80::1%25eth0]/` and as a raw bracketed address `[fe80::1%25eth0]`, if accepted by the runtime.
- IPv6 transition forms such as 6to4, Teredo, or NAT64 well-known prefix addresses where relevant.
- IPv4-mapped IPv6 dotted form: `::ffff:127.0.0.1`.
- IPv4-mapped IPv6 hex form: `::ffff:7f00:1`.
- IPv4-compatible IPv6 form: `::127.0.0.1`, if relevant.

### DNS

- Public hostname resolves to public address and succeeds.
- Hostname resolves to private address and is blocked before request.
- Hostname resolves to mixed public/private answers and is blocked if policy requires all answers public.
- CNAME chain resolves to a private address or private suffix and is blocked if policy requires public targets.
- Single-label hostname is rejected or explicitly allowed by policy.
- Resolver search-domain expansion cannot turn an external-looking request into an internal target.
- Private DNS suffixes such as `.local`, `.internal`, `.svc`, or `.cluster.local` are rejected or explicitly policy-covered.
- Cloud metadata DNS names resolve private or link-local and are blocked unless a trusted private-target opt-in permits them.
- DNS answer changes between preflight and connection-time lookup.
- Resolver returns no answers.
- Resolver returns IPv6 when IPv4 was expected, and vice versa.
- Runtime-specific lookup overloads, such as Node numeric family and `all: true`.

### Proxies, Ports, And Transport

- Ambient `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and `NO_PROXY` settings are ignored or explicitly controlled.
- `NO_PROXY` cannot force direct access to private targets after validation expected proxy egress.
- Proxy-side DNS resolution cannot bypass local public-target or host allowlist policy.
- CONNECT tunnel targets are validated before tunneling.
- Explicit default ports behave according to policy.
- Redirects to disallowed ports are rejected before the redirected request.
- If a validated IP is pinned, the original hostname is preserved for `Host`, SNI, and certificate verification.
- Connection pools, agents, or dispatchers do not reuse connections across incompatible tenant, policy, or trusted private-target opt-in contexts.

### Redirects

- Public URL redirects to another public URL and succeeds.
- Public URL redirects to private literal IP and is blocked before private request.
- Public URL redirects to hostname that resolves private and is blocked before target request.
- Cross-origin redirect strips sensitive headers.
- Cross-scheme redirect strips sensitive headers or has an explicit documented exception.
- Same-origin redirect preserves allowed headers.
- Redirect limit is enforced and response body is cleaned up.
- Caller redirect modes, such as follow/manual/error, cannot bypass validation.
- Redirect changes method from POST to GET where fetch semantics require it and removes body/content headers.

### Sensitive Headers And Credentials

- Initial request to a user-controlled target does not forward inbound, ambient, session, tenant, cookie, authorization, or cloud credential headers unless explicitly allowlisted.
- Errors, logs, stack traces, telemetry, and redacted URLs do not expose credentials, signed URLs, fragments, or customer-controlled secrets.

### Trusted Private-Target Opt-Ins

- Default behavior blocks private literal and private DNS targets.
- Explicit trusted private-target opt-in permits a known internal callsite.
- User-controlled call path cannot set or smuggle the opt-in.
- Redirect from trusted private callsite behaves according to documented policy.

### Response And Archive Download Cases

- Response body size limit, timeout, and abort behavior are covered where relevant.
- Error paths clean up response bodies and timers.
- Archive download callsites document that any later extraction path, link, file-count, decompressed-size, and compression-ratio controls are separate from SSRF egress policy.

## Review Procedure

1. State the intended egress behavior in one or two sentences.
2. Identify all URL sources and actors that can influence them.
3. Write or inspect the egress policy contract.
4. Review implementation against URL normalization, IP policy, DNS, connection-time lookup, proxies, ports, transport semantics, redirects, headers, trusted private-target opt-ins, logging, and response handling.
5. Review tests against the adversarial matrix and distinguish HTTP-mock coverage from DNS/socket coverage.
6. Classify findings as blockers, required tests, accepted tradeoffs, follow-ups, or not applicable.
7. If product compatibility conflicts with a strict host allowlist, document the chosen policy and the compensating runtime guardrails.

## Output Format

Use this shape:

```text
Intended behavior: <one or two sentences>

Egress policy:
- <scheme, host, port, private-network, DNS, connection-time, proxy, redirect, header, trusted private-target opt-in, and response policies>

Findings:
1. <short title>
  Severity: <ordered by severity>
  Classification: <blocker | required test | accepted tradeoff | follow-up | not applicable>
  Location: <file:line or design reference>
  Issue: <what is wrong>
  Impact: <what an attacker gains>
  Suggested fix: <specific change>

Checklist status:
- <area>: covered | not applicable | accepted tradeoff | intentionally deferred | unresolved/blocking
  (areas: URL normalization, IP ranges, DNS, connection-time lookup, proxies, ports, transport semantics, redirects, headers, trusted private-target opt-ins, shared policy, tests)

Adversarial tests: <missing or newly added tests from the matrix>

Compatibility decisions: <host allowlist or broad public-host policy, with rationale>

Residual risk: <known gaps, defense-in-depth assumptions, follow-up work, or None>
```

If there are no findings, write `Findings: None` and still complete the remaining sections.

## Definition Of Done

An outbound-fetch SSRF fix is not ready until:

- The egress policy contract is explicit.
- URL normalization and IP classification happen before security decisions.
- Hostname DNS answers and literal IPs are checked against a shared policy.
- Connection-time lookup cannot bypass preflight policy when the runtime performs a later lookup.
- Proxy behavior, port policy, and transport semantics cannot bypass host, DNS, TLS, or private-address checks.
- Redirect hops cannot bypass validation or leak sensitive headers.
- Initial and redirected outbound requests cannot leak sensitive inbound, ambient, session, tenant, cookie, authorization, or cloud credential headers.
- Private/internal targets are denied by default and require explicit trusted private-target opt-in.
- Tests cover malformed URLs, private/reserved targets, mapped IP aliases, DNS behavior, proxies, ports, redirects, sensitive-header handling on both initial requests and redirects, and test-mock limitations.
- Compatibility tradeoffs are documented as intentional decisions, not accidental gaps.
