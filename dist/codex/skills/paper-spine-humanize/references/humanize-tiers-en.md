# AI Humanization Writing Directives (English)

Apply when `humanize_tier` in `paper_spine_config.json` is not `none`.
Aligned with the 5 core detection dimensions: sentence structure, paragraph
similarity, information density, connector frequency, and term-context matching.

## Universal Rules (all tiers)

1. Preserve all LaTeX commands, citation keys, equations, file paths, numeric values
2. Do not change factual content
3. Do not add evidence the author has not provided
4. Keep technical terms as-is (unless heavy tier explicitly allows substitution)

---

## light

### Dimension 1: Sentence Structure
- Every 4 sentences, at least 1 must differ significantly in length (short ≤ 8 words or long ≥ 30 words)
- No 3 consecutive sentences with length difference under 6 words
- No two consecutive paragraphs starting with the same sentence pattern

### Dimension 2: Paragraph Structure
- No two consecutive paragraphs using the same structural template
- Available templates: claim-evidence-implication / problem-analysis-conclusion / compare-judge / question-answer / position-counter-synthesis
- Adjacent paragraphs must use different templates

### Dimension 3: Information Density
- No requirement at this tier

### Dimension 4: Connectors
- Ban: Firstly/Secondly/Finally, In conclusion/To sum up, Furthermore/Moreover/Additionally, It is worth noting/It should be pointed out
- Replace with natural logical flow between paragraphs
- Keep connectors under 8 per 1000 words

### Dimension 5: Term-Context Matching
- No requirement at this tier

---

## medium (includes all of light + below)

### Dimension 1: Sentence Structure
- Length distribution must show at least two peaks: one at 6-12 words (short), one at 25-35 words (long)
- Short sentences ≥ 15% per section

### Dimension 2: Paragraph Structure
- Each structural template used at most twice in the entire paper
- Use at least 4 different templates

### Dimension 3: Information Density
- Core argument paragraphs: density ≥ 80%
- Transition paragraphs: density ≤ 50%
- Create high-low-high density alternation
- Density difference between consecutive paragraphs ≥ 15%

### Dimension 4: Connectors
- Under 6 per 1000 words
- Connectors only at logical turning points, never at paragraph starts

### Dimension 5: Term-Context Matching
- Inject first-person academic narration ("Our study found", "We observed in experiments")
- At least 2 instances per 2000 words

---

## heavy (includes all of medium + below)

### Dimension 1: Sentence Structure
- Three peaks in length distribution: short (4-8 words), medium (12-20 words), long (30+ words)
- Add inverted sentences and rhetorical questions (1-2 per section)
- Allow 1-2 intuitive leaps skipping intermediate reasoning

### Dimension 2: Paragraph Structure
- Use 5+ different structural templates
- Introduction: may lead with problem, not "background→gap→approach→contributions"
- Discussion: may leave 1-2 questions deliberately open

### Dimension 3: Information Density
- Label every paragraph's density (high/medium/low). No 3 consecutive paragraphs at the same level.

### Dimension 4: Connectors
- Under 4 per 1000 words
- Connectors clustered at 2-3 critical logical turns; omitted everywhere else

### Dimension 5: Term-Context Matching
- Replace 1-2 standard academic terms with accurate-but-colloquial alternatives
- Allow occasional informal expression ("in other words", "to put it plainly")
- Allow personal commentary after result analyses
- At least 1 uncommon-but-precise academic term per 800 words
