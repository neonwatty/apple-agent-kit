---
name: macos-runner-health
description: Preflight and clean up self-hosted GUI macOS runners used by agents or CI workflows.
---

# macOS Runner Health

Use this skill for self-hosted Mac runners, especially GUI runners.

## Preflight

Check:

- host identity and macOS version
- architecture
- Xcode version
- runner working directory safety
- stale app or `xcodebuild` processes
- keychain availability when signing is required
- GUI/session assumptions for UI automation

## Cleanup

Cleanup must be conservative:

- kill only known automation processes
- remove only known derived data or artifact directories
- refuse to delete unexpected workspace paths
- run a post-cleanup healthcheck

## Verification

Record host proof and cleanup proof in a receipt. Do not claim a runner is healthy based only on a successful command if the command did not check the risky condition.
