# T001 Scout: Infrastructure Preflight Map

## Summary

The selected private adapter exists in the private repo root and still validates with the public dry-run validator. It is not tracked in the private repo. The private repo also has many unrelated pre-existing untracked artifact files, so adapter hygiene must be decided without sweeping those artifacts into the work.

## Adapter Status

Status: `ambiguous`

The adapter is a commit candidate because it validates and is needed for repeatable private automation. It can also be intentionally parked locally if the operator does not want private adapter policy committed yet. The important point for this tranche is to make that choice explicit before any real infrastructure execution.

## Artifact Hygiene

The private repo has hundreds of untracked files. The adapter is one untracked root file; the rest are artifact outputs from prior work. Treat those artifacts as unrelated and out of scope. Do not clean, move, commit, or summarize their private contents in public files.

## Safe Runner Preflight Candidates

- Public local check: run Apple Agent Kit Xcode readiness and record only status/counts.
- GitHub metadata check: read self-hosted runner count and online/offline counts without printing runner names or labels.
- Workflow metadata check: read workflow count and active count without dispatching workflows.
- Private runner script review or dry-run candidate: inspect the private runner preflight helper before running it; run only if it is confirmed read-only and does not touch keychain, signing, install, WDA, screenshots, app launch, or workflow dispatch.

## Safe Device Readiness Candidates

- Candidate only: inspect the private device-list and device-resolution helpers to confirm they are read-only before running.
- Candidate only: if confirmed read-only, collect only a sanitized device availability receipt, such as count/status, with no device identifiers in public files.
- Explicitly out of scope for this tranche unless later approved: install, WDA, screenshots, host-app automation, UI smoke, and workflow dispatch.

## Candidate Worker Package

Run a sanitized preflight receipt package that records:

- adapter exists and validates;
- adapter is parked or commit-candidate by explicit decision;
- unrelated private artifacts remain untouched;
- local Xcode readiness status/counts;
- GitHub runner/workflow metadata counts;
- candidate physical-device readiness command remains unrun until confirmed read-only.

Allowed files should be limited to this GoalBuddy board's `state.yaml` and a sanitized `notes/T003-preflight-receipt.md`. Verification should include GoalBuddy state validation, public leakage grep, and public git status.
