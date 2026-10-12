Read Direct Response Labels only when the caller requests replacement labels for a direct construction-only response. Read Construction Examples when checking activation, exact-byte intent, or serialization. Label selection is normative; the examples are illustrative.

# Response Labels and Examples

## Direct Response Labels

Use caller-selected labels only when the request supplies exactly five labels for the same five ordered fields. Each label must:

- contain only ASCII letters, digits, and internal spaces;
- begin and end with a letter or digit;
- contain no colon;
- be distinct case-insensitively; and
- differ case-insensitively from every canonical label.

If any condition fails, use all five canonical labels. Do not partially substitute labels. Mixed construction-and-portability requests always use canonical labels.

Map the supplied labels in order to result, assessment, candidate, authority, and next step. Preserve every core disposition, placeholder, serialization, authority-literal, and next-step rule for the matching semantic field.

A custom-labeled response is not a canonical handoff. When a later review must consume the result, retain canonical labels or provide the exact candidate as direct code.

## Construction Examples

### Construction within implementation

While preparing a larger task, the caller supplies Bash command `tool $query` and establishes that `query` is a non-secret scalar requiring exactly one argument. No other boundary requires correction.

```text
Construction result: REWRITE
Construction assessment: Double quoting preserves the confirmed scalar as one argument.
Construction candidate: tool "$query"
Execution authority: NOT ASSESSED BY THIS SKILL
Construction next step: Review the rewritten scalar boundary against the established intent.
```

A generic request to improve an application, or a mention of `tool` without construction work, does not activate. The skill does not execute the candidate.

### Intentional command substitution

The caller supplies Bash command `tool "$(date)"`, confirms one-argument expansion intent, and does not require the original stdout's trailing newline. Other command boundaries are confirmed.

```text
Construction result: VALID
Construction assessment: Intentional substitution is quoted as one argument; exact stdout-byte preservation is not required.
Construction candidate: tool "$(date)"
Execution authority: NOT ASSESSED BY THIS SKILL
Construction next step: Preserve the confirmed one-argument substitution form.
```

### Exact output bytes conflict with substitution

The caller supplies Bash command `tool "$(cat payload.txt)"`. One argument must equal the file's non-secret NUL-free bytes, including its final LF. The caller supplies no alternative representation.

```text
Construction result: BLOCKED
Construction assessment: Ordinary command substitution removes the required trailing newline before argument delivery.
Construction candidate: Not provided
Execution authority: NOT ASSESSED BY THIS SKILL
Construction next step: Provide a confirmed byte-preserving representation for the required argument.
```

### Leading whitespace

The supplied Bash fragment is exactly one leading space followed by `tool`, without terminal LF. Its construction is confirmed and already correct.

```text
Construction result: VALID
Construction assessment: Multiline serialization preserves the confirmed leading space.
Construction candidate: |
   tool
Execution authority: NOT ASSESSED BY THIS SKILL
Construction next step: Preserve the exact fragment after removing only the two-space payload prefixes.
```

For a candidate ending in LF, append a final two-space-only payload line before the authority field. That line encodes the terminal candidate LF; it is not an extra command.

### Reserved inline placeholder as actual text

The caller supplies the exact Bash fragment `Not provided` and confirms its two-word construction. Executable existence and target validity are outside scope. This candidate is actual text, not a blocked-result placeholder.

```text
Construction result: VALID
Construction assessment: The supplied two-word fragment retains its confirmed parsing boundaries.
Construction candidate: |
  Not provided
Execution authority: NOT ASSESSED BY THIS SKILL
Construction next step: Preserve the confirmed two-word fragment.
```

### Non-LF separators

When confirmed non-secret candidate data contains CR, VT, FF, U+0085, U+2028, or U+2029, preserve the actual characters. Do not substitute visible escape spellings or split on those characters. LF alone frames this report. If the response interface cannot retain the required characters, return `BLOCKED` with `Not provided` and request a byte-preserving output interface.

### Replacement-label fallback

Five eligible caller labels map to the five fields in order. A repeated label, a canonical label, or a label containing punctuation rejects the entire replacement set. Use canonical labels for that response. Mixed construction-and-portability requests also use canonical labels, even when all five replacements are otherwise eligible.

### Literal Bash exclamation mark

The caller supplies Bash command `tool "!42 suffix"` and confirms that the single literal argument must be `!42 suffix`. Bash history expansion is enabled outside POSIX mode. Other boundaries are confirmed.

```text
Construction result: REWRITE
Construction assessment: Single quoting preserves the confirmed literal argument without history expansion.
Construction candidate: tool '!42 suffix'
Execution authority: NOT ASSESSED BY THIS SKILL
Construction next step: Review the literal argument against the confirmed Bash quoting intent.
```

When an already-correct double-quoted form uses Bash POSIX mode, disabled history expansion, or the documented closing-quote exception, preserve it under `VALID`. Do not reject every command containing `!`. Exclamation marks supplied through parameter expansion are not reprocessed as history syntax merely because their expanded value contains `!`.
