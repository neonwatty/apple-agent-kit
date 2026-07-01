# v0 Release Readiness

Apple Agent Kit v0 is ready when the public repo proves four things:

1. The source validates as a Codex plugin and a Claude Code plugin.
2. The dry-run CLI validates adapters, renders workflow templates, and inspects a repo without product or device automation.
3. Public docs explain install, reuse, private adapters, evidence, and proof records.
4. The public tree has no tracked filled adapters, private rollout boards, secrets, host details, or private device bindings.

## Local Proof

Run from the repo root:

```bash
python3 scripts/validate-release.py
python3 path/to/plugin-creator/scripts/validate_plugin.py .
claude plugin validate . --strict
python3 scripts/aak.py validate-adapter templates/adapter.example.json --json
python3 scripts/aak.py inspect --repo . --adapter templates/adapter.example.json --json
python3 scripts/aak.py render-workflows --adapter templates/adapter.example.json --output /tmp/aak-v0-render --force
test -f /tmp/aak-v0-render/macos-fixture-ui-smoke.yml
test -f /tmp/aak-v0-render/ios-simulator-fixture-ui-smoke.yml
python3 scripts/aak.py prepare-fixture-ui-smoke --adapter templates/adapter.example.json --script /tmp/aak-fixture-smoke.sh --approval fixture-ui-smoke --json
python3 scripts/aak.py prepare-fixture-ui-smoke --adapter templates/adapter.example.json --script /tmp/aak-ios-fixture-smoke.sh --approval fixture-ui-smoke --platform ios --json
bash templates/fixture-ui-smoke-command.example.sh
python3 scripts/aak.py validate-fixture-ui-smoke-receipt templates/fixture-ui-smoke.receipt.example.json --json
python3 scripts/aak.py validate-fixture-ui-smoke-receipt templates/ios-simulator-fixture-ui-smoke.receipt.example.json --json
git ls-files docs/goals
git diff --check
```

`git ls-files docs/goals` should print nothing. GoalBuddy boards and filled rollout notes are useful ignored working artifacts, but they should not be part of the public v0 plugin surface.

## Privacy Boundary

Allowed in this public repo:

- generic skills and checklists
- example adapter values under `example` names
- dry-run scripts and templates
- sanitized proof records
- validation commands and receipts

Not allowed in this public repo:

- private adapter JSON
- real bundle identifiers, signing teams, runner labels, hostnames, usernames, device names, or secret values
- product smoke profiles for a private app
- workflow logs that expose private paths or host metadata
- screenshots or raw accessibility trees from personal apps

## Release Decision

This v0 path is source-first. A tag, marketplace listing, or package-registry publish is a separate release action and should happen only after the validation suite passes on the release branch.
