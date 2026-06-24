---
name: ios-simulator-ci
description: Add or run iOS simulator build, unit test, and UI smoke automation.
---

# iOS Simulator CI

Use this skill for iOS simulator automation.

## Requirements

- Project or workspace path.
- App scheme.
- Test target or test plan.
- Simulator destination.
- Result bundle path.

## Pattern

1. Generate the Xcode project if the repo uses XcodeGen.
2. Resolve or boot the simulator through normal Xcode tooling.
3. Build the app for simulator.
4. Run unit tests with a result bundle.
5. Run UI smoke with a separate result bundle when possible.
6. Upload bundles and screenshots only when useful.

## Verification

Parse or inspect `xcresult` output. If UI smoke passes, still check that the expected test target actually ran.
