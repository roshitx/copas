# Instagram TDD Automation and Feature Completion

## TL;DR
> **Summary**: Deliver full Instagram support (reels thumbnail, consistent filename, image-only, carousel, hybrid) using TDD-first execution across backend and frontend with deterministic automation.
> **Deliverables**:
> - Backend extractor + contract updates for Instagram media variants
> - Instagram deterministic backend/frontend test suites
> - CI integration and regression safety for Twitter
> - Expanded shared scenario schema and fixtures for Instagram
> **Effort**: Large
> **Parallel**: YES - 4 waves
> **Critical Path**: 1 -> 2 -> 4 -> 6 -> 8 -> 10 -> 11

## Context
### Original Request
User wants a comprehensive Instagram plan, TDD-first, because manual validation is exhausting. Current state: Instagram reels single video works, but filename prefix is not consistently aligned to Twitter style and reels thumbnail is missing. Instagram image-only, multi-image carousel, and hybrid media currently fail with HTTP 422.

### Interview Summary
- Scope locked to Instagram platform expansion only.
- Keep deterministic-first testing policy from Twitter baseline (no live network in PR-gated tests).
- Preserve existing Twitter behavior as non-regression guardrail.
- Target parity behavior for naming pattern: `platform_author_copas_io(.ext)` with index suffix when needed.

### Metis Review (gaps addressed)
- Confirmed 422 root cause is extractor runtime failure when `formats` is empty, not request model validation.
- Identified filename-author timing risk in backend format creation (author resolved after tokenized filename generation in some paths).
- Added explicit schema-generalization task for `tests/shared/scenario-schema.json` to unblock Instagram matrix validation.
- Added mandatory Twitter regression checkpoints in acceptance criteria across backend and frontend lanes.

## Work Objectives
### Core Objective
Make Instagram extraction/download feature-complete for reels + image-only + carousel + hybrid, with deterministic automated coverage that removes manual validation burden.

### Deliverables
- Instagram scenario matrix and fixtures (shared/backend/frontend)
- Backend extraction support for Instagram image/carousel/hybrid and robust thumbnail fallback
- Filename normalization parity for Instagram via backend token filename and frontend helper checks
- Backend unit/integration/contract tests for Instagram behavior and error mapping
- Frontend deterministic Playwright suite for Instagram flows
- CI updates to include Instagram deterministic lane while preserving Twitter gates

### Definition of Done (verifiable conditions with commands)
- `cd backend && PYTHONPATH=. pytest -m "unit or integration or contract" --ignore=tests/live -q -p no:mcp_eval`
- `cd backend && PYTHONPATH=. pytest tests/integration/api/test_extract_instagram.py -q -p no:mcp_eval`
- `cd frontend && npx playwright test tests/e2e/instagram-deterministic.spec.ts --project=chromium`
- `cd frontend && npx playwright test tests/e2e/twitter-deterministic.spec.ts --project=chromium`
- `cd frontend && npm run build`

### Must Have
- TDD sequence enforced per layer (RED -> GREEN -> REFACTOR).
- Deterministic assertions for filename, thumbnail, multiple download correctness.
- HTTP 422 eliminated for supported Instagram post types (reels/image/carousel/hybrid).
- Reels thumbnail visible in result card when extractor provides media thumbnail data.

### Must NOT Have (guardrails, AI slop patterns, scope boundaries)
- No live Instagram/X traffic in deterministic suites.
- No regressions to Twitter extraction/download behavior.
- No scope expansion to TikTok/YouTube/other platforms.
- No manual-only acceptance checks.

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed.
- Test decision: TDD with existing `pytest` + `@playwright/test` stack.
- QA policy: Every task includes happy-path and failure/edge scenario automation.
- Evidence: `.sisyphus/evidence/task-{N}-{slug}.{ext}`

## Execution Strategy
### Parallel Execution Waves
> Target: 5-8 tasks per wave. Shared dependencies extracted early.

Wave 1: Scenario contract + fixture foundations (Tasks 1-3)
Wave 2: Backend TDD + implementation for extraction gaps (Tasks 4-7)
Wave 3: Frontend deterministic Instagram suite + naming/thumbnail parity checks (Tasks 8-9)
Wave 4: CI integration, docs alignment, and full regression sweeps (Tasks 10-11)

### Dependency Matrix (full, all tasks)
- 1 -> 2, 3, 4, 8
- 2 -> 4, 8
- 3 -> 4, 8
- 4 -> 5, 6, 7
- 5 -> 6, 8
- 6 -> 8, 10
- 7 -> 10
- 8 -> 9, 10
- 9 -> 10
- 10 -> 11
- 11 -> Final Verification Wave

### Agent Dispatch Summary (wave -> task count -> categories)
- Wave 1 -> 3 tasks -> `implementation`, `testing`
- Wave 2 -> 4 tasks -> `implementation`, `testing`, `refactorer`
- Wave 3 -> 2 tasks -> `testing`, `visual-engineering`
- Wave 4 -> 2 tasks -> `implementation`, `testing`, `doc-writer`

## TODOs
> Implementation + Test = ONE task. Never separate.
> Every task includes Agent Profile + Parallelization + QA Scenarios.

- [ ] 1. Generalize shared scenario schema for multi-platform validation

  **What to do**: Update `tests/shared/scenario-schema.json` so scenario validation supports Instagram in addition to Twitter: platform enum, scenario ID pattern, URL pattern (include `instagram.com/p/` and `instagram.com/reel/`), filename regex, zip filename regex, and platform-specific constraints that stay strict.
  **Must NOT do**: Do not loosen schema into permissive `.*`; keep deterministic strict patterns for both Twitter and Instagram.

  **Recommended Agent Profile**:
  - Category: `testing` - Reason: This is contract schema work that directly controls fixture validity.
  - Skills: `[]` - No special skill required.
  - Omitted: `frontend-patterns` - No UI logic here.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: 2, 3, 4, 8 | Blocked By: none

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `tests/shared/scenario-schema.json` - Current Twitter-only constraints to generalize.
  - Pattern: `tests/shared/twitter-scenarios.json` - Existing strict scenario structure.
  - Pattern: `docs/testing-platform-expansion.md` - Expansion strategy and validation expectations.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io && python -m json.tool tests/shared/scenario-schema.json >/dev/null`
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io && python - <<'PY'
import json, jsonschema
schema=json.load(open('tests/shared/scenario-schema.json'))
twitter=json.load(open('tests/shared/twitter-scenarios.json'))
jsonschema.validate(twitter, schema)
print('ok')
PY`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Existing Twitter matrix remains valid
    Tool: Bash
    Steps: Run jsonschema validation for tests/shared/twitter-scenarios.json against updated schema
    Expected: Validation passes with no schema errors
    Evidence: .sisyphus/evidence/task-1-scenario-schema-twitter.txt

  Scenario: Invalid Instagram URL is rejected
    Tool: Bash
    Steps: Validate a synthetic payload with platform=instagram but URL outside instagram domains
    Expected: Validation fails with URL pattern error
    Evidence: .sisyphus/evidence/task-1-scenario-schema-invalid-url.txt
  ```

  **Commit**: YES | Message: `test(schema): generalize shared scenario contract for instagram` | Files: `tests/shared/scenario-schema.json`

- [ ] 2. Add Instagram shared scenario matrix and canonical deterministic expectations

  **What to do**: Create `tests/shared/instagram-scenarios.json` with at least 5 scenarios: single-video reel, single-image post, multi-image carousel (>=3 slides), hybrid carousel (video+image), and mixed-order carousel. Include expected format counts/types, filename patterns, zip behavior, and thumbnail expectations.
  **Must NOT do**: Do not include live-only assumptions or private/auth-required URLs in deterministic matrix.

  **Recommended Agent Profile**:
  - Category: `testing` - Reason: Scenario matrix defines test contract across layers.
  - Skills: `[]` - No additional skill needed.
  - Omitted: `backend-patterns` - Not implementation logic.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 4, 8 | Blocked By: 1

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `tests/shared/twitter-scenarios.json` - Shape and assertion vocabulary to mirror.
  - Pattern: `docs/testing-platform-expansion.md` - Scenario modeling checklist.
  - API/Type: `tests/shared/scenario-schema.json` - Updated schema constraints to satisfy.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io && python -m json.tool tests/shared/instagram-scenarios.json >/dev/null`
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io && python - <<'PY'
import json, jsonschema
schema=json.load(open('tests/shared/scenario-schema.json'))
insta=json.load(open('tests/shared/instagram-scenarios.json'))
jsonschema.validate(insta, schema)
print('ok')
PY`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: 5 Instagram scenario classes present
    Tool: Bash
    Steps: Parse tests/shared/instagram-scenarios.json and assert IDs include single-video, single-image, multi-image, hybrid, mixed-order
    Expected: All required IDs found exactly once
    Evidence: .sisyphus/evidence/task-2-instagram-scenarios-ids.txt

  Scenario: Filename expectations enforce instagram prefix
    Tool: Bash
    Steps: Parse all expected filename patterns in instagram scenarios
    Expected: Every pattern starts with ^instagram_ and ends with correct extension rule
    Evidence: .sisyphus/evidence/task-2-instagram-scenarios-filenames.txt
  ```

  **Commit**: YES | Message: `test(instagram): add shared instagram scenario matrix` | Files: `tests/shared/instagram-scenarios.json`

- [ ] 3. Add backend and frontend Instagram fixture packs derived from shared matrix

  **What to do**: Add deterministic fixture JSON files for each Instagram scenario under `backend/tests/fixtures/instagram/` and `frontend/tests/fixtures/instagram/`. Ensure fixtures include realistic extractor payload variants for reels, image, carousel, hybrid, thumbnail sparsity, and author/title absence.
  **Must NOT do**: Do not duplicate Twitter fixtures with only renamed fields; use Instagram-specific payload structures that exercise edge branches.

  **Recommended Agent Profile**:
  - Category: `testing` - Reason: Fixture quality determines deterministic reliability.
  - Skills: `[]` - No extra skill needed.
  - Omitted: `visual-engineering` - No UI work.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 4, 8 | Blocked By: 1

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `backend/tests/fixtures/twitter/*.json` - Fixture granularity baseline.
  - Pattern: `frontend/tests/fixtures/twitter/*.json` - Frontend fixture shape baseline.
  - Pattern: `tests/shared/instagram-scenarios.json` - Source matrix to map.
  - Pattern: `frontend/tests/e2e/helpers/mock-api.ts` - Expected fixture-to-api transformation behavior.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io && python -m json.tool backend/tests/fixtures/instagram/single-video.json >/dev/null`
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io && python -m json.tool frontend/tests/fixtures/instagram/single-video.json >/dev/null`
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io && python - <<'PY'
import glob, json
assert len(glob.glob('backend/tests/fixtures/instagram/*.json')) >= 5
assert len(glob.glob('frontend/tests/fixtures/instagram/*.json')) >= 5
for p in glob.glob('backend/tests/fixtures/instagram/*.json')+glob.glob('frontend/tests/fixtures/instagram/*.json'):
  json.load(open(p))
print('ok')
PY`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Fixture cardinality matches scenario matrix
    Tool: Bash
    Steps: Compare scenario count in tests/shared/instagram-scenarios.json vs file count in both fixture directories
    Expected: Both backend and frontend fixture counts equal matrix count
    Evidence: .sisyphus/evidence/task-3-fixture-cardinality.txt

  Scenario: Hybrid fixture contains mixed media entries
    Tool: Bash
    Steps: Parse hybrid fixture and check at least one video and one image entry are present
    Expected: Mixed media assertion passes
    Evidence: .sisyphus/evidence/task-3-hybrid-mixed-media.txt
  ```

  **Commit**: YES | Message: `test(instagram): add backend and frontend fixture packs` | Files: `backend/tests/fixtures/instagram/*`, `frontend/tests/fixtures/instagram/*`

- [ ] 4. Write failing backend integration suite for Instagram extraction (RED)

  **What to do**: Create `backend/tests/integration/api/test_extract_instagram.py` using fixture-driven coverage for all Instagram scenarios, plus explicit assertions for thumbnail fallback, filename prefix parity, and no 422 for supported media types.
  **Must NOT do**: Do not implement extractor fixes in this task; tests must fail initially on current behavior.

  **Recommended Agent Profile**:
  - Category: `testing` - Reason: TDD RED layer for backend behavior.
  - Skills: `[]` - Existing patterns are sufficient.
  - Omitted: `refactorer` - No production code edits yet.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 5, 6 | Blocked By: 1, 2, 3

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `backend/tests/integration/api/test_extract_twitter.py` - Structure and style baseline.
  - API/Type: `backend/app/schemas/extract.py` - Expected response fields.
  - Pattern: `backend/app/routers/extract.py` - Error code mapping logic.
  - Pattern: `backend/app/services/extractor.py` - Current branch points causing failures.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/backend && PYTHONPATH=. pytest tests/integration/api/test_extract_instagram.py -q -p no:mcp_eval` exits non-zero before implementation with at least one expected failure
  - [ ] Test file includes assertions for: platform=instagram, thumbnails presence, filename pattern `instagram_.*_copas_io`, and supported scenario success status

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: RED state captured for image/carousel/hybrid
    Tool: Bash
    Steps: Run only new Instagram integration suite on untouched extractor implementation
    Expected: Fails specifically on no-formats/422-related expectations
    Evidence: .sisyphus/evidence/task-4-instagram-red.txt

  Scenario: Existing Twitter integration remains green pre-fix
    Tool: Bash
    Steps: Run backend/tests/integration/api/test_extract_twitter.py
    Expected: Passes, proving new RED tests do not regress current behavior
    Evidence: .sisyphus/evidence/task-4-twitter-regression-pre-fix.txt
  ```

  **Commit**: YES | Message: `test(instagram): add failing extraction integration suite` | Files: `backend/tests/integration/api/test_extract_instagram.py`

- [ ] 5. Implement extractor normalization for Instagram image/carousel/hybrid (GREEN)

  **What to do**: Update `backend/app/services/extractor.py` so Instagram non-video media generates valid `formats` entries instead of empty list. Add image format generation path (single image + carousel image entries), mixed media flattening for hybrid, robust thumbnail fallback chain, and preserve media order for index-based filenames.
  **Must NOT do**: Do not alter Twitter-specific fallback semantics (`_fetch_fxtwitter` branch). Do not introduce platform-agnostic regressions to audio/video formatting.

  **Recommended Agent Profile**:
  - Category: `implementation` - Reason: Core production extractor behavior change.
  - Skills: `[]` - Existing module patterns are explicit.
  - Omitted: `frontend-patterns` - Backend-only task.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 6, 7, 8 | Blocked By: 4

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `backend/app/services/extractor.py` - `extract_media_info`, `_build_formats`, `_create_format`.
  - Pattern: `backend/app/routers/extract.py` - RuntimeError -> 422 mapping.
  - API/Type: `backend/app/schemas/extract.py:MediaResult` - output contract.
  - Test: `backend/tests/integration/api/test_extract_instagram.py` - expected behavior to satisfy.
  - Test: `backend/tests/integration/api/test_extract_twitter.py` - non-regression baseline.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/backend && PYTHONPATH=. pytest tests/integration/api/test_extract_instagram.py -q -p no:mcp_eval` exits 0
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/backend && PYTHONPATH=. pytest tests/integration/api/test_extract_twitter.py -q -p no:mcp_eval` exits 0

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Instagram image/carousel/hybrid no longer return 422
    Tool: Bash
    Steps: Run Instagram integration suite with fixtures for image, multi-image, hybrid
    Expected: All supported scenario tests return successful extract payload with non-empty formats
    Evidence: .sisyphus/evidence/task-5-instagram-green.txt

  Scenario: Twitter fallback behavior unchanged
    Tool: Bash
    Steps: Run targeted Twitter tests that cover image-only fallback and fxtwitter path
    Expected: Existing Twitter assertions pass without modification
    Evidence: .sisyphus/evidence/task-5-twitter-no-regression.txt
  ```

  **Commit**: YES | Message: `feat(instagram): support image carousel and hybrid extraction` | Files: `backend/app/services/extractor.py`

- [ ] 6. Fix backend filename parity and author resolution timing for Instagram tokens

  **What to do**: Ensure author is resolved before `_create_format` is called for both playlist and single-item Instagram flows so generated token filenames follow `instagram_<author>_copas_io[_index].ext`. Add explicit fallback when author absent (`instagram_copas_io...`) and sanitize consistently.
  **Must NOT do**: Do not rely only on frontend `a.download`; backend `Content-Disposition` must carry canonical filename.

  **Recommended Agent Profile**:
  - Category: `implementation` - Reason: Contract-facing filename semantics.
  - Skills: `[]` - Direct module edit + tests.
  - Omitted: `visual-engineering` - No UI changes required.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 8, 10 | Blocked By: 5

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `backend/app/services/extractor.py` - `_create_format` filename assembly.
  - Pattern: `backend/tests/integration/api/test_download_twitter.py` - header assertions baseline.
  - Pattern: `backend/tests/contract/test_download_contract.py` - content-disposition contract expectations.
  - Pattern: `frontend/hooks/use-download.ts` - frontend filename helper parity target.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/backend && PYTHONPATH=. pytest tests/integration/api/test_extract_instagram.py -q -p no:mcp_eval -k filename`
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/backend && PYTHONPATH=. pytest tests/integration/api/test_download_twitter.py -q -p no:mcp_eval -k instagram`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Author-present filename uses instagram_author prefix
    Tool: Bash
    Steps: Extract reel fixture with uploader/author and assert generated download filename includes instagram_<author>_copas_io
    Expected: Pattern matches exactly with normalized author slug
    Evidence: .sisyphus/evidence/task-6-filename-author.txt

  Scenario: Author-missing fallback remains deterministic
    Tool: Bash
    Steps: Extract fixture with missing author/title and inspect Content-Disposition from download endpoint token
    Expected: Filename falls back to instagram_copas_io[_index].ext, no empty double underscores
    Evidence: .sisyphus/evidence/task-6-filename-fallback.txt
  ```

  **Commit**: YES | Message: `fix(instagram): align token filename generation with naming contract` | Files: `backend/app/services/extractor.py`, `backend/tests/integration/api/test_extract_instagram.py`

- [ ] 7. Add backend unit/contract coverage for Instagram extractor edge behavior

  **What to do**: Extend backend unit and contract tests to lock behavior for: thumbnail fallback precedence, mixed-media ordering, filename fallback, and 422 only for truly unsupported/failed extraction cases. Add focused tests in `backend/tests/unit/services/` and update contract checks if needed.
  **Must NOT do**: Do not duplicate integration assertions verbatim; unit tests must isolate helper-level logic and edge branches.

  **Recommended Agent Profile**:
  - Category: `testing` - Reason: Behavior lock-in and regression prevention.
  - Skills: `[]` - Existing pytest patterns sufficient.
  - Omitted: `frontend-patterns` - Backend-only.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 10 | Blocked By: 5

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `backend/tests/unit/services/test_extractor_helpers.py` - helper-level mocking style.
  - Pattern: `backend/tests/contract/test_download_contract.py` - endpoint contract style.
  - Pattern: `backend/tests/conftest.py` - token_store module patch + limiter reset.
  - API/Type: `backend/app/services/extractor.py` - branches to isolate.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/backend && PYTHONPATH=. pytest tests/unit/services/test_extractor_helpers.py -q -p no:mcp_eval`
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/backend && PYTHONPATH=. pytest tests/contract/test_download_contract.py -q -p no:mcp_eval`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Thumbnail fallback order is deterministic
    Tool: Bash
    Steps: Run unit tests for cases where thumbnail is missing at top-level but present in thumbnails array/entry
    Expected: Correct fallback value chosen and exposed in MediaResult
    Evidence: .sisyphus/evidence/task-7-thumbnail-fallback.txt

  Scenario: Unsupported extraction still reports 422 contract shape
    Tool: Bash
    Steps: Trigger forced extractor runtime failure case and assert API error contract
    Expected: HTTP 422 with code EXTRACTION_FAILED and deterministic message format
    Evidence: .sisyphus/evidence/task-7-error-contract.txt
  ```

  **Commit**: YES | Message: `test(instagram): add unit and contract edge coverage` | Files: `backend/tests/unit/services/*`, `backend/tests/contract/*`

- [ ] 8. Build Instagram deterministic Playwright suite (RED->GREEN) including thumbnail and filename checks

  **What to do**: Add `frontend/tests/e2e/instagram-deterministic.spec.ts` using `mockExtractApi` and `mockDownloadApi` over Instagram fixtures. Cover single reel video, single image, multi-image, hybrid; assert thumbnail rendering, section behavior, button availability, download token calls, and filename expectations from mocked `Content-Disposition`.
  **Must NOT do**: Do not use live Instagram URLs in deterministic test. Do not depend on `page.on('download')` for correctness.

  **Recommended Agent Profile**:
  - Category: `testing` - Reason: Deterministic UI/download behavior verification.
  - Skills: `[]` - Existing harness is adequate.
  - Omitted: `frontend-ui-ux` - No redesign.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: 9, 10 | Blocked By: 1, 2, 3, 5, 6

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `frontend/tests/e2e/twitter-deterministic.spec.ts` - scenario structure and assertions.
  - Pattern: `frontend/tests/e2e/helpers/mock-api.ts` - deterministic extract/download mocks.
  - Pattern: `frontend/components/result-card.tsx` - thumbnail source and section testids.
  - Pattern: `frontend/hooks/use-download.ts` - filename builder behavior.
  - Fixture: `frontend/tests/fixtures/instagram/*.json` - scenario inputs.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/frontend && npx playwright test tests/e2e/instagram-deterministic.spec.ts --project=chromium`
  - [ ] Test suite includes explicit network guard assertion that no outbound `instagram.com`/`cdninstagram.com`/`fbcdn.net` calls occur during deterministic mode

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Reel thumbnail becomes visible in result card
    Tool: Playwright
    Steps: Load reel scenario fixture, submit URL, wait for result-card, query thumbnail image(s)
    Expected: At least one thumbnail is rendered and visible
    Evidence: .sisyphus/evidence/task-8-reel-thumbnail.png

  Scenario: Hybrid scenario exposes both media sections and deterministic downloads
    Tool: Playwright
    Steps: Open hybrid fixture scenario, expand image section, click one video and one image format button
    Expected: Both download calls hit mocked `/api/download` with tokens; no external network requests recorded
    Evidence: .sisyphus/evidence/task-8-hybrid-download.txt
  ```

  **Commit**: YES | Message: `test(instagram): add deterministic playwright coverage` | Files: `frontend/tests/e2e/instagram-deterministic.spec.ts`, `frontend/tests/e2e/helpers/*`

- [ ] 9. Align frontend filename helper behavior with backend header contract and add explicit assertions

  **What to do**: Ensure frontend tests assert parity between expected naming convention and backend `Content-Disposition` header semantics. If helper behavior differs, adjust `frontend/hooks/use-download.ts` tests/logic to avoid drift while keeping backend header as canonical truth.
  **Must NOT do**: Do not make frontend filename logic the only source of truth for correctness claims.

  **Recommended Agent Profile**:
  - Category: `testing` - Reason: Mostly assertion/behavior lock for naming parity.
  - Skills: `[]` - Existing test harness supports this.
  - Omitted: `backend-patterns` - No backend edits expected unless parity bug is discovered.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 10 | Blocked By: 8

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `frontend/hooks/use-download.ts` - local filename generation.
  - Pattern: `frontend/lib/api.ts` - download trigger behavior.
  - Test: `frontend/tests/e2e/instagram-deterministic.spec.ts` - deterministic assertions target.
  - Test: `backend/tests/integration/api/test_download_twitter.py` - header assertion baseline style.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/frontend && npx playwright test tests/e2e/instagram-deterministic.spec.ts --project=chromium -g "filename|download"`
  - [ ] Naming assertions pass for author-present and author-missing scenarios

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: Author-present file naming parity
    Tool: Playwright
    Steps: Use reel fixture with author, mock download header filename, trigger download button
    Expected: Test asserts deterministic expected filename pattern and header-driven canonical behavior
    Evidence: .sisyphus/evidence/task-9-filename-author.txt

  Scenario: Author-missing fallback parity
    Tool: Playwright
    Steps: Use fixture without author/title, trigger download path
    Expected: Assertions confirm fallback pattern `instagram_copas_io` (with optional index) and no malformed underscores
    Evidence: .sisyphus/evidence/task-9-filename-fallback.txt
  ```

  **Commit**: YES | Message: `test(frontend): lock instagram filename parity assertions` | Files: `frontend/hooks/use-download.ts`, `frontend/tests/e2e/instagram-deterministic.spec.ts`

- [ ] 10. Integrate Instagram deterministic coverage into CI and preserve deterministic/live split

  **What to do**: Update CI workflows so Instagram deterministic tests run in PR gate alongside existing backend/frontend deterministic suites. Keep live smoke non-blocking and separate (create Instagram live smoke workflow only if fixtures/URLs are stable and explicitly tagged `@live`).
  **Must NOT do**: Do not merge live smoke checks into PR blocking jobs.

  **Recommended Agent Profile**:
  - Category: `implementation` - Reason: Workflow orchestration and gating.
  - Skills: `[]` - Existing workflow patterns reusable.
  - Omitted: `security-auditor` - Not security-specific.

  **Parallelization**: Can Parallel: NO | Wave 4 | Blocks: 11 | Blocked By: 6, 7, 8, 9

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `.github/workflows/tests.yml` - deterministic gate baseline.
  - Pattern: `.github/workflows/twitter-live-smoke.yml` - live smoke separation pattern.
  - Test: `frontend/tests/e2e/instagram-deterministic.spec.ts` - CI target spec.
  - Test: `backend/tests/integration/api/test_extract_instagram.py` - backend CI inclusion.

  **Acceptance Criteria** (agent-executable only):
  - [ ] CI workflow config parses: `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io && python - <<'PY'
import yaml
yaml.safe_load(open('.github/workflows/tests.yml'))
print('ok')
PY`
  - [ ] Local representative deterministic command list in workflow includes Instagram suites without `@live` tag

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: PR gate includes Instagram deterministic suites
    Tool: Bash
    Steps: Inspect .github/workflows/tests.yml for backend and frontend steps referencing Instagram tests or umbrella deterministic commands that include them
    Expected: Instagram deterministic coverage executes in CI PR flow
    Evidence: .sisyphus/evidence/task-10-ci-deterministic.txt

  Scenario: Live tests remain isolated
    Tool: Bash
    Steps: Inspect workflows for @live usage and triggers
    Expected: Live suites are scheduled/manual and non-blocking for PR jobs
    Evidence: .sisyphus/evidence/task-10-ci-live-isolation.txt
  ```

  **Commit**: YES | Message: `chore(ci): include instagram deterministic coverage in pr gate` | Files: `.github/workflows/tests.yml`, `.github/workflows/*instagram*.yml`

- [ ] 11. Run full regression wave and publish evidence bundle

  **What to do**: Execute full backend + frontend deterministic suites including Twitter regression, collect evidence artifacts under `.sisyphus/evidence/`, and update platform expansion docs with Instagram-specific gotchas and fixture checklist.
  **Must NOT do**: Do not mark task complete with partial suite runs.

  **Recommended Agent Profile**:
  - Category: `testing` - Reason: Final validation and evidence collation.
  - Skills: `[]` - No specialized skill needed.
  - Omitted: `implementation` - Should not introduce new feature changes unless blockers are found.

  **Parallelization**: Can Parallel: NO | Wave 4 | Blocks: Final Verification Wave | Blocked By: 10

  **References** (executor has NO interview context - be exhaustive):
  - Pattern: `backend/pytest.ini` - marker and runtime config.
  - Pattern: `backend/tests/conftest.py` - token store + limiter fixtures.
  - Test: `backend/tests/integration/api/test_extract_twitter.py` - regression anchor.
  - Test: `frontend/tests/e2e/twitter-deterministic.spec.ts` - regression anchor.
  - Doc: `docs/testing-platform-expansion.md` - update template with Instagram notes.

  **Acceptance Criteria** (agent-executable only):
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/backend && PYTHONPATH=. pytest -m "unit or integration or contract" --ignore=tests/live -q -p no:mcp_eval`
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/frontend && npx playwright test tests/e2e/instagram-deterministic.spec.ts --project=chromium`
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/frontend && npx playwright test tests/e2e/twitter-deterministic.spec.ts --project=chromium`
  - [ ] `cd /Volumes/WORKSPACES/01-PROJECTS/personal/copas.io/frontend && npm run build`

  **QA Scenarios** (MANDATORY - task incomplete without these):
  ```text
  Scenario: End-to-end deterministic green wave
    Tool: Bash
    Steps: Run full backend deterministic markers + Instagram and Twitter deterministic Playwright specs
    Expected: All commands exit 0 with no flaky retries needed
    Evidence: .sisyphus/evidence/task-11-full-regression.txt

  Scenario: Evidence completeness and doc update
    Tool: Bash
    Steps: Verify .sisyphus/evidence contains artifacts for tasks 1-11 and docs/testing-platform-expansion.md includes Instagram section
    Expected: Evidence files present and docs updated with Instagram-specific guidance
    Evidence: .sisyphus/evidence/task-11-evidence-docs.txt
  ```

  **Commit**: YES | Message: `docs(testing): finalize instagram expansion evidence and guidance` | Files: `.sisyphus/evidence/*`, `docs/testing-platform-expansion.md`

## Final Verification Wave (4 parallel agents, ALL must APPROVE)
- [ ] F1. Plan Compliance Audit - oracle
- [ ] F2. Code Quality Review - unspecified-high
- [ ] F3. Real Agent QA - unspecified-high (+ playwright if UI)
- [ ] F4. Scope Fidelity Check - deep

## Commit Strategy
- Commit per completed wave, keep backend/frontend/schema updates logically grouped.
- Suggested prefixes: `test(instagram): ...`, `feat(instagram): ...`, `chore(ci): ...`, `docs(testing): ...`.
- Never mix live-smoke-only changes with deterministic gate logic in one commit.

## Success Criteria
- Instagram reels/image/carousel/hybrid all extract successfully with valid download options.
- Instagram filename behavior follows parity rule and is verified through backend headers + deterministic frontend assertions.
- Reels thumbnail renders in UI from normalized backend payload.
- Full deterministic test suite passes with no external social network calls.
- Twitter deterministic/integration suites remain green.
