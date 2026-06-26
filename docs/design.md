# Apple Agent Kit Design

## Boundary

Apple Agent Kit is public and generic. It provides automation routines and agent instructions for Apple app repositories without encoding private app or infrastructure details.

Private adapters live outside this repo. They bind the public routines to a product by supplying paths, schemes, bundle identifiers, runner labels, device names, signing values, smoke profiles, and secret names.

## Architecture

The kit has four layers:

1. Skills: Codex-facing instructions that tell agents how to inspect, plan, run, verify, and hand off Apple automation work.
2. Scripts: Generic shell or Python helpers for Xcode environment inspection, result-bundle parsing, runner preflight, and evidence validation.
3. Templates: GitHub Actions, Makefile, adapter, and receipt templates.
4. Adapter contract: A small repo-local configuration file that maps generic concepts to private app values.

The v0 command entrypoint is `scripts/aak.py`. It is intentionally dependency-free and dry-run oriented:

- `inspect`
- `validate-adapter`
- `render-workflows`
- `check-xcode`
- `summarize-xcresult`

The device-free self-hosted Mac runner-health and macOS eligibility templates render from `ci.macosRunnerLabels`. The iOS eligibility template defaults to a hosted macOS runner from `ci.macosRunner` and keeps simulator inventory read-only. Keep these separate from physical iOS runner labels so an eligibility check does not imply install, WDA, screenshots, app launch, UI smoke, simulator boot, or physical-device smoke.

## Initial Skill Set

- `apple-agent-intake`: inspect an Apple repo and choose relevant automation tracks.
- `macos-ci-smoke`: build, test, coverage, and app-smoke patterns for macOS apps.
- `macos-runner-health`: self-hosted GUI runner preflight and cleanup.
- `ios-simulator-ci`: simulator build, test, and UI smoke checks.
- `ios-physical-device`: physical iPhone preflight, install, WDA/Appium readiness, and UI smoke.
- `xcresult-proof`: parse `xcresult` bundles, summarize failures, coverage, and artifacts.
- `privacy-safe-evidence`: enforce evidence redaction and screenshot boundaries.

## Adapter Model

The public kit reads a repo-local adapter file and validates that required values exist before running commands. The adapter is the only place that should name a product, a real device, a runner label, a team ID, or a secret.

The kit supports dry runs first. Commands that touch physical devices, install apps, start WDA, dispatch self-hosted workflows, or interact with host apps require explicit user approval in the calling workflow and are out of scope for v0.

## Evidence Model

Every non-trivial automation run should emit a receipt. A receipt should include:

- timestamp
- host and Xcode summary
- adapter name and non-secret config summary
- command class
- result bundle path, if any
- artifact paths
- pass/fail classification
- strongest attempted disproof
- privacy assertions

Receipts must not include API keys, tokens, phone numbers, private message text, private URLs, raw accessibility trees from personal apps, or screenshots unless the adapter policy explicitly allows them.

## Validation Targets

The expected private validation path is:

1. Dry run against a sample repo.
2. macOS CI smoke on a sample Mac app.
3. iOS simulator smoke on a sample iOS app.
4. Self-hosted Mac runner preflight on a LAN Mac Mini, with no physical-device actions.
5. Physical iPhone smoke on a preview device, only after separate approval.
6. Audit generated receipts for usefulness and leakage.
