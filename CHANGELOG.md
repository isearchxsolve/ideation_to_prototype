# Changelog

All notable changes to this project are documented here.

## [1.1.0] - 2026-08-16

### Added
- Production-ready Dockerfile: non-root user, `HEALTHCHECK` against
  `/health`, version label via `--build-arg VERSION`. Installs only the
  slim runtime deps (`requirements-app.txt`), not the full QA toolchain.
- `src/demo/config.py` — Pydantic Settings model that validates all runtime
  config (host, port, browser, credentials) at startup and fails fast on
  invalid values. Supports `.env` for local development.
- `docs/DEPLOYMENT.md` — Docker/Kubernetes deployment guide, rollback
  procedure, observability notes, and a production security checklist.
- `docs/TEST_EVIDENCE.md` — maps each production-readiness claim to concrete
  results from the 1,220-case Selenium suite (junit.xml, per-test JSON,
  5-run stability window, security-test outcomes).
- `LICENSE` (MIT) and README references to deployment docs + license.
- CI `lint` job (ruff + black + acceptance gate) and `security` job
  (pip-audit dependency scan + hardcoded-secret scan) gating the test matrix.

### Changed
- Demo app reads config from the validated Settings model instead of raw
  `os.environ` reads; default host is `127.0.0.1` (containers set
  `APP_HOST=0.0.0.0` explicitly).
- Chromium-based browsers (Chrome/Edge) now launch with container-safe
  hardening flags (`--no-sandbox`, `--disable-dev-shm-usage`, `--disable-gpu`)
  consistently in both `tests/conftest.py` and `src/qa/driver_factory.py`.
- Worker WebDriver is now wrapped in a self-healing holder (`_DriverHolder`):
  if a browser session dies mid-run (OOM/renderer crash), the next test
  transparently provisions a fresh browser instead of cascading into
  hundreds of `InvalidSessionIdException` errors.
- Added Chromium memory-reduction flags (disable extensions, background
  networking, sync, component updates, etc.) so 4 parallel workers fit on
  16GB runners without OOM-killing a renderer.

### Fixed
- Flaky `test_signup_login_post_message_journey_browser` — replaced
  implicit-wait-only navigation with explicit `WebDriverWait` at every page
  boundary, eliminating the race where `driver.get("/login")` ran before the
  signup POST settled. Now passes 20/20 under parallel load.

## [1.0.0] - 2026-08-16

### Added
- 1,220 Selenium WebDriver test cases (smoke 110, functional 800,
  regression 210, e2e 100) against the Flask demo app.
- Page Object Model layer: BasePage + page objects for home, login, signup,
  dashboard, messages, and about pages, with a PageFactory registry.
- Deterministic test-data factory (users, products, orders, payments).
- Live-server fixture that boots the Flask app per xdist worker.
- Worker-scoped WebDriver reuse with per-test cookie/alert reset — full
  suite runs in ~20 minutes on 4 workers (NFR: < 60 min).
- HTML + JUnit reporting, per-test JSON records, screenshots on failure.
- GitHub Actions CI (`.github/workflows/qa.yml`) running each suite bucket
  headless on push/PR with artifact upload.
- `docs/coverage_matrix.md` mapping features to tests.
- `validate_project.py` acceptance-criteria gate.
- `run_stability.py` for 5-consecutive-run stability evidence.
- Root README with run/debug/extend instructions.
- Pinned `requirements-qa.txt`.

### Fixed
- XSS vulnerability in the demo app message board (message text is now
  HTML-escaped before rendering).
- Cookie/session leakage between tests (cookies now cleared on the app
  origin; leftover alerts dismissed before each test).
- Live-server port race between parallel xdist workers (ephemeral port
  fallback).
- `TestDataFactory.payment()` undefined-name bug (`_rng` → `self._rng`).
- Broken root Dockerfile (previously ran a truncated agent fragment; now
  serves the demo app).
- ruff + black clean across `tests/` and `src/`.

### Removed
- Tracked `__pycache__/*.pyc` files and accidental tool-output files.
