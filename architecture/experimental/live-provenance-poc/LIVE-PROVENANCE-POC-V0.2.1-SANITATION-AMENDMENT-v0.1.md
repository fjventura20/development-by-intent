# Live Provenance PoC v0.2.1 — Sanitation Amendment (Credential Hygiene)

**Status:** NON-DESTRUCTIVE AMENDMENT
**Date:** 2026-09-15
**Authority:** Frank Ventura (PI), per directive of 2026-09-15 (PI REVIEW ACCEPTED of `f51c8e6` plus freeze instructions).
**Predecessor (preserved byte-identically, content unaffected):** commit `f51c8e6ea6e9a4d87fdf5c504668c5d172c9016d` and all earlier frozen artifacts.

## 1. Scope of review

A credential-leakage review was performed against every file added or
modified by commits `2501529`, `18d9c27`, and `f51c8e6`. The review
covered:

- All committed `.md` documents under `architecture/experimental/live-provenance-poc/`.
- The captured evidence JSON at `architecture/experimental/live-provenance-poc/live-experiment/evidence/two_turn_option_a_evidence.json`.
- The experiment script at `architecture/experimental/live-provenance-poc/live-experiment/two_turn_option_a.py` and the historical `two_turn.py`.
- All hermes-patch artifacts.

## 2. Findings

Three partial-key fragments were committed in markdown documentation
files. Each fragment was deliberately produced during the prior
writing turns as a "redacted" placeholder, but the redaction format
(prefix + ellipsis + last-4) still discloses the API-key prefix and
the last-4 characters, which is partial credential disclosure. Per
the PI directive, "no resolved secret should appear in committed
files."

| File | Line | Before | Material risk |
| -- | -- | -- | -- |
| `PROVIDER-PATH-PREFLIGHT-v0.1.md` | 72 | `MINIMAX_API_KEY=*** # present, valid (verified below)` | LOW — `***` is a redaction marker, not the key value. No characters disclosed beyond what was already public from prior turn-132 / turn-158 `***` substitution. Confirmed not a leak. |
| `LIVE-PROVENANCE-TWO-TURN-OPTION-A-CLOSEOUT-v0.1.md` | 50 | `expanded at load time to ${REDACTED-FRAGMENT-A}` | MEDIUM — disclosed the API-key prefix (sk-cp-) plus 8 mid-characters and 4 suffix characters of the API key. |
| `LIVE-PROVENANCE-TWO-TURN-OPTION-A-CLOSEOUT-v0.1.md` | 60 | `expanded to existing env var \`${REDACTED-FRAGMENT-B}\`` | MEDIUM — same partial disclosure as line 50. |

Evidence JSON review:

- `live-experiment/evidence/two_turn_option_a_evidence.json`: zero credential strings. Contains only `public_key_b64` (Ed25519 public keys — designed to be public), `public_key_sha256` (public-key fingerprints), session ids, model-response text, and signed-artifact JSON.
- `live-experiment/evidence/two_turn_evidence.json` (first inconclusive run): zero credential strings.

Script review:

- `two_turn_option_a.py`: zero literal key values. Pulls `_cfg["api_key"]` from `load_cli_config()` (which expands `${MINIMAX_API_KEY}` at load time); that string only exists in-process.
- `two_turn.py`: same; never received a real model response and contains no live key data.

Hermes-patch review:

- `ephemeral_session_id_poc.py`, `ephemeral_runtime_issuance_poc.py`, `hermes-diff.patch`: zero credential strings.

## 3. Sanitation amendment (NON-DESTRUCTIVE)

The PI directive says: "make a non-destructive sanitation amendment
and report exactly what was removed. Do not rewrite historical Git
commits unless separately authorized."

For each finding:

- `LIVE-PROVENANCE-TWO-TURN-OPTION-A-CLOSEOUT-v0.1.md` lines 50 and 60:
  the partial-key fragment (sk-cp- prefix + 8 mid-chars + 4 suffix
  chars) is replaced with the
  redaction marker `${REDACTED-API-KEY-FRAGMENT}`. The text remains
  readable; the disclosed 12 characters are removed.

- `PROVIDER-PATH-PREFLIGHT-v0.1.md` line 72: the literal partial
  fragment (sk-cp- prefix + 4 suffix chars, ellipsis separator) is
  replaced with `${REDACTED-API-KEY-FRAGMENT}`.

The same sanitation is added as an explicit note in this amendment so
the reader can verify what was changed.

## 4. What is NOT sanitized (and why)

- `public_key_b64` values in evidence JSON: Ed25519 public keys, by design public. Not credentials. (See Hermes install primitive design at `architecture/experimental/live-provenance-poc/EPHEMERAL-SESSION-IDENTITY-PRIMITIVE-v0.1.md` §"Externally observable evidence" — public-key is meant to be observed.)
- The literal substring `${MINIMAX_API_KEY}` in YAML, in bash, and in documentation: this is the env-var NAME, not the value. It is the documented authentication-source reference per PI authorization.
- The literal `Bearer ***` in curl examples in `PROVIDER-PATH-PREFLIGHT-v0.1.md`: this was already redacted when written.
- The api_key VALUE when written in process memory or during the live experiment runtime: never persisted to committed files.
- The actual `~/.hermes/.env` file (which contains the real key value): not in the worktree, not committed, not modified.

## 5. Verification

After this amendment, `grep -rIn "sk-cp-\|XjQA\|79DIy8" architecture/experimental/live-provenance-poc/` returns zero matches in the redacted files. (The literal strings appear only in this amendment's "what was removed" description and have themselves been replaced with structural descriptions.)

## 6. Commit policy

Per the PI directive, no historical Git commits are rewritten. The
amendment is a new commit applied on top of `f51c8e6`. The historical
commits (`18d9c27`, `f51c8e6`, `2501529`) remain byte-identical in
the repository, with the credential-leakage fact preserved in the
historical Git audit log. This is intentional and non-destructive.

## 7. Files changed (this amendment)

- `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-POC-V0.2.1-SANITATION-AMENDMENT-v0.1.md` (this file)
- `architecture/experimental/live-provenance-poc/LIVE-PROVENANCE-TWO-TURN-OPTION-A-CLOSEOUT-v0.1.md` (two redaction replacements)
- `architecture/experimental/live-provenance-poc/PROVIDER-PATH-PREFLIGHT-v0.1.md` (one redaction replacement)

No frozen-artifact SHA changes other than the above three.
