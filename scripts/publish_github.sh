#!/usr/bin/env bash
# Uses the account owner's existing GitHub CLI login. Does not request or embed tokens.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
repo="${1:-RAckklot/em-ir-switching-phase-audit}"
if ! command -v gh >/dev/null; then
  echo "Install GitHub CLI (https://cli.github.com/), then run: gh auth login" >&2
  exit 2
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "Authenticate first with: gh auth login" >&2
  exit 2
fi
if [ ! -d .git ]; then
  git init -b main
fi
git add -A
if ! git diff --cached --quiet; then
  git commit -m "Publish validated EM-IR phase-audit v1.0.0"
fi
if git remote get-url origin >/dev/null 2>&1; then
  echo "An origin remote already exists. Inspect it before pushing:" >&2
  git remote -v >&2
  exit 2
fi
gh repo create "$repo" --public --source=. --remote=origin --push --description \
  "Validated, reproducible dynamic IR-drop phase counterexample and tool documentation audit"
echo "Public repository created. Connect it to Zenodo BEFORE running scripts/create_release.sh."
