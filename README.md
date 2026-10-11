# rlm-agent-self-learning

Notes and experiments for evaluating [Prime Agent](https://github.com/PrimeIntellect-ai/prime-agent), an open-source RLM coding agent.

The three claims under test (from the Prime Agent README):

1. Subagent fan-out via `rlm.spawn(...)` can fix many failing tests in parallel.
2. `/autonomous` with a user-defined quality gate stops only when work is verifiably done.
3. `/refine` can make a second run cheaper than the first, and recorded snapshots allow rollback (`/refine rollback <id>`).

## Layout

| Path | What |
|------|------|
| `RUNBOOK.md` | Copy-pasteable steps for runs 1-3; every command is labelled README / source / UNVERIFIED |
| `fixture-a/`, `fixture-b/` | Two small billing libraries, each with 8 modules and 8 deliberate bugs (8 failing test files each) |
| `gate.sh`, `gate_selftest.sh` | Quality gate (pytest passes, tests untouched, no skips, no new deps) and its proof of rejection |
| `metrics.py` | `begin` / `finish` per run; appends a row to `results.csv` |
| `REPORT_TEMPLATE.md`, `refine_log.md` | Evaluation template and `/refine` proposal log |
| `setup_fixtures.sh` | Gives each fixture its own git repo with one "initial" commit |

## Quick start

```bash
bash setup_fixtures.sh    # required after every fresh clone: nested .git dirs are not stored in this repo
bash gate_selftest.sh     # should end with "SELFTEST: ALL REJECTIONS PROVEN"
```

Then follow `RUNBOOK.md`. It has not been run against a real `prime-agent` install.
