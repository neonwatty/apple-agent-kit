# T001 Scout: Mac Runner Rollout Map

## Summary

The selected private adapter exists and validates, but it does not yet contain a `ci.macosRunnerLabels` binding. The private repo does not yet have the device-free Mac runner-health workflow installed. GitHub runner metadata is readable and shows one online self-hosted runner, but the metadata scan did not find a sanitized match for the selected hardware naming pattern, so the first Worker should prepare the private workflow and leave workflow dispatch behind an exact approval and label-specificity gate.

## Adapter Status

Status: `needs binding`

- Private adapter exists.
- Private adapter validates.
- `ci.macosRunnerLabels` is absent.
- Existing physical-runner labels remain separate and must not be reused as proof that the Mac runner-health lane is configured.

## Workflow Status

Status: `absent`

- The private workflow surface exists.
- The device-free Mac runner-health workflow is not installed yet.
- Existing private runner-health workflows belong to another lane and should not be dispatched while the preview iPhone is parked.

## Runner Metadata Needs

- GitHub runner metadata is readable.
- One self-hosted runner is online.
- The selected runner needs an explicit private label binding before dispatch is considered robust.
- If the private runner has no dedicated label yet, the Worker should either stop before dispatch with a label-specificity blocker or record that the operator chose a broader generic label binding.

## Safe Files For First Worker

- The private adapter file.
- The private device-free Mac runner-health workflow file.
- A private scratch render directory.
- This GoalBuddy board's `state.yaml` and notes.

## Candidate Worker Package

Update the private adapter with a Mac runner label binding, render workflows into private scratch output, review only the rendered Mac runner-health workflow, and install only that workflow into the private workflow surface. Stop before dispatch.

The Worker should verify:

- private adapter validation passes;
- private render succeeds;
- rendered Mac runner-health workflow contains the selected runner labels;
- rendered workflow has no iPhone/device/app/smoke actions;
- only the private adapter and private Mac runner-health workflow changed in the private repo;
- public GoalBuddy leakage checks pass.
