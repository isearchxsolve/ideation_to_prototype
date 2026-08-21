# MASTER_BLUEPRINT.md: SYSTEM RECOVERY & VISION ALIGNMENT

## Executive Goal
Shift priority immediately from testing the dummy Flask demo app to making `idea-terminal-engine` and `NeonArchitect` reliably execute raw ideas to terminal `RELEASED` prototypes with zero human intervention.

---

## Phase 1: Robust Inference Gateway & Direct NIM Failover
**Target Files:**
- `D:\ideation_to_prototype\idea-terminal-engine\engine\agents\runners.py`
- `D:\ideation_to_prototype\idea-terminal-engine\config\models.json`

### Action Items:
1. Update `_call_once` in `engine/agents/runners.py` to handle gateway connection timeouts (`TimeoutError`, `socket.timeout`, HTTP 502/503/504) by transparently falling back to the `nim` provider (`https://integrate.api.nvidia.com/v1`).
2. Add automated fallback routing in `call_model` so that if OmniRoute (`http://localhost:20128/v1`) fails or times out after 10s, execution automatically routes to direct NIM API key credentials.

---

## Phase 2: V5 Generation Core Integration & Monolith Hardening
**Target Files:**
- `C:\god_ai\neon_architect_v5_perf.py`
- `C:\Users\Admin\Downloads\neon_unified\generation_core.py`

### Action Items:
1. Validate compatibility of `C:\Users\Admin\Downloads\neon_unified\generation_core.py` against `neon_architect_v5_perf.py`.
2. Configure explicit environment variable loading `NEON_GENERATION_CORE=C:\Users\Admin\Downloads\neon_unified\generation_core.py` inside the runner.
3. Fix string concatenation SQL queries at line 10483 in `neon_architect_v5_perf.py` to use parameterized statements (`?` / `%s`).

---

## Phase 3: Unblocking Idea-to-Prototype Execution Loop
**Target Files:**
- `D:\ideation_to_prototype\idea-terminal-engine\engine\orchestrator.py`
- `D:\ideation_to_prototype\idea-terminal-engine\engine\agents\prompts.py`

### Action Items:
1. Modify `BEHOLDER` payload in `engine/orchestrator.py` to pass full stdout/stderr and exit codes so evidence evaluation never fails on missing print markers.
2. Update `engine/cli.py` `selftest` command to automatically trigger mock/fallback providers when local gateway is unreachable, ensuring `selftest` runs to completion (`RELEASED`).

---

## Phase 4: Project Validation Gate Realignment
**Target File:**
- `D:\ideation_to_prototype\validate_project.py`

### Action Items:
1. Add Criterion #11 to `validate_project.py`: Check if `idea-terminal-engine` selftest has reached terminal state `RELEASED` and generated a valid GTM artifact in `clients/selftest/*/artifacts/release.json`.
2. Ensure validation fails if the core idea execution pipeline is not functional.