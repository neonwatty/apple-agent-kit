# prcard Manual Remote PR Session Proof - 2026-06-29

## Summary

A manual GitHub `workflow_dispatch` for `prcard/prcard-mac` PR #2 asked the MacBook Air receiver to check out SHA `5c8629b9d0600399b98e9e2ad415bc07b8ac9716`, run the approved `macos-tests` profile with `make test`, create a private Codex session from operator instructions, and publish only a sanitized receipt.

## Result

- Date: 2026-06-29
- Repo: `prcard/prcard-mac`
- PR: `2`
- SHA: `5c8629b9d0600399b98e9e2ad415bc07b8ac9716`
- GitHub workflow run: `28384369309`
- Request id: `mprs-28384369309-1`
- Host profile alias: `macbook-air`
- Run profile: `macos-tests`
- Command expectation: `make test` through the private `macos-tests` profile; the public workflow does not accept raw command input.
- Result: succeeded
- Codex session created: true
- Operator resume proof: private readiness response `PRCARD_DOGFOOD_READY`
- Physical device requested: false
- Physical device gate: disabled

## Sanitization

The public PR receipt/comment leak scan passed for raw prompt phrase, local home paths, raw command text, stdout/stderr markers, token-like strings, and device-id-like strings.

This proof record intentionally omits raw prompt text, raw logs, local paths, usernames, hostnames, tokens, serials, UDIDs, and private device identifiers.

## Notes

Full workflow logs and private receiver state remain operational evidence and are not copied into this public proof record.
