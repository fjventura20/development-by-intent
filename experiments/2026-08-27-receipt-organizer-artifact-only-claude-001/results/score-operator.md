# Operator Scoring — BP-RO-ARTIFACT-ONLY-CLAUDE-001

## Overall classification

**BLOCKED — environment-state-loss failure.**

The R-turn target acknowledged the Receipt Organizer behavior with all
substantive freeze-gate checks passing (READY present, no tool_use, no
prohibited phrases). However, the host Claude Code CLI cannot reliably deliver
subsequent `--resume` calls to the live session — see failures.md [T-1.0].

Per the protocol, this is classified as **environment-state-loss failure**, NOT
behavioral failure. Tests T1–T5 and G were not run.

## R-turn scoring (the only test that ran)

The R turn is not a scored test (it precedes the freeze gate). For
completeness, the operator scored the R output against the reconstruction
prompt's three substantive criteria:

| Criterion | Status |
|---|---|
| READY keyword present (case-sensitive, whole word, on its own line) | PASS |
| No tool_use content blocks in response | PASS |
| No verbatim prohibited phrases in response | PASS |
| Single-line output (rather than a long preamble) | PASS — exactly 1 line |

## What this evidence does and does not support

**Supports:**
- The target model can read the supplied RO durable package and acknowledge
  the Receipt Organizer behavior in a fresh conversation.
- The operator-side prelude and reconstruction prompt are correctly framed —
  no imperatives leaked from the artifact set to the target's
  interpretation.

**Does NOT support:**
- Multi-turn stateful behavior (ledger persistence across turns).
- Receipt extraction accuracy, classification, dedup, or query answering on
  any test receipt.
- Any claim about behavioral portability at the stateful tier until a
  different environment can deliver the multi-turn sequence.

## Recommendation

Mark this experiment BLOCKED. The R-turn evidence is preserved and operator-
scored above; ChatGPT independent scoring will be requested only on the R-turn
output. Tests T1–T5 and G are marked NOT RUN with environment-state-loss as
the documented reason.

File a v0.3 protocol amendment requiring a **session-resume pre-flight check**
(immediately after the R turn, attempt one resume with a benign message; if it
fails, fall back to a different environment before any tests run). This same
bug likely affected the AB replication series — recommend a retrospective audit
of 004, 005, 006 to confirm whether their session-resume calls actually
delivered to live session content.
