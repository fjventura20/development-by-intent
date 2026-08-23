#!/usr/bin/env bash
set -euo pipefail

REPO="development-by-intent"
DESCRIPTION="Experimental methodology for building, testing, and preserving AI-native applications through conversational intent."

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required: https://cli.github.com/"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Authenticate first with: gh auth login"
  exit 1
fi

cd "$(dirname "$0")"

if [[ ! -d .git ]]; then
  git init -b main
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "Initial Development by Intent experimental baseline"
fi

OWNER="$(gh api user --jq .login)"
if gh repo view "$OWNER/$REPO" >/dev/null 2>&1; then
  echo "Repository $OWNER/$REPO already exists; pushing current main branch."
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$OWNER/$REPO.git"
  git push -u origin main
else
  gh repo create "$REPO" \
    --public \
    --description "$DESCRIPTION" \
    --source=. \
    --remote=origin \
    --push
fi

echo "Published: https://github.com/$OWNER/$REPO"
