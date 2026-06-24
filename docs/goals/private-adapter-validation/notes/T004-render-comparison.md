# T004 Rendered Workflow Comparison

## Summary

Rendered workflows were created in a scratch directory and compared to the selected private repo's existing workflow family.

## Mapping

- Public iOS simulator template maps to the private simulator CI workflow at a skeleton level: checkout, Xcode selection, build, unit tests, UI smoke, and result-bundle upload.
- Public iOS physical template maps to the private preview physical smoke workflow at a skeleton level: workflow dispatch, self-hosted runner labels, runner preflight, physical smoke, and artifact upload.
- Public macOS CI template is not applicable to the selected private iOS-only validation target.

## Expected Differences

- The private simulator workflow has repo-specific change detection, Node setup, version checks, generated-project setup, built-config verification, and CI environment stubs.
- The private physical workflow has repo-specific device inputs, signing/keychain environment, device-list/resolve steps, preview-specific smoke wrappers, and screenshot artifact handling.
- The public templates intentionally stay generic and should not copy private secret names, bundle identifiers, runner labels, or product-specific script wrappers.

## Follow-Up Candidates

- Add a later public-kit template concept for "iOS generated-project CI with optional Node/version preflight" if more adapters need it.
- Add a later private template/adaptor overlay layer for product-specific workflow steps.
- Improve public `aak inspect` later so it can ignore existing `*.xcresult` bundle internals by default when summarizing test surfaces.
