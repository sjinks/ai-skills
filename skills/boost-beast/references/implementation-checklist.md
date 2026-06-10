# Implementation Checklist

Use this checklist before and after implementing Beast code changes.

## Before Editing

- Identify the Beast boundary: parser, serializer, session loop, WebSocket session, TLS stream, proxy bridge, or adapter.
- Identify the role: client, server, proxy/gateway, tunnel, parser adapter, or WebSocket endpoint.
- Inspect the local async style: callbacks, coroutines, composed operations, strands, or single-threaded `io_context`.
- Find existing error/result types, logging patterns, test fixtures, and parser policies.
- Decide ownership for stream, buffer, parser, serializer, message, timers, and queued output.
- Decide resource limits: header, body, message, queue, and timeout.
- Decide close/drain/keep-alive behavior after rejection.

## While Editing

- Set parser limits before reads.
- Keep buffers, messages, serializers, and body storage alive until operations finish.
- Serialize reads and writes according to Beast stream rules.
- Validate framing, method/status, target, version, host, body policy, and upgrade before public adaptation.
- Map errors by protocol phase and connection state.
- Bound queues and streaming output.
- Avoid blocking filesystem, DNS, compression, or application work on the I/O executor unless the surrounding codebase already owns that tradeoff.

## Before Finishing

- Add or update tests at the narrowest stable seam.
- Include malformed and boundary cases, not only happy paths.
- Verify timeout, cancellation, disconnect, and shutdown behavior for the touched phase.
- Check logs/metrics avoid secrets and include enough protocol phase context.
- Re-run the repository's relevant build, tests, formatting, or lint commands.
- Summarize remaining untested Beast risks clearly.

## Minimum Evidence For A Finished Change

- What Beast boundary changed.
- What lifetime and operation-serialization decisions were made.
- What parser/serializer limits or policies were added or preserved.
- What close, timeout, cancellation, and error mapping behavior applies.
- What tests ran and what important cases remain uncovered.