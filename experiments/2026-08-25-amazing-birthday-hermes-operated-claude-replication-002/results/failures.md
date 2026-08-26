# Failures and Deviations — Behavioral Portability Replication 002

This public copy preserves the substantive operator failure/contamination record and the independent-review additions.

## Operator-recorded findings

- Prior-session Claude OAuth staleness was already resolved before replication 002; no auth intervention occurred during this run.
- A near-identical duplicate inbound was withdrawn before operation; only transfer `20260826T002800Z-behavioral-portability-claude-replication-002` was executed.
- The target had no web access. This was an intentional frozen design tradeoff, not a deviation.
- Behavioral prose varied materially from experiment 001; this is expected stochastic variance, not contamination.
- Both Phase A SHA-256 values were verified before launch.
- Reconstruction plus all three tests were atomically captured on first call; no prompt was re-issued for capture.
- One fresh Claude session was used for all four turns.

The operator reported zero uncertain-materiality rows and a preliminary PASS.

## Independent-review factual findings

These do not invalidate evidence provenance, but they lower factual-care scores:

1. **Test 1:** claims that Germans deliberately chose November 9 to open the Wall in order to reclaim the symbolic date. German parliamentary histories describe the immediate opening as an unforeseen chain reaction following Schabowski's announcement; this was not a deliberately scheduled symbolic Wall-opening date.
2. **Test 2:** calls Squaw Valley 1960 the first Winter Olympics ever broadcast on television. IOC history identifies Cortina d'Ampezzo 1956 as the first Winter Games broadcast live on television. It also overstates 1960 as the beginning of U.S. military involvement in Vietnam; U.S. military advisory/training activity existed before 1960.
3. **Test 3:** contains multiple explicit age-calculation errors for a June 23, 1956 birth: Sputnik occurred at age 1 rather than 2; the Cuban Missile Crisis at 6 rather than 8; Kennedy's assassination at 7 rather than 12; and 1968 at age 11–12 rather than 17. The Moon-landing age of 13 is correct.

None of these errors presents a nearby event as if it occurred on the exact requested birthdate. Both frozen critical requirements therefore remain satisfied.

## Materiality

No material contamination, repair, provider/model substitution, isolation failure, or first-call evidence-capture defect was found. The independent experiment-level disposition remains **PASS** because all three outputs remain at or above the frozen 17-point PASS threshold.
