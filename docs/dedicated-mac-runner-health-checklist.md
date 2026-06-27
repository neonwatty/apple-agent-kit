# Dedicated Mac Runner-Health Checklist

Use this checklist when a private adapter binds Apple Agent Kit to a specific self-hosted Mac runner. The checklist is public-safe by design: fill private values only in a private repo or private incident log.

This lane proves runner readiness only. It must not install apps, launch apps, boot simulators, start WDA, take screenshots, run UI smoke, touch physical devices, build products, or test products.

## Inputs

- Apple Agent Kit commit or tag:
- Private adapter location, recorded privately:
- Rendered workflow name: `macos-runner-health.yml`
- Intended runner binding, recorded privately:
- Exact exclusions approved by the operator:

## Pre-Dispatch Gates

All gates should pass immediately before dispatch:

- The selected Apple Agent Kit source validates.
- The private adapter validates.
- `macos-runner-health.yml` renders from the private adapter into scratch space only.
- The rendered workflow matches the installed workflow.
- The installed workflow on the dispatch ref matches the reviewed workflow.
- The workflow trigger is `workflow_dispatch` only.
- Prohibited-action scan is clean outside inert safety-scan assertion text.
- The private runner binding maps to exactly one matching runner.
- Exactly one matching runner is online.
- The operator approval names the runner-health workflow and excludes app/device/product automation.

## Generic Verification Commands

Run from the public Apple Agent Kit checkout:

```sh
python3 scripts/validate-release.py
python3 scripts/aak.py validate-adapter /path/to/private-adapter.json --json
python3 scripts/aak.py render-workflows \
  --adapter /path/to/private-adapter.json \
  --output /tmp/aak-runner-health-render \
  --force
```

Then compare the rendered workflow with the installed private workflow using a structured YAML-aware check or a direct diff after confirming both files are expected to be identical.

## Safety Scan

The runner-health workflow may contain prohibited terms only as inert assertion text. It should not contain commands that perform:

- app install;
- app launch;
- WDA startup;
- screenshot capture;
- UI smoke;
- physical-device smoke;
- simulator boot;
- product build;
- product test.

## Dispatch

Dispatch only the runner-health workflow, only after the exact approval phrase is present.

```sh
gh workflow run macos-runner-health.yml --ref <reviewed-ref>
```

Do not dispatch adjacent workflows as part of this lane.

## Sanitized Receipt

Record:

- timestamp;
- event type;
- run status and conclusion;
- matching runner count;
- matching online runner count;
- observed step classes;
- failed step classes;
- prohibited-action scan result;
- statement that no app/device/product automation ran.

Do not record:

- private runner labels;
- hostnames;
- runner names;
- usernames;
- raw adapter JSON;
- signing teams;
- secret names or values;
- private repository URLs in public docs.

## Promotion Boundary

A passing runner-health dispatch proves only that the self-hosted Mac runner can accept the workflow and complete the generic health checks. Product CI, signing, app install, simulator automation, UI smoke, and physical-device workflows each need their own approval gate and proof receipt.
