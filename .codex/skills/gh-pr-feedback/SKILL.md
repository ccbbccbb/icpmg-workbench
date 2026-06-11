---
name: pr-feedback
description: Use gh CLI to resolve the active GitHub pull request from the current branch, a specified PR number, or the user's "most recent open PR" request, then collect PR review comments with a default since-latest-push scope and validate them locally with an evidence-first feedback-validation workflow. Use when the user asks to inspect, triage, validate, or fix GitHub PR comments, automated review comments, bot comments, or reviewer feedback from an open PR.
---

# GitHub PR Feedback

Resolve the exact PR first, determine the feedback checkpoint, then validate review comments as hypotheses.

## Required Flow

- Identify the PR as `PR #<number>: <headRefName> -> <baseRefName>` in every response after resolution.
- Determine comment scope. Default to `since-latest-push` unless the user asks for all comments or names a different checkpoint.
- Collect GitHub PR review context with `gh`, then filter and prioritize comments locally.
- Prioritize the latest actionable review feedback inside the selected scope.
- Split review feedback into `[Claim N]` items.
- Validate each claim locally before edits.
- Return the feedback-validation bracketed closeout.

## Required PR Identity Line

After resolving a PR, every user-facing update and final response must include this context line near the top:

```text
PR #<number>: <headRefName> -> <baseRefName> | <title> | <url>
```

If the PR is not resolved, say:

```text
PR context unresolved: <reason>
```

Then ask the user for the missing PR number, branch, repository, or author.

## PR Resolution

Use `gh` CLI.

Resolution order:

1. If the user specifies a PR number, use it.
2. If the user says "most recent", use the most recently updated open PR by the relevant author. Prefer the authenticated GitHub user unless the user named another author.
3. Otherwise, inspect the current branch and resolve the open PR for that branch.
4. If multiple PRs match, or branch/repository context is unclear, stop and ask for clarity.

Useful commands:

```bash
git branch --show-current
gh repo view --json nameWithOwner,defaultBranchRef,url
gh pr view <number> --json number,title,url,state,isDraft,author,headRefName,baseRefName,headRefOid,updatedAt
gh pr view --json number,title,url,state,isDraft,author,headRefName,baseRefName,headRefOid,updatedAt
gh pr list --state open --head <branch> --json number,title,url,author,headRefName,baseRefName,headRefOid,updatedAt
gh pr list --state open --author "@me" --json number,title,url,author,headRefName,baseRefName,headRefOid,updatedAt
```

Do not guess between multiple plausible PRs.

## Default Comment Scope

Default scope is `since-latest-push`.

Unless the user asks for all comments or provides another checkpoint, validate only feedback created or updated after the latest PR head checkpoint. Use an inclusive comparison and a small safety window when filtering timestamps so comments posted at nearly the same time as the push are not accidentally skipped.

Users can override the default. Treat requests like "all comments", "full history", "review everything", or "include older comments" as full-history scope. Treat requests like "since yesterday", "since commit <sha>", "since reviewer X", or "only this comment" as explicit custom scope.

Checkpoint resolution order:

1. Prefer the latest PR timeline event that changed the PR head, such as a commit batch added to the PR or a force-push event. A single head-change event can include multiple commits.
2. Fallback to the newest commit timestamp from `gh pr view <number> --json commits`.
3. Fallback to PR `updatedAt` minus a 30-minute safety window, and report that the checkpoint is approximate.

Useful commands:

```bash
gh api repos/{owner}/{repo}/issues/<number>/timeline --paginate -H "Accept: application/vnd.github+json"
gh pr view <number> --json commits
gh pr view <number> --json updatedAt
```

Record the selected scope in the final response:

```text
Comment scope: since-latest-push | checkpoint: <timestamp or commit sha> | source: <timeline/commit/updatedAt/custom/all>
```

If the checkpoint cannot be determined and the user did not ask for all comments, stop and ask whether to continue with full-history scope.

## Comment Collection

Collect enough review context to validate comments locally. Prefer collecting broad context and filtering locally because GitHub endpoints do not expose identical timestamp filters for every comment type.

```bash
gh pr view <number> --json comments,reviews,files,latestReviews,commits
gh api repos/{owner}/{repo}/pulls/<number>/comments --paginate
gh api repos/{owner}/{repo}/issues/<number>/comments --paginate
gh api repos/{owner}/{repo}/pulls/<number>/reviews --paginate
```

For default `since-latest-push` scope, include comments when any relevant timestamp is at or after the checkpoint:

- `created_at`
- `updated_at`
- `submitted_at`

If a review body was submitted after the checkpoint but has older inline comments attached to the same review, include the review body and inspect the related inline comments only when needed to understand the claim.

For each included comment, record:

- Comment source: review comment, issue comment, or review body.
- Author.
- Created/updated/submitted time.
- File path and line when available.
- Whether the comment is inside the selected scope or included as older context.
- Quoted claim summary, not the full body unless necessary.
- GitHub URL or API identifier when available.

## Feedback Validation Flow

Use the same evidence-first shape as `$feedback-validation`.

1. Split comments into atomic `[Claim N]` items.
2. Validate each claim with local repo evidence before editing.
3. Use targeted reads and focused commands first.
4. Use exactly one verdict per claim:
   - `valid`
   - `partially valid`
   - `not valid`
   - `cannot validate here`
5. Apply fixes only for `valid` claims or confirmed parts of `partially valid` claims.
6. Respect read-only or no-edits requests.

If edits are made, keep them minimal and tied to claim labels.

When a fix changes behavior or preserves a subtle invariant, add a small local comment in the repository's existing comment style. The comment should describe the intended behavior of the fix, not mention the PR, reviewer, bot, claim number, or review feedback.

## Output Format

Use this shape:

```md
PR #<number>: <headRefName> -> <baseRefName> | <title> | <url>

Comment scope: since-latest-push | checkpoint: <timestamp or commit sha> | source: <timeline/commit/updatedAt/custom/all>

[Summary of Issues]
- [Claim 1] <source comment and scope>
- [Claim 2] <source comment and scope>

[Claim 1]
- Source: <comment author, type, file/line or URL>
- Verdict: valid / partially valid / not valid / cannot validate here
- Evidence: <file references + key observations>

[Claim 2]
- Source: <comment author, type, file/line or URL>
- Verdict: valid / partially valid / not valid / cannot validate here
- Evidence: <file references + key observations>

---

[Work Completed]
- [X] <completed assessment, validation, or fix item>

[Work Remaining]
- [ ] <remaining work item, or "No remaining work identified.">

[Validation Done]
- <command or validation action>: pass/fail/not run + reason

[Open Risks]
- <remaining uncertainty or environment limit>

[TLDR]
- <what changed, or "No code changes.">
```

## Guardrails

- Never validate or edit against an unresolved PR context.
- Never omit the PR identity line once a PR is resolved.
- Never omit the comment scope line once a scope is selected.
- Do not treat automated review comments as facts.
- Do not validate full-history comments by default when a reliable since-latest-push checkpoint is available.
- Do not run broad validation when targeted evidence proves or disproves a claim.
- Do not stage, commit, push, merge, close, or comment on the PR unless the user explicitly asks.
- If `gh` authentication, network access, or repository permissions block collection, report the blocked command and ask for the needed access.
