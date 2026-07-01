# Adapter Contract

Adapters map public automation routines to a private Apple app repo.

The recommended file name is `.apple-agent-kit.json` for machine-readable use. YAML can be supported later, but JSON keeps v0 dependency-free.

## Example

```json
{
  "name": "example-preview",
  "platforms": {
    "macos": {
      "project": "App.xcodeproj",
      "scheme": "App",
      "destination": "platform=macOS",
      "derivedDataPath": "build",
      "appSmokeCommand": "make app-smoke"
    },
    "ios": {
      "project": "apple/App.xcodeproj",
      "scheme": "AppPreview",
      "uiScheme": "AppPreview",
      "uiTestTarget": "AppPreviewUITests",
      "simulatorDestination": "platform=iOS Simulator,name=iPhone 16",
      "physicalDeviceName": "Preview iPhone",
      "bundleIdentifier": "com.example.app.preview"
    }
  },
  "ci": {
    "macosRunner": "macos-15",
    "macosRunnerLabels": ["self-hosted", "macOS", "apple-agent-kit"],
    "physicalRunnerLabels": ["self-hosted", "macOS", "ios-physical"]
  },
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
  },
  "privacy": {
    "screenshots": "sterile-only",
    "rawAccessibilityTrees": false,
    "redactSecrets": true
  }
}
```

## Public Kit Rules

- Do not commit real adapters to this public repo unless they use example values.
- Do not hardcode product names, bundle identifiers, signing teams, or device identifiers in public scripts.
- Do not require secrets for dry-run validation.
- Refuse physical-device actions if the adapter is missing a privacy policy.
- Prefer explicit receipt files over prose-only claims.

## Validation

Validate an adapter with:

```bash
python3 scripts/aak.py validate-adapter .apple-agent-kit.json
```

Validate a fixture UI smoke receipt with:

```bash
python3 scripts/aak.py validate-fixture-ui-smoke-receipt fixture-ui-smoke.receipt.json
```

Render workflow templates into a scratch directory with:

```bash
python3 scripts/aak.py render-workflows --adapter .apple-agent-kit.json --output /tmp/aak-workflows --force
```

Review rendered workflows before copying them into a private repository.

## CI Runner Fields

- `ci.macosRunner` is for hosted or generic macOS CI templates that use a single `runs-on` value.
- `ci.macosRunnerLabels` is for self-hosted Mac runner-health workflows that use label arrays.
- `ci.physicalRunnerLabels` is for physical iOS workflows and should stay separate from device-free Mac runner health checks.

## Fixture UI Smoke Fields

The optional `automation` object describes sterile GUI smoke hooks for private repos. These fields are inert in the public kit unless a private workflow or operator explicitly runs the smoke command.

- `automation.fixtureBundleIdentifier` is a sanitized fixture, test host, or demo-mode bundle identifier. Do not point it at personal apps or live-account surfaces.
- `automation.fixtureSmokeCommand` is the private repo command that runs the deterministic UI smoke.
- `automation.logSubsystem` names the fixture log subsystem or structured log source to collect.
- `automation.allowedEvidence` should list only evidence classes allowed by policy, such as `logs`, `sterile-screenshots`, `result-bundles`, or `hashes`.
- `automation.fixtureReceiptPath` is the relative path where the private smoke command writes the validated receipt.
- `automation.allowedArtifactGlobs` is the relative allowlist uploaded by the manual fixture workflow.

For iOS simulator fixture smoke, `platforms.ios.simulatorDestination` must be set. `prepare-fixture-ui-smoke --platform ios` exports the destination as `AAK_FIXTURE_SIMULATOR_DESTINATION` so the private command does not guess a device.

Use `templates/fixture-ui-smoke.receipt.example.json` or `templates/ios-simulator-fixture-ui-smoke.receipt.example.json` when recording a fixture smoke proof. Keep filled receipts private if they include product-specific paths, log excerpts, bundle identifiers, result bundle internals, or screenshots.

Use `templates/fixture-ui-smoke-command.example.sh` as a private-repo starting point for writing the receipt and sanitized log artifact. Replace only the probe section with app-specific fixture automation; keep raw accessibility trees, host paths, account data, and non-fixture screenshots out of the receipt.

## Manual Remote PR Session Fields

Manual remote PR sessions let a developer enqueue a validated request from GitHub, then let a predefined private Mac pull and accept that request. The public adapter shape is only a contract; repo-specific commands, local paths, tokens, host identities, and product launch details stay in private adapters.

Recommended private adapter section:

```json
{
  "manualRemotePrSession": {
    "enabled": false,
    "queueProvider": "github-actions-artifact",
    "hostProfiles": [
      {
        "alias": "example-mac",
        "acceptedRunProfiles": ["unit-tests", "ui-smoke"],
        "allowLaunchApp": true,
        "allowCodexSession": true,
        "allowedCodexSurfaces": ["cli", "desktop-open"],
        "allowedCodexCapabilities": [],
        "physicalDeviceDefault": false
      }
    ],
    "runProfiles": [
      {
        "id": "unit-tests",
        "commands": [
          {
            "id": "test",
            "command": "make test",
            "timeoutMinutes": 30
          }
        ],
        "artifactPolicy": {
          "mode": "receipt-only",
          "allowedGlobs": []
        }
      }
    ]
  }
}
```

Contract rules:

- `enabled` must default to `false` until a private poller, queue allowlist, and receipt publication path are installed.
- `queueProvider` is `github-actions-artifact` for v1. The remote Mac polls GitHub for validated job-request artifacts; it does not expose an inbound LAN webhook.
- `hostProfiles[].alias` is a stable, sanitized alias. Do not publish hostnames, serial numbers, local usernames, device names, or network addresses.
- `runProfiles[].commands` are private allowlisted commands. Workflow inputs must never provide arbitrary shell commands.
- `allowLaunchApp` and `allowCodexSession` are separate gates. A test-only job must not implicitly launch the app or start an agent session.
- `allowedCodexSurfaces` is a private host allowlist. `cli` means a local Codex CLI/app-server session can be created; `desktop-open` means the adapter may open the checkout in Codex Desktop; `desktop-session` means the adapter can prove prompt delivery into a visible Codex Desktop session.
- `allowedCodexCapabilities` is a private host allowlist for Desktop-only session features such as `computer-use` and `browser-use`. Do not advertise these capabilities until the receiving Mac can prove them with a sterile local probe.
- If a request asks for `desktop-session` with `fallbackPolicy` set to `require-requested-surface`, the adapter must fail or skip Codex session creation rather than silently returning a CLI session.
- `physicalDeviceDefault` must remain `false`. Physical iPhone support is a gated extension that requires a separate approval reference, private device policy, and stricter evidence controls.
