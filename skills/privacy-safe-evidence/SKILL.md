---
name: privacy-safe-evidence
description: Collect useful automation evidence without leaking private app, device, account, or user data.
---

# Privacy-Safe Evidence

Use this skill before collecting screenshots, accessibility trees, logs, or receipts from Apple automation.

## Default Policy

Allowed:

- result bundle paths
- sanitized summaries
- hashes and counts
- sterile fixture screenshots
- command classes and exit codes

Not allowed:

- tokens or API keys
- raw private accessibility trees
- screenshots of personal apps or accounts
- message, email, reminder, contact, or phone content
- private URLs
- unredacted device identifiers

## Receipt

Each receipt should include:

- timestamp
- command class
- adapter name
- artifact paths
- pass/fail classification
- privacy assertions
- strongest attempted disproof

When in doubt, redact and keep the raw artifact local or omit it entirely.
