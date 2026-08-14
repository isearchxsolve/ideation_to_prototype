# Architecture: Selenium QA Automation (1000 Test Cases)

## Components

### 1. Test Runner Layer
- **pytest** orchestrates execution with `pytest-xdist` for parallelism (4-8 workers).
- **pytest-html** generates HTML reports; JUnit XML emitted for CI consumption.
- **pytest-rerunfailures** provides automatic retry on transient failures (max 2 reruns).

### 2. WebDriver Management Layer
- **webdriver-manager** auto-provisions Chromium, Firefox, and Edge drivers.
- **selenium** WebDriver instances created per-worker via session-scoped fixtures.
- Headless mode enforced for CI; local debug mode optional via env var.

### 3. Page Object Model (POM) Layer
- **BasePage**: abstract base with common actions (click, type, wait, screenshot).
- **PageFactory**: registry mapping route paths to page objects.
- **Component Objects**: reusable UI fragments (header, footer, form fields).
- All locators use `data-testid` attributes; CSS selectors as fallback.

### 4. Test Data Layer
- **DataLoader**: reads JSON/CSV/YAML fixtures from `tests/data/`.
- **TestDataFactory**: generates unique seed data per run to avoid collisions.
- **EnvironmentConfig**: loads env vars for URLs, credentials, browser targets.

### 5. Test Case Layer
- **Smoke tests**: critical-path validation (100 cases).
- **Functional tests**: feature-by-feature coverage (600 cases).
- **Regression tests**: historical bug repro + edge cases (200 cases).
- **E2E tests**: full user journey flows (100 cases).
- All tests use POM + data-driven parameterization.

### 6. Reporting & Observability Layer
- **Screenshot on failure**: captured automatically via pytest hooks.
- **Logs**: per-test log files in `reports/logs/`.
- **Coverage matrix**: `docs/coverage_matrix.md` maps features to test IDs.

### 7. CI/CD Layer
- **GitHub Actions**: `.github/workflows/ci.yml` runs full suite headless on push/PR.
- **Sharded jobs**: suite split across matrix jobs for parallel CI execution.
- **Artifact upload**: HTML reports + screenshots uploaded as CI artifacts.

## Data Flow

```
[CI Trigger / Local CLI]
        |
        v
[pytest-xdist workers] -- spawns N parallel processes
        |
        v
[WebDriver Manager] -- provisions browser drivers
        |
        v
[EnvironmentConfig] -- loads env vars (URL, browser, credentials)
        |
        v
[TestDataFactory / DataLoader] -- generates unique test data
        |
        v
[Page Objects] -- interact with browser via Selenium WebDriver
        |
        v
[Assertions] -- validate expected vs actual state
        |
        v
[pytest hooks] -- capture screenshots, logs on pass/fail
        |
        v
[pytest-html + JUnit XML] -- write reports to reports/
        |
        v
[CI Artifact Upload] -- publish reports for review
```

### Key Interfaces (Stubs)

#### BasePage (interface stub)
```python
class BasePage:
    def __init__(self, driver: WebDriver, wait: WebDriverWait): ...
    def click(self, locator: tuple) -> None: ...
    def type(self, locator: tuple, text: str) -> None: ...
    def wait_for_element(self, locator: tuple, timeout: int = 10) -> WebElement: ...
    def take_screenshot(self, name: str) -> str: ...
    def is_element_visible(self, locator: tuple) -> bool: ...
```

#### EnvironmentConfig (interface stub)
```python
class EnvironmentConfig:
    @property
    def base_url(self) -> str: ...
    @property
    def browser(self) -> str: ...
    @property
    def credentials(self) -> dict: ...
    @property
    def headless(self) -> bool: ...
```

#### DataLoader (interface stub)
```python
class DataLoader:
    def load_json(self, path: str) -> list: ...
    def load_csv(self, path: str) -> list: ...
    def load_yaml(self, path: str) -> dict: ...
```
