#!/usr/bin/env python3
"""Collect one results row per Prime Agent run.

  metrics.py begin  <run_label>                         # record start time (run just before starting the agent)
  metrics.py finish <run_label> <fixture_dir> [--log FILE] [--subagents N] [--turns N] [--tokens N]

--log is optional: a `prime-agent --mode json` event stream (JSONL) or a session JSONL/JSON file.
Turns/tokens/subagents are parsed best-effort from it and printed as "n/a" when not found.
The event names (turn_end, message_end) and usage keys come from reading the source, not from
documentation, so treat parsed numbers as UNVERIFIED until compared once against the TUI's own counters.
Explicit --turns/--tokens/--subagents override parsing (use them to copy numbers from the TUI).
"""
import argparse, csv, datetime as dt, json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, ".runs")
CSV = os.path.join(HERE, "results.csv")
COLUMNS = ["run_label", "fixture", "start_ts", "duration_s", "turns", "tokens", "subagents", "gate_passed", "lines_changed"]


def begin(label):
    os.makedirs(RUNS, exist_ok=True)
    now = time.time()
    with open(os.path.join(RUNS, f"{label}.start"), "w") as f:
        f.write(repr(now))
    print(f"start recorded for {label}: {dt.datetime.fromtimestamp(now, dt.timezone.utc).isoformat()}")


def read_events(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        out = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try: out.append(json.loads(line))
                except json.JSONDecodeError: pass
        return out


def usage_tokens(u):
    if not isinstance(u, dict): return 0
    def g(*keys): return next((u[k] for k in keys if isinstance(u.get(k), (int, float))), 0)
    return int(g("input", "inputTokens") + g("output", "outputTokens")
               + g("cacheRead", "cache_read") + g("cacheWrite", "cache_write"))


def walk(o):
    yield o
    if isinstance(o, dict):
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)


def parse_log(path):
    """Return (turns, tokens, subagents); each None when not observable."""
    events = read_events(path)
    raw = open(path, encoding="utf-8", errors="replace").read()
    turns = sum(1 for e in events if isinstance(e, dict) and e.get("type") == "turn_end") or None
    tokens = 0
    for e in events:
        if isinstance(e, dict) and e.get("type") == "message_end":
            msg = e.get("message") or {}
            if msg.get("role") == "assistant": tokens += usage_tokens(msg.get("usage"))
    if not tokens:  # session-file shape: assistant messages carrying usage
        for e in events:
            for node in walk(e):
                if isinstance(node, dict) and node.get("role") == "assistant" and "usage" in node:
                    tokens += usage_tokens(node["usage"])
    spawned = len(re.findall(r"rlm\.spawn\(", raw))
    # code appears in the log both as the call and possibly echoed; count distinct name="..." arguments instead
    names = set(re.findall(r"rlm\.spawn\([^)]*?name\s*=\s*\\?[\"']([^\"'\\]+)", raw))
    return turns, (tokens or None), (len(names) if names else (spawned or None))


def sh(cwd, *cmd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def lines_changed(fx):
    base = sh(fx, "git", "rev-list", "--max-parents=0", "HEAD").stdout.split()[-1]
    sh(fx, "git", "add", "-N", ".")  # make untracked new files visible to diff --stat (intent-to-add only)
    stat = sh(fx, "git", "diff", "--shortstat", base).stdout.strip()
    ins = re.search(r"(\d+) insertion", stat); dele = re.search(r"(\d+) deletion", stat)
    return (int(ins.group(1)) if ins else 0) + (int(dele.group(1)) if dele else 0), sh(fx, "git", "diff", "--stat", base).stdout


def finish(a):
    fx = os.path.abspath(a.fixture)
    start_file = os.path.join(RUNS, f"{a.label}.start")
    start = float(open(start_file).read()) if os.path.exists(start_file) else None
    duration = round(time.time() - start, 1) if start else "n/a"
    gate = subprocess.run(["bash", os.path.join(HERE, "gate.sh"), fx], capture_output=True, text=True)
    checks = re.findall(r"^\[(PASS|FAIL)\] check (\d): (.*)$", gate.stdout, re.M)
    turns = tokens = subs = None
    if a.log:
        turns, tokens, subs = parse_log(a.log)
    turns = a.turns if a.turns is not None else turns
    tokens = a.tokens if a.tokens is not None else tokens
    subs = a.subagents if a.subagents is not None else subs
    changed, stat = lines_changed(fx)
    row = {"run_label": a.label, "fixture": os.path.basename(fx),
           "start_ts": dt.datetime.fromtimestamp(start, dt.timezone.utc).isoformat() if start else "n/a",
           "duration_s": duration, "turns": "n/a" if turns is None else turns,
           "tokens": "n/a" if tokens is None else tokens, "subagents": "n/a" if subs is None else subs,
           "gate_passed": gate.returncode == 0, "lines_changed": changed}
    new = not os.path.exists(CSV)
    with open(CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if new: w.writeheader()
        w.writerow(row)
    print(f"== {a.label} on {row['fixture']}")
    for status, n, msg in checks: print(f"  [{status}] check {n}: {msg}")
    print(f"  wall-clock: {duration}s | turns: {row['turns']} | tokens: {row['tokens']} | subagents: {row['subagents']}")
    print(f"  lines changed vs initial commit: {changed}\n{stat}")
    print(f"row appended to {CSV}")
    return 0 if row["gate_passed"] else 1


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("begin"); b.add_argument("label")
    f = sub.add_parser("finish"); f.add_argument("label"); f.add_argument("fixture")
    f.add_argument("--log"); f.add_argument("--subagents", type=int); f.add_argument("--turns", type=int); f.add_argument("--tokens", type=int)
    a = p.parse_args()
    if a.cmd == "begin": begin(a.label)
    else: sys.exit(finish(a))
