# Product Fieldnotes: learning contract

## Purpose

Teach experienced product managers how methods work and where judgment matters. General professional learning is useful without company context. Never imply personal relevance from job title alone.

The new format is `learning_edition`, schema version 2. Older editions retain their data, URLs, validation rules, and rendered HTML. Do not silently rewrite the archive to match the new contract.

## Selection and cadence

Collect into private queues for practice, books, foundations, and optional frontier signals. Daily collection does not require daily publication. Select a substantive weekly learning edition. Aim for a book assessment approximately fortnightly and a short worked foundation weekly. Books and foundations can coexist; neither competes for a single slot.

There is no vendor-news minimum. An empty frontier queue must not suppress durable learning. A technical release qualifies only when its effect on PM work is demonstrated. Compare it with prior art and label distribution changes honestly. Do not use novelty scores as proof of value.

This contract does not change scheduler jobs. Schedules and delivery are administered separately. The initial pilot tests the learning format; automated validation cannot establish reader approval or content fit.

## Practice lesson

Explain the problem, what the team tried first, the actual method, its evidence, and its limits. Use a practitioner case or original research. Classify evidence as documented adoption, practitioner self-report, original research, research proposal, or editorial synthesis. Synthesis alone is not evidence of adoption.

Teach with concrete inputs and a worked decision. A worked example must include starting situation, inputs, alternatives, decision, resulting artifact, and limitations. Declare `kind: hypothetical` or `kind: documented`, and include that word in the visible label. Cite documented artifacts. An invented study plan cannot be described as an observed result.

## Books

Give title, author, publication date and format where dates differ. Explain the thesis, several ideas, critical assessment, audience, and reading verdict. State exactly what was accessed. Distinguish a full-book review from a sample assessment, publisher-description assessment, or author-interview assessment.

Public interviews can support discussion of the author's argument. They cannot establish unseen chapter contents, the quality of every case, or a full-book reading claim. Disclose transcript mirrors and whether audio was checked. Recent means a recent publication, not necessarily new this week.

## Foundations

Explain the original idea and a common misuse. Work through a decision with alternatives and an output. Do not force a foundation to share the practice topic. Use hypothetical numbers only with an explicit label, stated assumptions, and verified arithmetic.

## Evidence and readability

Put numbered citations next to externally sourced claims. Every listed source must be cited, and every section's `source_ids` must match its inline references. Source IDs start at 1 and are ordered, unique, and contiguous. Use direct HTTP(S) source URLs. Retain retrieval notes and evidence quotes privately.

Attribute self-reports. Explain incentives, selection bias, missing raw data, and access limits. A source reporting an avoided outcome is not evidence that the outcome was measured. Never turn a search snippet into a full-page reading claim.

Use accessible headings and short sentences. Paragraphs cover one idea, with at most three sentences. The existing 32-word ceiling is a backstop, not proof of clarity. Review the actual explanation for jargon, omissions, and repeated advice across sections.

## Learning schema

Common required fields: `edition_type`, `schema_version`, `slug`, `date`, `title`, `dek`, `reading_time`, `topics`, `editor_note`, `coverage_note`, `practice`, `sources`.

- `practice`: `title`, `learning_objective`, `evidence_type`, `problem`, `old_approach`, `method` (title/body blocks), `evidence`, `limitations`, `worked_example`, `source_ids`.
- `book`: optional object or null. Fields: `title`, `author`, `publication_date`, `access_basis`, `thesis`, `ideas` (title/body blocks), `critique`, `audience`, `verdict`, `verdict_reason`, `source_ids`.
- `foundation`: optional object or null. Fields: `title`, `original`, `misuse`, `worked_example`, `source_ids`.
- `worked_example`: `kind`, `label`, `situation`, `input`, `alternatives`, `decision`, `artifact`, `limitations`.
- `developments`: optional list, default empty. Each item requires `title`, `new`, `not_new`, `pm_consequence`, `evidence`, `limitations`, `source_ids`. No score fields required.
- `sources`: objects with `id`, `title`, and `url`.

Use `coverage_note` to explain omissions and gaps. Do not fill empty tracks with weak content. The pilot at `content/2026-09-12-learning.json` is the complete reference example.

## Continuity and privacy

Maintain separate queues in `private/candidate-backlog.json`. Each candidate needs sources, evidence category, prior coverage, and a learning objective. Record selection state and why it qualifies; reject padding explicitly.

Maintain topic coverage in `private/knowledge-map.json`. Audit rolling editions across strategy, discovery, prioritization, experimentation, pricing, growth, leadership, and AI-assisted or AI-native PM. Gaps guide future research, not weekly quotas. Avoid repeating the same lesson within 30 editions unless a named update warrants it. Similarity and learning value require editorial review, not title matching alone.

Keep the private directory ignored by Git. Public content must not contain company context, customer identifiers, reader details, research scratchpads, or delivery destinations. Run the private-marker scan after building and inspect the Git diff before pushing. Marker checks supplement, rather than replace, manual review.

## Publication acceptance

1. Review the actual teaching, examples, citations, and access labels.
2. Run `.venv/bin/python -m pytest tests/ -q` and `.venv/bin/python scripts/build.py`.
3. Verify old editions remain unchanged, local assets resolve, and private files are not tracked.
4. Commit and push only authorized public changes.
5. Read the exact deployed report URL and compare it with the local artifact.
6. Verify companion delivery independently. A live page is not proof of notification.
