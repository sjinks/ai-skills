---
name: "skill-audit"
description: "Audit a skill draft for consistency, cohesion, coherence, and completeness before implementation"
argument-hint: "Skill text, selected skill, or path to SKILL.md"
agent: "agent"
---

Analyze the provided skill as if auditing it before implementation. Use the skill text, selected editor content, or referenced skill file supplied by the user.

If no skill content or path is available, ask for the skill draft before continuing. If multiple skills are provided, audit each separately unless the user asks for a comparative review.

Evaluate the skill in these categories:

1. Consistency: contradictions, conflicting priorities, terminology mismatches, or incompatible instructions.
2. Cohesion: whether every section supports the same purpose and target workflow.
3. Coherence: clarity, logical flow, readability, sequencing, and ease of following the instructions.
4. Completeness: missing requirements, edge cases, input and output expectations, error handling, validation steps, and success criteria.

For each category, provide:

- `Rating`: a score from 1 to 5, where 1 means poor and 5 means excellent.
- `Findings`: specific observations grounded in the skill text.
- `Recommendations`: actionable changes that would improve the skill.

End with `Top 5 Changes`, ranked by expected impact. Focus on changes that would most improve the skill's usefulness, reliability, and ease of implementation.

Do not implement or rewrite the full skill unless explicitly asked. Keep the audit direct, concrete, and evidence-based.
