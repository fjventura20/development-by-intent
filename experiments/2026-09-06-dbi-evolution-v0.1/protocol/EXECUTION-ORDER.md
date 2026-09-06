# Execution Order (frozen at protocol freeze)

```json
{
  "schema_version": "0.1",
  "record_kind": "execution-order-randomization",
  "experiment_id": "DBI-Evolution-v0.4",
  "generated_at_utc": "2026-09-06T19:35:00Z",
  "method": "OS-CSPRNG draw via random.SystemRandom(); Fisher-draw of arm order per matched reconstruction level",
  "random_seed_hex": "ed82e105f3b5791b09c4a62f13364a6ff6d870ab159f2a72892575f0be5ab12e",
  "random_seed_source": "random.SystemRandom().getrandbits(256) - OS entropy (/dev/urandom)",
  "reconstruction_level_arm_order": {
    "R1": [
      "C",
      "M"
    ],
    "R2": [
      "C",
      "M"
    ],
    "R3": [
      "M",
      "C"
    ]
  },
  "rule": "Each matched reconstruction level (R1, R2, R3) executes the two arms in the recorded order. Each reconstruction uses an isolated fresh session. No conversational or session state crosses between Arm C and Arm M.",
  "isolation_guarantee": "The OS-CSPRNG seed, the resulting arm-order map, and the per-reconstruction session_id values for both arms will be recorded at execution time in the post-execution deviation/deviation-or-record log.",
  "frozen_at_protocol_freeze": true,
  "operational_note": "This artifact contains ONLY the randomization seed and the resulting arm-order map. It does NOT contain any generated candidate information. Per PI instruction, generation artifacts are produced at execution time, not at protocol freeze."
}
```
