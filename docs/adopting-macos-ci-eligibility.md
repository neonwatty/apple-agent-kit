# Adopting the macOS CI Eligibility Lane

The macOS CI eligibility lane proves that a private Apple app repo can consume Apple Agent Kit safely on a self-hosted Mac before that runner is trusted with heavier work.

This lane is intentionally smaller than CI. It validates the private adapter, renders reusable workflow templates into scratch space, checks Xcode readiness, and records a device-free assertion. It does not build, test, install, launch, screenshot, run WDA, run app smoke, or touch physical devices.

## Public and Private Split

Keep these files public in Apple Agent Kit:

- `templates/github-actions/macos-ci-eligibility.yml`
- `scripts/aak.py`
- `docs/adopting-macos-ci-eligibility.md`
- `docs/private-adapter-rollout-checklist.md`

Keep these files private in the app repo:

- `.apple-agent-kit.json`
- installed `.github/workflows/macos-ci-eligibility.yml`
- runner labels
- project, scheme, bundle, signing, secret, device, and host details
- workflow run logs that expose host names or usernames

## Required Private Adapter Fields

The adapter must include:

```json
{
  "name": "private-app-preview",
  "platforms": {
    "macos": {
      "project": "App.xcodeproj",
      "scheme": "App",
      "destination": "platform=macOS",
      "derivedDataPath": "build",
      "appSmokeCommand": "make app-smoke"
    }
  },
  "ci": {
    "macosRunner": "macos-15",
    "macosRunnerLabels": ["self-hosted", "macOS", "private-runner-label"]
  },
  "privacy": {
    "screenshots": "sterile-only",
    "rawAccessibilityTrees": false,
    "redactSecrets": true
  }
}
```

The eligibility workflow only uses `ci.macosRunnerLabels`, but the platform fields make the adapter useful for later lanes and keep validation honest.

## Adoption Steps

1. Create a private branch in the app repo.
2. Add or update `.apple-agent-kit.json` with repo-specific values.
3. Validate the adapter:

```bash
python3 path/to/apple-agent-kit/scripts/aak.py validate-adapter .apple-agent-kit.json --json
```

4. Render workflows into scratch space:

```bash
python3 path/to/apple-agent-kit/scripts/aak.py render-workflows \
  --adapter .apple-agent-kit.json \
  --output /tmp/aak-workflows \
  --force
```

5. Review `/tmp/aak-workflows/macos-ci-eligibility.yml`.
6. Copy the reviewed workflow to `.github/workflows/macos-ci-eligibility.yml`.
7. Add a private assertion when useful, such as checking the dedicated runner label in the installed workflow.
8. Open a private PR and let existing repo gates run.
9. After merge, dispatch `macos-ci-eligibility.yml` from the default branch.
10. Record the PR URL, workflow run URL, and sanitized pass/fail result.

## Safety Boundary

This lane must not run:

- product build or product test
- app install or app launch
- host app automation
- UI smoke or app smoke
- screenshots or screen recording
- WDA or WebDriverAgent
- `simctl install`, `simctl launch`, `simctl io`, or screenshot commands
- `devicectl`, `xcdevice`, `ios-deploy`, or physical-device commands

Use a direct scan before opening the private PR:

```bash
rg -n "(xcodebuild\\s+(build|test)|simctl\\s+(install|launch|io|screenshot)|devicectl|xcdevice|ios-deploy|WebDriverAgent)" \
  .github/workflows/macos-ci-eligibility.yml
```

The expected result is no matches.

## Proof Checklist

Before calling the rollout complete, collect proof that tries to disprove the change:

- Adapter validation passed.
- Render receipt reports `"physical_device_actions": false`.
- Installed workflow YAML parses.
- Installed workflow uses the expected self-hosted Mac labels.
- Forbidden-command scan has no matches.
- Private PR merged through normal repo gates.
- Default-branch `workflow_dispatch` run completed successfully.
- Final handoff does not expose host names, usernames, secrets, signing details, device names, or private labels beyond what the user has approved.

