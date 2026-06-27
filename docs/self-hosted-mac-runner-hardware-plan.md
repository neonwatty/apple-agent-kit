# Self-Hosted Mac Runner Hardware Plan

This plan is for a device-free Mac mini runner lane. It validates the Mac runner before any physical iPhone, install, WDA, screenshot, app launch, UI smoke, or physical-device workflow is allowed.

## Goals

- Prove the runner host is reachable by GitHub Actions.
- Prove macOS, Xcode, simulator runtimes, disk, and automation process state are healthy.
- Keep device workflows parked until the operator explicitly approves them later.
- Keep private runner labels, hostnames, device names, signing teams, and secret names in private adapters.

## Public Kit Shape

Use `templates/github-actions/macos-runner-health.yml` as the public generic template. Pair it with the [Dedicated Mac Runner-Health Checklist](dedicated-mac-runner-health-checklist.md) when preparing a private self-hosted runner. The workflow is intentionally limited to:

- host summary;
- Xcode summary;
- simulator runtime listing;
- process safety summary;
- disk summary;
- an explicit device-free assertion.

The adapter field `ci.macosRunnerLabels` binds the generic workflow to private self-hosted runner labels. If omitted, rendering uses example labels only.

## Private Adapter Work

In a private repo, the next adapter update should:

- set `ci.macosRunnerLabels` to the Mac mini runner labels;
- render `macos-runner-health.yml` into a private workflow branch or scratch path;
- review the rendered workflow before copying it into `.github/workflows`;
- dispatch only the runner-health workflow after exact approval.

Do not reuse iOS physical-device runner-health workflows while the preview iPhone is parked, because those workflows may include device naming or listing steps.

## Hardware Checklist

- Runner machine has stable power and network.
- GitHub self-hosted runner service is online and scoped to the intended private repo or org.
- Runner labels are specific enough to avoid accidental dispatch to another Mac.
- Xcode command line tools point to the intended Xcode.
- The runner user can run non-GUI Xcode commands without prompts.
- Disk has enough free space for DerivedData, checkouts, and result bundles.
- Any signing/keychain checks remain a separate later gate.

## Gate Order

1. Render and review the private runner-health workflow.
2. Dispatch runner-health only.
3. Save a sanitized receipt with host/Xcode/disk/process status.
4. Decide whether runner cleanup or provisioning is needed.
5. Ask for separate approval before any signing, app install, WDA, screenshot, UI smoke, or physical-device workflow.

## Approval Boundary

The approval phrase for this lane should name the private runner-health workflow only. It should explicitly exclude install, WDA, screenshots, app launch, UI smoke, and physical-device smoke.
