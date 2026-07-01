# Privacy-Safe Evidence

Automation evidence should prove behavior without exposing private data.

## Allowed By Default

- command names and exit codes
- Xcode version and platform summary
- result bundle paths
- sanitized test summaries
- coverage summaries
- artifact file paths
- hashes or counts of sensitive objects
- screenshots from sterile fixtures when the adapter allows them
- bounded OSLog or structured log excerpts from sterile fixtures

## Not Allowed By Default

- API keys, tokens, signing passwords, or session cookies
- phone numbers, contacts, private URLs, message text, reminder titles, email content
- raw accessibility trees from personal apps
- screenshots of personal apps or accounts
- unredacted device rows when they expose private identifiers

## Receipt Requirement

Before declaring a run complete, the agent should try to disprove the result and record what it checked. Passing happy-path tests alone is not enough.

Fixture UI smoke receipts should include the fixture target, log time window, expected events, observed event count, artifact allowlist, withheld artifacts, privacy assertions, and the strongest attempted disproof. Use sanitized event names or counts in public proof records; keep raw logs local or private when they expose paths, usernames, host details, or product data.

For local Xcode readiness, prefer:

```bash
python3 scripts/aak.py check-xcode --json
```

The JSON summary reports runtime counts rather than raw simulator rows.
