# Testing Platform Expansion Guide

This document describes how to extend the copas.io test suite to support additional platforms beyond Twitter/X.

## Architecture Overview

The test system follows a 4-layer architecture for validating media extraction platforms:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Scenario Matrix                                          │
│    tests/shared/{platform}-scenarios.json                   │
│    Defines test cases, URLs, expectations                   │
└───────────────┬─────────────────────────────────────────────┘
                │
                ├──────────────────────────────────────────┐
                │                                           │
┌───────────────▼──────────────────┐  ┌───────────────────▼──────────────────┐
│ 2. Backend Fixtures               │  │ Frontend Fixtures                     │
│    backend/tests/fixtures/        │  │    frontend/tests/fixtures/           │
│    {platform}/*.json              │  │    {platform}/*.json                 │
│    Mock API responses             │  │    Mock UI data                        │
└───────────────┬──────────────────┘  └───────────────────┬──────────────────┘
                │                                           │
                └───────────────┬───────────────────────────┘
                                │
                ┌───────────────▼───────────────────────────────────┐
│ 3. Backend Integration Tests                       │
                │    backend/tests/integration/api/                  │
                │    test_extract_{platform}.py                     │
                │    Validates API responses against fixtures       │
                └───────────────┬───────────────────────────────────┘
                                │
                ┌───────────────▼───────────────────────────────────┐
│ 4. Frontend E2E Tests                             │
                │    frontend/tests/e2e/                            │
                │    {platform}-deterministic.spec.ts                │
                │    Validates full UI flow with deterministic data │
                └───────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Purpose | Validation Target |
|-------|---------|-------------------|
| Scenario Matrix | Defines what to test | Data model consistency |
| Backend Fixtures | Mock API behavior | API contract |
| Frontend Fixtures | Mock UI state | UI component rendering |
| Backend Tests | API extraction logic | Business logic |
| E2E Tests | Full user journey | End-to-end reliability |


## Directory Structure

```
tests/
  shared/
    twitter-scenarios.json       # Twitter test scenario matrix
    <platform>-scenarios.json    # Add one per new platform
    scenario-schema.json         # JSON schema for all scenario files

backend/
  tests/
    unit/
      services/
        test_token_store.py
        test_extractor_helpers.py
        test_<platform>_helpers.py   # Add per platform
    integration/
      api/
        test_extract_twitter.py
        test_extract_<platform>.py   # Add per platform
        test_download_twitter.py
        test_download_<platform>.py  # Add per platform
    contract/
      test_download_contract.py      # Generic; covers all platforms
    fixtures/
      twitter/                       # One JSON per scenario
      <platform>/                    # Add per platform

frontend/
  tests/
    fixtures/
      twitter/                       # One JSON per scenario
      <platform>/                    # Add per platform
    e2e/
      twitter-deterministic.spec.ts
      <platform>-deterministic.spec.ts  # Add per platform
      twitter-live-smoke.spec.ts
      <platform>-live-smoke.spec.ts     # Add per platform
```

## Step 1 — Define Scenarios

Create `tests/shared/<platform>-scenarios.json` following the schema in `tests/shared/scenario-schema.json`.

Minimum required scenarios per platform:
- Single media (image or video)
- Multi-media (same type)
- Mixed media (if platform supports it)

Each scenario entry:

```json
{
  "id": "<platform>-<type>",
  "platform": "<platform>",
  "url": "https://...",
  "author": "<handle>",
  "media_count": 1,
  "types": ["image"],
  "expected_filename": "<platform>_<author>_copas_io.<ext>",
  "expected_zip": null
}
```

## Step 2 — Backend Fixtures

Create `backend/tests/fixtures/<platform>/` with one JSON file per scenario.

Each fixture file shape:

```json
{
  "scenario_id": "<platform>-<type>",
  "input_url": "https://...",
  "mock_fxtwitter_response": {},
  "expected_result": {
    "platform": "<platform>",
    "author": "<handle>",
    "title": "...",
    "formats": [],
    "thumbnails": [],
    "thumbnail": "..."
  }
}
```

Replace `mock_fxtwitter_response` with the appropriate external API response mock for the platform.

## Step 3 — Frontend Fixtures

Create `frontend/tests/fixtures/<platform>/` mirroring the backend fixtures.

Each file drives the Playwright route stub. Required shape:

```json
{
  "scenario_id": "<platform>-<type>",
  "platform": "<platform>",
  "author": "<handle>",
  "title": "...",
  "formats": [
    {
      "id": "...",
      "label": "...",
      "type": "video/mp4",
      "size_mb": null,
      "download_url": "/api/download?token=mock_token_<scenario_id>"
    }
  ],
  "thumbnail": "https://...",
  "thumbnails": ["https://..."],
  "duration": null
}
```

## Step 4 — Backend Unit Tests

Create `backend/tests/unit/services/test_<platform>_helpers.py` covering:
- Format extraction from platform-specific API response
- Filename generation
- Thumbnail resolution
- Edge cases: missing fields, empty media arrays, rate-limit responses

Mark tests: `@pytest.mark.unit`

## Step 5 — Backend Integration Tests

Create `backend/tests/integration/api/test_extract_<platform>.py`.

Follow the pattern in `test_extract_twitter.py`:
- Mock the external API call with `respx`
- Mock `token_store` via module reference (not direct import)
- Reset rate limiter in autouse fixture
- Cover: all scenario types, error cases (404, 429, 500, timeout)

Create `backend/tests/integration/api/test_download_<platform>.py` if the platform uses platform-specific download tokens.

Mark tests: `@pytest.mark.integration`

## Step 6 — Frontend Deterministic E2E

Create `frontend/tests/e2e/<platform>-deterministic.spec.ts`.

Follow the pattern in `twitter-deterministic.spec.ts`:
- Import fixtures from `frontend/tests/fixtures/<platform>/`
- Use `mockExtractApi` and `mockDownloadApi` from `tests/e2e/helpers/mock-api.ts`
- One `test.describe` block per scenario
- Assert: result card visible, format labels, download interaction, filename pattern

## Step 7 — Live Smoke Tests

Create `frontend/tests/e2e/<platform>-live-smoke.spec.ts`.

Follow the pattern in `twitter-live-smoke.spec.ts`:
- Tag each test with `@live`
- Use `test.describe.configure({ retries: 2, timeout: 60_000 })`
- 5+ canonical URLs covering each scenario type
- Assertions: result card visible, at least one download button
- Screenshot capture on completion

## Step 8 — CI Integration

### PR Gate (`tests.yml`)

Add two new jobs following the existing pattern:

```yaml
backend-<platform>:
  name: Backend <Platform> Tests
  # ... same as backend-integration job
  - name: Run <platform> tests
    run: pytest -m "integration or contract" -k <platform> -q

frontend-<platform>-deterministic:
  name: Frontend <Platform> Deterministic E2E
  # ... same as frontend-deterministic job
  - name: Run deterministic tests
    run: npx playwright test tests/e2e/<platform>-deterministic.spec.ts --project=chromium
```

### Live Smoke (`twitter-live-smoke.yml`)

Add the new platform's live smoke file to the existing job:

```yaml
- name: Run live smoke suite
  run: npx playwright test tests/e2e/twitter-live-smoke.spec.ts tests/e2e/<platform>-live-smoke.spec.ts --project=chromium --grep @live
```

Or create a separate `<platform>-live-smoke.yml` following the same structure.

## Canonical URL Selection Criteria

Choose 5 canonical test URLs per platform that cover:
1. Single image post
2. Single video post
3. Multi-image post (if platform supports)
4. Multi-video post (if platform supports)
5. Mixed media post (if platform supports)

Prefer:
- Public accounts with stable, long-lived content
- Posts from high-follower accounts (less likely to be deleted)
- Posts without age restriction or login requirement

## Rate Limiter Considerations

The backend uses `slowapi` with a 10/minute default limit per IP.

In backend integration tests, reset the limiter between tests using the autouse conftest fixture:

```python
@pytest.fixture(autouse=True)
def reset_rate_limiter():
    from app.main import limiter
    limiter.reset()
    yield
    limiter.reset()
```

If the new platform has a separate limiter or different rate, add a corresponding reset.

## Token Store Mockability

To allow integration tests to mock `token_store`, the module must import it by module reference:

```python
# In extractor.py or equivalent
import app.services.token_store as _token_store_module

# Usage inside functions:
token = _token_store_module.token_store.create(...)
```

This allows tests to patch `app.services.extractor._token_store_module.token_store` cleanly.


## Required Fixture Fields (From Schema)

### Scenario Matrix Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✓ | Unique identifier, pattern `{platform}-{scenario-type}` |
| `url` | string | ✓ | Valid platform URL |
| `platform` | string | ✓ | Platform name (must match enum in schema) |
| `author` | string | ✓ | Content creator handle |
| `expected.media_count` | integer | ✓ | Number of media items |
| `expected.types` | array | ✓ | Array of `["image", "video"]` |
| `expected.filename_pattern` | string | Conditional | Pattern for single media (required if single) |
| `expected.filename_patterns` | array | Conditional | Array of patterns for multi-media (required if multi) |
| `zip_expectations` | object\|null | ✓ | Zip behavior (or null for single items) |
| `zip_expectations.should_zip` | boolean | Conditional | Whether to create zip |
| `zip_expectations.zip_filename` | string | Conditional | Zip filename pattern |
| `zip_expectations.file_count` | integer | Conditional | Number of files in zip (min: 2) |

### Backend Fixture Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scenario_id` | string | ✓ | Links to scenario matrix |
| `input_url` | string | ✓ | Test URL |
| `expected_backend_response.platform` | string | ✓ | Platform identifier |
| `expected_backend_response.author` | string | ✓ | Content creator |
| `expected_backend_response.title` | string | ✓ | Content title |
| `expected_backend_response.formats` | array | ✓ | Download options |
| `expected_backend_response.formats[].id` | string | ✓ | Format ID |
| `expected_backend_response.formats[].label` | string | ✓ | Display label |
| `expected_backend_response.formats[].type` | string | ✓ | MIME type |
| `expected_backend_response.formats[].size_mb` | number\|null | ✓ | File size or null |
| `expected_backend_response.formats[].download_url` | string | ✓ | API download endpoint |
| `expected_backend_response.thumbnails` | array | ✓ | Thumbnail URLs |
| `expected_backend_response.thumbnail` | string\|null | ✓ | Primary thumbnail |
| `expected_backend_response.duration` | integer\|null | ✓ | Video duration in seconds |
| `validation_rules` | object | ✓ | Validation config |
| `validation_rules.must_have_formats` | boolean | ✓ | Check formats array |
| `validation_rules.must_have_thumbnails` | boolean | ✓ | Check thumbnails array |
| `validation_rules.expected_platform` | string | ✓ | Platform name |
| `validation_rules.expected_author` | string | ✓ | Author username |
| `validation_rules.media_type_check` | string | ✓ | `"image"` or `"video"` |

### Frontend Fixture Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scenario_id` | string | ✓ | Links to scenario matrix |
| `ui_state.loading` | boolean | ✓ | Loading state |
| `ui_state.error` | string\|null | ✓ | Error message or null |
| `ui_state.data.platform` | string | ✓ | Platform name |
| `ui_state.data.title` | string | ✓ | Content title |
| `ui_state.data.author` | string | ✓ | Creator handle |
| `ui_state.data.thumbnail` | string | ✓ | Preview image |
| `ui_state.data.formats` | array | ✓ | Download options |
| `ui_state.data.formats[].id` | string | ✓ | Format ID |
| `ui_state.data.formats[].label` | string | ✓ | Display label |
| `ui_state.data.formats[].type` | string | ✓ | MIME type |
| `ui_state.data.formats[].size_mb` | number\|null | ✓ | File size or null |
| `ui_state.downloadState.isDownloading` | boolean | ✓ | Download in progress |
| `ui_state.downloadState.downloadedFile` | string\|null | ✓ | Filename or null |
| `ui_state.downloadState.downloadError` | string\|null | ✓ | Error or null |

## Required Assertions Per Scenario Type

### Single Image
```python
assert data["platform"] == expected_platform
assert data["author"] == expected_author
assert len(data["formats"]) == 1
assert all(f["type"].startswith("image/") for f in data["formats"])
assert data["duration"] is None
assert len(data["thumbnails"]) > 0
```

### Single Video
```python
assert data["platform"] == expected_platform
assert data["author"] == expected_author
assert len(data["formats"]) == 1
assert all(f["type"].startswith("video/") for f in data["formats"])
assert data["duration"] is not None
assert data["duration"] > 0
assert len(data["thumbnails"]) > 0
```

### Multi Image
```python
assert data["platform"] == expected_platform
assert data["author"] == expected_author
assert len(data["formats"]) >= 2
assert all(f["type"].startswith("image/") for f in data["formats"])
assert data["duration"] is None
assert len(data["thumbnails"]) >= 2
```

### Multi Video
```python
assert data["platform"] == expected_platform
assert data["author"] == expected_author
assert len(data["formats"]) >= 2
assert all(f["type"].startswith("video/") for f in data["formats"])
assert data["duration"] is not None
assert data["duration"] > 0
assert len(data["thumbnails"]) >= 2
```

### Hybrid (Video + Image)
```python
assert data["platform"] == expected_platform
assert data["author"] == expected_author
assert len(data["formats"]) >= 2
assert any(f["type"].startswith("image/") for f in data["formats"])
assert any(f["type"].startswith("video/") for f in data["formats"])
assert data["duration"] is not None
assert data["duration"] > 0
assert len(data["thumbnails"]) >= 2
```

## Naming Conventions

### Files

| Type | Pattern | Example |
|------|---------|--------|
| Scenario matrix | `{platform}-scenarios.json` | `instagram-scenarios.json` |
| Platform template | `platform-template.json` | `platform-template.json` |
| Backend fixture | `{scenario-type}.json` | `single-image.json`, `multi-video.json` |
| Backend test | `test_extract_{platform}.py` | `test_extract_instagram.py` |
| Frontend fixture | `{scenario-type}.json` | `single-image.json` |
| Frontend E2E test | `{platform}-deterministic.spec.ts` | `instagram-deterministic.spec.ts` |
| Live smoke test | `{platform}-live-smoke.spec.ts` | `instagram-live-smoke.spec.ts` |

### Directories

| Type | Pattern | Example |
|------|---------|---------|
| Backend fixtures | `backend/tests/fixtures/{platform}/` | `backend/tests/fixtures/instagram/` |
| Frontend fixtures | `frontend/tests/fixtures/{platform}/` | `frontend/tests/fixtures/instagram/` |
| Backend integration | `backend/tests/integration/api/` | `backend/tests/integration/api/` |
| Frontend E2E | `frontend/tests/e2e/` | `frontend/tests/e2e/` |

### Test Markers

| Marker | Purpose | Usage |
|--------|---------|-------|
| `@pytest.mark.unit` | Unit tests | `@pytest.mark.unit` |
| `@pytest.mark.integration` | Integration tests | `@pytest.mark.integration` |
| `@pytest.mark.contract` | Contract tests | `@pytest.mark.contract` |
| `@live` (Playwright) | Live API calls | `@test('test name', { tag: ['@live'] })` |
| `@pytest.mark.live` | Live backend tests | `@pytest.mark.live` |
| `@pytest.mark.deterministic` | Deterministic fixtures | `@pytest.mark.deterministic` |
| `@pytest.mark.smoke` | Smoke tests | `@pytest.mark.smoke` |
| `@pytest.mark.slow` | Slow tests (run separately) | `@pytest.mark.slow` |

### Scenario IDs

Format: `{platform}-{scenario-type}`

Examples:
- `twitter-single-image`
- `instagram-multi-video-2`
- `youtube-single-video`
- `tiktok-multi-image-4`

Scenario types:
- `single-image`
- `single-video`
- `multi-image-{count}`
- `multi-video-{count}`
- `hybrid-video-image`
- `carousel` (for platforms with carousels)

## Validation Checklist

Before submitting a new platform:

- [ ] Scenario matrix created at `tests/shared/{platform}-scenarios.json`
- [ ] All scenarios have required fields (id, url, platform, author, expected, zip_expectations)
- [ ] Backend fixtures created in `backend/tests/fixtures/{platform}/`
- [ ] All backend fixtures validate against schema
- [ ] Frontend fixtures created in `frontend/tests/fixtures/{platform}/`
- [ ] Backend integration tests created at `backend/tests/integration/api/test_extract_{platform}.py`
- [ ] Frontend E2E tests created at `frontend/tests/e2e/{platform}-deterministic.spec.ts`
- [ ] Live smoke tests added with `@live` marker
- [ ] CI workflow updated to include new platform test suites
- [ ] All test files follow naming conventions
- [ ] All scenarios have appropriate assertions
- [ ] Schema updated if platform-specific fields needed
- [ ] Documentation reviewed and updated
