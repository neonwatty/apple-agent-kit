---
name: codex-autoreview
description: Run a slim Codex-native closeout review for Apple Agent Kit branches and PRs before commit, PR, or merge.
---

# Codex Autoreview

Use this skill when the user asks for autoreview, Codex review, PR closeout review, or a rigorous review before commit, push, PR, or merge.

## Contract

This is code review, not approval routing. Review output is advisory until verified against the real files.

Before reviewing, freeze:

- original request or issue;
- base branch or PR base;
- intended behavior and owner boundary;
- changed files and non-test scope;
- validator commands already run;
- privacy and hardware actions explicitly out of scope.

Classify findings as:

- `in-scope blocker`: introduced by this branch, concrete, and fixable without changing the PR purpose;
- `follow-up`: real but outside this branch's owner boundary;
- `stop-and-escalate`: requires a new public contract, private adapter decision, credentials, hardware dispatch, app launch, screenshots, physical-device automation, or release-process change.

Fix only in-scope blockers. After any fix, rerun focused validators and repeat review only if the reviewed diff materially changed.

## Apple Agent Kit Checks

For public repo changes, confirm:

- `python3 scripts/validate-release.py` passes;
- `git diff --check` passes;
- no private runner labels, hostnames, local paths, device IDs, bundle IDs, signing teams, screenshots, secrets, raw logs, private command lines, or repo-specific adapter details appear in public files;
- schemas, examples, docs, and validators agree;
- public workflows do not run private hardware/app automation.

For private adapter changes, do not run hardware actions unless the user explicitly approved that specific dispatch. Planning and static review are allowed; install, app launch, UI smoke, screenshots, product build/test, physical-device automation, and Codex-session bridge execution are gated.

## Output

Lead with findings, ordered by severity, using file and line references. Then list validators run and end with one verdict:

- `ready`
- `needs-fix`
- `blocked`

If there are no issues, say so clearly and mention any residual risk or unavailable proof.
