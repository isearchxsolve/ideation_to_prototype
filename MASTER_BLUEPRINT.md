# Master Implementation Blueprint

This document provides step-by-step instructions for implementing all audit findings across Levels 1 to 5 to achieve 100% test reliability and architectural compliance.

---

## Phase 1: Defect Remediation & Stack Trace Protection (Level 5)

### Step 1.1: Register Global JSON Exception Handlers in Flask App
- **Target File:** `src/demo/app.py`
- **Action:** Add global exception handlers for `Exception`, `HTTPException`, and `ValidationError`.
- **Specification:**
  ```python
  @app.errorhandler(Exception)
  def handle_unexpected_error(error):
      # Log detailed trace internally via logging, return sanitized JSON to client
      logger.error(f"Unhandled Exception: {error}", exc_info=True)
      return jsonify({
          "error": "Internal Server Error",
          "message": "An unexpected error occurred. Please contact support."
      }), 500
  ```

### Step 1.2: Protect Selenium Interactions Against Stale Elements
- **Target File:** `tests/pages/base_page.py`
- **Action:** Wrap element interaction methods (`click`, `find_visible`, `get_text`) in retry loops capturing `StaleElementReferenceException`.
- **Specification:**
  ```python
  def click(self, locator: Locator, timeout: int | None = None) -> BasePage:
      end_time = time.time() + (timeout or self.default_timeout)
      while True:
          try:
              element = self.find_visible(locator, timeout)
              element.click()
              return self
          except (StaleElementReferenceException, ElementClickInterceptedException) as e:
              if time.time() > end_time:
                  raise e
              time.sleep(0.25)
  ```

---

## Phase 2: Structural Refactoring & Deduplication (Level 4)

### Step 2.1: Consolidate Shared Test Utilities
- **Target File:** `tests/conftest.py`
- **Action:** Move repetitive helpers like `_unique_email` into shared Pytest fixtures.
- **Specification:**
  ```python
  @pytest.fixture
  def unique_email():
      def _make_email(prefix: str = "test") -> str:
          return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"
      return _make_email
  ```

### Step 2.2: Add Cache Clearing Hook for Configuration
- **Target File:** `src/demo/config.py`
- **Action:** Expose `get_settings.cache_clear()` via a Pytest autouse fixture in `tests/conftest.py` to prevent environment state pollution.

---

## Phase 3: Architectural Boundary Enforcement (Level 3)

### Step 3.1: Enforce Page Factory Abstraction
- **Target File:** `tests/pages/page_factory.py`
- **Action:** Ensure all page instantiations go through `PageFactory.get_page(route_name)` rather than direct concrete class imports in tests.

---

## Phase 4: Feature Enhancements (Level 2)

### Step 4.1: Integrate Pydantic Validation Schemas
- **Target File:** Create `src/demo/schemas.py`
- **Action:** Define Pydantic request models for all JSON routes (Auth, User Registration, Checkout).
- **Specification:**
  ```python
  from pydantic import BaseModel, EmailStr, Field

  class UserRegisterSchema(BaseModel):
      email: EmailStr
      password: str = Field(..., min_length=8)
  ```

---

## Phase 5: Business Vision & Reliability Verification (Level 1)

### Step 5.1: Execute Baseline Test Verification
- Run test suite: `pytest tests/baseline/test_architectural_baseline.py`
- Confirm 100% pass rate with zero stack trace leaks and complete element interaction resilience.
