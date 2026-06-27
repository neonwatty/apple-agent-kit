# Foil macOS CI Eligibility Proof - 2026-06-25

This record captures the first default-branch proof that Apple Agent Kit can be used from a public app repository while keeping repo-specific adapter details private.

## What Was Proved

- A public app repository can consume the public Apple Agent Kit from GitHub Actions.
- The app-specific adapter can stay out of git and be materialized from a repository secret.
- A dedicated self-hosted Mac runner can be selected with visible, intentional labels.
- The macOS CI eligibility lane can validate the adapter, render reusable workflows, and check Xcode readiness without running product or device automation.
- The same workflow can pass from the default branch after a normal PR and merge queue path.

## Public Pieces

- Public kit repository: `neonwatty/apple-agent-kit`
- Public app repository: `usefoil/foil`
- Public app PR: `https://github.com/usefoil/foil/pull/326`
- Public workflow name: `Apple Agent Kit macOS CI Eligibility`
- Public workflow file path: `.github/workflows/macos-ci-eligibility.yml`
- Public runner labels used by the workflow: dedicated self-hosted macOS labels, redacted from this public proof record.

These labels are intentionally visible because GitHub Actions `runs-on` values in public repositories are public workflow content.

## Private Pieces

- The app adapter stayed private in `APPLE_AGENT_KIT_ADAPTER_JSON`.
- Project, scheme, signing, bundle, product smoke, and any future device-specific values stayed in the adapter rather than in Apple Agent Kit.
- Full workflow logs should be treated as operational evidence, not copied into public docs, because self-hosted runner logs can include host paths, usernames, and machine names.

## Proof Runs

PR proof:

- Run URL: `https://github.com/usefoil/foil/actions/runs/28179518448`
- Trigger: `pull_request`
- Result: success
- Job: `eligibility`

Default-branch proof:

- Run URL: `https://github.com/usefoil/foil/actions/runs/28190536072`
- Trigger: `workflow_dispatch`
- Branch: `main`
- Commit: `6ca2bece90c5b69b835682ceb68a952014be9b6b`
- Result: success
- Duration: 19 seconds
- Runner name observed in GitHub Actions: redacted dedicated Mac runner.

## Passed Steps

The default-branch proof completed these steps:

- Checked out the public app repo.
- Checked out `neonwatty/apple-agent-kit`.
- Materialized the private adapter from a GitHub secret.
- Validated the private adapter.
- Asserted the dedicated Mac runner binding.
- Rendered reusable workflow templates into scratch space.
- Checked Xcode readiness.
- Recorded the device-free assertion.

## Explicit Non-Goals

This proof did not run:

- product build
- product test
- app install
- app launch
- app smoke
- UI smoke
- screenshots or screen recording
- WDA or WebDriverAgent
- microphone QA
- live transcription
- physical-device smoke

The strongest realistic failure mode was that the eligibility lane might accidentally run product or device automation. The proof addressed that with direct workflow inspection, forbidden-command scans, and the workflow's own device-free assertion.

## Follow-Up

Use this proof as the reference for the public-repo/private-adapter adoption path in `docs/adopting-macos-ci-eligibility.md`.
