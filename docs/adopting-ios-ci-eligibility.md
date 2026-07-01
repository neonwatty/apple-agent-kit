# Adopting the iOS CI Eligibility Lane

The iOS CI eligibility lane proves that an iOS app repo can consume Apple Agent Kit safely before the repo is trusted with heavier simulator or physical-device automation.

This lane is intentionally smaller than CI. It validates a private iOS adapter, renders reusable workflow templates into scratch space, checks Xcode readiness, inventories available iPhone simulators, and records a device-free assertion. It does not build, test, install, launch, boot simulators, screenshot, run WDA, run app smoke, run UI smoke, or touch physical devices.

Use this lane before adding simulator builds, simulator tests, UI automation, microphone QA, live transcription, or physical-device workflows.

## Public and Private Split

Keep these files public in Apple Agent Kit:

- `templates/github-actions/ios-ci-eligibility.yml`
- `scripts/aak.py`
- `docs/adopting-ios-ci-eligibility.md`
- `docs/private-adapter-rollout-checklist.md`
- sanitized proof records, such as `docs/proof-records/foil-ios-ci-eligibility-2026-06-25.md`

Keep these values private in the app repo or repository secrets:

- `.apple-agent-kit.json`
- project, scheme, bundle, signing, secret, UI target, device, and host details
- workflow run logs that expose paths, usernames, host names, or generated environment details

For public app repositories, keep the adapter in `APPLE_AGENT_KIT_ADAPTER_JSON` and materialize it inside the workflow workspace. The installed workflow may be public, but the adapter body must not be committed.

For private app repositories, committing `.apple-agent-kit.json` may be acceptable, but the public template still works with a repository secret and keeps the lane shape consistent.

## Required Private Adapter Fields

The adapter must include an iOS platform entry:

```json
{
  "name": "private-ios-preview",
  "platforms": {
    "ios": {
      "project": "App.xcodeproj",
      "scheme": "App",
      "uiScheme": "App",
      "uiTestTarget": "AppUITests",
      "simulatorDestination": "platform=iOS Simulator,name=iPhone 16",
      "bundleIdentifier": "com.example.app"
    }
  },
  "ci": {
    "macosRunner": "macos-15",
    "macosRunnerLabels": ["not-used-by-hosted-ios-eligibility"],
    "physicalRunnerLabels": ["not-used-by-device-free-eligibility"]
  },
  "privacy": {
    "screenshots": "sterile-only",
    "rawAccessibilityTrees": false,
    "redactSecrets": true
  }
}
```

The eligibility workflow only uses the adapter for validation, rendering, and iOS-only shape checks. The platform fields make the adapter useful for later simulator and physical-device lanes while keeping those heavier actions out of this proof.

## Adoption Steps for a Public App Repo

1. Create a branch in the app repo.
2. Store the private adapter in a repository secret:

```bash
gh secret set APPLE_AGENT_KIT_ADAPTER_JSON --repo OWNER/REPO < .apple-agent-kit.json
```

3. Confirm the secret exists without printing its value:

```bash
gh secret list --repo OWNER/REPO | rg '^APPLE_AGENT_KIT_ADAPTER_JSON\b'
```

4. Render workflows from a local copy of the private adapter:

```bash
python3 path/to/apple-agent-kit/scripts/aak.py render-workflows \
  --adapter /tmp/app-adapter.json \
  --output /tmp/aak-workflows \
  --force
```

5. Review `/tmp/aak-workflows/ios-ci-eligibility.yml`.
6. Copy the reviewed workflow to `.github/workflows/ios-ci-eligibility.yml`.
7. Parse the workflow and run the forbidden-command scans.
8. Open a PR and let the repo's normal gates run.
9. After merge, dispatch `ios-ci-eligibility.yml` from the default branch.
10. Record a sanitized proof with the PR URL, workflow run URL, tested commit, passed steps, and explicit non-goals.

## Minimal Public Workflow Shape

This is the expected public-repo shape. Replace only repository owner/name values if using a fork of Apple Agent Kit.

```yaml
name: Apple Agent Kit iOS CI Eligibility

on:
  pull_request:
    branches: [main]
    paths:
      - .github/workflows/ios-ci-eligibility.yml
  workflow_dispatch:

permissions:
  contents: read

jobs:
  eligibility:
    runs-on: macos-15
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v6
      - name: Checkout Apple Agent Kit
        uses: actions/checkout@v6
        with:
          repository: neonwatty/apple-agent-kit
          ref: main
          path: .aak/apple-agent-kit
      - name: Materialize private adapter
        env:
          APPLE_AGENT_KIT_ADAPTER_JSON: ${{ secrets.APPLE_AGENT_KIT_ADAPTER_JSON }}
        run: |
          set -euo pipefail
          test -n "$APPLE_AGENT_KIT_ADAPTER_JSON"
          printf '%s' "$APPLE_AGENT_KIT_ADAPTER_JSON" > .apple-agent-kit.json
      - name: Validate private adapter
        run: python3 .aak/apple-agent-kit/scripts/aak.py validate-adapter .apple-agent-kit.json --json
      - name: Assert iOS-only adapter shape
        run: |
          set -euo pipefail
          python3 <<'PY'
          import json

          with open(".apple-agent-kit.json", encoding="utf-8") as handle:
              adapter = json.load(handle)
          platforms = set((adapter.get("platforms") or {}).keys())
          if platforms != {"ios"}:
              raise SystemExit(f"expected iOS-only adapter, got: {sorted(platforms)}")
          print("adapter platforms: ios")
          PY
      - name: Render reusable workflow templates
        run: |
          set -euo pipefail
          rm -rf artifacts/aak-render
          python3 .aak/apple-agent-kit/scripts/aak.py render-workflows \
            --adapter .apple-agent-kit.json \
            --output artifacts/aak-render \
            --force
      - name: Xcode readiness
        run: python3 .aak/apple-agent-kit/scripts/aak.py check-xcode --adapter .apple-agent-kit.json --platform ios --json
      - name: Device-free assertion
        run: |
          set -euo pipefail
          echo "No product build, product test, app install, WDA, screenshots, app launch, app smoke, UI smoke, microphone QA, live transcription, simulator boot, or physical-device smoke is run by this workflow."
```

## Safety Boundary

This lane must not run:

- product build or product test
- app install or app launch
- simulator boot
- host app automation
- UI smoke or app smoke
- screenshots or screen recording
- WDA or WebDriverAgent
- `simctl boot`, `simctl install`, `simctl launch`, `simctl io`, or screenshot commands
- `devicectl`, `xcdevice`, `ios-deploy`, or physical-device commands

Use a direct scan before opening the PR:

```bash
rg -n "(xcodebuild\\s+(build|test)|simctl\\s+(boot|install|launch|io|screenshot)|devicectl|xcdevice|ios-deploy|WebDriverAgent)" \
  .github/workflows/ios-ci-eligibility.yml
```

The expected result is no matches.

For public-repo secret-backed workflows, also scan for accidental product commands:

```bash
rg -n "(make\\s+(build|test|test-app-smoke|test-ui)|open\\s+|osascript|xcodebuild\\s+(build|test))" \
  .github/workflows/ios-ci-eligibility.yml
```

The expected result is no matches.

## Proof Checklist

Before calling the rollout complete, collect proof that tries to disprove the change:

- Adapter validation passed.
- Xcode readiness reported privacy-safe simulator destination eligibility.
- Render receipt reports `"physical_device_actions": false`.
- Installed workflow YAML parses.
- Installed workflow asserts the iOS-only adapter shape.
- Forbidden-command scan has no matches.
- Private PR merged through normal repo gates.
- Default-branch `workflow_dispatch` run completed successfully.
- Final handoff does not expose secrets, signing details, bundle IDs, private labels, device names, host names, or usernames beyond what the user has approved.

For a public proof record, include:

- Public PR URL.
- Default-branch run URL.
- Merge commit or tested commit.
- Public runner label or hosted runner image.
- Passed eligibility steps.
- Explicit list of things the workflow did not run.
- Statement that the adapter stayed in a secret and was not committed.
