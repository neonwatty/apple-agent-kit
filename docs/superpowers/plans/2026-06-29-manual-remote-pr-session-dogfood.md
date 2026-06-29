# Manual Remote PR Session Dogfood Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan one task at a time. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the full Manual Remote PR Session loop on a real open `prcard/prcard-mac` PR using the MacBook Air receiver, including custom Codex instructions and sanitized public proof.

**Architecture:** A GitHub `workflow_dispatch` on `prcard/prcard-mac` publishes a validated job artifact for PR #2 at an exact SHA. The MacBook Air receiver pulls the job, checks out the SHA, runs the allowlisted `macos-tests` profile with `make test`, creates or resumes a private Codex session from the custom prompt, and posts only a sanitized receipt back to the PR.

**Tech Stack:** GitHub CLI, GitHub Actions `workflow_dispatch`, private Manual Remote PR Session receiver on the MacBook Air, Python receiver scripts, LaunchAgent, Codex CLI/App, sanitized receipt validation.

---

## Current Concrete Target

- Repo: `prcard/prcard-mac`
- PR: `2`
- PR URL: `https://github.com/prcard/prcard-mac/pull/2`
- Branch: `codex/release-artifact-backfill`
- Base: `main`
- SHA: `5c8629b9d0600399b98e9e2ad415bc07b8ac9716`
- GitHub checks observed green on 2026-06-29.
- Host profile alias: `macbook-air`
- Run profile: `macos-tests`
- Command expectation: `make test` through the private `macos-tests` run profile. The public workflow does not accept a raw `command` input.
- Launch app: `false` for the first app-realistic pass, because the approved first target is test-focused.
- Codex session: `true`
- Artifact mode: `receipt-only`

## File Map

- Public plan only: `docs/superpowers/plans/2026-06-29-manual-remote-pr-session-dogfood.md`
- Existing public workflow in app repo: `.github/workflows/manual-remote-pr-session.yml` in `prcard/prcard-mac`
- Existing private receiver root on the MacBook Air: `~/apple-agent-kit-manual-remote-pr-session/.apple-agent-kit.local.manual-remote/`
- Existing private receiver state on the MacBook Air: `~/.apple-agent-kit/manual-remote-pr-session/`
- Optional sanitized proof record after success: `docs/proof-records/prcard-manual-remote-pr-session-2026-06-29.md`

## Task 1: Preflight The MacBook Air Receiver

**Files:**
- Read-only: MacBook Air private receiver and LaunchAgent state.

- [ ] **Step 1: Confirm local GitHub auth can see the target PR**

Run:

```bash
gh pr view 2 \
  --repo prcard/prcard-mac \
  --json number,state,isDraft,headRefName,headRefOid,statusCheckRollup,url \
  --jq '{number,state,isDraft,headRefName,headRefOid,url,checks:[.statusCheckRollup[] | {name:.name,status:.status,conclusion:.conclusion}]}'
```

Expected:

```text
state is OPEN
isDraft is false
headRefOid is 5c8629b9d0600399b98e9e2ad415bc07b8ac9716
every completed check has conclusion SUCCESS
```

- [ ] **Step 2: Confirm the MacBook Air LaunchAgent is healthy**

Run:

```bash
ssh "$PRIVATE_HOST_ALIAS" 'zsh -lc "launchctl print gui/$(id -u)/com.apple-agent-kit.manual-remote-pr-session | sed -n '\''1,90p'\''"'
```

Expected:

```text
state = not running
last exit code = 0
run interval = 60 seconds
```

- [ ] **Step 3: Confirm receiver Python compiles on the MacBook Air**

Run:

```bash
ssh "$PRIVATE_HOST_ALIAS" 'zsh -lc "cd ~/apple-agent-kit-manual-remote-pr-session && python3 -m py_compile .apple-agent-kit.local.manual-remote/poller.py"'
```

Expected: command exits `0` with no output.

- [ ] **Step 4: Commit**

No commit for this task. It is read-only preflight.

## Task 2: Dispatch The Real Manual Remote PR Session

**Files:**
- No local file edits.
- GitHub workflow target: `prcard/prcard-mac/.github/workflows/manual-remote-pr-session.yml`

- [ ] **Step 1: Export exact dogfood values**

Run:

```bash
export DOGFOOD_REPO='prcard/prcard-mac'
export DOGFOOD_PR='2'
export DOGFOOD_SHA='5c8629b9d0600399b98e9e2ad415bc07b8ac9716'
export DOGFOOD_PROMPT='<sanitized operator instructions omitted from the public plan>'
```

Expected: variables are set in the current shell.

- [ ] **Step 2: Dispatch the workflow from the default branch**

Run:

```bash
gh workflow run manual-remote-pr-session.yml \
  --repo "$DOGFOOD_REPO" \
  --ref main \
  -f pr_number="$DOGFOOD_PR" \
  -f sha="$DOGFOOD_SHA" \
  -f host_profile_alias=macbook-air \
  -f run_profile=macos-tests \
  -f launch_app=false \
  -f create_codex_session=true \
  -f codex_instructions="$DOGFOOD_PROMPT" \
  -f artifact_mode=receipt-only
```

Expected: command exits `0`.

- [ ] **Step 3: Capture the new workflow run id**

Run:

```bash
export DOGFOOD_RUN_ID="$(
  gh run list \
    --repo "$DOGFOOD_REPO" \
    --workflow manual-remote-pr-session.yml \
    --event workflow_dispatch \
    --limit 1 \
    --json databaseId,headBranch,createdAt,status,conclusion \
    --jq '.[0].databaseId'
)"
printf 'DOGFOOD_RUN_ID=%s\n' "$DOGFOOD_RUN_ID"
export DOGFOOD_REQUEST_ID="mprs-${DOGFOOD_RUN_ID}-1"
printf 'DOGFOOD_REQUEST_ID=%s\n' "$DOGFOOD_REQUEST_ID"
```

Expected: `DOGFOOD_RUN_ID` is a numeric GitHub Actions run id and `DOGFOOD_REQUEST_ID` has the form `mprs-<run-id>-1`.

- [ ] **Step 4: Commit**

No commit for this task. The dispatch is an external action and should not modify the public kit repository.

## Task 3: Monitor GitHub And Pull The Job On The MacBook Air

**Files:**
- Read-only: GitHub run logs and MacBook Air receiver state.

- [ ] **Step 1: Watch the GitHub workflow finish**

Run:

```bash
gh run watch "$DOGFOOD_RUN_ID" --repo "$DOGFOOD_REPO" --exit-status
```

Expected: command exits `0`. If it exits nonzero, inspect with:

```bash
gh run view "$DOGFOOD_RUN_ID" --repo "$DOGFOOD_REPO" --log-failed
```

- [ ] **Step 2: Trigger an immediate receiver poll instead of waiting for the next LaunchAgent interval**

Run:

```bash
ssh "$PRIVATE_HOST_ALIAS" 'zsh -lc "cd ~/apple-agent-kit-manual-remote-pr-session && python3 .apple-agent-kit.local.manual-remote/poller.py"'
```

Expected:

```text
accepted manual remote PR session job
```

or:

```text
no new manual remote PR session jobs
```

The second output is acceptable only if the LaunchAgent already processed the request.

- [ ] **Step 3: Confirm the request id is processed locally**

Run:

```bash
ssh "$PRIVATE_HOST_ALIAS" "DOGFOOD_REQUEST_ID='$DOGFOOD_REQUEST_ID' python3 -c 'import json,pathlib,os; request_id=os.environ[\"DOGFOOD_REQUEST_ID\"]; p=pathlib.Path.home()/\".apple-agent-kit/manual-remote-pr-session/state.json\"; data=json.loads(p.read_text()); print(request_id in data.get(\"processedRequestIds\", []))'"
```

Expected:

```text
True
```

- [ ] **Step 4: Commit**

No commit for this task. It is operational proof collection.

## Task 4: Validate The Private Receipt And Public Comment

**Files:**
- Read-only: MacBook Air receipt JSON.
- Read-only: GitHub PR comments.

- [ ] **Step 1: Validate the receipt on the MacBook Air**

Run:

```bash
ssh "$PRIVATE_HOST_ALIAS" "zsh -lc 'cd ~/apple-agent-kit-manual-remote-pr-session && python3 scripts/aak.py validate-manual-remote-receipt ~/.apple-agent-kit/manual-remote-pr-session/receipts/${DOGFOOD_REQUEST_ID}.json --json'"
```

Expected:

```text
"ok": true
"requestId": "mprs-..."
"result": "succeeded"
```

- [ ] **Step 2: Confirm the receipt includes a created Codex session and no physical device use**

Run:

```bash
ssh "$PRIVATE_HOST_ALIAS" "DOGFOOD_REQUEST_ID='$DOGFOOD_REQUEST_ID' python3 -c 'import json,pathlib,os; request_id=os.environ[\"DOGFOOD_REQUEST_ID\"]; p=pathlib.Path.home()/f\".apple-agent-kit/manual-remote-pr-session/receipts/{request_id}.json\"; data=json.loads(p.read_text()); print(json.dumps({\"result\":data.get(\"result\"),\"codexSession\":data.get(\"codexSession\"),\"physicalDevice\":data.get(\"physicalDevice\")}, indent=2))'"
```

Expected:

```text
result is succeeded
codexSession.created is true
codexSession.sessionRef starts with codex-exec:
physicalDevice.gate is disabled
physicalDevice.requested is false
```

- [ ] **Step 3: Leak-scan the public PR comment**

Run:

```bash
python3 - <<'PY'
import json, os, re, subprocess, sys

repo = os.environ["DOGFOOD_REPO"]
pr = os.environ["DOGFOOD_PR"]
request_id = os.environ["DOGFOOD_REQUEST_ID"]
body = subprocess.check_output([
    "gh", "api", f"repos/{repo}/issues/{pr}/comments", "--paginate", "--jq",
    f'.[] | select(.body | contains("apple-agent-kit:manual-remote-pr-session:{request_id}")) | .body',
], text=True)

checks = {
    "raw_prompt_phrase": "<private prompt phrase omitted>" in body,
    "local_air_home": "<private home path omitted>" in body,
    "local_current_home": "<local workspace home path omitted>" in body,
    "raw_command_text": "<private command text omitted>" in body,
    "raw_stdout_marker": "<stdout marker omitted>" in body,
    "raw_stderr_marker": "<stderr marker omitted>" in body,
    "token_like": bool(re.search(r"<token-prefix-pattern-omitted>", body)),
    "udid_like": bool(re.search(r"\b[0-9A-Fa-f]{8}-[0-9A-Fa-f]{16}\b", body)),
}
print(json.dumps({"ok": not any(checks.values()), "checks": checks}, indent=2))
if any(checks.values()):
    sys.exit(1)
PY
```

Expected:

```text
"ok": true
```

- [ ] **Step 4: Commit**

No commit for this task unless Task 6 creates the sanitized proof record.

## Task 5: Resume The Codex Session From The Receipt

**Files:**
- Read-only: MacBook Air receipt JSON.
- Writes private operator-resume files under MacBook Air `~/.apple-agent-kit/manual-remote-pr-session/operator-resume/`.

- [ ] **Step 1: Run the operator open/resume command**

Run:

```bash
ssh "$PRIVATE_HOST_ALIAS" "zsh -lc 'cd ~/apple-agent-kit-manual-remote-pr-session && python3 .apple-agent-kit.local.manual-remote/poller.py --open-receipt ${DOGFOOD_REQUEST_ID} --resume-prompt '\''<sanitized resume instructions omitted from the public plan>'\'''"
```

Expected:

```text
requestId=mprs-...
result=succeeded
codexSession=codex-exec:...
checkoutExists=true
resumeExitCode=0
resumeLastMessagePath=...
```

- [ ] **Step 2: Confirm the private resume response**

Run:

```bash
ssh "$PRIVATE_HOST_ALIAS" "DOGFOOD_REQUEST_ID='$DOGFOOD_REQUEST_ID' python3 -c 'from pathlib import Path; import os; request_id=os.environ[\"DOGFOOD_REQUEST_ID\"]; d=Path.home()/f\".apple-agent-kit/manual-remote-pr-session/operator-resume/{request_id}\"; files=sorted(d.glob(\"*-last-message.md\"), key=lambda p:p.stat().st_mtime); print(files[-1].read_text().strip())'"
```

Expected:

```text
PRCARD_DOGFOOD_READY
```

- [ ] **Step 3: Commit**

No commit for this task. The resume artifacts are private machine state.

## Task 6: Write The Sanitized Proof Record

**Files:**
- Create: `docs/proof-records/prcard-manual-remote-pr-session-2026-06-29.md`

- [ ] **Step 1: Create the proof record**

Write this file with the observed run id and request id from Task 2:

```markdown
# prcard Manual Remote PR Session Proof - 2026-06-29

## Summary

A manual GitHub `workflow_dispatch` for `prcard/prcard-mac` PR #2 asked the MacBook Air receiver to check out the target SHA, run the approved `macos-tests` profile with `make test`, create a private Codex session from operator instructions, and publish only a sanitized receipt.

## Result

- Date: 2026-06-29
- Repo: `prcard/prcard-mac`
- PR: `2`
- SHA: `5c8629b9d0600399b98e9e2ad415bc07b8ac9716`
- GitHub workflow run: `28384369309`
- Request id: `mprs-28384369309-1`
- Host profile alias: `macbook-air`
- Run profile: `macos-tests`
- Command expectation: `make test` through the private `macos-tests` profile; the public workflow does not accept raw command input.
- Result: succeeded
- Codex session created: true
- Operator resume proof: private readiness response `PRCARD_DOGFOOD_READY`
- Physical device requested: false
- Physical device gate: disabled

## Sanitization

The public PR receipt/comment leak scan passed for raw prompt phrase, local home paths, raw command text, stdout/stderr markers, token-like strings, and device-id-like strings.

This proof record intentionally omits raw prompt text, raw logs, local paths, usernames, hostnames, tokens, serials, UDIDs, and private device identifiers.
```

Expected: proof record contains no local home paths, usernames, hostnames, raw prompts, raw logs, tokens, or device identifiers.

- [ ] **Step 2: Leak-scan the new proof record**

Run:

```bash
python3 - <<'PY'
from pathlib import Path
import re
import sys

p = Path("docs/proof-records/prcard-manual-remote-pr-session-2026-06-29.md")
body = p.read_text()
checks = {
    "local_air_home": "<private home path omitted>" in body,
    "local_current_home": "<local workspace home path omitted>" in body,
    "token_like": bool(re.search(r"<token-prefix-pattern-omitted>", body)),
    "udid_like": bool(re.search(r"\b[0-9A-Fa-f]{8}-[0-9A-Fa-f]{16}\b", body)),
    "raw_stdout_marker": "<stdout marker omitted>" in body,
    "raw_stderr_marker": "<stderr marker omitted>" in body,
}
print(checks)
if any(checks.values()):
    sys.exit(1)
PY
```

Expected: all values are `False`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/proof-records/prcard-manual-remote-pr-session-2026-06-29.md docs/superpowers/plans/2026-06-29-manual-remote-pr-session-dogfood.md
git commit -m "docs: record prcard manual remote session dogfood plan"
```

Expected: commit succeeds.

## Task 7: Decide Whether To Add The `mprs` Operator Wrapper

**Files:**
- Possible private create: private receiver `mprs` helper
- Possible private modify: private receiver README

- [ ] **Step 1: Decide from dogfood friction**

Use this rule:

```text
If the Python command was easy enough during Task 5, defer the wrapper.
If the Python command felt too long or error-prone, add a private wrapper that supports:
  mprs open mprs-...
  mprs prompt mprs-... "safe prompt"
```

Expected: one decision recorded in the session notes.

- [ ] **Step 2: Commit**

No public commit for this task. The wrapper would live in the private receiver and should be planned separately if selected.

## Self-Review

- Spec coverage: The plan covers exact PR/SHA dispatch, MacBook Air pull/execute behavior, custom Codex prompt, receipt validation, public leak scan, physical-device gate check, operator resume, and sanitized proof.
- Placeholder scan: Commands use concrete values for repo, PR, SHA, host profile, run profile, and prompts. Dynamic values are derived by shell variables from the real workflow run id.
- Type consistency: The plan consistently uses `DOGFOOD_RUN_ID`, `DOGFOOD_REQUEST_ID`, `macbook-air`, `macos-tests`, the private profile expectation of `make test`, and `manual-remote-pr-session.yml`.
