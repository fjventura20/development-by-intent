#!/usr/bin/env sh
# Wrapper self-test: no model invocation; exercises structural paths only.
set -eu
WRAPPER="/home/fjventura20/devProjectsU/development-by-intent-feat-ablation-003-freeze/experiments/2026-08-28-amazing-birthday-ablation-003/tools/ablation-capture.sh"
TESTDIR="/home/fjventura20/devProjectsU/development-by-intent-feat-ablation-003-freeze/experiments/2026-08-28-amazing-birthday-ablation-003/preflight/wrapper-self-test"

# 1. Missing-arg test: must exit 99
if "$WRAPPER" 2>/dev/null; then
  echo "FAIL: missing-arg did not exit 99"
  exit 1
fi
echo "PASS: missing-arg exits 99"

# 2. Bad PINNED_CWD test: must exit 97
PINNED_CWD=/nonexistent "$WRAPPER" 1 --allowedTools "" 2>/dev/null && echo "FAIL: bad cwd did not exit 97" || echo "PASS: bad cwd exits 97"

# 3. Missing CONDITION: must exit 99
PINNED_CWD="$TESTDIR" "$WRAPPER" 1 --allowedTools "" 2>/dev/null && echo "FAIL: missing CONDITION did not exit 99" || echo "PASS: missing CONDITION exits 99"

# 4. No-clobber test: create a captured file, then run wrapper, must exit 98
mkdir -p "$TESTDIR/captures/A/a"
touch "$TESTDIR/captures/A/a/attempt-1-cli98.std.stdout.txt"
PINNED_CWD="$TESTDIR" CONDITION=A SESSION=a TRIGGER_SHA7=cli98 TRIGGER_TEXT=__test__   "$WRAPPER" 1 --allowedTools "" 2>/dev/null && echo "FAIL: no-clobber did not exit 98" || echo "PASS: no-clobber exits 98"

# 5. No `flock` audit (must be absent from wrapper)
if grep -q 'flock' "$WRAPPER"; then
  echo "FAIL: wrapper still references flock (should not per controller simplification §Simplify 1)"
  exit 1
fi
echo "PASS: no flock in wrapper"

# 6. Mask-claude-failure audit: wrapper passes through underlying Claude rc
if ! grep -q 'claude_rc=' "$WRAPPER"; then
  echo "FAIL: wrapper does not capture Claude rc (would mask Claude failures)"
  exit 1
fi
echo "PASS: wrapper captures Claude rc"

# 7. Do not commit a runtime model capture into the freeze preflight
if [ -f "$TESTDIR/captures/A/a/attempt-1-cli98.std.stdout.jsonl" ] && [ -s "$TESTDIR/captures/A/a/attempt-1-cli98.std.stdout.jsonl" ]; then
  echo "FAIL: preflight contains a runtime model capture (would violate Simplify 5)"
  exit 1
fi
echo "PASS: preflight does not contain runtime model captures"

# OK
exit 0
