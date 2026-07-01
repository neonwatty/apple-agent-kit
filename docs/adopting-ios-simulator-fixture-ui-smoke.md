# Adopting iOS Simulator Fixture UI Smoke

The iOS simulator fixture UI smoke lane is the first iOS GUI proof after eligibility. It is manual-dispatch only, adapter-gated, and intended for sterile fixture apps, demo modes, or test-only simulator surfaces.

Use this lane after iOS CI eligibility passes. Do not use it for personal devices, live accounts, production data, broad app exploration, WDA/Appium sessions, or physical-device work.

## Adapter Fields

The private adapter must include an iOS platform with a simulator destination and the shared fixture automation block:

```json
{
  "platforms": {
    "ios": {
      "project": "App.xcodeproj",
      "scheme": "AppPreview",
      "simulatorDestination": "platform=iOS Simulator,name=iPhone 16"
    }
  },
  "automation": {
    "fixtureBundleIdentifier": "com.example.app.fixture",
    "fixtureSmokeCommand": "make fixture-ui-smoke",
    "logSubsystem": "com.example.app.fixture",
    "allowedEvidence": ["logs", "result-bundles"],
    "fixtureReceiptPath": "artifacts/fixture-ui-smoke/fixture-ui-smoke.receipt.json",
    "allowedArtifactGlobs": [
      "artifacts/fixture-ui-smoke/fixture-ui-smoke.receipt.json",
      "artifacts/fixture-ui-smoke/*.log",
      "artifacts/fixture-ui-smoke/*.xcresult"
    ]
  }
}
```

`prepare-fixture-ui-smoke --platform ios` exports:

- `AAK_FIXTURE_PLATFORM=ios`
- `AAK_FIXTURE_SIMULATOR_DESTINATION`
- `AAK_FIXTURE_RECEIPT_PATH`
- `AAK_FIXTURE_BUNDLE_ID`
- `AAK_FIXTURE_LOG_SUBSYSTEM`

The private command must create the receipt at `automation.fixtureReceiptPath` and the receipt must validate with:

```bash
python3 path/to/apple-agent-kit/scripts/aak.py prepare-fixture-ui-smoke \
  --adapter .apple-agent-kit.json \
  --script /tmp/aak-ios-fixture-smoke.sh \
  --approval fixture-ui-smoke \
  --platform ios \
  --json

python3 path/to/apple-agent-kit/scripts/aak.py validate-fixture-ui-smoke-receipt \
  artifacts/fixture-ui-smoke/fixture-ui-smoke.receipt.json \
  --json
```

Use `templates/fixture-ui-smoke-command.example.sh` as the receipt-writing scaffold. For iOS, replace the marked probe section with deterministic simulator build/install/launch or XCTest UI steps against the fixture app only.

## Workflow Installation

1. Render templates from the private adapter.
2. Review `ios-simulator-fixture-ui-smoke.yml`.
3. Copy it into `.github/workflows/ios-simulator-fixture-ui-smoke.yml`.
4. Store the private adapter in `APPLE_AGENT_KIT_ADAPTER_JSON`.
5. Dispatch the workflow manually and type `fixture-ui-smoke` in the approval input.

The workflow validates the adapter, prepares the fixture command for `platform=ios`, checks Xcode readiness, runs only the private fixture command, validates the fixture receipt, asserts the simulator boundary, uploads the receipt for diagnosis, and uploads adapter-allowlisted evidence only after receipt validation succeeds.

## Privacy Rules

- `privacy.rawAccessibilityTrees` must be `false`.
- `privacy.redactSecrets` must be `true`.
- `privacy.screenshots` must be `none` or `sterile-only`.
- Artifact paths must be relative and sanitized.
- Keep raw simulator logs, full UI trees, result bundle internals, host paths, and account content out of public receipts.

## Promotion Gate

Do not promote from simulator fixture smoke to physical-device automation until:

- The same fixture receipt passes on the default branch.
- The expected fixture events are present in logs or result bundles.
- The receipt states `adapter.platform` is `ios`.
- Physical-device actions are explicitly excluded.
- Any screenshots are sterile and adapter-allowlisted.
