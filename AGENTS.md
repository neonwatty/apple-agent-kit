# Agent Instructions

Use this repository as a public, reusable Apple automation kit. Keep app-specific details such as bundle identifiers, signing teams, runner labels, device names, account data, private URLs, and product smoke profiles out of the public tree.

## Closeout Review

- Use `skills/codex-pr-closeout-review` for PR, branch, commit, or dirty-work closeout reviews before merge or ship.
- Prefer end-to-end testing over unit tests when getting code ready for PR or reviewing a PR. Unit tests are useful for small logic checks, but readiness should be judged with the smallest realistic workflow that proves the changed behavior works.
- For Apple automation changes, favor proof commands that exercise rendered workflows, adapter validation, Xcode inspection, `xcresult` parsing, simulator eligibility, or release validation rather than only isolated helper functions.
- Keep review scope tight: fix in-scope regressions introduced by the diff, and report broader cleanup or hardening as follow-up.

## Evidence

- Use privacy-safe summaries, hashes, counts, command classes, exit codes, and sterile fixture artifacts.
- Do not commit screenshots, logs, accessibility trees, device identifiers, paths, tokens, account content, or private adapter values that could identify a real app, device, user, or organization.
