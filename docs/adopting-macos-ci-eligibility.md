# Adopting the macOS CI Eligibility Lane

The macOS CI eligibility lane proves that an Apple app repo can consume Apple Agent Kit safely on a self-hosted Mac before that runner is trusted with heavier work.

This lane is intentionally smaller than CI. It validates the private adapter, renders reusable workflow templates into scratch space, checks Xcode readiness, and records a device-free assertion. It does not build, test, install, launch, screenshot, run WDA, run app smoke, or touch physical devices.

Use this lane before adding product CI, app smoke, UI automation, microphone QA, live transcription, or physical-device workflows.

## Public and Private Split

Keep these files public in Apple Agent Kit:

- `templates/github-actions/macos-ci-eligibility.yml`
- `scripts/aak.py`
- `docs/adopting-macos-ci-eligibility.md`
- `docs/private-adapter-rollout-checklist.md`
- sanitized proof records, such as `docs/proof-records/foil-macos-ci-eligibility-2026-06-25.md`

Keep these values private in the app repo or repository secrets:

- `.apple-agent-kit.json`
- project, scheme, bundle, signing, secret, device, and host details
- workflow run logs that expose host names or usernames

For private app repositories, committing `.apple-agent-kit.json` may be acceptable.

For public app repositories, keep the adapter in a secret such as `APPLE_AGENT_KIT_ADAPTER_JSON` and materialize it inside the workflow workspace. The installed workflow may be public, but its visible `runs-on` labels must be intentionally non-sensitive.

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

## Adoption Steps for a Private App Repo

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

## Adoption Steps for a Public App Repo

Use this path when the app repo is public but repo-specific adapter values should stay private.

1. Create a branch in the app repo.
2. Store the adapter in a repository secret:

```bash
gh secret set APPLE_AGENT_KIT_ADAPTER_JSON --repo OWNER/REPO < .apple-agent-kit.json
```

3. Confirm the secret exists without printing its value:

```bash
gh secret list --repo OWNER/REPO | rg '^APPLE_AGENT_KIT_ADAPTER_JSON\b'
```

4. Add a public workflow file at `.github/workflows/macos-ci-eligibility.yml`.
5. Materialize the private adapter from the secret:

```yaml
- name: Materialize private adapter
  env:
    APPLE_AGENT_KIT_ADAPTER_JSON: ${{ secrets.APPLE_AGENT_KIT_ADAPTER_JSON }}
  run: |
    set -euo pipefail
    test -n "$APPLE_AGENT_KIT_ADAPTER_JSON"
    printf '%s' "$APPLE_AGENT_KIT_ADAPTER_JSON" > .apple-agent-kit.json
```

6. Bind the job to approved public runner labels:

```yaml
runs-on: [self-hosted, macOS, mac-mini-2, app-label]
```

7. Add a direct assertion for the dedicated binding:

```yaml
- name: Assert dedicated Mac binding
  run: |
    set -euo pipefail
    grep -F "runs-on: [self-hosted, macOS, mac-mini-2, app-label]" .github/workflows/macos-ci-eligibility.yml
```

8. Validate and render with a local copy of the private adapter before opening the PR:

```bash
python3 path/to/apple-agent-kit/scripts/aak.py validate-adapter /tmp/app-adapter.json --json
python3 path/to/apple-agent-kit/scripts/aak.py render-workflows \
  --adapter /tmp/app-adapter.json \
  --output /tmp/aak-workflows \
  --force
```

9. Parse the workflow and run the forbidden-command scan.
10. Open a PR and let the repo's normal gates run.
11. After merge, dispatch `macos-ci-eligibility.yml` from the default branch.
12. Record a sanitized proof with the PR URL, workflow run URL, commit, visible runner labels, and explicit non-goals.

## Minimal Public Workflow Shape

This is the expected public-repo shape. Replace only the runner labels and repository owner/name values.

```yaml
name: Apple Agent Kit macOS CI Eligibility

on:
  pull_request:
    branches: [main]
    paths:
      - .github/workflows/macos-ci-eligibility.yml
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: macos-ci-eligibility-${{ github.head_ref || github.ref }}
  cancel-in-progress: true

jobs:
  eligibility:
    runs-on: [self-hosted, macOS, mac-mini-2, app-label]
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
      - name: Assert dedicated Mac binding
        run: |
          set -euo pipefail
          grep -F "runs-on: [self-hosted, macOS, mac-mini-2, app-label]" .github/workflows/macos-ci-eligibility.yml
      - name: Render reusable workflow templates
        run: |
          set -euo pipefail
          rm -rf artifacts/aak-render
          python3 .aak/apple-agent-kit/scripts/aak.py render-workflows \
            --adapter .apple-agent-kit.json \
            --output artifacts/aak-render \
            --force
      - name: Xcode readiness
        run: python3 .aak/apple-agent-kit/scripts/aak.py check-xcode --json
      - name: Device-free assertion
        run: |
          set -euo pipefail
          echo "No product build, product test, app install, WDA, screenshots, app launch, app smoke, UI smoke, microphone QA, live transcription, or physical-device smoke is run by this workflow."
```

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

For public-repo secret-backed workflows, also scan for accidental product commands:

```bash
rg -n "(make\\s+(build|test|test-app-smoke|test-ui)|open\\s+|osascript|xcodebuild\\s+(build|test))" \
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

For a public proof record, include:

- Public PR URL.
- Default-branch run URL.
- Merge commit or tested commit.
- Visible runner labels.
- Passed eligibility steps.
- Explicit list of things the workflow did not run.
- Statement that the adapter stayed in a secret and was not committed.
