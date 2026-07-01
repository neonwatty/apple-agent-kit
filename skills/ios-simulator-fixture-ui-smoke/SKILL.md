---
name: ios-simulator-fixture-ui-smoke
description: Add or run privacy-safe iOS simulator fixture UI smoke automation for Apple app repositories. Use when an iOS repo is ready to move beyond dry-run eligibility into deterministic simulator GUI smoke using a sterile fixture app, demo mode, XCTest UI test, result bundle, sanitized logs, or scripted simulator checks.
---

# iOS Simulator Fixture UI Smoke

Use this skill when iOS automation should prove GUI behavior on a simulator without touching personal devices, private accounts, production data, or physical-device surfaces.

## Requirements

- A private adapter with `platforms.ios.simulatorDestination`.
- A private adapter with an `automation` block.
- A sterile fixture app, demo mode, or test-only simulator surface.
- A fixture smoke command owned by the private repo.
- A receipt path and artifact policy.

## Pattern

1. Validate the adapter and check the configured simulator destination with `check-xcode --adapter <adapter> --platform ios --require-simulator-destination --json`.
2. Prepare the fixture command with `--platform ios`.
3. Confirm the fixture target is not a live app/account surface.
4. Use the adapter-provided simulator destination and avoid physical-device commands.
5. Build, install, launch, or test only the fixture app or demo mode named by the adapter.
6. Prefer XCTest UI tests, stable accessibility identifiers, or deterministic simulator commands over natural-language agent flows.
7. Collect bounded evidence: result bundle paths, sanitized command summaries, fixture log counts, hashes, and sterile screenshots only when allowed.
8. Write a fixture UI smoke receipt with `adapter.platform` set to `ios`.

## Verification

Before declaring success, try to disprove the smoke:

- Confirm the simulator destination came from the adapter.
- Confirm `check-xcode --adapter <adapter> --platform ios --require-simulator-destination --json` matched the configured simulator destination without requiring a boot.
- Confirm the expected fixture bundle identifier or demo mode was the target.
- Confirm at least one expected UI event appeared in logs or the result bundle.
- Confirm no personal screenshots, raw private accessibility trees, private URLs, UDIDs, or unredacted identifiers were captured.
- Confirm the receipt states what did not run, including physical-device actions and non-fixture app automation.

Do not promote simulator fixture smoke into physical-device automation until the receipt is repeatable and privacy-safe.
