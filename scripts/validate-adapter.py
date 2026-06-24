#!/usr/bin/env python3
"""Compatibility wrapper for `aak validate-adapter`."""

from __future__ import annotations

import sys
from pathlib import Path

import aak


def main() -> int:
    if len(sys.argv) != 2:
        print("error: usage: scripts/validate-adapter.py <adapter.json>", file=sys.stderr)
        return 1
    return aak.command_validate_adapter_path(Path(sys.argv[1]))


if __name__ == "__main__":
    raise SystemExit(main())
