---
name: apple-agent-intake
description: Inspect an Apple app repository and recommend macOS/iOS automation setup before editing workflows or scripts.
---

# Apple Agent Intake

Use this skill before adding Apple Agent Kit automation to a repository.

## Steps

1. Inspect the repository shape:
   - Xcode project or workspace files
   - `project.yml` or XcodeGen usage
   - `Makefile`
   - `scripts/`
   - `.github/workflows/`
   - existing test targets and UI test targets
2. Identify platforms:
   - macOS app
   - iOS simulator app
   - iOS physical-device app
   - release/TestFlight/notarization workflows
3. Look for existing proof assets:
   - `*.xcresult` handling
   - coverage reporting
   - screenshot artifacts
   - runner preflight scripts
   - privacy or evidence docs
4. Recommend the smallest next automation track.

## Output

Give a short report with:

- detected platforms
- relevant existing commands
- missing adapter values
- recommended first track
- verification command to disprove the setup

Do not touch physical devices or self-hosted runners during intake.
