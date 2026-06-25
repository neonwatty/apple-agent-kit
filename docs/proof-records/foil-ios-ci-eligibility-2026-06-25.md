# Foil iOS CI Eligibility Proof - 2026-06-25

This record captures the first default-branch iOS proof that Apple Agent Kit can be used from a public app repository while keeping repo-specific adapter details private.

## What Was Proved

- A public iOS app repository can consume the public Apple Agent Kit from GitHub Actions.
- The app-specific adapter can stay out of git and be materialized from a repository secret.
- A hosted macOS runner can validate the iOS adapter, render reusable workflows, check Xcode readiness, and inspect simulator availability without running product or device automation.
- The same workflow can pass from the default branch after a normal PR, merge queue, and post-merge workflow dispatch path.

## Public Pieces

- Public kit repository: `neonwatty/apple-agent-kit`
- Public app repository: `usefoil/foil-ios`
- Public app PR: `https://github.com/usefoil/foil-ios/pull/73`
- Public workflow name: `Apple Agent Kit iOS CI Eligibility`
- Public workflow file path: `.github/workflows/ios-ci-eligibility.yml`
- Public runner label used by the workflow: `macos-15`

This proof used a GitHub-hosted macOS runner. It did not use a self-hosted Mac or a physical iPhone.

## Private Pieces

- The app adapter stayed private in `APPLE_AGENT_KIT_ADAPTER_JSON`.
- Project, scheme, bundle, UI target, signing, product smoke, and future device-specific values stayed in the adapter rather than in Apple Agent Kit.
- Full workflow logs should be treated as operational evidence, not copied into public docs, because logs can include local paths, usernames, and generated environment details.

## Proof Runs

PR proof:

- Run URL: `https://github.com/usefoil/foil-ios/actions/runs/28193642643`
- Trigger: `pull_request`
- Result: success
- Job: `eligibility`
- Duration: 1 minute

Merge queue proof:

- Run URL: `https://github.com/usefoil/foil-ios/actions/runs/28201125416`
- Trigger: `merge_group`
- Result: success
- Jobs: `Repo hygiene ratchet`, `Hosted simulator sanity`
- Note: this was an existing repository gate, separate from the new Apple Agent Kit eligibility workflow.

Default-branch proof:

- Run URL: `https://github.com/usefoil/foil-ios/actions/runs/28201431010`
- Trigger: `workflow_dispatch`
- Branch: `main`
- Commit: `1769eec77c06df25d0c223e63a46213730d02d27`
- Result: success
- Duration: 31 seconds

## Passed Steps

The default-branch proof completed these steps:

- Checked out the public app repo.
- Checked out `neonwatty/apple-agent-kit`.
- Materialized the private adapter from a GitHub secret.
- Validated the private adapter.
- Asserted the adapter was iOS-only.
- Rendered reusable workflow templates into scratch space.
- Checked Xcode readiness.
- Listed available iPhone simulators without booting, installing, launching, or capturing simulator output.
- Recorded the device-free assertion.

The default-branch proof log reported:

- `adapter platforms: ios`
- `"physical_device_actions": false`
- `"available_iPhone_simulators": 42`

## Explicit Non-Goals

This proof did not run:

- product build
- product test
- app install
- app launch
- app smoke
- UI smoke
- screenshots or screen recording
- simulator boot
- WDA or WebDriverAgent
- microphone QA
- live transcription
- physical-device smoke

The strongest realistic failure mode was that an iOS eligibility lane might accidentally start app, simulator, WDA, screenshot, or physical-device automation while proving adapter compatibility. The proof addressed that with direct workflow inspection, forbidden-command scans, and the workflow's own device-free assertion.

## Follow-Up

Use this proof as the reference for the public-repo/private-adapter iOS eligibility path. Keep heavier simulator CI, UI automation, and physical-device workflows behind separate approval gates.
