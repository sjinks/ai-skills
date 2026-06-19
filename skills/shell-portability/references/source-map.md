Read this for the provenance and source-confidence behind the portability claims in `SKILL.md` and `references/portability-catalog.md`.

# Source Map

Portability claims track POSIX.1-2017 (IEEE Std 1003.1-2017) Shell & Utilities, the dash/busybox-ash feature sets, the bash manual, and GNU-vs-BSD/macOS coreutils man pages.

## Source confidence

- **High**: presence/absence of constructs in POSIX.1-2017 (authoritative spec text); GNU vs BSD flag differences for the common utilities in the catalog (verifiable in each project's man pages). bash version-feature gates (macOS bash 3.2) are documented in the bash manual `CHANGES`.
- **Medium**: busybox feature coverage varies by build configuration (a stripped busybox may omit applets or flags); treat busybox claims as "default build" and verify on the actual image.
- **Lower**: exact behavior of `set -e` and `echo` across every historical shell version; the catalog gives the safe portable form rather than enumerating every divergence.

## Key references

- POSIX.1-2017 Shell & Utilities (`test`, `sed`, `grep`, `xargs`, etc.) — the portable floor.
- FreeBSD man pages (`xargs(1)`, `readlink(1)`) — GNU-vs-BSD behavior differences.
- dash(1), busybox ash — near-POSIX `/bin/sh` feature sets.
- Greg's Wiki [Bashism page](https://mywiki.wooledge.org/Bashism) and [Rich's sh tricks](https://www.etalabs.net/sh_tricks.html).
