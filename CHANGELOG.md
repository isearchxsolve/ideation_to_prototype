# Changelog

All notable changes to this project are documented here.

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
