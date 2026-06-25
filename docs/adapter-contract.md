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

Render workflow templates into a scratch directory with:

```bash
python3 scripts/aak.py render-workflows --adapter .apple-agent-kit.json --output /tmp/aak-workflows --force
```

Review rendered workflows before copying them into a private repository.

## CI Runner Fields

- `ci.macosRunner` is for hosted or generic macOS CI templates that use a single `runs-on` value.
- `ci.macosRunnerLabels` is for self-hosted Mac runner-health workflows that use label arrays.
- `ci.physicalRunnerLabels` is for physical iOS workflows and should stay separate from device-free Mac runner health checks.
