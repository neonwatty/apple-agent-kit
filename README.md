# Apple Agent Kit

Apple Agent Kit is an open-source Codex plugin and agent playbook collection for proof-driven macOS and iOS automation.

The public kit contains reusable patterns only: skills, scripts, templates, receipt formats, and privacy-safe evidence rules. App-specific details such as bundle identifiers, schemes, device names, signing teams, runner labels, secret names, and product smoke profiles belong in private adapters.

## Goals

- Help coding agents set up reliable Xcode build, test, smoke, and release checks.
- Make self-hosted Mac runner and physical iPhone automation repeatable.
- Capture evidence that can be audited after the run.
- Keep private product details out of the public plugin.
- Support Codex first while keeping the content easy to reuse from Claude Code.

## Repository Shape

- `.codex-plugin/plugin.json` - Codex plugin manifest.
- `skills/` - Agent-facing playbooks.
- `docs/` - Design, adapter contract, evidence policy, and operating notes.
- `scripts/` - Generic helper scripts that must not contain app-specific values.
- `templates/` - Reusable workflow and config templates.

## v0 Commands

The v0 command surface is dependency-free Python and dry-run oriented:

```bash
python3 scripts/aak.py inspect --repo . --adapter templates/adapter.example.json --json
python3 scripts/aak.py validate-adapter templates/adapter.example.json
python3 scripts/aak.py render-workflows --adapter templates/adapter.example.json --output /tmp/aak-render --force
python3 scripts/aak.py check-xcode --json
python3 scripts/aak.py summarize-xcresult path/to/TestResults.xcresult --json
```

These commands do not install apps, boot simulators, start WDA, launch host apps, dispatch CI workflows, or touch physical devices.

The rendered workflow set includes device-free eligibility templates:

- `macos-runner-health.yml` checks a specific Mac runner on demand.
- `macos-ci-eligibility.yml` validates a private adapter, renders reusable workflows into scratch space, and checks Xcode readiness without building or testing the product.
- `ios-ci-eligibility.yml` validates a private iOS adapter, renders reusable workflows into scratch space, checks Xcode readiness, and inventories simulators without building, testing, booting, installing, launching, screenshotting, or touching physical devices.

Bind the self-hosted Mac lanes with private `ci.macosRunnerLabels`; keep physical iPhone workflows behind a separate approval gate.

See [Adopting the macOS CI Eligibility Lane](docs/adopting-macos-ci-eligibility.md), [Adopting the iOS CI Eligibility Lane](docs/adopting-ios-ci-eligibility.md), [Self-Hosted Runner Scope and Onboarding](docs/self-hosted-runner-scope-onboarding.md), and the [Private Adapter Rollout Checklist](docs/private-adapter-rollout-checklist.md) for a repeatable public/private adoption path. Public proof records include [Foil macOS CI Eligibility Proof - 2026-06-25](docs/proof-records/foil-macos-ci-eligibility-2026-06-25.md) and [Foil iOS CI Eligibility Proof - 2026-06-25](docs/proof-records/foil-ios-ci-eligibility-2026-06-25.md).

## Private Adapters

Private adapters provide concrete values for a repo:

- project or workspace path
- scheme names
- bundle identifiers
- UI test targets
- runner labels
- device names
- signing and secret variable names
- allowed screenshot/evidence policy

See [docs/adapter-contract.md](docs/adapter-contract.md).

## Status

This repo is at v0 dry-run stage. Physical runner and iPhone workflows should be validated only through private adapters and explicit operator approval.
