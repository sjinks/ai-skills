# Boost.Beast Package Index

Use this map to load the smallest useful part of the Boost.Beast skill package. Start with the main `SKILL.md`; load these files only when the task needs the detail. If the user describes a concrete symptom, suspicious pattern, or failure mode, start with [scenarios](./scenarios.md) before choosing task-oriented references.

## Quick Routing

| Task | Load first | Then load when needed |
|---|---|---|
| Investigate a concrete code smell or failure mode | [scenarios](./scenarios.md) | Scenario-specific references from the table |
| Choose an implementation approach | [decision trees](./decision-trees.md) | [HTTP patterns](./http-patterns.md), [WebSocket patterns](./websocket-patterns.md), [body types](./body-types.md) |
| Implement HTTP parser or serializer code | [implementation checklist](./implementation-checklist.md) | [HTTP patterns](./http-patterns.md), [error mapping](./error-mapping.md), [testing](./testing.md) |
| Implement or review WebSocket code | [role playbooks](./role-playbooks.md) | [WebSocket patterns](./websocket-patterns.md), [observability](./observability.md), [testing](./testing.md) |
| Harden HTTP parsing or proxy behavior | [HTTP strictness](./http-strictness.md) | [threat model](./threat-model.md), [HTTP fixtures](../assets/http-fixtures.md), [testing](./testing.md) |
| Debug Beast behavior | [debugging](./debugging.md) | [error mapping](./error-mapping.md), [observability](./observability.md) |
| Produce a code review | [review checklist](./review-checklist.md) | [review templates](../assets/review-templates.md), task-specific references |
| Plan tests | [testing](./testing.md) | [HTTP fixtures](../assets/http-fixtures.md), [threat model](./threat-model.md) |
| Check version compatibility | [version notes](./version-notes.md) | Boost.Asio skill for executor and coroutine foundations |

## Overlap Rules

- Use [decision trees](./decision-trees.md) to choose; use pattern references to implement.
- Use [scenarios](./scenarios.md) when the starting point is an observed bad behavior rather than a planned task.
- Use [threat model](./threat-model.md) to understand risks; use [HTTP strictness](./http-strictness.md) to enforce policy; use [testing](./testing.md) and [HTTP fixtures](../assets/http-fixtures.md) to verify behavior.
- Use [role playbooks](./role-playbooks.md) for role-specific semantics; use the main `SKILL.md` procedure as the general workflow wrapper.
- Use [observability](./observability.md) for production signals after the protocol behavior is already designed.

## Terminology

- **Parser adapter:** Boundary from Beast parser/message state to public application objects.
- **Parser differential:** Disagreement between Beast and another parser or HTTP intermediary.
- **Strictness gate:** Validation after Beast parsing and before adaptation or forwarding.
- **Close/drain/keep-alive decision:** Policy for connection handling after rejection.