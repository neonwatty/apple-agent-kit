# Apple Agent Kit v0 Dry-Run Automation

## Objective

Turn the public Apple Agent Kit scaffold into a usable v0 dry-run automation kit: a generic command surface that can inspect an Apple app repo, validate a private adapter, render workflow templates, check local Xcode readiness, and summarize `xcresult` bundles without touching physical devices or leaking private product details.

## Original Request

The user asked to plan the next Apple Agent Kit work with GoalBuddy prep after approving a public/open-source plugin design with private repo-specific adapters.

## Intake Summary

- Input shape: `existing_plan`
- Audience: maintainers and users of the open-source Apple Agent Kit, plus private app adapter maintainers later.
- Authority: `approved`
- Proof type: `test`
- Completion proof: a final audit receipt showing the v0 dry-run command surface works against example fixtures/templates, validates the adapter contract, passes plugin validation, and contains no private app identifiers.
- Goal oracle: `scripts/validate-adapter.py templates/adapter.example.json`, plugin validation, dry-run CLI help/fixture commands, workflow rendering checks, and a repo-specific leakage grep must all pass before completion.
- Likely misfire: the goal could produce more docs or templates but no usable dry-run command surface, or it could accidentally bake private adapter details into the public repo.
- Blind spots considered: Codex plugin manifest validation, Claude Code compatibility, no physical-device side effects, public/private boundary, Xcode availability variance, and proof that the generated public templates do not leak private identifiers.
- Existing plan facts: start with v0 dry-run automation; add `aak inspect`, `aak validate-adapter`, `aak render-workflows`, `aak check-xcode`, and `aak summarize-xcresult`; create private adapters later; do not run on Mac Mini or preview iPhone until dry-run proof is in place and the user approves.

## Goal Oracle

The oracle for this goal is:

`A final Judge/PM receipt maps implemented v0 dry-run commands to passing verification: adapter validation, plugin validation, CLI help and dry-run checks, workflow rendering checks, and a private-identifier grep over the public repo.`

The PM must keep comparing task receipts to this oracle. Planning, discovery, a passing tiny slice, or a clean-looking board is not enough. The goal finishes only when a final Judge/PM audit maps receipts and verification back to this oracle and records `full_outcome_complete: true`.

## Goal Kind

`existing_plan`

## Current Tranche

Complete the v0 dry-run foundation in the public repository. This tranche stops before any private adapter is committed, before any LAN Mac Mini workflow is dispatched, and before any preview iPhone install, WDA session, screenshot, or host-app automation is attempted.

## Non-Negotiable Constraints

- Work in `/Users/neonwatty/Desktop/apple-agent-kit`, not the blog repo.
- Keep the repo public-safe: no private app names, private bundle IDs, real device IDs, signing teams, tokens, runner names, or product-specific workflows.
- Do not touch physical devices, start WDA, install apps, launch host apps, or dispatch self-hosted workflows during this tranche.
- Keep private adapters out of this public repo.
- Preserve Codex plugin validity.
- Prefer generic dependency-light scripts for v0.
- Before declaring completion, try to disprove the change with commands and direct inspection.

## Stop Rule

Stop only when a final audit proves the full original outcome for this tranche is complete.

Do not stop after planning, discovery, or Judge selection if a safe Worker task can be activated.

Do not stop after a single verified Worker package when the broader owner outcome still has safe local follow-up work. Advance the board to the next highest-leverage safe Worker package and continue unless a phase, risk, rejected-verification, ambiguity, or final-completion review is due.

## Slice Sizing

Safe means bounded, explicit, verified, and reversible. It does not mean tiny.

A good Worker slice for this goal should produce a working v0 command surface or a coherent verified part of it, not just another prose plan.

## Board Health

The PM owns board health. If the board looks stale, misleading, offline, or inconsistent, run:

```bash
node /Users/neonwatty/.codex/plugins/cache/goalbuddy/goalbuddy/0.3.9/skills/goalbuddy/scripts/check-goal-state.mjs docs/goals/v0-dry-run-automation
```

Repair only GoalBuddy control files unless an active Worker or PM task explicitly allows product-file edits.

## Canonical Board

Machine truth lives at:

`docs/goals/v0-dry-run-automation/state.yaml`

If this charter and `state.yaml` disagree, `state.yaml` wins for task status, active task, receipts, verification freshness, and completion truth.

## Run Command

```text
/goal Follow docs/goals/v0-dry-run-automation/goal.md.
```

## PM Loop

On every `/goal` continuation:

1. Read this charter.
2. Read `state.yaml`.
3. Run the GoalBuddy update checker when available.
4. Work only on the active board task.
5. Write a compact task receipt.
6. Update the board.
7. Continue to the next safe Worker/PM task when safe local work remains.
8. Finish only with a Judge/PM audit receipt that maps receipts and verification back to the goal oracle and records `full_outcome_complete: true`.
