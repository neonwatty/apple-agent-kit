# Self-Hosted Runner Scope and Onboarding

Use this guide when a private adapter needs a self-hosted Mac runner and the first workflow stays queued. The goal is to prove runner scope before changing product CI.

The preferred path is an organization runner group that grants selected repositories access to one managed Mac. When that is not possible because an existing runner is repo-scoped, install a separate repo-scoped runner service beside the existing service and give it its own runner directory, service label, and work folder.

## Decision Tree

1. Check repo-visible runners:

```bash
gh api repos/OWNER/REPO/actions/runners --paginate \
  | jq '.runners[]? | {id,name,status,busy,labels:[.labels[].name]}'
```

2. Check org runners and runner groups when the token has org runner permissions:

```bash
gh api orgs/OWNER/actions/runners --paginate \
  | jq '.runners[]? | {id,name,status,busy,labels:[.labels[].name]}'

gh api orgs/OWNER/actions/runner-groups --paginate \
  | jq '.runner_groups[]? | {id,name,visibility,selected_repositories_url,runners_url}'
```

3. Choose the path:

- If the target runner appears under org runners, grant the target repo through the runner group.
- If the target runner appears only under one repository, treat it as repo-scoped.
- If the target repo has no visible self-hosted runner and the runner is repo-scoped elsewhere, install a second repo-scoped runner service.
- If the host is already busy with product or device automation, stop and wait for the hardware to go idle before installing or validating a new runner.

## Org Runner Group Path

Use an org runner group when possible.

Checklist:

- Token has the required org runner permissions.
- Runner group contains the intended Mac runner.
- Runner group allows selected repositories, or visibility is intentionally `all`.
- Target repo is selected for the runner group.
- Repo-visible runner list shows the expected labels.
- A device-free runner health or eligibility workflow starts and completes.

## Repo-Scoped Fallback Path

Use a separate repo-scoped runner when the existing runner cannot be shared through an org runner group.

Rules:

- Do not reconfigure an existing runner directory.
- Do not stop or uninstall an existing runner service unless explicitly approved.
- Create a new directory for the new repo, such as `~/actions-runner-repo-name`.
- Use a distinct runner name, such as `repo-name-mac-mini-2`.
- Keep a distinct work folder inside that runner directory.
- Add a repo-specific label in addition to the hardware label.
- Verify both old and new services are running after installation.

Example registration shape:

```bash
TOKEN="$(gh api repos/OWNER/REPO/actions/runners/registration-token --method POST --jq .token)"
ssh HOST TOKEN="$TOKEN" 'bash -s' <<'REMOTE'
set -euo pipefail
RUNNER_VERSION="2.335.1"
RUNNER_DIR="$HOME/actions-runner-repo-name"
RUNNER_TARBALL="$HOME/actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz"
RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz"

mkdir -p "$RUNNER_DIR"
if [ ! -f "$RUNNER_TARBALL" ]; then
  curl -fsSL "$RUNNER_URL" -o "$RUNNER_TARBALL"
fi

tar -xzf "$RUNNER_TARBALL" -C "$RUNNER_DIR"
cd "$RUNNER_DIR"
./config.sh \
  --unattended \
  --url https://github.com/OWNER/REPO \
  --token "$TOKEN" \
  --name repo-name-mac-mini-2 \
  --work _work \
  --labels mac-mini-2,repo-name \
  --replace
./svc.sh install
./svc.sh start
./svc.sh status
REMOTE
```

Do not print registration tokens in logs. Fetch the token locally and pass it through environment or standard input.

## Public Repo Adapter Privacy

For private repos, committing `.apple-agent-kit.json` to the private app repo may be acceptable.

For public repos, keep the adapter private by storing it in a repository secret such as `APPLE_AGENT_KIT_ADAPTER_JSON`. The workflow can materialize it inside the ephemeral workspace:

```yaml
- name: Materialize private adapter
  env:
    APPLE_AGENT_KIT_ADAPTER_JSON: ${{ secrets.APPLE_AGENT_KIT_ADAPTER_JSON }}
  run: |
    set -euo pipefail
    test -n "$APPLE_AGENT_KIT_ADAPTER_JSON"
    printf '%s' "$APPLE_AGENT_KIT_ADAPTER_JSON" > .apple-agent-kit.json
```

Keep the public workflow generic where possible, but remember that `runs-on` labels in public repos are visible. Avoid labels that reveal sensitive host names, device names, or user names.

## Proof Checklist

Before calling runner onboarding complete, prove:

- The target repo sees an online runner with the expected labels.
- Existing runner services on the host are still present.
- The new runner has a separate directory and service when repo-scoped fallback was used.
- Adapter validation passes.
- Render receipt reports `"physical_device_actions": false`.
- The eligibility workflow completes from the PR branch.
- The default-branch `workflow_dispatch` completes after merge.
- Final notes explicitly say what was not run.

