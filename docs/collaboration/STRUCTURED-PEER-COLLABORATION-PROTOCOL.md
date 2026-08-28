# Structured Peer Collaboration Protocol

**Protocol:** SPCP 0.1.1  
**Status:** Amended pilot candidate  
**Date:** 2026-08-28  
**Participants:** Frank, ChatGPT, and Hermes Agent

## 1. Purpose

SPCP structures sustained peer reasoning between ChatGPT and Hermes without
turning either participant into an isolated worker. It preserves open-ended
proposal, criticism, disagreement, synthesis, and redirection while reducing
repeated context, mailbox polling, and reasoning-agent involvement in delivery
mechanics.

The governing idea is:

> Rich semantic conversation over a lean deterministic transport.

SPCP is an intellectual and coordination layer. It does not replace the
ChatGPT-Hermes Exchange Protocol or the Conversation-State Wrapper. Those
systems establish delivery, identity, ordering, integrity, recovery, and
idempotency. SPCP defines what a useful peer turn contains and how shared
understanding is maintained economically.

## 2. Roles

### Frank: intent owner and governor

Frank establishes objectives, priorities, constraints, and standards of
success. He resolves genuine value conflicts or scope decisions that the peers
cannot resolve. In steady-state operation he is not the mailbox courier and
should not be needed for routine receipt acknowledgements or status polling.
This does not displace the Development by Intent operating notice at transfer
`20260828T093119Z-dbi-collaboration-notice-001`; its decision gates remain
authoritative for preregistration changes, destructive actions, material scope
changes, and external publication.

### ChatGPT and Hermes: reasoning peers

ChatGPT and Hermes have equal standing in the intellectual conversation. Both
may:

- propose, challenge, question, or revise;
- introduce and evaluate evidence;
- identify methodological or operational risks;
- request deeper reasoning from the other;
- synthesize agreement and preserve disagreement;
- recommend escalation to Frank.

Different operational strengths do not create fixed silos. Either peer may
reason about design, execution, evidence, or governance when the thread needs
it.

### Gateways and bridges: deterministic transport

Transport components deliver, validate, deduplicate, acknowledge, retry, and
notify. They do not interpret evidence or generate conversational content.
Transport receipts must not consume a reasoning turn.

## 3. One thread per objective

Every collaboration has one stable `thread_id` and one clearly stated
objective. A thread may contain as many substantive turns as the problem
requires. SPCP imposes no arbitrary turn limit.

A new objective starts a new thread. Related evidence may be referenced across
threads, but unrelated objectives must not be folded into the same state merely
because they use the same mailbox.

Thread status is one of:

- `ACTIVE` — substantive peer reasoning is in progress;
- `WAITING` — a named actor or external event is expected;
- `BLOCKED` — progress requires a recorded dependency or Frank's decision;
- `CLOSED` — the completion conditions are satisfied;
- `SUPERSEDED` — a named successor thread replaces this thread.

These statuses describe the intellectual and coordination lifecycle. They are
independent of the Exchange Protocol transfer states (`pending`, `processing`,
`completed`, and `failed`). A thread may be `CLOSED` while its final delivery
package is still `processing`, or `ACTIVE` while one transfer is `failed`. The
two state machines are observed together but are not synchronized.

## 4. Compact shared state

Each peer thread has one canonical `STATE.md`. It captures the shared
intellectual state of the conversation: what has been concluded, what is
disputed, what evidence is in play, and what should happen next. It is distinct
from the Conversation-State Wrapper's
`~/.hermes/state/conversations/<conversation_id>.json`, which is execution
control state for a multi-turn dialogue. `STATE.md` may reference wrapper state
by `conversation_id` and `current_turn` but never edits it; the wrapper edits
its own state and never edits `STATE.md`.

`STATE.md` is a checkpoint, not a transcript. It contains:

- objective and completion conditions;
- settled conclusions;
- active evidence references;
- open questions;
- explicitly recorded disagreements;
- the next expected action and actor;
- the last accepted substantive message;
- a monotonically increasing `state_version`.

`next_actor` means the peer expected to produce the next substantive message.
It is not the wrapper's execution-level `expected_actor` field.

The target size is 1,000 words or fewer. Compression follows the archival rules
in section 8.

State changes are explicit. A sender proposes a state delta. The receiver
accepts it, corrects it, or records a disagreement. No agent may silently turn
a proposal into consensus or erase a dissenting position.

## 5. Substantive peer messages

Every peer message carries a small envelope:

```yaml
protocol: spcp-0.1.1
thread_id: example-thread-001
message_id: chatgpt-004
parent_message_id: hermes-003
sender: ChatGPT
message_type: challenge
state_version_read: 3
response_required: true
depth: standard
summary: One-sentence description of the new contribution
artifact_refs: []
```

Allowed `message_type` values are:

- `proposal`
- `challenge`
- `question`
- `evidence`
- `decision`
- `synthesis`
- `blocker`
- `delta-ack`

The message body contains only the sections that add value:

1. **New contribution** — what changed since the parent turn.
2. **Reasoning or evidence** — why the contribution matters.
3. **Requested response** — one primary question, decision, or action. Required
   mechanical follow-ons may be listed under `### Mechanical follow-ons` so
   they remain explicit but visibly separate from the intellectual response.
   Follow-ons must not crowd out or substitute for the primary response.
4. **Proposed state delta** — exact additions, changes, or removals to
   `STATE.md`.

Natural dialogue is encouraged. The structure makes the delta visible; it does
not prescribe the conclusion.

## 6. Delta-only rule

A peer reads, in order:

1. the current `STATE.md`;
2. the parent message;
3. the specific messages referenced by `parent_message_id`, `artifact_refs`,
   or any disagreement ID or decision ID mentioned in the parent;
4. older messages only when the first three do not resolve an ambiguity, and
   then only the specific older messages needed—not the whole archive.

Messages reference durable artifacts by repository, ref or commit, and path.
They do not paste an artifact merely to prove it exists. A previous argument is
referenced by message ID rather than restated unless new reasoning changes it.

A message with no new reasoning, evidence, decision, disagreement, question,
or requested action is transport status and must not invoke a reasoning peer.

The full envelope is required when a message introduces new reasoning,
evidence, decisions, disagreements, or actionable questions. A message used
only to accept a proposed state delta may use a minimal envelope containing
`protocol`, `thread_id`, `message_id`, `parent_message_id`, `sender`,
`message_type: delta-ack`, and `state_version_read`. The full envelope is the
default, not a tax on every line of dialogue.

## 7. Disagreement and decision discipline

Disagreement is a productive state, not a transport failure. `STATE.md` records
each unresolved disagreement with:

- a stable disagreement ID;
- the exact question;
- each peer's current position;
- the evidence that could resolve it;
- the current resolution owner.

A disagreement ends only when:

- both peers accept a resolution;
- both peers precisely characterize the remaining difference and agree it is
  not blocking;
- new evidence is commissioned;
- Frank makes the governing decision.

Decisions record their rationale and the evidence available at the time. A
later decision may supersede an earlier one but must reference it explicitly.

## 8. Checkpoints and compression

A synthesis checkpoint occurs when any of these is true:

- approximately five substantive turns have occurred since the last checkpoint;
- `STATE.md` approaches 1,000 words;
- the active question changes;
- a major decision closes a phase;
- either peer detects repeated reasoning or loss of shared context.

One peer proposes a synthesis of settled conclusions, open disagreements, and
the next action. The other peer approves or corrects it. After acceptance, the
state version increments and earlier messages become archival context rather
than required reading.

If state exceeds 1,000 words, settled detail moves to a referenced
`archive/STATE-v<N>-archived.md` file, hash-bound to the state version that
introduced it. Canonical `STATE.md` keeps current conclusions, active evidence,
open questions, disagreements, and the next action. Inline compression without
archival is permitted only for transcript restatement—not for a decision,
dissenting position, or evidence reference.

## 9. Token-efficiency rules

These rules remove redundancy without limiting intellectual depth:

- Standard messages target 500-1,000 tokens.
- `depth: deep` explicitly permits a longer analysis when the evidence needs it.
- Each message has one primary requested response; mechanical follow-ons remain
  visibly separate.
- Full history is not restated.
- Settled material is referenced from `STATE.md`.
- No model is invoked when the canonical remote state has not changed.
- Delivery acknowledgements, commit detection, and retries are machine events.
- A peer may continue for unlimited substantive turns while new reasoning is
  emerging.

The relevant efficiency measure is the proportion of reasoning turns that add
new intellectual value, not the raw number of turns.

## 10. Interaction with existing exchange machinery

SPCP uses the current exchange package, manifest, hashing, marker, and durable
Git commit rules unchanged during the pilot.

Mapping:

| Existing mechanism | SPCP responsibility |
|---|---|
| Exchange manifest | Delivery identity and file integrity |
| Conversation-State Wrapper | Turn identity, parentage, recovery, and no-fork |
| `STATE.md` | Compact shared intellectual state |
| Peer message | New reasoning, evidence, decision, or question |
| Bridge acknowledgement | Delivery only; no reasoning turn |

SPCP metadata may initially travel inside Markdown payloads. No manifest-schema
change is required for the pilot. Schema integration should be considered only
after the protocol proves useful.

## 11. Completion and escalation

A thread closes when its recorded completion conditions are satisfied and both
peers accept the closing synthesis. It does not close merely because a fixed
number of turns elapsed.

Escalation to Frank is appropriate when:

- the objective or scope must change materially, including any change to a
  frozen experimental protocol, preregistered research design, or standing
  governance mandate;
- a value or authority conflict cannot be resolved from existing governance;
- continuing requires new credentials, spending, or external authority;
- the peers agree that additional dialogue has stopped producing new value;
- a destructive, irreversible, safety-sensitive, or externally consequential
  action is proposed;
- publication, third-party contact, or a commitment in Frank's name is
  proposed.

## 12. Pilot acceptance criteria

The pilot passes when one real collaboration thread demonstrates:

1. At least 80% of reasoning-agent messages contain new reasoning, evidence,
   decisions, disagreements, or actionable questions.
2. Frank performs no mailbox receipt polling or acknowledgement relay.
3. No substantive message is executed twice.
4. Every unresolved disagreement is visible in `STATE.md`.
5. Every final decision references its evidence.
6. Both peers report that the structure preserved or improved conversational
   synergy.
7. Transport events are distinguishable from semantic turns in the durable
   record.

For criterion 1, each peer classifies its own outbound messages. Either peer
may ask Frank to classify a disputed message. A classification dispute is
recorded under section 7 rather than silently resolved.

## 13. Pilot boundaries

The pilot does not modify an already frozen experimental protocol, regenerate
frozen artifacts, or authorize model execution. Its first task is peer review
of SPCP itself. After both peers approve a candidate, they select a live thread
on which to test it.
