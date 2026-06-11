---
name: explain-plainly
description: Restate chat content, specs, code discussion, product decisions, or technical concepts in plain English. Use when the user wants recent chat, pasted text, or a bounded window translated into what it means, why it matters, what happens next, blockers, tradeoffs, and outcomes.
---

# Explain Plainly

Translate discussion into the simplest accurate explanation of what is going on.

Output is terse, but formatted enough to scan. No preamble. Start with the explanation. Sentence fragments are fine.

## Workflow

1. **Lock the source.** State what's being translated (last response, pasted text, or N-response window). If ambiguous, use the smallest reasonable scope and say so or if uncertain ask for clarity.

2. **Find the core idea.** Identify the thing being explained, the practical problem it solves, who or what it affects, and the consequence if it is wrong or misunderstood.

3. **Translate jargon -> plain English.** Convert technical descriptions into observable behavior, practical meaning, or everyday cause and effect. Keep exact identifiers only when they help anchor the explanation.

4. **Add shape only when useful.** If the source is a process, include a chronological flow. If it is a concept, include the mental model. If it is a decision, include the tradeoff. If it is a bug, include expected vs actual behavior.

5. **Call out gaps.** Separate intent from reality when they differ. One line per issue: `Expected: X -> Actual: Y`.

## Output Format

Use bracketed section labels so the answer has a consistent shape without feeling like a formal report.

Include only the sections that help the explanation:

- `[Summary]`: 2-5 sentences that make the idea understandable in plain english terms without assuming codebase knowledge.
- `[Source]`: what content is being translated, only when the scope might be unclear.
- `[Why it Matters]`: practical consequence, user impact, maintenance impact, or decision pressure.
- `[How it Works]`: short step-by-step flow, state map, or cause/effect chain when the source has moving parts.
- `[Tradeoffs]`: only when the source includes competing options or design pressure.
- `[Blockers]`: only when the source includes missing info, prerequisites, or unresolved decisions.
- `[Mismatch]`: only when bugs, ambiguity, or inconsistency exist. Use `Expected: X -> Actual: Y`.

## Formatting Examples

### Concept Explanation

```md
[Summary]
This feature is a guardrail. It makes sure a player cannot start the same session twice and accidentally create two versions of the same run.

[Why It Matters]
Without this, the game can disagree with itself: one part thinks the session exists, while another part still treats it as missing.

[How It Works]
1. The first successful start writes a permanent "session exists" marker.
2. Later reads check that marker before loading gameplay data.
3. A second start sees the marker and stops before changing state.
```

### Decision Or Tradeoff

```md
[Summary]
There are two reasonable paths: keep the logic centralized, or split it into smaller files. Centralized is easier to follow at first. Split files are easier to maintain once the logic grows.

[Tradeoffs]
- Keep one file: fewer imports, but the file keeps absorbing unrelated responsibilities.
- Split by responsibility: more files, but each file has a clearer job.

[Recommendation]
Split only at the boundary where the current file is already mixing separate jobs. Do not split just to make the file count look cleaner.
```

### UX Or Process Flow

```md
[Summary]
The user is trying to continue a session from a URL. The app needs to turn that URL into one valid session id, then show either the game or a clear blocking state.

[How It Works]
1. User opens `/session/<id>`.
2. The app normalizes `<id>` into the canonical session id format.
3. If the id is valid, the app loads the session.
4. If the id is invalid or missing, the app shows the blocking state instead of guessing.

[Mismatch]
Expected: one URL format resolves consistently -> Actual: multiple parsing paths can disagree.
```

## Rules

- Use adult plain English, not baby talk. Short words are good; condescension is not.
- Prefer concrete cause and effect over analogies. Use analogies only when they make the explanation more accurate, not cuter.
- Lead with what a person needs to understand before naming internal files, types, fields, hooks, or contracts.
- Name buttons, screens, prompts, files, functions, fields, and commands exactly when known and useful.
- Do not omit guards, blockers, or prerequisites. Translate them into practical impact.
- Avoid vague phrases like "handles the logic", "manages state", or "abstracts complexity" unless you immediately explain what that means in practice.
- Keep examples, lists, and flows short. The goal is clarity, not a full spec.
- Prefer bracketed labels over markdown headings in the final answer.
- This skill explains first. If implementation is also requested, deliver the plain-English explanation first, then switch to code.
