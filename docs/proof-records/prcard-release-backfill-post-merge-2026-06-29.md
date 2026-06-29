# prcard Release Backfill Post-Merge Proof - 2026-06-29

## Summary

`prcard/prcard-mac` PR #2 was merged through the repository merge queue after the Manual Remote PR Session dogfood run succeeded. The post-merge CI and Release workflows completed successfully, and the release artifact backfill guard confirmed that the latest release already had the expected macOS artifact.

## Merge

- Repo: `prcard/prcard-mac`
- PR: `2`
- PR title: `Fix macOS release artifact backfill`
- Tested PR SHA before merge: `5c8629b9d0600399b98e9e2ad415bc07b8ac9716`
- Merge commit: `7664cda1231306316216b9a331abaf7603e87959`
- Merged at: `2026-06-29T16:37:00Z`

## Post-Merge Workflows

- Merge queue CI run: `28387534322`, result: success
- Auto-merge run: `28387648958`, result: success
- Push CI run: `28387670822`, result: success
- Release run: `28387670827`, result: success

## Release Artifact State

- Latest release: `v1.0.0`
- macOS artifact: `PRcardMac-macOS.zip`, state: uploaded
- checksum artifact: `PRcardMac-macOS.zip.sha256`, state: uploaded
- Release Artifact workflow did not need a new dispatch after PR #2 merged because the Release workflow detected that the latest release already had the macOS zip.

## Sanitization

This proof record intentionally omits raw workflow logs, local paths, usernames, hostnames, tokens, device identifiers, signing details, and private command text.
