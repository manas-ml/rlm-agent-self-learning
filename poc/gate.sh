#!/usr/bin/env bash
# Quality gate for the Prime Agent PoC. Usage: gate.sh [fixture_dir]   (default: current dir)
# Exit 0 only if all four checks pass. Prints one [PASS]/[FAIL] line per check.
# Prime Agent runs gate commands in the session cwd and treats exit 0 as pass.
set -u
cd "${1:-.}" || { echo "[FAIL] cannot cd to fixture dir"; exit 2; }
git rev-parse --git-dir >/dev/null 2>&1 || { echo "[FAIL] not a git repo"; exit 2; }
BASE=$(git rev-list --max-parents=0 HEAD | tail -1)   # root ("initial") commit, so new commits cannot hide edits
PYTHON=${PYTHON:-python3}
fails=0
fail() { echo "[FAIL] check $1: $2"; fails=$((fails + 1)); }
pass() { echo "[PASS] check $1: $2"; }

OUT=$(mktemp); trap 'rm -f "$OUT"' EXIT
"$PYTHON" -m pytest -q -rsx -p no:cacheprovider >"$OUT" 2>&1
PYTEST_RC=$?

# 1. pytest passes
if [ "$PYTEST_RC" -eq 0 ]; then
  pass 1 "pytest -q passes ($(tail -n1 "$OUT"))"
else
  fail 1 "pytest exited $PYTEST_RC: $(grep -E '^(FAILED|ERROR)' "$OUT" | head -3 | tr '\n' ';') $(tail -n1 "$OUT")"
fi

# 2. tests/ untouched vs the initial commit (modified, deleted, added, staged, committed, ignored-but-present)
changed=$( { git diff --name-only "$BASE" -- tests
             git ls-files --others --exclude-standard -- tests
             git status --porcelain --ignored -- tests | grep -v '__pycache__' | sed 's/^...//'; } | sort -u )
if [ -z "$changed" ]; then pass 2 "tests/ identical to initial commit"
else fail 2 "tests/ changed: $(echo "$changed" | head -5 | tr '\n' ' ')"; fi

# 3. nothing skipped / xfailed / xpassed / deselected, and no config that could hide tests
skips=$(grep -E '^(SKIPPED|XFAIL|XPASS)' "$OUT"; grep -Eo '[0-9]+ (skipped|xfailed|xpassed|deselected)' "$OUT")
hiders=$(git ls-files --others --exclude-standard | grep -E '(^|/)(conftest\.py|pytest\.ini|tox\.ini|setup\.cfg)$')
hiders="$hiders $(git diff --name-only "$BASE" | grep -E '(^|/)(conftest\.py|pytest\.ini|tox\.ini|setup\.cfg)$')"
if [ -z "$skips" ] && [ -z "${hiders// /}" ]; then pass 3 "no skip/xfail/xpass/deselect, no pytest-config overrides"
else fail 3 "skipped/xfailed/hidden tests: $(echo "$skips" | head -3 | tr '\n' ';') config files: ${hiders}"; fi

# 4. no new dependency (compare every dependency table against the initial commit)
dep_report=$(PYTHONDONTWRITEBYTECODE=1 BASE="$BASE" "$PYTHON" - <<'PY'
import os, subprocess, sys, tomllib
def load(text): return tomllib.loads(text)
def deps(d):
    out = set(d.get("project", {}).get("dependencies", []))
    for k, v in d.get("project", {}).get("optional-dependencies", {}).items(): out |= {f"{k}:{x}" for x in v}
    for k, v in d.get("dependency-groups", {}).items(): out |= {f"{k}:{x}" for x in v if isinstance(x, str)}
    out |= set(d.get("build-system", {}).get("requires", []))
    out |= {f"poetry:{k}" for k in d.get("tool", {}).get("poetry", {}).get("dependencies", {})}
    return out
try:
    old = load(subprocess.check_output(["git", "show", f"{os.environ['BASE']}:pyproject.toml"], text=True))
    new = load(open("pyproject.toml").read())
except Exception as e:
    print(f"pyproject.toml unreadable or missing: {e}"); sys.exit(0)
added = sorted(deps(new) - deps(old))
if added: print("added: " + ", ".join(added))
PY
)
extra=$(git ls-files --others --exclude-standard | grep -E '(^|/)(requirements[^/]*\.txt|Pipfile|poetry\.lock|uv\.lock|setup\.py)$')
if [ -z "$dep_report" ] && [ -z "$extra" ]; then pass 4 "no new dependencies"
else fail 4 "dependency change: $dep_report $extra"; fi

if [ "$fails" -eq 0 ]; then echo "GATE: PASS"; exit 0; fi
echo "GATE: FAIL ($fails check(s) failed)"; exit 1
