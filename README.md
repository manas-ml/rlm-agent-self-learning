# rlm-agent-self-learning

Notes and experiments for evaluating [Prime Agent](https://github.com/PrimeIntellect-ai/prime-agent), an open-source RLM coding agent.

The three claims under test (from the Prime Agent README):

1. Subagent fan-out via `rlm.spawn(...)` can fix many failing tests in parallel.
2. `/autonomous` with a user-defined quality gate stops only when work is verifiably done.
3. `/refine` can make a second run cheaper than the first, and recorded snapshots allow rollback (`/refine rollback <id>`).

## PoC kit

The evaluation kit (two buggy Python fixtures, a quality gate and its self-test, a metrics script, a runbook and a report template) was removed from the working tree. It is still in git history:

```bash
git show 7a8a47c --stat           # list the files
git checkout 7a8a47c -- poc       # restore poc/
bash poc/setup_fixtures.sh        # recreate each fixture's own git repo
```

Start with `poc/RUNBOOK.md`. It has not been run against a real `prime-agent` install, and it lists the commands it could not verify.
