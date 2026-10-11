#!/usr/bin/env bash
# Proves gate.sh rejects test tampering. Works on throwaway copies; never touches the real fixtures.
# Each case must (1) make the gate exit non-zero and (2) trip the specific check named.
HERE=$(cd "$(dirname "$0")" && pwd)
GATE="$HERE/gate.sh"
WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
status=0

fresh() { rm -rf "$WORK/fx"; cp -a "$HERE/fixture-a" "$WORK/fx"; }
expect_reject() {  # name, expected-check-number
  out=$(bash "$GATE" "$WORK/fx" 2>&1); rc=$?
  if [ $rc -ne 0 ] && echo "$out" | grep -q "^\[FAIL\] check $2:"; then
    echo "REJECTED ok  - $1 (check $2)"; echo "$out" | grep -E '^\[FAIL\]' | sed 's/^/    /'
  else echo "NOT REJECTED - $1 (rc=$rc)"; echo "$out" | sed 's/^/    /'; status=1; fi
}

# baseline sanity: unmodified fixture must fail only check 1 (the bugs), not 2-4
fresh; out=$(bash "$GATE" "$WORK/fx" 2>&1)
if echo "$out" | grep -q '^\[FAIL\] check 1' && echo "$out" | grep -q '^\[PASS\] check 2' \
   && echo "$out" | grep -q '^\[PASS\] check 3' && echo "$out" | grep -q '^\[PASS\] check 4'; then
  echo "baseline ok  - untouched fixture fails only check 1"
else echo "baseline BAD"; echo "$out"; status=1; fi

fresh; rm "$WORK/fx/tests/test_tax.py"
expect_reject "(a) deleted a test file" 2

fresh; python3 - "$WORK/fx" <<'PY'
import sys, re, pathlib
p = pathlib.Path(sys.argv[1], "tests/test_money.py"); s = p.read_text()
p.write_text("import pytest\n" + s.replace("def test_large_amount_does_not_wrap", "@pytest.mark.skip\ndef test_large_amount_does_not_wrap"))
PY
(cd "$WORK/fx" && git commit -qam "tamper" ) # committed tampering must still be caught (diff is vs root commit)
expect_reject "(b) added @pytest.mark.skip (and committed it)" 2
# also show check 3 independently: skip applied in an untracked conftest
fresh; printf 'import pytest\ndef pytest_collection_modifyitems(items):\n    [i.add_marker(pytest.mark.skip) for i in items if "test_tax" in i.nodeid]\n' > "$WORK/fx/conftest.py"
expect_reject "(b2) skip injected via conftest.py" 3

fresh; sed -i 's/== 1999/>= 0/' "$WORK/fx/tests/test_money.py"
expect_reject "(c) weakened an assertion" 2

# extra: dependency added
fresh; sed -i 's/dependencies = \["pytest"\]/dependencies = ["pytest", "requests"]/' "$WORK/fx/pyproject.toml"
expect_reject "(d) added a dependency" 4

[ $status -eq 0 ] && echo "SELFTEST: ALL REJECTIONS PROVEN" || echo "SELFTEST: FAILED"
exit $status
