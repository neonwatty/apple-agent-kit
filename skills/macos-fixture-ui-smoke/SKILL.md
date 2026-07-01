---
name: macos-fixture-ui-smoke
description: Add or run privacy-safe macOS fixture UI smoke automation for Apple app repositories. Use when a repo is ready to move beyond dry-run eligibility into deterministic GUI smoke using a sterile fixture app, demo mode, OSLog evidence, sanitized screenshots, or scripted click/type/menu/window/dialog checks.
---

# macOS Fixture UI Smoke

Use this skill when macOS automation should prove GUI behavior without touching personal apps, private accounts, or production data.

## Requirements

- A private adapter with an `automation` block.
- A sterile fixture app, demo mode, or test-only surface.
- A fixture smoke command owned by the private repo.
- A log source such as OSLog subsystem/category, structured app logs, or XCTest attachments.
- A receipt path and artifact policy.

## Pattern

1. Validate the adapter and confirm `privacy.screenshots` allows sterile fixture captures before collecting images.
2. Confirm the fixture target is not a personal app or live account.
3. Run a GUI-session preflight: active Aqua session, Screen Recording when screenshots are needed, Accessibility for UI actions, and Event Synthesizing only when the smoke requires background input.
4. Build or launch only the fixture app or demo mode named by the adapter.
5. Run the fixture smoke command from the private repo. Prefer stable accessibility identifiers, scripted commands, or XCTest UI tests over natural-language agent flows.
6. Collect bounded evidence: result bundle paths, sanitized command output, OSLog excerpts for the fixture subsystem, sterile screenshots only when allowed, and hashes/counts for sensitive objects.
7. Write a fixture UI smoke receipt. Use `templates/fixture-ui-smoke.receipt.example.json` as the public shape.

## Verification

Before declaring success, try to disprove the smoke:

- Confirm the expected fixture bundle identifier or demo mode was the target.
- Confirm at least one expected UI event appeared in logs or the result bundle.
- Confirm no personal screenshots, raw private accessibility trees, private URLs, or unredacted identifiers were captured.
- Confirm negative paths are represented when practical, such as disabled controls, missing element IDs, invalid inputs, or stale snapshots.
- Confirm the receipt states what did not run, including physical-device actions and non-fixture app automation.

Do not promote fixture smoke into general desktop automation until the fixture receipt is repeatable and privacy-safe.
