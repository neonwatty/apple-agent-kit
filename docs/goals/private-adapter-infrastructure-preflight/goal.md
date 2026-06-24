# Private Adapter Infrastructure Preflight

## Objective

Run a private-adapter infrastructure preflight tranche that decides whether the validated private adapter is ready for later Mac runner and physical iPhone testing, while stopping before workflow dispatch, app install, WDA, screenshots, host-app automation, or any other real device action unless explicitly approved in a later tranche.

## Original Request

The user asked to proceed with the next recommended step after private-adapter dry-run validation: plan the infrastructure preflight tranche.

## Intake Summary

- Input shape: `existing_plan`
- Audience: Apple Agent Kit maintainers and private adapter maintainers.
- Authority: `approved`
- Proof type: `test`
- Completion proof: a final audit receipt showing the private adapter status was resolved, preflight-only readiness checks were run or explicitly blocked, no risky infrastructure action occurred, and the next gated action was recommended.
- Goal oracle: a final Judge/PM receipt maps receipts to adapter hygiene, runner readiness evidence, device readiness evidence, public leakage checks, private repo status, and a clear go/no-go for the next infrastructure action.
- Likely misfire: accidentally dispatching self-hosted workflows, installing to a device, starting WDA, taking screenshots, or treating adapter dry-run validation as enough to begin physical automation.
- Blind spots considered: whether to commit the private adapter, pre-existing private artifacts, runner label availability, keychain/signing checks, physical device readiness, and explicit approval boundaries.
- Existing plan facts: commit or intentionally park the private adapter; record that pre-existing artifacts are unrelated; run only runner/device readiness checks first; decide the next gated action.

## Goal Oracle

The oracle for this goal is:

`A final Judge/PM receipt proves the private adapter status is intentionally resolved, preflight-only infrastructure checks have receipts or precise blockers, no prohibited infrastructure action occurred, public leakage checks pass, and the next gated action is explicit.`

The PM must keep comparing task receipts to this oracle. Planning, adapter existence, or dry-run validation alone is not enough. The goal finishes only when a final Judge/PM audit maps receipts and verification back to this oracle and records `full_outcome_complete: true`.

## Goal Kind

`existing_plan`

## Current Tranche

Complete infrastructure preflight only. This tranche may inspect local/GitHub metadata and run non-mutating readiness commands, but it must stop before workflow dispatch, app install, WDA, screenshots, host-app automation, or any real device interaction beyond explicitly approved readiness checks.

## Non-Negotiable Constraints

- Keep public Apple Agent Kit files free of private app names, bundle IDs, device IDs, signing teams, tokens, runner names, and product-specific workflow copies.
- Do not commit private adapters, private rendered workflows, or private evidence to the public repo.
- Do not dispatch GitHub Actions workflows during this tranche.
- Do not install apps, start WDA, take screenshots, launch host apps, or run UI smoke.
- Do not alter private artifacts except by documenting their unrelated status.
- Preserve private details only in the private repo, private scratch files, or uncommitted local receipts.
- Ask for explicit user approval before any action that could mutate runner/device/app state.

## Stop Rule

Stop only when a final audit proves the infrastructure preflight tranche is complete.

Do not stop after deciding adapter status if runner/device readiness evidence or a precise blocker is still missing.

Do not continue into workflow dispatch, install, WDA, screenshots, or UI smoke without explicit approval for the exact target and action.

## Slice Sizing

Safe means bounded, explicit, verified, and reversible. It does not mean tiny.

A good Worker slice either resolves adapter hygiene or gathers a coherent preflight receipt. It must not mix preflight with real infrastructure execution.

## Board Health

The PM owns board health. If the board looks stale, misleading, offline, or inconsistent, run:

```bash
node /Users/neonwatty/.codex/plugins/cache/goalbuddy/goalbuddy/0.3.9/skills/goalbuddy/scripts/check-goal-state.mjs docs/goals/private-adapter-infrastructure-preflight/state.yaml
```

Repair only GoalBuddy control files unless an active Worker or PM task explicitly allows product-file edits.

## Canonical Board

Machine truth lives at:

`docs/goals/private-adapter-infrastructure-preflight/state.yaml`

If this charter and `state.yaml` disagree, `state.yaml` wins for task status, active task, receipts, verification freshness, and completion truth.

## Run Command

```text
/goal Follow docs/goals/private-adapter-infrastructure-preflight/goal.md.
```

## PM Loop

On every `/goal` continuation:

1. Read this charter.
2. Read `state.yaml`.
3. Run the GoalBuddy update checker when available.
4. Work only on the active board task.
5. Keep private app identifiers out of public committed files.
6. Stop before any infrastructure-mutating action unless a task records exact explicit approval.
7. Write a compact task receipt.
8. Update the board.
9. Continue to the next safe preflight task when safe local work remains.
10. Finish only with a Judge/PM audit receipt that maps receipts and verification back to the goal oracle and records `full_outcome_complete: true`.
