# T001 Scout: Private Target Surface

## Target

A selected private iOS app repository is available through authenticated GitHub and as a local clone. The local clone is suitable for private adapter work, but it already has unrelated untracked artifact output that must be ignored.

## Relevant Surface

- Workflow surface: simulator CI, preview physical smoke, production physical smoke, preview install, production install, runner health, release, and auto-merge workflows.
- Script surface: iOS build, test, simulator UI smoke, physical device smoke, preview/production install, runner preflight, device resolution, WDA smoke, screenshot, and diagnostics helpers.
- Xcode surface: XcodeGen project config, primary app scheme, preview app scheme, unit test target, UI test target, and preview UI test target.
- Existing proof surface: result bundles, screenshot artifacts, runner preflight scripts, built-config verification, and workflow-level artifact uploads.

## Safe Adapter Location

Use the private repo root adapter file. Do not place the adapter in the public Apple Agent Kit repo.

## Recommended Worker Package

Create or update the private repo adapter, then run:

- `aak validate-adapter`
- `aak inspect`
- `aak render-workflows` into a scratch directory

The Worker should not dispatch workflows, install apps, start WDA, capture screenshots, or touch any physical device.

## Candidate Comparison Package

After adapter validation, compare rendered scratch workflows against the private repo's existing workflow family and record a sanitized summary: which public templates correspond to existing private workflows, which private workflows are intentionally out of scope, and which public-kit template gaps should become follow-up work.
