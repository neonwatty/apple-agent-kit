# Private Mac Runner Health Rollout

## Objective

Roll out the device-free self-hosted Mac runner-health lane for the selected private Mac mini runner: bind the private adapter to the selected runner labels, render and review the public `macos-runner-health.yml` template privately, install it into the private workflow surface when safe, dispatch only that runner-health workflow after exact approval, and capture a sanitized receipt that decides whether the runner is ready for later CI use.

## Original Request

The user asked to make a detailed GoalBuddy prep board for the next steps after parking the preview iPhone and moving on with Mac Mini 2 hardware plans.

## Intake Summary

- Input shape: `existing_plan`
- Audience: Apple Agent Kit maintainers and private adapter maintainers.
- Authority: `approved_for_prep`
- Proof type: `test`
- Completion proof: a final audit receipt showing the private adapter binding exists or is explicitly blocked, the private runner-health workflow was rendered/reviewed/installed or precisely blocked, exact approval was obtained before dispatch, the runner-health workflow completed or produced a clear remediation blocker, and no iPhone/device/app smoke action occurred.
- Goal oracle: a final Judge/PM receipt maps receipts to private adapter binding, rendered workflow review, private workflow installation, runner-health dispatch approval, runner-health result, public leakage checks, private repo status, and a clear ready/not-ready decision for the selected Mac runner.
- Likely misfire: accidentally reusing an iOS physical-device runner-health workflow, touching the parked preview iPhone, dispatching a workflow before exact approval, committing private runner labels to the public repo, or treating local render success as proof the hardware runner is healthy.
- Blind spots considered: private adapter commit policy, exact runner label binding, whether a private branch is needed, whether workflow dispatch is permitted, how to capture logs without leaking private host details, and remediation flow if the runner-health check fails.
- Existing plan facts: keep the preview iPhone parked; use the new public device-free Mac runner-health template; bind private `ci.macosRunnerLabels`; render/review privately; install only the Mac runner-health workflow; dispatch only after exact approval; save a sanitized receipt; decide if the runner is ready or needs remediation.

## Goal Oracle

The oracle for this goal is:

`The selected private Mac runner has a validated private adapter binding, a reviewed device-free runner-health workflow, an exact-approval dispatch receipt or precise blocker, a sanitized runner-health result, no iPhone/device/app action, no public private-value leakage, and an explicit ready/not-ready next decision.`

The PM must keep comparing task receipts to this oracle. Adapter edits, rendering, or workflow installation alone are not enough. The goal finishes only when a final Judge/PM audit maps current receipts and verification back to this oracle and records `full_outcome_complete: true`.

## Goal Kind

`existing_plan`

## Current Tranche

Complete Mac runner-health rollout only. This tranche may edit private adapter/workflow files and may dispatch the private Mac runner-health workflow only after exact approval. It must not run iPhone/device checks, app install, WDA, screenshots, host-app automation, UI smoke, physical-device smoke, or product build/test workflows.

## Non-Negotiable Constraints

- The preview iPhone is parked for this tranche.
- Keep public Apple Agent Kit files free of private app names, repo names, bundle IDs, device IDs, signing teams, tokens, runner names, runner labels, hostnames, and product-specific workflow copies.
- Do not dispatch any workflow until an active task records the exact approved workflow and approval phrase.
- Dispatch only the private Mac runner-health workflow in this tranche, never an iOS physical-device workflow.
- Do not install apps, start WDA, take screenshots, launch host apps, run UI smoke, run physical-device smoke, or touch the parked iPhone.
- Preserve private details only in private repo files, private scratch files, private branch/PR text, or uncommitted local receipts.
- Ask for explicit user approval before any action that mutates remote workflow state.

## Stop Rule

Stop only when a final audit proves the Mac runner-health rollout tranche is complete.

Do not stop after adapter binding, rendering, or workflow installation if dispatch/result evidence or a precise blocker is still missing.

Do not continue into build/test/product automation, physical-device work, signing/keychain changes, app install, WDA, screenshots, or UI smoke without a new explicit approval for that later tranche.

## Slice Sizing

Safe means bounded, explicit, verified, and reversible. It does not mean tiny.

A good Worker slice either prepares the private runner-health workflow end to end up to the approval gate, or dispatches/records the approved runner-health workflow. It must not mix runner health with product CI or device automation.

## Board Health

The PM owns board health. If the board looks stale, misleading, offline, or inconsistent, run:

```bash
node /Users/neonwatty/.codex/plugins/cache/goalbuddy/goalbuddy/0.3.9/skills/goalbuddy/scripts/check-goal-state.mjs docs/goals/private-mac-runner-health-rollout/state.yaml
```

Repair only GoalBuddy control files unless an active Worker or PM task explicitly allows product/private repo edits.

## Canonical Board

Machine truth lives at:

`docs/goals/private-mac-runner-health-rollout/state.yaml`

If this charter and `state.yaml` disagree, `state.yaml` wins for task status, active task, receipts, verification freshness, and completion truth.

## Run Command

```text
/goal Follow docs/goals/private-mac-runner-health-rollout/goal.md.
```

## PM Loop

On every `/goal` continuation:

1. Read this charter.
2. Read `state.yaml`.
3. Run the GoalBuddy update checker when available.
4. Work only on the active board task.
5. Keep private identifiers out of public committed files.
6. Keep the preview iPhone parked.
7. Stop before workflow dispatch unless exact approval is recorded for the private Mac runner-health workflow.
8. Write a compact task receipt.
9. Update the board.
10. Continue to the next safe Mac runner-health task when safe local work remains.
11. Finish only with a Judge/PM audit receipt that maps receipts and verification back to the goal oracle and records `full_outcome_complete: true`.
