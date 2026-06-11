---
name: scope-flow
description: Use Scope Flow for read-only scope, tracked draft/todo lifecycle docs, completed archival, and review-gated commits. Automatic scoped commits are allowed only in explicit Mode 4.
---

# Overview: Scope Flow

Use this skill when the user asks to scope work, create or refine a checklist plan, operate in read-only investigation mode, integrate a scoped task, or continue from an existing scope document, prompt, log, report, or user-provided context.

Scope Flow keeps scope documents out of the repo root, uses folder state to show lifecycle, and supports review-gated checkpoints with user-approved commits by default. Automatic scoped commits happen only in explicit Mode 4.

## 1. Mode Selection

Determine the mode via user prompt and context before doing work.

1. Read Only: inspect and analyze only. Do not write files, stage, commit, run mutating commands, or modify generated artifacts. Scope and investigation happen in chat until confirmed by the user.
2. Prepare Scope: inspect the repo and create or update a tracked draft markdown scope file. Only move a draft to todo after user confirmation.
3. Integrate Review-Gated: validate the confirmed scope against the codebase, move the tracked scope doc through todo, in-progress, ready-for-qa, and completed archival states, implement the confirmed scope, validate touched surfaces, and stop at each commit checkpoint for user review.
4. Integrate With Commits (explicit only): same as (3), but the agent may automatically stage and commit scoped files at lifecycle checkpoints without asking again at each checkpoint. Never choose Mode 4 by default or by inference. Use Mode 4 only when the user explicitly asks for automatic commits, "mode 4", "mode four", "commit as you go", or equivalent wording.

If the user says "readonly", "read only", "read-only", "scope only", "no edits", or "investigate only", choose (1).

If the user asks to integrate a scope without explicitly asking for automatic commits or mode four (4), choose three (3).

If it is not clearly one of the four modes, default to (1). Provide a scope preview in chat and ask whether to proceed to (2). Do not jump directly from (1) to (3) or (4).

## 2. Scope Markdown File Lifecycle

### 2.a • Folder States

Use folder location as the source of truth for scope state:

1. Read Only: no scope file exists; scope preview stays in chat only.
2. Draft [1/5]: `reports/scope/drafts/<MM-DD-SLUG-SCOPE.md>`.
3. Todo [2/5]: `reports/scope/todo/<MM-DD-SLUG-SCOPE.md>`.
4. In Progress [3/5]: `reports/scope/in-progress/<MM-DD-SLUG-SCOPE.md>`.
5. Ready For QA [4/5]: `reports/scope/ready-for-qa/<MM-DD-SLUG-SCOPE.md>`.
6. Completed [5/5]: `reports/scope/completed/<MM-DD-SLUG-SCOPE.md>`.

### 2.b • Lifecycle Rules

- `reports/scope/drafts/` is a tracked lifecycle folder for pre-todo scope drafts.
- Draft docs may be staged and committed when the user asks to preserve draft history, but do not auto-promote them to todo without user confirmation.
- `reports/scope/todo/`, `reports/scope/in-progress/`, and `reports/scope/ready-for-qa/` are tracked lifecycle folders.
- `reports/scope/ready-for-qa/` keeps a tracked `.gitkeep` so the QA handoff folder exists even when no scope is waiting there.
- `reports/scope/ready-for-qa/` means the agent integrated the scope and local validation passed, but the user still needs to QA or validate the result.
- `reports/scope/completed/` is the final archive after user validation. Move completed scope docs directly into this folder.
- Do not create scope files in the repo root.
- Do not use top-level `reports/todo/` for Scope Flow docs; use `reports/scope/todo/`.
- Do not auto-push branches or auto-create pull requests.

## 3. Scope Markdown File Naming And Headings

### 3.a • File Names

- Scope markdown filenames must start with `MM-DD-`, using the month and day from the document's `Created` timestamp (zero-padded, UTC-5).
- After creation, keep the filename stable across lifecycle folder moves. Do not rename the date prefix when promoting draft to todo, in-progress, ready-for-qa, or completed.
- Scope markdown filenames must use uppercase kebab-case with a `.md` extension.
- Scope files must end with `-SCOPE.md`.
- Do not create an extra per-scope folder inside `reports/scope/{drafts,todo,in-progress,ready-for-qa}`.
- Example draft path: `reports/scope/drafts/05-27-EXAMPLE-TASK-SCOPE.md`.
- Example ready-for-qa path: `reports/scope/ready-for-qa/05-27-EXAMPLE-TASK-SCOPE.md`.
- Example completed archive path: `reports/scope/completed/05-27-EXAMPLE-TASK-SCOPE.md`.

### 3.b • Markdown Heading Numbers

- Number every `##` heading and every `###` subheading in scope docs.
- Use dotted subheading labels under their parent heading: `### 3.a • Example Heading`.
- Optional sections must still use a numbered heading and include `(Optional)`: `### 5.d • Example Heading (Optional)`.
- Keep heading numbers stable while editing. If a section is removed, renumber before finishing the scope update.

## 4. Checklist Rules

All planning and implementation docs must use checklist-driven execution:

- `[ ]` means not started, blocked, deferred, or not locally verified.
- `[X]` means the code exists and the required validation passed locally.
- Do not mark an item `[X]` based only on intent, partial implementation, inspection, or unrun tests.
- Include validation commands required for every touched surface.
- If validation is not run, fails, or is blocked, leave related items unchecked and state why.
- Do not create a second backlog section that duplicates unchecked checklist items. The checklist is the source of truth.

## 5. Scope Size And Milestones

Assign a scope size before integration starts:

- Small: one surface, low risk, docs-only, or a contained one-file change. Use a todo checkpoint and a ready-for-qa checkpoint only.
- Medium: multiple files in one surface. Add one milestone checkpoint after the primary behavior is implemented and validated.
- Large: multiple surfaces, contract plus client, generated artifacts, risky refactors, or broad test churn. Add named milestones in the scope doc before implementation begins.

Milestones are not time-based. A milestone checkpoint happens only when a coherent, locally validated slice is complete.

Each milestone should have:

- A short name, such as `contract validation`, `client wiring`, or `test cleanup`.
- The exact files or checklist items it owns.
- The validation command that must pass before the milestone checkpoint.
- A conventional commit message chosen before work begins.

## 6. Change Documentation Rules

For (2), (3), and (4), every scope document that targets code changes must include concise change documentation immediately after `## 2. Scope`. Choose exactly one path based on the number of main code targets:

- For 1 to 3 targeted function-level refactors, use `## 3. Changes` with `### 3.a • Changes Before` and `### 3.b • Changes After`.
- Each before/after section must use fenced `code` blocks to show the current code being targeted and the expected shape after scoped work.
- Keep before/after blocks focused on the relevant functions, branches, or callsites. Do not paste unrelated files.
- For more than 3 main targets, use `## 3. Affected Logic` instead of before/after blocks.
- `## 3. Affected Logic` must be a numbered list of all primary target filepaths with LOC references: `1. {nameOfCode} in {pathToFile}:{LOC} - <single sentence incoming change>`.
- If there are many small repetitive changes, group them under `### 3.a • Other Logic Changes (Optional)` with concise bullets instead of expanding every tiny helper into the primary numbered list.

## 7. Scope Document Shape

For (2), (3), and (4), write or update a repo scope document with this structure:

Set `Created` exactly once when creating the scope document. Use the current time in `MM-DD-YY HH:mm (UTC-5)` format. Preserve the original `Created` value on later edits, lifecycle moves, and archival.

````md
# <Task Name>

Created: <MM-DD-YY HH:mm (UTC-5)>
Status: Draft [1/5] | Todo [2/5] | In Progress [3/5] | Ready For QA [4/5] | Completed [5/5]
Scope Size: Small | Medium | Large

## 1. Goal

<One or two sentences describing the concrete outcome.>

## 2. Scope

- [ ] <Specific implementation or investigation item>
- [ ] <Specific implementation or investigation item>

## 3. Changes

### 3.a • Changes Before

```code
<For 1 to 3 targeted function-level refactors, show the relevant current code.>
```

### 3.b • Changes After

```code
<For 1 to 3 targeted function-level refactors, show the expected changed shape.>
```

<For more than 3 main targets, replace `## 3. Changes` with:>

## 3. Affected Logic

1. `<nameOfCode>` in `<pathToFile>:<LOC>` - <Single sentence description of incoming change>

### 3.a • Other Logic Changes (Optional)

- <Optional concise grouping for many small repetitive changes>

## 4. Milestones

- [ ] `<commit message>` after <coherent validated slice>. Validation: `<command>` from `<directory>`.

<For small scopes, use:>

No milestone checkpoints required for this small scope.

## 5. Ready For QA Plan

- [ ] Move the completed implementation scope doc to `reports/scope/ready-for-qa/<MM-DD-SLUG-SCOPE.md>` after local validation passes.
- [ ] Ask the user to QA or validate the integrated work.

## 6. Completed Archive Plan

- [ ] After user validation, move the scope doc to `reports/scope/completed/<MM-DD-SLUG-SCOPE.md>`.

## 7. Out Of Scope

- <Boundaries that prevent accidental expansion>

## 8. Validation

- [ ] `<command>` from `<directory>` validates <surface>
- [ ] `<command>` from `<directory>` validates <surface>

## 9. Results & Agent Notes

Fill this out only when the current task is 100% done.
````

## 8. Commit Protocol

By default in Modes 1 through 3, the agent must not stage or commit lifecycle checkpoints unless the user explicitly approves that checkpoint. Mode 4 is the only exception.

At each Scope Flow checkpoint, the agent must report:

- Changed files.
- Validation results.
- Proposed conventional commit message.
- Any risks, blockers, or review notes.

Mode 4 is the only Scope Flow automatic-commit mode. Never infer Mode 4 from integration requests alone. In Mode 4, the agent may stage and commit scoped files at lifecycle checkpoints without asking again, as long as the commit remains scope-specific, validations required for that checkpoint have passed, and no stop condition applies.

### 8.a • Lifecycle Checkpoints

- Todo checkpoint: after the user confirms the draft, move the doc from `reports/scope/drafts/<MM-DD-SLUG-SCOPE.md>` to `reports/scope/todo/<MM-DD-SLUG-SCOPE.md>`.
- Milestone checkpoints: required for medium and large scopes according to the milestone plan; optional for small scopes.
- Ready-for-QA checkpoint: after all scoped implementation and required local validations pass, move the doc to `reports/scope/ready-for-qa/<MM-DD-SLUG-SCOPE.md>`.
- Completed archive checkpoint: after the user validates the integrated work, move the doc to `reports/scope/completed/<MM-DD-SLUG-SCOPE.md>`.

In Mode 3, stop after preparing each checkpoint and wait for explicit user approval before staging or committing.

In Mode 4, create the checkpoint commit using the Scoped Staging Protocol.

### 8.b • Scoped Staging Protocol

Before every Scope Flow commit, whether approved checkpoint-by-checkpoint in Mode 3 or automatic in Mode 4:

1. Record currently staged paths with `git diff --cached --name-only`.
2. Compare staged paths against the scope-owned paths.
3. If unrelated files are staged, unstage only those unrelated paths.
4. Stage only scope-owned paths for the current commit.
5. Commit with the planned conventional commit message.
6. Restage the unrelated paths that were staged before the scope commit.

### 8.c • Stop Conditions With Examples

Stop and ask the user before committing in all modes if:

- A pre-staged file overlaps a scope-owned file. Example: `client/src/battle/useBattle.ts` is already staged before integration starts, and the scope also modifies that file.
- The scope-owned file needs partial staging. Example: `client/src/app/page.tsx` contains both the scoped UI fix and local debug edits that should not be committed.
- A validation required for the commit is failing or blocked. Example: `bun run types` fails after client changes, or `sozo test` cannot run because the local profile is unavailable.
- The commit would include files outside the confirmed scope. Example: the scope covers client copy changes, but `contracts/src/systems/battle.cairo` or `.env.local` is staged for the commit.

Never force push.

## 9. Workflow Breakdown

### 9.a • Read Only Workflow

1. Inspect only the files needed to understand the task.
2. Identify the most direct implementation path that matches existing architecture and validation requirements.
3. Keep scope and checklist output in chat only.
4. Do not create a markdown file unless the user confirms the read-only investigation is good.
5. After user confirmation, proceed to (2) so the scope is captured in a draft markdown file.
6. End with a one-sentence summary of current state. If there is actionable work, the next step is to proceed to (2).

### 9.b • Prepare Scope Workflow

1. Inspect only the files needed to understand the task.
2. Create or update the draft scope file under `reports/scope/drafts/<MM-DD-SLUG-SCOPE.md>`. For new scopes, derive the `MM-DD-` filename prefix from the `Created` timestamp in §3.a.
3. Set `Created` to the current time in `MM-DD-YY HH:mm (UTC-5)` format if the scope file is new, then never change it.
4. Set `Status: Draft [1/5]`.
5. Include implementation steps, validation commands, scope size, and checklist items.
6. Leave all implementation and validation items unchecked unless implementation and validation are already complete.
7. Do not stage or commit draft scope files unless the user explicitly asks to preserve draft history.
8. End with a one-sentence summary of current state. Ask the user to confirm whether the draft should move to todo.

### 9.c • Todo Promotion Workflow

After the user confirms a draft is ready to enter the tracked todo queue:

1. Move the scope doc from `reports/scope/drafts/<MM-DD-SLUG-SCOPE.md>` to `reports/scope/todo/<MM-DD-SLUG-SCOPE.md>`.
2. Set `Status: Todo [2/5]`.
3. Handle the todo checkpoint using the Commit Protocol.
4. Suggested commit message: `docs: add todo scope for <task>`.
5. End with the todo scope path and the first unchecked integration item.

### 9.d • In Progress Workflow

1. Start from a tracked scope doc in `reports/scope/todo/` or `reports/scope/in-progress/`.
2. If only a draft exists, ask the user to confirm todo promotion before integration.
3. Validate the scope against the current codebase before implementing.
4. Propose scope corrections before implementation when the provided plan is stale, incomplete, or mismatched with the code.
5. When implementation begins, move the scope doc to `reports/scope/in-progress/<MM-DD-SLUG-SCOPE.md>` and set `Status: In Progress [3/5]`.
6. Implement only confirmed scoped items unless the user expands the task.
7. Preserve existing comments, names, formatting, and architecture.
8. Update checklist state only after each item is implemented and locally verified.
9. Run required validation commands for every touched surface.
10. Handle milestone checkpoints according to the scope size and milestone plan.
11. Leave failed, blocked, or deferred work unchecked.

### 9.e • Ready For QA Workflow

When all current scoped implementation is complete:

1. Run all required validations for touched surfaces.
2. Mark checklist items `[X]` only when implementation exists and validation passed locally.
3. Move the scope doc to `reports/scope/ready-for-qa/<MM-DD-SLUG-SCOPE.md>`.
4. Set `Status: Ready For QA [4/5]`.
5. Fill out `## 9. Results & Agent Notes` with implementation summary, validations, and commits if created.
6. Handle the ready-for-qa checkpoint using the Commit Protocol.
7. Suggested commit message: `patch: integrate <task>` unless `feat`, `fix`, `test`, `refactor`, or `docs` is more accurate.
8. Ask the user to QA or validate the integrated work.

### 9.f • Completed Archive Workflow

After the user confirms the integrated work is validated:

1. Move the scope doc from `reports/scope/ready-for-qa/<MM-DD-SLUG-SCOPE.md>` to `reports/scope/completed/<MM-DD-SLUG-SCOPE.md>`.
2. Set `Status: Completed [5/5]`.
3. Handle the completed archive checkpoint using the Commit Protocol.
4. Suggested commit message: `docs: archive completed scope for <task>`.

## 10. Requirements Checklist

- The implementation matches the current checklist, including scope changes made after inspecting the code.
- Required validations have passed for touched surfaces, or blocked validation remains unchecked with the reason stated.
- The checklist reflects real state: `[X]` only for implemented and locally verified work, `[ ]` for anything deferred, blocked, or not yet validated.
- No unchecked item remains that belongs to the current task before moving to `reports/scope/ready-for-qa/`.
- Required todo, milestone, ready-for-qa, and completed archive checkpoints have been handled through the Commit Protocol when the workflow reaches those phases.

For pure (1), implementation acceptance can be skipped. Done means the investigation is accurate enough for the user to decide whether to proceed to (2).

For pure (2), implementation acceptance can be skipped. Done means the draft scope is accurate enough for the user to decide whether to move it to todo.

## 11. Results & Agent Notes Format

Fill this out only when the current task is 100% done. Keep the summary under 140 characters.

```md
[Mode]
<(1) Read Only | (2) Prepare Scope | (3) Integrate Review-Gated | (4) Integrate With Commits>

[Validation]
- `<command>`: <passed | failed | not run, with reason>

[Commits]
- `<sha>` `<message>` or `Not created; awaiting user approval.`

[Summary]
<One sentence, max 140 characters. Example: "Integrated checked scope and passed client validation.">
```
