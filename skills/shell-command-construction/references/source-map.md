Read this map when checking provenance, source confidence, or the boundary of this construction-only package.

# Source Map

| Area | Sources | Confidence |
|---|---|---|
| Shell quoting, expansions, heredocs, redirections, and pathname expansion | POSIX Shell Command Language; GNU Bash Reference Manual | High |
| Utility option termination | POSIX Utility Syntax Guidelines | High |
| Git multiline message interfaces | Git documentation | High |
| Remote command serialization and reparsing | OpenSSH `ssh(1)` manual | High |
| Secret-safe representation boundary | OWASP Secrets Management Cheat Sheet | Medium |

## Ownership boundary

This package is the normative owner for construction dispositions, required construction facts, boundary-preserving actions, and no-drift constraints. Its `Safety projection` field is always `not assessed by this skill`.

Construction output does not assess execution safety, authorization, target validity, destructive effects, or permission to run. Portability-only requests are excluded; mixed requests require `shell-portability` review before a compatibility conclusion.
