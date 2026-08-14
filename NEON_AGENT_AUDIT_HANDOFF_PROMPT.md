Neon Agent Audit Handoff Prompt

You are taking over a deep audit and hardening task for:

C:\god_ai\neon_architect_v5_perf.py

The user wants a thorough audit of the Neon agent, specifically checking whether it is suitable for project execution and fixing all issues across:

NVIDIA NIM
OmniRoute
OpenRouter
Provider/model discovery
Provider pooling and account rotation
Streaming and non-streaming execution
Retry and cooldown behavior
Rate-limit handling
Performance and concurrency
Generation stages
Tool execution
Testing and validation
Preview server behavior
Deployment behavior
Persistence and state writes
Security and credential handling
Fallback behavior
Overall suitability as the project’s execution agent
Environment
Operating system: Windows
Target file: C:\god_ai\neon_architect_v5_perf.py
Main workspace: D:\ideation_to_prototype
Related project: D:\ideation_to_prototype\idea-terminal-engine
The target script is very large and monolithic, approximately 14,000+ lines.
Do not reset or discard unrelated changes in C:\god_ai. It is a dirty repository with many unrelated modifications.
Only modify the target script unless a missing dependency or required project file is explicitly confirmed.
Use apply_patch for source edits.
Do not perform destructive Git or filesystem operations.
Do not make real provider, deployment, GitHub, or production calls during testing unless explicitly authorized.
Current audit status

The target script has already been statically inspected and several fixes have already been applied. Do not blindly redo them. First inspect the current file and verify the changes.

Changes already applied
1. Dependency guard for NIM verification

The NIM verification path now refuses to run if httpx is unavailable instead of proceeding into an invalid execution path.

Verify that the guard is still present and that optional dependency failures produce clear messages.

2. Atomic JSON persistence

A helper named _atomic_json_dump was added. It uses a unique temporary file created with tempfile.mkstemp, flushes and fsyncs the file, and replaces the target atomically.

The following persistence paths were updated to use it:

model-dead state
project API-key state
configuration
session state
project state

Verify that all relevant JSON writes use the helper and that no predictable shared .tmp files remain.

3. Correct failed-request accounting

Provider.record_failure now commits the reserved token to the provider’s rate-limit bucket. Previously, failed, timed-out, and rate-limited requests were not counted consistently, allowing repeated retries to exceed the intended RPM accounting.

Verify that:

Successful calls commit correctly.
Failed calls commit correctly.
429 responses are counted.
Timeouts and generic provider failures are counted.
A failure is not double-counted when no token was reserved.
4. Specialized generation path hardening

SpecializedAgent._call_nim was substantially revised.

It now:

Refuses to emit placeholder source if the OpenAI client package is missing.
Calls pool.begin_logical_turn().
Uses configurable generation retry settings.
Uses provider-pool availability and shortest wait information.
Adds thinking-related extra_body / chat_template_kwargs.
Checks for missing clients.
Checks for empty choices.
Checks for empty content.
Retries malformed or empty responses.
Handles 404 and 410 as permanent model failures.
Handles 429 responses with cooldown and shared-account propagation.
Records provider failures.
Raises a clear error after retry exhaustion.

A semantic failure branch was added so an empty response does not permanently starve a single-account deployment for the entire logical turn.

Verify this path with:

One provider.
Multiple providers.
Multiple credentials for the same provider.
Different providers with different credentials.
A provider returning empty choices.
A provider returning empty content.
A provider raising a 429.
A provider raising a 404.
A provider raising a timeout.
All providers being unavailable.
5. Streaming lifecycle hardening

The main streaming consumer _consume_stream was updated to avoid a queue deadlock and thread leak.

It now has a stop event and bounded queue behavior intended to prevent the reader thread from blocking forever when the consumer times out or stops consuming.

Verify carefully that:

The reader thread exits after a timeout.
The queue cannot block forever while shutting down.
The sentinel is delivered during normal completion.
The response is closed.
A truly stuck provider thread is tracked as an orphan.
Repeated timeouts do not create unbounded orphan threads.
The reader thread does not mutate shared payload state after the caller has moved on.
Error payload dumps do not contain credentials or authorization headers.
6. Provider-pool exhaustion behavior

ProviderPool.current() no longer silently returns a permanently disabled provider when all providers are unavailable. It should raise an explicit error instead.

Verify that every caller handles this correctly and that an unavailable pool produces a useful user-facing error rather than an unrelated index, key, or client error.

7. Warm-up probing

The free-chat/model warm-up probe was changed from serial probing to concurrent probing with one overall deadline.

Verify that:

All candidate probes can start concurrently.
Total warm-up time is bounded by the configured deadline.
Threads are joined or tracked appropriately.
A slow provider cannot block every other provider.
Rate-limit accounting is correct during warm-up.
Failed probes do not corrupt provider availability state.
8. Local preview binding

The FastAPI preview server was changed from binding to 0.0.0.0 to binding to 127.0.0.1.

Verify that other preview paths do not accidentally expose local development servers on all interfaces.

9. GitHub deployment security

The GitHub deployment path was changed to avoid embedding the GitHub token directly in the Git push URL.

It now attempts to use a temporary askpass script and environment variables for credentials. It also no longer uses --force.

Verify the implementation carefully because this area had an indentation and control-flow defect during editing.

Required checks:

Every Git step is checked immediately.
git add failure stops execution.
Commit failure is handled only as a permitted “nothing to commit” case.
Branch rename failure stops execution.
Push failure stops execution.
The token is not present in process argv.
The token is not written to .git/config.
The temporary askpass directory is removed after completion.
The token is not printed in errors.
Force-push is not used.
The repository path is correctly constrained.
No arbitrary repository or working directory can be selected through unvalidated input.

Update stale comments if they still refer to embedding a token in the URL.

10. V5 generation loader

The V5 generation loader was changed to:

Prefer an explicitly configured NEON_GENERATION_CORE path.
Otherwise load generation_core.py beside the agent script.
Use importlib.util.spec_from_file_location.
Avoid importing an arbitrary generation_core module from the caller’s current working directory.
Record _V5_CORE_IMPORT_ERROR.
Set _HAS_V5_CORE accurately.

Verify the loader carefully and preserve the safer import behavior.

Important current finding: V5 core candidate FOUND locally

A local machine search was performed specifically for generation_core.py.

The exact result found was:

C:\Users\Admin\Downloads\neon_unified\generation_core.py
Size: 63,480 bytes
LastWriteTime: 8/6/2026 03:06:37 AM

This is currently the strongest identified candidate for the missing V5 core.

The target Neon file explicitly expects the active V5 generation layer to come from generation_core.py and imports:

GenerationOrchestratorV5
detect_stack
SUPPORTED_STACKS

The loader supports two intended resolution mechanisms:

NEON_GENERATION_CORE
generation_core.py beside the target agent script

The target file also records a failure message:

generation_core.py is not present beside the agent

when the core cannot be loaded.

Required V5-core investigation

Do NOT blindly copy the candidate or silently enable it.

First inspect:

C:\Users\Admin\Downloads\neon_unified\generation_core.py

Then verify:

It defines/exported GenerationOrchestratorV5.
It defines/exports detect_stack.
It defines/exports SUPPORTED_STACKS.
It imports successfully in the current Python environment.
Its imports/dependencies are available.
Its APIs are actually compatible with the target neon_architect_v5_perf.py.
It does not belong to an unrelated Neon branch/version.
It is not merely a backup or stale experimental implementation.
Its version/date/content aligns with the target script's v5 expectations.
It does not introduce a security or path-loading regression.

Perform a direct isolated import test against the exact file:

@'
from pathlib import Path
import importlib.util


p = Path(r"C:\Users\Admin\Downloads\neon_unified\generation_core.py")
spec = importlib.util.spec_from_file_location("generation_core_candidate", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


print("IMPORT=OK")
print("GenerationOrchestratorV5=", hasattr(m, "GenerationOrchestratorV5"))
print("detect_stack=", hasattr(m, "detect_stack"))
print("SUPPORTED_STACKS=", hasattr(m, "SUPPORTED_STACKS"))
print("STACKS=", getattr(m, "SUPPORTED_STACKS", None))
'@ | python -

Then perform a compatibility-oriented inspection of:

constructor signatures
generate(...)
detect_stack(...)
stack identifiers
configuration expectations
preview/QA callbacks
persistence expectations
referenced helper modules
Decision rule for the V5 core

Based on the investigation, make exactly one evidence-backed decision:

Option A — Restore/use the discovered V5 core

If the candidate is confirmed to be the correct compatible V5 core:

use the existing safer NEON_GENERATION_CORE mechanism;
prefer an explicit configured path over implicit module discovery;
document the chosen path;
do not copy the file into arbitrary locations unless necessary;
verify the integrated Neon import path;
verify GenerationOrchestratorV5 execution with an offline/minimal smoke test;
preserve the ability to report the exact core path/version.
Option B — Reject the candidate

If the candidate is stale, incompatible, unrelated, incomplete, or unsafe:

do not use it;
explain exactly why;
keep _HAS_V5_CORE false;
explicitly identify the remaining V5-core blocker.
Option C — Restore beside the agent

If the candidate is confirmed correct but the project architecture requires the core beside the agent:

copy only after verification;
document the source path and checksum;
preserve the safer explicit import logic;
perform a post-copy import test.

Do NOT silently select a random backup, lasthelp copy, or historical Neon artifact.

Additional investigation already performed

Searches found many other Neon files referring to generation_core.py, including older/alternate architectural versions. Do not assume those are interchangeable.

The target agent itself is explicit that its active V5 orchestrator is GenerationOrchestratorV5 from generation_core.py.

Therefore the audit must now resolve whether the discovered neon_unified\generation_core.py is the intended production companion rather than continuing to treat the core as simply “missing.”

Architecture findings

The script contains two materially different generation and execution systems.

Main conversational streaming path

This path uses:

ProviderPool
streaming _parse_stream
_consume_stream
tool calls
account-aware provider selection
logical-turn exclusions
stream retries
Legacy or specialized generation path

This path uses:

SpecializedAgent
_call_nim
non-streaming OpenAI-compatible requests
planner, architect, frontend, backend, database, and test agents
direct generated-file results

These paths must not drift apart in:

provider selection
retries
model failure classification
rate-limit handling
account cooldown behavior
thinking flags
empty-response handling
timeout handling
telemetry and logging

Audit both paths independently and then compare them.

Provider endpoints

Current provider endpoints include:

NVIDIA NIM: https://integrate.api.nvidia.com/v1
OmniRoute: defaults to http://localhost:20128/v1
OpenRouter: https://openrouter.ai/api/v1

Provider discovery behavior:

NIM accounts can come from configured API keys and environment variables.
OmniRoute can use an environment key or a local dummy/default credential.
OpenRouter is enabled when its key is configured.
The pool dynamically discovers models from /models and probes candidates.

Verify that:

/models failure does not crash the entire application unnecessarily.
Empty model lists are handled clearly.
Model IDs are normalized consistently.
Provider names and model IDs do not collide.
Account identity is based on stable (base_url, api_key) semantics.
Credentials are never logged.
Duplicate providers are deduplicated correctly.
A model disabled for one credential is not incorrectly disabled for every credential unless intended.
Permanent model failure is persisted safely.
Rate limits are shared at the correct scope.
OmniRoute’s local endpoint is not treated as a public remote provider accidentally.
OpenRouter’s model naming and provider-specific payload extras are compatible.
NIM thinking parameters are not sent to providers that do not support them.
Unknown provider-specific request fields are filtered or isolated appropriately.
Performance audit

Check for:

Serial requests that should be concurrent.
Repeated /models discovery without caching.
Repeated construction of OpenAI or httpx clients.
Excessive sleeps in retry loops.
Retry storms after 429 responses.
Retry storms when all providers are down.
Queue backpressure deadlocks.
Thread leaks.
Unbounded orphan tracking.
File writes on every token or retry.
Excessive terminal or UI rendering during streaming.
Deep-copying very large payloads unnecessarily.
Provider fairness under multiple accounts.
Account starvation caused by logical-turn exclusions.
Model warm-up blocking startup.
Generation agents running sequentially when they could safely run concurrently.
Test execution timeouts and process cleanup.
Security audit

Search the script for:

Bearer
api_key
token
Authorization
clone_url
git push
--force
subprocess
shell=True
0.0.0.0
eval(
exec(
temporary files
JSON dumps of payloads
exception text containing headers or tokens

Check specifically for:

Credentials in logs.
Credentials in exception messages.
Credentials in process argv.
Credentials in URLs.
Credentials persisted without appropriate permissions.
Arbitrary command execution through tool arguments.
Path traversal in project file operations.
Unsafe Git operations.
Public network binding.
Untrusted module imports.
Generated code being executed without containment.
Required tests
1. Syntax and compilation

Run:

@'
from pathlib import Path
import ast


p = Path(r"C:\god_ai\neon_architect_v5_perf.py")
source = p.read_text(encoding="utf-8")
ast.parse(source, filename=str(p))
compile(source, str(p), "exec")
print("syntax=OK", "lines=", len(source.splitlines()))
'@ | python -
2. Import test

Use a loader that registers the module in sys.modules before execution because the script uses dataclasses and module-level metadata:

@'
from pathlib import Path
import importlib.util
import sys


path = Path(r"C:\god_ai\neon_architect_v5_perf.py")
spec = importlib.util.spec_from_file_location("neon_audit_target", path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


print("import=OK")
print("HAS_V5_CORE=", module._HAS_V5_CORE)
print("V5_ERROR=", module._V5_CORE_IMPORT_ERROR)
print("HAS_HTTPX=", module.HAS_HTTPX)
print("HAS_OPENAI=", module.HAS_OPENAI)
print("HAS_RICH=", module.HAS_RICH)
'@ | python -
3. V5 core candidate import test

Run the exact isolated import against:

C:\Users\Admin\Downloads\neon_unified\generation_core.py

Then report:

import result
required symbols
stack list
version/identity clues
dependency errors
compatibility concerns

Do not substitute a different generation_core.py.

4. Offline provider success test

Construct a Provider with a fake client and verify _call_nim returns valid content exactly once.

5. Offline empty-response test

Fake:

empty choices
empty content

Verify retries happen and placeholder source is never returned.

6. Offline 429 test

Fake a response exception with status 429 and retry headers. Verify:

cooldown is applied
shared account cooldown is propagated
the provider is not immediately hammered again
a second provider can be selected
7. Offline permanent model failure test

Fake 404 or 410 and verify:

provider is marked permanently disabled
model-dead state is persisted safely if project state is configured
another account or provider can be selected
8. Streaming test

Use a fake streaming response that:

yields normal chunks
yields a finish reason
raises an exception
blocks indefinitely

Verify normal completion, error propagation, timeout behavior, response closing, queue shutdown, and orphan tracking.

9. Provider exhaustion test

Mark every provider unavailable or permanently disabled and verify a clear RuntimeError or user-facing error.

10. Persistence test

Use a temporary directory and verify:

target JSON is valid
no predictable shared .tmp remains
interrupted writes do not leave a corrupt target
file permissions are reasonable on Windows-compatible code paths
11. Tool and path safety test

Test:

project-relative valid paths
.. traversal
absolute paths outside the project
shell metacharacters
destructive Git arguments
force-push attempts
deployment provider selection
12. Static security scan

Run:

rg -n "shell=True|0\.0\.0\.0|--force|Bearer |Authorization|api_key|clone_url|git push|eval\(|exec\(" C:\god_ai\neon_architect_v5_perf.py

Review every result manually. Do not treat a clean grep as sufficient.

13. Optional linting

Check whether ruff, pyflakes, or mypy are installed. Do not install packages solely for this audit unless explicitly authorized. If unavailable, report that limitation.

Final assessment

Give a direct answer to:

Is this Neon agent the right fit for handling this project?

Use this decision framework:

If the discovered V5 core is verified as compatible and successfully integrated, reassess the agent as a true V5 project orchestrator rather than assuming the legacy path is the only active backend.
If the discovered V5 core is invalid or incompatible, state that explicitly and retain the legacy-path limitation.
If the V5 core is valid but not yet integrated, state that the agent is architecturally capable but not yet fully operational as the intended V5 orchestrator.
Explain whether it should be:
the canonical project orchestrator,
a provider-routing and generation assistant,
a temporary bridge,
or rejected until the generation core is restored.

Do not declare production readiness based solely on static import success. The provider/pool, generation, persistence, streaming, and real integration tests still determine suitability.

Final response requirements
Start with the direct verdict.
State what was changed.
State what was verified.
State the V5 core investigation result.

Explicitly mention the discovered candidate:

C:\Users\Admin\Downloads\neon_unified\generation_core.py

State whether that candidate was:
verified compatible and integrated,
found but rejected,
or found but still awaiting integration.
State remaining blockers.
Identify anything that could not be tested without real API credentials or live services.
Include the exact target path: C:\god_ai\neon_architect_v5_perf.py.
Include approximate line references from the final file for major changes.
Clearly distinguish:
fixed
verified
not verified
still blocked
Do not claim all execution paths are production-ready unless live NIM, OmniRoute, and OpenRouter integration tests have actually been run.

The most important instruction is:

Inspect the current file first, preserve the fixes already made, investigate and verify the discovered generation_core.py candidate, and finish with a concrete verdict rather than extending the audit indefinitely.