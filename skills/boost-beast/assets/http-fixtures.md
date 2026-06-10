# HTTP Fixtures

Use these raw fixtures as seeds for Beast parser tests, strictness gates, proxy/gateway tests, and fuzz corpora. Replace `\r\n` escapes with actual CRLF bytes when a test helper requires literal wire format.

Fixtures are grouped as **trusted** when they represent known-good shapes and **untrusted or ambiguous** when they exercise malformed, hostile, or parser-differential-sensitive input.

## Trusted Fixtures

### Valid Minimal HTTP/1.1 Request

```text
GET / HTTP/1.1\r\n
Host: example.test\r\n
\r\n
```

Expected: accept if origin-form `GET /` is allowed.

### Valid Keep-Alive Pair

```text
GET /one HTTP/1.1\r\n
Host: example.test\r\n
\r\n
GET /two HTTP/1.1\r\n
Host: example.test\r\n
\r\n
```

Expected: two cleanly separated requests if pipelining or sequential keep-alive parsing is supported.

## Untrusted Or Ambiguous Fixtures

### Missing Host

```text
GET / HTTP/1.1\r\n
User-Agent: test\r\n
\r\n
```

Expected: reject when HTTP/1.1 `Host` is required.

### Duplicate Matching Content-Length

```text
POST /upload HTTP/1.1\r\n
Host: example.test\r\n
Content-Length: 5\r\n
Content-Length: 5\r\n
\r\n
hello
```

Expected: accept only if duplicate matching lengths are explicitly permitted; otherwise reject.

### Conflicting Content-Length

```text
POST /upload HTTP/1.1\r\n
Host: example.test\r\n
Content-Length: 5\r\n
Content-Length: 6\r\n
\r\n
hello!
```

Expected: reject and close.

### Transfer-Encoding Plus Content-Length

```text
POST /upload HTTP/1.1\r\n
Host: example.test\r\n
Transfer-Encoding: chunked\r\n
Content-Length: 4\r\n
\r\n
5\r\n
hello\r\n
0\r\n
\r\n
```

Expected: reject or handle exactly as documented. Proxy/gateway paths should treat this as request-smuggling-sensitive.

### Malformed Chunk Size

```text
POST /upload HTTP/1.1\r\n
Host: example.test\r\n
Transfer-Encoding: chunked\r\n
\r\n
Z\r\n
hello\r\n
0\r\n
\r\n
```

Expected: reject and close.

### Missing Chunk Terminator

```text
POST /upload HTTP/1.1\r\n
Host: example.test\r\n
Transfer-Encoding: chunked\r\n
\r\n
5\r\n
hello\r\n
```

Expected: incomplete message; EOF before complete chunked body is not a successful request.

### Pipelined Request After Rejected Body

```text
POST /upload HTTP/1.1\r\n
Host: example.test\r\n
Content-Length: 1000000000\r\n
\r\n
GET /admin HTTP/1.1\r\n
Host: example.test\r\n
\r\n
```

Expected: reject oversized body and close; do not interpret hidden bytes as a second request.

### Absolute-Form Target

```text
GET http://example.test/path HTTP/1.1\r\n
Host: example.test\r\n
\r\n
```

Expected: accept only for proxy/gateway roles or documented origin-server compatibility.

### CONNECT Authority Form

```text
CONNECT example.test:443 HTTP/1.1\r\n
Host: example.test:443\r\n
\r\n
```

Expected: handle only in a tunnel role after destination policy approval.

### Header Injection Attempt

```text
GET / HTTP/1.1\r\n
Host: example.test\r\n
X-Test: safe\r\n
 injected: folded\r\n
\r\n
```

Expected: reject if obsolete folding is not permitted by local strictness policy.