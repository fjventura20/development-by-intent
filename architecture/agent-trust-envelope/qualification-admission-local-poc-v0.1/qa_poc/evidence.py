"""ATE Qualification & Admission Local PoC v0.1 — public-key/custody evidence manifest.

Per design §7: "Evidence records only public material and custody metadata:
    authority_id, key_id, public_key, permitted_artifact_types, file owner/mode."

Private keys/seeds are not committed and not placed in evidence.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import List, Optional

from .canonical import canonical_sha256
from .crypto import Ed25519PublicKey, key_id_from_public_key
from .models import ALL_DOMAINS


@dataclass
class AuthorityPublicMaterial:
    authority_id: str
    key_id: str
    public_key_pem: str  # base64-free PEM string
    permitted_artifact_types: List[str] = field(default_factory=list)
    file_owner: Optional[str] = None
    file_mode: Optional[str] = None  # octal string

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PublicKeyManifest:
    manifest_id: str
    authorities: List[AuthorityPublicMaterial]
    manifest_digest: str = ""

    def finalize(self) -> "PublicKeyManifest":
        d = {"manifest_id": self.manifest_id, "authorities": [a.to_dict() for a in self.authorities]}
        return PublicKeyManifest(
            manifest_id=self.manifest_id,
            authorities=self.authorities,
            manifest_digest=canonical_sha256(d),
        )

    def to_json(self) -> str:
        return json.dumps(
            {
                "manifest_id": self.manifest_id,
                "manifest_digest": self.manifest_digest,
                "authorities": [a.to_dict() for a in self.authorities],
            },
            indent=2,
            sort_keys=True,
        )


def make_authority_record(
    *,
    authority_id: str,
    pub: Ed25519PublicKey,
    permitted_artifact_types: List[str],
    file_owner: Optional[str] = None,
    file_mode: Optional[str] = None,
) -> AuthorityPublicMaterial:
    from cryptography.hazmat.primitives import serialization
    pem_bytes = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    kid = key_id_from_public_key(pub)
    return AuthorityPublicMaterial(
        authority_id=authority_id,
        key_id=kid,
        public_key_pem=pem_bytes.decode("ascii"),
        permitted_artifact_types=permitted_artifact_types,
        file_owner=file_owner,
        file_mode=file_mode,
    )
