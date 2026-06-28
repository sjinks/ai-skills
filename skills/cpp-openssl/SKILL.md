---
name: cpp-openssl
description: "Use when: designing, implementing, reviewing, or debugging C/C++ that calls the OpenSSL (or LibreSSL/BoringSSL) library API directly: SSL_CTX/SSL setup, TLS handshakes, certificate and key loading, peer and hostname verification, ALPN/SNI, the EVP cipher/digest/PKEY interfaces, AEAD, key derivation, RAND, the error queue, BIO chains, object lifetime and refcounts, and 1.1.1-vs-3.0 provider portability. Not the openssl(1) command-line tool."
argument-hint: "Describe the OpenSSL API design, bug, review target, TLS flow, certificate/verification question, or crypto operation you want help with."
user-invocable: true
---

# C/C++ OpenSSL API Skill

Use this skill for C/C++ work that calls the OpenSSL library API (or an OpenSSL-compatible library such as LibreSSL or BoringSSL) directly: TLS server/client setup, handshakes, certificate and key handling, peer verification, the `EVP` cryptographic interfaces, random generation, the error queue, BIO chains, and the object lifecycle/reference-count rules that make OpenSSL safe or unsafe to use. This is about the C API linked into an application, not the `openssl(1)` command-line tool.

This skill is standalone for OpenSSL-specific design and review. Do not assume any particular repository layout, TLS wrapper (an async-I/O library's SSL stream, libcurl, a custom BIO loop), build system, or house style. Inspect the local OpenSSL usage first when editing, then apply these rules through the codebase's existing conventions.

## Routing

- **WORKFLOW SKILL**: use for OpenSSL TLS and cryptography design, implementation, review, debugging, hardening, and test planning.
- INVOKES: inspect local OpenSSL usage first (which version, which wrapper owns the handshake/IO, how the error queue is drained); apply the rules below through existing conventions.
- FOR SINGLE OPERATIONS: answer narrow OpenSSL questions directly after identifying the OpenSSL major version, the object whose lifetime/refcount is in question, and whether the data is attacker-controlled.
- Use this skill when OpenSSL is the boundary: `SSL_CTX`/`SSL` configuration, certificate/key loading, peer/hostname verification, `EVP_*` crypto, `RAND_*`, `BIO` chains, `ERR_*` handling, or OpenSSL object lifetime/refcounting.
- Out of scope items are listed under DO NOT USE FOR; in routing terms, cede the transport event loop, executor affinity, strands, timers, and socket lifecycle to the async-I/O or networking layer, returning here only for the `SSL_shutdown`/`SSL_get_error` interaction.

## DO NOT USE FOR:

- The `openssl(1)` command-line tool: key/cert generation, `s_client`/`s_server` probing, `x509`/`req`/`pkey` inspection, or shell pipelines invoking the binary. This skill is the linked C API only.
- Designing application protocol semantics (HTTP framing, request routing) where no OpenSSL call is the hard part.
- Generic "is TLS secure" policy questions with no OpenSSL code, configuration, or API in scope.
- Event-loop, cancellation, or socket-shutdown mechanics where the TLS library is incidental - route to the networking/transport layer, returning here only for the `SSL_shutdown`/`SSL_get_error` interaction.

## Operating Posture

- Treat OpenSSL as security infrastructure: a call that "works" in a happy-path test can still be insecure (verification disabled, error queue ignored, AEAD nonce reused). Prioritize verification correctness, error handling, and lifetime safety over API tidiness.
- Assume the network peer is hostile. Every byte that crosses the TLS boundary, every certificate field, and every handshake extension is attacker-influenced until a verification step says otherwise.
- Make security decisions explicit and fail-closed: protocol floor, cipher policy, peer verification, hostname matching, and certificate revocation should be deliberate configuration, never defaults you forgot to set.
- Respect the OpenSSL version in scope. 1.0.2, 1.1.0/1.1.1, and 3.x differ in defaults, API surface (opaque structs, providers, low-level deprecations), and threading model. Establish the version before asserting behavior.
- Own every allocation and reference. For each `*_new`/`*_dup`/`*_get1_*`/`*_up_ref` know who frees or down-refs it; for each `*_get0_*` know that you borrow and must not free.
- Drain and report the error queue. An OpenSSL function that returns failure usually pushed one or more entries onto the thread-local error queue; reading them is the difference between "handshake failed" and an actionable diagnosis.

## Terminology Baseline

- **Context vs connection:** `SSL_CTX` is the shared, mostly-immutable template (certificates, verify mode, options, cipher policy); `SSL` is the per-connection object created from it via `SSL_new`. Configure policy on the `CTX`, override per-connection only when needed.
- **own (`get1`/`new`/`dup`/`up_ref`) vs borrow (`get0`):** OpenSSL's naming encodes ownership. A `get1` or `new`/`dup` return value is owned by you and must be freed (or its refcount dropped); a `get0` return value is borrowed and must not be freed and must not outlive its parent.
- **Error queue:** a thread-local stack of error codes. `SSL_get_error` classifies the result of an `SSL_*` IO call; `ERR_get_error`/`ERR_error_string_n` (or `ERR_print_errors`) drain the detailed queue. The two are complementary, not interchangeable.
- **Want-read / want-write:** non-fatal results (`SSL_ERROR_WANT_READ`/`WANT_WRITE`) meaning "retry the same operation after the socket is readable/writable." They are normal flow control, not errors.
- **AEAD:** authenticated encryption (e.g. AES-GCM, ChaCha20-Poly1305) via the `EVP` interface; correctness depends on never reusing a (key, nonce) pair and on checking the authentication tag at decrypt time.
- **Provider (3.x) / engine (legacy):** the algorithm backend. OpenSSL 3.x routes algorithms through providers (`default`, `fips`, `legacy`). The `legacy` provider holds older algorithms such as RC4, RC2, single-DES, Blowfish, CAST, IDEA, SEED (ciphers) and MD4, MDC2, RIPEMD-160, Whirlpool (digests), which require explicitly loading it. Note MD5 and SHA-1 stay in the `default` provider (the TLS PRF needs them), so they keep working without the `legacy` provider.

## When To Use

- Designing or configuring a TLS server or client `SSL_CTX`: protocol version floor, cipher/ciphersuite policy, certificate chain and private key, peer verification mode, client-auth (mTLS), ALPN, SNI, session resumption/tickets, and OCSP/CRL.
- Implementing or reviewing certificate and key loading (`SSL_CTX_use_certificate_chain_file`, `use_PrivateKey_file`, `load_verify_locations`, in-memory `BIO`/`PEM_read_*` variants) and peer/hostname verification (`SSL_CTX_set_verify`, `SSL_set1_host`/`X509_VERIFY_PARAM_set1_host`, custom verify callbacks, ClientHello callbacks).
- Implementing or reviewing handshake and record IO with `SSL_do_handshake`, `SSL_read`/`SSL_write` (or `SSL_read_ex`/`SSL_write_ex`), `SSL_get_error` retry loops, and `SSL_shutdown`.
- Using the `EVP` interfaces for symmetric encryption/AEAD, digests/HMAC, key derivation (HKDF/PBKDF2/scrypt), asymmetric sign/verify/encrypt, and `EVP_PKEY` key generation.
- Generating randomness (`RAND_bytes`), comparing secrets (`CRYPTO_memcmp`), and zeroizing key material (`OPENSSL_cleanse`).
- Debugging handshake failures, `SSL_ERROR_SYSCALL`/`SSL_ERROR_SSL`, certificate-verify errors, "unsupported algorithm" after a 3.x upgrade, intermittent decrypt failures (often nonce/IV reuse), memory leaks of OpenSSL objects, or threading crashes.
- Porting code across OpenSSL 1.0.2 → 1.1.x → 3.x (opaque structs, removed `SSL_library_init`, deprecated low-level cipher/MD calls, provider loading, `ENGINE` → provider migration).

## Task Modes

- **Design mode:** define the TLS role (server/client/mTLS), the `SSL_CTX` policy (protocol floor, cipher policy, verification, ALPN/SNI), certificate provisioning and rotation, session resumption policy, and the verification/test plan before suggesting code.
- **Implementation mode:** inspect local OpenSSL usage and version first, then make the smallest change that preserves object lifetimes, drains the error queue on failure, keeps verification fail-closed, and handles want-read/want-write correctly.
- **Review mode:** lead with security and correctness risks: disabled or misconfigured verification, missing hostname check, ignored return values, ignored error queue, AEAD nonce reuse, refcount/leak bugs, non-constant-time secret comparison, and missing tests.
- **Debug mode:** build a symptom-driven hypothesis table from the `SSL_get_error` class, the drained `ERR_*` queue, the OpenSSL version, the certificate chain, and the wire bytes before proposing a fix.
- **Test-planning mode:** specify deterministic tests for valid and invalid certificate chains, hostname mismatch, expired/revoked certs, client-auth required/optional/none, protocol/cipher negotiation, renegotiation/resumption, truncation/close-notify handling, and AEAD tamper detection.

## Core Rules

### Object Lifetime And Reference Counts

- For every OpenSSL object, identify the constructor (`*_new`, `*_dup`, `PEM_read_*`, `d2i_*`) and pair it with exactly one free (`*_free`) on every path, including error paths; prefer RAII wrappers (`std::unique_ptr` with a custom deleter, or `bssl::UniquePtr`-style helpers) so early returns and exceptions cannot leak.
- Honor the `get1`/`get0` distinction: a `get1`/`up_ref` result is owned and must be freed or down-ref'd; a `get0` result is borrowed, must not be freed, and must not be stored beyond the lifetime of its parent (e.g. an `X509*` from `SSL_get0_peer_certificate` in 3.x, or a `get0` cipher/SNI string).
- Do not free an object you handed to a "transfer" API, and do free one you only shared. The `_add0_` vs `_add1_` naming encodes this: `SSL_CTX_add0_chain_cert` takes ownership (do not free), `SSL_CTX_add1_chain_cert` increments a refcount (you still free your own). Beware functions that transfer without a `0` suffix: `SSL_CTX_add_extra_chain_cert` takes ownership, whereas `SSL_CTX_use_certificate`/`SSL_CTX_use_PrivateKey` up-ref and leave you owning your reference. Check each call's documented ownership and match your free accordingly.
- Treat `SSL_CTX` as shared immutable state across connections; never mutate a `CTX` from one connection's callback in a way that races other connections. Per-connection overrides belong on the `SSL` object.
- For ex-data (`SSL_CTX_set_ex_data`/`SSL_get_ex_data`), ensure the pointed-to owner outlives every `SSL`/`SSL_CTX` that references it; the index from `*_get_ex_new_index` is process-global and should be obtained once.

### Context Configuration (SSL_CTX)

- Set an explicit protocol floor with `SSL_CTX_set_min_proto_version(ctx, TLS1_2_VERSION)` (TLS 1.3 where viable); do not rely on `SSL_CTX_set_options` with `SSL_OP_NO_TLSv1` flags as the only floor on modern OpenSSL.
- Set `SSL_OP_NO_SSLv2 | SSL_OP_NO_SSLv3` plus `SSL_OP_NO_COMPRESSION`, and prefer `SSL_OP_CIPHER_SERVER_PREFERENCE` on servers; for forward secrecy, leave ECDHE enabled and do not pin to static-RSA key exchange.
- Configure cipher policy deliberately: `SSL_CTX_set_cipher_list` for TLS ≤1.2 and `SSL_CTX_set_ciphersuites` for TLS 1.3 (they are separate knobs). Prefer a vetted modern list over hand-rolled strings.
- Choose the right method: `TLS_server_method()`/`TLS_client_method()` (1.1.0+) rather than the deprecated `SSLv23_*`/version-specific methods (on 1.1.0+ `SSLv23_method` is a deprecated alias for `TLS_method`; only the SSLv2 methods were truly removed); on 1.0.2 use `SSLv23_*_method` plus `SSL_OP_NO_*` flags.
- Configure ALPN (`SSL_CTX_set_alpn_protos` on the client, `SSL_CTX_set_alpn_select_cb` on the server) and SNI (`SSL_set_tlsext_host_name` on the client, `SSL_CTX_set_tlsext_servername_callback` / ClientHello callback on the server) explicitly where the protocol needs them.
- Decide session resumption policy: enable the session cache or stateless tickets intentionally, and rotate ticket keys; an unrotated or shared ticket key undermines forward secrecy.

### Certificates, Keys, And Peer Verification

- **This is the highest-risk area.** Default OpenSSL does NOT verify the peer unless you set it up. On a client (and on a server doing mTLS) you must both set `SSL_CTX_set_verify(ctx, SSL_VERIFY_PEER, ...)` (add `SSL_VERIFY_FAIL_IF_NO_PEER_CERT` for required client auth) and load a trust anchor set via `SSL_CTX_set_default_verify_paths` or `SSL_CTX_load_verify_locations`/`...store`.
- **Always verify the hostname/identity separately from the chain.** Chain validation does not check that the certificate matches the host you intended to reach. Use `SSL_set1_host` (1.1.0+) or `X509_VERIFY_PARAM_set1_host` before the handshake (and `SSL_add1_host` for additional names); set `X509_CHECK_FLAG_NO_PARTIAL_WILDCARDS` as appropriate. Never roll your own CN/SAN matching unless you must, and if you do, match SANs (DNS/IP) first, ignore CN when SANs are present, and reject embedded NULs.
- Do not "fix" a verification failure by returning 1 from a verify callback or setting `SSL_VERIFY_NONE`. A verify callback that returns 1 on error silently disables verification; use it only to inspect/log, leave the result intact, or apply a narrowly-scoped, documented exception.
- Load the certificate chain (leaf + intermediates) with `SSL_CTX_use_certificate_chain_file`, the private key with `SSL_CTX_use_PrivateKey_file`, then call `SSL_CTX_check_private_key` to confirm they match before serving. For in-memory material, use `BIO_new_mem_buf` + `PEM_read_bio_*` and free the BIO.
- Set verification depth (`SSL_CTX_set_verify_depth`) and decide on revocation: enable CRL/OCSP checking (`X509_VERIFY_PARAM_set_flags` with `X509_V_FLAG_CRL_CHECK`, or OCSP stapling via `SSL_CTX_set_tlsext_status_cb`) where the threat model requires it; document if you intentionally skip revocation.
- Protect private key files (filesystem permissions) and, if encrypted, supply the passphrase via a password callback rather than disabling encryption; never log key material or passphrases.
- In a ClientHello callback (server-side SNI/ALPN/JA3-style inspection), treat all parsed fields as untrusted input: bounds-check every length prefix before indexing, and fail the handshake (return the error/alert) rather than reading out of bounds.

### Handshake And Record IO

- Drive IO through `SSL_get_error` after every `SSL_do_handshake`/`SSL_read`/`SSL_write`(`_ex`): on `SSL_ERROR_WANT_READ`/`WANT_WRITE`, wait for socket readiness and retry the *same* call with the *same* arguments; on `SSL_ERROR_ZERO_RETURN`, the peer sent close-notify (clean EOF); on `SSL_ERROR_SYSCALL`/`SSL_ERROR_SSL`, the connection is fatal - drain `ERR_*` and stop.
- Never assume `SSL_write` wrote everything in one call, and never change the buffer pointer/length between a `WANT_WRITE` and its retry (unless `SSL_MODE_ACCEPT_MOVING_WRITE_BUFFER` is set). Treat partial progress and retries as the norm.
- Distinguish a clean shutdown (`SSL_ERROR_ZERO_RETURN`, i.e. close-notify received) from a truncated connection (unexpected EOF without close-notify). The classification is version-dependent: OpenSSL 1.1.x and earlier report truncation as `SSL_ERROR_SYSCALL` with a 0 return and an empty error queue, whereas OpenSSL 3.0 by default reports `SSL_ERROR_SSL` with reason "unexpected eof while reading" (`SSL_OP_IGNORE_UNEXPECTED_EOF` restores the old `SSL_ERROR_SYSCALL` behavior). For protocols where truncation is an attack vector, treat a missing close-notify as an error, not as end-of-data, under either mapping.
- If you use a higher-level wrapper (an async-I/O library's SSL stream), let it own the want-read/want-write loop; this skill governs the `SSL_CTX` policy, verification setup, and error-queue handling, while the wrapper governs the event loop.
- Be deliberate about renegotiation: it is disabled/limited by default on modern OpenSSL; do not re-enable it without a reason, and never expose unbounded peer-initiated renegotiation (a historical DoS vector).

### Error Queue Handling

- After any OpenSSL failure, capture the diagnosis before doing anything else that might call into OpenSSL: read `SSL_get_error` for the IO class, then drain the detailed queue with `ERR_get_error` in a loop (or `ERR_error_string_n` / `ERR_print_errors_cb`) for human-readable context.
- The error queue is thread-local and cumulative. Clear it with `ERR_clear_error()` *before* an operation whose success you will judge by the queue, so you do not attribute a stale prior error to the current call.
- Do not let the queue leak across an API boundary into unrelated code; a library that returns to its caller should leave the error queue clean (drain it) or document that the caller must drain it.

### EVP Crypto (Prefer High-Level Interfaces)

- Use the `EVP_*` interfaces, not low-level per-algorithm calls (`AES_encrypt`, `MD5_Init`, `DES_*`); the low-level calls are deprecated in 3.x, bypass providers, and are easy to misuse. `EVP_EncryptInit_ex`/`EVP_DigestInit_ex`/`EVP_PKEY_*` are the supported surface.
- For symmetric secrecy use AEAD (AES-GCM, AES-OCB, or ChaCha20-Poly1305), not unauthenticated CBC/CTR; if you must use a non-AEAD mode, add an encrypt-then-MAC HMAC and verify it in constant time.
- **Never reuse a (key, nonce/IV) pair with a stream cipher or AEAD** - it is catastrophic (GCM forgery, keystream reuse). Use a counter or random 96-bit nonce with documented uniqueness; rotate keys before the nonce space is exhausted.
- At decrypt time, always check the AEAD tag: with GCM, set the expected tag (`EVP_CTRL_GCM_SET_TAG`) and treat a non-positive `EVP_DecryptFinal_ex` return as authentication failure - discard all plaintext, do not act on unauthenticated bytes.
- Choose modern primitives: SHA-256/384/512 or SHA-3 for hashing (MD5/SHA-1 only for compatibility with a documented non-security use), and check every `EVP_*` return value (1 = success). Match the KDF to the input: PBKDF2/scrypt/Argon2 (deliberately slow and salted) for low-entropy **passwords**; HKDF only to expand already-high-entropy keying material - never use HKDF as a password KDF. On 3.x these are available via `EVP_KDF`.
- On OpenSSL 3.x, load the `legacy` provider explicitly if you genuinely need an algorithm it holds (e.g. RC4, single-DES, MD4, RIPEMD-160), and the `default` provider otherwise; an "unsupported algorithm" error after a 3.x upgrade usually means the algorithm lives in `legacy`. MD5 and SHA-1 are not in `legacy` (they stay in `default`), so a failure to init them points elsewhere.

### Randomness And Secret Handling

- Generate keys, nonces, and tokens with `RAND_bytes` (or `RAND_priv_bytes` for long-lived private values) and **check the return value** (1 = success); never fall back to `rand()`/`random()`/`std::rand` for security material, and never seed a CSPRNG from a predictable source.
- Compare secrets, MACs, and tags with `CRYPTO_memcmp`, not `memcmp`/`==`/`strcmp`, to avoid timing side channels.
- Zeroize key material, derived keys, and plaintext secrets after use with `OPENSSL_cleanse` (it is not optimized away like `memset`); for heap secrets prefer `OPENSSL_clear_free`/`OPENSSL_secure_clear_free`. Keep secrets out of logs, exceptions, and core dumps.

### Version And Portability

- Establish the OpenSSL major version first (`OPENSSL_VERSION_NUMBER` / `OPENSSL_VERSION_MAJOR`). 1.1.0+ made most structs opaque (use accessors, not field access) and made `SSL_library_init`/`OpenSSL_add_all_algorithms` unnecessary - init is automatic, and those calls became deprecated no-ops (not hard-removed, so legacy code still compiles); 3.x deprecates low-level algorithm APIs and the `ENGINE` interface in favor of providers.
- Guard version-specific calls with `#if OPENSSL_VERSION_NUMBER >= ...` (as the local code already does for `SSL_client_hello_*`), and prefer the accessor/`EVP` form that exists across your supported range.
- Account for LibreSSL/BoringSSL differences when targeting them: some `SSL_CTX_*` options, provider APIs, and `EVP_KDF`/`EVP_MAC` surfaces differ or are absent; do not assume an OpenSSL 3.x-only API exists there.
- Threading: 1.1.0+ manages its own locks (no manual `CRYPTO_set_locking_callback`); still treat a single `SSL` object as non-shareable across concurrent threads, and an `SSL_CTX` as safe to share for read but synchronize any mutation.

## Common Failure Modes

- Verification silently disabled: `SSL_VERIFY_NONE`, a verify callback returning 1 on error, or no trust store loaded - the connection "works" but accepts any certificate (MITM).
- Chain validated but hostname not checked: missing `SSL_set1_host`/`X509_VERIFY_PARAM_set1_host` - accepts a valid certificate for the wrong host.
- Ignored error queue: a handshake fails and the log says only "error" because `ERR_*` was never drained; or a stale queue entry is misattributed because `ERR_clear_error` was not called first.
- want-read/want-write mishandled: treating `SSL_ERROR_WANT_READ`/`WANT_WRITE` as fatal, busy-looping, or retrying with a changed buffer.
- AEAD/IV reuse or unchecked tag: reusing a GCM nonce, or treating decrypted bytes as valid without checking `EVP_DecryptFinal_ex`.
- Leaks and use-after-free: forgetting `*_free` on an error path, freeing a `get0` borrow, or storing a borrowed pointer past its parent's lifetime.
- Non-constant-time comparison of MACs/tokens with `memcmp`/`==`.
- 3.x "unsupported algorithm": a legacy algorithm used without loading the `legacy` provider, or low-level deprecated calls failing to link.

## Verification Plan

When the task changes TLS configuration, verification, or crypto, plan tests that fail without the fix:

- Verification: connect with a valid chain (accept), an untrusted/self-signed chain (reject), an expired cert (reject), and a valid cert for the wrong hostname (reject). For mTLS, test client-auth required/optional/none.
- Negotiation: assert the negotiated protocol is ≥ the configured floor and that a client offering only TLS 1.0/1.1 is rejected; assert ALPN/SNI selection.
- IO/shutdown: exercise partial reads/writes, want-read/want-write retries, clean close-notify, and (where relevant) truncation detection.
- Crypto: round-trip encrypt/decrypt; flip one ciphertext/tag byte and assert decrypt fails (tag check); assert `RAND_bytes` return value is checked; assert secret comparisons use `CRYPTO_memcmp`.
- Lifecycle: run under ASan/LSan and (where available) Valgrind to catch OpenSSL object leaks and use-after-free; confirm the error queue is empty at API boundaries.

## Definition Of Done

An OpenSSL change is ready only when:

- Peer verification is fail-closed: verify mode set, trust anchors loaded, and hostname/identity checked separately from the chain - with any exception documented and narrowly scoped.
- The protocol floor, cipher policy, and (where used) ALPN/SNI/resumption are explicit configuration, not defaults left unset.
- Every OpenSSL object has a matched free on all paths (RAII preferred), `get0` borrows are not freed or escaped, and the change runs leak-clean under a sanitizer.
- Every OpenSSL return value that signals failure is checked, the error queue is drained for diagnosis and left clean at boundaries, and `SSL_get_error` drives the IO retry loop correctly.
- Crypto uses `EVP` high-level interfaces with AEAD and unique nonces, checks AEAD tags, derives keys with a real KDF, generates randomness with a checked `RAND_bytes`, compares secrets with `CRYPTO_memcmp`, and zeroizes secrets with `OPENSSL_cleanse`.
- The code is correct for the target OpenSSL major version(s), with version-guarded calls where the API surface differs, and tests cover the verification, negotiation, IO, and tamper-detection paths above.
