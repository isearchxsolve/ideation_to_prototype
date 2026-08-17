# Test Evidence: Production-Readiness Claims

Every production-readiness claim in this project is grounded in the 1,220-case
Selenium QA suite. This document maps each claim to the concrete test evidence
that proves it, with the exact artifact and numbers.

**Evidence source (latest run):**

| Artifact | Value |
|---|---|
| `reports/junit.xml` | `tests=1220, failures=0, errors=0, skipped=0` |
| Run timestamp | `2026-08-17T03:00:32` |
| `reports/per-test/*.json` | 1,220 records, all `outcome: "passed"` |
| `reports/report.html` | self-contained HTML report, 1,220 green |
| `reports/stability_runs.json` | last-5 window all `exit_code: 0` |

---

## Claim 1 — The suite is complete and green

**Claim:** The product ships with a full, passing regression suite.

**Proof (junit.xml, latest run):**

```
tests=1220  failures=0  errors=0  skipped=0  time=1664.7s
```

**Proof (per-test JSON, 1,220 files):**

```
outcomes: {'passed': 1220}
```

Every one of the 1,220 collected tests has a per-test JSON record with
`outcome: "passed"`. Zero failures, zero errors, zero skips.

---

## Claim 2 — Coverage spans all four suite buckets

**Claim:** Smoke, functional, regression, and e2e coverage all exist and pass.

**Proof (pytest marker collection):**

| Marker | Collected | Passed |
|---|---|---|
| `smoke` | 110 | 110 |
| `functional` | 800 | 800 |
| `regression` | 210 | 210 |
| `e2e` | 100 | 100 |
| **Total** | **1220** | **1220** |

**Proof (by source file):**

| File | Tests | Passed |
|---|---|---|
| `test_smoke.py` | 110 | 110 |
| `test_auth_functional.py` | 240 | 240 |
| `test_forms_functional.py` | 240 | 240 |
| `test_navigation_functional.py` | 320 | 320 |
| `test_regression.py` | 210 | 210 |
| `test_e2e_journeys.py` | 100 | 100 |

---

## Claim 3 — The suite is stable, not flaky

**Claim:** The suite passes repeatedly under parallel load — a prerequisite for
trusting it as a release gate.

**Proof (`reports/stability_runs.json`, last-5 window):**

```
run 1  exit=0  3032.1s  1220 passed
run 2  exit=0  1848.5s  1220 passed
run 3  exit=0  1663.3s  1220 passed
run 4  exit=0  1770.7s  1220 passed
run 5  exit=0  1672.8s  1220 passed
last-5 all clean: True
```

Five consecutive full-suite runs, each 1,220/1,220 green, each exit code 0.
This is acceptance criterion #6 in `validate_project.py`, now satisfied.

**Why this matters:** earlier runs in the same file show `exit=1` with
`1040 errors` — a browser session dying mid-run and cascading. Those failures
drove the self-healing driver fix (Claim 6). The last-5 clean window is the
post-fix evidence.

---

## Claim 4 — Security-sensitive behavior is verified in a real browser

**Claim:** The app resists the common injection/XSS classes, verified through
actual browser interaction (not just unit mocks).

**Proof (30 security regression tests, all passed):**

| Test family | Cases | Passed |
|---|---|---|
| `test_login_sql_injection_browser` | 10 | 10 |
| `test_signup_xss_name_browser` | 10 | 10 |
| `test_message_xss_browser` | 10 | 10 |
| **Total** | **30** | **30** |

These drive real payloads through the live Flask app via Selenium and assert
the malicious input is neutralized (escaped / rejected), proving the XSS fix
called out in the CHANGELOG.

---

## Claim 5 — The previously-flaky e2e journey is fixed

**Claim:** `test_signup_login_post_message_journey_browser` no longer flakes.

**Proof (per-test record for the exact case that failed):**

```json
{
  "nodeid": "tests/test_e2e_journeys.py::test_signup_login_post_message_journey_browser[10]",
  "outcome": "passed",
  "duration_s": 7.4771,
  "longrepr": null,
  "screenshot": null
}
```

This is parameter `[10]` — the specific instance that produced the
`NoSuchElementException` in the earlier failing run. It now passes with no
traceback and no failure screenshot. All 20 parameters of this test pass in the
latest run, and the whole e2e bucket is 100/100.

---

## Claim 6 — The harness survives a crashed browser (self-healing)

**Claim:** A dead WebDriver session no longer cascades into hundreds of errors.

**Proof (before vs. after, from `stability_runs.json`):**

| Run | Result | Evidence |
|---|---|---|
| Before fix | `exit=1` | `161 passed, 1059 errors` — `InvalidSessionIdException` cascade |
| After fix | `exit=0` ×5 | `1220 passed` each, no cascade |

The before-run shows a single dead session taking down ~1,040 tests. After the
`_DriverHolder` self-healing wrapper + Chromium memory-reduction flags, five
consecutive runs complete 1,220/1,220 with no cascade.

---

## Claim 7 — The suite is fast enough to be a practical gate

**Claim:** Full-suite runtime is within the <60 min NFR.

**Proof (per-test durations, 1,220 tests):**

```
min 0.088s   median 1.031s   max 11.336s   avg 1.866s
full suite wall-clock: ~27–50 min across 4 parallel workers
```

All five stability runs completed well under the 60-minute budget.

---

## How to reproduce this evidence

```bash
# Full suite (parallel, HTML + JUnit + per-test reports)
pytest

# Re-record stability evidence (5 consecutive runs)
python run_stability.py 5

# Acceptance gate (reads the evidence above)
python validate_project.py
```

Reports land in `reports/`:
- `junit.xml` — machine-readable pass/fail per test
- `report.html` — self-contained visual report
- `per-test/*.json` — one record per test (outcome, duration, traceback)
- `screenshots/` — captured on failure
- `stability_runs.json` — per-run exit codes and summaries

---

## Summary

| Claim | Evidence | Status |
|---|---|---|
| Suite complete & green | 1220/1220 passed, 0 fail/error/skip | ✅ |
| All 4 buckets covered | smoke 110, functional 800, regression 210, e2e 100 | ✅ |
| Stable under load | 5 consecutive clean runs | ✅ |
| Security verified in browser | 30/30 SQLi+XSS tests pass | ✅ |
| Flaky e2e fixed | `[10]` now passes, e2e 100/100 | ✅ |
| Self-healing harness | no cascade across 5 runs | ✅ |
| Fast enough | median 1.0s/test, <60 min full suite | ✅ |

All claims are backed by artifacts in `reports/` from the run timestamped
`2026-08-17T03:00:32`, and by the 5-run stability window ending
`2026-08-16T21:30:26 → +27m`.
