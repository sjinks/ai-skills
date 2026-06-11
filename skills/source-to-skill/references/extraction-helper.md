# Extraction Helper Operational Reference

Read this when running `scripts/extract.py` beyond the basic preflight/list/extract commands in `SKILL.md`: capabilities, output files, metadata fields, archive limits, URL sources, and regression tests.

## Capabilities

- Standard-library extraction for `.txt`, `.md`, `.markdown`, `.rst`, `.adoc`, `.html`, `.htm`, `.rtf`, `.docx`, and `.epub`.
- PDF extraction when `pdftotext` is already installed.
- MOBI/AZW/AZW3 extraction when Calibre's `ebook-convert` is already installed.
- Archive safety checks for ZIP-based formats, with configurable member, entry-size, and total-size limits.
- Input warning metadata for missing paths, unsupported files, and directories with no supported files.
- No automatic dependency installation.
- No execution of embedded document content, macros, scripts, or examples.

## Flags And Working Directory

- Add `--strict` when any skipped, empty, or failed source should make the extraction command fail.
- Use `--mode technical` for technical books or documentation so metadata records the intended analysis mode.
- By default, the helper creates a unique working directory under `/tmp`, such as `/tmp/source_skill_work_abcd1234`, so parallel agents do not overwrite each other's extraction artifacts. The exact path is printed after extraction and recorded in `metadata.json`.
- For a stable or deliberately shared location, pass `--output-dir` or set `SOURCE_SKILL_WORKDIR`:

```bash
python3 <this-skill-directory>/scripts/extract.py <source-path-or-glob>... --mode text --output-dir /tmp/source_skill_work_MY_RUN
```

## Output Files

The helper writes these files to the selected output directory:

- `full_text.md`: combined extracted text with source boundaries. PDF form-feed page breaks are converted to `<!-- PAGE BREAK -->` markers.
- `metadata.json`: extractor/schema version, run metadata, source list, extraction methods, failures, word counts, and estimated tokens.

`metadata.json` includes each source's resolved path, byte size, SHA-256 hash when the source was small enough to read, page-break count, and line range in `full_text.md`. It also records extractor version, metadata schema version, generation time, Python version, platform, and CLI arguments when run from the command line.

Use only non-sensitive fields as provenance anchors for generated artifacts: source title or URL, content hash, and line ranges. Use file basenames only when no stronger source identity exists. Do not copy resolved paths, output directories, local source paths, or CLI arguments into generated skills or source maps.

## Reporting Extraction Metadata

- For extract-only mode, report extraction metadata operationally.
- For generated skill files, source maps, and generate/update completion reports, mention extraction method/date/version, failures, warnings, skipped inputs, empty content, or low-quality conversion only when they affect confidence, reproducibility, or limitations; omit clean-run extraction statistics.

## Archive Safety Limits

Tune with environment variables when needed:

- `SOURCE_SKILL_MAX_ARCHIVE_MEMBERS`
- `SOURCE_SKILL_MAX_ARCHIVE_ENTRY_BYTES`
- `SOURCE_SKILL_MAX_ARCHIVE_TOTAL_BYTES`
- `SOURCE_SKILL_MAX_SOURCE_BYTES`

## Regression Tests

Run the extractor regression tests after changing the helper:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 <this-skill-directory>/scripts/test_extract.py
```

## URL Sources

For URL sources, use approved fetch tools only. Preserve the URL, retrieval date, title or heading when available, and access limitations as provenance. Do not execute downloaded content, scripts, or examples. If network access, authentication, or conversion support is unavailable, stop and report the limitation instead of inventing source content.

When a URL points at a mutable branch or latest version, prefer a stable permalink, versioned URL, release tag, commit hash, DOI, or archived URL when available. Record the stable source identity instead of the transient local download path.
