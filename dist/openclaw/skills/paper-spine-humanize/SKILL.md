---
name: paper-spine-humanize
description: Reduces AI detection patterns in academic writing via tiered stylistic constraints applied during generation.
---

# PaperSpine Humanize

Use this branch when `humanize_tier` in `paper_spine_config.json` is set to
`light`, `medium`, or `heavy`.  Its job is to apply tier-specific writing
constraints during all prose generation phases — not as a post-hoc fix.

## When To Use

Automatically invoked by `paper-spine-rewrite` and `paper-spine-build` when
the config has `humanize_tier` set to a non-`none` value.  Users configure the
tier in the PaperSpine intake TUI (field 16).

## Tiers

| Tier | Strategy |
|------|----------|
| `light` | Replace formulaic connectors, enforce sentence-length variation |
| `medium` | + Break uniform sentence patterns, layer information density, inject first-person |
| `heavy` | + Allow controlled imperfection, vary structure, use rare terms, permit intuitive leaps |

## Instructions

Read `references/humanize-tiers-{output_language}.md` for the complete
tier-specific writing directives.  The language suffix comes from
`output_language` in the config (`zh` or `en`).

Apply the matching tier's rules throughout all writing phases.  These are
writing constraints enforced during generation — not a checklist to run after
the fact.

## Required Output: humanize_matrix.md

During writing, produce `paper_rewriting_output/humanize_matrix.md` as a
teaching artifact.  Every humanization change must be recorded in this matrix,
not applied silently:

| Row ID | Manuscript Unit | AI Pattern Found | Detection Dimension | Severity | Applied Change | Expected Effect | Teaching Note |
|--------|----------------|------------------|---------------------|----------|---------------|-----------------|---------------|

- **Manuscript Unit**: paragraph number or section name
- **AI Pattern Found**: the specific AI feature detected (e.g. "3 consecutive sentences 18-22 chars", "paragraphs all follow claim-explanation-summary")
- **Detection Dimension**: one of the 5 CNKI 2026 dimensions (sentence structure / paragraph similarity / information density / connector frequency / term-context matching)
- **Severity**: High / Medium / Low — impact on detection score
- **Applied Change**: what specific change was made
- **Expected Effect**: which dimension score this reduces
- **Teaching Note**: why this pattern triggers detectors

The matrix must be written row by row during writing, not after the fact.
Each paragraph that undergoes humanization gets at least one row.

## Verification

```bash
python scripts/humanize_check.py paper_rewriting_output --markdown --write
```

Produces `paper_rewriting_output/humanize_report.md`.  Checks matrix coverage
against total paragraphs, scans for remaining AI patterns, and flags gaps.

## Integration

This branch is called internally by rewrite and build.  Users do not invoke it
directly.  The orchestrator pipeline includes it as an optional stage after
writing and before LaTeX assembly.
