Read this reference when an example of focused verification pseudocode would help.

## Example

**`mkdir()` can report success without creating a directory**

**Why it matters:** The code removes the final `/` before checking the wildcard. Patterns that require that slash no longer match. `mkdir()` can then report success without creating the local directory.

**Estimated priority:** Medium. Existing wildcard registrations can fail silently.

**How to reproduce:** In a test directory, register `cache-*/` as a local wildcard and call `mkdir()` for `cache-example/`. The call reports success, but the local directory is missing.

**Suggested fix:** Pass the original path to the wildcard matcher. Normalize the path only when checking for an exact directory registration.

**Verification:** Repeat the same operation and confirm that the local directory exists. For patterns without a final slash, check that slash-terminated paths match the same way they did before the change.

Pseudocode for the first check:

```text
register local wildcard "cache-*/"
call mkdir for "cache-example/"
assert local directory "cache-example" exists
```

Adapted from the [PR review comment on wildcard matching](https://github.com/Automattic/vip-go-mu-plugins/pull/7707#discussion_r4633081193).
