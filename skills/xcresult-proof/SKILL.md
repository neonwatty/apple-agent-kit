---
name: xcresult-proof
description: Inspect Xcode result bundles and produce auditable test, failure, coverage, and artifact summaries.
---

# xcresult Proof

Use this skill whenever a workflow produces an `xcresult` bundle.

## Checks

- Confirm the bundle exists.
- Use `xcrun xcresulttool get test-results summary` when available.
- Use `xcrun xccov view --report` for coverage when coverage is enabled.
- Summarize failures before logs.
- Upload the bundle on CI failure.

## Burden Of Proof

Treat a successful `xcodebuild` exit as a claim. Verify the result bundle or explain why no bundle exists.

## Output

Return:

- bundle path
- pass/fail classification
- failing tests, if any
- coverage summary, if available
- artifact paths
- residual risk
