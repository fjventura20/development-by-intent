# Failures and Deviations — Transcript-Only Claude 004

**Disposition:** INDETERMINATE (per v0.1.1 § Freeze / first-call / no-repair rules)
**Behavioral signal:** Strong PASS across all three preserved tests (see `interpretation.md`)
**Independent review:** Required, pending ChatGPT review via Frank-as-relay

## Failure 1 — raw evidence capture truncation (BLOCKING-class evidence defect)

**Class:** `evidence_capture_failure` (per protocol's failure taxonomy implied by § Freeze / first-call / no-repair rules).

**Symptom.** Two of four raw JSON captures are byte-clipped at 8,192 bytes mid-envelope.

| File | Bytes | State |
|------|-------|-------|
| `reconstruction-raw.json` | 1,993 | clean; full JSON envelope parses |
| `test-1-raw.json` | 7,616 | clean; full JSON envelope parses |
| `test-2-raw.json` | **8,192** | **truncated mid-envelope**; JSON parser fails on unterminated string at byte 8,107 |
| `test-3-raw.json` | **8,192** | **truncated mid-envelope**; JSON parser fails on unterminated string at byte 8,107 |

**Where it cuts.** Both truncations land inside the trailing `"modelUsage"` / `"permissions"` block — *after* the `"result"` JSON string has fully closed. The assistant-text content (the load-bearing portion of the experiment) is fully visible in the captured bytes of every truncated file.

For test-2 the captured region ends inside the `modelUsage.claude-sonnet-4-6` block, after `total_cost_usd: 0.08714579999999998` and `outputTokens: 4529`. Visible assistant narrative includes the closing line *"You were born on a day that barely exists — which is exactly right for someone born into a year that remade the world."* (final of the leap-year framing) before the `","stop_reason":"end_turn"`-then-envelope tail.

For test-3 the captured region ends after `total_cost_usd: 0.091788`. Visible assistant narrative includes the closing line *"The world in 1956 was divided, frightened, and electrified by possibility. It is almost unrecognizable from the one you inhabit now."* followed by *"You were there for all of it."* before the `","stop_reason":"end_turn"`-then-envelope tail.

**Root cause.** Operator pipeline used `claude ... | tee FILE | head -c 200`. The `head -c 200` consumer closed after 200 bytes; SIGPIPE rippled upstream; Claude Code's streaming JSON serializer appears to emit a partial-write boundary at ~8 KiB (kernel PIPE_BUF boundary on this Linux host) when its consumer is gone. The transcript content was not lost — only the trailing JSON envelope — but the captures are formally truncated JSON and an automated validator cannot certify them as clean first-call records.

**Mitigation in this run.** None applied. Per protocol: no re-issues for evidence capture, ever. The protocol was followed; the capture discipline was inadequate.

**Mitigation for a clean replication.** Two options:
- (a) Drop the `| head -c 200` consumer entirely; let `tee` write to file alone and inspect the file in a separate step.
- (b) Use `claude --output-format stream-json` and accumulate via a controlled consumer that reads the entire stream before closing.

This is exactly the same class of evidence-capture defect that affected upstream experiment 001, and the same fix pattern (different capture discipline, same scientific design) that resolved it in replication 002.

**Per protocol § Freeze / first-call / no-repair rules:**
> *"Lost/truncated/re-issued first-call evidence makes the run INDETERMINATE."*

This run is **INDETERMINATE.**

## Contamination / repair / fallback checks (all clean)

- **No contamination detected.** Target session `eec5da0c-ede0-4777-9bd6-29c367fd24e1` is fresh; `~/.claude/projects/` shows no prior Amazing Birthday context reachable from the session. `claude auth status` confirms `loggedIn=true` for this operator only.
- **No repair applied.** No clarification, hint, regeneration, prompt-engineering repair, model fallback, or provider fallback occurred during the four turns. The four user prompts sent to the target were, in frozen order:
  1. `Reconstruct the application per the system prompt. When you are ready, state that you are ready.`
  2. `Birthdate November 9, 1989`
  3. `Birthdate February 29, 1960`
  4. `Birthdate June 23, 1956`
- **Same target model across all turns.** `claude --model claude-sonnet-4-6` invoked for every turn. No model fallback or substitution.
- **No-tools posture held.** `--allowedTools ''` for every turn (denies Read, Write, Bash, WebFetch, WebSearch). Target had no path to read the withheld test set before freeze, nor any path to look anything up.

## Sub-findings (not failures, surface for protocol v0.2)

- **Cache behavior.** First prompt carries 16,523 cache-creation tokens (the transcript text is cached for the entire session). Subsequent turns use 20,581–20,581 cache-read tokens. The transcript-only input has a different cost profile than the artifact-only Phase A: replication 002 cost $0.21 across 4 turns; this run cost $0.38. The delta is the cache-warmup cost of inlining the much larger transcript (27 KB vs. ~5 KB total of two Phase A artifacts).
- **Internal model split.** Claude Code at session start allocated a Haiku 4.5 sub-thread for tool-search warmup (15 output tokens, $0.0005) before settling into Sonnet 4-6 for the work itself. The target *visible* outputs are all Sonnet 4-6.
- **ttft_ms tail.** Cold-start reconstruction ttft was 12.2 s; withheld-test ttft ranged 39.6–55.5 s (deep-cache reads, not cold). The ttft itself is not a behavioral metric but the asymmetry is worth noting.

None of these are protocol deviations. They are noted for replication-005 design.
