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
