"""Run the full QA suite 5 consecutive times and record pass/fail per run.

Acceptance criterion #6: 5 consecutive local runs with 0 unintended failures.
Results are appended to reports/stability_runs.json.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "reports" / "stability_runs.json"
N_RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 5

records = []
if RESULTS.exists():
    records = json.loads(RESULTS.read_text(encoding="utf-8"))

for i in range(1, N_RUNS + 1):
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q", "--no-header"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    duration = round(time.time() - t0, 1)
    tail = "\n".join(proc.stdout.strip().splitlines()[-3:])
    record = {
        "run": i,
        "started_utc": started,
        "exit_code": proc.returncode,
        "duration_s": duration,
        "summary": tail,
    }
    records.append(record)
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"[run {i}/{N_RUNS}] exit={proc.returncode} in {duration}s :: {tail}")

failed = [r for r in records[-N_RUNS:] if r["exit_code"] != 0]
print(f"\nSTABILITY: {N_RUNS - len(failed)}/{N_RUNS} clean runs")
sys.exit(1 if failed else 0)
