# Prime Agent PoC runbook

Evidence labels used below:
- **[README]** quoted from the README at https://github.com/PrimeIntellect-ai/prime-agent (commit 2ee7e62, 2026-10-10).
- **[SRC]** read from the repo's source (`crates/pa-core/src/slash_command_args.rs`, `.../session_engine/slash_commands.rs`, `crates/pa-cli/src/{args,command_registry}.rs`, `crates/pa-core/src/autonomous/*`, `prime-agent-runtime/src/rlm/__init__.py`). Not user docs, so re-check with `/help` and `prime-agent --help` on your installed version.
- **UNVERIFIED**: not found in the README or source. Try it, then write down what happened.

> **Docs gap.** The brief named `packages/coding-agent/docs/usage.md`, `docs/rlm.md`, `docs/long-running-agents.md`, `docs/quickstart.md` and `docs/skills.md`. None exist in the current repo. `docs/` holds only `daily-stats.md`, `decision-api.md` and three `legacy-*` files, and there is no `packages/` dir. Everything below comes from the README plus source.

> **`rlm(...)` does not exist.** The runtime raises `'rlm' is not callable; spawn a child with: handle = await rlm.spawn('sub-task', name='worker')` [SRC `rlm/__init__.py:23`]. The task prompt below uses `rlm.spawn` for that reason. It is the one deliberate deviation from the brief.

## 0. Safety (read first)

The README says: "Prime Agent executes model-generated Python and project commands with your user permissions", and that worker/kernel processes are not a security sandbox [README].

- Run everything inside a disposable VM or container, or at minimum a fresh clone in a throwaway directory. Do not run it on your daily machine.
- No credentials in the environment: no cloud keys, no `GITHUB_TOKEN`, no SSH agent, no `~/.aws`. `/login` is the only credential it needs, and it needs a provider key or subscription. Use a key with a spend limit.
- Review every diff (`git -C fixture-a diff`) before trusting a run. Use only trusted repos and skills.
- The agent could edit `gate.sh` (it sits one directory above the fixture and runs with your permissions). Before each run: `chmod a-w gate.sh gate_selftest.sh` and check afterwards with `git diff -- gate.sh` from the repo root (or `sha256sum gate.sh` before and after). A passing gate means nothing if `gate.sh` itself changed.
- `prime-agent shutdown` stops every agent and background service when you finish [README].

## 1. Install and log in

```bash
curl -fsSL https://app.primeintellect.ai/prime-agent/install.sh | sh     # [README]; Windows: install.ps1 via PowerShell
cd fixture-a
prime-agent                                                              # [README]
# inside the TUI, first launch:
/login                                                                   # [README] pick a subscription or API-key provider
```
Check: `prime-agent status` and `prime-agent doctor` [README].

Prep once (outside the agent):
```bash
# (from the repo root)
bash setup_fixtures.sh       # only after a fresh clone: recreates the fixtures' git repos
bash gate_selftest.sh        # must end "SELFTEST: ALL REJECTIONS PROVEN"
chmod a-w gate.sh gate_selftest.sh
cat results.csv 2>/dev/null  # absent on a clean checkout
```

## 2. Run 1 on fixture-a

```bash
# (from the repo root)
bash setup_fixtures.sh       # only after a fresh clone: recreates the fixtures' git repos
python3 metrics.py begin run1              # records the start time
cd fixture-a && prime-agent
```
Inside the TUI, in this order:

**a. Goal** [SRC: `/goal [--budget <tokens>] <objective>`; `/goal status|pause|resume|clear` also exist]
```
/goal make the pytest suite pass without modifying anything under tests/ or pyproject.toml
```
**b. Task prompt** (paste as a normal message). The brief's wording, with `rlm(...)` replaced by the real API:
```
Eight test files fail. Use await rlm.spawn(prompt, name=...) to spawn one subagent per failing module in parallel (give each a unique name). Each subagent must diagnose the root cause, fix the source (not the tests), and report a one-line summary back with agent_message. Merge results, then run the full suite.
```
Spawn semantics [SRC `rlm/__init__.py`, `refinement/planner.rs`]: `rlm.spawn` returns a handle immediately and never returns the child's answer. Results come back through `agent_message.send(message, receiver_role="parent")` or files. `rlm.list_subagents()` recovers handles, and `rlm.collect(...)` exists (signature not read; UNVERIFIED).

**c. Autonomous mode with budgets and the gate** [SRC: usage string, verbatim]
```
/autonomous on --max-turns 15 --max-tokens 400000 --timeout-ms 1200000 --gate "bash ../gate.sh"
```
- Full flag list: `--max-continuations --max-turns --max-tokens --timeout-ms --gate <command> --gate-retries <n> --gate-timeout-ms <n> --subagent-keep-alive-ms <n>`; also `/autonomous status` and `/autonomous off`.
- A gate is a shell command run in the session cwd (the fixture dir). Exit 0 = pass. Defaults: 3 retries, 5 min timeout [SRC `autonomous/mod.rs`, `gates.rs`]. A gate is not re-run if the workspace is unchanged since its last failure.
- README: "A passed gate checks only what that gate verifies; reaching a limit does not imply task success" [README]. Record in the report whether the run ended on the gate or on a limit.
- UNVERIFIED: whether child-session tokens/turns count against the parent's `--max-tokens`/`--max-turns`; whether `/autonomous on` can be issued before the task prompt. If the run does not continue by itself, note that.

**d. Detach and reattach mid-run** (wait until subagents are visibly running)
- UNVERIFIED: the in-TUI key or command that detaches while leaving the session running. README only says sessions "keep running after the terminal disconnects". `Ctrl+Z` (suspend) is documented in the TUI hotkeys source and is not the same thing. Closing the terminal window is the README-described path. Record which action you used.
- From another terminal:
  ```bash
  prime-agent agents                 # [README] browse running, idle, saved sessions
  prime-agent sessions --json        # [SRC] status, activity, usage per agent
  prime-agent attach <agent>         # [README] reattach
  ```
- Note in the report: are the Python REPL state, subagents, goal and autonomous budgets still there (`/goal status`, `/autonomous status`)?

**e. Finish and measure**
```bash
# (from the repo root)
bash setup_fixtures.sh       # only after a fresh clone: recreates the fixtures' git repos
python3 metrics.py finish run1 fixture-a [--turns N --tokens N --subagents N]
git -C fixture-a diff --stat
git -C fixture-a diff          # review the full diff for the report
```
- Take turns and tokens from the TUI or `prime-agent sessions --json` (it carries a `usage` object: `inputTokens`, `outputTokens`, `cost` per the CLI tests; whether it covers child sessions is UNVERIFIED) and pass them as flags.
- Optional: `--log FILE` parses `turn_end` / `message_end` events from a `prime-agent --mode json` stream or session JSONL. Event names come from source only (UNVERIFIED). Cross-check once against the TUI. Where the session file lives is UNVERIFIED (`prime-agent --resume` lists sessions; `--session-dir <dir>` sets a custom one [SRC]).
- `metrics.py finish` runs `gate.sh`, appends a row to `results.csv`, and exits non-zero if the gate fails. It runs `git add -N .` in the fixture so new files show in the diff stat.

Headless alternative to steps a-c, same budgets [SRC `args.rs`]. Use it only as a second condition. The runbook flow above is the primary one.
```bash
cd fixture-a && prime-agent -p --mode json --goal "make the pytest suite pass without modifying anything under tests/ or pyproject.toml" \
  --autonomous-max-turns 15 --autonomous-max-tokens 400000 --autonomous-timeout-ms 1200000 \
  --autonomous-gate "bash ../gate.sh" "<task prompt above>" | tee ../run1.jsonl
```
(whether `-p` takes the prompt positionally is UNVERIFIED; check `prime-agent --help`.)

## 3. After run 1: `/refine`

Syntax [SRC `session_engine/slash_commands.rs`]: `/refine [--global] [instructions]` and `/refine rollback <refinement-id>` (`--global` goes before `rollback` or after the id).

**Scope matters.** Default `/refine` writes to a store local to the current session [SRC planner prompt: "The default editable continual harness store is local to the current Prime Agent session"]. A new session on fixture-b will not see it. To test transfer, use `--global`. Global entries must be "stable cross-session lessons", and project-specific lessons are allowed only if they name the project. That is a tension with the reject-fixture-a rule: if the model proposes fixture-specific global edits they get rejected, and an empty/near-empty refine is a legitimate outcome to report.

```bash
python3 metrics.py finish run1 fixture-a ...    # (if not done)
# in the same TUI session that did run 1:
/refine --global focus on reusable, repo-independent tactics for diagnosing and fixing failing unit tests via parallel subagents; do not mention specific file or project names
```
Record **every proposed change verbatim** in `refine_log.md` (template in that file): the refinement id, summary, rationale, and each edit's action/kind/title/content/reason as shown in the TUI row.
- UNVERIFIED: whether the TUI asks for approval before applying or applies immediately. The source has a "plan without mutating" function, but I did not find the UI path. If it applies immediately, rejection is at whole-refinement granularity: `/refine --global rollback <refinement-id>`. Per-edit rejection is not documented. In that case re-run `/refine --global <tighter instructions>` until the proposal passes the criteria below.
- UNVERIFIED: where history is stored. A test fixture suggests `<agent dir>/harness/refinements.jsonl`. Look there to capture verbatim JSON.

Accept/reject rules (from the brief): reject anything vague, anything mentioning fixture-a, anything that weakens the gate or tells the agent to edit tests. One-line reason per edit in `refine_log.md`.

Caveat for the whole PoC: README/source describe an **auto-refine** that can run at compaction checkpoints ("compact-trigger auto-refine", settings key `autoRefine`, structure UNVERIFIED). It writes local state by default. Check the transcript for refinement rows during every run and log them as confounds.

## 4. Run 2 on fixture-b (identical goal / prompt / budgets / gate)

```bash
python3 metrics.py begin run2
cd fixture-b && prime-agent          # NEW session so only persisted harness state carries over
```
Paste the identical `/goal`, task prompt, and `/autonomous on ... --gate "bash ../gate.sh"` line from Section 2. Then:
```bash
python3 metrics.py finish run2 fixture-b --turns N --tokens N --subagents N
```

## 5. Rollback test (run 3)

Documented mechanism: `/refine rollback <refinement-id>` [SRC]. The README says "recorded snapshots support rollback" and gives no command [README]; the command above is the only one found.
```bash
# 1. in any session: restore the pre-refine harness
/refine --global rollback <refinement-id>        # one per refinement you applied in step 3
# 2. verify it took: UNVERIFIED how. Compare the harness overview / history before and after.
# 3. reset the repo
git -C fixture-b reset --hard && git -C fixture-b clean -fdx
# 4. fresh session, same inputs
python3 metrics.py begin run3 && cd fixture-b && prime-agent
#    ... identical /goal, task prompt, /autonomous line ...
python3 metrics.py finish run3 fixture-b --turns N --tokens N --subagents N
```
If no id is available or rollback errors, mark rollback UNVERIFIED in the report and skip run 3.

## 6. Optional stretch: nightly gate re-run

Schedules [SRC `command_registry.rs`, README]:
```bash
prime-agent schedule add <agent> "0 3 * * *" -- "Run: bash ../gate.sh, then write a 5-line summary of pass/fail per check to ../nightly_summary.md"
prime-agent schedule list
prime-agent schedule cancel <job-id>
```
In-session alternatives: `/heartbeat` (user-level, syntax UNVERIFIED) or `await rlm_heartbeat.create("re-run the gate", interval="1h", label="gate")` from the REPL [SRC `skills/rlm-heartbeat`]. Note: a schedule re-enters an agent session, so the agent, not cron, runs the gate. For a deterministic nightly gate use plain `cron` + `bash gate.sh fixture-b >> nightly.log`.

## 7. Repeats and reset

Repeat each run 3 times if budget allows: `git -C fixture-X reset --hard && git -C fixture-X clean -fdx`, use distinct labels (`run1-r2`, ...), and start a fresh session each time.
