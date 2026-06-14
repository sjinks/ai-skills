# archive-extraction-safety

> Use when: reviewing, designing, implementing, or testing safe archive extraction for ZIP, TAR, tar.gz, tgz, package importers, backup restore, plugin/theme upload, artifact unpacking, decompression bomb controls, Zip Slip, Tar Slip, symlink and hardlink entries, absolute paths, Windows drive, UNC, namespace, device, ADS, or normalization hazards, Unicode path normalization, nested archives, parser mismatch, extraction destination-root trust and containment, race-resistant writes, overwrite policy, and cleanup after partial extraction.

This skill is aimed at code and designs that extract untrusted or semi-trusted archives into a destination directory.

It helps an assistant:

- define the extraction contract, accepted formats, destination root, allowed entry types, overwrite policy, and resource limits
- review ZIP/TAR traversal, absolute paths, Windows drive/UNC paths, Unicode/path normalization, symlinks, hardlinks, special files, executable bits, permission/ownership restoration, parser mismatch, and destination containment
- check file count, decompressed size, compression ratio, nested archive depth, and partial extraction cleanup
- return `BLOCK`, `CONCERNS`, or `CLEAN` with findings, checklist status, tests, and residual risk

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
