# Prime Agent PoC report

Date: ____  Agent version (`prime-agent --version`): ____  Model/provider: ____  Env (VM/container): ____
Repeats per run: ____ (recommend 3; report median and range if >1)

## Success criteria
- [ ] Run 2 passes the gate with fewer turns OR fewer tokens than run 1
- [ ] Run 3 (rolled back) regresses toward run 1 numbers (not toward run 2)
- [ ] Diffs are reviewable (read in full; no unexplained changes)
- [ ] No test files were touched (gate check 2 passed in every run)
- [ ] `gate.sh` unmodified (checksum before == after)

## Results (from `results.csv`)
| Run | Fixture | Gate passed | Turns | Tokens | Duration (s) | Subagents | Lines changed |
|-----|---------|-------------|-------|--------|--------------|-----------|---------------|
| 1 (baseline, no refine) | fixture-a | | | | | | |
| 2 (after /refine --global) | fixture-b | | | | | | |
| 3 (refine rolled back) | fixture-b | | | | | | |

How each number was obtained (TUI / `sessions --json` / `--log` parse / flag): ____
Did tokens include child sessions? ____ (UNVERIFIED in the runbook)

## Claim checks
1. **Fan-out**: subagents spawned ____ of 8. Parallel (overlapping in time)? ____ Wall-clock vs a sequential estimate: ____
2. **Autonomous + gate**: run ended because  [ ] gate passed  [ ] turn limit  [ ] token limit  [ ] timeout  [ ] other. A limit stop is not a success. Gate attempts used: ____
3. **/refine + rollback**: see Qualitative below.

## Qualitative checklist
- [ ] Did subagents collide on shared files (two children editing the same file, overwritten edits, a merge step that reverted work)? Evidence: ____
- [ ] Did the gate or a budget limit end each run? (limit != success) Run1 ____ Run2 ____ Run3 ____
- [ ] Did detach/reattach preserve state (REPL variables, subagents still running, `/goal`, `/autonomous` budgets)? Method used to detach: ____
- [ ] Was the `/refine` output specific and evidence-backed, or generic? Quote the best and worst edit: ____  (see refine_log.md)
- [ ] Did auto-refine fire during any run (confound)? ____
- [ ] Did the agent try to edit tests, pyproject, or gate.sh (visible in transcript even if the gate caught it)? ____

## Known confounds (state which applied)
- Model nondeterminism: single runs are anecdotes. A 10-20% turn/token difference is within normal variance. Use 3 repeats.
- fixture-b may be easier or harder than fixture-a (e.g. the rounding fix in b is a one-word change; a's needs a rewrite of the expression). Check with a no-refine control: run fixture-b with a clean harness (that is run 3 only if rollback is complete; otherwise use a fresh agent dir/machine).
- Prompt caching changes token counts and cost between runs (cache reads vs writes). Report input, output and cache separately if available; the metrics script sums all four.
- Session order effects: run 2 and 3 happen later, so provider-side caching and model updates may differ.
- Budget/limit settings interact with fan-out: if children don't count toward limits, "tokens" is not comparable between a fan-out run and a serial one.

## Verdict
Claim 1: ____  Claim 2: ____  Claim 3: ____   Confidence and why: ____
UNVERIFIED items resolved during the run: ____
