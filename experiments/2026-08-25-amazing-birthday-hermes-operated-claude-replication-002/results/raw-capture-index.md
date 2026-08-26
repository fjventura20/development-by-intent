# Raw First-Call Capture Index — Replication 002

Source transfer: `fjventura20/hermes-coordination`, branch `mailbox/main`, transfer `20260826T013000Z-behavioral-portability-claude-replication-002-result-001`.

The public experiment directory preserves the verbatim first-call prose witnesses used for scoring. The original structured JSON envelopes remain independently addressable in the public coordination repository and are bound by the returned manifest SHA-256 values.

| Turn | Source file | Git blob SHA | Manifest SHA-256 | Session |
|---|---|---|---|---|
| Reconstruction | `reconstruction.json` | `dd574595dd1a16ac60535ba8695c1746ac100a43` | `612fe7b33cf4874e0073b1cb714777dc07bd2e64695b5fb1ca97075a7b2e2201` | `b1f41015-a416-44cc-b5eb-35abc83274de` |
| Test 1 | `test-1-output.json` | `9cd24f6f6703f8368710097f7ef9a412346f4f1c` | `c9adea927245f7a561a95b9a62f4a1ec37255cdddc31c69753f38b9bc7d28b2f` | same |
| Test 2 | `test-2-output.json` | `528e9f8ecf6a28ab942da642a225e80ffc426937` | `4075710a5c6e64d64922533b7930635781fc1029ce8c0d21cdcee401ca5aad4f` | same |
| Test 3 | `test-3-output.json` | `387008f9db94f5a893688d91ef8c08c3068d4f61` | `6373bbba054e0b10f335f5da91956150ff2cc96f0177b29e4ff38359e560e07f` | same |

All four JSON envelopes report one-turn successful completion. The three test JSON envelopes report `claude-sonnet-4-6`; the reconstruction envelope includes substantive Sonnet 4.6 usage plus a small Claude Code Haiku orchestration entry. No web-search or web-fetch requests are recorded.

The operator environment record states that each JSON envelope was written on the first CLI call through shell `tee`, before stdout interpretation, and that no prompt was re-issued for capture. This capture provenance is the procedural variable replication 002 was designed to test.
