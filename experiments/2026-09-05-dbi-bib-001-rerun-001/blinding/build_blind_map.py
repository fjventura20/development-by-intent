#!/usr/bin/env python3
"""
DBI-BIB-001-RERUN-001 — Blind Map Construction
Gate 2 of the Evaluation Phase.

Constructs the fresh blind map per EVALUATION-PROCEDURE.md §'Blind candidate construction'
and §'Randomization':
  - 60 opaque blind IDs (UUID4)
  - two independently generated permutations (one per evaluator)
  - private mapping file (blind-map.json) preserved separately from evaluator-visible material
  - explicit new seed for each permutation (seed_A, seed_B)
  - records hashes/provenance

The mapping is preserved separately in blinding/blind-map.json.
The two orderings are preserved in blinding/evaluator-A-order.json and blinding/evaluator-B-order.json.
No mapping is shipped to either evaluator before both score sets are locked.
"""
import hashlib
import json
import random
import uuid
from pathlib import Path

# ---- Fixed inputs ----
EVDIR = Path("/home/fjventura20/devProjectsU/development-by-intent/experiments/2026-09-05-dbi-bib-001-rerun-001")
RUNS = EVDIR / "runs"
TEST_PROMPTS = {
    "T1": "Birthdate February 20, 1952",
    "T2": "Birthdate June 23, 1956",
    "T3": "Birthdate February 29, 1960",
    "T4": "Birthdate November 9, 1989",
    "T5": "Birthdate August 24, 1931",
}

RECON_IDS = ["R1", "R2", "R3", "R4", "R5", "R6"]
BLOCK_IDS = ["A", "B"]
TEST_IDS = ["T1", "T2", "T3", "T4", "T5"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    # Verify every candidate raw file is present
    candidates = []
    missing = []
    for r in RECON_IDS:
        for b in BLOCK_IDS:
            for t in TEST_IDS:
                p = RUNS / r / "captures" / b / f"{t}.raw.json"
                if not p.is_file() or p.stat().st_size == 0:
                    missing.append({"reconstruction_id": r, "block": b, "test_id": t, "raw_path": str(p)})
                    continue
                sha = sha256_file(p)
                candidates.append({
                    "reconstruction_id": r,
                    "block": b,
                    "test_id": t,
                    "raw_path": str(p),
                    "raw_size_bytes": p.stat().st_size,
                    "raw_sha256": sha,
                    "test_prompt": TEST_PROMPTS[t],
                    "test_prompt_sha256": hashlib.sha256(TEST_PROMPTS[t].encode("utf-8")).hexdigest(),
                })

    if missing:
        print("MISSING candidates — aborting blind map construction:")
        for m in missing:
            print("  ", m)
        raise SystemExit(1)

    if len(candidates) != 60:
        print(f"Expected 60 candidates, found {len(candidates)} — aborting.")
        raise SystemExit(1)

    # ---- Blind ID assignment (UUID4) ----
    # Use uuid.uuid4() (NOT uuid5 / uuid3) to ensure no provenance correlation.
    # We assign blind IDs in canonical R/B/T order, then drop the order by randomizing the master mapping.
    rng_master = random.SystemRandom()  # OS CSPRNG
    master_seed = rng_master.getrandbits(256)  # 256-bit from /dev/urandom

    # Master mapping: list of (blind_id, candidate) in a randomly permuted order.
    # The blind ID itself is fresh UUID4 (no provenance info).
    blind_assignments = []
    for c in candidates:
        bid = str(uuid.uuid4())  # fresh UUID4
        blind_assignments.append({"blind_id": bid, **c})

    # Randomly permute the master list to remove ordering bias
    perm_rng = random.Random(master_seed)
    perm_rng.shuffle(blind_assignments)

    blind_map = {
        "schema_version": "0.1",
        "record_kind": "blind-map",
        "experiment_id": "DBI-BIB-001-RERUN-001",
        "constructed_at_utc": "2026-09-06T09:30:00Z",
        "constructed_by": "Hermes (operator) — Gate 2 / Evaluation Phase",
        "candidate_count": len(blind_assignments),
        "blind_id_algorithm": "uuid.uuid4 (Python stdlib; OS CSPRNG)",
        "blind_id_ordering_seed": f"{master_seed:064x}",
        "blind_id_ordering_seed_source": "random.SystemRandom().getrandbits(256) — OS entropy (/dev/urandom)",
        "blind_id_ordering_algorithm": "Fisher-Yates shuffle over the 60 (UUID4, candidate) tuples, seeded with master_seed",
        "non_provenance_invariants": [
            "blind IDs are fresh UUID4 — no reconstruction ID, block, test ID, order, or timestamp encoded",
            "blind-map.json is private to operator; NOT shipped to either evaluator before both score sets are locked",
            "evaluator-A-order.json and evaluator-B-order.json each independently re-shuffle the blind IDs",
        ],
        "candidates": blind_assignments,
    }

    blind_map_path = EVDIR / "blinding" / "blind-map.json"
    blind_map_path.write_text(json.dumps(blind_map, indent=2, sort_keys=False) + "\n")
    blind_map_sha = sha256_file(blind_map_path)
    print(f"Wrote {blind_map_path} ({blind_map_path.stat().st_size} bytes, sha256 {blind_map_sha})")

    # ---- Per-evaluator random permutations ----
    # Each gets a fresh seed from the OS CSPRNG (independent of master_seed)
    seed_A = random.SystemRandom().getrandbits(256)
    seed_B = random.SystemRandom().getrandbits(256)

    # Both evaluators see ALL 60 candidates (full scoring per protocol — no sample expansion)
    base_order = [c["blind_id"] for c in blind_assignments]

    rng_A = random.Random(seed_A)
    order_A = list(base_order)
    rng_A.shuffle(order_A)

    rng_B = random.Random(seed_B)
    order_B = list(base_order)
    rng_B.shuffle(order_B)

    same_ordering = order_A == order_B

    evaluator_A_order_path = EVDIR / "blinding" / "evaluator-A-order.json"
    evaluator_B_order_path = EVDIR / "blinding" / "evaluator-B-order.json"

    evaluator_A_record = {
        "schema_version": "0.1",
        "record_kind": "evaluator-ordering",
        "evaluator": "A",
        "experiment_id": "DBI-BIB-001-RERUN-001",
        "generated_at_utc": "2026-09-06T09:30:00Z",
        "method": "Fisher-Yates shuffle over all 60 blind IDs, seeded with seed_A",
        "random_seed_hex": f"{seed_A:064x}",
        "random_seed_source": "random.SystemRandom().getrandbits(256) — OS entropy (/dev/urandom)",
        "candidate_count": 60,
        "ordered_blind_ids": order_A,
        "ordered_blind_ids_sha256": hashlib.sha256(json.dumps(order_A).encode()).hexdigest(),
    }
    evaluator_B_record = {
        "schema_version": "0.1",
        "record_kind": "evaluator-ordering",
        "evaluator": "B",
        "experiment_id": "DBI-BIB-001-RERUN-001",
        "generated_at_utc": "2026-09-06T09:30:00Z",
        "method": "Fisher-Yates shuffle over all 60 blind IDs, seeded with seed_B",
        "random_seed_hex": f"{seed_B:064x}",
        "random_seed_source": "random.SystemRandom().getrandbits(256) — OS entropy (/dev/urandom)",
        "candidate_count": 60,
        "ordered_blind_ids": order_B,
        "ordered_blind_ids_sha256": hashlib.sha256(json.dumps(order_B).encode()).hexdigest(),
    }
    evaluator_A_order_path.write_text(json.dumps(evaluator_A_record, indent=2) + "\n")
    evaluator_B_order_path.write_text(json.dumps(evaluator_B_record, indent=2) + "\n")

    a_sha = sha256_file(evaluator_A_order_path)
    b_sha = sha256_file(evaluator_B_order_path)
    print(f"Wrote {evaluator_A_order_path} (sha256 {a_sha})")
    print(f"Wrote {evaluator_B_order_path} (sha256 {b_sha})")
    print(f"orderings_identical={same_ordering}  (expected with 60 elements: probability ~1/60!)")

    # ---- Provenance summary ----
    provenance = {
        "schema_version": "0.1",
        "record_kind": "blind-map-provenance",
        "experiment_id": "DBI-BIB-001-RERUN-001",
        "constructed_at_utc": "2026-09-06T09:30:00Z",
        "blind_map_sha256": blind_map_sha,
        "evaluator_A_order_sha256": a_sha,
        "evaluator_B_order_sha256": b_sha,
        "orderings_identical": bool(same_ordering),
        "candidate_count": len(blind_assignments),
        "blind_id_algorithm": "uuid.uuid4 (OS CSPRNG)",
        "ordering_algorithm": "Fisher-Yates shuffle, per-evaluator seed from OS CSPRNG",
        "operational_notes": [
            "blind-map.json is NOT shipped to either evaluator. It is private operator evidence until BOTH score sets are locked.",
            "Each evaluator receives evaluator-X-order.json (an ordered list of 60 blind IDs) + the frozen behavioral baseline + frozen rubric + the matrix of (blind_id, test_prompt, raw_output_text).",
            "No reconstruction_id, block, test_id, session_id, model, or any provenance is included in the evaluator packet.",
        ],
    }
    provenance_path = EVDIR / "blinding" / "blind-map-provenance.json"
    provenance_path.write_text(json.dumps(provenance, indent=2) + "\n")
    prov_sha = sha256_file(provenance_path)
    print(f"Wrote {provenance_path} (sha256 {prov_sha})")

    # Print quick summary of a few blind_id assignments for audit
    print("\n--- Blind map summary (first 5 entries) ---")
    for c in blind_assignments[:5]:
        print(f"  {c['blind_id']}  <- {c['reconstruction_id']}/{c['block']}/{c['test_id']}  sha256={c['raw_sha256'][:16]}...")


if __name__ == "__main__":
    main()
