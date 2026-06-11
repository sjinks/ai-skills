# Adversarial Test Matrix

Read this when reviewing test coverage for an SSRF/outbound-fetch change (Review Procedure step 5) or composing the `Adversarial tests:` output section.


Adapt this matrix to the runtime and policy. Mark each item as covered, not applicable, accepted tradeoff, intentionally deferred, or unresolved/blocking.

## URL Shape

- Missing hostname: `https:///path`, `https:path`, empty string, relative URL.
- Mixed-case scheme and hostname.
- Trailing dot: `https://localhost./` and allowlisted-host variants with a trailing dot.
- Repeated trailing dots: `https://localhost../` and allowlisted-host variants with repeated trailing dots.
- URL credentials: `https://user:pass@example.com/`.
- Explicit allowed, default, and disallowed ports.
- Encoded or unusual host forms accepted by the runtime.
- IDNA/punycode allowlist lookalikes when host allowlists exist.
- Host allowlist wildcard and suffix cases, for example ensuring `*.example.com` does not match `example.com.evil` or `evil-example.com`.

## Literal IPs

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

## DNS

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

## Proxies, Ports, And Transport

- Ambient `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and `NO_PROXY` settings are ignored or explicitly controlled.
- `NO_PROXY` cannot force direct access to private targets after validation expected proxy egress.
- Proxy-side DNS resolution cannot bypass local public-target or host allowlist policy.
- CONNECT tunnel targets are validated before tunneling.
- Explicit default ports behave according to policy.
- Redirects to disallowed ports are rejected before the redirected request.
- If a validated IP is pinned, the original hostname is preserved for `Host`, SNI, and certificate verification.
- Connection pools, agents, or dispatchers do not reuse connections across incompatible tenant, policy, or trusted private-target opt-in contexts.

## Redirects

- Public URL redirects to another public URL and succeeds.
- Public URL redirects to private literal IP and is blocked before private request.
- Public URL redirects to hostname that resolves private and is blocked before target request.
- Cross-origin redirect strips sensitive headers.
- Cross-scheme redirect strips sensitive headers or has an explicit documented exception.
- Same-origin redirect preserves allowed headers.
- Redirect limit is enforced and response body is cleaned up.
- Caller redirect modes, such as follow/manual/error, cannot bypass validation.
- Redirect changes method from POST to GET where fetch semantics require it and removes body/content headers.

## Sensitive Headers And Credentials

- Initial request to a user-controlled target does not forward inbound, ambient, session, tenant, cookie, authorization, or cloud credential headers unless explicitly allowlisted.
- Errors, logs, stack traces, telemetry, and redacted URLs do not expose credentials, signed URLs, fragments, or customer-controlled secrets.

## Trusted Private-Target Opt-Ins

- Default behavior blocks private literal and private DNS targets.
- Explicit trusted private-target opt-in permits a known internal callsite.
- User-controlled call path cannot set or smuggle the opt-in.
- Redirect from trusted private callsite behaves according to documented policy.

## Response And Archive Download Cases

- Response body size limit, timeout, and abort behavior are covered where relevant.
- Error paths clean up response bodies and timers.
- Archive download callsites document that any later extraction path, link, file-count, decompressed-size, and compression-ratio controls are separate from SSRF egress policy.
