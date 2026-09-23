# COA-E1 v6.3 — Session Isolation Evidence

This file documents the session and memory isolation discipline applied during the v6.3 behavioral execution. Two pieces of evidence:

1. **Per-arm isolated profiles** (separate `~/.hermes/profiles/<name>/` directories, with `state.db` and `memories/` scoped to each profile).
2. **Default Telegram gateway memory UNCHANGED** before/after the entire run.

---

## 1. Per-arm isolated profiles

Three profiles were created at the start of the v6.3 execution:

```
/home/fjventura20/.hermes/profiles/coa-e1-arm-a/   (cloned from default, MEMORY.md/USER.md blanked)
/home/fjventura20/.hermes/profiles/coa-e1-arm-b/   (cloned from default, MEMORY.md/USER.md blanked)
/home/fjventura20/.hermes/profiles/coa-e1-arm-c/   (cloned from default, MEMORY.md/USER.md blanked)
```

Each profile carries:

- Its own `state.db` (SQLite SessionDB facade) at `/home/fjventura20/.hermes/profiles/<name>/state.db`.
- Its own `memories/` directory at `/home/fjventura20/.hermes/profiles/<name>/memories/`.
- Its own `sessions/` directory at `/home/fjventura20/.hermes/profiles/<name>/sessions/`.
- Its own `.env` (cloned from default; carries the `minimax` provider credentials).
- Its own `config.yaml` (cloned from default; binds `model.default: MiniMax-M3`, `model.provider: minimax`).

Wrapper scripts at `/home/fjventura20/.local/bin/coa-e1-arm-{a,b,c}` invoke `hermes -p coa-e1-arm-{a,b,c} ...` automatically.

### `state.db` is profile-scoped

Operator-runner used `-p coa-e1-arm-{a,b,c}` for every invocation. Each profile's `state.db` is a **separate SQLite file**, not shared with the default profile or with each other.

Verification (operator shell, post-run):

```
$ ls -la /home/fjventura20/.hermes/profiles/coa-e1-arm-{a,b,c}/state.db
-rw-r----- 1 fjventura20 fjventura20 266240 Sep 12 16:55 /home/fjventura20/.hermes/profiles/coa-e1-arm-a/state.db
-rw-r----- 1 fjventura20 fjventura20 327680 Sep 12 16:55 /home/fjventura20/.hermes/profiles/coa-e1-arm-b/state.db
-rw-r----- 1 fjventura20 fjventura20 376832 Sep 12 16:55 /home/fjventura20/.hermes/profiles/coa-e1-arm-c/state.db
```

(Compared with default profile: `/home/fjventura20/.hermes/profiles/main/state.db` is a symlink to `/home/fjventura20/.hermes/profiles/main/sessions/state.db`; arm profiles are independent files.)

### Each `--oneshot` invocation mints a fresh session id in the per-profile `state.db`

Per-session evidence (from `payload/EVIDENCE-v6.3-CLEAN/ARM-{A,B,C}/session-evidence.json`):

**ARM-A session IDs** (11 invocations: 1 init + 10 tasks):
```
20260912_165711_3e3173  (init)
20260912_165719_f337c4  (T6)
20260912_165726_169dca  (T1)
20260912_165733_adeb05  (T8)
20260912_165747_1eaaf3  (T3)
20260912_165807_f18bcb  (T7)
20260912_165817_393902  (T2)
20260912_165831_17195f  (T9)
20260912_165852_650a77  (T4)
20260912_165901_c766f9  (T10)
20260912_170037_747e57  (T5)
```

**ARM-B session IDs** (11 invocations):
```
20260912_170304_24e726  (init)
… (each task: distinct session id within coa-e1-arm-b profile)
```

**ARM-C session IDs** (11 invocations):
```
20260912_170555_<hex>   (init)
… (each task: distinct session id within coa-e1-arm-c profile)
```

Each session id is unique across the entire run. No session is shared between tasks or between arms.

### Pre-run memory clearing

Before each arm's first `--oneshot`, the operator executed:

```bash
mkdir -p /home/fjventura20/.hermes/profiles/$p/memories/.bak-pre-coa-e1
cp /home/fjventura20/.hermes/profiles/$p/memories/MEMORY.md .bak-pre-coa-e1/MEMORY.md.bak
cp /home/fjventura20/.hermes/profiles/$p/memories/USER.md .bak-pre-coa-e1/USER.md.bak
echo "" > /home/fjventura20/.hermes/profiles/$p/memories/MEMORY.md
echo "" > /home/fjventura20/.hermes/profiles/$p/memories/USER.md
```

This guaranteed that the per-arm profiles started with **empty MEMORY.md and USER.md** (1 byte each: `\n`). The cloned default-gateway content was preserved in `.bak-pre-coa-e1/` for evidence.

---

## 2. Default Telegram gateway memory UNCHANGED

The Telegram gateway runs on the `default` profile and uses `/home/fjventura20/.hermes/memories/MEMORY.md` and `USER.md` (note: NOT under a profile subdirectory — the default profile's memory lives at the home-level path).

Operator captured SHA-256s **before** the v6.3 run started (during the substrate-binding preflight at commit `67aee09`):

```
/home/fjventura20/.hermes/memories/MEMORY.md   1545 bytes  sha256:79078583976a6f7e7a38d92133ee471667c8a98237df479116a8385740cf4b1f
/home/fjventura20/.hermes/memories/USER.md      862 bytes  sha256:29928765b633021e1278f594da3f0b438d941403050dc54859d49ae3aa89cff4
```

Operator re-captured SHA-256s **after** the v6.3 run completed (post-ARM-C):

```
$ sha256sum /home/fjventura20/.hermes/memories/MEMORY.md /home/fjventura20/.hermes/memories/USER.md
79078583976a6f7e7a38d92133ee471667c8a98237df479116a8385740cf4b1f  /home/fjventura20/.hermes/memories/MEMORY.md
29928765b633021e1278f594da3f0b438d941403050dc54859d49ae3aa89cff4  /home/fjventura20/.hermes/memories/USER.md
```

**Both SHA-256s match byte-for-byte.** The default Telegram gateway memory was not touched by the COA-E1 v6.3 execution. The participant's T3 memory-write side effect was scoped to the per-arm profile `coa-e1-arm-c/memories/MEMORY.md` (see `ARM-C-MEMORY-DIFF.md`), not the default gateway.

---

## 3. Per-arm profile `MEMORY.md` state at end of run

| Profile | Final `MEMORY.md` size | Final SHA-256 | Modified by participant during arm? |
|---|---|---|---|
| `coa-e1-arm-a` | 1 byte (`\n`) | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` | NO |
| `coa-e1-arm-b` | 1 byte (`\n`) | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` | NO |
| `coa-e1-arm-c` | 719 bytes | `d68416dbe0e7e82eb33482f62aa7f1f2ceb157e1d98c1080544a7079b5393b49` | **YES** (T3 response) |

Only ARM-C was modified by the participant. ARM-A and ARM-B remained at the pre-run cleared state (1 byte).

---

## 4. Cross-references

- Per-arm profile creation: `EXECUTION-RESULT-v6.3.md` §"Session isolation discipline (per-arm profiles)".
- Runner script: `/tmp/coa-e1-v63-runner/run_arm.py` (operator infrastructure, not under freeze).
- Stop-BLOCKER #2 record (predecessor, documenting why per-arm profiles were needed): `experiments/2026-09-12-condition-of-agency-e1/execution/hermes/STOP-BLOCKER-2026-09-12-v6.3.md`.
