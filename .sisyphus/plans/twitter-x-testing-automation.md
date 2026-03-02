# Twitter X Automated Testing Plan

## TL;DR
> **Summary**: Build a deterministic, agent-executable test system for X/Twitter download correctness across backend and frontend, then isolate live-link smoke tests into a non-blocking workflow.
> **Deliverables**:
> - Backend pytest stack (unit/integration/contract/live markers)
> - Frontend Playwright stack (deterministic E2E + live smoke)
> - Shared scenario fixtures for 5 canonical Twitter cases
> - CI split: deterministic PR gate + scheduled/manual live smoke
> **Effort**: Large
> **Parallel**: YES - 4 waves
> **Critical Path**: T1/T2/T3 -> T4/T5/T6 -> T7/T8/T9/T10 -> T11

## Context
### Original Request
Create a complete testing plan to remove manual testing burden for Twitter/X download scenarios (single image/video, multi-image, multi-video, hybrid), with verification of download output correctness, multiple download handling, and filename correctness.

### Interview Summary
- Current focus is only X/Twitter; broader platform expansion comes later.
- Provided canonical links for live testing baseline:
  - `https://x.com/rwhendry/status/2027767749695705372?s=20`
  - `https://x.com/sosmedkeras/status/2027955413753417803?s=20`
  - `https://x.com/mikuroQ/status/2027735620534358393?s=20`
  - `https://x.com/IndonesiaGaruda/status/2027914018976108959?s=20`
  - `https://x.com/Villgecrazylady/status/2027532953966825726?s=20`

### Metis Review (gaps addressed)
- Added strict deterministic/no-network PR lane guardrails.
- Added explicit contract checks for `/api/extract` and `/api/download` (headers/status/error payloads).
- Added token TTL/expiry and repeated-download assertions.
- Added explicit ZIP content assertions (entry names/count/types).
- Added extension mechanism without redesign (scenario-matrix architecture).

## Work Objectives
### Core Objective
Ship a reliable, low-flake automated test system for Twitter/X downloads so manual per-case verification is no longer needed.

### Deliverables
- Backend testing infrastructure and suites for unit, integration, and API contracts.
- Frontend Playwright E2E deterministic suite for all five Twitter content shapes.
- Live smoke suite using provided real links (scheduled/manual, non-blocking).
- CI workflows with deterministic PR gate and isolated live lane.
- Scenario matrix + fixtures reusable for future platform expansion.

### Definition of Done (verifiable conditions with commands)
- `cd backend && pytest -m "unit or integration or contract" --maxfail=1 --disable-warnings` exits `0`.
- `cd frontend && npx playwright test tests/e2e/twitter-deterministic.spec.ts` exits `0`.
- `cd frontend && npm run build` exits `0`.
- CI PR workflow runs backend deterministic + frontend deterministic + build and blocks on failure.
- CI live smoke workflow runs separately and records artifacts for each canonical URL.

### Must Have
- Coverage for: single image, single video, multi-image, multi-video, hybrid.
- Assertions for filename correctness from backend `Content-Disposition` and frontend ZIP entries.
- Assertions for multi-download behavior and token-expiry behavior.
- No human/manual checks in acceptance criteria.

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- No non-Twitter platform implementation in this phase.
- No PR-gated outbound calls to live X/fxtwitter/yt-dlp endpoints.
- No flaky selector strategy (avoid brittle CSS chains).
- No acceptance criteria that require opening browser manually.

## Verification Strategy
> ZERO HUMAN INTERVENTION — all verification is agent-executed.
- Test decision: tests-after with deterministic-first strategy.
- Backend framework: `pytest`, `pytest-asyncio`, `respx`, `pytest-cov`, `pytest-socket`.
- Frontend framework: Playwright (Chromium required lane; optional Firefox/WebKit as non-gate).
- QA policy: every task includes happy path + failure/edge scenario.
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`.

## Execution Strategy
### Parallel Execution Waves
Wave 1: foundation and contracts setup (`T1`,`T2`,`T3`)
Wave 2: backend suites + fixture matrix (`T4`,`T5`,`T6`)
Wave 3: frontend deterministic/live suites + CI (`T7`,`T8`,`T9`,`T10`)
Wave 4: hardening + extension template (`T11`)

### Dependency Matrix (full, all tasks)
- `T1` blocks `T4`,`T5`,`T6`,`T11`
- `T2` blocks `T7`,`T8`,`T9`,`T11`
- `T3` blocks `T4`,`T7`,`T11`
- `T4` blocks `T5`,`T9`,`T10`
- `T5` blocks `T10`
- `T6` blocks `T10`
- `T7` blocks `T8`,`T9`,`T10`
- `T8` blocks `T10`
- `T9` blocks `T10`
- `T10` blocks `T11`

### Agent Dispatch Summary (wave → task count → categories)
- Wave 1 → 3 tasks → `testing`, `implementation`
- Wave 2 → 3 tasks → `testing`, `backend-patterns`
- Wave 3 → 4 tasks → `testing`, `visual-engineering`, `executor`
- Wave 4 → 1 task → `review`, `doc-writer`

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task has Agent Profile + Parallelization + QA Scenarios.

- [x] 1. Bootstrap backend testing toolchain and marker policy

  **What to do**: Add backend dev-test dependencies and runner config (`requirements-dev.txt`, `pytest.ini`), define markers: `unit`, `integration`, `contract`, `live`, `smoke`, and set strict marker usage.
  **Must NOT do**: Do not add platform-specific logic in this task; do not add live-network calls.

  **Recommended Agent Profile**:
  - Category: `testing` — Reason: test infra bootstrap.
  - Skills: `[]` — no special skill required.
  - Omitted: `frontend-ui-ux` — not relevant.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: `T4,T5,T6,T11` | Blocked By: none

  **References**:
  - `backend/requirements.txt` — existing backend dependency baseline.
  - `backend/app/routers/extract.py` — error semantics to map in tests.

  **Acceptance Criteria**:
  - [x] `cd backend && pip install -r requirements.txt -r requirements-dev.txt` exits `0`.
  - [x] `cd backend && pytest --markers` lists all required markers.

  **QA Scenarios** (MANDATORY — task incomplete without these):
  ```text
  Scenario: Marker registration works
    Tool: Bash
    Steps: Run `cd backend && pytest --markers`
    Expected: Output contains unit/integration/contract/live/smoke markers
    Evidence: .sisyphus/evidence/task-1-backend-markers.txt

  Scenario: Unknown marker rejected
    Tool: Bash
    Steps: Run `cd backend && pytest -m doesnotexist -q`
    Expected: Non-zero exit with marker error/warning, proving strict marker handling
    Evidence: .sisyphus/evidence/task-1-backend-marker-error.txt
  ```

  **Commit**: YES | Message: `test(backend): bootstrap pytest infrastructure and marker policy` | Files: `backend/requirements-dev.txt`, `backend/pytest.ini`

- [x] 2. Bootstrap frontend Playwright infrastructure

  **What to do**: Add Playwright dependencies/config/scripts, deterministic downloads directory, and base config for local + CI execution.
  **Must NOT do**: Do not implement scenario assertions yet.

  **Recommended Agent Profile**:
  - Category: `testing` — Reason: E2E runner setup.
  - Skills: `[]` — baseline tooling setup.
  - Omitted: `backend-patterns` — not needed.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: `T7,T8,T9,T11` | Blocked By: none

  **References**:
  - `frontend/package.json` — scripts/deps insertion point.
  - `frontend/lib/api.ts` — backend endpoint expectations.

  **Acceptance Criteria**:
  - [x] `cd frontend && npx playwright install --with-deps` exits `0`.
  - [x] `cd frontend && npx playwright test --list` exits `0`.

  **QA Scenarios**:
  ```text
  Scenario: Playwright runner boots
    Tool: Bash
    Steps: Run `cd frontend && npx playwright test --list`
    Expected: Test runner lists specs without runtime config errors
    Evidence: .sisyphus/evidence/task-2-playwright-list.txt

  Scenario: Missing browser binary handling
    Tool: Bash
    Steps: Run list command before install in clean env
    Expected: Clear install prompt/error; then install command resolves it
    Evidence: .sisyphus/evidence/task-2-playwright-install.txt
  ```

  **Commit**: YES | Message: `test(frontend): bootstrap playwright infrastructure` | Files: `frontend/package.json`, `frontend/playwright.config.ts`

- [x] 3. Create shared Twitter scenario matrix and canonical fixtures

  **What to do**: Add a single source-of-truth scenario matrix mapping 5 Twitter cases to expected outputs (counts, media types, filename patterns, zip expectations, status behavior).
  **Must NOT do**: Do not couple expectations to unstable exact CDN URLs.

  **Recommended Agent Profile**:
  - Category: `implementation` — Reason: shared structured test artifacts.
  - Skills: `[]`.
  - Omitted: `visual-engineering` — not relevant.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: `T4,T7,T11` | Blocked By: none

  **References**:
  - `backend/app/schemas/extract.py` — response contract fields.
  - `frontend/types/index.ts` — frontend contract consumer.
  - `backend/app/services/extractor.py` — label/filename semantics.

  **Acceptance Criteria**:
  - [x] Fixture files exist for all five canonical links and validate against expected schema.
  - [x] Matrix can be imported by both backend and frontend tests.

  **QA Scenarios**:
  ```text
  Scenario: Matrix completeness
    Tool: Bash
    Steps: Run a fixture validation script/test over all scenario entries
    Expected: Exactly 5 scenarios present and all required keys valid
    Evidence: .sisyphus/evidence/task-3-matrix-validation.txt

  Scenario: Schema mismatch catches fixture drift
    Tool: Bash
    Steps: Intentionally run validator against malformed fixture in test
    Expected: Validation fails with explicit missing/invalid field message
    Evidence: .sisyphus/evidence/task-3-schema-failure.txt
  ```

  **Commit**: YES | Message: `test(shared): add twitter scenario matrix and canonical fixtures` | Files: `backend/tests/fixtures/twitter/*`, `frontend/tests/fixtures/twitter/*`, `tests/shared/twitter-scenarios.*`

- [x] 4. Implement backend unit tests for token, filename, and extractor helpers

  **What to do**: Add unit tests for token lifecycle (`TTL=300`), filename construction, tweet-id extraction, URL normalization, and format-label generation behavior.
  **Must NOT do**: No HTTP network calls.

  **Recommended Agent Profile**:
  - Category: `testing` — Reason: deterministic unit coverage.
  - Skills: `[]`.
  - Omitted: `frontend-ui-ux` — not relevant.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: `T5,T9,T10` | Blocked By: `T1,T3`

  **References**:
  - `backend/app/services/token_store.py` — token semantics.
  - `backend/app/services/extractor.py` — helper behavior under test.
  - `backend/app/utils/platform.py` — URL/platform mapping.

  **Acceptance Criteria**:
  - [x] `cd backend && pytest -m unit -q` exits `0`.
  - [x] Unit suite includes explicit expiry test for token TTL and filename pattern checks.

  **QA Scenarios**:
  ```text
  Scenario: Token expires deterministically
    Tool: Bash
    Steps: Run unit test case with mocked/frozen time crossing 300s TTL
    Expected: token lookup returns None after expiry boundary
    Evidence: .sisyphus/evidence/task-4-token-expiry.txt

  Scenario: Filename format regression
    Tool: Bash
    Steps: Run unit tests for single and indexed filenames
    Expected: filenames match {platform}_{author}_copas_io(_{index}).ext
    Evidence: .sisyphus/evidence/task-4-filename-pattern.txt
  ```

  **Commit**: YES | Message: `test(backend): add unit tests for token and filename helpers` | Files: `backend/tests/unit/services/test_token_store.py`, `backend/tests/unit/services/test_extractor_helpers.py`

- [x] 5. Implement backend integration tests for `/api/extract` Twitter scenarios

  **What to do**: Test router behavior and extraction responses for all 5 scenario shapes using deterministic mocks/stubs for external dependencies.
  **Must NOT do**: No live X calls in integration tests.

  **Recommended Agent Profile**:
  - Category: `testing` — Reason: API integration reliability.
  - Skills: `[]`.
  - Omitted: `executor` — not needed.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: `T10` | Blocked By: `T1,T4`

  **References**:
  - `backend/app/routers/extract.py` — status mapping/response model.
  - `backend/app/schemas/extract.py` — expected response fields.

  **Acceptance Criteria**:
  - [x] `cd backend && pytest -m integration -q tests/integration/api/test_extract_twitter.py` exits `0`.
  - [x] Assertions include: media counts, type coverage, author/title/thumbnails presence, tokenized download URLs.

  **QA Scenarios**:
  ```text
  Scenario: All five twitter cases pass
    Tool: Bash
    Steps: Run integration extract suite
    Expected: single/multi/hybrid cases produce expected format groups and metadata
    Evidence: .sisyphus/evidence/task-5-extract-cases.txt

  Scenario: Extract error mapping
    Tool: Bash
    Steps: Run forced error tests for ValueError/PermissionError/RuntimeError paths
    Expected: returns 400/403/422 with ErrorResponse payload
    Evidence: .sisyphus/evidence/task-5-extract-errors.txt
  ```

  **Commit**: YES | Message: `test(backend): add twitter extract integration suite` | Files: `backend/tests/integration/api/test_extract_twitter.py`

- [x] 6. Implement backend integration+contract tests for `/api/download`

  **What to do**: Validate download endpoint token handling, streaming headers, repeated download behavior, and expiry-to-410 behavior.
  **Must NOT do**: Avoid brittle binary-byte equality for compressed artifacts; assert headers and stable metadata.

  **Recommended Agent Profile**:
  - Category: `testing` — Reason: download contract correctness.
  - Skills: `[]`.
  - Omitted: `visual-engineering` — irrelevant.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: `T10` | Blocked By: `T1`

  **References**:
  - `backend/app/routers/download.py` — token routing/status behavior.
  - `backend/app/services/streamer.py` — `Content-Disposition`/`Content-Type` behavior.
  - `backend/app/services/token_store.py` — expiry semantics.

  **Acceptance Criteria**:
  - [x] `cd backend && pytest -m "integration or contract" -q tests/integration/api/test_download_twitter.py tests/contract/test_download_contract.py` exits `0`.
  - [x] Assertions include: `410` on expired/invalid token, attachment header with expected filename, correct content type.

  **QA Scenarios**:
  ```text
  Scenario: Valid token download
    Tool: Bash
    Steps: Run download integration suite for valid tokens
    Expected: 200 response, attachment Content-Disposition includes expected filename
    Evidence: .sisyphus/evidence/task-6-download-valid.txt

  Scenario: Expired token handling
    Tool: Bash
    Steps: Run expiry-path tests with mocked time > TTL
    Expected: 410 with stable error detail
    Evidence: .sisyphus/evidence/task-6-download-expired.txt
  ```

  **Commit**: YES | Message: `test(backend): add download integration and contract tests` | Files: `backend/tests/integration/api/test_download_twitter.py`, `backend/tests/contract/test_download_contract.py`

- [x] 7. Add deterministic frontend E2E harness for extract/download UI flow

  **What to do**: Build Playwright deterministic harness with network interception/stubbing for `/api/extract` and `/api/download` plus stable selectors.
  **Must NOT do**: No dependency on live external Twitter in this suite.

  **Recommended Agent Profile**:
  - Category: `testing` — Reason: deterministic UI automation.
  - Skills: `[]`.
  - Omitted: `backend-patterns`.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: `T8,T9,T10` | Blocked By: `T2,T3`

  **References**:
  - `frontend/hooks/use-download.ts` — behavior under test.
  - `frontend/components/result-card.tsx` — UI paths (single/multi/hybrid + Download Semua).
  - `frontend/lib/api.ts` — request boundary to intercept.

  **Acceptance Criteria**:
  - [x] `cd frontend && npx playwright test tests/e2e/twitter-deterministic.spec.ts --project=chromium` exits `0`.
  - [x] Deterministic suite runs with zero outbound network dependencies.

  **QA Scenarios**:
  ```text
  Scenario: Deterministic extract+download wiring
    Tool: Playwright
    Steps: Intercept extract and download routes with fixture responses
    Expected: UI renders expected sections and download event is emitted
    Evidence: .sisyphus/evidence/task-7-deterministic-harness.zip

  Scenario: Backend failure surfaced to user
    Tool: Playwright
    Steps: Stub extract route to return 422 ErrorResponse
    Expected: error message state is shown and no download action is available
    Evidence: .sisyphus/evidence/task-7-error-ui.png
  ```

  **Commit**: YES | Message: `test(frontend): add deterministic playwright harness for twitter downloads` | Files: `frontend/tests/e2e/twitter-deterministic.spec.ts`

- [x] 8. Implement deterministic Playwright assertions for all 5 Twitter shapes

  **What to do**: Add scenario-driven E2E tests for single-image, single-video, multi-image, multi-video, and hybrid, including filename and ZIP-entry assertions.
  **Must NOT do**: Do not validate unstable pixel details; focus on binary pass/fail behavior.

  **Recommended Agent Profile**:
  - Category: `testing` — Reason: scenario assertions.
  - Skills: `[]`.
  - Omitted: `artistry` — unnecessary.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: `T10` | Blocked By: `T2,T7`

  **References**:
  - `frontend/hooks/use-download.ts` — filename + zip logic.
  - `frontend/components/format-button.tsx` — per-format triggers.
  - `frontend/components/result-card.tsx` — Download Semua and grouped views.

  **Acceptance Criteria**:
  - [x] Test suite includes all five content-shape cases with strict expected counts and filename conventions.
  - [x] ZIP scenario validates entry names/order/count for multi-image path.

  **QA Scenarios**:
  ```text
  Scenario: Multi-image Download Semua ZIP
    Tool: Playwright
    Steps: Trigger Download Semua on multi-image fixture
    Expected: one .zip download; archive entries named twitter_{author}_copas_io_{n}.jpg
    Evidence: .sisyphus/evidence/task-8-multi-image-zip.txt

  Scenario: Hybrid media rendering and download
    Tool: Playwright
    Steps: Use hybrid fixture and trigger one video + one image download action
    Expected: both media sections visible and both downloads emitted with expected extensions
    Evidence: .sisyphus/evidence/task-8-hybrid-downloads.txt
  ```

  **Commit**: YES | Message: `test(frontend): add twitter scenario e2e assertions` | Files: `frontend/tests/e2e/twitter-deterministic.spec.ts`, `frontend/tests/e2e/helpers/*`

- [x] 9. Add live Twitter smoke suite (non-blocking lane)

  **What to do**: Add live smoke Playwright/backend checks using the 5 canonical URLs with retries and artifact capture.
  **Must NOT do**: Must not block PR gate.

  **Recommended Agent Profile**:
  - Category: `testing` — Reason: production drift detection.
  - Skills: `[]`.
  - Omitted: `quick` — insufficient for flaky-network hardening.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: `T10` | Blocked By: `T2,T4,T7`

  **References**:
  - Provided canonical links in this plan context.
  - `frontend/playwright.config.ts` — `@live` project/timeout/retry profile.

  **Acceptance Criteria**:
  - [x] `cd frontend && npx playwright test tests/e2e/twitter-live-smoke.spec.ts --grep @live` executes and stores traces/screenshots.
  - [x] Failure output clearly distinguishes extraction fail vs download fail vs filename mismatch.

  **QA Scenarios**:
  ```text
  Scenario: Live single-image smoke
    Tool: Playwright
    Steps: Run @live case for rwhendry link
    Expected: extract succeeds and at least one image download event is captured
    Evidence: .sisyphus/evidence/task-9-live-single-image.zip

  Scenario: Live outage handling
    Tool: Playwright
    Steps: Simulate/encounter upstream fail path in live run
    Expected: suite records actionable failure artifact without corrupting deterministic lane
    Evidence: .sisyphus/evidence/task-9-live-failure.txt
  ```

  **Commit**: YES | Message: `test(live): add twitter live smoke suite` | Files: `frontend/tests/e2e/twitter-live-smoke.spec.ts`

- [x] 10. Implement CI workflows: deterministic PR gate + isolated live smoke

  **What to do**: Add CI workflows separating required deterministic checks from scheduled/manual live checks, with artifact upload and retry policy.
  **Must NOT do**: Do not run live suite on every PR.

  **Recommended Agent Profile**:
  - Category: `executor` — Reason: CI orchestration across lanes.
  - Skills: `[]`.
  - Omitted: `frontend-ui-ux`.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: `T11` | Blocked By: `T4,T5,T6,T7,T8,T9`

  **References**:
  - `.github/workflows/` (to be created).
  - `frontend/package.json` scripts and backend pytest commands from prior tasks.

  **Acceptance Criteria**:
  - [x] PR workflow blocks merge when deterministic tests/build fail.
  - [x] Live workflow runs on schedule/manual dispatch and is non-blocking for PRs.

  **QA Scenarios**:
  ```text
  Scenario: Deterministic gate failure blocks PR
    Tool: Bash
    Steps: Run workflow locally/act with intentionally failing deterministic test
    Expected: workflow exits non-zero before merge-ready status
    Evidence: .sisyphus/evidence/task-10-pr-gate-fail.txt

  Scenario: Live workflow isolation
    Tool: Bash
    Steps: Trigger live workflow manually
    Expected: live job runs independently and publishes artifacts, no PR-block status coupling
    Evidence: .sisyphus/evidence/task-10-live-workflow.txt
  ```

  **Commit**: YES | Message: `ci(test): add deterministic gate and isolated live smoke workflows` | Files: `.github/workflows/tests.yml`, `.github/workflows/twitter-live-smoke.yml`

- [x] 11. Add extension template for future platforms without redesign

  **What to do**: Add documented scenario-manifest contract and template tests showing how to onboard a new platform by adding rows/fixtures only.
  **Must NOT do**: Do not implement non-Twitter production tests in this task.

  **Recommended Agent Profile**:
  - Category: `doc-writer` — Reason: reusable onboarding blueprint.
  - Skills: `[]`.
  - Omitted: `implementation` — only template/wiring docs.

  **Parallelization**: Can Parallel: NO | Wave 4 | Blocks: none | Blocked By: `T1,T2,T3,T10`

  **References**:
  - Scenario matrix artifacts from `T3`.
  - Backend/Frontend deterministic suites from `T4-T8`.

  **Acceptance Criteria**:
  - [x] Template docs include required fields, expected assertions, and CI tag conventions.
  - [x] A sample placeholder platform row passes schema validation (without enabling non-Twitter execution).

  **QA Scenarios**:
  ```text
  Scenario: Extension template validation
    Tool: Bash
    Steps: Validate sample row against scenario schema
    Expected: schema validation passes for template row structure
    Evidence: .sisyphus/evidence/task-11-template-schema.txt

  Scenario: Scope guardrail enforcement
    Tool: Bash
    Steps: Run deterministic suites with twitter-only filter
    Expected: no non-twitter tests are executed in this phase
    Evidence: .sisyphus/evidence/task-11-scope-guard.txt
  ```

  **Commit**: YES | Message: `docs(test): add cross-platform scenario expansion template` | Files: `docs/testing-platform-expansion.md`, `tests/shared/scenario-schema.*`

## Final Verification Wave (4 parallel agents, ALL must APPROVE)
- [x] F1. Plan Compliance Audit — oracle
- [x] F2. Code Quality Review — unspecified-high
- [x] F3. Real Manual QA Simulation — unspecified-high (+ playwright)
- [x] F4. Scope Fidelity Check — deep

## Commit Strategy
- Commit group A: backend test infra + fixtures + backend suites.
- Commit group B: frontend Playwright infra + deterministic suite.
- Commit group C: CI workflows + live smoke + docs.
- Conventional messages:
  - `test(backend): add twitter deterministic unit integration contract suites`
  - `test(frontend): add playwright twitter deterministic and live smoke suites`
  - `ci(test): add deterministic gate and isolated live smoke workflow`

## Success Criteria
- Deterministic tests fully replace manual Twitter test loop for covered cases.
- Filename correctness validated for single and multi/zip paths.
- Failures are diagnosable via stored artifacts and clear assertion messages.
- Platform expansion can be done by adding scenario rows and fixtures, not redesigning architecture.
