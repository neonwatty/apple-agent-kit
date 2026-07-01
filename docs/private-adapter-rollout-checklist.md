# Private Adapter Rollout Checklist

Use this checklist when applying Apple Agent Kit to a private Apple app repo. Keep the filled copy private if it contains repo-specific values.

## Scope

- Repo:
- Platform: macOS / iOS / both
- Lane: runner health / macOS CI eligibility / iOS CI eligibility / fixture UI smoke / simulator CI / physical device
- Approved hardware binding:
- Explicit exclusions:
- Dedicated runner-health checklist, if applicable:

## Public Kit Baseline

- Apple Agent Kit branch or commit:
- Template used:
- Public docs reviewed:
- Public changes needed before private rollout:

## Private Adapter

- `.apple-agent-kit.json` added or updated.
- Project/workspace path is correct.
- Scheme names are correct.
- Runner labels are private and specific.
- Physical device labels stay separate from Mac runner labels.
- Secrets and signing values are not committed.
- Fixture UI smoke fields are present when the lane needs GUI evidence:
  - `automation.fixtureBundleIdentifier`
  - `automation.fixtureSmokeCommand`
  - `automation.logSubsystem`
  - `automation.allowedEvidence`
  - `automation.fixtureReceiptPath`
  - `automation.allowedArtifactGlobs`
- Privacy policy is present:
  - `redactSecrets`
  - `rawAccessibilityTrees`
  - screenshot policy

## Local Verification

Run from the private repo:

```bash
python3 path/to/apple-agent-kit/scripts/aak.py validate-adapter .apple-agent-kit.json --json
python3 path/to/apple-agent-kit/scripts/aak.py render-workflows --adapter .apple-agent-kit.json --output /tmp/aak-workflows --force
```

Record:

- Adapter validation result:
- Render receipt path:
- Render receipt reports `"physical_device_actions": false`:
- Installed workflow YAML parse result:
- Forbidden-command scan result:
- Fixture UI smoke receipt path, if applicable:
- Fixture target is sterile and not a personal app:
- Fixture log evidence has bounded time window and sanitized content:

## Private PR

- Branch:
- PR URL:
- Files changed:
- Existing repo gates:
- New Apple Agent Kit gate:
- Merge method:
- Merge commit:

## Default Branch Proof

- Workflow dispatched from default branch:
- Run URL:
- Conclusion:
- Relevant passed steps:
- Sanitized notes:
- Runner-health proof, if applicable:
  - Manual-dispatch-only workflow:
  - Matching runner count:
  - Matching online runner count:
  - Prohibited-action scan result:
  - App/device/product automation excluded:
- Fixture UI smoke proof, if applicable:
  - Sterile fixture or demo mode:
  - Expected events observed:
  - Screenshots allowed by policy:
  - Raw private accessibility trees withheld:
  - Non-fixture apps excluded:

## Completion Gate

Do not promote the lane to heavier CI until:

- The default-branch proof passed.
- The safety boundary was verified with a command or direct inspection.
- Any hardware-specific labels are documented privately.
- The final handoff names what was not run.
