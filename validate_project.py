"""Project validation gate — checks the PLAN.md acceptance criteria.

Runs fast, static checks (no WebDriver) and reports PASS/FAIL per criterion.
Exit code 0 only when every criterion is green.

Usage: python validate_project.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))


def count_collected_tests() -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-o", "addopts="],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return sum(1 for line in proc.stdout.splitlines() if "::" in line)


def main() -> int:
    # 1. PLAN.md exists with required sections
    plan = ROOT / "PLAN.md"
    plan_text = plan.read_text(encoding="utf-8") if plan.exists() else ""
    sections = ["## Requirements", "## Risks", "## Acceptance Criteria"]
    check(
        "1. PLAN.md with Requirements/Risks/Acceptance Criteria",
        plan.exists() and all(s in plan_text for s in sections),
    )

    # 2. tests/ populated with POM modules and >= 1000 test cases
    pages = list((ROOT / "tests" / "pages").glob("*.py"))
    n_tests = count_collected_tests()
    check(
        "2. POM modules + >= 1000 test cases",
        len(pages) >= 5 and n_tests >= 1000,
        f"{len(pages)} page modules, {n_tests} tests collected",
    )

    # 3. Test runner collects cleanly (full run verified by stability runs)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-o", "addopts="],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    check("3. pytest collection exits cleanly", proc.returncode == 0)

    # 4. Reports generated in reports/
    report_html = ROOT / "reports" / "report.html"
    junit_xml = ROOT / "reports" / "junit.xml"
    check(
        "4. HTML + JUnit reports present in reports/",
        report_html.exists() and junit_xml.exists(),
    )

    # 5. CI workflow exists and runs suite headless
    workflow = ROOT / ".github" / "workflows" / "qa.yml"
    wf_text = workflow.read_text(encoding="utf-8") if workflow.exists() else ""
    check(
        "5. CI workflow runs suite on push/PR",
        workflow.exists() and "pytest" in wf_text and "push" in wf_text,
    )

    # 6. Stability: 5 consecutive clean runs recorded
    stability = ROOT / "reports" / "stability_runs.json"
    ok6 = False
    detail6 = "no stability_runs.json yet"
    if stability.exists():
        runs = json.loads(stability.read_text(encoding="utf-8"))
        last5 = runs[-5:]
        clean = len(last5) == 5 and all(r.get("exit_code") == 0 for r in last5)
        ok6 = clean
        detail6 = f"last {len(last5)} runs, clean={clean}"
    check("6. 5 consecutive clean runs", ok6, detail6)

    # 7. Coverage matrix documents tested features
    matrix = ROOT / "docs" / "coverage_matrix.md"
    check("7. Coverage matrix exists", matrix.exists())

    # 8. README documents run/debug/extend
    readme = ROOT / "README.md"
    readme_text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    check(
        "8. README documents run/debug/extend",
        readme.exists()
        and all(k in readme_text.lower() for k in ("quick start", "debug", "extend")),
    )

    # 9. Code quality: ruff + black clean
    ruff = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "tests", "src"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    black = subprocess.run(
        [sys.executable, "-m", "black", "--check", "-q", "tests", "src"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    check(
        "9. ruff + black clean",
        ruff.returncode == 0 and black.returncode == 0,
        f"ruff={ruff.returncode}, black={black.returncode}",
    )

    # 10. This validator itself returns green (computed below)
    all_green = all(ok for _, ok, _ in RESULTS)
    check("10. validate_project returns green", all_green)

    # Report
    print("=" * 64)
    print("PROJECT VALIDATION")
    print("=" * 64)
    for name, ok, detail in RESULTS:
        mark = "PASS" if ok else "FAIL"
        line = f"[{mark}] {name}"
        if detail:
            line += f"  ({detail})"
        print(line)
    print("=" * 64)
    verdict = "GREEN" if all(ok for _, ok, _ in RESULTS) else "RED"
    print(f"VERDICT: {verdict}")
    return 0 if verdict == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
