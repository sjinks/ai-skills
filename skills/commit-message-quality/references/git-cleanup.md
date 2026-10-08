When to read: when a proposed body contains optional Markdown headings or lines beginning with Git's configured comment character.

# Git Message Cleanup

Check the effective cleanup mode before promising that heading lines survive. According to [Git's git-commit documentation](https://git-scm.com/docs/git-commit#Documentation/git-commit.txt---cleanupltmodegt), `default` uses `strip` when the message is edited and `whitespace` otherwise; `commit.cleanup` can override the default. `strip` removes commentary, whose comment character is configurable (normally `#`). Thus it is incorrect to say all default commits remove `#` headings.

For a body with comment-like headings, recommend explicit `--cleanup=whitespace` or `--cleanup=verbatim` to preserve those lines. The former still cleans whitespace; the latter leaves the message unchanged. This skill returns advice and message text; it does not run a commit command. Keep headings out when their preservation cannot be established. Use optional headings only when they materially improve a large message, and never invent empty sections.
