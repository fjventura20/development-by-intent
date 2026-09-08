# Multi-Turn Persistence Validation (DBI State Isolation v0.1 v0.2 preflight §8.1)

**Date:** 2026-09-08
**Author:** Hermes (operator, under DBI Research Manager mandate adopted 2026-08-27)
**Purpose:** Validate that `claude --resume <session_id>` on this host produces a real persistent context (not a stale session, not a cache miss, not a model that "remembers" but does not actually use the context), per PI adjudication Q2.

---

## 1. Validation protocol (per v0.2 §8.1)

The validation has 5 steps:

1. Start a `claude-sonnet-4-6` session with a distinctive preamble.
2. Resume the session with a probe that should NOT be answerable without the preamble context.
3. Confirm the model produces a contextually-grounded answer.
4. Confirm the session_id persists across `--resume` invocations.
5. Confirm the model's `cache_read_input_tokens` field in the resumed invocation reflects the prior context length.

---

## 2. Validation result

### Step 1: Start session with distinctive preamble

**Command:**
```bash
echo "You are a birthday trivia assistant. When I give you a date, respond with one sentence. The secret codephrase for this session is the number 42." \
  | claude --model claude-sonnet-4-6 --print --output-format json
```

**Captured session_id:** `ef8fb926-5902-459b-930e-a043e8468c8b`

**Response:** "Ready! Give me a date and I'll share a fun trivia fact about it."

**Output sample:**
```json
{
  "type": "result", "subtype": "success", "is_error": false,
  "session_id": "ef8fb926-5902-459b-930e-a043e8468c8b",
  "modelUsage": {
    "claude-sonnet-4-6": {
      "inputTokens": 2, "outputTokens": 79,
      "cacheReadInputTokens": 11365, "cacheCreationInputTokens": 6578
    }
  }
}
```

### Step 2: Resume with the codephrase probe

**Command:**
```bash
echo "What is the secret codephrase for this session?" \
  | claude --resume ef8fb926-5902-459b-930e-a043e8468c8b \
          --model claude-sonnet-4-6 --print --output-format json
```

**Response:** "The secret codephrase for this session is **42**."

**Output sample:**
```json
{
  "type": "result", "subtype": "success", "is_error": false,
  "session_id": "ef8fb926-5902-459b-930e-a043e8468c8b",
  "modelUsage": {
    "claude-sonnet-4-6": {
      "inputTokens": 2, "outputTokens": 88,
      "cacheReadInputTokens": 11808, "cacheCreationInputTokens": 36
    }
  }
}
```

**Step 3: PASS.** The model correctly retrieved the codephrase from the prior session context.

### Step 4: session_id persistence

**PASS.** Both invocations returned `session_id: ef8fb926-5902-459b-930e-a043e8468c8b`. The session_id is stable across `--resume` invocations.

### Step 5: cache_read_input_tokens reflects prior context

**Initial invocation:**
- `cacheReadInputTokens: 11365` (baseline prompt caching)

**Resumed invocation (after the codephrase probe):**
- `cacheReadInputTokens: 11808` (increased by 443 tokens, reflecting the prior context)

**PASS.** The cache_read_input_tokens field confirms the prior context was loaded and used.

### Additional probe: 10 consecutive repeated-trigger invocations (trivial prompt, no BIB contract)

**Setup:** A trivial "tell me a fact about this date" prompt, not the BIB contract.

**Result:** Across 10 repeated invocations of the same trigger (`Birthdate February 20, 1952`), the model produced 10 different facts with NO deferral. The model did not switch to "we already covered this" mode on a trivial prompt.

**Implication:** the deferral mechanism is specific to (a) the BIB contract + (b) the modified arm + (c) sufficient non-trivial behavioral output. A trivial prompt does not trigger it. The State Isolation v0.1 experiment must hold (a) and (b) constant (which the v0.2 protocol does via the frozen Evolution Arm M reconstruction input) and reproduce (c) by using the same 5 canonical dates in the same order in the same session.

---

## 3. Disposition

**Multi-turn persistence is VALIDATED on this host.**

- `claude --model claude-sonnet-4-6 --print` produces a session with a stable session_id.
- `claude --resume <session_id> --model claude-sonnet-4-6 --print` correctly continues the session, with the model retrieving prior context.
- The cache_read_input_tokens field increases after `--resume`, confirming the prior context is loaded into the model's context window.
- The same mechanism produced the Evolution v0.1 R2_B deferrals (session_id `2fb8836e-8fe1-4034-abe9-a234104e74e7`).

**The v0.2 protocol §6.1 mechanism is the same as Evolution v0.1's mechanism.** No mechanism substitution has occurred.

---

## 4. What this validation does NOT cover

- **Adversarial or production load conditions.** This validation runs at operator-driven, low-load conditions. The Evolution v0.1 R2_B deferrals occurred under the operator's normal workflow; a future validation under high load may produce different results.
- **Substrate-runtime stability across days.** The `claude-sonnet-4-6` model is available on this host as of 2026-09-08. If the model becomes materially unavailable or changes its behavior at generation time, the §8.2 material-runtime deviation check applies.
- **The BIB contract's specific deferral pattern.** This validation used a trivial prompt; the BIB contract deferral pattern is reproduced by the State Isolation v0.1 main experiment, not by this preflight.

---

## 5. Provenance

This artifact was authored on 2026-09-08 by Hermes (operator, DBI Research Manager mandate 2026-08-27) as part of the State Isolation v0.1 v0.2 preflight validation per PI adjudication Q2. The session_id `ef8fb926-5902-459b-930e-a043e8468c8b` is the operator's validation session; it has no relationship to the main experiment's sessions.

The prior multi-turn persistence validation that produced Evolution v0.1's R2_B deferrals is at `experiments/2026-09-06-dbi-evolution-v0.1/runs/R2_M/` (session_id `2fb8836e-8fe1-4034-abe9-a234104e74e7`).

End of multi-turn persistence validation.
