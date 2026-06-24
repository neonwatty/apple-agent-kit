#!/usr/bin/env python3
"""Validate a v0 Apple Agent Kit adapter without third-party dependencies."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if len(sys.argv) != 2:
        return fail("usage: scripts/validate-adapter.py <adapter.json>")

    path = Path(sys.argv[1])
    if not path.is_file():
        return fail(f"adapter file not found: {path}")

    try:
        adapter = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        return fail(f"invalid JSON: {exc}")

    if not isinstance(adapter, dict):
        return fail("adapter root must be an object")

    if not adapter.get("name"):
        return fail("adapter.name is required")

    platforms = adapter.get("platforms")
    if not isinstance(platforms, dict) or not platforms:
        return fail("adapter.platforms must define at least one platform")

    privacy = adapter.get("privacy")
    if not isinstance(privacy, dict):
        return fail("adapter.privacy is required")

    if "redactSecrets" not in privacy:
        return fail("adapter.privacy.redactSecrets is required")

    for platform_name, config in platforms.items():
        if platform_name not in {"macos", "ios"}:
            return fail(f"unsupported platform: {platform_name}")
        if not isinstance(config, dict):
            return fail(f"platform config must be an object: {platform_name}")
        for key in ("project", "scheme"):
            if not config.get(key):
                return fail(f"platforms.{platform_name}.{key} is required")

    print(f"valid adapter: {adapter['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
