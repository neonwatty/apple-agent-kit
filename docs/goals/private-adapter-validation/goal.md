# Private Adapter Validation

## Objective

Validate Apple Agent Kit against one selected private Apple app repo using only dry-run commands first: create or locate a private adapter, validate it, inspect the private repo through the public CLI, render workflows into a scratch location, compare the result to existing private workflows, and decide whether the next tranche is ready for self-hosted Mac runner or physical iPhone testing.

## Original Request

The user asked to plan the next private-adapter validation tranche with GoalBuddy prep.

## Intake Summary

- Input shape: `existing_plan`
- Audience: Apple Agent Kit maintainers and private adapter maintainers.
- Authority: `approved`
- Proof type: `test`
- Completion proof: a final audit receipt showing a selected private repo adapter was validated with `aak`, rendered workflows were produced outside the public repo, differences were reviewed without leaking private values into public files, and a go/no-go decision was recorded for later infrastructure testing.
- Goal oracle: private adapter validation, private repo inspection, scratch workflow rendering, comparison notes, public repo leakage check, and final readiness decision all pass without physical-device, WDA, install, screenshot, or self-hosted runner side effects.
- Likely misfire: doing real infrastructure work too early, committing private adapter details into the public repo, or stopping after creating an adapter without proving the public kit can inspect/render against it.
- Blind spots considered: private repo name leakage, adapter ownership, where private adapter files should live, generated workflow review, physical-device approval boundary, and proof that no public files contain private identifiers.
- Existing plan facts: start with one private repo; run `aak validate-adapter`, `aak inspect`, and `aak render-workflows` first; compare rendered workflows to existing private workflows; only later decide whether to test on a Mac Mini or preview iPhone.

## Goal Oracle

The oracle for this goal is:

`A final Judge/PM receipt proves one selected private adapter was validated by the public kit, rendered workflows were reviewed in a scratch/private location, no public leakage occurred, and the next infrastructure-testing decision is explicit.`

The PM must keep comparing task receipts to this oracle. Planning, adapter creation without validation, or rendered files without review is not enough. The goal finishes only when a final Judge/PM audit maps receipts and verification back to this oracle and records `full_outcome_complete: true`.

## Goal Kind

`existing_plan`

## Current Tranche

Complete private-adapter dry-run validation only. This tranche stops before dispatching self-hosted workflows, touching a LAN Mac Mini, installing to a physical iPhone, starting WDA, taking screenshots, or launching host apps.

## Non-Negotiable Constraints

- Keep public Apple Agent Kit files free of private app names, bundle IDs, device IDs, signing teams, tokens, runner names, and product-specific workflow copies.
- Do not commit private adapters or rendered private workflows to the public repo.
- Do not run physical-device, WDA, install, screenshot, host-app, or self-hosted runner workflows in this tranche.
- Use scratch directories such as `/tmp` for rendered workflow output unless a private repo-local path is explicitly approved.
- Preserve private details only in the private repo, private scratch files, or task receipts that are not committed to the public repo.
- Before declaring completion, try to disprove the result with command output and direct inspection.

## Stop Rule

Stop only when a final audit proves the private-adapter dry-run validation tranche is complete.

Do not stop after selecting a private repo, creating an adapter, or rendering workflows if validation and comparison evidence is still missing.

Do not continue into infrastructure testing without explicit user approval for the target runner/device and adapter.

## Slice Sizing

Safe means bounded, explicit, verified, and reversible. It does not mean tiny.

A good Worker slice for this goal produces a private adapter and dry-run proof, or a verified comparison report. It should not merely add public docs.

## Board Health

The PM owns board health. If the board looks stale, misleading, offline, or inconsistent, run:

```bash
node /Users/neonwatty/.codex/plugins/cache/goalbuddy/goalbuddy/0.3.9/skills/goalbuddy/scripts/check-goal-state.mjs docs/goals/private-adapter-validation/state.yaml
```

Repair only GoalBuddy control files unless an active Worker or PM task explicitly allows product-file edits.

## Canonical Board

Machine truth lives at:

`docs/goals/private-adapter-validation/state.yaml`

If this charter and `state.yaml` disagree, `state.yaml` wins for task status, active task, receipts, verification freshness, and completion truth.

## Run Command

```text
/goal Follow docs/goals/private-adapter-validation/goal.md.
```

## PM Loop

On every `/goal` continuation:

1. Read this charter.
2. Read `state.yaml`.
3. Run the GoalBuddy update checker when available.
4. Work only on the active board task.
5. Keep private app identifiers out of public committed files.
6. Write a compact task receipt.
7. Update the board.
8. Continue to the next safe Worker/PM task when safe local work remains.
9. Finish only with a Judge/PM audit receipt that maps receipts and verification back to the goal oracle and records `full_outcome_complete: true`.
