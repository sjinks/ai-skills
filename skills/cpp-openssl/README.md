# cpp-openssl

> Use when: designing, implementing, reviewing, or debugging C/C++ code that calls the OpenSSL (or LibreSSL/BoringSSL) library API directly - `SSL_CTX`/`SSL` setup, TLS handshakes, certificate and private-key loading, peer and hostname verification, ALPN/SNI, session resumption, the `EVP` cipher/digest/PKEY interfaces, AEAD, HMAC, key derivation, RAND, the error queue, BIO chains, memory/reference-count lifecycle, secret zeroization, and 1.1.1-vs-3.0 provider/API portability. Not for the `openssl(1)` command-line tool.

This skill governs C/C++ work that calls the OpenSSL library API directly: TLS server/client setup, handshakes, certificate and key handling, peer verification, the `EVP` cryptographic interfaces, randomness, the error queue, BIO chains, and the object lifecycle/reference-count rules that make OpenSSL safe or unsafe to use. It is scoped to the linked C API, **not** the `openssl(1)` command-line tool. It is standalone: it assumes no particular repository layout, TLS wrapper, or build system, and inspects local usage before applying its rules.

It helps an assistant:

- configure an `SSL_CTX` fail-closed: explicit protocol floor, deliberate cipher/ciphersuite policy, ALPN/SNI, and intentional session-resumption/ticket-key rotation
- get peer verification right: set `SSL_VERIFY_PEER` with trust anchors loaded **and** check the hostname/identity separately from the chain (`SSL_set1_host`/`X509_VERIFY_PARAM_set1_host`), never silently re-enabling with a verify callback that returns 1
- own every allocation and reference: match each `*_new`/`get1`/`up_ref` with a free/down-ref, never free a `get0` borrow or escape it past its parent, and prefer RAII wrappers
- drive handshake/record IO through `SSL_get_error` (want-read/want-write retry with unchanged buffers, clean close-notify vs truncation), and drain/clear the thread-local error queue for diagnosis
- use the `EVP` high-level interfaces with AEAD and unique nonces, check AEAD tags, derive keys with a real KDF, check `RAND_bytes`, compare secrets with `CRYPTO_memcmp`, and zeroize with `OPENSSL_cleanse`
- stay correct across OpenSSL 1.0.2 → 1.1.x → 3.x (opaque structs, automatic init, providers, `ENGINE` → provider) and account for LibreSSL/BoringSSL differences
- plan verification, negotiation, IO, and tamper-detection tests that fail without the fix

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
