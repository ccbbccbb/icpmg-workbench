---
name: gh-issue-branch
description: Create a GitHub issue for scoped work, derive a stable branch name from the issue number and title, and switch the current worktree to that branch. Use when the user asks to create an issue-backed branch, run an issue-to-branch workflow, or use $gh-issue-branch.
---

# GitHub Issue To Branch

Create a GitHub issue for a scoped unit of work, derive a branch name from the resulting issue number and title, and switch the current worktree to that branch without staging, committing, or discarding local changes.

## Workflow

1. Inspect repository state before mutating anything:

```bash
git status --short
git remote -v
git branch --show-current
```

2. Create the issue with `gh issue create` when `gh` is available and authenticated.

- Use a concise title.
- Create title-only issues. Do not pass `--body`, `--body-file`, or create temporary issue body files.
- Do not stage, unstage, commit, or discard local changes.
- If the issue title or scope cannot be inferred safely, ask the user for the missing detail before creating the issue.

3. Resolve and verify the issue number from the returned issue URL:

```bash
gh issue view <issue-url> --json number,title,url
```

4. Build the branch name with this format:

```text
ccbbccbb/{issue-number}-{issue-title-slug}
```

Slug rules:

- Lowercase.
- Replace non-alphanumeric runs with `-`.
- Trim leading and trailing `-`.
- Keep the slug concise, preferably 8-12 meaningful words at most.
- Preserve the issue number exactly.

Example:

```text
Issue #452: Migrate client server-state reads to React Query hooks
Branch: ccbbccbb/452-migrate-client-server-state-reads-to-react-query-hooks
```

5. Switch the current worktree to the new branch:

```bash
git checkout -b <branch-name>
```

## Safety And Escalation

- Never stage or commit unless the user explicitly asks.
- Never discard dirty worktree changes.
- If `git checkout -b` fails because git metadata is outside the sandbox, request escalation for the same branch creation command.
- If issue creation fails because of network access or GitHub authentication, request approval to rerun the same `gh issue create` command with network access. If authentication still fails, ask the user to authenticate `gh`.
- If a matching branch already exists, inspect it before switching; do not overwrite it.

## Final Report

Report these details after the workflow completes:

- Issue URL.
- Branch name.
- Whether local changes were present and preserved.
- Whether anything was staged or committed.
