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

This repo is at design scaffold stage. The first implementation milestone is to add generic validation and dry-run commands before any physical runner or iPhone workflow is exercised.
