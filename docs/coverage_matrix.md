# Coverage Matrix

Maps application features to the test cases that cover them. Suite totals:
**1,220 tests** — smoke 110, functional 800, regression 210, e2e 100.

Target application: `src/demo/app.py` (Flask demo app with auth, messaging,
and navigation). All UI tests run against a live server via real Selenium
WebDriver; locators use `data-testid` attributes.

## Feature → Test mapping

| Feature | Routes | Test file(s) | Key test functions | Count |
|---|---|---|---|---|
| Home page rendering | `/` | test_smoke.py, test_navigation_functional.py | `test_home_page_element_present`, `test_home_page_title`, `test_page_loads_in_browser` | ~140 |
| Navigation bar & links | all pages | test_smoke.py, test_navigation_functional.py | `test_navigation_bar_present`, `test_nav_link_clickable`, `test_nav_link_navigates`, `test_nav_bar_present_on_all_pages_browser` | ~150 |
| Login (success/failure) | `/login` | test_auth_functional.py, test_smoke.py | `test_login_success_browser`, `test_login_form_field_count_browser`, `test_login_page_form_visible` | ~100 |
| Signup (validation, success) | `/signup` | test_auth_functional.py, test_forms_functional.py | `test_signup_success_browser`, `test_signup_form_renders_correctly_browser`, `test_signup_form_field_count_browser` | ~130 |
| Dashboard (auth-gated) | `/dashboard` | test_navigation_functional.py, test_regression.py | `test_dashboard_redirect_browser`, `test_dashboard_without_login_browser` | ~20 |
| Logout | `/logout` | test_regression.py, test_e2e_journeys.py | `test_logout_without_login_browser`, `test_full_signup_login_logout_journey_browser` | ~30 |
| Message board | `/messages` | test_forms_functional.py, test_regression.py, test_e2e_journeys.py | `test_message_accumulation_browser`, `test_message_board_interaction_journey_browser`, `test_messages_page_accessible_browser` | ~70 |
| About page | `/about` | test_navigation_functional.py | `test_page_loads_in_browser`, `test_direct_url_access_browser` | ~20 |
| 404 handling | any unknown | test_smoke.py, test_regression.py | `test_404_page_displayed`, `test_404_page_displayed_browser` | ~30 |
| Health/status APIs | `/health`, `/api/status` | test_smoke.py | `test_health_endpoint_json` | 10 |
| Form rendering & fields | `/login`, `/signup` | test_forms_functional.py | `test_login_form_renders_correctly_browser`, `test_signup_form_renders_correctly_browser` | ~50 |
| E2E user journeys | multi-page | test_e2e_journeys.py | `test_full_signup_login_logout_journey_browser`, `test_signup_login_post_message_journey_browser`, `test_failed_login_retry_journey_browser`, `test_navigation_browse_journey_browser` | 100 |

## Security & robustness coverage (regression suite)

| Threat / edge case | Test function |
|---|---|
| XSS in message board | `test_message_xss_browser` |
| XSS in signup name | `test_signup_xss_name_browser` |
| SQL injection in login | `test_login_sql_injection_browser` |
| Unicode password handling | `test_login_unicode_password_browser` |
| Oversized email input | `test_signup_long_email_browser` |
| Duplicate/unique user creation | `test_multiple_signup_unique_users_browser` |
| Rapid page switching / load stress | `test_rapid_page_switches_browser`, `test_rapid_home_loads_browser` |
| Unauthenticated access paths | `test_dashboard_without_login_browser`, `test_logout_without_login_browser` |

## Suite buckets (pytest markers)

| Marker | Purpose | Count |
|---|---|---|
| `smoke` | Critical-path validation | 110 |
| `functional` | Feature-by-feature coverage | 800 |
| `regression` | Historical bug repro + edge cases | 210 |
| `e2e` | Full user journey flows | 100 |

Run a single bucket: `pytest --qa-suite=smoke` (or `functional`,
`regression`, `e2e`).

## Not covered (known gaps)

- Cross-browser matrix (Firefox, Edge) is supported by the framework
  (`APP_BROWSER` env var) but CI currently runs Chromium only.
- No performance/load testing beyond rapid-load regression cases.
- API contract tests are limited to `/health` and `/api/status` smoke checks.
