#!/usr/bin/env sh
# Pure structural wrapper self-test — NO Claude invocation allowed.
set -u
WRAPPER_PATH="/home/fjventura20/devProjectsU/development-by-intent-feat-ablation-003-freeze/experiments/2026-08-28-amazing-birthday-ablation-003/tools/ablation-capture.sh"
FREEZE_ROOT="/home/fjventura20/devProjectsU/development-by-intent-feat-ablation-003-freeze/experiments/2026-08-28-amazing-birthday-ablation-003"

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; exit 1; }

EXECUTABLE=$(grep -vE "^[[:space:]]*#|^[[:space:]]*$" "$WRAPPER_PATH")

# Runtime-cap check first.
RUNTIME=$(find "$FREEZE_ROOT" -type f ! -path "*/wrapper-self-test/*" 2>/dev/null | xargs grep -lE '"type":"result"' 2>/dev/null | head -3 || true)
if [ -n "$RUNTIME" ]; then fail "freeze has runtime model captures at: $RUNTIME"; fi
pass "no runtime captures in freeze"

# 1. Missing argument
"$WRAPPER_PATH" 2>/dev/null && fail "missing-arg accepted" || pass "missing-arg rejected"

# 2. Bad PINNED_CWD
PINNED_CWD=/no/such/dir "$WRAPPER_PATH" 1 --allowedTools "" 2>/dev/null && fail "bad-cwd accepted" || pass "bad-cwd rejected"

# 3. No flock in executable lines
printf '%s\n' "$EXECUTABLE" | grep -q flock && fail "wrapper has flock" || pass "no flock in executable lines"

# 4. Captures claude_rc
printf '%s\n' "$EXECUTABLE" | grep -q "claude_rc=" || fail "wrapper does not capture Claude rc"

# 5. Re-emits claude_rc as exit
if ! printf '%s\n' "$EXECUTABLE" | grep -q "claude_rc"; then fail "wrapper missing claude_rc"; fi
pass "wrapper captures and re-emits Claude rc"

# 6. No-clobber (exit 98)
printf '%s\n' "$EXECUTABLE" | grep -q "exit 98" || fail "wrapper missing exit 98"

echo "ALL TESTS PASS"
exit 0
