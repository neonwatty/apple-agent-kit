# T001 Scout: v0 Dry-Run Automation Map

## Repo Map

- `.codex-plugin/plugin.json` defines a valid Codex plugin with skills at `./skills/`.
- `README.md` states the intended public/private boundary and says the repo is still at design scaffold stage.
- `docs/design.md` defines the four-layer architecture: skills, scripts, templates, and adapter contract.
- `docs/adapter-contract.md` defines a dependency-free JSON adapter model.
- `docs/privacy-safe-evidence.md` defines the evidence boundary and receipt requirement.
- `scripts/validate-adapter.py` validates the example adapter without third-party dependencies.
- `scripts/inspect-xcode-env.sh` reports host, macOS, Xcode, and simulator availability.
- `templates/github-actions/` contains static workflow templates but no renderer.
- `skills/` contains seven starter playbooks.

## Current Verification Evidence

- `scripts/validate-adapter.py templates/adapter.example.json` passed.
- `PYTHONPATH=/tmp/apple-agent-kit-pydeps python3 /Users/neonwatty/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py /Users/neonwatty/Desktop/apple-agent-kit` passed.
- `scripts/inspect-xcode-env.sh` ran successfully and reported host/Xcode/simulator availability.
- A private-identifier grep over the public repo returned no matches before this note was written.

## Strengths

- The public/private adapter boundary is documented.
- The adapter example and validator are dependency-light.
- Plugin validation already has a known command.
- Skills encode important safety boundaries, especially no physical-device actions without approval.

## Gaps

- There is no unified `aak` command surface.
- Workflow templates are static; users cannot render them from an adapter.
- Repo inspection is documented in a skill but not executable.
- `xcresult` proof is documented in a skill but not executable.
- `inspect-xcode-env.sh` emits raw simulator UUIDs; v0 CLI should support summary output suitable for receipts.
- There is no fixture-based proof that render/inspect/summarize commands work.

## Recommended v0 CLI Shape

Use one dependency-free Python entrypoint:

```text
scripts/aak.py inspect [--repo PATH] [--adapter PATH] [--json]
scripts/aak.py validate-adapter PATH
scripts/aak.py render-workflows --adapter PATH --output DIR [--force]
scripts/aak.py check-xcode [--json]
scripts/aak.py summarize-xcresult PATH [--json]
```

Keep `scripts/validate-adapter.py` as a thin wrapper or shared helper target to avoid breaking existing docs.

## Recommended First Worker Package

Implement the v0 CLI and fixture proof in one coherent slice.

Likely `allowed_files`:

- `scripts/aak.py`
- `scripts/validate-adapter.py`
- `scripts/inspect-xcode-env.sh`
- `templates/**`
- `docs/**`
- `README.md`
- `.gitignore`
- `docs/goals/v0-dry-run-automation/state.yaml`
- `docs/goals/v0-dry-run-automation/notes/**`

Likely verify commands:

- `python3 scripts/aak.py --help`
- `python3 scripts/aak.py validate-adapter templates/adapter.example.json`
- `python3 scripts/aak.py inspect --repo . --adapter templates/adapter.example.json --json`
- `python3 scripts/aak.py render-workflows --adapter templates/adapter.example.json --output /tmp/aak-render --force`
- `python3 scripts/aak.py check-xcode --json`
- `python3 scripts/aak.py summarize-xcresult /tmp/nonexistent.xcresult --json` should fail cleanly.
- `scripts/validate-adapter.py templates/adapter.example.json`
- plugin validation command
- private-identifier grep

## Risks

- Rendering workflows from private adapters could leak private names into generated files; the public repo should only commit generic examples and tests.
- `check-xcode` must not boot simulators, touch physical devices, or print sensitive device rows by default.
- `summarize-xcresult` must fail clearly when a bundle is missing and avoid pretending no tests means success.
- A v0 CLI that only prints prose would not satisfy the oracle.
