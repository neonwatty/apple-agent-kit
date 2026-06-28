---
name: codex-pr-closeout-review
description: Run a Codex-native, read-only structured closeout review for a local branch, PR diff, dirty patch, or commit before merge or ship. Use when the user asks for PR review, branch closeout, final review, autoreview, or after non-trivial code edits.
---

# Codex PR Closeout Review

Run the bundled helper as a closeout gate, not as permission to broaden the task.

## Contract

- Freeze scope before review: original request, target base, intended behavior, owner boundary, changed files, and rough non-test LOC.
- Review only the selected diff bundle.
- Treat review output as advisory; verify every finding in the real code before patching.
- Accept only findings introduced or exposed by the current diff and fixable inside the original task boundary.
- Classify broader design, cleanup, hardening, or adjacent-surface issues as follow-up.
- Stop and report scope breakage when the best fix requires a new public API, migration, protocol, storage contract, release-process change, or owner-boundary move.
- Prefer end-to-end proof over isolated unit proof when getting code ready for PR or reviewing a PR. Unit tests are useful for tight logic, but closeout confidence should come from the smallest realistic workflow that exercises the changed behavior.
- If review-triggered edits change code, rerun focused proof and rerun this helper.
- Stop after one clean structured review. Do not rerun just for nicer wording.

## Commands

Use the skill-local helper:

```bash
skills/codex-pr-closeout-review/scripts/codex-pr-review --mode branch --base origin/main
```

For dirty local work:

```bash
skills/codex-pr-closeout-review/scripts/codex-pr-review --mode local
```

For an already-committed change:

```bash
skills/codex-pr-closeout-review/scripts/codex-pr-review --mode commit --commit HEAD
```

Run focused proof in parallel only after formatting is stable:

```bash
skills/codex-pr-closeout-review/scripts/codex-pr-review \
  --mode branch --base origin/main \
  --parallel-tests "python3 scripts/validate-release.py"
```

Optional context must be repo-relative:

```bash
skills/codex-pr-closeout-review/scripts/codex-pr-review \
  --mode branch --base origin/main \
  --prompt-file review-notes.md \
  --evidence proof/summary.json
```

## Helper Behavior

- Builds one sanitized git bundle with safe git diff flags.
- Runs one Codex review in read-only mode with structured JSON output.
- Keeps web search off unless the caller passes `--web-search`.
- Rejects evidence paths that are absolute, escape the repo, point through symlinks, look sensitive, or contain secret-like values.
- Filters findings outside the reviewed changed files.
- Writes only requested output files plus normal stdout/stderr.
- Fails the Codex engine path cleanly if the model call exceeds `--timeout-seconds`.
- Exits `0` for clean review, `1` for actionable findings or incorrect verdict, `2` for parallel proof failure, `3` for unsafe input or target setup failure, and `4` for Codex/JSON/schema failure.

## Final Report

Include the review command, proof command, accepted findings and fixes, rejected or follow-up findings with rationale, and the final clean helper result or the conscious reason a remaining finding was not fixed.
