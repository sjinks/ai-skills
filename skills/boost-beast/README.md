# boost-beast

> Use when: designing, implementing, reviewing, or debugging Boost.Beast, beast::http, websocket, HTTP/1.1, parser, serializer, flat_buffer, tcp_stream, ssl_stream, async_read, async_write, body limits, keep-alive, chunked encoding, pipelining, upgrades, or protocol adapter code.

This skill is aimed at Boost.Beast HTTP and WebSocket work where parser/serializer policy, resource limits, stream ownership, EOF behavior, protocol upgrades, and security-sensitive framing need explicit handling.

It helps an assistant:

- separate Beast protocol boundaries from lower-level Asio executor concerns and generic HTTP/API design
- design or review HTTP parsers, serializers, body types, WebSocket sessions, TLS stream behavior, parser adapters, and protocol-facing tests
- enforce body/header limits, strictness gates, parser differential handling, close/drain/keep-alive policy, and request-smuggling-resistant framing decisions
- use role-specific, debugging, hardening, testing, and observability references without overloading the main skill file

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/`](references/) — extended workflow and reference material.
- [`assets/`](assets/) — HTTP fixtures and review templates.
