#!/usr/bin/env bash
# (Re)create each fixture as its own git repo with a single "initial" commit.
# Needed after cloning this repo, because nested .git dirs are not stored in the parent repo.
# WARNING: wipes any existing fixture-*/.git (and so any agent changes' history); work is kept in the tree.
set -euo pipefail
cd "$(dirname "$0")"
for d in fixture-a fixture-b; do
  rm -rf "$d/.git" "$d/.pytest_cache"; find "$d" -name __pycache__ -prune -exec rm -rf {} +
  git -C "$d" init -q -b main
  git -C "$d" config user.email poc@example.com; git -C "$d" config user.name poc
  git -C "$d" add . && git -C "$d" commit -q -m initial
  echo "$d: $(git -C "$d" log --oneline | head -1)"
done
