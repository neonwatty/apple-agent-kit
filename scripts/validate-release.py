#!/usr/bin/env python3
"""Validate the public Apple Agent Kit v0 release surface."""

from __future__ import annotations

import json
import os
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
    "AGENTS.md",
    "CHANGELOG.md",
    "LICENSE",
    "README.md",
    "docs/adapter-contract.md",
    "docs/adopting-ios-simulator-fixture-ui-smoke.md",
    "docs/adopting-macos-fixture-ui-smoke.md",
    "docs/install.md",
    "docs/manual-remote-pr-session.md",
    "docs/privacy-safe-evidence.md",
    "docs/private-adapter-rollout-checklist.md",
    "docs/slim-codex-autoreview.md",
    "docs/proof-records/index.md",
    "docs/v0-release-readiness.md",
    "scripts/aak.py",
    "skills/codex-autoreview/SKILL.md",
    "skills/codex-pr-closeout-review/SKILL.md",
    "skills/codex-pr-closeout-review/scripts/codex-pr-review",
    "skills/ios-simulator-fixture-ui-smoke/SKILL.md",
    "skills/macos-fixture-ui-smoke/SKILL.md",
    "schemas/fixture-ui-smoke.receipt.schema.json",
    "schemas/manual-remote-pr-session.job-request.schema.json",
    "schemas/manual-remote-pr-session.receipt.schema.json",
    "templates/adapter.example.json",
    "templates/fixture-ui-smoke-command.example.sh",
    "templates/fixture-ui-smoke.receipt.example.json",
    "templates/ios-simulator-fixture-ui-smoke.receipt.example.json",
    "templates/github-actions/ios-simulator-fixture-ui-smoke.yml",
    "templates/github-actions/macos-fixture-ui-smoke.yml",
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
    ".goalbuddy-board",
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
    tracked_goals = subprocess.run(
        ["git", "ls-files", "docs/goals"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if tracked_goals.stdout.strip():
        fail("docs/goals must not be tracked in the public v0 release tree")
    tracked_files = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    tracked_goalbuddy_boards = [
        path
        for path in tracked_files.stdout.splitlines()
        if ".goalbuddy-board" in Path(path).parts
    ]
    if tracked_goalbuddy_boards:
        fail(".goalbuddy-board must not be tracked in the public v0 release tree")


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
    load_json("schemas/fixture-ui-smoke.receipt.schema.json")
    with tempfile.TemporaryDirectory(prefix="aak-fixture-prepare-") as fixture_output:
        run([
            "python3",
            "scripts/aak.py",
            "prepare-fixture-ui-smoke",
            "--adapter",
            "templates/adapter.example.json",
            "--script",
            str(Path(fixture_output) / "fixture-ui-smoke.sh"),
            "--approval",
            "fixture-ui-smoke",
            "--json",
        ])
        run([
            "python3",
            "scripts/aak.py",
            "prepare-fixture-ui-smoke",
            "--adapter",
            "templates/adapter.example.json",
            "--script",
            str(Path(fixture_output) / "ios-simulator-fixture-ui-smoke.sh"),
            "--approval",
            "fixture-ui-smoke",
            "--platform",
            "ios",
            "--json",
        ])
    with tempfile.TemporaryDirectory(prefix="aak-fixture-command-") as fixture_output:
        receipt_path = Path(fixture_output) / "artifacts" / "fixture-ui-smoke" / "fixture-ui-smoke.receipt.json"
        log_path = Path(fixture_output) / "artifacts" / "fixture-ui-smoke" / "fixture.log"
        subprocess.run(
            ["bash", str(ROOT / "templates" / "fixture-ui-smoke-command.example.sh")],
            cwd=fixture_output,
            check=True,
            env={
                **os.environ,
                "AAK_FIXTURE_RECEIPT_PATH": str(receipt_path.relative_to(fixture_output)),
                "AAK_FIXTURE_LOG_PATH": str(log_path.relative_to(fixture_output)),
            },
        )
        run(["python3", "scripts/aak.py", "validate-fixture-ui-smoke-receipt", str(receipt_path), "--json"])
    run(["python3", "scripts/aak.py", "validate-fixture-ui-smoke-receipt", "templates/fixture-ui-smoke.receipt.example.json", "--json"])
    run(["python3", "scripts/aak.py", "validate-fixture-ui-smoke-receipt", "templates/ios-simulator-fixture-ui-smoke.receipt.example.json", "--json"])
    run(["python3", "scripts/aak.py", "validate-manual-remote-job", "templates/manual-remote-pr-session.job-request.example.json", "--json"])
    run(["python3", "scripts/aak.py", "validate-manual-remote-receipt", "templates/manual-remote-pr-session.receipt.example.json", "--json"])
    run(["python3", "scripts/aak.py", "inspect", "--repo", ".", "--adapter", "templates/adapter.example.json", "--json"])
    run(["python3", "skills/codex-pr-closeout-review/scripts/codex-pr-review", "--self-test"])
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
        fixture_workflow = Path(output) / "macos-fixture-ui-smoke.yml"
        if not fixture_workflow.is_file():
            fail("fixture UI smoke workflow was not rendered")
        fixture_workflow_text = fixture_workflow.read_text(encoding="utf-8")
        if "runs-on: [self-hosted, macOS, apple-agent-kit]" not in fixture_workflow_text:
            fail("fixture UI smoke workflow did not render macOS runner labels")
        if "id: validate-fixture-receipt" not in fixture_workflow_text:
            fail("fixture UI smoke workflow must identify the receipt validation step")
        if "Reset fixture UI smoke receipt" not in fixture_workflow_text:
            fail("fixture UI smoke workflow must remove stale receipts before running")
        if "steps.validate-fixture-receipt.outcome == 'success'" not in fixture_workflow_text:
            fail("fixture UI smoke workflow must gate evidence upload on receipt validation")
        ios_fixture_workflow = Path(output) / "ios-simulator-fixture-ui-smoke.yml"
        if not ios_fixture_workflow.is_file():
            fail("iOS simulator fixture UI smoke workflow was not rendered")
        ios_fixture_workflow_text = ios_fixture_workflow.read_text(encoding="utf-8")
        if "runs-on: macos-15" not in ios_fixture_workflow_text:
            fail("iOS simulator fixture UI smoke workflow did not render macOS runner")
        if "id: validate-fixture-receipt" not in ios_fixture_workflow_text:
            fail("iOS simulator fixture UI smoke workflow must identify the receipt validation step")
        if "Reset fixture UI smoke receipt" not in ios_fixture_workflow_text:
            fail("iOS simulator fixture UI smoke workflow must remove stale receipts before running")
        if "steps.validate-fixture-receipt.outcome == 'success'" not in ios_fixture_workflow_text:
            fail("iOS simulator fixture UI smoke workflow must gate evidence upload on receipt validation")
        ios_eligibility_workflow = Path(output) / "ios-ci-eligibility.yml"
        if not ios_eligibility_workflow.is_file():
            fail("iOS eligibility workflow was not rendered")
        if "check-xcode --adapter .apple-agent-kit.json --platform ios --json" not in ios_eligibility_workflow.read_text(encoding="utf-8"):
            fail("iOS eligibility workflow must render adapter-aware Xcode readiness")


def iter_public_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        rel_parts = path.relative_to(ROOT).parts
        if rel_parts[:2] == ("docs", "goals"):
            continue
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
