# source-to-skill

> Use when: converting books, articles, documentation, notes, transcripts, or other source material into reusable agent skills; extracting frameworks, decision rules, workflows, checklists, examples, provenance, and validation gates for high-value generated skills.

This skill is aimed at turning source material into reusable agent skills that change future agent behavior, rather than producing document summaries. It was inspired by [book-to-skill](https://github.com/virgiliojr94/book-to-skill/blob/master/SKILL.md).

It helps an assistant:

- inventory source paths, URLs, notes, folders, globs, prior analysis, and existing skills before deciding whether to analyze, generate, or update
- apply rights, substitution, source-integrity, and scope gates before writing generated skill files
- use the local extractor helper for supported local documents, preserving metadata, source boundaries, line ranges, hashes, extraction quality, and warnings as provenance anchors
- extract behavior-shaping material such as trigger contexts, decision rules, workflows, checklists, frameworks, anti-patterns, examples, vocabulary, and confidence notes
- generate compact `SKILL.md` files with optional references, examples, or checklists only when those supporting files reduce cognitive load
- validate frontmatter, trigger specificity, links, provenance, copyright posture, output formats, severity rubrics, stop conditions, and completion reporting before declaring success

## Files

- [`SKILL.md`](SKILL.md) — the full skill definition.
- [`references/`](references/) — extended workflow and reference material.
