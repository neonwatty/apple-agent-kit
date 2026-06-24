#!/usr/bin/env bash
set -euo pipefail

echo "Apple Agent Kit Xcode environment"
echo "host=$(hostname)"
echo "user=$(id -un)"
echo "arch=$(uname -m)"
sw_vers || true

if command -v xcodebuild >/dev/null 2>&1; then
  xcodebuild -version
else
  echo "xcodebuild=missing"
fi

if command -v xcrun >/dev/null 2>&1; then
  xcrun simctl list devices available | sed -n '1,80p' || true
else
  echo "xcrun=missing"
fi
