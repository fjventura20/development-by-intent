"""Transport extractor — Stage C successor.

Separates the five layers per SUCCESSOR-DESIGN-v0.1 §1.2:
  1. exact captured stdout bytes (preserved byte-for-byte by the caller)
  2. deterministic payload extraction (this module)
  3. schema validation (schema_validate.py)
  4. parsed candidate Action (caller)
  5. GEL processing (gel.py)

Frozen rules (v0.1):
  Rule 1: strip literal tirith banner prefix if present
  Rule 2: strip one optional outer markdown JSON code fence
  Rule 3: strip one optional session_id footer line
  Rule 4: trim exactly one leading and one trailing newline

NO JSON parsing, NO field inference, NO repair.
"""
import hashlib


TIRITH_BANNER_BYTES = (
    "⚠ tirith security scanner enabled but not available "
    "— command scanning will use pattern matching only\n"
).encode("utf-8")

JSON_FENCE_OPEN_BYTES = b"```json\n"
JSON_FENCE_CLOSE_BYTES = b"\n```"
SESSION_FOOTER_PREFIX = b"session_id: "


def extract_payload(stdout_bytes):
    """Extract payload bytes from raw stdout.

    Returns:
      {
        "status": "OK"|"MALFORMED_FENCE"|"EMPTY",
        "payload_bytes": <bytes>,
        "raw_sha256": <hex>,
        "extraction_log": [<str>, ...],
      }
    """
    raw_sha256 = hashlib.sha256(stdout_bytes).hexdigest()
    log = []
    b = stdout_bytes

    # Rule 1: tirith banner prefix
    if b.startswith(TIRITH_BANNER_BYTES):
        b = b[len(TIRITH_BANNER_BYTES):]
        log.append("rule1_banner_stripped")
    else:
        log.append("rule1_banner_not_present")

    # Rule 2: markdown JSON fence
    fence_opened = False
    fence_closed = False
    if b.startswith(JSON_FENCE_OPEN_BYTES):
        b = b[len(JSON_FENCE_OPEN_BYTES):]
        fence_opened = True
        log.append("rule2_fence_open_stripped")
    if b.endswith(JSON_FENCE_CLOSE_BYTES):
        b = b[:-len(JSON_FENCE_CLOSE_BYTES)]
        fence_closed = True
        log.append("rule2_fence_close_stripped")

    # Malformed fence: opened but not closed, or vice versa
    if fence_opened and not fence_closed:
        return {
            "status": "MALFORMED_FENCE",
            "payload_bytes": b"",
            "raw_sha256": raw_sha256,
            "extraction_log": log + ["rule2_malformed_open_without_close"],
        }
    if fence_closed and not fence_opened:
        return {
            "status": "MALFORMED_FENCE",
            "payload_bytes": b"",
            "raw_sha256": raw_sha256,
            "extraction_log": log + ["rule2_malformed_close_without_open"],
        }

    # Rule 3: session_id footer line
    if b.endswith(b"\n"):
        # Find the last newline
        last_nl = b.rfind(b"\n")
        last_line = b[last_nl + 1:]
        if last_line.startswith(SESSION_FOOTER_PREFIX):
            b = b[:last_nl]
            log.append("rule3_session_footer_stripped")
        else:
            log.append("rule3_session_footer_not_present")
    else:
        log.append("rule3_session_footer_not_present")

    # Rule 4: trim one leading and one trailing newline
    if b.startswith(b"\n"):
        b = b[1:]
        log.append("rule4_leading_newline_trimmed")
    if b.endswith(b"\n"):
        b = b[:-1]
        log.append("rule4_trailing_newline_trimmed")

    # Status: empty check
    if len(b) == 0:
        return {
            "status": "EMPTY",
            "payload_bytes": b"",
            "raw_sha256": raw_sha256,
            "extraction_log": log,
        }

    return {
        "status": "OK",
        "payload_bytes": b,
        "raw_sha256": raw_sha256,
        "extraction_log": log,
    }
