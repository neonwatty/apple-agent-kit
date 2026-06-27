# Install and Reuse

Apple Agent Kit v0 is source-first. The public repo contains generic skills, scripts, workflow templates, and evidence rules. Private app bindings stay outside this repo in private adapters.

## Get the Source

```bash
git clone https://github.com/neonwatty/apple-agent-kit.git
cd apple-agent-kit
python3 scripts/validate-release.py
```

The validator checks plugin manifests, required docs, adapter examples, rendered workflow templates, proof-record links, and public/private leakage guards. It does not build products, boot simulators, install apps, dispatch workflows, start WDA, take screenshots, or touch physical devices.

## Codex

The Codex manifest is:

```text
.codex-plugin/plugin.json
```

For development, validate the source with the Codex plugin validator when it is available:

```bash
python3 path/to/plugin-creator/scripts/validate_plugin.py .
```

To install through Codex, add the plugin through a configured marketplace that points at this repo or a local checkout:

```bash
codex plugin add apple-agent-kit@<marketplace>
```

Use `scripts/validate-release.py` as the source-level fallback when a local Codex marketplace is not configured.

## Claude Code

The Claude Code manifest is:

```text
.claude-plugin/plugin.json
```

Validate it with:

```bash
claude plugin validate . --strict
```

For local session testing without publishing:

```bash
claude --plugin-dir /path/to/apple-agent-kit
```

Claude Code discovers the skill directories under `skills/`. If future commands or hooks call bundled scripts, they should use `${CLAUDE_PLUGIN_ROOT}` for plugin-internal paths.

## Private Adapters

Do not commit filled adapters to this public repo. Keep real values in private app repos or repository secrets:

- project and workspace paths
- scheme names and bundle identifiers
- signing teams and secret names
- runner labels and host details
- device names and physical-device bindings
- product smoke commands and evidence policy choices

Use `templates/adapter.example.json` only as a public-safe example.
