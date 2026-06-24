---
name: ios-physical-device
description: Prepare and run privacy-aware physical iPhone automation with Xcode, WDA/Appium, or XCTest UI tests.
---

# iOS Physical Device

Use this skill for physical iPhone automation.

## Hard Boundary

Do not install apps, start WDA, launch host apps, or take screenshots without explicit user approval for the target device and adapter.

## Preflight

Check:

- Xcode version
- `xcrun devicectl` availability
- device visibility
- device lock/readiness state
- signing keychain and identity availability
- Automation Mode readiness
- privacy policy in the adapter

## Pattern

1. Resolve the device by adapter-provided name.
2. Fail fast if the device is locked or not launch-ready.
3. Build with explicit destination and derived data path.
4. Verify the built bundle identifier before installing.
5. Install or test only the expected app.
6. Capture artifacts according to the privacy policy.
7. Emit a receipt.

## Automation Mode

If Xcode times out while enabling Automation Mode, retry only within the adapter-configured limit and surface a clear operator action. Do not loop indefinitely.
