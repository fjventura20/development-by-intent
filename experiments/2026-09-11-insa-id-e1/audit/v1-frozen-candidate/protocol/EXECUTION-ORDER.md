# INSA-ID-E1 — Execution Order (frozen pre-execution)

**Status:** v0.1 (frozen-candidate), pending Frank-as-PI GO for execution.
**Author:** Hermes (operator).
**Date:** 2026-09-11.
**Binding:**
- Proposal: `docs/proposals/2026-09-10-INSA-ID-E1-proposal.md` @ `ed95705632027f459b396cd423eae54e8bb9a81b`
- Protocol: `protocol/INSA-ID-E1-protocol.md` (SHA filled at MANIFEST freeze)

---

## §1. OS-CSPRNG draw

The execution order is determined by an OS-CSPRNG draw at execution preflight time. The draw produces a deterministic ordering of (R, B, arm, candidate) tuples.

**Pre-freeze declaration (this artifact, frozen before execution):**

- **Draw mechanism:** `os.urandom` (Linux `/dev/urandom`); the seed is the SHA-256 of the draw-event timestamp concatenated with the OS-CSPRNG output sample. The seed is recorded in `hashing/execution-order-seed.txt` (immutable, written once, SHA-256 of the file recorded in `MANIFEST.json`).
- **Draw event:** `draw_event = sha256(utc_timestamp || os.urandom(32))`. The draw_event SHA is the reproducibility handle.
- **Ordering produced:** A list of `(R, B, arm, candidate)` tuples sorted by the draw_event-derived per-tuple score (CSPRNG output XORed with a per-tuple salt). The first tuple in the sorted list is executed first; the last is executed last.
- **Reproducibility:** Given the same draw_event and the same per-tuple salts, the same ordering is produced. Verification command recorded below.

**Pre-freeze salts and counts (NOT yet drawn — drawn at execution preflight):**

- **Reconstructions:** R1, R2, R3 (matches v0.1 BIB-001 non-deviated count). Frozen before draw.
- **Reconstruction inputs (B):** B1 = `inputs/reconstruction-input.txt` for both arms. The BIB exemplar source (`c3692150`) is byte-identical for Arm C and Arm M; only the layered second instruction differs (M directive vs no-op). Frozen before draw.
- **Arms:** C (control), M (modification). Frozen before draw.
- **Candidates per (R, B, arm):** N=10 (matches v0.1 OS-CSPRNG count). Frozen before draw.

**Total candidates:** 3 reconstructions × 1 B × 2 arms × 10 candidates = 60 candidates. Matches v0.1 §5.

**The draw event happens at execution preflight time, NOT at protocol freeze time.** This artifact freezes the draw mechanism + counts + reproducibility handles; the actual ordered list is produced at execution preflight and locked into `hashing/execution-order-list.json` (immutable, content-addressed).

---

## §2. Per-tuple salt

Per-tuple salt = `sha256("INSA-ID-E1:" || R || ":" || B || ":" || arm || ":" || candidate)`. Each (R, B, arm, candidate) tuple has a deterministic salt derived from its identity; the salt is reproducible from this artifact's specification.

---

## §3. Verification command (post-draw)

After the draw at execution preflight, the locked `hashing/execution-order-list.json` can be verified for reproducibility:

```
python3 -c "
import hashlib, json
seed = open('hashing/execution-order-seed.txt', 'rb').read()
with open('hashing/execution-order-list.json') as f:
    ordered = json.load(f)['order']
for entry in ordered:
    salt = hashlib.sha256(f'INSA-ID-E1:{entry[\"R\"]}:{entry[\"B\"]}:{entry[\"arm\"]}:{entry[\"candidate\"]}'.encode()).hexdigest()
    entry['salt'] = salt
# Verification: re-sort by (seed XOR salt) and confirm matches original order
# (The actual scoring uses a CSPRNG-derived byte stream; see hashing/score-derivation.py at preflight time.)
"
```

The verification command is runnable post-draw; the actual scoring function lives in `hashing/score-derivation.py` and is generated at preflight time (immutable, content-addressed).

---

## §4. Pre-flight checklist (run at execution preflight, before any model dispatch)

1. Verify all 16 frozen pre-execution artifact SHAs match `MANIFEST.json`.
2. Verify the frozen v0.3 architecture blob (`848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`) is unchanged on the local branch (no modifications to v0.3 since protocol freeze).
3. Verify the dbi-evolution-v0.1 frozen protocol SHA (`8874692d560d9a6363ef4105fae5384b18cf6ef2`) is unchanged (no modifications to v0.1 protocol since protocol freeze).
4. Verify model preflight (protocol §13): model identifier, CLI version, frozen source commit, tool posture, auth path, session-creation mechanism all recorded in `preflight/model-preflight-<executor>.md` and `preflight/model-preflight-<evaluator-A>.md`.
5. Verify the authority manifest is current and the grant provenance references the Frank-as-PI execution GO (not the protocol-authorization GO).
6. Run the OS-CSPRNG draw per §1 above. Lock `hashing/execution-order-seed.txt` and `hashing/execution-order-list.json`.
7. Verify evaluator blinding packet (`evaluation/evaluator-input-packet.md`) is frozen and contains no arm identity, no reconstruction number, no experiment identity, no candidate number.
8. Verify control validity pre-check C20 (protocol §8) by replaying Arm C candidates against the frozen BIB envelope (`inputs/baseline-envelope-membership.json`). C20 must PASS for Arm C candidates before any M-arm analysis; failure → STOP, classify `INVALID_EXPERIMENT`.

**Only after all 8 preflight items PASS does model dispatch begin.**

---

**End of EXECUTION-ORDER.md v0.1 (frozen-candidate).**