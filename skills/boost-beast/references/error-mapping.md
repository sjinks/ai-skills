# Error Mapping

Use this reference when translating Beast, Asio, TLS, parser, and WebSocket outcomes into application behavior.

## Mapping Table

| Outcome | Usually means | Normal when | Action |
|---|---|---|---|
| `http::error::end_of_stream` | Peer closed the HTTP stream cleanly enough for Beast to report EOF | Idle keep-alive read after prior complete message | Close the connection without application error |
| Parser error | Malformed or policy-rejected HTTP message | Rarely normal for untrusted clients | Reject, log sanitized reason, and usually close |
| Body limit exceeded | Request or response body exceeded configured limit | A client sends too much data | Return size error if safe, then apply the close/drain/keep-alive decision |
| Header limit exceeded | Header block exceeded policy | A client sends too many or too-large headers | Reject before public request construction |
| `net::error::operation_aborted` | Operation was canceled | Server shutdown, timeout cancellation, local close | Treat as normal if cancellation was intentional; otherwise inspect owner lifecycle |
| Timeout | Peer was idle or too slow | Slowloris defense, slow upstream, stalled write | Cancel lowest layer, close, and record timeout phase |
| Connection reset | Peer reset TCP connection | Client disconnect, upstream failure | Close session; log at low severity unless state makes it suspicious |
| TLS short read or stream truncation | TLS close was not authenticated or peer closed abruptly | Some peer ecosystems behave this way on shutdown | Decide per security boundary; do not suppress for sensitive downloads or uploads |
| TLS handshake failure | Certificate, protocol, SNI, ALPN, or peer behavior problem | Misconfigured or unauthorized peer | Fail connection before HTTP state exists |
| WebSocket close frame | Peer initiated WebSocket close | Normal close handshake | Echo/complete close and release resources |
| WebSocket protocol error | Invalid frame, message too large, bad UTF-8 when required | Malformed or malicious peer | Close WebSocket with appropriate close code |

## Error Handling Principles

- Include protocol phase in diagnostics: accept, TLS handshake, HTTP read headers, HTTP read body, write headers, write body, upgrade, WebSocket read, WebSocket write, shutdown.
- Distinguish local cancellation from remote failure. The same error code can be benign during shutdown and suspicious during steady state.
- Map malformed input separately from internal failures. Bad client bytes should not look like server bugs.
- Do not leak full headers, credentials, cookies, authorization tokens, or bodies in error logs.
- Use close behavior consistent with parser state. Ambiguous framing often requires closing instead of keep-alive reuse.

## Tests To Pair With Mapping

- Clean keep-alive close maps to normal close.
- EOF before complete headers maps to malformed or disconnect according to policy.
- Timeout during headers, body, and write each produce distinct diagnostics.
- Local shutdown cancellation does not emit an application error.
- Parser limit failures do not construct public application request objects.
- WebSocket close handshake and abnormal disconnect produce different outcomes.