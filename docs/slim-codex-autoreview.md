# Slim Codex Autoreview

Slim Codex Autoreview is a closeout review pattern for Apple Agent Kit branches and private adapter PRs. It borrows the useful discipline from OpenClaw's larger `autoreview` skill while staying Codex-native: freeze scope, review the branch diff, verify every accepted finding in the real code, fix only in-scope blockers, rerun proof, and stop when there are no accepted blockers.

This is a design and skill, not a bundled multi-engine review harness.

## Why Slim

OpenClaw's autoreview helper is a capable structured reviewer with engine isolation, multiple review engines, long-running heartbeats, model controls, and panel support. That is useful for a broad agent-skills repository, but Apple Agent Kit v0 needs a smaller public closeout gate:

- no copied helper script;
- no multi-engine panel by default;
- no private repo context in public prompts;
- no branch expansion after review starts;
- no automatic acceptance of model findings;
- no review-triggered hardware, app launch, screenshot, or physical-device execution.

Codex GitHub review remains the cloud PR path: a maintainer can request `@codex review` on a PR, and Codex posts focused GitHub review comments. Slim Codex Autoreview is the local branch habit before pushing or merging.

## Closeout Contract

Before review, freeze:

- original request or issue;
- base branch or PR base;
- changed files and intended behavior;
- public/private boundary;
- validator commands already run;
- hardware/app actions that are explicitly out of scope.

During review:

- review the diff against the frozen base;
- prioritize concrete bugs, privacy leaks, security regressions, broken validators, and missing proof;
- treat findings as advisory until verified by reading the affected code and nearby docs;
- classify each finding as `in-scope blocker`, `follow-up`, or `stop-and-escalate`;
- fix only in-scope blockers that preserve the PR's purpose;
- rerun focused validators after any fix;
- rerun review only when the fix materially changes the reviewed diff.

Stop and ask for direction when a finding requires a new public contract, a private adapter decision, credentials, hardware dispatch, product build/test execution, app launch, UI smoke, physical-device automation, screenshots, or a Codex-session bridge run.

## Apple Agent Kit Review Checklist

For public repo changes, verify:

- `python3 scripts/validate-release.py` passes;
- `git diff --check` passes;
- examples use only `example` or generic values;
- schemas and validators agree on required fields;
- public workflow templates do not dispatch private runners, install apps, launch apps, start WDA, boot simulators, touch physical devices, or start Codex session bridges;
- receipts cannot contain raw logs, local paths, hostnames, serial numbers, UDIDs, private command lines, screenshots, bundle IDs, signing teams, runner labels, or secrets;
- docs clearly separate merge-queue-tip automation from manual remote PR sessions.

For private adapter PRs, additionally verify:

- the adapter maps only approved host/run profiles;
- workflow input cannot provide shell commands;
- physical-device support is disabled unless a private approval reference is present;
- raw evidence remains local or in approved private storage;
- public docs and receipts stay sanitized.

## Local Codex Flow

Use the `codex-autoreview` skill at closeout. A typical local sequence is:

```bash
git status --short --branch
git diff --stat origin/main...
python3 scripts/validate-release.py
git diff --check
```

Then ask Codex to review the branch against the PR base using the frozen scope. The review output should be short and finding-led:

- blocker findings with file/line references;
- rejected or follow-up findings with one-sentence rationale;
- validators run;
- final verdict: `ready`, `needs-fix`, or `blocked`.

## GitHub PR Flow

After local proof passes:

1. Push the branch.
2. Open a focused PR.
3. Request Codex review on GitHub with `@codex review` when the repository has Codex code review enabled.
4. Treat Codex comments as advisory until locally verified.
5. Merge only after required checks are green and the maintainer has decided the review is resolved.

CodeRabbit can remain an optional external review source for teams that use it, but it is not required by this public kit. Its Codex plugin flow is useful context for structured findings and iterative fixes; Slim Codex Autoreview keeps the default dependency surface to Codex plus repo validators.
