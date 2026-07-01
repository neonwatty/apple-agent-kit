#!/bin/bash
set -euo pipefail

# Copy this file into a private app repo and replace the marked probe section
# with deterministic fixture-app launch/click/type/assert steps.

receipt_path="${AAK_FIXTURE_RECEIPT_PATH:-artifacts/fixture-ui-smoke/fixture-ui-smoke.receipt.json}"
log_path="${AAK_FIXTURE_LOG_PATH:-artifacts/fixture-ui-smoke/fixture.log}"
fixture_platform="${AAK_FIXTURE_PLATFORM:-macos}"
bundle_id="${AAK_FIXTURE_BUNDLE_ID:-com.example.app.fixture}"
log_subsystem="${AAK_FIXTURE_LOG_SUBSYSTEM:-com.example.app.fixture}"
fixture_mode="${AAK_FIXTURE_MODE:-sterile-demo}"

mkdir -p "$(dirname "$receipt_path")" "$(dirname "$log_path")"

started_at="$(python3 - <<'PY'
from datetime import datetime, timezone
print(datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
PY
)"

# Private repos replace this section with GUI automation against a sterile
# fixture app or demo mode. Keep emitted evidence bounded and sanitized.
cat > "$log_path" <<EOF
subsystem=$log_subsystem event=fixture-window-opened
subsystem=$log_subsystem event=fixture-button-pressed
subsystem=$log_subsystem event=fixture-text-updated
EOF

completed_at="$(python3 - <<'PY'
from datetime import datetime, timezone
print(datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"))
PY
)"

if command -v shasum >/dev/null 2>&1; then
  log_sha="$(shasum -a 256 "$log_path" | awk '{print $1}')"
else
  log_sha="$(sha256sum "$log_path" | awk '{print $1}')"
fi
log_size="$(wc -c < "$log_path" | tr -d ' ')"

python3 - "$receipt_path" "$started_at" "$completed_at" "$bundle_id" "$fixture_mode" "$log_subsystem" "$log_path" "$log_sha" "$log_size" <<'PY'
import json
import sys

(
    receipt_path,
    started_at,
    completed_at,
    bundle_id,
    fixture_mode,
    log_subsystem,
    log_path,
    log_sha,
    log_size,
) = sys.argv[1:]
fixture_platform = __import__("os").environ.get("AAK_FIXTURE_PLATFORM", "macos")
command_class = "ios-simulator-fixture-ui-smoke" if fixture_platform == "ios" else "macos-fixture-ui-smoke"

receipt = {
    "schemaVersion": "fixture-ui-smoke/v1",
    "kind": "fixture-ui-smoke.receipt",
    "adapter": {
        "name": "example-preview",
        "platform": fixture_platform,
    },
    "startedAt": started_at,
    "completedAt": completed_at,
    "result": "succeeded",
    "target": {
        "fixtureBundleIdentifier": bundle_id,
        "fixtureMode": fixture_mode,
        "nonFixtureAppsTouched": False,
        "physicalDeviceActions": False,
    },
    "commands": [
        {
            "id": "fixture-ui-smoke",
            "class": command_class,
            "summary": "Ran deterministic sterile fixture smoke scaffold",
            "durationSeconds": 0,
            "exitCode": 0,
            "result": "succeeded",
        }
    ],
    "evidence": {
        "logSubsystem": log_subsystem,
        "logTimeWindow": f"{started_at}/{completed_at}",
        "expectedEvents": [
            "fixture-window-opened",
            "fixture-button-pressed",
            "fixture-text-updated",
        ],
        "observedEventCount": 3,
        "artifacts": [
            {
                "label": "sanitized-fixture-log",
                "path": log_path,
                "sha256": log_sha,
                "sizeBytes": int(log_size),
            }
        ],
        "withheld": [
            {
                "label": "raw-accessibility-tree",
                "reason": "raw private accessibility trees are not public evidence",
            },
            {
                "label": "screenshots",
                "reason": "the scaffold starts with screenshots disabled",
            },
        ],
    },
    "privacy": {
        "screenshots": "none",
        "rawAccessibilityTrees": False,
        "redactSecrets": True,
        "assertions": [
            "No personal app screenshots were captured.",
            "No private account data was used.",
            "No raw private accessibility tree was published.",
        ],
    },
    "strongestAttemptedDisproof": "Checked fixture-only target, expected log events, artifact allowlist, and exclusion of physical-device actions.",
}

with open(receipt_path, "w", encoding="utf-8") as handle:
    json.dump(receipt, handle, indent=2, sort_keys=True)
    handle.write("\n")
PY
