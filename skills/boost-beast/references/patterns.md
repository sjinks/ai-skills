# Boost.Beast Patterns

This compatibility map replaces the former monolithic pattern file. Load the narrower pattern reference that matches the task:

- Use [HTTP patterns](./http-patterns.md) for parser setup, serializer lifetime, no-body responses, serialized HTTP writes, streaming bodies, and timeout wrappers.
- Use [WebSocket patterns](./websocket-patterns.md) for single-writer WebSocket sends, close-aware queueing, and message lifetime.

Use [decision trees](./decision-trees.md) first when the task is still about choosing an approach rather than writing code.