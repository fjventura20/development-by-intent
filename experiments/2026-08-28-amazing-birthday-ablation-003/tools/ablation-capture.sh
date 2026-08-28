#!/usr/bin/env sh
# BP-AB-ABLATION-003 wrapper: ablation-capture.sh
# Single POSIX shell script. No `flock`. No concurrency machinery (single-process experiment).
# Per §6.2: never overwrite an invocation capture. Per §6.6.6: record underlying
# Claude exit code; never mask a failed Claude call by returning wrapper exit 0.
#
# Usage:
#   PINNED_CWD=<abs-path> \
#   CONDITION=<A|B|C> \
#   SESSION=<a|b|c> \
#   TRIGGER_SHA7=<7hex> \
#   TRIGGER_TEXT="Birthdate <date>" \
#   tools/ablation-capture.sh <attempt-nn> <claude-flags...>
#
# Exit codes:
#   0   = Claude invocation succeeded (capture files written)
#   97  = Pinned cwd resolution / cd failure — BLOCK condition
#   98  = Capture target exists — pre-generator contamination risk; do not overwrite
#   99  = Wrapper self-error (parameter or invocation failure)
#   1-254 = Claude's underlying exit code (re-emitted; do not mask)
#
# Capture files (written only on Claude invocation, never on early exits):
#   $PINNED_CWD/captures/<condition>/<session>/attempt-<NN>-<trigger-sha7>.stdout.txt
#   $PINNED_CWD/captures/<condition>/<session>/attempt-<NN>-<trigger-sha7>.stderr.txt
#   $PINNED_CWD/captures/<condition>/<session>/attempt-<NN>-<trigger-sha7>.exit.txt

set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: ablation-capture.sh <attempt-nn> <claude-flags...>" >&2
  exit 99
fi

attempt="$1"
shift

# Validate environment
: "${PINNED_CWD:?PINNED_CWD must be set}"
: "${CONDITION:?CONDITION (A|B|C) must be set}"
: "${SESSION:?SESSION (a|b|c) must be set}"
: "${TRIGGER_SHA7:?TRIGGER_SHA7 (7 hex chars) must be set}"
: "${TRIGGER_TEXT:?TRIGGER_TEXT must be set}"

# Resolve and cd to pinned cwd
if [ ! -d "$PINNED_CWD" ]; then
  echo "wrapper: PINNED_CWD does not exist or is not a directory: $PINNED_CWD" >&2
  exit 97
fi
if [ ! -w "$PINNED_CWD" ]; then
  echo "wrapper: PINNED_CWD is not writable: $PINNED_CWD" >&2
  exit 97
fi
cd "$PINNED_CWD"

# Compute capture paths
capture_dir="$PINNED_CWD/captures/$CONDITION/$SESSION"
mkdir -p "$capture_dir"

stdout_path="$capture_dir/attempt-${attempt}-${TRIGGER_SHA7}.stdout.txt"
stderr_path="$capture_dir/attempt-${attempt}-${TRIGGER_SHA7}.stderr.txt"
exit_path="$capture_dir/attempt-${attempt}-${TRIGGER_SHA7}.exit.txt"

# No-clobber gate (§6.2)
if [ -e "$stdout_path" ] || [ -e "$stderr_path" ] || [ -e "$exit_path" ]; then
  echo "wrapper: capture target exists; refusing to overwrite (attempt=$attempt sha7=$TRIGGER_SHA7)" >&2
  exit 98
fi

# Invoke Claude. Per §6.6.3: never mask a failed call.
# We invoke with the recorded flags plus trigger via stdin, capture stdout/stderr/exit.
claude "$@" <<EOF
$TRIGGER_TEXT
EOF

claude_rc=$?
printf '%s\n' "$claude_rc" > "$exit_path" 2>/dev/null || true

# Re-emit Claude's exit code to the wrapper caller (§6.6.3).
# If we could not write the exit file, the wrapper itself has a problem —
# report the wrapper self-error so it is not masked.
if [ ! -s "$exit_path" ]; then
  echo "wrapper: failed to write exit capture; Claude rc was $claude_rc but is not preserved" >&2
  exit 99
fi

exit "$claude_rc"
