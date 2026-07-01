# Adopting macOS Fixture UI Smoke

The macOS fixture UI smoke lane is the first GUI proof after eligibility. It is manual-dispatch only, adapter-gated, and intended for sterile fixture apps or demo modes.

Use this lane after macOS CI eligibility and runner health pass. Do not use it for personal apps, live accounts, broad desktop automation, or physical-device work.

## Adapter Fields

Add an `automation` block to the private adapter:

```json
{
  "automation": {
    "fixtureBundleIdentifier": "com.example.app.fixture",
    "fixtureSmokeCommand": "make fixture-ui-smoke",
    "logSubsystem": "com.example.app.fixture",
    "allowedEvidence": ["logs", "sterile-screenshots"],
    "fixtureReceiptPath": "artifacts/fixture-ui-smoke/fixture-ui-smoke.receipt.json",
    "allowedArtifactGlobs": [
      "artifacts/fixture-ui-smoke/fixture-ui-smoke.receipt.json",
      "artifacts/fixture-ui-smoke/*.log",
      "artifacts/fixture-ui-smoke/*.png"
    ]
  }
}
```

The private command must create the receipt at `automation.fixtureReceiptPath` and the receipt must validate with:

```bash
python3 path/to/apple-agent-kit/scripts/aak.py prepare-fixture-ui-smoke \
  --adapter .apple-agent-kit.json \
  --script /tmp/aak-fixture-smoke.sh \
  --approval fixture-ui-smoke \
  --platform macos \
  --json

python3 path/to/apple-agent-kit/scripts/aak.py validate-fixture-ui-smoke-receipt \
  artifacts/fixture-ui-smoke/fixture-ui-smoke.receipt.json \
  --json
```

Use `templates/fixture-ui-smoke-command.example.sh` as the starting point for the private command. Keep its receipt-writing shape, but replace the marked probe section with the actual fixture-app launch, click/type, menu, window, or dialog checks. The scaffold intentionally starts with screenshots disabled; add sterile screenshots only after log and receipt evidence is repeatable.

## Workflow Installation

1. Render templates from the private adapter.
2. Review `macos-fixture-ui-smoke.yml`.
3. Copy it into `.github/workflows/macos-fixture-ui-smoke.yml`.
4. Store the private adapter in `APPLE_AGENT_KIT_ADAPTER_JSON`.
5. Dispatch the workflow manually and type `fixture-ui-smoke` in the approval input.

The workflow validates the adapter, checks Xcode readiness, runs only the private fixture command, validates the fixture receipt, asserts the device boundary, and uploads only the receipt plus adapter-allowlisted artifacts.

## Privacy Rules

- `privacy.rawAccessibilityTrees` must be `false`.
- `privacy.redactSecrets` must be `true`.
- `privacy.screenshots` must be `none` or `sterile-only`.
- Artifact paths must be relative and sanitized.
- Keep raw logs private when they expose host paths, usernames, private URLs, or product data.

## Promotion Gate

Do not promote from fixture UI smoke to broader app smoke until:

- The same fixture receipt passes on the default branch.
- The expected log events are present in the receipt.
- The strongest attempted disproof is documented.
- Non-fixture apps and physical-device actions are explicitly excluded.
- Screenshots, if any, are sterile and adapter-allowlisted.
