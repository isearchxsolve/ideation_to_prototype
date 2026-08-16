# Selenium QA Automation Suite

A 1,220-test Selenium WebDriver suite (Python/pytest) exercising the Flask
demo application in `src/demo/`. Built around a Page Object Model, data
factories, parallel execution, and HTML/JUnit reporting.

## Layout

```
src/demo/            Flask application under test (auth, messaging, navigation)
src/qa/              Shared QA helpers (config, driver factory)
tests/
  conftest.py        Fixtures: WebDriver reuse, live server, reporting hooks
  pages/             Page Object Model (BasePage + one class per page)
  factories/         Deterministic test-data factory
  config/            Environment configuration loader
  test_smoke.py      110 critical-path tests
  test_*_functional  800 feature tests (auth, forms, navigation)
  test_regression.py 210 edge-case / security tests
  test_e2e_journeys  100 multi-page user journeys
docs/coverage_matrix.md   Feature → test mapping
.github/workflows/qa.yml  CI: runs each suite bucket headless on push/PR
```

## Quick start

```bash
pip install -r requirements-qa.txt
pytest                      # full suite, parallel, HTML + JUnit reports
```

Reports land in `reports/` (`report.html`, `junit.xml`, `per-test/*.json`,
`screenshots/` on failure).

## Configuration (env vars)

| Variable | Default | Meaning |
|---|---|---|
| `APP_BASE_URL` | `http://localhost:8000` | App under test |
| `APP_BROWSER` | `chromium` | `chromium`, `firefox`, or `edge` |
| `APP_HEADLESS` | `true` | Run headless |
| `APP_TIMEOUT` | `15` | Explicit wait seconds |
| `APP_IMPLICIT_WAIT` | `5` | Implicit wait seconds |
| `APP_VIEWPORT_WIDTH/HEIGHT` | `1366`/`768` | Browser window size |
| `APP_REPORT_DIR` | `reports` | Report output directory |

Credentials are read from `APP_ADMIN_USER`/`APP_ADMIN_PASS`/`APP_TEST_USER`/
`APP_TEST_PASS` — never hardcoded.

## Running subsets

```bash
pytest --qa-suite=smoke          # one bucket: smoke|functional|regression|e2e
pytest --qa-bucket=login         # one feature bucket
pytest tests/test_smoke.py -k home   # file + keyword filter
pytest -n 4                      # control parallelism (default: -n auto)
```

## Debugging

- **See the browser:** `APP_HEADLESS=false pytest tests/test_smoke.py -k title -n 0`
- **Screenshots on failure** are written to `reports/screenshots/` automatically.
- **Per-test JSON** in `reports/per-test/` includes outcome, duration, and traceback.
- **Stability runs:** `python run_stability.py 5` runs the suite 5× and records
  results to `reports/stability_runs.json`.

## Extending the suite

1. **New page:** add a class in `tests/pages/` subclassing `BasePage`, register
   it with `@register("/route", "alias")`, and register it in the
   `page_factory` fixture in `conftest.py`.
2. **New test:** use the `driver` and `live_server` fixtures; locate elements
   via `data-testid` (`[data-testid='...']`). Add the matching marker
   (`smoke`/`functional`/`regression`/`e2e`).
3. **New test data:** use the `data_factory` fixture (`user()`, `product()`,
   `order()`, `payment()`).

The `driver` fixture reuses one browser per parallel worker and resets cookies
+ alerts between tests, so tests stay isolated without paying driver-startup
cost per test.

## Code quality

```bash
ruff check tests src     # lint
black tests src          # format
python validate_project.py   # acceptance-criteria gate
```

## CI

`.github/workflows/qa.yml` runs each suite bucket headless on every push/PR
to `master`/`main` and uploads `reports/` as artifacts.
