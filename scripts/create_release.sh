#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
if [ "${1:-}" != "--zenodo-enabled" ]; then
  echo "First link GitHub to Zenodo and enable this repository at https://zenodo.org/account/settings/github/" >&2
  echo "Then run: bash scripts/create_release.sh --zenodo-enabled" >&2
  exit 2
fi
command -v gh >/dev/null || { echo "GitHub CLI gh is required" >&2; exit 2; }
gh auth status >/dev/null
gh repo view >/dev/null
gh release create v1.0.0 EM_IR_Validated_Report.pdf \
  --title "v1.0.0 — Validated switching-phase counterexample" \
  --notes-file RELEASE_NOTES.md --latest
echo "Release published. Check Zenodo's GitHub integration for the archived DOI."
