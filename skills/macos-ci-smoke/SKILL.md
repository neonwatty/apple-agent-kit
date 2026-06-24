---
name: macos-ci-smoke
description: Add or run proof-driven macOS build, test, coverage, and app-smoke automation for an Apple app repository.
---

# macOS CI Smoke

Use this skill for macOS app automation.

## Requirements

- A project or workspace path.
- A scheme.
- A macOS destination, usually `platform=macOS`.
- A test command that writes an `xcresult` bundle.
- An app smoke command or a clear reason it is out of scope.

## Pattern

1. Build with warnings treated as errors when the repo supports it.
2. Run tests with `-resultBundlePath`.
3. Parse the result bundle before trusting the command exit status.
4. Generate or summarize coverage when enabled.
5. Run an app smoke that launches the built app directly when possible.
6. Upload `xcresult` and logs on failure in CI.

## Verification

Before declaring success, inspect the result bundle or the generated summary and name the strongest realistic failure mode that was checked.
