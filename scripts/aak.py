#!/usr/bin/env python3
"""Apple Agent Kit v0 dry-run command surface."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "templates" / "github-actions"
SECRET_KEY_RE = re.compile(r"(token|secret|password|api[_-]?key|private[_-]?key)", re.I)
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
REPO_FULL_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
RFC3339_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")
FORBIDDEN_CONTRACT_TEXT = [
    re.compile("BEGIN " + r"(RSA |OPENSSH |EC |DSA )?" + "PRIVATE " + "KEY"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    re.compile(re.escape("/Users/")),
]
FORBIDDEN_RECEIPT_KEYS = {
    "deviceUdid",
    "hostName",
    "hostname",
    "localPath",
    "rawLog",
    "rawLogs",
    "serialNumber",
    "stderr",
    "stdout",
    "udid",
}
IGNORED_DIRS = {
    ".git",
    ".goalbuddy-board",
    ".swiftpm",
    "DerivedData",
    "build",
    "node_modules",
    "artifacts",
}


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def load_json_file(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"adapter file not found: {path}"]
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON: {exc}"]
    except OSError as exc:
        return None, [f"could not read {path}: {exc}"]
    if not isinstance(value, dict):
        return None, ["adapter root must be an object"]
    return value, []


def validate_adapter_data(adapter: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not adapter.get("name"):
        errors.append("adapter.name is required")

    platforms = adapter.get("platforms")
    if not isinstance(platforms, dict) or not platforms:
        errors.append("adapter.platforms must define at least one platform")
    else:
        for platform_name, config in platforms.items():
            if platform_name not in {"macos", "ios"}:
                errors.append(f"unsupported platform: {platform_name}")
                continue
            if not isinstance(config, dict):
                errors.append(f"platform config must be an object: {platform_name}")
                continue
            for key in ("project", "scheme"):
                if not config.get(key):
                    errors.append(f"platforms.{platform_name}.{key} is required")

    privacy = adapter.get("privacy")
    if not isinstance(privacy, dict):
        errors.append("adapter.privacy is required")
    elif "redactSecrets" not in privacy:
        errors.append("adapter.privacy.redactSecrets is required")

    return errors


def require_object(parent: dict[str, Any], key: str, errors: list[str], path: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{path}.{key} must be an object")
        return {}
    return value


def require_string(parent: dict[str, Any], key: str, errors: list[str], path: str, *, allow_empty: bool = False) -> str:
    value = parent.get(key)
    if not isinstance(value, str) or (not allow_empty and not value):
        errors.append(f"{path}.{key} must be a non-empty string")
        return ""
    return value


def require_bool(parent: dict[str, Any], key: str, errors: list[str], path: str) -> bool:
    value = parent.get(key)
    if not isinstance(value, bool):
        errors.append(f"{path}.{key} must be a boolean")
        return False
    return value


def is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def reject_unknown_keys(value: dict[str, Any], allowed: set[str], errors: list[str], path: str) -> None:
    for key in sorted(set(value) - allowed):
        errors.append(f"{path}.{key} is not allowed")


def require_datetime_string(parent: dict[str, Any], key: str, errors: list[str], path: str) -> str:
    value = require_string(parent, key, errors, path)
    if not value:
        return ""
    if not RFC3339_DATETIME_RE.fullmatch(value):
        errors.append(f"{path}.{key} must be an RFC3339 date-time")
        return value
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{path}.{key} must be an RFC3339 date-time")
    return value


def validate_safe_id(value: str, field: str, errors: list[str]) -> None:
    if not SAFE_ID_RE.fullmatch(value):
        errors.append(f"{field} must be a sanitized identifier")


def validate_common_remote_pr_fields(data: dict[str, Any], errors: list[str]) -> None:
    request_id = require_string(data, "requestId", errors, "root")
    if request_id:
        validate_safe_id(request_id, "requestId", errors)

    repository = require_object(data, "repository", errors, "root")
    reject_unknown_keys(repository, {"fullName", "htmlUrl"}, errors, "repository")
    full_name = require_string(repository, "fullName", errors, "repository")
    if full_name and not REPO_FULL_NAME_RE.fullmatch(full_name):
        errors.append("repository.fullName must look like owner/repo")
    require_string(repository, "htmlUrl", errors, "repository")

    pull_request = require_object(data, "pullRequest", errors, "root")
    pr_number = pull_request.get("number")
    if not is_integer(pr_number) or pr_number < 1:
        errors.append("pullRequest.number must be a positive integer")
    require_string(pull_request, "htmlUrl", errors, "pullRequest")

    git = require_object(data, "git", errors, "root")
    reject_unknown_keys(git, {"sha"}, errors, "git")
    sha = require_string(git, "sha", errors, "git")
    if sha and not SHA_RE.fullmatch(sha):
        errors.append("git.sha must be a 40-character commit SHA")


def collect_forbidden_contract_values(value: Any, errors: list[str], path: str = "root") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_RECEIPT_KEYS or SECRET_KEY_RE.search(key):
                errors.append(f"{path}.{key} is not allowed in sanitized manual remote session data")
            collect_forbidden_contract_values(nested, errors, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            collect_forbidden_contract_values(nested, errors, f"{path}[{index}]")
    elif isinstance(value, str):
        for pattern in FORBIDDEN_CONTRACT_TEXT:
            if pattern.search(value):
                errors.append(f"{path} appears to contain private or secret material")
                break


def validate_manual_remote_job_data(job: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    collect_forbidden_contract_values(job, errors)
    reject_unknown_keys(
        job,
        {
            "schemaVersion",
            "kind",
            "requestId",
            "requestedAt",
            "repository",
            "pullRequest",
            "git",
            "target",
            "actions",
            "codexSession",
            "evidencePolicy",
            "gates",
            "requester",
            "validation",
        },
        errors,
        "root",
    )

    if job.get("schemaVersion") != "manual-remote-pr-session/v1":
        errors.append("schemaVersion must be manual-remote-pr-session/v1")
    if job.get("kind") != "manual-remote-pr-session.job-request":
        errors.append("kind must be manual-remote-pr-session.job-request")
    require_datetime_string(job, "requestedAt", errors, "root")
    validate_common_remote_pr_fields(job, errors)

    pull_request = job.get("pullRequest") if isinstance(job.get("pullRequest"), dict) else {}
    reject_unknown_keys(pull_request, {"number", "htmlUrl", "baseRef", "headRef"}, errors, "pullRequest")
    require_string(pull_request, "baseRef", errors, "pullRequest")
    require_string(pull_request, "headRef", errors, "pullRequest")

    target = require_object(job, "target", errors, "root")
    reject_unknown_keys(target, {"hostProfileAlias", "runProfile"}, errors, "target")
    host_alias = require_string(target, "hostProfileAlias", errors, "target")
    run_profile = require_string(target, "runProfile", errors, "target")
    if host_alias:
        validate_safe_id(host_alias, "target.hostProfileAlias", errors)
    if run_profile:
        validate_safe_id(run_profile, "target.runProfile", errors)

    actions = require_object(job, "actions", errors, "root")
    reject_unknown_keys(actions, {"runTests", "launchApp", "createCodexSession", "physicalDevice"}, errors, "actions")
    require_bool(actions, "runTests", errors, "actions")
    require_bool(actions, "launchApp", errors, "actions")
    require_bool(actions, "createCodexSession", errors, "actions")
    physical_device = require_bool(actions, "physicalDevice", errors, "actions")
    if "commands" in job:
        errors.append("job requests must not contain commands; commands come from private adapters")

    codex_session = job.get("codexSession")
    if codex_session is not None:
        if not isinstance(codex_session, dict):
            errors.append("codexSession must be an object when present")
        else:
            reject_unknown_keys(codex_session, {"instructions"}, errors, "codexSession")
            instructions = codex_session.get("instructions", "")
            if not isinstance(instructions, str):
                errors.append("codexSession.instructions must be a string")
            elif len(instructions) > 4000:
                errors.append("codexSession.instructions must be 4000 characters or fewer")

    evidence = require_object(job, "evidencePolicy", errors, "root")
    reject_unknown_keys(evidence, {"artifactMode", "allowedArtifactGlobs"}, errors, "evidencePolicy")
    artifact_mode = require_string(evidence, "artifactMode", errors, "evidencePolicy")
    if artifact_mode and artifact_mode not in {"receipt-only", "allowlist"}:
        errors.append("evidencePolicy.artifactMode must be receipt-only or allowlist")
    allowed_globs = evidence.get("allowedArtifactGlobs")
    if not isinstance(allowed_globs, list) or not all(isinstance(item, str) and item for item in allowed_globs):
        errors.append("evidencePolicy.allowedArtifactGlobs must be a list of non-empty strings")
    if artifact_mode == "receipt-only" and allowed_globs:
        errors.append("receipt-only jobs must not request allowed artifacts")

    gates = require_object(job, "gates", errors, "root")
    reject_unknown_keys(gates, {"physicalDeviceApproval", "approvalRef"}, errors, "gates")
    approval = require_string(gates, "physicalDeviceApproval", errors, "gates")
    approval_ref = require_string(gates, "approvalRef", errors, "gates", allow_empty=True)
    if approval and approval not in {"disabled", "explicit-private-approval"}:
        errors.append("gates.physicalDeviceApproval must be disabled or explicit-private-approval")
    if physical_device and (approval != "explicit-private-approval" or not approval_ref):
        errors.append("physical-device jobs require explicit-private-approval and a non-empty approvalRef")
    if not physical_device and approval != "disabled":
        errors.append("physical-device approval must be disabled when actions.physicalDevice is false")

    requester = require_object(job, "requester", errors, "root")
    reject_unknown_keys(requester, {"actor", "workflowRunId", "workflowRunAttempt"}, errors, "requester")
    require_string(requester, "actor", errors, "requester")
    require_string(requester, "workflowRunId", errors, "requester")
    require_string(requester, "workflowRunAttempt", errors, "requester")

    validation = require_object(job, "validation", errors, "root")
    reject_unknown_keys(validation, {"status", "validatedAt", "validator"}, errors, "validation")
    if validation.get("status") != "validated":
        errors.append("validation.status must be validated")
    require_datetime_string(validation, "validatedAt", errors, "validation")
    require_string(validation, "validator", errors, "validation")

    return errors


def validate_manual_remote_receipt_data(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    collect_forbidden_contract_values(receipt, errors)
    reject_unknown_keys(
        receipt,
        {
            "schemaVersion",
            "kind",
            "requestId",
            "repository",
            "pullRequest",
            "git",
            "hostProfileAlias",
            "startedAt",
            "completedAt",
            "result",
            "commands",
            "launch",
            "codexSession",
            "physicalDevice",
            "artifacts",
            "redactions",
        },
        errors,
        "root",
    )

    if receipt.get("schemaVersion") != "manual-remote-pr-session/v1":
        errors.append("schemaVersion must be manual-remote-pr-session/v1")
    if receipt.get("kind") != "manual-remote-pr-session.receipt":
        errors.append("kind must be manual-remote-pr-session.receipt")
    validate_common_remote_pr_fields(receipt, errors)

    pull_request = receipt.get("pullRequest") if isinstance(receipt.get("pullRequest"), dict) else {}
    reject_unknown_keys(pull_request, {"number", "htmlUrl"}, errors, "pullRequest")
    host_alias = require_string(receipt, "hostProfileAlias", errors, "root")
    if host_alias:
        validate_safe_id(host_alias, "hostProfileAlias", errors)
    require_datetime_string(receipt, "startedAt", errors, "root")
    require_datetime_string(receipt, "completedAt", errors, "root")
    result = require_string(receipt, "result", errors, "root")
    if result and result not in {"succeeded", "failed", "canceled", "rejected", "timed-out"}:
        errors.append("result must be succeeded, failed, canceled, rejected, or timed-out")

    commands = receipt.get("commands")
    if not isinstance(commands, list):
        errors.append("commands must be a list")
    else:
        for index, command in enumerate(commands):
            path = f"commands[{index}]"
            if not isinstance(command, dict):
                errors.append(f"{path} must be an object")
                continue
            reject_unknown_keys(command, {"id", "class", "summary", "durationSeconds", "exitCode", "result"}, errors, path)
            command_id = require_string(command, "id", errors, path)
            if command_id:
                validate_safe_id(command_id, f"{path}.id", errors)
            command_class = require_string(command, "class", errors, path)
            if command_class:
                validate_safe_id(command_class, f"{path}.class", errors)
            summary = require_string(command, "summary", errors, path)
            if summary and len(summary) > 240:
                errors.append(f"{path}.summary must be 240 characters or fewer")
            duration = command.get("durationSeconds")
            if not is_number(duration) or duration < 0:
                errors.append(f"{path}.durationSeconds must be a non-negative number")
            if not is_integer(command.get("exitCode")):
                errors.append(f"{path}.exitCode must be an integer")
            command_result = require_string(command, "result", errors, path)
            if command_result and command_result not in {"succeeded", "failed", "canceled", "skipped", "timed-out"}:
                errors.append(f"{path}.result has an unsupported value")

    launch = require_object(receipt, "launch", errors, "root")
    reject_unknown_keys(launch, {"requested", "result"}, errors, "launch")
    require_bool(launch, "requested", errors, "launch")
    launch_result = require_string(launch, "result", errors, "launch")
    if launch_result and launch_result not in {"not-requested", "succeeded", "failed", "skipped"}:
        errors.append("launch.result has an unsupported value")

    codex = require_object(receipt, "codexSession", errors, "root")
    reject_unknown_keys(codex, {"requested", "created", "sessionRef", "instructionsDigest"}, errors, "codexSession")
    require_bool(codex, "requested", errors, "codexSession")
    require_bool(codex, "created", errors, "codexSession")
    require_string(codex, "sessionRef", errors, "codexSession", allow_empty=True)
    require_string(codex, "instructionsDigest", errors, "codexSession", allow_empty=True)

    physical = require_object(receipt, "physicalDevice", errors, "root")
    reject_unknown_keys(physical, {"requested", "gate", "approvalRef"}, errors, "physicalDevice")
    physical_requested = require_bool(physical, "requested", errors, "physicalDevice")
    gate = require_string(physical, "gate", errors, "physicalDevice")
    approval_ref = require_string(physical, "approvalRef", errors, "physicalDevice", allow_empty=True)
    if gate and gate not in {"disabled", "explicit-private-approval"}:
        errors.append("physicalDevice.gate must be disabled or explicit-private-approval")
    if physical_requested and (gate != "explicit-private-approval" or not approval_ref):
        errors.append("physical-device receipts require explicit-private-approval and a non-empty approvalRef")
    if not physical_requested and gate != "disabled":
        errors.append("physicalDevice.gate must be disabled when physicalDevice.requested is false")

    artifacts = require_object(receipt, "artifacts", errors, "root")
    reject_unknown_keys(artifacts, {"allowed", "withheld"}, errors, "artifacts")
    allowed = artifacts.get("allowed")
    if not isinstance(allowed, list):
        errors.append("artifacts.allowed must be a list")
    else:
        for index, artifact in enumerate(allowed):
            path = f"artifacts.allowed[{index}]"
            if not isinstance(artifact, dict):
                errors.append(f"{path} must be an object")
                continue
            reject_unknown_keys(artifact, {"label", "path", "sha256", "sizeBytes"}, errors, path)
            require_string(artifact, "label", errors, path)
            artifact_path = require_string(artifact, "path", errors, path)
            if artifact_path.startswith("/") or artifact_path.startswith("~") or ".." in Path(artifact_path).parts:
                errors.append(f"{path}.path must be a relative sanitized path or storage ID")
            sha256 = require_string(artifact, "sha256", errors, path)
            if sha256 and not re.fullmatch(r"^[0-9a-fA-F]{64}$", sha256):
                errors.append(f"{path}.sha256 must be a SHA-256 hex digest")
            if not is_integer(artifact.get("sizeBytes")) or artifact.get("sizeBytes") < 0:
                errors.append(f"{path}.sizeBytes must be a non-negative integer")

    withheld = artifacts.get("withheld")
    if not isinstance(withheld, list):
        errors.append("artifacts.withheld must be a list")
    else:
        for index, artifact in enumerate(withheld):
            path = f"artifacts.withheld[{index}]"
            if not isinstance(artifact, dict):
                errors.append(f"{path} must be an object")
                continue
            reject_unknown_keys(artifact, {"label", "reason"}, errors, path)
            require_string(artifact, "label", errors, path)
            require_string(artifact, "reason", errors, path)

    redactions = receipt.get("redactions")
    if not isinstance(redactions, list) or not all(isinstance(item, str) and item for item in redactions):
        errors.append("redactions must be a list of non-empty strings")

    return errors


def load_and_validate_adapter(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    adapter, errors = load_json_file(path)
    if adapter is None:
        return None, errors
    return adapter, validate_adapter_data(adapter)


def redact_value(key: str, value: Any) -> Any:
    if SECRET_KEY_RE.search(key):
        return "<redacted>"
    if isinstance(value, dict):
        return {nested_key: redact_value(nested_key, nested_value) for nested_key, nested_value in value.items()}
    if isinstance(value, list):
        return [redact_value(key, item) for item in value]
    return value


def summarize_adapter(adapter: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": adapter.get("name"),
        "platforms": sorted((adapter.get("platforms") or {}).keys()),
        "ci": redact_value("ci", adapter.get("ci", {})),
        "privacy": redact_value("privacy", adapter.get("privacy", {})),
    }


def command_validate_adapter_path(path: Path, *, json_output: bool = False) -> int:
    adapter, errors = load_and_validate_adapter(path)
    if errors:
        if json_output:
            emit_json({"ok": False, "path": str(path), "errors": errors})
        else:
            for error in errors:
                eprint(f"error: {error}")
        return 1

    assert adapter is not None
    if json_output:
        emit_json({"ok": True, "path": str(path), "adapter": summarize_adapter(adapter)})
    else:
        print(f"valid adapter: {adapter['name']}")
    return 0


def command_validate_manual_remote_job_path(path: Path, *, json_output: bool = False) -> int:
    job, errors = load_json_file(path)
    if job is not None:
        errors.extend(validate_manual_remote_job_data(job))
    if errors:
        if json_output:
            emit_json({"ok": False, "path": str(path), "errors": errors})
        else:
            for error in errors:
                eprint(f"error: {error}")
        return 1
    assert job is not None
    if json_output:
        emit_json({
            "ok": True,
            "path": str(path),
            "requestId": job.get("requestId"),
            "sha": (job.get("git") or {}).get("sha"),
            "physical_device_actions": bool((job.get("actions") or {}).get("physicalDevice")),
        })
    else:
        print(f"valid manual remote PR job: {job['requestId']}")
    return 0


def command_validate_manual_remote_receipt_path(path: Path, *, json_output: bool = False) -> int:
    receipt, errors = load_json_file(path)
    if receipt is not None:
        errors.extend(validate_manual_remote_receipt_data(receipt))
    if errors:
        if json_output:
            emit_json({"ok": False, "path": str(path), "errors": errors})
        else:
            for error in errors:
                eprint(f"error: {error}")
        return 1
    assert receipt is not None
    if json_output:
        emit_json({
            "ok": True,
            "path": str(path),
            "requestId": receipt.get("requestId"),
            "result": receipt.get("result"),
            "physical_device_actions": bool((receipt.get("physicalDevice") or {}).get("requested")),
        })
    else:
        print(f"valid manual remote PR receipt: {receipt['requestId']}")
    return 0


def iter_repo_files(repo: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.relative_to(repo).parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def relative_paths(paths: list[Path], repo: Path) -> list[str]:
    return sorted(str(path.relative_to(repo)) for path in paths)


def inspect_repo(repo: Path, adapter_path: Path | None) -> dict[str, Any]:
    files = iter_repo_files(repo)
    workflows = [path for path in files if path.parts[-3:-1] == (".github", "workflows")]
    scripts = [path for path in files if len(path.relative_to(repo).parts) >= 2 and path.relative_to(repo).parts[0] == "scripts"]
    test_paths = [
        path
        for path in files
        if any("test" in part.lower() or "uitest" in part.lower() for part in path.relative_to(repo).parts)
    ]

    project_files = [path for path in files if path.name.endswith((".xcodeproj", ".xcworkspace"))]
    project_dirs = [
        path
        for path in repo.rglob("*")
        if not any(part in IGNORED_DIRS for part in path.relative_to(repo).parts)
        and path.is_dir()
        and path.name.endswith((".xcodeproj", ".xcworkspace"))
    ]

    adapter_summary: dict[str, Any] | None = None
    adapter_errors: list[str] = []
    if adapter_path is not None:
        adapter, adapter_errors = load_and_validate_adapter(adapter_path)
        if adapter is not None:
            adapter_summary = summarize_adapter(adapter)

    return {
        "ok": not adapter_errors,
        "timestamp": now_iso(),
        "repo": str(repo),
        "xcode_projects": sorted(
            {str(path.relative_to(repo)) for path in project_dirs + project_files}
        ),
        "xcodegen": (repo / "project.yml").is_file(),
        "swift_package": (repo / "Package.swift").is_file(),
        "makefile": any((repo / name).is_file() for name in ("Makefile", "makefile")),
        "workflow_files": relative_paths(workflows, repo),
        "script_files": relative_paths(scripts, repo),
        "test_files": relative_paths(test_paths[:100], repo),
        "adapter": adapter_summary,
        "adapter_errors": adapter_errors,
        "recommended_next_track": recommend_track(project_dirs + project_files, workflows, scripts, test_paths),
    }


def recommend_track(
    project_paths: list[Path],
    workflows: list[Path],
    scripts: list[Path],
    test_paths: list[Path],
) -> str:
    if not project_paths:
        return "add adapter and project/workspace discovery"
    if not workflows:
        return "render CI workflow templates"
    if not test_paths:
        return "add result-bundle test coverage"
    if not scripts:
        return "add repo-native command wrappers"
    return "audit proof quality and dry-run adapter fit"


def command_inspect(args: argparse.Namespace) -> int:
    repo = Path(args.repo).expanduser().resolve()
    if not repo.is_dir():
        eprint(f"error: repo not found: {repo}")
        return 66
    adapter_path = Path(args.adapter).expanduser().resolve() if args.adapter else None
    payload = inspect_repo(repo, adapter_path)
    if args.json:
        emit_json(payload)
    else:
        print(f"repo: {payload['repo']}")
        print(f"xcode projects: {len(payload['xcode_projects'])}")
        print(f"workflow files: {len(payload['workflow_files'])}")
        print(f"script files: {len(payload['script_files'])}")
        print(f"test files: {len(payload['test_files'])}")
        print(f"recommended next track: {payload['recommended_next_track']}")
        if payload["adapter_errors"]:
            for error in payload["adapter_errors"]:
                eprint(f"adapter error: {error}")
    return 0 if payload["ok"] else 1


def render_text(template_name: str, text: str, adapter: dict[str, Any]) -> str:
    ci = adapter.get("ci") or {}
    macos_runner = ci.get("macosRunner") or "macos-15"
    macos_runner_labels = ci.get("macosRunnerLabels") or ["self-hosted", "macOS", "apple-agent-kit"]
    if not isinstance(macos_runner_labels, list) or not all(isinstance(item, str) for item in macos_runner_labels):
        macos_runner_labels = ["self-hosted", "macOS", "apple-agent-kit"]
    physical_labels = ci.get("physicalRunnerLabels") or ["self-hosted", "macOS", "ios-physical"]
    if not isinstance(physical_labels, list) or not all(isinstance(item, str) for item in physical_labels):
        physical_labels = ["self-hosted", "macOS", "ios-physical"]

    if template_name == "macos-ci.yml":
        text = text.replace("runs-on: macos-15", f"runs-on: {macos_runner}")
    if template_name in {"ios-simulator-ci.yml", "ios-ci-eligibility.yml"}:
        text = text.replace("runs-on: macos-15", f"runs-on: {macos_runner}")
    if template_name == "ios-physical-device.yml":
        label_text = "[" + ", ".join(physical_labels) + "]"
        text = re.sub(r"runs-on: \[[^\n]+\]", f"runs-on: {label_text}", text)
    if template_name in {"macos-runner-health.yml", "macos-ci-eligibility.yml"}:
        label_text = "[" + ", ".join(macos_runner_labels) + "]"
        text = re.sub(r"runs-on: \[[^\n]+\]", f"runs-on: {label_text}", text)
    return text


def command_render_workflows(args: argparse.Namespace) -> int:
    adapter_path = Path(args.adapter).expanduser().resolve()
    adapter, errors = load_and_validate_adapter(adapter_path)
    if errors:
        for error in errors:
            eprint(f"error: {error}")
        return 1
    assert adapter is not None

    output = Path(args.output).expanduser().resolve()
    if output.exists() and any(output.iterdir()) and not args.force:
        eprint(f"error: output directory is not empty: {output} (use --force)")
        return 73
    output.mkdir(parents=True, exist_ok=True)

    rendered: list[str] = []
    for template in sorted(TEMPLATE_DIR.glob("*.yml")):
        destination = output / template.name
        destination.write_text(render_text(template.name, template.read_text(encoding="utf-8"), adapter), encoding="utf-8")
        rendered.append(str(destination))

    receipt = {
        "ok": True,
        "timestamp": now_iso(),
        "adapter": summarize_adapter(adapter),
        "template_dir": str(TEMPLATE_DIR),
        "output": str(output),
        "rendered": rendered,
        "dry_run": True,
        "physical_device_actions": False,
    }
    (output / "render-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    emit_json(receipt)
    return 0


def run_command(command: list[str], timeout: int = 20) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, "", f"{command[0]} not found"
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or "command timed out"
    return completed.returncode, completed.stdout, completed.stderr


def command_check_xcode(args: argparse.Namespace) -> int:
    payload: dict[str, Any] = {
        "ok": True,
        "timestamp": now_iso(),
        "host": platform.node(),
        "user": os.environ.get("USER") or "",
        "arch": platform.machine(),
        "tools": {
            "xcodebuild": shutil.which("xcodebuild") is not None,
            "xcrun": shutil.which("xcrun") is not None,
        },
        "physical_device_actions": False,
    }

    status, stdout, stderr = run_command(["sw_vers"])
    payload["macos"] = {"status": status, "output": stdout.strip(), "error": stderr.strip()}
    if status != 0:
        payload["ok"] = False

    status, stdout, stderr = run_command(["xcodebuild", "-version"])
    payload["xcode"] = {"status": status, "output": stdout.strip(), "error": stderr.strip()}
    if status != 0:
        payload["ok"] = False

    runtime_counts: dict[str, int] = {}
    if payload["tools"]["xcrun"]:
        status, stdout, stderr = run_command(["xcrun", "simctl", "list", "devices", "available"], timeout=30)
        current_runtime = "unknown"
        for line in stdout.splitlines():
            if line.startswith("-- ") and line.endswith(" --"):
                current_runtime = line.strip("- ")
                runtime_counts.setdefault(current_runtime, 0)
            elif line.startswith("    "):
                runtime_counts[current_runtime] = runtime_counts.get(current_runtime, 0) + 1
        payload["simulators"] = {
            "status": status,
            "runtime_device_counts": runtime_counts,
            "error": stderr.strip(),
        }
    else:
        payload["simulators"] = {"status": 127, "runtime_device_counts": {}, "error": "xcrun not found"}
        payload["ok"] = False

    if args.json:
        emit_json(payload)
    else:
        print("Apple Agent Kit Xcode environment")
        print(f"host={payload['host']}")
        print(f"user={payload['user']}")
        print(f"arch={payload['arch']}")
        print(payload["macos"]["output"])
        print(payload["xcode"]["output"] or payload["xcode"]["error"])
        print("simulator runtimes:")
        for runtime, count in sorted(runtime_counts.items()):
            print(f"  {runtime}: {count}")
    return 0 if payload["ok"] else 69


def command_summarize_xcresult(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    if not path.exists():
        payload = {"ok": False, "path": str(path), "error": "xcresult bundle not found"}
        if args.json:
            emit_json(payload)
        else:
            eprint(f"error: {payload['error']}: {path}")
        return 66

    payload: dict[str, Any] = {
        "ok": True,
        "timestamp": now_iso(),
        "path": str(path),
        "summary": None,
        "coverage": None,
        "errors": [],
    }

    status, stdout, stderr = run_command(
        ["xcrun", "xcresulttool", "get", "test-results", "summary", "--path", str(path), "--compact"],
        timeout=30,
    )
    if status == 0 and stdout.strip():
        try:
            payload["summary"] = json.loads(stdout)
        except json.JSONDecodeError:
            payload["summary"] = stdout.strip()
    else:
        payload["ok"] = False
        payload["errors"].append(stderr.strip() or "could not parse xcresult test summary")

    status, stdout, stderr = run_command(["xcrun", "xccov", "view", "--report", str(path)], timeout=30)
    if status == 0 and stdout.strip():
        payload["coverage"] = stdout.strip()
    elif stderr.strip():
        payload["errors"].append(stderr.strip())

    if args.json:
        emit_json(payload)
    else:
        print(f"xcresult: {path}")
        if payload["summary"] is not None:
            print(json.dumps(payload["summary"], indent=2, sort_keys=True) if isinstance(payload["summary"], dict) else payload["summary"])
        for error in payload["errors"]:
            eprint(f"warning: {error}")
    return 0 if payload["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aak",
        description="Apple Agent Kit dry-run automation commands.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect an Apple app repo without changing it.")
    inspect_parser.add_argument("--repo", default=".", help="Repository path to inspect.")
    inspect_parser.add_argument("--adapter", help="Optional adapter JSON path to validate and summarize.")
    inspect_parser.add_argument("--json", action="store_true", help="Emit JSON.")
    inspect_parser.set_defaults(func=command_inspect)

    validate_parser = subparsers.add_parser("validate-adapter", help="Validate an Apple Agent Kit adapter JSON file.")
    validate_parser.add_argument("path", help="Adapter JSON path.")
    validate_parser.add_argument("--json", action="store_true", help="Emit JSON.")
    validate_parser.set_defaults(func=lambda args: command_validate_adapter_path(Path(args.path), json_output=args.json))

    manual_job_parser = subparsers.add_parser(
        "validate-manual-remote-job",
        help="Validate a Manual Remote PR Session job request JSON file.",
    )
    manual_job_parser.add_argument("path", help="Manual remote PR session job request JSON path.")
    manual_job_parser.add_argument("--json", action="store_true", help="Emit JSON.")
    manual_job_parser.set_defaults(
        func=lambda args: command_validate_manual_remote_job_path(Path(args.path), json_output=args.json)
    )

    manual_receipt_parser = subparsers.add_parser(
        "validate-manual-remote-receipt",
        help="Validate a Manual Remote PR Session proof receipt JSON file.",
    )
    manual_receipt_parser.add_argument("path", help="Manual remote PR session receipt JSON path.")
    manual_receipt_parser.add_argument("--json", action="store_true", help="Emit JSON.")
    manual_receipt_parser.set_defaults(
        func=lambda args: command_validate_manual_remote_receipt_path(Path(args.path), json_output=args.json)
    )

    render_parser = subparsers.add_parser("render-workflows", help="Render workflow templates from an adapter.")
    render_parser.add_argument("--adapter", required=True, help="Adapter JSON path.")
    render_parser.add_argument("--output", required=True, help="Output directory.")
    render_parser.add_argument("--force", action="store_true", help="Allow writing into a non-empty output directory.")
    render_parser.set_defaults(func=command_render_workflows)

    xcode_parser = subparsers.add_parser("check-xcode", help="Summarize local Xcode readiness without device actions.")
    xcode_parser.add_argument("--json", action="store_true", help="Emit JSON.")
    xcode_parser.set_defaults(func=command_check_xcode)

    xcresult_parser = subparsers.add_parser("summarize-xcresult", help="Summarize an existing xcresult bundle.")
    xcresult_parser.add_argument("path", help="Path to an existing .xcresult bundle.")
    xcresult_parser.add_argument("--json", action="store_true", help="Emit JSON.")
    xcresult_parser.set_defaults(func=command_summarize_xcresult)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
