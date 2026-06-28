#!/usr/bin/env python3
"""Validate the public Apple Agent Kit v0 release surface."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    "CHANGELOG.md",
    "LICENSE",
    "README.md",
    "docs/adapter-contract.md",
    "docs/install.md",
    "docs/manual-remote-pr-session.md",
    "docs/privacy-safe-evidence.md",
    "docs/private-adapter-rollout-checklist.md",
    "docs/slim-codex-autoreview.md",
    "docs/proof-records/index.md",
    "docs/v0-release-readiness.md",
    "scripts/aak.py",
    "skills/codex-autoreview/SKILL.md",
    "schemas/manual-remote-pr-session.job-request.schema.json",
    "schemas/manual-remote-pr-session.receipt.schema.json",
    "templates/adapter.example.json",
    "templates/github-actions/manual-remote-pr-session.yml",
    "templates/manual-remote-pr-session.job-request.example.json",
    "templates/manual-remote-pr-session.receipt.example.json",
]

PROOF_RECORDS = [
    "docs/proof-records/foil-ios-ci-eligibility-2026-06-25.md",
    "docs/proof-records/foil-macos-ci-eligibility-2026-06-25.md",
    "docs/proof-records/prcard-ios-ci-eligibility-2026-06-27.md",
]

PRIVATE_KEY_SUFFIX = "PRIVATE " + "KEY"

FORBIDDEN_TEXT = [
    re.compile("BEGIN " + r"(RSA |OPENSSH |EC |DSA )?" + PRIVATE_KEY_SUFFIX),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(re.escape("/Users/" + "neonwatty/")),
    re.compile("mac" + r"[- ]?mini[- ]?2", re.IGNORECASE),
]

FORBIDDEN_PATH_PARTS = {
    ".git",
    "__pycache__",
    "DerivedData",
    "build",
    "artifacts",
}

TEXT_EXTENSIONS = {
    ".json",
    ".md",
    ".py",
    ".sh",
    ".txt",
    ".yml",
    ".yaml",
}

def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(command: list[str], *, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        fail("command failed: " + " ".join(command))
    return completed


def load_json(path: str) -> dict:
    full_path = ROOT / path
    try:
        value = json.loads(full_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path} must contain a JSON object")
    return value


def check_required_files() -> None:
    missing = [path for path in REQUIRED_FILES + PROOF_RECORDS if not (ROOT / path).is_file()]
    if missing:
        fail("missing required files: " + ", ".join(missing))

    if (ROOT / "docs" / "goals").exists():
        fail("docs/goals must not be present in the public v0 release tree")


def check_manifests() -> None:
    codex = load_json(".codex-plugin/plugin.json")
    claude = load_json(".claude-plugin/plugin.json")
    if codex.get("name") != "apple-agent-kit":
        fail(".codex-plugin/plugin.json name must be apple-agent-kit")
    if claude.get("name") != "apple-agent-kit":
        fail(".claude-plugin/plugin.json name must be apple-agent-kit")
    if codex.get("version") != claude.get("version"):
        fail("Codex and Claude plugin versions must match")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", str(codex.get("version", ""))):
        fail("plugin version must be semver-like")
    if codex.get("skills") != "./skills/":
        fail("Codex manifest must point skills to ./skills/")


def check_cli() -> None:
    run(["python3", "scripts/aak.py", "validate-adapter", "templates/adapter.example.json", "--json"])
    run(["python3", "scripts/aak.py", "validate-manual-remote-job", "templates/manual-remote-pr-session.job-request.example.json", "--json"])
    run(["python3", "scripts/aak.py", "validate-manual-remote-receipt", "templates/manual-remote-pr-session.receipt.example.json", "--json"])
    run(["python3", "scripts/aak.py", "inspect", "--repo", ".", "--adapter", "templates/adapter.example.json", "--json"])
    with tempfile.TemporaryDirectory(prefix="aak-release-render-") as output:
        completed = run(
            [
                "python3",
                "scripts/aak.py",
                "render-workflows",
                "--adapter",
                "templates/adapter.example.json",
                "--output",
                output,
                "--force",
            ]
        )
        payload = json.loads(completed.stdout)
        if payload.get("physical_device_actions") is not False:
            fail("render receipt must assert physical_device_actions=false")
        receipt = Path(output) / "render-receipt.json"
        if not receipt.is_file():
            fail("render workflow receipt was not created")


def iter_public_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        rel_parts = path.relative_to(ROOT).parts
        if any(part in FORBIDDEN_PATH_PARTS for part in rel_parts):
            continue
        if path.is_file() and path.suffix in TEXT_EXTENSIONS:
            files.append(path)
    return files


def check_leakage() -> None:
    offenders: list[str] = []
    for path in iter_public_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN_TEXT:
            if pattern.search(text):
                offenders.append(str(path.relative_to(ROOT)))
                break
    if offenders:
        fail("possible private leakage in: " + ", ".join(sorted(offenders)))


def check_optional_external_validators() -> None:
    if shutil.which("claude"):
        run(["claude", "plugin", "validate", ".", "--strict"])


def main() -> int:
    check_required_files()
    check_manifests()
    check_cli()
    check_leakage()
    check_optional_external_validators()
    print("Apple Agent Kit v0 release validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
