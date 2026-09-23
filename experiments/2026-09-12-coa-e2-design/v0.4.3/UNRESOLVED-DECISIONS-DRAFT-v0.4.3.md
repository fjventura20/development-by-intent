# COA-E2 v0.4.3 Unresolved Decisions

- ChatGPT/PI must review the exact pre-freeze mechanism-check evidence before
  freeze. The mechanism check exists to establish the real CLI footer channel
  and structure from which the runner parses the session ID; until that
  evidence is reviewed, the session-ID parser operates in `MECHANISM_NOT_RUN`
  mode and dry-run synthetic fixtures only.
- ChatGPT/PI must decide whether provider-bound request capture is available;
  absent that, the evidence ceiling is `P1_APPLICATION_LAYER_PASS`.
- A later three-pair blinded pilot may be designed only after a clear
  one-pair signal; no such pilot is authorized here.
- The runner currently parses the session ID from a declared CLI footer
  pattern; if the separately authorized mechanism check reveals a different
  channel or structure, the parser and the synthetic fixtures must be
  updated before freeze.
