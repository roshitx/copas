## [2026-03-02] Task: All T1-T11 + F1-F4 COMPLETE

### Verification Results
- Backend: 89 tests pass (unit + integration + contract)
- Frontend Playwright: 30/30 deterministic tests pass
- Frontend build: exits 0

### Key Learnings

#### Backend
- pytest must be run with `PYTHONPATH=.` from backend/ dir — no virtualenv, uses system pytest
- Disable global mcp_eval pytest plugin: `-p no:mcp_eval`
- `--ignore=tests/live` required to skip live tests in PR gate (they use `@pytest.mark.timeout`)
- `timeout` marker must be in pytest.ini markers list or --strict-markers fails
- token_store must be patched at `app.services.extractor._token_store_module.token_store` (module-level import pattern for mockability)
- Rate limiter (slowapi) must be reset in autouse fixture: `limiter.reset()` before+after each test
- conftest.py patches at two paths: `app.services.extractor._token_store_module.token_store` + direct

#### Frontend Playwright
- `page.route()` intercepts at http://localhost:8000/api/... pattern — must match full URL including protocol+host
- `triggerBrowserDownload` (creates <a> element and clicks) does NOT trigger Playwright's page.on('download') — test via route intercept flag or just verify button is clickable
- `video-section` details element has `open` attr by default — DO NOT click its summary (closes it)
- `video-group` details element has `open` attr by default — DO NOT click its summary
- `image-section` details element is CLOSED by default — must click summary to expand before asserting format buttons inside
- Strict mode: when locator resolves to multiple elements, use `.first()` or scope to specific parent
- `getByText('Video 1')` also matches accordion summary text — use `getByTestId('format-button').filter({hasText:'Video 1'})` instead
- In hybrid scenario: 1 video renders directly in video-section (not video-group) — use `videoSection.getByTestId('format-button').first()`

#### result-card.tsx data-testids
- `result-card` — outer wrapper
- `video-section` — accordion for videos (open by default)
- `video-group` — nested accordion per video group (open by default, only in isMultiVideo)
- `image-section` — accordion for images (closed by default)
- `audio-section` — accordion for audio (closed by default)
- `format-button` — every download button
- `download-all-button` — Download Semua Foto button

#### CI
- Backend CI must use: `PYTHONPATH=. pytest -m "unit or integration or contract" --ignore=tests/live -p no:mcp_eval`
- Frontend CI: kill port 3000 before running (dev server may conflict)
- Live smoke: run backend with `uvicorn app.main:app` then wait for /health

### Files Delivered
- backend/requirements-dev.txt, pytest.ini
- backend/tests/unit/services/test_token_store.py (10 tests)
- backend/tests/unit/services/test_extractor_helpers.py (37 tests)
- backend/tests/integration/api/test_extract_twitter.py (17 tests)
- backend/tests/integration/api/test_download_twitter.py (15 tests)
- backend/tests/contract/test_download_contract.py (10 tests)
- backend/tests/conftest.py
- frontend/playwright.config.ts
- frontend/tests/e2e/helpers/mock-api.ts
- frontend/tests/e2e/twitter-deterministic.spec.ts (30 tests)
- frontend/tests/e2e/twitter-live-smoke.spec.ts (5 @live tests)
- tests/shared/twitter-scenarios.json (5 scenarios)
- tests/shared/scenario-schema.json
- frontend/tests/fixtures/twitter/ (5 fixture JSONs)
- backend/tests/fixtures/twitter/ (5 fixture JSONs)
- .github/workflows/tests.yml
- .github/workflows/twitter-live-smoke.yml
- docs/testing-platform-expansion.md
