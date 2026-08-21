"""Non-interactive Neon runner — runs autopilot in background, logs to file."""
from __future__ import annotations

import importlib.util
import os
import sys
import time

os.environ["NEON_GENERATION_CORE"] = r"C:\Users\Admin\Downloads\neon_unified\generation_core.py"
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "neon_architect_v5_perf.py"
spec = importlib.util.spec_from_file_location("neon_audit_target", TARGET)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

project = Path(__file__).resolve().parent
root_cfg = module.load_config()
cfg = module.apply_project_to_runtime(root_cfg, project)
cfg["_root"] = root_cfg
cfg["project_dir"] = str(project)

agent = module.NeonArchitect(cfg)

if not agent.goal:
    agent.goal = "Complete the SDLC: finish implementation and QA testing using Selenium with 1000 test cases for the idea-terminal-engine project"
    agent.project_state["goal"] = agent.goal
    agent._sync_project_state()

result = agent._start_autopilot(restart=False)

# Run autopilot turns until SDLC complete or max turns
MAX_TURNS = 30
for i in range(MAX_TURNS):
    sys.stdout.flush()
    prompt = agent._autopilot_prompt()
    try:
        agent.run_turn(prompt)
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"Turn error: {e}")
        import traceback
        traceback.print_exc()
        break
    if agent.sdlc_phase_idx >= len(module.SDLC_PHASES):
        print("\n*** SDLC COMPLETE ***")
        break

try:
    module.save_session(agent, also_config=True)
except Exception:
    pass
for p in agent.pool.providers:
    p.close()
print(f"\nTotal usage: {agent.meter.report()}")
print("Done.")
