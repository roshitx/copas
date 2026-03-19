# TESTS — SHARED FIXTURES

## PURPOSE

Shared test scenario definitions used across frontend (Playwright) and backend (pytest). Single source of truth for Twitter test cases.

## STRUCTURE

```
tests/
├── platform-template.json    # Template schema for adding new platform fixtures
├── scenario-schema.json      # JSON schema for validating scenario files
└── twitter-scenarios.json    # Canonical Twitter test scenarios
```

## FIXTURE SYNC RULE

Twitter fixtures exist in **three** locations — keep them identical:
1. `tests/twitter-scenarios.json` (canonical/shared)
2. `backend/tests/fixtures/twitter/` (pytest consumption)
3. `frontend/tests/fixtures/twitter/` (Playwright consumption)

When modifying Twitter test data, update **all three**.

## ADDING A NEW PLATFORM

1. Copy `platform-template.json` → `{platform}-scenarios.json`
2. Follow `scenario-schema.json` for structure
3. Create fixture copies in both `backend/tests/fixtures/{platform}/` and `frontend/tests/fixtures/{platform}/`
4. See `docs/testing-platform-expansion.md` for full guide
