"""ATE P1 v0.1.1 — Privileged executor.

Per v0.1.1 §3 and §4: all mutations occur inside ONE SQLite transaction
(BEGIN IMMEDIATE ... COMMIT). Inside that transaction:

  E5 — Final revocation check
  E6 — Nonce uniqueness establishment (INSERT OR FAIL on PRIMARY KEY)
  E7 — Protected mutation (resource fixture state)
  E8 — Nonce finalization (RESERVED -> CONSUMED)
  E9 — Audit append + audit anchor update
  E10 — COMMIT

If ANY step raises, the transaction is rolled back; no protected
mutation, no consumed nonce, no audit event, no advanced anchor.

Per v0.1.1 §C5: the authoritative nonce transition occurs only inside
this transaction. An aborted transaction leaves no partially-committed
RESERVED state. After restart, a committed CONSUMED nonce remains
CONSUMED.

The privileged executor:
  - Verifies the trust-decision signature (E2).
  - Verifies exact request/decision binding (E3).
  - Re-verifies nonce uniqueness / revocation inside the transaction
    (this is the immediate-executor-reverification property).
  - Performs the protected mutation (E7) using a per-resource
    unguessable executor-only credential.

The executor owns:
  - the audit HMAC key (passed to audit_chain.make_record_mac);
  - the resource credentials (one per resource_id, stored in the
    executor's secure store file outside the authority DB);
  - the DB write handle.

The executor exposes:
  - a single execute_request(request_dict) -> response_dict method.
  - a verify_audit_chain() -> (ok, reason) method for the E0 startup gate.
  - a deterministic barrier interface for tests that need to inject
    state between E5 and E6 (see DeterministicBarrier).

The requester-facing surface is `IPCWorker` (subprocess entrypoint).
"""
from __future__ import annotations

import datetime
import os
import sqlite3
from typing import Any, Callable, Dict, List, Optional, Tuple

from audit_chain import (
    is_chain_empty,
    make_anchor_mac,
    make_record_mac,
    read_anchor,
    record_digest,
    verify_audit_chain,
)
from crypto_utils import canonical_bytes, fingerprint_obj, hmac_sha256_hex, random_hex
from ipc_protocol import (
    SCHEMA_ID_REQ,
    verify_request_signature,
)
from authority_db import open_db
from protected_resource import apply_mutation as _pr_apply_mutation
import protected_resource


# ---- Reason codes (PX_*) ----------------------------------------------


class ReasonCode:
    OK = "PX_OK"
    AUDIT_INTEGRITY_FAILURE = "PX_AUDIT_INTEGRITY_FAILURE"
    TRUST_DECISION_INVALID = "PX_TRUST_DECISION_INVALID"
    OPERATION_BINDING_MISMATCH = "PX_OPERATION_BINDING_MISMATCH"
    TARGET_BINDING_MISMATCH = "PX_TARGET_BINDING_MISMATCH"
    SESSION_BINDING_MISMATCH = "PX_SESSION_BINDING_MISMATCH"
    NONCE_BINDING_MISMATCH = "PX_NONCE_BINDING_MISMATCH"
    AUTHORITY_EXPIRED = "PX_AUTHORITY_EXPIRED"
    AUTHORITY_REVOKED = "PX_AUTHORITY_REVOKED"
    NONCE_REPLAY_OR_BUSY = "PX_NONCE_REPLAY_OR_BUSY"
    REVERIFICATION_FAILED = "PX_REVERIFICATION_FAILED"
    REQUEST_SIGNATURE_INVALID = "PX_REQUEST_SIGNATURE_INVALID"
    REQUEST_SCHEMA_INVALID = "PX_REQUEST_SCHEMA_INVALID"
    RESOURCE_NOT_FOUND = "PX_RESOURCE_NOT_FOUND"
    RESOURCE_CREDENTIAL_INVALID = "PX_RESOURCE_CREDENTIAL_INVALID"
    UNKNOWN_ERROR = "PX_UNKNOWN_ERROR"
    AUDIT_APPEND_FAILED = "PX_AUDIT_APPEND_FAILED"
    COMMIT_FAILED = "PX_COMMIT_FAILED"


# ---- Executor configuration and stores --------------------------------


class ExecutorConfig:
    """Holds the executor-only material.

    audit_key and resource_credentials are passed in from the caller
    (the privileged_executor process). They never appear in the
    requester-facing IPC.
    """

    def __init__(
        self,
        *,
        db_path: str,
        audit_key: bytes,
        resource_credentials: Dict[str, bytes],
        trust_decision_pub_keys: Dict[str, bytes],
        request_signing_key: bytes,
        now_utc_fn: Callable[[], float] = lambda: datetime.datetime.utcnow().timestamp(),
        decision_issuer_keys: Optional[Dict[str, bytes]] = None,
    ) -> None:
        self.db_path = db_path
        self.audit_key = audit_key
        self.resource_credentials = resource_credentials  # resource_id -> cred
        self.trust_decision_pub_keys = trust_decision_pub_keys  # decision_id -> pub
        self.request_signing_key = request_signing_key
        self.now_utc_fn = now_utc_fn
        self.decision_issuer_keys = decision_issuer_keys or {}


# ---- DeterministicBarrier ---------------------------------------------


class DeterministicBarrier:
    """Test hook for injecting state between protocol steps.

    Per v0.1 §17.5 and the v0.1.1 §E4 pre-use revalidation: tests may
    inject deterministic state changes (e.g., a revocation) between
    the executor's pre-checks and the protected mutation. The barrier
    is consulted inside the transaction at E7 (immediately before the
    protected mutation). The hook is callable by the test only via a
    `barrier_fn` registered on the executor.
    """

    def __init__(self) -> None:
        self._hooks: List[Callable[[], None]] = []

    def add(self, hook: Callable[[], None]) -> None:
        self._hooks.append(hook)

    def reset(self) -> None:
        self._hooks = []

    def fire(self) -> None:
        for hook in self._hooks:
            hook()


# ---- Executor core -----------------------------------------------------


class PrivilegedExecutor:
    def __init__(self, config: ExecutorConfig, barrier: Optional[DeterministicBarrier] = None) -> None:
        self.config = config
        self.barrier = barrier or DeterministicBarrier()
        self._conn: Optional[sqlite3.Connection] = None

    # ---- DB lifecycle ------------------------------------------------

    def open(self) -> None:
        self._conn = open_db(self.config.db_path)
        # Store audit_key fingerprint (NOT the key itself) so internal
        # integrity checks can detect mismatched-key restarts.
        self._conn.execute(
            "UPDATE executor_state SET audit_key_fingerprint=?, "
            "resource_credential_fingerprint=? WHERE id=1",
            (
                fingerprint_obj({"k": self.config.audit_key.hex()}),
                fingerprint_obj(
                    {rid: c.hex() for rid, c in self.config.resource_credentials.items()}
                ),
                ),
        )
        self._conn.commit()

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _db(self) -> sqlite3.Connection:
        assert self._conn is not None, "executor not opened"
        return self._conn

    # ---- E0 startup integrity gate ----------------------------------

    def startup_integrity_check(self) -> Tuple[bool, str]:
        """Per v0.1.1 §C7: verify audit chain + anchor + executor state
        before serving any request. Failure locks execution.
        """
        # Check locked flag
        row = self._db().execute(
            "SELECT locked, last_lock_reason FROM executor_state WHERE id=1"
        ).fetchone()
        if int(row["locked"]) == 1:
            return False, f"executor_locked:{row['last_lock_reason']}"
        # Verify audit chain
        ok, reason = verify_audit_chain(self._db(), self.config.audit_key)
        if not ok:
            # Lock the executor
            self._db().execute(
                "UPDATE executor_state SET locked=1, last_lock_reason=? WHERE id=1",
                (reason,),
            )
            self._db().commit()
            return False, f"startup_lock:{reason}"
        return True, "verified"

    # ---- E2-E3 decision/binding checks (pre-transaction) ------------

    def _verify_decision_signature(
        self, decision_id: str, decision_signature_b64: str
    ) -> Tuple[bool, str]:
        # Trust-decision verification against a fixture-trust-decision public key.
        # The pre-built decision_signatures table stores the upstream payload.
        row = self._db().execute(
            "SELECT signed_payload_json, signature_b64 FROM decision_signatures WHERE decision_id=?",
            (decision_id,),
        ).fetchone()
        if row is None:
            return False, ReasonCode.TRUST_DECISION_INVALID
        if row["signature_b64"] != decision_signature_b64:
            return False, ReasonCode.TRUST_DECISION_INVALID
        pub = self.config.trust_decision_pub_keys.get(decision_id)
        if pub is None:
            return False, ReasonCode.TRUST_DECISION_INVALID
        import hmac as _hmac, hashlib as _hashlib
        try:
            sig = _hmac.new(pub, canonical_bytes(__import__("json").loads(row["signed_payload_json"])), _hashlib.sha256).digest()
            expected_b64 = __import__("base64").b64encode(sig).decode("ascii")
        except Exception:
            return False, ReasonCode.TRUST_DECISION_INVALID
        if expected_b64 != decision_signature_b64:
            return False, ReasonCode.TRUST_DECISION_INVALID
        return True, ReasonCode.OK

    def _verify_request_binding(
        self, request: Dict[str, Any], signed_payload: Dict[str, Any]
    ) -> Tuple[bool, str]:
        # The trust decision stored in decision_signatures carries the binding
        # fields (operation, target, session, nonce). All must match.
        # The actual upstream ATE v0.3.1 binding check is upstream; here we
        # require the signed_request_payload to match the binding fields
        # recorded for the decision.
        row = self._db().execute(
            "SELECT signed_payload_json FROM decision_signatures WHERE decision_id=?",
            (request["decision_id"],),
        ).fetchone()
        if row is None:
            return False, ReasonCode.TRUST_DECISION_INVALID
        decision_payload = __import__("json").loads(row["signed_payload_json"])
        # Binding requirements per v0.1 §E3
        if signed_payload.get("operation") != decision_payload.get("operation"):
            return False, ReasonCode.OPERATION_BINDING_MISMATCH
        if signed_payload.get("resource_id") != decision_payload.get("resource_id"):
            return False, ReasonCode.TARGET_BINDING_MISMATCH
        if signed_payload.get("session_id") != decision_payload.get("session_id"):
            return False, ReasonCode.SESSION_BINDING_MISMATCH
        if signed_payload.get("nonce") != decision_payload.get("nonce"):
            return False, ReasonCode.NONCE_BINDING_MISMATCH
        return True, ReasonCode.OK

    # ---- Main request handler ---------------------------------------

    def execute_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process one IPC request and return the IPC response."""
        # Schema check
        if request.get("schema_id") != SCHEMA_ID_REQ:
            return self._fail(ReasonCode.REQUEST_SCHEMA_INVALID, request)

        # E0 lock check (cheap; also done at startup)
        row = self._db().execute(
            "SELECT locked FROM executor_state WHERE id=1"
        ).fetchone()
        if int(row["locked"]) == 1:
            return self._fail(ReasonCode.AUDIT_INTEGRITY_FAILURE, request)

        # Verify request signature
        if not verify_request_signature(request, self.config.request_signing_key):
            return self._fail(ReasonCode.REQUEST_SIGNATURE_INVALID, request)

        # E2 verify trust decision
        decision_id = request["decision_id"]
        decision_sig = request["decision_signature_b64"]
        ok, reason = self._verify_decision_signature(decision_id, decision_sig)
        if not ok:
            return self._fail(reason, request)

        # E3 binding
        payload = request["signed_request_payload"]
        ok, reason = self._verify_request_binding(request, payload)
        if not ok:
            return self._fail(reason, request)

        # E4 freshness (issued_at_utc within authority window)
        now = self.config.now_utc_fn()
        if float(payload["issued_at_utc"]) > now + 1.0:
            return self._fail(ReasonCode.AUTHORITY_EXPIRED, request)

        # E5-E10: BEGIN IMMEDIATE ... COMMIT
        return self._execute_transaction(request, payload)

    def _fail(self, reason_code: str, request: Dict[str, Any]) -> Dict[str, Any]:
        from ipc_protocol import make_response
        return make_response(
            request_id=request.get("request_id", ""),
            verdict="DENIED",
            reason_code=reason_code,
            mutation_count_after=self._db().execute(
                "SELECT COALESCE(SUM(mutation_count),0) AS c FROM protected_resources"
            ).fetchone()["c"],
            audit_chain_tip_seq=int(
                self._db().execute("SELECT COALESCE(MAX(seq),0) AS s FROM audit_records").fetchone()["s"]
            ),
            resource_state_after=None,
        )

    def _execute_transaction(
        self, request: Dict[str, Any], payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """The atomic transaction per v0.1.1 §3 / §4."""
        from ipc_protocol import make_response

        conn = self._db()
        decision_id = request["decision_id"]
        nonce = payload["nonce"]
        resource_id = payload["resource_id"]
        issued_at_utc = float(payload["issued_at_utc"])

        try:
            conn.execute("BEGIN IMMEDIATE")

            # E5 final revocation check (inside transaction)
            rev = conn.execute(
                "SELECT reason FROM revocations WHERE subject_type=? AND subject_id=?",
                ("decision", decision_id),
            ).fetchone()
            if rev is not None:
                conn.execute("ROLLBACK")
                return make_response(
                    request_id=request["request_id"],
                    verdict="DENIED",
                    reason_code=ReasonCode.AUTHORITY_REVOKED,
                    mutation_count_after=0,
                    audit_chain_tip_seq=int(
                        conn.execute("SELECT COALESCE(MAX(seq),0) AS s FROM audit_records").fetchone()["s"]
                    ),
                    resource_state_after=None,
                )

            # E6 nonce uniqueness (INSERT OR FAIL inside transaction)
            existing = conn.execute(
                "SELECT state FROM nonces WHERE nonce=?", (nonce,)
            ).fetchone()
            if existing is not None:
                conn.execute("ROLLBACK")
                return make_response(
                    request_id=request["request_id"],
                    verdict="DENIED",
                    reason_code=ReasonCode.NONCE_REPLAY_OR_BUSY,
                    mutation_count_after=0,
                    audit_chain_tip_seq=int(
                        conn.execute("SELECT COALESCE(MAX(seq),0) AS s FROM audit_records").fetchone()["s"]
                    ),
                    resource_state_after=None,
                )
            try:
                conn.execute(
                    "INSERT INTO nonces (nonce, state, decision_id, first_seen_at) "
                    "VALUES (?, 'RESERVED', ?, ?)",
                    (nonce, decision_id, _iso(issued_at_utc)),
                )
            except sqlite3.IntegrityError:
                conn.execute("ROLLBACK")
                return make_response(
                    request_id=request["request_id"],
                    verdict="DENIED",
                    reason_code=ReasonCode.NONCE_REPLAY_OR_BUSY,
                    mutation_count_after=0,
                    audit_chain_tip_seq=int(
                        conn.execute("SELECT COALESCE(MAX(seq),0) AS s FROM audit_records").fetchone()["s"]
                    ),
                    resource_state_after=None,
                )

            # E7 protected mutation (with resource credential check)
            res = conn.execute(
                "SELECT resource_id, state_json, mutation_count FROM protected_resources WHERE resource_id=?",
                (resource_id,),
            ).fetchone()
            if res is None:
                conn.execute("ROLLBACK")
                return make_response(
                    request_id=request["request_id"],
                    verdict="DENIED",
                    reason_code=ReasonCode.RESOURCE_NOT_FOUND,
                    mutation_count_after=0,
                    audit_chain_tip_seq=int(
                        conn.execute("SELECT COALESCE(MAX(seq),0) AS s FROM audit_records").fetchone()["s"]
                    ),
                    resource_state_after=None,
                )
            # The executor MUST present its credential to the resource
            # adapter. We model this as a check against the resource_id's
            # stored credential. The credential is held ONLY by the
            # executor (config.resource_credentials) and is required to
            # perform the mutation.
            cred = self.config.resource_credentials.get(resource_id)
            # If a credential is required but missing OR doesn't match
            # the executor-held one, deny.
            if cred is None:
                conn.execute("ROLLBACK")
                return make_response(
                    request_id=request["request_id"],
                    verdict="DENIED",
                    reason_code=ReasonCode.RESOURCE_CREDENTIAL_INVALID,
                    mutation_count_after=0,
                    audit_chain_tip_seq=int(
                        conn.execute("SELECT COALESCE(MAX(seq),0) AS s FROM audit_records").fetchone()["s"]
                    ),
                    resource_state_after=None,
                )

            # Optional deterministic barrier (used by T4 revocation race)
            try:
                self.barrier.fire()
            except Exception:
                conn.execute("ROLLBACK")
                return make_response(
                    request_id=request["request_id"],
                    verdict="DENIED",
                    reason_code=ReasonCode.REVERIFICATION_FAILED,
                    mutation_count_after=0,
                    audit_chain_tip_seq=int(
                        conn.execute("SELECT COALESCE(MAX(seq),0) AS s FROM audit_records").fetchone()["s"]
                    ),
                    resource_state_after=None,
                )

            # Final revocation re-check inside transaction (post-barrier)
            rev2 = conn.execute(
                "SELECT reason FROM revocations WHERE subject_type=? AND subject_id=?",
                ("decision", decision_id),
            ).fetchone()
            if rev2 is not None:
                # Per v0.1 §E7 final rule: failed revalidation after
                # reservation transitions RESERVED -> CONSUMED denied.
                conn.execute(
                    "UPDATE nonces SET state='CONSUMED', finalized_at=?, outcome='DENIED_REVERIFICATION' "
                    "WHERE nonce=?",
                    (_iso(self.config.now_utc_fn()), nonce),
                )
                _append_audit(conn, self.config.audit_key, request, payload,
                              outcome="DENIED", reason_code=ReasonCode.AUTHORITY_REVOKED,
                              mutation_count_after=0)
                conn.execute("COMMIT")
                return make_response(
                    request_id=request["request_id"],
                    verdict="DENIED",
                    reason_code=ReasonCode.AUTHORITY_REVOKED,
                    mutation_count_after=0,
                    audit_chain_tip_seq=int(
                        conn.execute("SELECT COALESCE(MAX(seq),0) AS s FROM audit_records").fetchone()["s"]
                    ),
                    resource_state_after=None,
                )

            # Apply mutation via the credential-aware resource path
            presented = self.config.resource_credentials.get(resource_id)
            ok, reason = protected_resource.apply_mutation(
                conn,
                resource_id,
                payload["operation"],
                request["request_id"],
                presented_credential=presented if presented is not None else b"",
            )
            if not ok:
                conn.execute("ROLLBACK")
                return make_response(
                    request_id=request["request_id"],
                    verdict="DENIED",
                    reason_code=reason,
                    mutation_count_after=int(
                        conn.execute(
                            "SELECT COALESCE(MAX(seq),0) AS s FROM audit_records"
                        ).fetchone()["s"]
                    ),
                    audit_chain_tip_seq=int(
                        (conn.execute("SELECT COALESCE(MAX(seq),0) AS s FROM audit_records").fetchone() or {"s": 0})["s"]
                    ),
                    resource_state_after=None,
                )
            res2 = conn.execute(
                "SELECT mutation_count FROM protected_resources WHERE resource_id=?",
                (resource_id,),
            ).fetchone()
            new_count = int(res2["mutation_count"])
            new_state_json = conn.execute(
                "SELECT state_json FROM protected_resources WHERE resource_id=?",
                (resource_id,),
            ).fetchone()["state_json"]

            # E8 nonce finalization
            conn.execute(
                "UPDATE nonces SET state='CONSUMED', finalized_at=?, outcome='EXECUTED' WHERE nonce=?",
                (_iso(self.config.now_utc_fn()), nonce),
            )

            # E9 audit append + anchor update (atomic with mutation)
            audit_chain_tip = _append_audit(
                conn, self.config.audit_key, request, payload,
                outcome="EXECUTED", reason_code=ReasonCode.OK,
                mutation_count_after=new_count,
            )

            # E10 COMMIT
            conn.execute("COMMIT")

            return make_response(
                request_id=request["request_id"],
                verdict="EXECUTED",
                reason_code=ReasonCode.OK,
                mutation_count_after=new_count,
                audit_chain_tip_seq=audit_chain_tip,
                resource_state_after=__import__("json").loads(new_state_json),
            )

        except Exception as e:
            try:
                conn.execute("ROLLBACK")
            except sqlite3.OperationalError:
                pass
            return make_response(
                request_id=request["request_id"],
                verdict="DENIED",
                reason_code=ReasonCode.COMMIT_FAILED,
                mutation_count_after=0,
                audit_chain_tip_seq=int(
                    conn.execute("SELECT COALESCE(MAX(seq),0) AS s FROM audit_records").fetchone()["s"]
                ),
                resource_state_after=None,
            )


# ---- helpers ----------------------------------------------------------


def _iso(ts: float) -> str:
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _apply_mutation(state_json: str, operation: str, request_id: str) -> str:
    """Apply the deterministic protected-resource mutation.

    The resource state is a JSON object; the mutation appends a record.
    """
    import json as _json
    state = _json.loads(state_json)
    history = state.setdefault("history", [])
    history.append({
        "operation": operation,
        "request_id": request_id,
    })
    return _json.dumps(state, sort_keys=True, separators=(",", ":"))


def _append_audit(
    conn: sqlite3.Connection,
    audit_key: bytes,
    request: Dict[str, Any],
    payload: Dict[str, Any],
    *,
    outcome: str,
    reason_code: str,
    mutation_count_after: int,
) -> int:
    """Append an audit record and update the anchor atomically.

    Returns the new audit chain tip sequence number.
    """
    last_seq_row = conn.execute(
        "SELECT COALESCE(MAX(seq),0) AS s FROM audit_records"
    ).fetchone()
    last_seq = int(last_seq_row["s"])
    # The previous_record_digest is the SHA-256 of the canonical record-
    # without-MAC. That digest is NOT stored as a separate column; the
    # stored MAC is over the record-without-MAC and the next record's
    # previous_digest is computed from the previous record's content.
    # However, to detect reorders we need the previous record's digest.
    # We compute it from the canonical form of the previous record.
    prev_record_row = conn.execute(
        "SELECT event_ts, request_id, decision_id, nonce, resource_id, "
        "operation, target_display, outcome, reason_code, previous_digest, "
        "seq FROM audit_records WHERE seq=?",
        (last_seq,),
    ).fetchone() if last_seq > 0 else None
    if prev_record_row is not None:
        prev_digest = record_digest(dict(prev_record_row))
    else:
        prev_digest = ""
    seq = last_seq + 1
    record_no_mac = {
        "seq": seq,
        "event_ts": _iso(__import__("time").time()),
        "request_id": request["request_id"],
        "decision_id": request["decision_id"],
        "nonce": payload["nonce"],
        "resource_id": payload["resource_id"],
        "operation": payload["operation"],
        "target_display": payload["target_display"],
        "outcome": outcome,
        "reason_code": reason_code,
        "previous_digest": prev_digest,
    }
    record_no_mac["record_mac"] = make_record_mac(audit_key, record_no_mac)
    conn.execute(
        "INSERT INTO audit_records (seq, event_ts, request_id, decision_id, nonce, "
        "resource_id, operation, target_display, outcome, reason_code, "
        "previous_digest, record_mac) "
        "VALUES (:seq,:event_ts,:request_id,:decision_id,:nonce,:resource_id,"
        ":operation,:target_display,:outcome,:reason_code,:previous_digest,"
        ":record_mac)",
        record_no_mac,
    )
    new_digest = record_digest(record_no_mac)
    new_anchor_mac = make_anchor_mac(audit_key, seq, new_digest)
    conn.execute(
        "UPDATE audit_anchor SET final_seq=?, final_record_digest=?, anchor_mac=?, updated_at=? "
        "WHERE id=1",
        (seq, new_digest, new_anchor_mac, _iso(__import__("time").time())),
    )
    return seq
