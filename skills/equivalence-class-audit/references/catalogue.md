When to read: after the required-input gate, while enumerating candidate equivalents.

# Equivalence-Class Catalogue

Use these 18 canonical axis names. Candidate lists illustrate each axis; they do not expand the locked scope. Coverage and disposition rules are defined in `SKILL.md`.

### Opposite Bound

If the finding concerns one bound, audit the opposite bound and the boundary value itself.

Candidates include numeric ranges, string lengths, collection sizes, indexes, timestamps, versions, percentages, quotas, currency amounts, and retry limits.

### Sibling Parameter/Field

If the finding targets one parameter or field in a logical group, audit the other parameters or fields in that same signature, message, record, schema, config block, request, response, or form.

Candidates include pagination fields, date ranges, sort fields, resource IDs, auth token metadata, pricing fields, feature flags, configuration keys, schema columns, and migration fields.

### Mirror Call Site/Use Site

If the finding targets one invocation, reference, include, route, rule, query, template, or configuration use, audit other uses of the same API, helper, policy, schema, component, or artifact inside the locked scope.

### Inverse Operation

If the finding concerns one direction of a paired operation, audit the inverse.

Candidates include encode/decode, serialize/deserialize, marshal/unmarshal, compress/decompress, encrypt/decrypt, sign/verify, open/close, lock/unlock, subscribe/unsubscribe, create/delete, read/write, migrate/rollback, import/export, grant/revoke, and enable/disable.

### Type/Schema Narrowing

If the finding narrows a type, schema, enum, union, allowed value set, or contract at one boundary, audit all other producers and consumers that may still accept or rely on the wider shape.

Candidates include API validators, database schemas, JSON/XML schemas, protobuf/IDL definitions, config schemas, generated clients, static types, migration constraints, and downstream consumers.

### Validation vs Normalization/Sanitization

If one side was applied, audit whether the other is needed and present. Validation rejects bad input; normalization or sanitization transforms input before storage, comparison, logging, rendering, path construction, or execution.

Candidates include user strings, URLs, paths, identifiers, Unicode text, case-folded names, numeric coercion, structured logs, rendered HTML, shell or query sinks, and policy matching keys.

### Happy/Error/Retry/Cancel Path Twin

If one execution path was fixed, audit the corresponding happy, error, timeout, retry, cancellation, rollback, and partial-failure paths.

Candidates include response construction, transaction handling, state transitions, event emission, metrics, retries, compensating actions, and user notifications.

### Race/Shared-State Twin

If the finding involves consistency, ordering, idempotency, or concurrency at one site, audit other readers and writers of the same shared state.

Candidates include memory state, files, locks, queues, database rows, caches, leases, sessions, counters, idempotency keys, generated artifacts, and distributed coordination records.

### Permission/Authorization Class

If an authorization or permission check was missing or wrong for one surface, audit equivalent surfaces for the same resource, tenant, capability, role, ownership model, or administrative action.

Candidates include REST routes, GraphQL fields, RPC methods, CLI commands, background jobs, webhooks, admin variants, bulk actions, export paths, import paths, and read-only projections.

### Observability Twin

If logging, metrics, tracing, audit events, alerts, or diagnostics were missing or fixed on one branch, audit the matching branch and equivalent resources.

Candidates include success/failure metrics, span start/end, correlation IDs, audit logs, redaction rules, sampled traces, retry counters, and alert thresholds.

### Resource Cleanup

If cleanup was missing or fixed on one path, audit every path that allocates, reserves, opens, subscribes, locks, schedules, or materializes the same kind of resource.

Candidates include files, sockets, database connections, cursors, transactions, locks, timers, listeners, subscriptions, child processes, temp files, buffers, leases, and cloud resources.

### Contract Symmetry

If one side of a machine-checkable or externally consumed contract changed, audit the matching side.

Candidates include request/response shapes, schema/runtime validators, serializer/deserializer pairs, migration up/down, API spec/runtime behavior, generated client/server definitions, producer/consumer event schemas, and seed data/schema constraints.

### Equivalence by Naming

If names imply parallel responsibilities, audit the parallel symbols, sections, routes, resources, tests, or documents.

Candidates include `findBy...` families, `before...`/`after...` hooks, `on...` handlers, role-prefixed permissions, resource-prefixed routes, similarly named configuration keys, migration pairs, and repeated documentation sections.

### Test Mirror

If a test was added, changed, or revealed a bug for one case, audit the neighboring tests that should exist for sibling candidates, boundaries, paths, modes, contracts, and sentinels.

Candidates include parameterized cases, boundary tests, negative tests, contract tests, migration rollback tests, permission matrix tests, retry/cancel tests, and documentation examples that function as executable tests.

### Empty/Sentinel Equivalence

If the finding concerns one absent-like or sentinel value, audit the other sentinel values that callers or artifacts can supply for the same logical slot.

Candidates include missing key, explicit null, empty string, whitespace-only string, zero, negative one, false, NaN, empty list, empty object/map, empty file, default enum value, omitted config key, and sentinel timestamps.

### Async/Sync or Mode Twin

If the finding targets one variant or mode, audit equivalent variants.

Candidates include async/sync APIs, streaming/buffered modes, dry-run/apply modes, strict/lenient parsing, batch/single item operations, online/offline modes, admin/user modes, preview/publish modes, and read-only/mutating modes.

### Documentation/Spec Prose Twin

If behavior, constraints, errors, or guarantees changed, audit human-readable prose that describes the old behavior.

Candidates include README sections, API reference prose, comments, runbooks, migration guides, changelog notes, tutorials, generated docs, error messages, UI copy, and incident remediation notes.

### Cache/Projection/Source-of-Truth Twin

If a defect involves stale data, invalidation, consistency, or duplicated representation, audit every cache, projection, index, export, denormalized field, materialized view, read replica, or generated artifact of the same source of truth.
